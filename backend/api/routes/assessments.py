"""
RTRWH Platform — Assessment CRUD Routes
=======================================
Endpoints for creating, storing, retrieving, listing, and updating site assessments.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from db.database import get_db
from db.models import AssessmentModel
from models.schemas import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentListItem,
    AssessmentDetailResponse,
    CalculationResponse,
)
from services.calculation_service import compute_full_assessment

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])


@router.post("", response_model=AssessmentDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(payload: AssessmentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new site assessment, execute hydrological calculations, and store in database."""
    try:
        # Calculate full results
        calc_result = compute_full_assessment(
            roof_schema=payload.roof,
            rainfall_schema=payload.rainfall,
            demand_schema=payload.demand,
            site_schema=payload.site,
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Computation error: {str(e)}")

    assessment = AssessmentModel(
        site_name=payload.site_name,
        assessor_name=payload.assessor_name,
        organization=payload.organization,
        remarks=payload.remarks,
        roof_area_m2=payload.roof.area_m2,
        annual_rainfall_mm=payload.rainfall.annual_mm,
        annual_harvestable_m3=calc_result.annual_net_harvestable_m3,
        recommended_structure=calc_result.recommended_structure,
        feasibility_label=calc_result.feasibility_label,
        location_data=payload.location.model_dump(),
        roof_data=payload.roof.model_dump(),
        rainfall_data=payload.rainfall.model_dump(),
        demand_data=payload.demand.model_dump() if payload.demand else {},
        site_data=payload.site.model_dump() if payload.site else {},
        calculation_results=calc_result.model_dump(),
    )

    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    return AssessmentDetailResponse(
        id=assessment.id,
        site_name=assessment.site_name,
        assessor_name=assessment.assessor_name,
        organization=assessment.organization,
        remarks=assessment.remarks,
        created_at=assessment.created_at.isoformat(),
        updated_at=assessment.updated_at.isoformat(),
        location=payload.location,
        roof=payload.roof,
        rainfall=payload.rainfall,
        demand=payload.demand or payload.demand.model_construct(),
        site=payload.site or payload.site.model_construct(),
        results=calc_result,
    )


@router.get("", response_model=List[AssessmentListItem])
async def list_assessments(db: AsyncSession = Depends(get_db)):
    """List all site assessments sorted by newest first."""
    result = await db.execute(
        select(AssessmentModel).order_by(desc(AssessmentModel.created_at))
    )
    assessments = result.scalars().all()

    items = []
    for a in assessments:
        loc = a.location_data or {}
        loc_str = loc.get("address") or loc.get("district") or "Coordinates Recorded"
        if loc.get("latitude") and loc.get("longitude"):
            loc_str = f"{loc.get('latitude'):.4f} N, {loc.get('longitude'):.4f} E"
        
        items.append(
            AssessmentListItem(
                id=a.id,
                site_name=a.site_name,
                assessor_name=a.assessor_name,
                created_at=a.created_at.isoformat(),
                location_summary=loc_str,
                roof_area_m2=a.roof_area_m2,
                annual_harvestable_m3=a.annual_harvestable_m3,
                recommended_structure=a.recommended_structure or "Assessment Pending",
                feasibility_label=a.feasibility_label or "HIGH",
            )
        )
    return items


@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
async def get_assessment(assessment_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch complete assessment details, inputs, and calculation outputs by ID."""
    result = await db.execute(
        select(AssessmentModel).where(AssessmentModel.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return AssessmentDetailResponse(
        id=assessment.id,
        site_name=assessment.site_name,
        assessor_name=assessment.assessor_name,
        organization=assessment.organization,
        remarks=assessment.remarks,
        created_at=assessment.created_at.isoformat(),
        updated_at=assessment.updated_at.isoformat(),
        location=assessment.location_data,
        roof=assessment.roof_data,
        rainfall=assessment.rainfall_data,
        demand=assessment.demand_data or {},
        site=assessment.site_data or {},
        results=CalculationResponse(**assessment.calculation_results),
    )


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(assessment_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an assessment by ID."""
    result = await db.execute(
        select(AssessmentModel).where(AssessmentModel.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    await db.delete(assessment)
    await db.commit()
    return None
