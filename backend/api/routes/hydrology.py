"""
RTRWH Platform — Hydrology Routes
==================================
Endpoints for rapid on-spot hydrological calculations, runoff coefficients lookup,
soil types, and engineering assumptions.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import QuickCalculateRequest, CalculationResponse
from services.calculation_service import compute_full_assessment
from domain.hydrology.assumptions import (
    RUNOFF_COEFFICIENTS,
    ROOF_MATERIAL_DISPLAY,
    SOIL_INFILTRATION_RATES,
    SOIL_TYPE_DISPLAY,
    WATER_DEMAND_PER_CAPITA,
    SYSTEM_EFFICIENCY,
    FIRST_FLUSH_DEPTH_MM,
)

router = APIRouter(prefix="/api/hydrology", tags=["Hydrology"])


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_hydrology(payload: QuickCalculateRequest):
    """
    Execute complete hydrological assessment on-the-fly without saving to database.
    Ideal for rapid on-site what-if analysis and client-side integration.
    """
    try:
        results = compute_full_assessment(
            roof_schema=payload.roof,
            rainfall_schema=payload.rainfall,
            demand_schema=payload.demand,
            site_schema=payload.site,
        )
        return results
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hydrological calculation error: {str(e)}")


@router.get("/coefficients")
async def get_runoff_coefficients():
    """Retrieve all standard roof materials, runoff coefficients, ranges, and citations."""
    return [
        {
            "key": k,
            "display_name": ROOF_MATERIAL_DISPLAY.get(k, a.name),
            "value": a.value,
            "range_min": a.range_min,
            "range_max": a.range_max,
            "source": a.source,
            "description": a.description,
            "confidence": a.confidence,
            "note": a.note,
        }
        for k, a in RUNOFF_COEFFICIENTS.items()
    ]


@router.get("/soil-types")
async def get_soil_types():
    """Retrieve standard soil types, typical infiltration rates, and sources."""
    return [
        {
            "key": k,
            "display_name": SOIL_TYPE_DISPLAY.get(k, a.name),
            "infiltration_rate_mm_hr": a.value,
            "range_min": a.range_min,
            "range_max": a.range_max,
            "source": a.source,
            "description": a.description,
            "confidence": a.confidence,
            "note": a.note,
        }
        for k, a in SOIL_INFILTRATION_RATES.items()
    ]


@router.get("/assumptions")
async def get_all_assumptions():
    """Retrieve full engineering assumptions registry with source citations."""
    return {
        "system_efficiency": {
            "name": SYSTEM_EFFICIENCY.name,
            "value": SYSTEM_EFFICIENCY.value,
            "source": SYSTEM_EFFICIENCY.source,
            "description": SYSTEM_EFFICIENCY.description,
            "note": SYSTEM_EFFICIENCY.note,
        },
        "first_flush_depth_mm": {
            "name": FIRST_FLUSH_DEPTH_MM.name,
            "value": FIRST_FLUSH_DEPTH_MM.value,
            "source": FIRST_FLUSH_DEPTH_MM.source,
            "description": FIRST_FLUSH_DEPTH_MM.description,
            "note": FIRST_FLUSH_DEPTH_MM.note,
        },
        "water_demand_standards": {
            k: {
                "name": a.name,
                "value_lpcd": a.value,
                "source": a.source,
                "description": a.description,
            }
            for k, a in WATER_DEMAND_PER_CAPITA.items()
        },
    }
