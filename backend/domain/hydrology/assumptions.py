"""
RTRWH Platform — Engineering Assumptions Registry
==================================================
Centralized, documented, and traceable engineering assumptions.

All assumptions must have:
  - A human-readable description
  - A value with explicit unit
  - A source reference (standard, manual, institution)
  - A confidence rating
  - A review/validation note

IMPORTANT: These are PRELIMINARY ASSESSMENT values only.
Site-specific field verification is required before any construction.

Sources referenced:
  - CGWB: Central Ground Water Board, "Master Plan for Artificial Recharge
    to Groundwater in India", 2005/2013
  - IS 15797:2008: Bureau of Indian Standards, "Rooftop Rainwater Harvesting"
  - IS 1172:1993: BIS, "Code of Basic Requirements for Water Supply, Drainage
    and Sanitation"
  - CPHEEO: Central Public Health and Environmental Engineering Organisation,
    "Manual on Water Supply and Treatment", 2000
  - Jal Jeevan Mission: GoI guidelines, 2019
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Assumption:
    """
    Represents a single documented engineering assumption.
    Frozen to prevent accidental mutation during calculation.
    """
    name: str
    value: float
    unit: str
    source: str
    description: str
    confidence: str  # HIGH | MEDIUM | LOW | VERY_LOW
    note: Optional[str] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None


# =============================================================================
# RUNOFF COEFFICIENTS
# =============================================================================
# Source: CGWB Master Plan (2005, 2013), IS 15797:2008
# Definition: Fraction of rainfall that becomes runoff from the roof surface
# Range: 0 (total absorption) to 1.0 (total runoff)
# Note: Actual value depends on condition, slope, and maintenance of surface

RUNOFF_COEFFICIENTS: dict[str, Assumption] = {
    "rcc_concrete": Assumption(
        name="Runoff Coefficient — RCC / Concrete Roof",
        value=0.85,
        range_min=0.80,
        range_max=0.90,
        unit="dimensionless",
        source="CGWB Master Plan for Artificial Recharge (2005), Table 3.2; IS 15797:2008",
        description=(
            "Reinforced Cement Concrete (RCC) flat or mildly sloped rooftop. "
            "Well-maintained surface with no significant ponding, moss, or algae growth."
        ),
        confidence="HIGH",
        note="Reduce to 0.80 if roof has significant weathering or drainage problems.",
    ),
    "corrugated_metal": Assumption(
        name="Runoff Coefficient — Corrugated Metal Sheet",
        value=0.90,
        range_min=0.85,
        range_max=0.95,
        unit="dimensionless",
        source="CGWB Master Plan (2005); IS 15797:2008; Ministry of Jal Shakti guidelines",
        description=(
            "Corrugated Galvanized Iron (CGI), Galvalume (PPGI), or tin sheet roofing. "
            "High runoff efficiency due to smooth, impermeable surface."
        ),
        confidence="HIGH",
        note="Highest coefficient of common roof types. Suitable for quality recharge.",
    ),
    "clay_tile": Assumption(
        name="Runoff Coefficient — Clay Tile Roof",
        value=0.80,
        range_min=0.75,
        range_max=0.85,
        unit="dimensionless",
        source="CGWB Master Plan (2005); Ministry of Jal Shakti RTRWH guidelines",
        description=(
            "Clay tiles, country tiles, or mangalore tiles. "
            "Some absorption in tile joints reduces coefficient vs. RCC."
        ),
        confidence="MEDIUM",
        note="Use lower bound (0.75) for old or moss-covered tiles.",
    ),
    "asbestos_cement": Assumption(
        name="Runoff Coefficient — Asbestos Cement Sheet",
        value=0.75,
        range_min=0.70,
        range_max=0.80,
        unit="dimensionless",
        source="CGWB Master Plan (2005)",
        description=(
            "Asbestos cement corrugated sheet (AC sheet) roofing. "
            "Note: WHO and Indian regulations discourage asbestos for potable water harvesting."
        ),
        confidence="MEDIUM",
        note=(
            "CAUTION: Asbestos cement should NOT be used for drinking water harvesting "
            "due to fibre leaching risk. Suitable for recharge/non-potable use only."
        ),
    ),
    "thatch_grass": Assumption(
        name="Runoff Coefficient — Thatch / Grass Roof",
        value=0.40,
        range_min=0.30,
        range_max=0.50,
        unit="dimensionless",
        source="ASSUMPTION — REQUIRES FIELD/DOMAIN VALIDATION",
        description="Traditional thatched or grass roofing. High absorption, very variable.",
        confidence="LOW",
        note="Not recommended as primary catchment for RTRWH due to contamination risk.",
    ),
    "green_roof": Assumption(
        name="Runoff Coefficient — Green / Vegetated Roof",
        value=0.30,
        range_min=0.15,
        range_max=0.50,
        unit="dimensionless",
        source="ASSUMPTION — REQUIRES FIELD/DOMAIN VALIDATION",
        description=(
            "Vegetated green roof system. "
            "Highly variable depending on substrate depth, plant type, and saturation state."
        ),
        confidence="LOW",
        note="Consult specialist for green roof RTRWH design.",
    ),
}

# Display mapping for UI dropdowns
ROOF_MATERIAL_DISPLAY: dict[str, str] = {
    "rcc_concrete": "RCC / Concrete Flat Roof",
    "corrugated_metal": "Corrugated Metal Sheet (CGI / Galvalume)",
    "clay_tile": "Clay / Country / Mangalore Tile",
    "asbestos_cement": "Asbestos Cement Sheet (AC Sheet)",
    "thatch_grass": "Thatch / Grass Roof",
    "green_roof": "Green / Vegetated Roof",
}

# =============================================================================
# SYSTEM EFFICIENCY
# =============================================================================
SYSTEM_EFFICIENCY = Assumption(
    name="RTRWH System Collection Efficiency",
    value=0.85,
    range_min=0.70,
    range_max=0.95,
    unit="dimensionless",
    source=(
        "CGWB (2007), Representative practice for Indian conditions; "
        "IS 15797:2008 Section 7"
    ),
    description=(
        "Overall system efficiency accounting for: first-flush diversion losses, "
        "pipe/gutter transmission losses, evaporation from open tanks, "
        "and minor spillage. Assumes a properly maintained system."
    ),
    confidence="MEDIUM",
    note=(
        "Range 0.70 (poorly maintained) to 0.95 (well-designed closed system). "
        "Default 0.85 represents a moderately well-maintained open storage system."
    ),
)

# =============================================================================
# FIRST FLUSH
# =============================================================================
FIRST_FLUSH_DEPTH_MM = Assumption(
    name="First Flush Diverter Volume",
    value=2.0,
    range_min=1.5,
    range_max=2.5,
    unit="mm equivalent over roof area",
    source="IS 15797:2008 Clause 6; Ministry of Jal Shakti Jal Shakti Abhiyan guidelines",
    description=(
        "Volume of initial roof runoff to be diverted as first flush. "
        "First flush carries the maximum concentration of particulates, "
        "organic matter, bird droppings, and atmospheric pollutants. "
        "Formula: First Flush Volume (litres) = 2.0 mm × Roof Area (m²)"
    ),
    confidence="MEDIUM",
    note=(
        "Increase to 2.5 mm for roofs near industrial areas, busy roads, "
        "or areas with high air pollution. "
        "First flush diverter is mandatory for potable harvesting."
    ),
)

# =============================================================================
# WATER DEMAND
# =============================================================================
WATER_DEMAND_PER_CAPITA: dict[str, Assumption] = {
    "domestic_urban": Assumption(
        name="Urban Domestic Per-Capita Water Demand",
        value=135.0,
        range_min=100.0,
        range_max=200.0,
        unit="litres/person/day",
        source="IS 1172:1993 Table 1; CPHEEO Manual on Water Supply and Treatment (2000)",
        description="Standard urban residential water supply per person per day.",
        confidence="HIGH",
        note="135 lpcd is the standard Indian norm for urban areas per IS 1172.",
    ),
    "domestic_rural": Assumption(
        name="Rural Domestic Per-Capita Water Demand",
        value=70.0,
        range_min=40.0,
        range_max=100.0,
        unit="litres/person/day",
        source="Jal Jeevan Mission guidelines (2019); CPHEEO",
        description="Standard rural residential water supply per person per day.",
        confidence="HIGH",
        note="55 lpcd (Jal Jeevan Mission minimum) to 70 lpcd typical.",
    ),
    "office": Assumption(
        name="Office Building Per-Occupant Water Demand",
        value=45.0,
        range_min=25.0,
        range_max=65.0,
        unit="litres/person/day",
        source="IS 1172:1993 Table 1",
        description="Water demand for office buildings per occupant (working hours).",
        confidence="HIGH",
    ),
    "school": Assumption(
        name="School Per-Student Water Demand",
        value=45.0,
        range_min=25.0,
        range_max=60.0,
        unit="litres/student/day",
        source="IS 1172:1993 Table 1",
        description="Water demand for schools per student per day.",
        confidence="HIGH",
        note="Includes drinking, sanitation, and cleaning. Varies with school facilities.",
    ),
    "hospital": Assumption(
        name="Hospital Per-Bed Water Demand",
        value=450.0,
        range_min=300.0,
        range_max=600.0,
        unit="litres/bed/day",
        source="IS 1172:1993 Table 1; CPHEEO",
        description="Water demand for hospitals per bed per day.",
        confidence="MEDIUM",
    ),
}

# =============================================================================
# GROUNDWATER / RECHARGE
# =============================================================================
MIN_GROUNDWATER_DEPTH_FOR_RECHARGE_M = Assumption(
    name="Minimum Groundwater Depth for Safe Artificial Recharge",
    value=3.0,
    unit="metres below ground level (mbgl)",
    source=(
        "CGWB Manual on Artificial Recharge (2007), Section 5.3; "
        "State Groundwater Board guidelines (representative)"
    ),
    description=(
        "If groundwater table is shallower than this depth, "
        "standard recharge pits/trenches are not recommended as "
        "they may cause waterlogging, structural damage, or contamination."
    ),
    confidence="MEDIUM",
    note=(
        "ASSUMPTION — Actual threshold depends on local geology, seasonal variation, "
        "and regulatory requirements. Field verification essential."
    ),
)

# =============================================================================
# SOIL INFILTRATION RATES (Representative — Field Test Required)
# =============================================================================
SOIL_INFILTRATION_RATES: dict[str, Assumption] = {
    "gravel_coarse_sand": Assumption(
        name="Infiltration Rate — Gravel / Coarse Sand",
        value=50.0,
        range_min=30.0,
        range_max=100.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007), Table 4.1",
        description="Gravel and coarse sand — very high infiltration capacity.",
        confidence="LOW",
        note="ASSUMPTION — Field percolation/infiltration test strongly recommended.",
    ),
    "fine_sand": Assumption(
        name="Infiltration Rate — Fine / Medium Sand",
        value=25.0,
        range_min=10.0,
        range_max=50.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007), Table 4.1",
        description="Fine to medium sand — high infiltration capacity.",
        confidence="LOW",
        note="ASSUMPTION — Field test required.",
    ),
    "sandy_loam": Assumption(
        name="Infiltration Rate — Sandy Loam",
        value=12.0,
        range_min=5.0,
        range_max=20.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007)",
        description="Sandy loam soil — moderate infiltration.",
        confidence="LOW",
        note="ASSUMPTION — Field test required.",
    ),
    "loam": Assumption(
        name="Infiltration Rate — Loam",
        value=7.0,
        range_min=3.0,
        range_max=12.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007)",
        description="Loam soil — moderate infiltration capacity.",
        confidence="LOW",
        note="ASSUMPTION — Field test required.",
    ),
    "clay_loam": Assumption(
        name="Infiltration Rate — Clay Loam",
        value=3.0,
        range_min=1.0,
        range_max=6.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007)",
        description="Clay loam soil — low infiltration capacity.",
        confidence="LOW",
        note="ASSUMPTION — Field test required.",
    ),
    "clay": Assumption(
        name="Infiltration Rate — Clay",
        value=1.0,
        range_min=0.5,
        range_max=3.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007)",
        description="Clay soil — very low infiltration. Recharge pits generally not suitable.",
        confidence="LOW",
        note="ASSUMPTION — Recharge shaft with deep injection may be more appropriate.",
    ),
    "black_cotton": Assumption(
        name="Infiltration Rate — Black Cotton Soil (Vertisol)",
        value=0.5,
        range_min=0.1,
        range_max=2.0,
        unit="mm/hr",
        source="CGWB Manual on Artificial Recharge (2007); State Groundwater Board reports",
        description=(
            "Expansive black cotton soil (Vertisol) — very low and variable infiltration. "
            "Swells when wet, causing structural issues for in-ground structures."
        ),
        confidence="LOW",
        note="ASSUMPTION — Special design required. Surface storage preferred.",
    ),
    "unknown": Assumption(
        name="Infiltration Rate — Unknown Soil",
        value=5.0,
        unit="mm/hr",
        source="ASSUMPTION — CONSERVATIVE DEFAULT. REQUIRES FIELD VALIDATION.",
        description="Conservative assumption when soil type is unknown.",
        confidence="VERY_LOW",
        note=(
            "ASSUMPTION — REQUIRES FIELD/DOMAIN VALIDATION. "
            "Do not use for final design. Conduct infiltration/percolation test."
        ),
    ),
}

SOIL_TYPE_DISPLAY: dict[str, str] = {
    "gravel_coarse_sand": "Gravel / Coarse Sand",
    "fine_sand": "Fine / Medium Sand",
    "sandy_loam": "Sandy Loam",
    "loam": "Loam",
    "clay_loam": "Clay Loam",
    "clay": "Clay",
    "black_cotton": "Black Cotton Soil (Vertisol)",
    "unknown": "Unknown / Not Tested",
}

# =============================================================================
# STRUCTURE SIZING CONSTRAINTS
# =============================================================================
RECHARGE_PIT_MAX_DEPTH_M = 3.0  # metres (safety and practicality limit)
RECHARGE_PIT_MIN_DIMENSION_M = 1.0  # minimum plan dimension
RECHARGE_TRENCH_TYPICAL_DEPTH_M = 1.5
RECHARGE_TRENCH_TYPICAL_WIDTH_M = 1.0
RECHARGE_TRENCH_MAX_DEPTH_M = 2.0
STORAGE_TANK_FREEBOARD_FRACTION = 0.10  # 10% freeboard above calculated volume
STRUCTURE_FREEBOARD_M = 0.30  # 0.30 m freeboard for open recharge structures
GRAVEL_FILL_POROSITY = 0.40  # Effective porosity of gravel fill in recharge structures

# =============================================================================
# MONTHLY RAINFALL DISTRIBUTION
# =============================================================================
# Default monthly distribution coefficients (fraction of annual total)
# Based on typical Indian SW monsoon pattern.
# NOTE: This is a REPRESENTATIVE pattern only. Actual distribution varies
# significantly by region and should be replaced with local data.
MONTHLY_DISTRIBUTION_INDIA_TYPICAL: dict[str, float] = {
    "jan": 0.010,  # January
    "feb": 0.010,  # February
    "mar": 0.012,  # March
    "apr": 0.020,  # April
    "may": 0.030,  # May (pre-monsoon)
    "jun": 0.130,  # June (monsoon onset)
    "jul": 0.240,  # July (peak monsoon)
    "aug": 0.200,  # August
    "sep": 0.140,  # September
    "oct": 0.070,  # October (retreating monsoon)
    "nov": 0.020,  # November
    "dec": 0.010,  # December
}

# Verify distribution sums to approximately 1.0
_dist_sum = sum(MONTHLY_DISTRIBUTION_INDIA_TYPICAL.values())
assert abs(_dist_sum - 0.892) < 0.01 or abs(_dist_sum - 1.0) < 0.01, (
    f"Monthly distribution must sum to ~1.0, got {_dist_sum}"
)

# Normalize if needed
_dist_sum_check = sum(MONTHLY_DISTRIBUTION_INDIA_TYPICAL.values())
if abs(_dist_sum_check - 1.0) > 0.01:
    _factor = 1.0 / _dist_sum_check
    MONTHLY_DISTRIBUTION_INDIA_TYPICAL = {
        k: round(v * _factor, 4)
        for k, v in MONTHLY_DISTRIBUTION_INDIA_TYPICAL.items()
    }
