# DEVELOPER ONBOARDING GUIDE — HydroRefil

Welcome to the **HydroRefil** codebase! This document is designed to get new developers, hydrologists, and contributors up to speed on the architecture, data flow, and code conventions in under 10 minutes.

---

## 🧭 1. Understanding the Core Philosophy

### A. Dual-Engine Architecture
To support field engineers working in remote or low-connectivity areas (e.g. rural water survey blocks, hilly terrains), HydroRefil executes calculations deterministically across two parallel engines:
1. **Backend Engine (`backend/domain/hydrology/`):** Written in Python 3.12 with Pydantic validation. Used for REST API requests, database persistence, and automated Pytest verification.
2. **Frontend Offline Engine (`frontend/Hydro Refil/src/domain/hydrology.ts`):** Written in pure TypeScript with zero external calculation dependencies. Used for real-time form feedback and automatic offline fallback if the backend API is disconnected.

> **CRITICAL RULE:** Whenever you modify or add a calculation formula, **you must update both the Python domain and the TypeScript domain identically**.

---

## 🔄 2. End-to-End Data Flow

```
[User interacts with UI: Area / Material / District / Soil]
                     │
                     ▼
  [Live Preview Dock: calculates in real-time via src/domain/hydrology.ts]
                     │
                     ▼ (User clicks "Execute Assessment & Save")
  [services/api.ts sends POST /api/assessments to FastAPI]
                     │
         ┌───────────┴───────────┐
         ▼ (Backend Online)      ▼ (Backend Offline / Network Down)
  [FastAPI computes & saves   [Calculates via TypeScript domain
   to SQLite via SQLAlchemy]   and persists to browser LocalStorage]
         │                       │
         └───────────┬───────────┘
                     ▼
  [AssessmentDetail Page: Renders Charts, Sizing Cards, and Audit Trail]
```

---

## 🗃️ 3. How to Add or Modify Engineering Data

### Adding a New Rooftop Material
1. Open `config/hydrology-assumptions.json` and add your material key, runoff coefficient value, validated range, and citation.
2. Update `backend/domain/hydrology/assumptions.py` in `RUNOFF_COEFFICIENTS`.
3. Update `frontend/Hydro Refil/src/data/runoff-coefficients.json`.
4. Add a unit test in `backend/tests/test_rtrwh.py`.

### Adding a Regional IMD Weather Station / District Normal
1. Open `frontend/Hydro Refil/src/data/rainfall-india.json`.
2. Add your district record:
   ```json
   { "state": "Tamil Nadu", "district": "Tiruchirappalli", "annual_rainfall_mm": 840, "lat": 10.7905, "lng": 78.7047 }
   ```
3. The dropdown in `LocationPicker.tsx` will automatically populate it.

---

## 🧪 4. Running the Complete Verification Suite

```bash
# 1. Backend Pytest
cd backend
python -m pytest tests/ -v

# 2. Frontend Production Build & TypeScript Check
cd "../frontend/Hydro Refil"
npm run build
```
