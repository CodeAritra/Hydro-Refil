"""
RTRWH Platform — Artificial Recharge Calculation Engine
=========================================================
Groundwater artificial recharge potential assessment.

Methods covered:
  - Surface spreading / infiltration assessment
  - Recharge pit/trench volume estimation
  - Annual recharge potential from available runoff
  - Recharge rate estimation from soil properties

IMPORTANT DISCLAIMER:
  Artificial recharge calculations presented here are for PRELIMINARY ASSESSMENT
  ONLY. Actual recharge rates depend on:
    - Field-measured infiltration/permeability (not assumed values)
    - Seasonal groundwater fluctuations
    - Aquifer characteristics
    - Confining layer properties
    - Regulatory requirements from State Groundwater Board
  A qualified hydrogeologist must verify all recharge designs before construction.

Sources:
  CGWB: "Manual on Artificial Recharge of Ground Water", 2007
  CGWB: "Master Plan for Artificial Recharge to Ground Water in India", 2013
  Ministry of Jal Shakti: "Guidelines for Artificial Recharge", 2019

Author: RTRWH Platform Engineering Team
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional

from domain.hydrology.assumptions import (
    SOIL_INFILTRATION_RATES,
    MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M,
    RECHARGE_PIT_MAX_DEPTH_M,
    RECHARGE_TRENCH_TYPICAL_DEPTH_M,
    GRAVEL_FILL_POROSITY,
    STRUCTURE_FREEBOARD_M,
)
from domain.hydrology.rtrwh import CalculationTrace


# =============================================================================
# DATA CLASSES — Inputs
# =============================================================================

@dataclass
class SiteConditionsInput:
    """
    Site hydrogeological conditions for AR assessment.
    All fields are optional because field data may not be available.
    Missing data triggers warnings and uses conservative assumptions.
    """
    # Soil / infiltration
    soil_type_key: str = "unknown"  # Key in SOIL_INFILTRATION_RATES
    infiltration_rate_mm_hr: Optional[float] = None  # Field-measured (overrides soil type)
    infiltration_data_source: str = "assumed"  # 'field_measured' | 'assumed' | 'database'

    # Groundwater
    groundwater_depth_mbgl: Optional[float] = None  # metres below ground level
    groundwater_data_source: str = "unknown"  # 'field_measured' | 'cgwb_record' | 'unknown'

    # Available area
    available_area_m2: Optional[float] = None  # Available land for recharge structure
    is_paved_area: bool = False  # If True, permeability of surface layer is compromised

    # Constraints
    distance_to_septic_m: Optional[float] = None  # Distance from sewage/septic (safety)
    distance_to_well_m: Optional[float] = None  # Distance from drinking water well

    def get_infiltration_rate(self) -> tuple[float, str, str]:
        """
        Return (infiltration_rate_mm_hr, data_source, confidence).
        Field-measured value takes precedence over assumed.
        """
        if self.infiltration_rate_mm_hr is not None:
            return (
                self.infiltration_rate_mm_hr,
                "field_measured",
                "HIGH" if self.infiltration_data_source == "field_measured" else "MEDIUM",
            )
        # Fall back to soil type assumption
        assumption = SOIL_INFILTRATION_RATES.get(
            self.soil_type_key,
            SOIL_INFILTRATION_RATES["unknown"]
        )
        return assumption.value, "assumed", assumption.confidence

    def validate(self) -> list[str]:
        errors = []
        if self.groundwater_depth_mbgl is not None and self.groundwater_depth_mbgl < 0:
            errors.append("Groundwater depth cannot be negative")
        if self.available_area_m2 is not None and self.available_area_m2 < 0:
            errors.append("Available area cannot be negative")
        if self.infiltration_rate_mm_hr is not None and self.infiltration_rate_mm_hr < 0:
            errors.append("Infiltration rate cannot be negative")
        return errors


# =============================================================================
# DATA CLASSES — Results
# =============================================================================

@dataclass
class RechargeResult:
    """
    Complete artificial recharge assessment result.
    """
    # Recharge potential
    annual_runoff_available_litres: float
    annual_recharge_potential_litres: float
    annual_recharge_potential_m3: float

    # Site conditions used
    infiltration_rate_mm_hr: float
    infiltration_data_source: str
    infiltration_confidence: str
    groundwater_depth_mbgl: Optional[float]
    soil_type_key: str

    # Feasibility
    recharge_feasible: bool
    feasibility_reason: str
    feasibility_label: str  # 'HIGHLY_FEASIBLE' | 'FEASIBLE' | 'CONDITIONAL' | 'NOT_RECOMMENDED'

    # Warnings
    warnings: list[str]
    calculation_trace: list[CalculationTrace]

    # Suitability checks
    groundwater_depth_adequate: bool
    contamination_risk_low: bool
    available_area_adequate: Optional[bool]


# =============================================================================
# CALCULATION ENGINE
# =============================================================================

def calculate_recharge_potential(
    annual_runoff_available_litres: float,
    site: SiteConditionsInput,
    peak_runoff_m3_per_hr: Optional[float] = None,
) -> RechargeResult:
    """
    Calculate artificial groundwater recharge potential.

    APPROACH:
    The annual recharge potential is calculated as the minimum of:
      1. Available runoff volume (from RTRWH calculation)
      2. Maximum infiltration capacity of proposed structure

    For a recharge pit of area A_pit and infiltration rate I (mm/hr):
      Infiltration_rate = I × A_pit (litres/hr)
      Annual capacity = I × A_pit × usable_hours_per_year

    However, for preliminary assessment, we use a simplified approach:
      Recharge_potential = min(Available_runoff, Site_infiltration_capacity)

    Source: CGWB Manual on Artificial Recharge (2007), Chapter 4

    Args:
        annual_runoff_available_litres: From RTRWH calculation
        site: Site hydrogeological conditions
        peak_runoff_m3_per_hr: Peak runoff rate for structure sizing

    Returns:
        RechargeResult with full calculation trace
    """
    traces: list[CalculationTrace] = []
    warnings: list[str] = []

    # Validate inputs
    errors = site.validate()
    if errors:
        raise ValueError(f"Site validation failed: {'; '.join(errors)}")

    # ------------------------------------------------------------------
    # STEP 1: Groundwater Depth Check
    # ------------------------------------------------------------------
    gw_depth = site.groundwater_depth_mbgl
    gw_depth_adequate = True
    gw_adequate_text = ""

    if gw_depth is None:
        warnings.append(
            "Groundwater depth not provided. "
            "Cannot reliably assess recharge suitability. "
            "Field measurement or CGWB data strongly recommended."
        )
        gw_depth_adequate = True  # Assume adequate if unknown (with warning)
        gw_adequate_text = "UNKNOWN — assumed adequate (conservative)"
    elif gw_depth < MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M.value:
        gw_depth_adequate = False
        gw_adequate_text = (
            f"INSUFFICIENT — depth {gw_depth:.1f} m is less than minimum "
            f"{MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M.value:.1f} m"
        )
        warnings.append(
            f"Groundwater depth ({gw_depth:.1f} m below GL) is shallow. "
            f"Standard recharge structures may cause waterlogging. "
            f"Minimum recommended depth: {MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M.value} m BGL. "
            f"Source: {MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M.source}"
        )
    else:
        gw_adequate_text = f"ADEQUATE — {gw_depth:.1f} m BGL"

    traces.append(CalculationTrace(
        formula_name="Groundwater Depth Check",
        formula_expression="gw_depth >= min_safe_depth",
        inputs={
            "Groundwater Depth": f"{gw_depth} m BGL" if gw_depth else "NOT PROVIDED",
            "Minimum Safe Depth (CGWB)": f"{MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M.value} m",
        },
        result=gw_adequate_text,
        notes=MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M.note,
    ))

    # ------------------------------------------------------------------
    # STEP 2: Get Infiltration Rate
    # ------------------------------------------------------------------
    inf_rate, inf_source, inf_confidence = site.get_infiltration_rate()

    traces.append(CalculationTrace(
        formula_name="Infiltration Rate",
        formula_expression="I = field_measured OR soil_type_default",
        inputs={
            "Soil Type": site.soil_type_key,
            "Data Source": inf_source,
            "Confidence": inf_confidence,
        },
        result=f"I = {inf_rate:.1f} mm/hr",
        notes=(
            "IMPORTANT: This value is "
            + ("field-measured." if inf_source == "field_measured"
               else "ASSUMED based on soil type. "
               "Field infiltration test (double-ring infiltrometer or "
               "tube test) REQUIRED for final design.")
        ),
    ))

    if inf_confidence in ("LOW", "VERY_LOW"):
        warnings.append(
            f"Infiltration rate ({inf_rate:.1f} mm/hr) is ASSUMED based on soil type. "
            "Actual site infiltration may differ significantly. "
            "Conduct field infiltration test (IS 9451:1994) before design."
        )

    # ------------------------------------------------------------------
    # STEP 3: Contamination Risk Check
    # ------------------------------------------------------------------
    contamination_risk_low = True
    if site.distance_to_septic_m is not None and site.distance_to_septic_m < 15:
        contamination_risk_low = False
        warnings.append(
            f"Recharge structure is close to septic system "
            f"({site.distance_to_septic_m:.0f} m). "
            "Minimum recommended separation: 15 m. "
            "Risk of groundwater contamination. Consult hydrogeologist."
        )
    if site.distance_to_well_m is not None and site.distance_to_well_m < 30:
        contamination_risk_low = False
        warnings.append(
            f"Recharge structure is close to drinking water well "
            f"({site.distance_to_well_m:.0f} m). "
            "Minimum recommended separation: 30 m. "
            "Ensure runoff quality before recharging."
        )

    # ------------------------------------------------------------------
    # STEP 4: Recharge Potential Estimation
    #
    # We use a simplified but transparent approach:
    # Annual recharge potential from a recharge pit of plan area A_pit:
    #   Q_annual (litres) = I (mm/hr) × A_pit (m²) × effective_hours/year
    #
    # Since we don't know A_pit yet (it's what we're sizing in structures.py),
    # we use a different approach:
    #
    # The recharge potential is limited to the LESSER of:
    #   a) Available runoff (upstream limit)
    #   b) Infiltration capacity of the site material × available area
    #
    # For this preliminary step, we estimate using available_area if provided,
    # otherwise we assume the recharge pit area = 10% of roof area as a
    # preliminary assumption.
    #
    # Source: CGWB Manual on Artificial Recharge (2007), Section 5
    # ------------------------------------------------------------------
    available_m2 = site.available_area_m2
    area_adequate = None

    # Minimum required plan area for meaningful recharge
    # Rule of thumb: structure area >= peak_runoff / (2 × infiltration_rate)
    # This is covered in detail in structures.py
    # Here we just estimate total potential.

    if available_m2 is not None and available_m2 > 0:
        # Effective infiltration hours per year
        # Use monsoon season hours as a proxy
        # India: ~90 rain days/year × average storm duration ~4 hrs
        # (representative estimate — actual varies significantly)
        EFFECTIVE_RECHARGE_HOURS_PER_YEAR = 360  # hours (ASSUMPTION)
        annual_infiltration_capacity_litres = (
            inf_rate * available_m2 * EFFECTIVE_RECHARGE_HOURS_PER_YEAR
        )
        annual_recharge_litres = min(
            annual_runoff_available_litres,
            annual_infiltration_capacity_litres
        )
        area_adequate = annual_infiltration_capacity_litres >= (
            annual_runoff_available_litres * 0.5
        )

        traces.append(CalculationTrace(
            formula_name="Annual Recharge Capacity Estimate",
            formula_expression=(
                "Q_recharge = min(Available_Runoff, "
                "I × Available_Area × Effective_Hours)"
            ),
            inputs={
                "Available Runoff": f"{annual_runoff_available_litres:,.0f} L/yr",
                "Infiltration Rate (I)": f"{inf_rate:.1f} mm/hr",
                "Available Area": f"{available_m2:.1f} m²",
                "Effective Recharge Hours": f"{EFFECTIVE_RECHARGE_HOURS_PER_YEAR} hr/yr (APPROX.)",
            },
            result=f"{annual_recharge_litres:,.0f} litres/year",
            notes=(
                f"Infiltration capacity = {annual_infiltration_capacity_litres:,.0f} L/yr. "
                f"Limiting factor: "
                + ("runoff volume" if annual_runoff_available_litres <= annual_infiltration_capacity_litres
                   else "infiltration capacity")
            ),
        ))
    else:
        # No area provided — use available runoff as upper bound
        annual_recharge_litres = annual_runoff_available_litres
        warnings.append(
            "Available land area for recharge structure not provided. "
            "Recharge potential is set equal to available runoff — this is an upper bound. "
            "Actual recharge depends on site dimensions and soil infiltration."
        )
        traces.append(CalculationTrace(
            formula_name="Annual Recharge Potential (Upper Bound)",
            formula_expression="Q_recharge ≤ Available_Runoff (area not known)",
            inputs={
                "Available Runoff": f"{annual_runoff_available_litres:,.0f} L/yr",
                "Available Area": "NOT PROVIDED",
            },
            result=f"{annual_recharge_litres:,.0f} L/yr (UPPER BOUND)",
            notes="This is an upper bound. Actual recharge depends on site area and infiltration capacity.",
        ))

    # ------------------------------------------------------------------
    # STEP 5: Overall Feasibility
    # ------------------------------------------------------------------
    recharge_feasible, feasibility_label, feasibility_reason = _assess_recharge_feasibility(
        gw_depth_adequate=gw_depth_adequate,
        inf_rate=inf_rate,
        inf_confidence=inf_confidence,
        annual_recharge_litres=annual_recharge_litres,
        contamination_risk_low=contamination_risk_low,
        warnings=warnings,
    )

    return RechargeResult(
        annual_runoff_available_litres=round(annual_runoff_available_litres, 1),
        annual_recharge_potential_litres=round(annual_recharge_litres, 1),
        annual_recharge_potential_m3=round(annual_recharge_litres / 1000.0, 2),
        infiltration_rate_mm_hr=inf_rate,
        infiltration_data_source=inf_source,
        infiltration_confidence=inf_confidence,
        groundwater_depth_mbgl=gw_depth,
        soil_type_key=site.soil_type_key,
        recharge_feasible=recharge_feasible,
        feasibility_reason=feasibility_reason,
        feasibility_label=feasibility_label,
        warnings=warnings,
        calculation_trace=traces,
        groundwater_depth_adequate=gw_depth_adequate,
        contamination_risk_low=contamination_risk_low,
        available_area_adequate=area_adequate,
    )


def _assess_recharge_feasibility(
    gw_depth_adequate: bool,
    inf_rate: float,
    inf_confidence: str,
    annual_recharge_litres: float,
    contamination_risk_low: bool,
    warnings: list[str],
) -> tuple[bool, str, str]:
    """
    Determine overall recharge feasibility.
    Returns (feasible: bool, label: str, reason: str)
    """
    if not gw_depth_adequate:
        return (
            False,
            "NOT_RECOMMENDED",
            "Groundwater table is too shallow for standard recharge structures. "
            "Waterlogging risk. Consider surface storage tanks instead.",
        )

    if inf_rate < 1.0:
        return (
            False,
            "NOT_RECOMMENDED",
            f"Soil infiltration rate is very low ({inf_rate:.1f} mm/hr). "
            "Standard recharge pits/trenches are unlikely to be effective. "
            "Consider recharge shaft with deep injection or surface storage.",
        )

    if not contamination_risk_low:
        return (
            True,
            "CONDITIONAL",
            "Recharge is potentially feasible but contamination risk needs mitigation. "
            "Adequate separation from sewage and wells must be ensured. "
            "First flush and filtration are mandatory.",
        )

    if inf_rate < 5.0:
        return (
            True,
            "CONDITIONAL",
            f"Low to moderate infiltration rate ({inf_rate:.1f} mm/hr). "
            "Recharge pit or trench may work but will require larger dimensions. "
            "Consider recharge shaft for better performance.",
        )

    if annual_recharge_litres < 1000:
        return (
            True,
            "LOW_POTENTIAL",
            "Recharge potential is very low. "
            "Assessment may not justify construction cost.",
        )

    if inf_confidence in ("LOW", "VERY_LOW"):
        return (
            True,
            "FEASIBLE_LOW_CONFIDENCE",
            "Recharge appears technically feasible but infiltration data is assumed. "
            "Field measurement required before committing to design.",
        )

    return (
        True,
        "HIGHLY_FEASIBLE",
        f"Good infiltration capacity ({inf_rate:.1f} mm/hr), adequate groundwater depth, "
        f"and sufficient runoff volume ({annual_recharge_litres/1000:.1f} m³/year). "
        "Standard recharge structures are recommended.",
    )
