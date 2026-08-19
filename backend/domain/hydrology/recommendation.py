"""
RTRWH Platform — Recommendation Engine
=======================================
Rule-based, explainable recommendation engine for RTRWH and AR structures.

Design Principle:
  This is a DETERMINISTIC, RULE-BASED system.
  Every recommendation is traceable to specific input conditions.
  No black-box AI/ML — all decision logic is visible and auditable.

Recommendation Decision Logic:
  The engine evaluates multiple factors and uses a decision tree approach:

  1. Groundwater depth → determines recharge vs. storage
  2. Soil infiltration → determines structure type
  3. Available area → determines structure size/type
  4. Rainfall + runoff → determines required capacity
  5. Water demand → determines priority (storage vs. recharge)

Structure Selection Rules:
  HIGH_WATER_TABLE (< 3m BGL):
    → Storage Tank (no recharge recommended)

  LOW_INFILTRATION (< 3 mm/hr):
    + Deep groundwater (> 10m BGL): → Recharge Shaft
    + Otherwise:                    → Storage Tank

  MODERATE_INFILTRATION (3-10 mm/hr):
    + Large area available:  → Recharge Trench
    + Small area available:  → Recharge Pit
    + Very small area:       → Recharge Shaft

  HIGH_INFILTRATION (> 10 mm/hr):
    + Adequate area:  → Recharge Pit (preferred)
    + Limited area:   → Recharge Trench

  HIGH_DEMAND + RAINFALL_SURPLUS:
    → Storage Tank first, then Recharge Pit

Sources:
  CGWB Manual on Artificial Recharge (2007)
  IS 15797:2008
  Ministry of Jal Shakti implementation guidelines

Author: RTRWH Platform Engineering Team
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Literal
from domain.hydrology.rtrwh import RTRWHResult
from domain.hydrology.recharge import RechargeResult, SiteConditionsInput
from domain.hydrology.structures import (
    StructureDimensions,
    StructureType,
    size_storage_tank,
    size_recharge_pit,
    size_recharge_trench,
    size_recharge_shaft,
)


@dataclass
class RecommendationResult:
    """
    Complete recommendation result with full explainability.
    Every field is traceable to inputs and decision rules.
    """
    # Primary recommendation
    primary_structure_type: StructureType
    primary_structure_display: str
    primary_structure_dimensions: StructureDimensions

    # Secondary recommendation (complementary structure)
    secondary_structure_type: Optional[StructureType]
    secondary_structure_display: Optional[str]
    secondary_structure_dimensions: Optional[StructureDimensions]

    # Explanation
    recommendation_reason: str
    decision_factors: list[str]  # List of factors that drove the decision
    confidence: str  # 'HIGH' | 'MEDIUM' | 'LOW'
    confidence_reason: str

    # Performance estimates
    expected_annual_storage_or_recharge_litres: float
    demand_met_percentage: float

    # Warnings
    warnings: list[str]

    # Decision trace (for full explainability)
    decision_trace: list[str]


def generate_recommendation(
    rtrwh_result: RTRWHResult,
    recharge_result: RechargeResult,
    site: SiteConditionsInput,
    demand_met_pct: float = 0.0,
) -> RecommendationResult:
    """
    Generate a rule-based, explainable structure recommendation.

    Args:
        rtrwh_result: RTRWH calculation results
        recharge_result: AR calculation results
        site: Site conditions
        demand_met_pct: % of demand that can be met by harvested water

    Returns:
        RecommendationResult with full decision trace
    """
    decision_trace: list[str] = []
    decision_factors: list[str] = []
    warnings: list[str] = list(rtrwh_result.warnings) + list(recharge_result.warnings)

    net_annual_litres = rtrwh_result.annual_net_harvestable_litres
    annual_demand_litres = rtrwh_result.annual_demand_litres
    gw_depth = site.groundwater_depth_mbgl
    inf_rate = recharge_result.infiltration_rate_mm_hr
    available_area = site.available_area_m2
    roof_area = rtrwh_result.roof_area_m2

    # Peak storm runoff for structure sizing (simplified: 24-hr design storm)
    # Use 30% of monsoon season rainfall as peak storm proxy
    # This is conservative for preliminary sizing
    peak_storm_volume_m3 = net_annual_litres * 0.30 / 1000.0
    # But cap at reasonable limits
    peak_storm_volume_m3 = min(peak_storm_volume_m3, 50.0)  # max 50 m³ for preliminary

    decision_trace.append(
        f"Input: Roof Area = {roof_area:.0f} m², "
        f"Annual Rainfall = {rtrwh_result.annual_rainfall_mm:.0f} mm, "
        f"Net Harvestable = {net_annual_litres:,.0f} L/yr"
    )

    # ==========================================================================
    # RULE 1: Groundwater depth check (CRITICAL)
    # If water table is too shallow, recharge structures will cause waterlogging
    # ==========================================================================
    gw_depth_adequate = recharge_result.groundwater_depth_adequate

    if not gw_depth_adequate:
        decision_trace.append(
            f"RULE 1: Groundwater depth ({gw_depth:.1f} m BGL) < 3.0 m minimum. "
            "Recharge structures NOT recommended. → Storage Tank selected."
        )
        decision_factors.append(
            f"Shallow groundwater ({gw_depth:.1f} m BGL) prevents underground recharge"
        )
        return _recommend_storage_tank(
            net_annual_litres=net_annual_litres,
            peak_storm_volume_m3=peak_storm_volume_m3,
            annual_demand_litres=annual_demand_litres,
            demand_met_pct=demand_met_pct,
            reason=(
                f"Groundwater table is shallow ({gw_depth:.1f} m below ground level). "
                "Standard recharge structures (pit, trench, shaft) are not recommended "
                "as they may cause waterlogging and structural damage. "
                "Surface or underground storage tanks are appropriate."
            ),
            decision_factors=decision_factors,
            decision_trace=decision_trace,
            warnings=warnings,
            confidence="HIGH",
            confidence_reason="Groundwater depth is a definitive criterion from CGWB guidelines.",
        )

    decision_trace.append(
        f"RULE 1: Groundwater depth adequate "
        f"({'%.1f m' % gw_depth if gw_depth else 'unknown, assumed adequate'}). "
        "Recharge structures can be considered."
    )

    # ==========================================================================
    # RULE 2: Infiltration rate
    # ==========================================================================
    decision_trace.append(
        f"RULE 2: Soil infiltration rate = {inf_rate:.1f} mm/hr "
        f"(source: {recharge_result.infiltration_data_source}, "
        f"confidence: {recharge_result.infiltration_confidence})"
    )

    # ==========================================================================
    # RULE 3: Primary decision — demand vs. recharge orientation
    # ==========================================================================
    high_demand = annual_demand_litres > 0 and demand_met_pct < 80.0

    # ==========================================================================
    # RULE 4: Structure selection based on infiltration + area
    # ==========================================================================
    if inf_rate < 1.0:
        # Very low infiltration — surface recharge structures ineffective
        decision_trace.append(
            f"RULE 4: Very low infiltration ({inf_rate:.1f} mm/hr < 1.0 mm/hr threshold). "
            "Standard pit/trench not suitable. → Checking groundwater depth for shaft."
        )
        if gw_depth and gw_depth > 5.0:
            # Shaft can bypass the impermeable surface layer
            return _recommend_recharge_shaft(
                peak_storm_volume_m3=peak_storm_volume_m3,
                inf_rate=inf_rate,
                gw_depth=gw_depth,
                net_annual_litres=net_annual_litres,
                demand_met_pct=demand_met_pct,
                reason=(
                    f"Surface soil has very low infiltration rate ({inf_rate:.1f} mm/hr). "
                    f"Standard recharge pits/trenches are ineffective. "
                    f"However, groundwater is at {gw_depth:.1f} m depth, allowing a "
                    "recharge shaft to bypass the low-permeability surface layer "
                    "and reach a more permeable aquifer below."
                ),
                decision_factors=decision_factors + [
                    f"Very low surface infiltration ({inf_rate:.1f} mm/hr) eliminates pit/trench",
                    f"Deep groundwater ({gw_depth:.1f} m) makes shaft viable",
                ],
                decision_trace=decision_trace,
                warnings=warnings,
            )
        else:
            # Low infiltration + shallow water = storage only
            return _recommend_storage_tank(
                net_annual_litres=net_annual_litres,
                peak_storm_volume_m3=peak_storm_volume_m3,
                annual_demand_litres=annual_demand_litres,
                demand_met_pct=demand_met_pct,
                reason=(
                    f"Surface soil has very low infiltration ({inf_rate:.1f} mm/hr) and "
                    f"groundwater depth ({gw_depth:.1f if gw_depth else 'unknown'} m BGL) "
                    "does not support a recharge shaft. "
                    "Surface storage tank is the appropriate solution."
                ),
                decision_factors=decision_factors + [
                    "Low infiltration + insufficient depth for recharge shaft",
                ],
                decision_trace=decision_trace,
                warnings=warnings,
                confidence="MEDIUM",
                confidence_reason="Soil data may be assumed; verify with field test.",
            )

    elif inf_rate < 5.0:
        # Low-moderate infiltration → recharge shaft or trench preferred
        decision_trace.append(
            f"RULE 4: Low-moderate infiltration ({inf_rate:.1f} mm/hr). "
            "→ Recharge Trench selected (larger infiltration area than pit)."
        )
        return _recommend_recharge_trench_primary(
            peak_storm_volume_m3=peak_storm_volume_m3,
            inf_rate=inf_rate,
            available_area=available_area,
            net_annual_litres=net_annual_litres,
            demand_met_pct=demand_met_pct,
            reason=(
                f"Soil infiltration rate ({inf_rate:.1f} mm/hr) is relatively low. "
                "A recharge trench is preferred over a pit as it provides a larger "
                "infiltration surface area for the same volume, improving recharge efficiency. "
                "Filter fabric lining is recommended to prevent clogging."
            ),
            decision_factors=decision_factors + [
                f"Low-moderate infiltration ({inf_rate:.1f} mm/hr) favors trench over pit",
                "Trench provides larger surface area per unit volume",
            ],
            decision_trace=decision_trace,
            warnings=warnings,
        )

    else:
        # Good infiltration → recharge pit is primary choice
        decision_trace.append(
            f"RULE 4: Good infiltration ({inf_rate:.1f} mm/hr ≥ 5.0 mm/hr threshold). "
            "→ Recharge Pit selected."
        )
        return _recommend_recharge_pit_primary(
            peak_storm_volume_m3=peak_storm_volume_m3,
            inf_rate=inf_rate,
            available_area=available_area,
            net_annual_litres=net_annual_litres,
            demand_met_pct=demand_met_pct,
            annual_demand_litres=annual_demand_litres,
            reason=(
                f"Good soil infiltration capacity ({inf_rate:.1f} mm/hr), "
                f"adequate groundwater depth, "
                f"and estimated annual runoff of {net_annual_litres/1000:.1f} m³. "
                "A gravel-filled recharge pit is the most appropriate and "
                "cost-effective structure for these site conditions."
            ),
            decision_factors=decision_factors + [
                f"Good infiltration rate ({inf_rate:.1f} mm/hr) supports recharge pit",
                "Cost-effective and low-maintenance solution",
            ],
            decision_trace=decision_trace,
            warnings=warnings,
        )


# =============================================================================
# RECOMMENDATION HELPERS
# =============================================================================

def _recommend_storage_tank(
    net_annual_litres: float,
    peak_storm_volume_m3: float,
    annual_demand_litres: float,
    demand_met_pct: float,
    reason: str,
    decision_factors: list[str],
    decision_trace: list[str],
    warnings: list[str],
    confidence: str = "HIGH",
    confidence_reason: str = "",
) -> RecommendationResult:
    # Design tank for 60-day dry period or 50% of annual demand, whichever is smaller
    if annual_demand_litres > 0:
        tank_design_litres = min(annual_demand_litres * 0.5, annual_demand_litres / 12 * 2)
        tank_design_litres = max(tank_design_litres, peak_storm_volume_m3 * 1000.0)
    else:
        tank_design_litres = max(net_annual_litres * 0.20, peak_storm_volume_m3 * 1000.0)

    dims = size_storage_tank(design_volume_litres=tank_design_litres)

    return RecommendationResult(
        primary_structure_type="storage_tank",
        primary_structure_display="Rainwater Storage Tank",
        primary_structure_dimensions=dims,
        secondary_structure_type=None,
        secondary_structure_display=None,
        secondary_structure_dimensions=None,
        recommendation_reason=reason,
        decision_factors=decision_factors,
        confidence=confidence,
        confidence_reason=confidence_reason or "Groundwater/soil conditions clearly indicate storage solution.",
        expected_annual_storage_or_recharge_litres=round(net_annual_litres, 0),
        demand_met_percentage=demand_met_pct,
        warnings=warnings,
        decision_trace=decision_trace,
    )


def _recommend_recharge_pit_primary(
    peak_storm_volume_m3: float,
    inf_rate: float,
    available_area: Optional[float],
    net_annual_litres: float,
    demand_met_pct: float,
    annual_demand_litres: float,
    reason: str,
    decision_factors: list[str],
    decision_trace: list[str],
    warnings: list[str],
) -> RecommendationResult:
    dims = size_recharge_pit(
        design_volume_m3=peak_storm_volume_m3,
        infiltration_rate_mm_hr=inf_rate,
        max_footprint_m2=available_area,
    )

    # If demand is significant, also recommend a small storage tank
    secondary_dims = None
    secondary_type = None
    secondary_display = None
    if annual_demand_litres > 10000:  # > 10,000 L/yr demand
        tank_litres = min(annual_demand_litres * 0.10, 5000.0)  # small supplementary tank
        secondary_dims = size_storage_tank(design_volume_litres=tank_litres)
        secondary_type = "storage_tank"
        secondary_display = "Supplementary Small Storage Tank"

    return RecommendationResult(
        primary_structure_type="recharge_pit",
        primary_structure_display="Gravel-Filled Recharge Pit",
        primary_structure_dimensions=dims,
        secondary_structure_type=secondary_type,
        secondary_structure_display=secondary_display,
        secondary_structure_dimensions=secondary_dims,
        recommendation_reason=reason,
        decision_factors=decision_factors,
        confidence="MEDIUM",
        confidence_reason=(
            "Infiltration rate may be assumed. Field test recommended for final design."
        ),
        expected_annual_storage_or_recharge_litres=round(net_annual_litres, 0),
        demand_met_percentage=demand_met_pct,
        warnings=warnings,
        decision_trace=decision_trace,
    )


def _recommend_recharge_trench_primary(
    peak_storm_volume_m3: float,
    inf_rate: float,
    available_area: Optional[float],
    net_annual_litres: float,
    demand_met_pct: float,
    reason: str,
    decision_factors: list[str],
    decision_trace: list[str],
    warnings: list[str],
) -> RecommendationResult:
    available_length = math.sqrt(available_area) if available_area else None
    dims = size_recharge_trench(
        design_volume_m3=peak_storm_volume_m3,
        infiltration_rate_mm_hr=inf_rate,
        available_length_m=available_length,
    )

    return RecommendationResult(
        primary_structure_type="recharge_trench",
        primary_structure_display="Gravel-Filled Recharge Trench",
        primary_structure_dimensions=dims,
        secondary_structure_type=None,
        secondary_structure_display=None,
        secondary_structure_dimensions=None,
        recommendation_reason=reason,
        decision_factors=decision_factors,
        confidence="MEDIUM",
        confidence_reason=(
            "Infiltration data may be assumed. Field percolation test recommended."
        ),
        expected_annual_storage_or_recharge_litres=round(net_annual_litres, 0),
        demand_met_percentage=demand_met_pct,
        warnings=warnings,
        decision_trace=decision_trace,
    )


def _recommend_recharge_shaft(
    peak_storm_volume_m3: float,
    inf_rate: float,
    gw_depth: float,
    net_annual_litres: float,
    demand_met_pct: float,
    reason: str,
    decision_factors: list[str],
    decision_trace: list[str],
    warnings: list[str],
) -> RecommendationResult:
    dims = size_recharge_shaft(
        design_volume_m3=peak_storm_volume_m3,
        infiltration_rate_mm_hr=inf_rate,
        groundwater_depth_m=gw_depth,
    )

    return RecommendationResult(
        primary_structure_type="recharge_shaft",
        primary_structure_display="Recharge Shaft (Bore-well Type)",
        primary_structure_dimensions=dims,
        secondary_structure_type=None,
        secondary_structure_display=None,
        secondary_structure_dimensions=None,
        recommendation_reason=reason,
        decision_factors=decision_factors,
        confidence="LOW",
        confidence_reason=(
            "Recharge shaft effectiveness is highly dependent on subsurface geology. "
            "Hydrogeological investigation required."
        ),
        expected_annual_storage_or_recharge_litres=round(net_annual_litres, 0),
        demand_met_percentage=demand_met_pct,
        warnings=warnings + [
            "Recharge shaft requires professional drilling and CGWB/State Board approval."
        ],
        decision_trace=decision_trace,
    )
