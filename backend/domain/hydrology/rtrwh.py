"""
RTRWH Platform — RTRWH Calculation Engine
==========================================
Rooftop Rainwater Harvesting potential calculations.

All formulas are documented with:
  - Formula name
  - Input parameters with units
  - Output with units
  - Source reference
  - Calculation trace (for explainability)

FUNDAMENTAL UNIT RELATIONSHIP:
  1 mm of rainfall over 1 m² of area = 1 litre of water
  Proof: 1 mm = 0.001 m
         Volume = 1 m² × 0.001 m = 0.001 m³ = 1 litre ✓

Author: RTRWH Platform Engineering Team
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional
from domain.hydrology.assumptions import (
    RUNOFF_COEFFICIENTS,
    SYSTEM_EFFICIENCY,
    FIRST_FLUSH_DEPTH_MM,
    MONTHLY_DISTRIBUTION_INDIA_TYPICAL,
    WATER_DEMAND_PER_CAPITA,
)


# =============================================================================
# DATA CLASSES — Inputs
# =============================================================================

@dataclass
class RoofInput:
    """Roof/catchment parameters for RTRWH calculation."""
    area_m2: float  # Roof catchment area in square metres
    material_key: str  # Must match key in RUNOFF_COEFFICIENTS
    slope_deg: float = 0.0  # Roof slope in degrees (0 = flat)
    num_downpipes: int = 1  # Number of downpipes/drainpipes
    has_first_flush_diverter: bool = True  # Whether first-flush diverter is present

    def validate(self) -> list[str]:
        """Return list of validation errors, empty if valid."""
        errors = []
        if self.area_m2 <= 0:
            errors.append(f"Roof area must be > 0 m² (got {self.area_m2})")
        if self.area_m2 > 50000:
            errors.append(f"Roof area {self.area_m2} m² seems very large — please verify")
        if self.material_key not in RUNOFF_COEFFICIENTS:
            errors.append(f"Unknown roof material: {self.material_key}")
        return errors


@dataclass
class RainfallInput:
    """Rainfall data for RTRWH calculation."""
    annual_mm: float  # Annual rainfall in mm
    monthly_mm: Optional[dict[str, float]] = None  # Monthly distribution (optional)
    data_source: str = "user_provided"  # 'user_provided' | 'imd_database' | 'estimated'

    def validate(self) -> list[str]:
        errors = []
        if self.annual_mm < 0:
            errors.append(f"Annual rainfall cannot be negative (got {self.annual_mm})")
        if self.annual_mm == 0:
            errors.append("Annual rainfall is 0 — no harvesting potential exists")
        if self.annual_mm > 12000:
            errors.append(
                f"Annual rainfall {self.annual_mm} mm is very high — please verify "
                "(Cherrapunji is ~11,000 mm, world record)"
            )
        if self.monthly_mm is not None:
            total = sum(self.monthly_mm.values())
            if abs(total - self.annual_mm) > self.annual_mm * 0.05:
                errors.append(
                    f"Sum of monthly rainfall ({total:.0f} mm) differs from "
                    f"annual total ({self.annual_mm:.0f} mm) by more than 5%"
                )
        return errors

    def get_monthly_mm(self) -> dict[str, float]:
        """
        Return monthly rainfall values in mm.
        If monthly data not provided, distribute annual using typical Indian pattern.
        """
        if self.monthly_mm and len(self.monthly_mm) == 12:
            return self.monthly_mm
        # Use typical Indian distribution pattern
        return {
            month: round(self.annual_mm * fraction, 1)
            for month, fraction in MONTHLY_DISTRIBUTION_INDIA_TYPICAL.items()
        }


@dataclass
class WaterDemandInput:
    """Water demand parameters."""
    num_people: int = 0
    per_capita_demand_lpd: float = 135.0  # litres/person/day
    occupancy_type: str = "domestic_urban"  # Key for demand assumptions
    additional_demand_lpm: float = 0.0  # Additional monthly demand in litres
    non_potable_fraction: float = 0.40  # Fraction of demand potentially met by rainwater

    def validate(self) -> list[str]:
        errors = []
        if self.num_people < 0:
            errors.append("Number of people cannot be negative")
        if self.per_capita_demand_lpd <= 0:
            errors.append("Per-capita demand must be > 0")
        if self.non_potable_fraction < 0 or self.non_potable_fraction > 1:
            errors.append("Non-potable fraction must be between 0 and 1")
        return errors

    def annual_total_litres(self) -> float:
        """Total annual water demand in litres."""
        daily = (self.num_people * self.per_capita_demand_lpd) + (
            self.additional_demand_lpm / 30.44
        )
        return daily * 365.0

    def annual_harvestable_demand_litres(self) -> float:
        """
        Annual demand potentially replaceable by rainwater.
        Only non-potable or direct-use fraction counts unless treatment is applied.
        """
        return self.annual_total_litres() * self.non_potable_fraction


# =============================================================================
# DATA CLASSES — Results
# =============================================================================

@dataclass
class MonthlyResult:
    """Monthly RTRWH calculation result."""
    month: str
    rainfall_mm: float
    gross_runoff_litres: float  # Before first-flush and system losses
    net_harvestable_litres: float  # After all losses
    demand_litres: float
    balance_litres: float  # Positive = surplus, Negative = deficit
    cumulative_harvested_litres: float = 0.0


@dataclass
class CalculationTrace:
    """
    Structured record of a calculation step for explainability.
    Every major calculation step should produce a trace.
    """
    formula_name: str
    formula_expression: str
    inputs: dict[str, str]  # parameter_name: "value unit"
    result: str  # "value unit"
    notes: Optional[str] = None


@dataclass
class RTRWHResult:
    """
    Complete RTRWH assessment result.
    All values are fully traceable to inputs.
    """
    # Key metrics
    roof_area_m2: float
    annual_rainfall_mm: float
    runoff_coefficient: float
    system_efficiency: float

    # Annual totals
    annual_gross_runoff_litres: float
    annual_net_harvestable_litres: float
    first_flush_annual_loss_litres: float

    # Monthly breakdown
    monthly_results: list[MonthlyResult]

    # Water balance
    annual_demand_litres: float
    annual_surplus_deficit_litres: float  # Positive = surplus
    demand_met_percentage: float  # % of demand potentially met

    # Meta
    material_key: str
    runoff_coefficient_source: str
    data_quality_flags: list[str]  # Warnings about data quality
    calculation_trace: list[CalculationTrace]

    # Feasibility indicators
    feasibility_score: float  # 0.0 to 1.0
    feasibility_label: str  # 'HIGH' | 'MODERATE' | 'LOW' | 'INSUFFICIENT_DATA'
    warnings: list[str]

    @property
    def annual_net_harvestable_m3(self) -> float:
        return self.annual_net_harvestable_litres / 1000.0


# =============================================================================
# CALCULATION ENGINE
# =============================================================================

def calculate_rtrwh_potential(
    roof: RoofInput,
    rainfall: RainfallInput,
    demand: Optional[WaterDemandInput] = None,
) -> RTRWHResult:
    """
    Calculate complete Rooftop Rainwater Harvesting potential.

    CORE FORMULA:
        Harvestable_Volume = P × A × C × η
        Where:
            P = Annual rainfall (mm)
            A = Roof catchment area (m²)
            C = Runoff coefficient (dimensionless, 0-1)
            η = System efficiency (dimensionless, 0-1)

    UNIT VERIFICATION:
        mm × m² = (m/1000) × m² = m³/1000 = litres
        Therefore: P(mm) × A(m²) = volume in litres ✓

    Source: CGWB Master Plan for Artificial Recharge (2005), Chapter 3;
            IS 15797:2008; Ministry of Jal Shakti guidelines

    Args:
        roof: Roof/catchment characteristics
        rainfall: Rainfall data (annual + optional monthly)
        demand: Optional water demand for balance calculation

    Returns:
        RTRWHResult with complete calculation trace
    """
    traces: list[CalculationTrace] = []
    warnings: list[str] = []
    data_quality_flags: list[str] = []

    # ------------------------------------------------------------------
    # STEP 0: Input Validation
    # ------------------------------------------------------------------
    roof_errors = roof.validate()
    rain_errors = rainfall.validate()
    all_errors = roof_errors + rain_errors
    if all_errors:
        raise ValueError(f"Input validation failed: {'; '.join(all_errors)}")

    # ------------------------------------------------------------------
    # STEP 1: Get Runoff Coefficient
    # ------------------------------------------------------------------
    if roof.material_key not in RUNOFF_COEFFICIENTS:
        raise ValueError(
            f"Unknown roof material '{roof.material_key}'. "
            f"Valid options: {list(RUNOFF_COEFFICIENTS.keys())}"
        )
    coeff_assumption = RUNOFF_COEFFICIENTS[roof.material_key]
    C = coeff_assumption.value
    eta = SYSTEM_EFFICIENCY.value

    traces.append(CalculationTrace(
        formula_name="Runoff Coefficient Selection",
        formula_expression="C = f(roof_material)",
        inputs={"roof_material": roof.material_key},
        result=f"C = {C} (source: {coeff_assumption.source})",
        notes=coeff_assumption.note,
    ))

    if coeff_assumption.confidence in ("LOW", "VERY_LOW"):
        warnings.append(
            f"Runoff coefficient for '{roof.material_key}' has {coeff_assumption.confidence} "
            f"confidence. {coeff_assumption.note or ''}"
        )
        data_quality_flags.append(f"LOW_CONFIDENCE_COEFFICIENT: {roof.material_key}")

    # ------------------------------------------------------------------
    # STEP 2: Annual Gross Runoff
    # Gross = P × A × C  (before system losses)
    # Unit: mm × m² = litres
    # ------------------------------------------------------------------
    P = rainfall.annual_mm
    A = roof.area_m2
    annual_gross_litres = P * A * C

    traces.append(CalculationTrace(
        formula_name="Annual Gross Runoff",
        formula_expression="Gross_Runoff (L) = P (mm) × A (m²) × C",
        inputs={
            "P (Annual Rainfall)": f"{P:.1f} mm",
            "A (Roof Area)": f"{A:.2f} m²",
            "C (Runoff Coefficient)": f"{C:.2f}",
        },
        result=f"{annual_gross_litres:,.0f} litres/year",
        notes=(
            "Unit basis: 1 mm rainfall × 1 m² area = 1 litre. "
            "This is a physical relationship, not an approximation."
        ),
    ))

    # ------------------------------------------------------------------
    # STEP 3: First Flush Loss
    # First flush diverts early storm runoff (most contaminated portion)
    # Volume = ff_depth_mm × A (litres per event)
    # Annual loss requires estimating number of rain events/year.
    #
    # For annual calculation, we use a simplified approach:
    # We assume first-flush diverter is triggered at the start of each
    # rain day (wet days). Wet days estimated from rainfall.
    # ------------------------------------------------------------------
    ff_depth_mm = FIRST_FLUSH_DEPTH_MM.value
    # Approximate number of rain days per year (India heuristic)
    # Rough estimate: wet_days ≈ annual_rainfall_mm / 10
    # (approximate, as average Indian rain intensity ~10 mm/event)
    # Source: IMD climatological averages
    estimated_rain_events = max(1, int(P / 10))
    ff_annual_loss_litres = ff_depth_mm * A * estimated_rain_events

    traces.append(CalculationTrace(
        formula_name="First Flush Annual Loss",
        formula_expression=(
            "FF_Loss (L/yr) = ff_depth (mm) × A (m²) × estimated_rain_events"
        ),
        inputs={
            "First Flush Depth": f"{ff_depth_mm:.1f} mm/event (IS 15797:2008)",
            "Roof Area": f"{A:.2f} m²",
            "Estimated Rain Events/Year": f"{estimated_rain_events} events "
            f"(≈ Annual_Rainfall/10 mm; APPROXIMATION)",
        },
        result=f"{ff_annual_loss_litres:,.0f} litres/year diverted",
        notes=(
            "First flush loss is an approximation. Actual depends on local rain event "
            "frequency. For precise analysis, use rain gauge event records."
        ),
    ))

    # ------------------------------------------------------------------
    # STEP 4: Net Harvestable Volume
    # Net = (Gross - First_Flush_Loss) × System_Efficiency
    # ------------------------------------------------------------------
    volume_after_ff = max(0.0, annual_gross_litres - ff_annual_loss_litres)
    annual_net_litres = volume_after_ff * eta

    traces.append(CalculationTrace(
        formula_name="Net Annual Harvestable Volume",
        formula_expression=(
            "Net (L/yr) = (Gross_Runoff - First_Flush_Loss) × η (System Efficiency)"
        ),
        inputs={
            "Gross Runoff": f"{annual_gross_litres:,.0f} L/yr",
            "First Flush Loss": f"{ff_annual_loss_litres:,.0f} L/yr",
            "Volume after FF diversion": f"{volume_after_ff:,.0f} L/yr",
            "η (System Efficiency)": f"{eta:.2f} (CGWB default)",
        },
        result=f"{annual_net_litres:,.0f} litres/year",
        notes=SYSTEM_EFFICIENCY.note,
    ))

    # ------------------------------------------------------------------
    # STEP 5: Monthly Breakdown
    # ------------------------------------------------------------------
    monthly_rainfall = rainfall.get_monthly_mm()
    monthly_results: list[MonthlyResult] = []
    cumulative = 0.0
    month_names = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec",
    ]

    demand_monthly = 0.0
    if demand:
        annual_demand = demand.annual_harvestable_demand_litres()
        demand_monthly = annual_demand / 12.0
    annual_demand_litres = demand.annual_harvestable_demand_litres() if demand else 0.0

    for month in month_names:
        p_m = monthly_rainfall.get(month, 0.0)
        gross_m = p_m * A * C
        ff_m = ff_depth_mm * A  # one event per month (simplified)
        net_m = max(0.0, (gross_m - ff_m) * eta)
        balance_m = net_m - demand_monthly
        cumulative += net_m
        monthly_results.append(MonthlyResult(
            month=month,
            rainfall_mm=p_m,
            gross_runoff_litres=round(gross_m, 1),
            net_harvestable_litres=round(net_m, 1),
            demand_litres=round(demand_monthly, 1),
            balance_litres=round(balance_m, 1),
            cumulative_harvested_litres=round(cumulative, 1),
        ))

    traces.append(CalculationTrace(
        formula_name="Monthly Breakdown",
        formula_expression=(
            "Monthly_Net (L) = (P_month × A × C - FF_event) × η"
        ),
        inputs={
            "Monthly Distribution": "Based on provided monthly data or IMD typical pattern",
            "Calculation": "Applied same formula per month",
        },
        result=f"12 monthly values computed — see monthly_results",
        notes=(
            "If monthly rainfall was not provided, a typical Indian SW monsoon "
            "distribution was applied. This is an approximation."
        ),
    ))

    # ------------------------------------------------------------------
    # STEP 6: Water Balance
    # ------------------------------------------------------------------
    annual_surplus_deficit = annual_net_litres - annual_demand_litres
    demand_met_pct = (
        min(100.0, (annual_net_litres / annual_demand_litres) * 100.0)
        if annual_demand_litres > 0
        else 0.0
    )

    if demand and annual_demand_litres > 0:
        traces.append(CalculationTrace(
            formula_name="Annual Water Balance",
            formula_expression="Balance = Net_Harvestable - Demand_Harvestable",
            inputs={
                "Net Harvestable Water": f"{annual_net_litres:,.0f} L/yr",
                "Harvestable Demand": f"{annual_demand_litres:,.0f} L/yr",
            },
            result=(
                f"{'Surplus' if annual_surplus_deficit >= 0 else 'Deficit'}: "
                f"{abs(annual_surplus_deficit):,.0f} L/yr | "
                f"Demand Met: {demand_met_pct:.1f}%"
            ),
        ))

    # ------------------------------------------------------------------
    # STEP 7: Feasibility Assessment
    # ------------------------------------------------------------------
    feasibility_score, feasibility_label = _assess_feasibility(
        annual_net_litres, annual_demand_litres, P, A, warnings
    )

    # ------------------------------------------------------------------
    # STEP 8: Data Quality Warnings
    # ------------------------------------------------------------------
    if rainfall.data_source == "estimated":
        warnings.append(
            "Rainfall data is ESTIMATED. Results accuracy depends on local rainfall. "
            "Use IMD station data or site measurements for reliable assessment."
        )
        data_quality_flags.append("ESTIMATED_RAINFALL")

    if not rainfall.monthly_mm:
        warnings.append(
            "Monthly rainfall distribution not provided. "
            "A typical Indian SW monsoon pattern was applied. "
            "Actual monthly distribution may differ significantly."
        )
        data_quality_flags.append("ASSUMED_MONTHLY_DISTRIBUTION")

    return RTRWHResult(
        roof_area_m2=A,
        annual_rainfall_mm=P,
        runoff_coefficient=C,
        system_efficiency=eta,
        annual_gross_runoff_litres=round(annual_gross_litres, 1),
        annual_net_harvestable_litres=round(annual_net_litres, 1),
        first_flush_annual_loss_litres=round(ff_annual_loss_litres, 1),
        monthly_results=monthly_results,
        annual_demand_litres=round(annual_demand_litres, 1),
        annual_surplus_deficit_litres=round(annual_surplus_deficit, 1),
        demand_met_percentage=round(demand_met_pct, 1),
        material_key=roof.material_key,
        runoff_coefficient_source=coeff_assumption.source,
        data_quality_flags=data_quality_flags,
        calculation_trace=traces,
        feasibility_score=feasibility_score,
        feasibility_label=feasibility_label,
        warnings=warnings,
    )


def _assess_feasibility(
    net_annual_litres: float,
    demand_litres: float,
    annual_rainfall_mm: float,
    roof_area_m2: float,
    warnings: list[str],
) -> tuple[float, str]:
    """
    Multi-factor feasibility assessment for RTRWH.
    Returns (score 0-1, label string).
    """
    score = 0.0
    factors = 0

    # Factor 1: Absolute volume
    if net_annual_litres >= 50000:  # >= 50,000 litres
        score += 1.0
    elif net_annual_litres >= 20000:
        score += 0.7
    elif net_annual_litres >= 5000:
        score += 0.4
    else:
        score += 0.1
        warnings.append(
            f"Low annual harvestable volume ({net_annual_litres:,.0f} L). "
            "RTRWH may not be cost-effective."
        )
    factors += 1

    # Factor 2: Rainfall adequacy
    if annual_rainfall_mm >= 600:
        score += 1.0
    elif annual_rainfall_mm >= 300:
        score += 0.6
    else:
        score += 0.2
        warnings.append(
            f"Annual rainfall ({annual_rainfall_mm:.0f} mm) is low. "
            "Limited harvesting potential in arid/semi-arid conditions."
        )
    factors += 1

    # Factor 3: Demand match (if demand provided)
    if demand_litres > 0:
        ratio = net_annual_litres / demand_litres
        if ratio >= 0.5:
            score += 1.0
        elif ratio >= 0.2:
            score += 0.6
        else:
            score += 0.2
        factors += 1

    # Factor 4: Catchment size
    if roof_area_m2 >= 100:
        score += 1.0
    elif roof_area_m2 >= 50:
        score += 0.7
    else:
        score += 0.4
        warnings.append(
            f"Small catchment area ({roof_area_m2:.0f} m²). "
            "Limited collection volume. Consider multiple structures."
        )
    factors += 1

    avg_score = score / factors
    if avg_score >= 0.75:
        label = "HIGH"
    elif avg_score >= 0.50:
        label = "MODERATE"
    elif avg_score >= 0.25:
        label = "LOW"
    else:
        label = "VERY_LOW"

    return round(avg_score, 2), label
