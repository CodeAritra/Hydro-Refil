/**
 * RTRWH Platform — Client-Side Hydrological Engine (Offline-Capable)
 * ===================================================================
 * Complete TypeScript implementation of the hydrological domain model.
 * Produces identical deterministic results to the backend Python engine.
 */

import {
  RoofInput,
  RainfallInput,
  WaterDemandInput,
  SiteConditionsInput,
  AssessmentCalculationResult,
  MonthlyDataPoint,
  StructureDimensions,
  CalculationTraceItem,
} from '../types';
import runoffCoefficientsData from '../data/runoff-coefficients.json';
import soilTypesData from '../data/soil-types.json';

// Constants
export const SYSTEM_EFFICIENCY = 0.85; // CGWB default
export const FIRST_FLUSH_DEPTH_MM = 2.0; // IS 15797:2008 Clause 6
export const GRAVEL_FILL_POROSITY = 0.40; // 40% void fraction
export const MIN_GW_DEPTH_METERS = 3.0; // Minimum groundwater depth for recharge

const MONTHLY_WEIGHTS: Record<string, number> = {
  jan: 0.010, feb: 0.010, mar: 0.012, apr: 0.020,
  may: 0.030, jun: 0.130, jul: 0.240, aug: 0.200,
  sep: 0.140, oct: 0.070, nov: 0.020, dec: 0.010,
};

export function getRunoffCoefficient(materialKey: string): number {
  const match = runoffCoefficientsData.find((m) => m.key === materialKey);
  return match ? match.value : 0.85;
}

export function getSoilInfiltrationRate(soilKey: string): number {
  const match = soilTypesData.find((s) => s.key === soilKey);
  return match ? match.infiltration_rate_mm_hr : 5.0;
}

export function calculateRTRWHOffline(
  roof: RoofInput,
  rainfall: RainfallInput,
  demand?: WaterDemandInput,
  site?: SiteConditionsInput
): AssessmentCalculationResult {
  const traces: CalculationTraceItem[] = [];
  const warnings: string[] = [];

  const area = Math.max(1, roof.area_m2);
  const C = getRunoffCoefficient(roof.material_key);
  const annualRainfall = Math.max(0, rainfall.annual_mm);

  // 1. Gross Runoff
  const grossRunoffLitres = annualRainfall * area * C;
  traces.push({
    formula_name: 'Annual Gross Runoff',
    formula_expression: 'Gross = Annual_Rainfall (mm) × Roof_Area (m²) × Runoff_Coeff (C)',
    inputs: {
      'Annual Rainfall': `${annualRainfall.toFixed(1)} mm`,
      'Roof Catchment Area': `${area.toFixed(1)} m²`,
      'Runoff Coefficient': `${C.toFixed(2)} (${roof.material_key})`,
    },
    result: `${grossRunoffLitres.toLocaleString(undefined, { maximumFractionDigits: 0 })} Litres/yr`,
    notes: 'Physical basis: 1 mm rainfall over 1 m² catchment area = 1 Litre of runoff.',
  });

  // 2. First Flush Diverter Loss
  const rainEvents = Math.max(1, Math.floor(annualRainfall / 10));
  const ffLossLitres = FIRST_FLUSH_DEPTH_MM * area * rainEvents;
  traces.push({
    formula_name: 'First Flush Diversion',
    formula_expression: 'FF_Loss = FF_Depth (2 mm) × Area × Estimated_Events',
    inputs: {
      'First Flush Standard': '2.0 mm per storm event (IS 15797:2008)',
      'Estimated Rain Days': `${rainEvents} events/year`,
    },
    result: `${ffLossLitres.toLocaleString(undefined, { maximumFractionDigits: 0 })} Litres/yr diverted`,
    notes: 'Initial runoff containing dust, debris, and atmospheric particulates is diverted from storage.',
  });

  // 3. Net Harvestable Volume
  const volumeAfterFF = Math.max(0, grossRunoffLitres - ffLossLitres);
  const netHarvestableLitres = volumeAfterFF * SYSTEM_EFFICIENCY;
  const netHarvestableM3 = netHarvestableLitres / 1000.0;
  traces.push({
    formula_name: 'Net Harvestable Water Potential',
    formula_expression: 'Net_Yield = (Gross - FF_Loss) × System_Efficiency (0.85)',
    inputs: {
      'Gross Runoff': `${grossRunoffLitres.toFixed(0)} L`,
      'Diverted Loss': `${ffLossLitres.toFixed(0)} L`,
      'System Efficiency': '85% (CGWB 2007 guideline)',
    },
    result: `${netHarvestableLitres.toLocaleString(undefined, { maximumFractionDigits: 0 })} L (${netHarvestableM3.toFixed(2)} m³/yr)`,
  });

  // 4. Monthly Breakdown
  const months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  let annualDemandLitres = 0;
  if (demand && demand.num_people > 0) {
    const dailyDemand = (demand.num_people * (demand.per_capita_demand_lpd || 135)) + ((demand.additional_demand_lpm || 0) / 30.44);
    annualDemandLitres = dailyDemand * 365 * (demand.non_potable_fraction || 0.40);
  }
  const monthlyDemandLitres = annualDemandLitres / 12.0;

  let cumulativeHarvest = 0;
  const monthlyBreakdown: MonthlyDataPoint[] = months.map((m) => {
    const rainM = rainfall.monthly_mm?.[m] ?? (annualRainfall * (MONTHLY_WEIGHTS[m] || 0.083));
    const grossM = rainM * area * C;
    const netM = Math.max(0, (grossM - (FIRST_FLUSH_DEPTH_MM * area)) * SYSTEM_EFFICIENCY);
    cumulativeHarvest += netM;
    return {
      month: m.toUpperCase(),
      rainfall_mm: Number(rainM.toFixed(1)),
      gross_runoff_litres: Number(grossM.toFixed(1)),
      net_harvestable_litres: Number(netM.toFixed(1)),
      demand_litres: Number(monthlyDemandLitres.toFixed(1)),
      balance_litres: Number((netM - monthlyDemandLitres).toFixed(1)),
      cumulative_harvested_litres: Number(cumulativeHarvest.toFixed(1)),
    };
  });

  const surplusDeficit = netHarvestableLitres - annualDemandLitres;
  const demandMetPct = annualDemandLitres > 0
    ? Math.min(100, (netHarvestableLitres / annualDemandLitres) * 100)
    : 0;

  // 5. Site & Recharge Analysis
  const infRate = site?.infiltration_rate_mm_hr || getSoilInfiltrationRate(site?.soil_type_key || 'unknown');
  const gwDepth = site?.groundwater_depth_mbgl;
  const isGwAdequate = gwDepth === undefined || gwDepth >= MIN_GW_DEPTH_METERS;

  let rechargeFeasible = true;
  let rechargeLabel = 'HIGHLY_FEASIBLE';
  let rechargeReason = 'Good infiltration rate and sufficient subsoil depth support natural recharge.';

  if (!isGwAdequate) {
    rechargeFeasible = false;
    rechargeLabel = 'NOT_RECOMMENDED';
    rechargeReason = `Water table is very shallow (${gwDepth} m BGL < 3.0 m limit). In-ground recharge risks surface waterlogging and foundation damage.`;
    warnings.push(rechargeReason);
  } else if (infRate < 1.0) {
    rechargeFeasible = false;
    rechargeLabel = 'NOT_RECOMMENDED';
    rechargeReason = `Soil infiltration (${infRate} mm/hr) is very low. Surface recharge pits will pond and clog.`;
    warnings.push(rechargeReason);
  } else if (infRate < 5.0) {
    rechargeLabel = 'CONDITIONAL';
    rechargeReason = `Low-moderate infiltration (${infRate} mm/hr). Requires larger recharge trench or deep shaft.`;
  }

  const annualRechargeL = isGwAdequate && infRate >= 1.0 ? netHarvestableLitres : 0;
  const annualRechargeM3 = annualRechargeL / 1000.0;

  // 6. Structure Sizing & Recommendation
  const peakStormVolM3 = Math.min(50, Math.max(2, (netHarvestableLitres * 0.30) / 1000.0));
  let primaryDim: StructureDimensions;
  let recStructure = 'Gravel-Filled Recharge Pit';
  let recReason = '';
  const decisionFactors: string[] = [];

  if (!isGwAdequate || (demand && demand.num_people >= 10 && demandMetPct >= 50)) {
    // Storage tank
    recStructure = 'Rainwater Storage Tank (Surface / Sump)';
    recReason = !isGwAdequate
      ? `High groundwater table (${gwDepth} m BGL) necessitates surface storage tank over in-ground recharge.`
      : `Substantial on-site water demand (${annualDemandLitres.toLocaleString()} L/yr) makes direct storage the highest priority for conservation.`;
    decisionFactors.push(!isGwAdequate ? 'High groundwater table' : 'High domestic water demand');

    const tankVol = Math.max(peakStormVolM3, (annualDemandLitres * 0.15) / 1000.0);
    const depth = 2.5;
    const planArea = (tankVol * 1.1) / depth;
    const side = Math.sqrt(planArea);

    primaryDim = {
      structure_type: 'storage_tank',
      structure_display_name: 'Masonry / RCC Storage Tank',
      length_m: Number(side.toFixed(2)),
      width_m: Number(side.toFixed(2)),
      depth_m: depth,
      gross_volume_m3: Number((planArea * depth).toFixed(2)),
      effective_volume_m3: Number(tankVol.toFixed(2)),
      num_structures: 1,
      design_volume_m3: Number(tankVol.toFixed(2)),
      freeboard_m: 0.25,
      dimension_string: `${side.toFixed(2)} m (L) × ${side.toFixed(2)} m (W) × ${depth.toFixed(2)} m (D)`,
      notes: 'Includes 10% freeboard allowance. Provide sediment trap and overflow outlet.',
    };
  } else if (infRate < 5.0) {
    // Recharge trench or shaft
    if (gwDepth && gwDepth > 6.0) {
      recStructure = 'Recharge Shaft with Injection Pipe';
      recReason = `Low surface infiltration (${infRate} mm/hr) but deep groundwater (${gwDepth} m BGL) makes a drilled recharge shaft the most effective structure.`;
      decisionFactors.push('Low surface permeability', 'Deep permeable aquifer');

      primaryDim = {
        structure_type: 'recharge_shaft',
        structure_display_name: 'Bore-well Type Recharge Shaft',
        diameter_m: 0.50,
        depth_m: Number((gwDepth + 2).toFixed(1)),
        gross_volume_m3: Number((Math.PI * 0.25 * (gwDepth + 2)).toFixed(2)),
        effective_volume_m3: Number((peakStormVolM3 * 0.7).toFixed(2)),
        num_structures: 1,
        design_volume_m3: peakStormVolM3,
        freeboard_m: 0.5,
        dimension_string: `Ø 0.50 m diameter × ${(gwDepth + 2).toFixed(1)} m depth`,
        notes: 'Pre-filtration through graded sand-gravel chamber is mandatory before injection.',
      };
    } else {
      recStructure = 'Gravel-Filled Recharge Trench';
      recReason = `Moderate infiltration (${infRate} mm/hr). A linear recharge trench spreads runoff over a larger percolation footprint.`;
      decisionFactors.push('Moderate infiltration rate', 'Linear footprint distribution');

      const grossV = peakStormVolM3 / GRAVEL_FILL_POROSITY;
      const w = 1.0;
      const d = 1.5;
      const len = Math.max(3.0, grossV / (w * d));

      primaryDim = {
        structure_type: 'recharge_trench',
        structure_display_name: 'Continuous Recharge Trench',
        length_m: Number(len.toFixed(2)),
        width_m: w,
        depth_m: d,
        gross_volume_m3: Number((len * w * d).toFixed(2)),
        effective_volume_m3: Number((len * w * d * GRAVEL_FILL_POROSITY).toFixed(2)),
        num_structures: 1,
        design_volume_m3: peakStormVolM3,
        freeboard_m: 0.30,
        dimension_string: `${len.toFixed(2)} m (L) × ${w.toFixed(2)} m (W) × ${d.toFixed(2)} m (D)`,
        notes: 'Lined with geotextile filter fabric with central perforated PVC pipe.',
      };
    }
  } else {
    // Recharge pit
    recStructure = 'Gravel-Filled Recharge Pit';
    recReason = `Good infiltration capacity (${infRate} mm/hr) and favorable site conditions. A standard gravel recharge pit is the most cost-effective and compact AR structure.`;
    decisionFactors.push('High soil permeability', 'Compact construction footprint');

    const grossV = peakStormVolM3 / GRAVEL_FILL_POROSITY;
    const depth = 2.5;
    const areaPit = Math.max(2.25, grossV / depth);
    const side = Math.sqrt(areaPit);

    primaryDim = {
      structure_type: 'recharge_pit',
      structure_display_name: 'Standard Recharge Pit',
      length_m: Number(side.toFixed(2)),
      width_m: Number(side.toFixed(2)),
      depth_m: depth,
      gross_volume_m3: Number((side * side * depth).toFixed(2)),
      effective_volume_m3: Number((side * side * depth * GRAVEL_FILL_POROSITY).toFixed(2)),
      num_structures: 1,
      design_volume_m3: peakStormVolM3,
      freeboard_m: 0.30,
      dimension_string: `${side.toFixed(2)} m (L) × ${side.toFixed(2)} m (W) × ${depth.toFixed(2)} m (D)`,
      notes: 'Filled with graded gravel (40-20 mm) topped with coarse sand filter and mesh cover.',
    };
  }

  // Feasibility score
  let feasibilityScore = 0.5;
  let feasibilityLabel: 'HIGH' | 'MODERATE' | 'LOW' | 'VERY_LOW' = 'HIGH';
  if (netHarvestableLitres >= 50000) feasibilityScore += 0.3;
  if (annualRainfall >= 600) feasibilityScore += 0.2;
  if (feasibilityScore >= 0.8) feasibilityLabel = 'HIGH';
  else if (feasibilityScore >= 0.5) feasibilityLabel = 'MODERATE';
  else feasibilityLabel = 'LOW';

  return {
    status: 'success',
    annual_gross_runoff_litres: Math.round(grossRunoffLitres),
    annual_net_harvestable_litres: Math.round(netHarvestableLitres),
    annual_net_harvestable_m3: Number(netHarvestableM3.toFixed(2)),
    first_flush_annual_loss_litres: Math.round(ffLossLitres),
    runoff_coefficient: C,
    system_efficiency: SYSTEM_EFFICIENCY,
    feasibility_score: feasibilityScore,
    feasibility_label: feasibilityLabel,
    monthly_breakdown: monthlyBreakdown,
    annual_demand_litres: Math.round(annualDemandLitres),
    annual_surplus_deficit_litres: Math.round(surplusDeficit),
    demand_met_percentage: Number(demandMetPct.toFixed(1)),
    annual_recharge_potential_litres: Math.round(annualRechargeL),
    annual_recharge_potential_m3: Number(annualRechargeM3.toFixed(2)),
    recharge_feasible: rechargeFeasible,
    recharge_feasibility_label: rechargeLabel,
    recharge_feasibility_reason: rechargeReason,
    infiltration_rate_mm_hr: infRate,
    infiltration_data_source: site?.infiltration_data_source || 'assumed',
    groundwater_depth_adequate: isGwAdequate,
    recommended_structure: recStructure,
    recommendation_reason: recReason,
    primary_dimensions: primaryDim,
    confidence: 'HIGH',
    decision_factors: decisionFactors,
    warnings: warnings,
    calculation_trace: traces,
  };
}
