# PROJECT AUDIT — RTRWH Platform
**Audit Date:** 2026-08-19  
**Auditor:** Principal Solution Architect  
**Scope:** Complete repository audit prior to architecture refactor  
**Status:** PHASE 0 — COMPLETE

---

## Executive Summary

The existing prototype is a minimal, **non-functional skeleton** consisting of:
- A React/TypeScript (Vite) frontend with a single monolithic `App.tsx` component
- A FastAPI Python backend with a single route and a basic hydrology function
- A PostgreSQL + PostGIS database schema (SQL file only — no running database)
- No routing, no multi-step workflow, no tests, no documentation, no .env files

**Critical Assessment:** The prototype cannot run as-is due to at least 6 distinct blocking errors. It demonstrates the *concept* of the solution but requires near-complete implementation to be functional.

---

## 3.1 Current Architecture

### Frontend
| Property | Value |
|---|---|
| Framework | React 19 + TypeScript |
| Build Tool | Vite 8 |
| Styling | Tailwind CSS (v3) — partially set up but not properly linked to the Vite project |
| Routing | NONE — single page, no router |
| State Management | Local useState only |
| HTTP Client | Axios (in outer frontend/node_modules, not inner Hydro Refil/node_modules) |
| Mapping | Mapbox GL JS + react-map-gl (same package split issue) |
| PDF | jsPDF |
| Icons | lucide-react |
| Project Structure | Confused — two package.json files exist |

### Backend
| Property | Value |
|---|---|
| Framework | FastAPI |
| Runtime | Python 3.12 |
| Async | asyncpg (PostgreSQL async driver) |
| ORM | None — raw asyncpg queries |
| Validation | Pydantic v2 |
| CORS | Fully open (allow_origins=["*"]) |
| Server | Uvicorn (installed but no run config) |

### Database
| Property | Value |
|---|---|
| Type | PostgreSQL + PostGIS |
| Schema File | backend/init_db.sql |
| Status | Schema file exists. No running database. No migration tool. |
| ORM | None |

### APIs
| Endpoint | Method | Status |
|---|---|---|
| /api/assessments/calculate | POST | Defined but non-functional (requires live PostGIS DB) |

### Authentication
NONE — no authentication system implemented.

### Calculation Engine
- Single Python function: execute_hydrological_assessment() in hydrology_engine.py
- Contains several hardcoded values
- Partially calculates runoff, peak flow, and structure dimensions
- Recommendation logic is extremely basic (two if/elif/else branches)

---

## 3.2 Existing Features

| Feature | Status | Quality | Problems | Action |
|---|---|---|---|---|
| React + Vite project setup | Partial | Poor | Two nested package.json files — inner missing critical deps | Fix project structure |
| Tailwind CSS | Partial | Poor | Config in outer frontend/ but not inner Vite project | Fix config location |
| Mapbox GL map | Broken | Poor | API token is placeholder + syntax error in App.tsx | Replace with Leaflet/OSM |
| Polygon drawing tool | Broken | Medium | Depends on broken Mapbox setup | Replace with turf.js + Leaflet |
| Roof area calculation via geometry | Broken | Medium | Requires PostGIS backend | Replace with client-side turf.js |
| Site name input | Working | Poor | No validation, no persistence | Keep + extend |
| Roof material selector | Working | Poor | Only 4 options, no validation | Keep + extend |
| API call to backend | Broken | Poor | Backend not running; token/CORS issues | Fix + extend |
| FastAPI server | Partial | Poor | Missing startup command, hardcoded DB credentials | Fix |
| PostGIS area calculation | Broken | Poor | Requires running PostGIS instance | Replace with turf.js client-side |
| IDW rainfall interpolation | Broken | Poor | Requires populated weather_stations table | Replace with user-input |
| Hydrology calculation engine | Partial | Poor | Hardcoded values, missing many required calculations | Extend significantly |
| SCS-CN runoff model | Partial | Poor | Partially implemented but initial abstraction misapplied | Fix + document |
| Structure recommendation | Broken | Poor | Always returns "Standard Recharge Pit"; hardcoded dimensions | Rewrite |
| PDF report | Partial | Poor | Generates 4-line text PDF | Rewrite |
| Assessment workflow | Missing | — | No multi-step form, no workflow | Implement |
| Dashboard | Missing | — | No dashboard | Implement |
| Monthly rainfall analysis | Missing | — | Not implemented | Implement |
| Water demand calculation | Missing | — | Not implemented | Implement |
| Water balance | Missing | — | Not implemented | Implement |
| AR potential calculation | Missing | — | Not implemented | Implement |
| Structure dimension calculator | Missing | — | Hardcoded dimensions only | Implement |
| Calculation explainability | Missing | — | No formula display | Implement |
| Validation (frontend) | Missing | — | No input validation whatsoever | Implement |
| Validation (backend) | Partial | Poor | Only polygon closure check | Implement |
| Error handling | Partial | Poor | Basic try/catch, no user-friendly messages | Implement |
| Authentication | Missing | — | Not implemented | Not required for SIH prototype |
| Testing | Missing | — | Zero tests | Implement |
| Documentation | Missing | — | README is default Vite template | Implement |
| Responsive design | Missing | — | Fixed desktop-only layout | Implement |
| Offline support | Missing | — | All calculations require backend | Implement client-side calc |
| Git repository | Missing | — | No git init | Initialize |
| .env configuration | Missing | — | No .env or .env.example | Implement |
| Database migrations | Missing | — | SQL file only, no migration tool | Implement |

---

## 3.3 Existing Bugs

### CRITICAL (Application cannot start/function)

#### BUG-001 — Syntax Error in App.tsx (Line 11)
File: frontend/Hydro Refil/src/App.tsx  
Lines: 10-11  
Problem: The Mapbox token assignment is split across two lines — TypeScript parse error preventing compilation:
```
const MAPBOX_TOKEN = 'YOUR_MAPBOX_PUBLIC_TOKEN_HERE'; // Replace with actual
token    ← bare identifier, causes parse error
```
Action: Fix syntax + move to environment variable.

#### BUG-002 — Mapbox Token is a Placeholder
File: frontend/Hydro Refil/src/App.tsx  
Problem: MAPBOX_TOKEN = 'YOUR_MAPBOX_PUBLIC_TOKEN_HERE' — map will not load.  
Action: Move to .env; replace Mapbox with Leaflet + OpenStreetMap (free).

#### BUG-003 — Split Package Dependencies
Files: frontend/package.json vs frontend/Hydro Refil/package.json  
Problem: Critical dependencies (mapbox-gl, react-map-gl, axios, jspdf, lucide-react, @turf/turf) 
are in frontend/node_modules but the Vite project root is frontend/Hydro Refil/.
Vite will not resolve the outer node_modules by default.  
Action: Consolidate all dependencies into frontend/Hydro Refil/package.json.

#### BUG-004 — Backend Requires Running PostGIS Instance
File: backend/main.py  
Problem: On startup, connects to postgres://postgres:password@localhost:5432/rtrwh_spatial.
This database does not exist. Server crashes on startup.  
Action: Decouple calculations from database; use SQLite as default.

#### BUG-005 — Hardcoded Database Credentials
File: backend/main.py  
Line: 23  
Problem: Database DSN hardcoded — security vulnerability.  
Action: Move to environment variable via .env file.

#### BUG-006 — Python Backend Missing Requirements File
Problem: No requirements.txt or pyproject.toml exists. Cannot reproduce environment.  
Action: Generate requirements.txt.

### HIGH (Calculations incorrect or incomplete)

#### BUG-007 — Initial Abstraction Applied to Annual Rainfall (Hydrological Error)
File: backend/hydrology_engine.py  
Line: 19  
Problem:
```python
effective_rainfall_mm = max(0.0, annual_rainfall_mm - initial_abstraction_mm)
```
Subtracting a per-event initial abstraction (2.5 mm) from annual rainfall (1600 mm) is 
hydrologically incorrect. Initial abstraction is a per-storm concept, not annual.  
Action: Fix formula. Apply an annual efficiency/losses factor instead.

#### BUG-008 — Python Indentation Error in hydrology_engine.py
File: backend/hydrology_engine.py  
Lines: 52-53  
Problem: calc_width and assessment update are at function scope, not inside the else block.
This causes NameError (required_surface_area undefined) for the if/elif code paths.  
Action: Fix indentation.

#### BUG-009 — Structure Dimensions Hardcoded (Not Calculated)
File: backend/hydrology_engine.py  
Lines: 35-38  
Problem: Default dimensions are always 2.0m x 2.0m x 2.0m regardless of calculations.  
Action: Implement proper dimension calculation based on volume requirements.

#### BUG-010 — Feasibility Always "HIGHLY_FEASIBLE"
File: backend/hydrology_engine.py  
Line: 31  
Problem: Default feasibility set to HIGHLY_FEASIBLE with no multi-factor analysis.  
Action: Implement proper, multi-factor feasibility scoring.

#### BUG-011 — SYSTEM_EFFICIENCY Hardcoded Without Source Documentation
File: backend/hydrology_engine.py  
Line: 13  
Problem: SYSTEM_EFFICIENCY = 0.90 with no documentation of source or applicability.  
Action: Move to documented assumptions configuration.

### MEDIUM (Functional issues)

#### BUG-012 — No Input Validation in Frontend
Action: Add comprehensive validation.

#### BUG-013 — No Manual Area Input Fallback
Problem: Entire app non-functional if map fails.  
Action: Add manual area entry as primary/fallback.

#### BUG-014 — CORS Wildcard
File: backend/main.py  
Action: Configure via environment variable.

#### BUG-015 — PDF Report Contains Only 4 Lines
File: frontend/Hydro Refil/src/App.tsx  
Action: Implement complete report structure.

---

## 3.4 Technical Debt

| Item | Location | Severity | Description |
|---|---|---|---|
| Monolithic App.tsx | Frontend | High | All logic, UI, API calls in 206-line file |
| No separation of concerns | Frontend | High | Business logic inside UI component |
| No type safety for API responses | Frontend | High | results typed as any |
| No router | Frontend | High | No navigation between views |
| Hardcoded geography | Backend | High | Weather stations only cover Kolkata |
| Hardcoded hydrogeology | Backend | High | 20.0, 8.0 hardcoded for infiltration/water table |
| No requirements.txt | Backend | High | Cannot reproduce Python environment |
| No .env management | Both | High | Secrets hardcoded |
| No tests | Both | High | Zero test coverage |
| App.css is Vite template | Frontend | Medium | Default Vite styles, not app-specific |
| Recommendation engine non-existent | Backend | Medium | Single hardcoded string returned |
| No monthly rainfall model | Backend | Medium | Only annual figure computed |
| No water demand model | Backend | Medium | Not implemented |
| No AR calculation | Backend | Medium | Not implemented |
| README is Vite default | Frontend | Low | Contains Vite template text |
| App title is "hydro-refil" | Frontend | Low | Not professional |
| asyncio.on_event deprecated | Backend | Low | FastAPI deprecated event handlers |

---

## Recommended Target Architecture

Based on the audit, the recommended approach is:

1. **Keep** FastAPI + Python backend (solid choice for calculation-heavy work)
2. **Keep** React + TypeScript + Vite frontend (correct technology)
3. **Replace** PostGIS spatial area calculation with **turf.js client-side** (eliminates PostGIS dependency)
4. **Replace** Mapbox with **Leaflet + OpenStreetMap** (free, no token, excellent offline support)
5. **Add** SQLite as default database (zero-config, works without a server)
6. **Restructure** frontend into multi-page application with React Router
7. **Implement** all missing calculation modules in the Python domain layer
8. **Add** comprehensive testing framework

This approach maximizes what works while eliminating showstopper dependencies (Mapbox token, PostGIS server).

---
*End of Audit — PHASE 0 COMPLETE*
