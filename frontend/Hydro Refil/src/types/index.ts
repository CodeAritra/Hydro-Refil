/**
 * RTRWH Platform — Core TypeScript Definitions
 */

export type RoofMaterialKey =
  | 'rcc_concrete'
  | 'corrugated_metal'
  | 'clay_tile'
  | 'asbestos_cement'
  | 'thatch_grass'
  | 'green_roof';

export type SoilTypeKey =
  | 'gravel_coarse_sand'
  | 'fine_sand'
  | 'sandy_loam'
  | 'loam'
  | 'clay_loam'
  | 'clay'
  | 'black_cotton'
  | 'unknown';

export type StructureType =
  | 'storage_tank'
  | 'recharge_pit'
  | 'recharge_trench'
  | 'recharge_shaft'
  | 'soak_pit';

export interface LocationInput {
  latitude?: number;
  longitude?: number;
  address?: string;
  district?: string;
  state?: string;
  coordinates?: [number, number][]; // Polygon vertices [lng, lat]
}

export interface RoofInput {
  area_m2: number;
  material_key: RoofMaterialKey;
  slope_deg?: number;
  num_downpipes?: number;
  has_first_flush_diverter?: boolean;
}

export interface RainfallInput {
  annual_mm: number;
  monthly_mm?: Record<string, number>;
  data_source?: string;
}

export interface WaterDemandInput {
  num_people: number;
  per_capita_demand_lpd: number;
  occupancy_type?: string;
  additional_demand_lpm?: number;
  non_potable_fraction?: number;
}

export interface SiteConditionsInput {
  soil_type_key: SoilTypeKey;
  infiltration_rate_mm_hr?: number;
  infiltration_data_source?: 'field_measured' | 'assumed' | 'database';
  groundwater_depth_mbgl?: number;
  groundwater_data_source?: 'field_measured' | 'cgwb_record' | 'unknown';
  available_area_m2?: number;
  is_paved_area?: boolean;
  distance_to_septic_m?: number;
  distance_to_well_m?: number;
}

export interface MonthlyDataPoint {
  month: string;
  rainfall_mm: number;
  gross_runoff_litres: number;
  net_harvestable_litres: number;
  demand_litres: number;
  balance_litres: number;
  cumulative_harvested_litres: number;
}

export interface StructureDimensions {
  structure_type: StructureType;
  structure_display_name: string;
  length_m?: number;
  width_m?: number;
  depth_m?: number;
  diameter_m?: number;
  gross_volume_m3?: number;
  effective_volume_m3?: number;
  num_structures: number;
  design_volume_m3: number;
  infiltration_rate_mm_hr?: number;
  freeboard_m: number;
  dimension_string: string;
  notes: string;
}

export interface CalculationTraceItem {
  formula_name: string;
  formula_expression: string;
  inputs: Record<string, string>;
  result: string;
  notes?: string;
}

export interface AssessmentCalculationResult {
  status: string;
  annual_gross_runoff_litres: number;
  annual_net_harvestable_litres: number;
  annual_net_harvestable_m3: number;
  first_flush_annual_loss_litres: number;
  runoff_coefficient: number;
  system_efficiency: number;
  feasibility_score: number;
  feasibility_label: 'HIGH' | 'MODERATE' | 'LOW' | 'VERY_LOW' | 'INSUFFICIENT_DATA';
  monthly_breakdown: MonthlyDataPoint[];
  
  // Water balance
  annual_demand_litres: number;
  annual_surplus_deficit_litres: number;
  demand_met_percentage: number;

  // Recharge potential
  annual_recharge_potential_litres: number;
  annual_recharge_potential_m3: number;
  recharge_feasible: boolean;
  recharge_feasibility_label: string;
  recharge_feasibility_reason: string;
  infiltration_rate_mm_hr: number;
  infiltration_data_source: string;
  groundwater_depth_adequate: boolean;

  // Recommendations
  recommended_structure: string;
  recommendation_reason: string;
  primary_dimensions: StructureDimensions;
  secondary_structure?: string;
  secondary_dimensions?: StructureDimensions;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  decision_factors: string[];

  // Traceability & safety
  warnings: string[];
  calculation_trace: CalculationTraceItem[];
}

export interface AssessmentRecord {
  id: string;
  site_name: string;
  assessor_name?: string;
  organization?: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
  location: LocationInput;
  roof: RoofInput;
  rainfall: RainfallInput;
  demand: WaterDemandInput;
  site: SiteConditionsInput;
  results: AssessmentCalculationResult;
}

export interface AssessmentListItem {
  id: string;
  site_name: string;
  assessor_name?: string;
  created_at: string;
  location_summary: string;
  roof_area_m2: number;
  annual_harvestable_m3: number;
  recommended_structure: string;
  feasibility_label: string;
}
