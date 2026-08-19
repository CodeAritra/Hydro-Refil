"""
Unit Tests — Structure Sizing Calculations
"""

from domain.hydrology.structures import (
    size_storage_tank,
    size_recharge_pit,
    size_recharge_trench,
    size_recharge_shaft,
)


def test_size_storage_tank():
    dims = size_storage_tank(design_volume_litres=20000.0)
    assert dims.structure_type == "storage_tank"
    assert dims.length_m > 0
    assert dims.width_m > 0
    assert dims.depth_m <= 3.0
    assert dims.effective_volume_m3 == 20.0
    assert len(dims.calculation_trace) > 0


def test_size_recharge_pit():
    dims = size_recharge_pit(design_volume_m3=10.0, infiltration_rate_mm_hr=25.0)
    assert dims.structure_type == "recharge_pit"
    assert dims.length_m > 0
    assert dims.depth_m <= 3.0
    assert dims.effective_volume_m3 > 0


def test_size_recharge_trench():
    dims = size_recharge_trench(design_volume_m3=15.0, infiltration_rate_mm_hr=12.0)
    assert dims.structure_type == "recharge_trench"
    assert dims.length_m > 0
    assert dims.width_m == 1.0
    assert dims.depth_m >= 1.0


def test_size_recharge_shaft():
    dims = size_recharge_shaft(design_volume_m3=25.0, infiltration_rate_mm_hr=2.0, groundwater_depth_m=15.0)
    assert dims.structure_type == "recharge_shaft"
    assert dims.diameter_m == 0.50
    assert dims.depth_m >= 15.0
