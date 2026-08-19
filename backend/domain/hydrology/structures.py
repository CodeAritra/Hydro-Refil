"""
RTRWH Platform — Structure Sizing Calculator
=============================================
Indicative dimension calculation for RTRWH and Artificial Recharge structures.

IMPORTANT DISCLAIMER:
  All dimensions are INDICATIVE only and are based on simplified engineering
  relationships. They represent preliminary sizing for feasibility assessment.

  BEFORE CONSTRUCTION:
  - A qualified civil/structural engineer must verify all dimensions
  - Site-specific soil tests must be conducted
  - Local regulatory approvals (municipal, state groundwater board) must be obtained
  - A detailed engineering drawing must be prepared

Sources:
  CGWB: "Manual on Artificial Recharge of Ground Water", 2007
  IS 15797:2008: Rooftop Rainwater Harvesting (BIS)
  CPHEEO: Manual on Water Supply and Treatment, 2000
  General civil engineering practice

Author: RTRWH Platform Engineering Team
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Literal

from domain.hydrology.assumptions import (
    RECHARGE_PIT_MAX_DEPTH_M,
    RECHARGE_PIT_MIN_DIMENSION_M,
    RECHARGE_TRENCH_TYPICAL_DEPTH_M,
    RECHARGE_TRENCH_TYPICAL_WIDTH_M,
    RECHARGE_TRENCH_MAX_DEPTH_M,
    STORAGE_TANK_FREEBOARD_FRACTION,
    STRUCTURE_FREEBOARD_M,
    GRAVEL_FILL_POROSITY,
)
from domain.hydrology.rtrwh import CalculationTrace


StructureType = Literal[
    "storage_tank",
    "recharge_pit",
    "recharge_trench",
    "recharge_shaft",
    "soak_pit",
]


@dataclass
class StructureDimensions:
    """
    Indicative dimensions for a selected RTRWH or AR structure.
    All dimensions are in metres unless noted.
    """
    structure_type: StructureType
    structure_display_name: str

    # Primary dimensions
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    depth_m: Optional[float] = None
    diameter_m: Optional[float] = None  # For shafts/wells

    # Volume metrics
    gross_volume_m3: Optional[float] = None
    effective_volume_m3: Optional[float] = None  # After fill/freeboard deduction

    # Number of structures
    num_structures: int = 1

    # Design parameters used
    design_volume_m3: float = 0.0
    infiltration_rate_mm_hr: Optional[float] = None
    freeboard_m: float = 0.30

    # Traceability
    calculation_trace: list[CalculationTrace] = None
    warnings: list[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.calculation_trace is None:
            self.calculation_trace = []
        if self.warnings is None:
            self.warnings = []

    @property
    def dimension_string(self) -> str:
        """Human-readable dimension summary."""
        if self.diameter_m:
            return f"Ø {self.diameter_m:.2f} m × {self.depth_m:.2f} m depth"
        parts = []
        if self.length_m:
            parts.append(f"L: {self.length_m:.2f} m")
        if self.width_m:
            parts.append(f"W: {self.width_m:.2f} m")
        if self.depth_m:
            parts.append(f"D: {self.depth_m:.2f} m")
        return " × ".join(parts)

    @property
    def total_effective_volume_m3(self) -> float:
        """Total effective volume accounting for number of structures."""
        return (self.effective_volume_m3 or 0.0) * self.num_structures


def size_storage_tank(
    design_volume_litres: float,
    max_footprint_m2: Optional[float] = None,
    max_depth_m: float = 3.0,
) -> StructureDimensions:
    """
    Calculate indicative dimensions for a rainwater storage tank.

    DESIGN APPROACH:
      Required volume V_req = Design_Volume × (1 + Freeboard_fraction)
      Where freeboard = 10% of volume (standard practice)

      Tank proportioned with depth limited to 3m for:
        - Structural simplicity
        - Pump accessibility
        - Safety

      Area = V_req / Depth
      For a square tank: Side = sqrt(Area)

    Sources:
      CPHEEO Manual on Water Supply and Treatment (2000)
      IS 12288:1987 (Water Storage Tanks)

    Args:
        design_volume_litres: Required storage volume in litres
        max_footprint_m2: Maximum available footprint area (optional)
        max_depth_m: Maximum allowable depth in metres

    Returns:
        StructureDimensions for storage tank
    """
    traces: list[CalculationTrace] = []
    warnings: list[str] = []
    V_design_m3 = design_volume_litres / 1000.0

    # Apply freeboard
    freeboard_fraction = STORAGE_TANK_FREEBOARD_FRACTION
    V_required_m3 = V_design_m3 * (1 + freeboard_fraction)

    traces.append(CalculationTrace(
        formula_name="Required Tank Volume with Freeboard",
        formula_expression="V_required = V_design × (1 + freeboard_fraction)",
        inputs={
            "Design Volume": f"{design_volume_litres:,.0f} L = {V_design_m3:.2f} m³",
            "Freeboard Fraction": f"{freeboard_fraction:.0%} (standard practice)",
        },
        result=f"V_required = {V_required_m3:.2f} m³",
        notes="10% freeboard is standard civil engineering practice for liquid storage.",
    ))

    # Determine depth
    depth = min(max_depth_m, 3.0)

    # Calculate plan area
    plan_area_m2 = V_required_m3 / depth

    # Check against max footprint
    if max_footprint_m2 and plan_area_m2 > max_footprint_m2:
        warnings.append(
            f"Required tank footprint ({plan_area_m2:.1f} m²) exceeds "
            f"available area ({max_footprint_m2:.1f} m²). "
            "Consider: (1) Increasing depth, (2) Multiple tanks, "
            "(3) Reducing design volume."
        )
        plan_area_m2 = max_footprint_m2
        # Recalculate depth
        depth = V_required_m3 / plan_area_m2
        if depth > 4.0:
            warnings.append(
                "Required depth exceeds 4.0 m. Consider underground sump design "
                "with structural engineering review."
            )

    # Square tank dimensions
    side = math.sqrt(plan_area_m2)

    traces.append(CalculationTrace(
        formula_name="Tank Dimensions",
        formula_expression="Area = V / Depth; Side = √Area (square tank)",
        inputs={
            "Required Volume": f"{V_required_m3:.2f} m³",
            "Design Depth": f"{depth:.2f} m",
            "Plan Area": f"{plan_area_m2:.2f} m²",
        },
        result=f"L × W × D = {side:.2f} m × {side:.2f} m × {depth:.2f} m",
        notes="Square plan assumed for simplicity. Rectangular proportions can be adjusted.",
    ))

    gross_vol = side * side * depth
    effective_vol = V_design_m3

    return StructureDimensions(
        structure_type="storage_tank",
        structure_display_name="Underground / Surface Rainwater Storage Tank",
        length_m=round(side, 2),
        width_m=round(side, 2),
        depth_m=round(depth, 2),
        gross_volume_m3=round(gross_vol, 2),
        effective_volume_m3=round(effective_vol, 2),
        design_volume_m3=V_design_m3,
        freeboard_m=round(depth * freeboard_fraction, 2),
        calculation_trace=traces,
        warnings=warnings,
        notes=(
            "INDICATIVE DIMENSIONS ONLY. Actual tank design must account for: "
            "reinforcement requirements, waterproofing, inlet/outlet positions, "
            "overflow provisions, and local regulatory requirements."
        ),
    )


def size_recharge_pit(
    design_volume_m3: float,
    infiltration_rate_mm_hr: float,
    max_depth_m: float = RECHARGE_PIT_MAX_DEPTH_M,
    max_footprint_m2: Optional[float] = None,
) -> StructureDimensions:
    """
    Calculate indicative dimensions for a recharge pit.

    DESIGN APPROACH:
      A recharge pit is an open excavation filled with layered gravel/sand
      to allow infiltration into the sub-soil.

      Required volume = Design volume (storm runoff to be recharged)

      The pit dimensions are sized such that the gravel-filled volume
      provides sufficient storage buffer while runoff infiltrates.

      Effective storage = Gross_volume × Porosity_of_fill
      Where: Porosity of gravel fill ≈ 0.40 (40% void space)

      Plan_Area = Gross_Volume / Depth
      For square pit: Side = sqrt(Plan_Area)

    Sources:
      CGWB Manual on Artificial Recharge (2007), Section 5.4
      IS 15797:2008 Section 8

    Args:
        design_volume_m3: Volume to be recharged per storm event (m³)
        infiltration_rate_mm_hr: Site infiltration rate (mm/hr)
        max_depth_m: Maximum excavation depth (safety limit)
        max_footprint_m2: Available plan area constraint

    Returns:
        StructureDimensions for recharge pit
    """
    traces: list[CalculationTrace] = []
    warnings: list[str] = []

    # Include freeboard
    V_with_freeboard = design_volume_m3 * 1.10  # 10% extra for freeboard

    # The gravel fill has ~40% void space, so gross volume must be larger
    # Gross_volume = Net_design_volume / Porosity
    gross_required_m3 = V_with_freeboard / GRAVEL_FILL_POROSITY

    traces.append(CalculationTrace(
        formula_name="Gross Pit Volume Required",
        formula_expression="V_gross = V_design / Porosity_of_gravel_fill",
        inputs={
            "Design Volume": f"{design_volume_m3:.2f} m³",
            "With Freeboard (10%)": f"{V_with_freeboard:.2f} m³",
            "Gravel Fill Porosity": f"{GRAVEL_FILL_POROSITY:.0%} (CGWB, 2007)",
        },
        result=f"V_gross = {gross_required_m3:.2f} m³",
        notes=(
            "Gravel fill has approximately 40% void space. "
            "Gross pit volume must be 2.5× the storage volume needed."
        ),
    ))

    # Constrain depth
    depth = min(max_depth_m, RECHARGE_PIT_MAX_DEPTH_M)

    # Plan area
    plan_area_m2 = gross_required_m3 / depth

    # Check footprint constraint
    if max_footprint_m2 and plan_area_m2 > max_footprint_m2:
        warnings.append(
            f"Required pit footprint ({plan_area_m2:.1f} m²) exceeds "
            f"available area ({max_footprint_m2:.1f} m²). "
            "Options: (1) Use multiple pits, (2) Use recharge trench, "
            "(3) Accept partial recharge."
        )
        plan_area_m2 = max_footprint_m2

    plan_area_m2 = max(plan_area_m2, RECHARGE_PIT_MIN_DIMENSION_M ** 2)
    side = math.sqrt(plan_area_m2)
    side = max(side, RECHARGE_PIT_MIN_DIMENSION_M)

    # Minimum dimensions check
    if side < 1.5:
        warnings.append(
            f"Calculated pit width ({side:.2f} m) is small. "
            "Minimum practical width for recharge pit is ~1.5 m for construction access."
        )

    actual_gross_vol = side * side * depth
    effective_vol = actual_gross_vol * GRAVEL_FILL_POROSITY

    traces.append(CalculationTrace(
        formula_name="Recharge Pit Dimensions",
        formula_expression="Side = √(V_gross / Depth); Effective = V_gross × Porosity",
        inputs={
            "Gross Volume Required": f"{gross_required_m3:.2f} m³",
            "Design Depth": f"{depth:.2f} m",
            "Plan Area": f"{plan_area_m2:.2f} m²",
        },
        result=(
            f"L × W × D = {side:.2f} m × {side:.2f} m × {depth:.2f} m | "
            f"Effective storage: {effective_vol:.2f} m³"
        ),
    ))

    # Infiltration check
    infiltration_m_hr = infiltration_rate_mm_hr / 1000.0
    infiltration_per_hour_m3 = infiltration_m_hr * plan_area_m2
    drainage_time_hr = effective_vol / infiltration_per_hour_m3 if infiltration_per_hour_m3 > 0 else float('inf')

    traces.append(CalculationTrace(
        formula_name="Estimated Drainage / Recharge Time",
        formula_expression="t = V_effective / (I × A)",
        inputs={
            "Effective Storage": f"{effective_vol:.2f} m³",
            "Infiltration Rate": f"{infiltration_rate_mm_hr:.1f} mm/hr = {infiltration_m_hr:.4f} m/hr",
            "Pit Area": f"{plan_area_m2:.2f} m²",
        },
        result=f"Drainage time ≈ {drainage_time_hr:.1f} hours",
        notes=(
            "For effective recharge, drainage time should ideally be < 24 hours. "
            "Longer drainage times increase waterlogging risk."
        ),
    ))

    if drainage_time_hr > 48:
        warnings.append(
            f"Estimated drainage time ({drainage_time_hr:.0f} hours) is very long. "
            "Pit may not drain before next storm event. "
            "Consider larger infiltration area or recharge shaft."
        )

    return StructureDimensions(
        structure_type="recharge_pit",
        structure_display_name="Gravel-Filled Recharge Pit",
        length_m=round(side, 2),
        width_m=round(side, 2),
        depth_m=round(depth, 2),
        gross_volume_m3=round(actual_gross_vol, 2),
        effective_volume_m3=round(effective_vol, 2),
        design_volume_m3=design_volume_m3,
        infiltration_rate_mm_hr=infiltration_rate_mm_hr,
        freeboard_m=STRUCTURE_FREEBOARD_M,
        calculation_trace=traces,
        warnings=warnings,
        notes=(
            f"INDICATIVE DIMENSIONS ONLY. Recommended layers: "
            f"(1) {STRUCTURE_FREEBOARD_M:.1f} m freeboard, "
            "(2) 0.15 m coarse sand filter, "
            "(3) 0.30 m fine gravel, "
            "(4) Remaining depth — coarse gravel. "
            "Cover with perforated slab or mesh screen."
        ),
    )


def size_recharge_trench(
    design_volume_m3: float,
    infiltration_rate_mm_hr: float,
    available_length_m: Optional[float] = None,
) -> StructureDimensions:
    """
    Calculate indicative dimensions for a recharge trench.

    DESIGN APPROACH:
      A recharge trench is an elongated version of a recharge pit.
      Standard dimensions: 1.0 m wide × 1.5 m deep.
      Length is calculated based on volume requirement.

      V_gross = V_design / Porosity_fill
      Length = V_gross / (Width × Depth)

    Sources:
      CGWB Manual on Artificial Recharge (2007), Section 5.5
    """
    traces: list[CalculationTrace] = []
    warnings: list[str] = []

    width = RECHARGE_TRENCH_TYPICAL_WIDTH_M  # 1.0 m
    depth = RECHARGE_TRENCH_TYPICAL_DEPTH_M  # 1.5 m

    V_gross = design_volume_m3 / GRAVEL_FILL_POROSITY

    traces.append(CalculationTrace(
        formula_name="Trench Volume",
        formula_expression="V_gross = V_design / Gravel_Porosity",
        inputs={
            "Design Volume": f"{design_volume_m3:.2f} m³",
            "Gravel Porosity": f"{GRAVEL_FILL_POROSITY:.0%}",
        },
        result=f"V_gross = {V_gross:.2f} m³",
    ))

    required_length = V_gross / (width * depth)

    traces.append(CalculationTrace(
        formula_name="Required Trench Length",
        formula_expression="Length = V_gross / (Width × Depth)",
        inputs={
            "V_gross": f"{V_gross:.2f} m³",
            "Width (standard)": f"{width:.1f} m",
            "Depth (standard)": f"{depth:.1f} m",
        },
        result=f"Required length = {required_length:.1f} m",
    ))

    if available_length_m and required_length > available_length_m:
        warnings.append(
            f"Required trench length ({required_length:.1f} m) exceeds "
            f"available length ({available_length_m:.1f} m). "
            "Options: (1) Increase depth to 2.0 m, (2) Use multiple parallel trenches."
        )
        required_length = available_length_m
        # Adjust depth
        depth = V_gross / (width * required_length)
        depth = min(depth, RECHARGE_TRENCH_MAX_DEPTH_M)
        warnings.append(
            f"Adjusted depth to {depth:.2f} m with available length {required_length:.1f} m. "
            f"Note: Maximum trench depth is {RECHARGE_TRENCH_MAX_DEPTH_M:.1f} m."
        )

    actual_gross = required_length * width * depth
    effective_vol = actual_gross * GRAVEL_FILL_POROSITY

    return StructureDimensions(
        structure_type="recharge_trench",
        structure_display_name="Gravel-Filled Recharge Trench",
        length_m=round(required_length, 2),
        width_m=round(width, 2),
        depth_m=round(depth, 2),
        gross_volume_m3=round(actual_gross, 2),
        effective_volume_m3=round(effective_vol, 2),
        design_volume_m3=design_volume_m3,
        infiltration_rate_mm_hr=infiltration_rate_mm_hr,
        freeboard_m=STRUCTURE_FREEBOARD_M,
        calculation_trace=traces,
        warnings=warnings,
        notes=(
            "INDICATIVE DIMENSIONS ONLY. Trench to be lined with filter fabric "
            "(geotextile) to prevent clogging. "
            "Provide perforated inlet pipe along trench centreline."
        ),
    )


def size_recharge_shaft(
    design_volume_m3: float,
    infiltration_rate_mm_hr: float,
    groundwater_depth_m: Optional[float] = None,
) -> StructureDimensions:
    """
    Calculate indicative dimensions for a recharge shaft/borewell.

    Used when surface soil has poor permeability but deeper strata are permeable.
    Requires drilling equipment.

    Sources:
      CGWB Manual on Artificial Recharge (2007), Section 5.7
    """
    traces: list[CalculationTrace] = []
    warnings: list[str] = []

    # Standard diameter for recharge shaft
    diameter = 0.50  # metres (standard 500 mm borehole)

    # Depth: extend at least 2m below groundwater table, or to permeable strata
    if groundwater_depth_m:
        recommended_depth = groundwater_depth_m + 2.0
    else:
        recommended_depth = 10.0  # Default if unknown
        warnings.append(
            "Groundwater depth not provided. Shaft depth set to 10 m as default. "
            "Actual depth should be determined by hydrogeological investigation."
        )

    # Volume of shaft
    shaft_radius = diameter / 2.0
    shaft_volume = math.pi * shaft_radius ** 2 * recommended_depth

    traces.append(CalculationTrace(
        formula_name="Recharge Shaft Dimensions",
        formula_expression="V_shaft = π × r² × D",
        inputs={
            "Diameter": f"{diameter:.2f} m (standard)",
            "Depth": f"{recommended_depth:.1f} m",
            "Groundwater Depth": f"{groundwater_depth_m} m BGL" if groundwater_depth_m else "Unknown",
        },
        result=f"V_shaft = {shaft_volume:.2f} m³",
        notes="Volume is for a clean (unlined) borehole. Recharge occurs through entire shaft wall.",
    ))

    warnings.append(
        "Recharge shaft requires drilling by registered bore-well contractor. "
        "Pre-treatment of runoff (sedimentation + filtration) is mandatory. "
        "Central Ground Water Authority/State Board approval may be required."
    )

    return StructureDimensions(
        structure_type="recharge_shaft",
        structure_display_name="Recharge Shaft (Bore-well Type)",
        diameter_m=diameter,
        depth_m=round(recommended_depth, 1),
        gross_volume_m3=round(shaft_volume, 2),
        effective_volume_m3=round(shaft_volume * 0.6, 2),  # 60% effective after casing
        design_volume_m3=design_volume_m3,
        infiltration_rate_mm_hr=infiltration_rate_mm_hr,
        freeboard_m=0.5,
        calculation_trace=traces,
        warnings=warnings,
        notes=(
            "INDICATIVE SIZING ONLY. Requires geophysical survey, test drilling, "
            "and hydrogeological assessment by qualified expert. "
            "NOT a DIY structure — requires professional supervision."
        ),
    )
