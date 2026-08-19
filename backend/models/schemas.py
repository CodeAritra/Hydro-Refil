"""
RTRWH Platform — API Schemas
=============================
Pydantic schemas for data validation, assessment requests, responses,
and hydrological calculations.
"""

from typing import List, Dict, Optional, Any, Tuple
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Common / Nested Schemas
# -----------------------------------------------------------------------------

class LocationSchema(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    coordinates: Optional[List[Tuple[float, float]]] = Field(
        None, description="Optional polygon coordinate pairs [[lng, lat], ...]"
    )


class RoofDetailsSchema(BaseModel):
    area_m2: float = Field(..., gt=0, le=100000, description="Roof area in square meters")
    material_key: str = Field(
        "rcc_concrete",
        description="Material key: rcc_concrete, corrugated_metal, clay_tile, asbestos_cement, thatch_grass, green_roof"
    )
    slope_deg: Optional[float] = Field(0.0, ge=0, le=90)
    num_downpipes: Optional[int] = Field(1, ge=1, le=50)
    has_first_flush_diverter: Optional[bool] = True


class RainfallDetailsSchema(BaseModel):
    annual_mm: float = Field(..., ge=0, le=15000, description="Annual rainfall in mm")
    monthly_mm: Optional[Dict[str, float]] = Field(
        None, description="Dictionary of 12 monthly rainfall values in mm"
    )
    data_source: Optional[str] = "user_provided"


class DemandDetailsSchema(BaseModel):
    num_people: Optional[int] = Field(0, ge=0, le=100000)
    per_capita_demand_lpd: Optional[float] = Field(135.0, gt=0, le=1000)
    occupancy_type: Optional[str] = "domestic_urban"
    additional_demand_lpm: Optional[float] = Field(0.0, ge=0)
    non_potable_fraction: Optional[float] = Field(0.40, ge=0.0, le=1.0)


class SiteConditionsSchema(BaseModel):
    soil_type_key: Optional[str] = "unknown"
    infiltration_rate_mm_hr: Optional[float] = Field(None, ge=0, le=1000)
    infiltration_data_source: Optional[str] = "assumed"
    groundwater_depth_mbgl: Optional[float] = Field(None, ge=0, le=500)
    groundwater_data_source: Optional[str] = "unknown"
    available_area_m2: Optional[float] = Field(None, ge=0)
    is_paved_area: Optional[bool] = False
    distance_to_septic_m: Optional[float] = Field(None, ge=0)
    distance_to_well_m: Optional[float] = Field(None, ge=0)


# -----------------------------------------------------------------------------
# Calculation Request & Response Schemas
# -----------------------------------------------------------------------------

class QuickCalculateRequest(BaseModel):
    roof: RoofDetailsSchema
    rainfall: RainfallDetailsSchema
    demand: Optional[DemandDetailsSchema] = None
    site: Optional[SiteConditionsSchema] = None


class MonthlyDataPoint(BaseModel):
    month: str
    rainfall_mm: float
    gross_runoff_litres: float
    net_harvestable_litres: float
    demand_litres: float
    balance_litres: float
    cumulative_harvested_litres: float


class StructureDimensionsSchema(BaseModel):
    structure_type: str
    structure_display_name: str
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    depth_m: Optional[float] = None
    diameter_m: Optional[float] = None
    gross_volume_m3: Optional[float] = None
    effective_volume_m3: Optional[float] = None
    num_structures: int = 1
    design_volume_m3: float = 0.0
    infiltration_rate_mm_hr: Optional[float] = None
    freeboard_m: float = 0.30
    dimension_string: str = ""
    notes: str = ""


class TraceItemSchema(BaseModel):
    formula_name: str
    formula_expression: str
    inputs: Dict[str, str]
    result: str
    notes: Optional[str] = None


class CalculationResponse(BaseModel):
    status: str = "success"
    # RTRWH Summary
    annual_gross_runoff_litres: float
    annual_net_harvestable_litres: float
    annual_net_harvestable_m3: float
    first_flush_annual_loss_litres: float
    runoff_coefficient: float
    system_efficiency: float
    feasibility_score: float
    feasibility_label: str
    monthly_breakdown: List[MonthlyDataPoint]
    
    # Water balance
    annual_demand_litres: float
    annual_surplus_deficit_litres: float
    demand_met_percentage: float

    # Recharge Assessment
    annual_recharge_potential_litres: float
    annual_recharge_potential_m3: float
    recharge_feasible: bool
    recharge_feasibility_label: str
    recharge_feasibility_reason: str
    infiltration_rate_mm_hr: float
    infiltration_data_source: str
    groundwater_depth_adequate: bool

    # Recommendation
    recommended_structure: str
    recommendation_reason: str
    primary_dimensions: StructureDimensionsSchema
    secondary_structure: Optional[str] = None
    secondary_dimensions: Optional[StructureDimensionsSchema] = None
    confidence: str
    decision_factors: List[str]

    # Transparency & Engineering
    warnings: List[str]
    calculation_trace: List[TraceItemSchema]


# -----------------------------------------------------------------------------
# Assessment Entity Schemas
# -----------------------------------------------------------------------------

class AssessmentCreate(BaseModel):
    site_name: str = Field(..., min_length=1, max_length=255)
    assessor_name: Optional[str] = "Field Engineer"
    organization: Optional[str] = None
    remarks: Optional[str] = None
    location: LocationSchema = Field(default_factory=LocationSchema)
    roof: RoofDetailsSchema
    rainfall: RainfallDetailsSchema
    demand: Optional[DemandDetailsSchema] = Field(default_factory=DemandDetailsSchema)
    site: Optional[SiteConditionsSchema] = Field(default_factory=SiteConditionsSchema)


class AssessmentUpdate(BaseModel):
    site_name: Optional[str] = None
    assessor_name: Optional[str] = None
    organization: Optional[str] = None
    remarks: Optional[str] = None
    location: Optional[LocationSchema] = None
    roof: Optional[RoofDetailsSchema] = None
    rainfall: Optional[RainfallDetailsSchema] = None
    demand: Optional[DemandDetailsSchema] = None
    site: Optional[SiteConditionsSchema] = None


class AssessmentListItem(BaseModel):
    id: str
    site_name: str
    assessor_name: Optional[str] = None
    created_at: str
    location_summary: str
    roof_area_m2: float
    annual_harvestable_m3: float
    recommended_structure: str
    feasibility_label: str


class AssessmentDetailResponse(BaseModel):
    id: str
    site_name: str
    assessor_name: Optional[str]
    organization: Optional[str]
    remarks: Optional[str]
    created_at: str
    updated_at: str
    location: LocationSchema
    roof: RoofDetailsSchema
    rainfall: RainfallDetailsSchema
    demand: DemandDetailsSchema
    site: SiteConditionsSchema
    results: CalculationResponse
