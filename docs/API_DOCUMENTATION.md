# API DOCUMENTATION — HydroRefil REST Services

Interactive Swagger / OpenAPI documentation is hosted at: `http://localhost:8000/docs`

---

## 1. Hydrology Endpoints (`/api/hydrology`)

### `POST /api/hydrology/calculate`
Executes complete hydrological assessment and structure sizing on-the-fly without database persistence.
- **Request Body:**
```json
{
  "roof": {
    "area_m2": 250.0,
    "material_key": "rcc_concrete",
    "slope_deg": 0.0,
    "num_downpipes": 2,
    "has_first_flush_diverter": true
  },
  "rainfall": {
    "annual_mm": 1600.0,
    "data_source": "imd_database"
  },
  "demand": {
    "num_people": 6,
    "per_capita_demand_lpd": 135.0,
    "non_potable_fraction": 0.40
  },
  "site": {
    "soil_type_key": "sandy_loam",
    "groundwater_depth_mbgl": 12.0,
    "available_area_m2": 30.0
  }
}
```
- **Response (200 OK):**
```json
{
  "status": "success",
  "annual_gross_runoff_litres": 340000.0,
  "annual_net_harvestable_litres": 221000.0,
  "annual_net_harvestable_m3": 221.0,
  "first_flush_annual_loss_litres": 80000.0,
  "runoff_coefficient": 0.85,
  "system_efficiency": 0.85,
  "feasibility_score": 1.0,
  "feasibility_label": "HIGH",
  "monthly_breakdown": [ ... ],
  "annual_demand_litres": 118260.0,
  "annual_surplus_deficit_litres": 102740.0,
  "demand_met_percentage": 100.0,
  "annual_recharge_potential_litres": 221000.0,
  "annual_recharge_potential_m3": 221.0,
  "recharge_feasible": true,
  "recharge_feasibility_label": "HIGHLY_FEASIBLE",
  "recharge_feasibility_reason": "Good infiltration capacity...",
  "recommended_structure": "Gravel-Filled Recharge Pit",
  "recommendation_reason": "Good soil infiltration...",
  "primary_dimensions": {
    "structure_type": "recharge_pit",
    "structure_display_name": "Gravel-Filled Recharge Pit",
    "length_m": 4.69,
    "width_m": 4.69,
    "depth_m": 2.5,
    "effective_volume_m3": 22.0,
    "dimension_string": "L: 4.69 m × W: 4.69 m × D: 2.50 m"
  },
  "warnings": [],
  "calculation_trace": [ ... ]
}
```

### `GET /api/hydrology/coefficients`
Returns all registered roof materials, runoff coefficient values, ranges, confidence levels, and citations.

### `GET /api/hydrology/soil-types`
Returns subsoil classification table with typical infiltration rates ($mm/hr$) and percolation notes.

### `GET /api/hydrology/assumptions`
Returns complete assumptions registry.

---

## 2. Assessment CRUD Endpoints (`/api/assessments`)

### `POST /api/assessments`
Creates, computes, and stores an assessment record in SQLite / PostgreSQL.
- **Status:** `201 Created`
- **Response:** Complete `AssessmentDetailResponse` with generated UUID.

### `GET /api/assessments`
Lists all assessment summaries sorted by newest first.
- **Status:** `200 OK`

### `GET /api/assessments/{id}`
Fetches full assessment dossier, inputs, and calculation outputs by UUID.

### `DELETE /api/assessments/{id}`
Deletes assessment record by UUID.
- **Status:** `204 No Content`

---

## 3. Report Endpoints (`/api/reports`)

### `GET /api/reports/{id}/summary`
Generates clean report summary for export and document templating.
