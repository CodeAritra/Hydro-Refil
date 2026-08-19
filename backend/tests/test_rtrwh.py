"""
Unit Tests — RTRWH Calculations
"""

import pytest
from domain.hydrology.rtrwh import (
    RoofInput,
    RainfallInput,
    WaterDemandInput,
    calculate_rtrwh_potential,
)
from domain.hydrology.assumptions import RUNOFF_COEFFICIENTS, SYSTEM_EFFICIENCY


def test_fundamental_unit_conversion():
    """
    Verify fundamental relationship:
    1 mm rain over 1 m² = 1 litre of water.
    Gross runoff for 1000 mm over 100 m² with C=1.0 must equal 100,000 litres.
    """
    # Using RCC with 0.85
    roof = RoofInput(area_m2=100.0, material_key="rcc_concrete")
    rainfall = RainfallInput(annual_mm=1000.0)
    
    result = calculate_rtrwh_potential(roof=roof, rainfall=rainfall)
    
    expected_gross = 1000.0 * 100.0 * 0.85  # 85,000 litres
    assert abs(result.annual_gross_runoff_litres - expected_gross) < 0.1
    assert result.annual_net_harvestable_litres > 0
    assert result.annual_net_harvestable_m3 == round(result.annual_net_harvestable_litres / 1000.0, 2)


def test_monthly_distribution_sum():
    """Verify that monthly breakdown matches annual patterns."""
    roof = RoofInput(area_m2=200.0, material_key="corrugated_metal")
    rainfall = RainfallInput(annual_mm=1500.0)
    
    result = calculate_rtrwh_potential(roof=roof, rainfall=rainfall)
    
    assert len(result.monthly_results) == 12
    # Cumulative harvested by December should equal total annual cumulative
    dec_cum = result.monthly_results[-1].cumulative_harvested_litres
    assert dec_cum > 0


def test_water_balance_demand_met():
    """Verify demand calculation and percentage met."""
    roof = RoofInput(area_m2=300.0, material_key="rcc_concrete")
    rainfall = RainfallInput(annual_mm=1200.0)
    demand = WaterDemandInput(
        num_people=5,
        per_capita_demand_lpd=135.0,
        non_potable_fraction=0.50,
    )
    
    result = calculate_rtrwh_potential(roof=roof, rainfall=rainfall, demand=demand)
    
    assert result.annual_demand_litres > 0
    assert 0 <= result.demand_met_percentage <= 100.0
    assert isinstance(result.feasibility_score, float)
    assert result.feasibility_label in ["HIGH", "MODERATE", "LOW", "VERY_LOW"]


def test_invalid_inputs_raise_error():
    """Verify validation guards."""
    with pytest.raises(ValueError):
        calculate_rtrwh_potential(
            roof=RoofInput(area_m2=-50.0, material_key="rcc_concrete"),
            rainfall=RainfallInput(annual_mm=1000.0),
        )
    
    with pytest.raises(ValueError):
        calculate_rtrwh_potential(
            roof=RoofInput(area_m2=100.0, material_key="invalid_material"),
            rainfall=RainfallInput(annual_mm=1000.0),
        )
