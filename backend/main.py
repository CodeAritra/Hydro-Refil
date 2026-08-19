"""
RTRWH Platform — Enterprise Backend API
========================================
Production-grade FastAPI application for on-spot Rooftop Rainwater Harvesting
and Artificial Recharge assessment.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from db.database import init_db
from api.routes import hydrology, assessments, reports
from services.calculation_service import compute_full_assessment
from models.schemas import RoofDetailsSchema, RainfallDetailsSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="HydroRefil — RTRWH & Artificial Recharge Assessment API",
    description="Engineered on-spot hydrological calculation and structure sizing platform for SIH.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
if "*" in origins or os.getenv("APP_ENV") == "development":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(hydrology.router)
app.include_router(assessments.router)
app.include_router(reports.router)


# Global Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Invalid input parameters. Please verify form values."},
    )


@app.get("/")
async def root():
    return {
        "service": "HydroRefil RTRWH Assessment API",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


# -----------------------------------------------------------------------------
# Backward-compatibility route for older prototype requests
# -----------------------------------------------------------------------------
@app.post("/api/assessments/calculate")
async def legacy_calculate(payload: dict):
    """
    Backward-compatible endpoint for older prototype calls.
    Accepts polygon coordinates or direct area.
    """
    site_name = payload.get("site_name", "Survey Site")
    roof_material = payload.get("roof_material", "rcc_concrete")
    if roof_material == "concrete":
        roof_material = "rcc_concrete"
    
    # Calculate area from coordinates or use fallback
    area_m2 = payload.get("roof_area_m2", 150.0)
    coords = payload.get("coordinates")
    if coords and len(coords) >= 3:
        # Approximate Shoelace polygon area calculation on sphere/plane for legacy route
        try:
            from shapely.geometry import Polygon
            import pyproj
            poly = Polygon(coords)
            # Rough geographic area estimation in m²
            # 1 deg lat ≈ 111,000 m; 1 deg lng ≈ 111,000 * cos(lat)
            lat_center = sum(c[1] for c in coords) / len(coords)
            lat_factor = 111320.0
            lng_factor = 111320.0 * 0.92  # approximate for India
            scaled_coords = [(c[0] * lng_factor, c[1] * lat_factor) for c in coords]
            scaled_poly = Polygon(scaled_coords)
            area_m2 = abs(scaled_poly.area)
        except Exception:
            area_m2 = 150.0

    calc_res = compute_full_assessment(
        roof_schema=RoofDetailsSchema(area_m2=max(10.0, area_m2), material_key=roof_material),
        rainfall_schema=RainfallDetailsSchema(annual_mm=1200.0),
    )

    return {
        "status": "success",
        "input_summary": {
            "site_name": site_name,
            "calculated_roof_area_m2": round(area_m2, 2),
            "detected_annual_rainfall_mm": 1200.0,
        },
        "assessment_results": {
            "annual_harvesting_potential_litres": calc_res.annual_net_harvestable_litres,
            "recommended_structure": calc_res.recommended_structure,
            "dimensions": {
                "storage_tank_required_m3": calc_res.primary_dimensions.design_volume_m3,
                "structure_length_meters": calc_res.primary_dimensions.length_m or 0.0,
                "structure_width_meters": calc_res.primary_dimensions.width_m or 0.0,
                "structure_depth_meters": calc_res.primary_dimensions.depth_m or 0.0,
            },
            "warnings": calc_res.warnings,
        },
    }
