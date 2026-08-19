"""
Unit Tests — Recommendation Engine
"""

from domain.hydrology.rtrwh import RoofInput, RainfallInput, calculate_rtrwh_potential
from domain.hydrology.recharge import SiteConditionsInput, calculate_recharge_potential
from domain.hydrology.recommendation import generate_recommendation


def test_recommendation_high_water_table_recommends_storage():
    roof = RoofInput(area_m2=200.0, material_key="rcc_concrete")
    rainfall = RainfallInput(annual_mm=1400.0)
    rtrwh = calculate_rtrwh_potential(roof=roof, rainfall=rainfall)
    
    # High water table (2.0 m BGL < 3.0 m limit)
    site = SiteConditionsInput(
        soil_type_key="sandy_loam",
        groundwater_depth_mbgl=2.0,
    )
    recharge = calculate_recharge_potential(rtrwh.annual_net_harvestable_litres, site=site)
    
    rec = generate_recommendation(rtrwh_result=rtrwh, recharge_result=recharge, site=site)
    
    assert rec.primary_structure_type == "storage_tank"
    assert "shallow" in rec.recommendation_reason.lower() or "groundwater" in rec.recommendation_reason.lower()
    assert len(rec.decision_factors) > 0


def test_recommendation_good_soil_recommends_pit():
    roof = RoofInput(area_m2=150.0, material_key="rcc_concrete")
    rainfall = RainfallInput(annual_mm=1000.0)
    rtrwh = calculate_rtrwh_potential(roof=roof, rainfall=rainfall)
    
    # Good infiltration + deep water table
    site = SiteConditionsInput(
        soil_type_key="fine_sand",
        groundwater_depth_mbgl=15.0,
    )
    recharge = calculate_recharge_potential(rtrwh.annual_net_harvestable_litres, site=site)
    
    rec = generate_recommendation(rtrwh_result=rtrwh, recharge_result=recharge, site=site)
    
    assert rec.primary_structure_type == "recharge_pit"
    assert rec.confidence in ["HIGH", "MEDIUM"]
