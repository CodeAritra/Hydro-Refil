"""
RTRWH Platform — Report Routes
===============================
Endpoints for generating assessment summaries, printable reports, and data exports.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.database import get_db
from db.models import AssessmentModel

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{assessment_id}/summary")
async def get_report_summary(assessment_id: str, db: AsyncSession = Depends(get_db)):
    """Generate structured report payload suitable for document generation."""
    result = await db.execute(
        select(AssessmentModel).where(AssessmentModel.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    calc = assessment.calculation_results or {}
    roof = assessment.roof_data or {}
    rain = assessment.rainfall_data or {}
    dims = calc.get("primary_dimensions", {})

    return {
        "assessment_id": assessment.id,
        "site_name": assessment.site_name,
        "assessor_name": assessment.assessor_name,
        "date": assessment.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "location": assessment.location_data,
        "metrics": {
            "roof_area_m2": roof.get("area_m2"),
            "roof_material": roof.get("material_key"),
            "annual_rainfall_mm": rain.get("annual_mm"),
            "annual_harvest_litres": calc.get("annual_net_harvestable_litres"),
            "annual_harvest_m3": calc.get("annual_net_harvestable_m3"),
            "annual_demand_litres": calc.get("annual_demand_litres"),
            "demand_met_pct": calc.get("demand_met_percentage"),
            "recharge_potential_m3": calc.get("annual_recharge_potential_m3"),
        },
        "recommendation": {
            "structure": calc.get("recommended_structure"),
            "reason": calc.get("recommendation_reason"),
            "dimension_string": dims.get("dimension_string"),
            "effective_volume_m3": dims.get("effective_volume_m3"),
            "confidence": calc.get("confidence"),
        },
        "warnings": calc.get("warnings", []),
        "disclaimer": (
            "This report is generated for preliminary RTRWH feasibility assessment only. "
            "Site-specific geotechnical, infiltration, and structural verification by a "
            "qualified engineer is required prior to any construction activity."
        ),
    }
