"""
Integration Tests — Backend FastAPI Endpoints
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from db.database import init_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure database schema is created before running test client queries."""
    asyncio.run(init_db())


def test_root_endpoint():
    with TestClient(app) as client:
        res = client.get("/")
        assert res.status_code == 200
        assert "HydroRefil" in res.json()["service"]


def test_health_endpoint():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


def test_get_coefficients():
    with TestClient(app) as client:
        res = client.get("/api/hydrology/coefficients")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 4
        keys = [item["key"] for item in data]
        assert "rcc_concrete" in keys
        assert "corrugated_metal" in keys


def test_get_soil_types():
    with TestClient(app) as client:
        res = client.get("/api/hydrology/soil-types")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 5


def test_quick_calculate_endpoint():
    payload = {
        "roof": {
            "area_m2": 250.0,
            "material_key": "rcc_concrete",
        },
        "rainfall": {
            "annual_mm": 1400.0,
        },
        "demand": {
            "num_people": 6,
            "per_capita_demand_lpd": 135.0,
        },
        "site": {
            "soil_type_key": "sandy_loam",
            "groundwater_depth_mbgl": 8.0,
        }
    }
    with TestClient(app) as client:
        res = client.post("/api/hydrology/calculate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["annual_net_harvestable_litres"] > 0
        assert data["recommended_structure"] != ""
        assert len(data["monthly_breakdown"]) == 12
        assert len(data["calculation_trace"]) > 0


def test_assessment_crud():
    with TestClient(app) as client:
        # 1. Create
        create_payload = {
            "site_name": "SIH Demo Community Center",
            "assessor_name": "Er. Vikram Sharma",
            "organization": "Central Ground Water Authority",
            "remarks": "On-spot field verification",
            "location": {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "address": "New Delhi Central",
                "district": "New Delhi",
                "state": "Delhi",
            },
            "roof": {
                "area_m2": 500.0,
                "material_key": "rcc_concrete",
            },
            "rainfall": {
                "annual_mm": 800.0,
            },
            "demand": {
                "num_people": 20,
                "per_capita_demand_lpd": 45.0,
            },
            "site": {
                "soil_type_key": "loam",
                "groundwater_depth_mbgl": 14.0,
            }
        }
        create_res = client.post("/api/assessments", json=create_payload)
        assert create_res.status_code == 201
        created_data = create_res.json()
        assessment_id = created_data["id"]
        assert assessment_id is not None
        assert created_data["site_name"] == "SIH Demo Community Center"
        assert created_data["results"]["annual_net_harvestable_m3"] > 0

        # 2. Get Detail
        get_res = client.get(f"/api/assessments/{assessment_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == assessment_id

        # 3. List
        list_res = client.get("/api/assessments")
        assert list_res.status_code == 200
        items = list_res.json()
        assert any(item["id"] == assessment_id for item in items)

        # 4. Report Summary
        rep_res = client.get(f"/api/reports/{assessment_id}/summary")
        assert rep_res.status_code == 200
        assert rep_res.json()["assessment_id"] == assessment_id

        # 5. Delete
        del_res = client.delete(f"/api/assessments/{assessment_id}")
        assert del_res.status_code == 204
