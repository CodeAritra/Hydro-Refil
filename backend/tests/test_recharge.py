"""
Unit Tests — Artificial Recharge Calculations
"""

from domain.hydrology.recharge import (
    SiteConditionsInput,
    calculate_recharge_potential,
)


def test_shallow_groundwater_not_recommended():
    """Verify that groundwater depth < 3m triggers NOT_RECOMMENDED for recharge."""
    site = SiteConditionsInput(
        soil_type_key="sandy_loam",
        groundwater_depth_mbgl=2.0,  # < 3.0 m limit
    )
    result = calculate_recharge_potential(
        annual_runoff_available_litres=100000.0,
        site=site,
    )
    assert result.recharge_feasible is False
    assert result.feasibility_label == "NOT_RECOMMENDED"
    assert "shallow" in result.feasibility_reason.lower() or "waterlogging" in result.feasibility_reason.lower()


def test_good_infiltration_recharge_feasible():
    """Verify high infiltration rate enables feasible recharge assessment."""
    site = SiteConditionsInput(
        soil_type_key="fine_sand",
        groundwater_depth_mbgl=12.0,
        available_area_m2=20.0,
    )
    result = calculate_recharge_potential(
        annual_runoff_available_litres=150000.0,
        site=site,
    )
    assert result.recharge_feasible is True
    assert result.annual_recharge_potential_litres > 0
    assert result.annual_recharge_potential_m3 > 0
    assert result.groundwater_depth_adequate is True
