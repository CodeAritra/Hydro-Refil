# 🌧️ HydroRefil — On-Spot RTRWH & Artificial Recharge Sizing Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![BIS IS 15797](https://img.shields.io/badge/Standard-BIS%20IS%2015797:2008-0284c7.svg?style=flat)](https://bis.gov.in)
[![CGWB Standard](https://img.shields.io/badge/Standard-CGWB%20Manual%202007-0d9488.svg?style=flat)](http://cgwb.gov.in)

> **Smart India Hackathon (SIH) Solution**  
> *Designing and development of an application for on-spot assessment of Rooftop Rainwater Harvesting (RTRWH) and Artificial Recharge potential, including calculation and sizing of appropriate RTRWH and Artificial Recharge (AR) structures.*

---

## 🎯 Key Capabilities

1. **⚡ Rapid Field Assessment (3–5 Min):** Multi-step intuitive wizard for site survey, catchment area, rainfall normal, consumption demand, and subsoil parameters.
2. **🗺️ Free & Open GIS Location Capture:** Interactive Leaflet & OpenStreetMap integration with real-time GPS acquisition, manual coordinate entry, and pre-loaded IMD Indian district rainfall normals (35+ major districts).
3. **📐 Engineered Structure Dimensioning:** Automated calculation of indicative dimensions (L × W × D / Diameter), gravel void space porosity ($40\%$), and freeboard allowances for:
   - Gravel-Filled Recharge Pits (CGWB Section 5.4)
   - Continuous Recharge Trenches (CGWB Section 5.5)
   - Bore-Well Recharge Shafts (CGWB Section 5.7)
   - Surface / Underground Storage Sumps (IS 12288)
4. **📊 Interactive Hydrographs & Water Balance:** Monthly 12-month synthetic South-West monsoon hydrographs comparing rainfall line, harvest yield bars, and consumption demand lines.
5. **🔍 100% Transparent Formula Audit Trail:** Formula Inspection Modal showing step-by-step mathematical substitutions, physical unit relations, and BIS/CGWB citations.
6. **📱 Dual-Engine Offline Resilience:** Complete mathematical equivalence between Python backend and client-side TypeScript domain engine with local storage caching for zero-connectivity field sites.
7. **📄 Formal Field Dossier & PDF Export:** Print-ready official engineering reports with official disclaimers and sign-off blocks.

---

## 🏗️ System Architecture

```
rtrwh-platform/
├── backend/                  # FastAPI Python backend (Domain Hydrology Engine, REST APIs, Pytest)
│   ├── api/routes/           # Endpoints: /api/hydrology, /api/assessments, /api/reports
│   ├── db/                   # Async SQLAlchemy models & SQLite/PostgreSQL engine
│   ├── domain/hydrology/     # Unit-aware calculation modules & assumptions
│   ├── tests/                # 18 automated unit & integration tests
│   └── main.py               # FastAPI application entrypoint
│
├── frontend/Hydro Refil/     # React 19 + TypeScript + Vite + Tailwind CSS
│   ├── src/components/       # UI Primitives, Leaflet Map, Recharts, Results & Sizing Cards
│   ├── src/data/             # Static IMD District Rainfall & Runoff Coefficient Datasets
│   ├── src/domain/           # Client-Side Offline TypeScript Hydrology Engine
│   └── src/pages/            # Dashboard, NewAssessment, Detail, List, ReportView
│
├── config/                   # Centralized hydrology-assumptions.json
├── docs/                     # Full technical documentation suite (20+ files)
└── .env.example              # Environment variables template
```

---

## 🚀 Quick Start Guide (Windows / Linux / macOS)

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
python -m uvicorn main:app --reload --port 8000
```
- API is running at: `http://127.0.0.1:8000`
- Swagger UI Docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```bash
cd "frontend/Hydro Refil"
npm install
npm run build
npm run dev
```
- Web Application is running at: `http://localhost:5173`

---

## 🧪 Testing & Verification

Run the comprehensive backend test suite:
```bash
cd backend
python -m pytest tests/ -v
```
**Test Results:**
- `tests/test_rtrwh.py`: Fundamental $1\text{ mm} \times 1\text{ m}^2 = 1\text{ L}$ unit checks, monthly distribution, water balance.
- `tests/test_recharge.py`: Groundwater depth safety guards ($<3.0\text{ m}$ limit), infiltration feasibility.
- `tests/test_structures.py`: Dimension sizing calculations for pits, trenches, shafts, and sumps.
- `tests/test_recommendation.py`: Decision tree rule validation.
- `tests/test_api.py`: Full REST API and Assessment CRUD lifecycle.

---

## 📚 Technical Documentation Suite

| Document | Description |
|---|---|
| [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md) | Initial repository audit and 6 critical prototype bug resolutions |
| [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) | Formal Functional and Non-Functional Requirements Specification |
| [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md) | High-level system architecture and component interactions |
| [`docs/ENGINEERING_METHODOLOGY.md`](docs/ENGINEERING_METHODOLOGY.md) | Governing equations, mathematical proofs, and standard citations |
| [`docs/CALCULATION_VERIFICATION.md`](docs/CALCULATION_VERIFICATION.md) | Hand-calculated benchmark verification scenarios |
| [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md) | Centralized parameters, runoff coefficients, and soil infiltration rates |
| [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) | REST API endpoints, schemas, and payload examples |
| [`docs/COMMANDS.md`](docs/COMMANDS.md) | Exact Windows PowerShell / CMD commands for setup, run, and test |
| [`docs/SIH_DEMO_GUIDE.md`](docs/SIH_DEMO_GUIDE.md) | 3-minute demonstration script for SIH Hackathon judges |
| [`docs/FINAL_TECHNICAL_REPORT.md`](docs/FINAL_TECHNICAL_REPORT.md) | Comprehensive engineering completion report |

---

## ⚖️ Engineering Disclaimer
*This digital platform is engineered for preliminary decision support, rapid feasibility estimation, and structure sizing. All calculated dimensions are indicative. Actual physical construction requires on-site verification by a qualified civil engineer with certified soil percolation and geotechnical testing.*

---
Developed for the **Smart India Hackathon (SIH)**.
