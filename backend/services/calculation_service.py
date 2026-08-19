"""
RTRWH Platform — Calculation Service
====================================
Orchestrates domain models to compute complete RTRWH, Artificial Recharge,
Structure Sizing, and Explainable Recommendation results.
"""

from domain.hydrology.rtrwh import (
    RoofInput,
    RainfallInput,
    WaterDemandInput,
    calculate_rtrwh_potential,
)
from domain.hydrology.recharge import (
    SiteConditionsInput,
    calculate_recharge_potential,
)
from domain.hydrology.recommendation import generate_recommendation
from domain.hydrology.structures import StructureDimensions
from models.schemas import (
    RoofDetailsSchema,
    RainfallDetailsSchema,
    DemandDetailsSchema,
    SiteConditionsSchema,
    CalculationResponse,
    MonthlyDataPoint,
    StructureDimensionsSchema,
    TraceItemSchema,
)


def structure_dim_to_schema(dims: StructureDimensions) -> StructureDimensionsSchema:
    return StructureDimensionsSchema(
        structure_type=dims.structure_type,
        structure_display_name=dims.structure_display_name,
        length_m=dims.length_m,
        width_m=dims.width_m,
        depth_m=dims.depth_m,
        diameter_m=dims.diameter_m,
        gross_volume_m3=dims.gross_volume_m3,
        effective_volume_m3=dims.effective_volume_m3,
        num_structures=dims.num_structures,
        design_volume_m3=dims.design_volume_m3,
        infiltration_rate_mm_hr=dims.infiltration_rate_mm_hr,
        freeboard_m=dims.freeboard_m,
        dimension_string=dims.dimension_string,
        notes=dims.notes,
    )


def compute_full_assessment(
    roof_schema: RoofDetailsSchema,
    rainfall_schema: RainfallDetailsSchema,
    demand_schema: DemandDetailsSchema = None,
    site_schema: SiteConditionsSchema = None,
) -> CalculationResponse:
    """Run full hydrological computation across all domain modules."""
    
    # 1. Prepare Roof domain input
    roof = RoofInput(
        area_m2=roof_schema.area_m2,
        material_key=roof_schema.material_key,
        slope_deg=roof_schema.slope_deg or 0.0,
        num_downpipes=roof_schema.num_downpipes or 1,
        has_first_flush_diverter=roof_schema.has_first_flush_diverter if roof_schema.has_first_flush_diverter is not None else True,
    )

    # 2. Prepare Rainfall domain input
    rainfall = RainfallInput(
        annual_mm=rainfall_schema.annual_mm,
        monthly_mm=rainfall_schema.monthly_mm,
        data_source=rainfall_schema.data_source or "user_provided",
    )

    # 3. Prepare Demand domain input
    demand = None
    if demand_schema and (demand_schema.num_people or 0) > 0:
        demand = WaterDemandInput(
            num_people=demand_schema.num_people or 0,
            per_capita_demand_lpd=demand_schema.per_capita_demand_lpd or 135.0,
            occupancy_type=demand_schema.occupancy_type or "domestic_urban",
            additional_demand_lpm=demand_schema.additional_demand_lpm or 0.0,
            non_potable_fraction=demand_schema.non_potable_fraction or 0.40,
        )

    # 4. Run RTRWH calculation
    rtrwh_res = calculate_rtrwh_potential(roof=roof, rainfall=rainfall, demand=demand)

    # 5. Prepare Site domain input
    site = SiteConditionsInput(
        soil_type_key=(site_schema.soil_type_key if site_schema else "unknown") or "unknown",
        infiltration_rate_mm_hr=site_schema.infiltration_rate_mm_hr if site_schema else None,
        infiltration_data_source=(site_schema.infiltration_data_source if site_schema else "assumed") or "assumed",
        groundwater_depth_mbgl=site_schema.groundwater_depth_mbgl if site_schema else None,
        groundwater_data_source=(site_schema.groundwater_data_source if site_schema else "unknown") or "unknown",
        available_area_m2=site_schema.available_area_m2 if site_schema else None,
        is_paved_area=site_schema.is_paved_area if site_schema else False,
        distance_to_septic_m=site_schema.distance_to_septic_m if site_schema else None,
        distance_to_well_m=site_schema.distance_to_well_m if site_schema else None,
    )

    # 6. Run Artificial Recharge calculation
    recharge_res = calculate_recharge_potential(
        annual_runoff_available_litres=rtrwh_res.annual_net_harvestable_litres,
        site=site,
    )

    # 7. Run Recommendation Engine
    rec_res = generate_recommendation(
        rtrwh_result=rtrwh_res,
        recharge_result=recharge_res,
        site=site,
        demand_met_pct=rtrwh_res.demand_met_percentage,
    )

    # 8. Transform Monthly Breakdown
    monthly_data = [
        MonthlyDataPoint(
            month=m.month,
            rainfall_mm=m.rainfall_mm,
            gross_runoff_litres=m.gross_runoff_litres,
            net_harvestable_litres=m.net_harvestable_litres,
            demand_litres=m.demand_litres,
            balance_litres=m.balance_litres,
            cumulative_harvested_litres=m.cumulative_harvested_litres,
        )
        for m in rtrwh_res.monthly_results
    ]

    # 9. Transform Calculation Traces
    traces = [
        TraceItemSchema(
            formula_name=t.formula_name,
            formula_expression=t.formula_expression,
            inputs=t.inputs,
            result=t.result,
            notes=t.notes,
        )
        for t in rtrwh_res.calculation_trace + recharge_res.calculation_trace + [
            t for d in [rec_res.primary_structure_dimensions, rec_res.secondary_structure_dimensions]
            if d for t in d.calculation_trace
        ]
    ]

    return CalculationResponse(
        status="success",
        annual_gross_runoff_litres=rtrwh_res.annual_gross_runoff_litres,
        annual_net_harvestable_litres=rtrwh_res.annual_net_harvestable_litres,
        annual_net_harvestable_m3=rtrwh_res.annual_net_harvestable_m3,
        first_flush_annual_loss_litres=rtrwh_res.first_flush_annual_loss_litres,
        runoff_coefficient=rtrwh_res.runoff_coefficient,
        system_efficiency=rtrwh_res.system_efficiency,
        feasibility_score=rtrwh_res.feasibility_score,
        feasibility_label=rtrwh_res.feasibility_label,
        monthly_breakdown=monthly_data,
        annual_demand_litres=rtrwh_res.annual_demand_litres,
        annual_surplus_deficit_litres=rtrwh_res.annual_surplus_deficit_litres,
        demand_met_percentage=rtrwh_res.demand_met_percentage,
        annual_recharge_potential_litres=recharge_res.annual_recharge_potential_litres,
        annual_recharge_potential_m3=recharge_res.annual_recharge_potential_m3,
        recharge_feasible=recharge_res.recharge_feasible,
        recharge_feasibility_label=recharge_res.feasibility_label,
        recharge_feasibility_reason=recharge_res.feasibility_reason,
        infiltration_rate_mm_hr=recharge_res.infiltration_rate_mm_hr,
        infiltration_data_source=recharge_res.infiltration_data_source,
        groundwater_depth_adequate=recharge_res.groundwater_depth_adequate,
        recommended_structure=rec_res.primary_structure_display,
        recommendation_reason=rec_res.recommendation_reason,
        primary_dimensions=structure_dim_to_schema(rec_res.primary_structure_dimensions),
        secondary_structure=rec_res.secondary_structure_display,
        secondary_dimensions=structure_dim_to_schema(rec_res.secondary_structure_dimensions) if rec_res.secondary_structure_dimensions else None,
        confidence=rec_res.confidence,
        decision_factors=rec_res.decision_factors,
        warnings=rec_res.warnings,
        calculation_trace=traces,
    )
