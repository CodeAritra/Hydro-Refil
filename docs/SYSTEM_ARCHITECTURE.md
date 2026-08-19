# SYSTEM ARCHITECTURE — HydroRefil

## 1. High-Level Architecture

HydroRefil follows a clean, decoupled **Domain-Driven Architecture (DDD)** with dual-engine execution capabilities (Backend Python API + Frontend TypeScript Domain):

```
+-------------------------------------------------------------------------+
|                              USER INTERFACE                             |
|    React 19 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Recharts|
+------------------------------------+------------------------------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v (Online HTTP REST)                          v (Offline Fallback)
+-----------------------------+             +-----------------------------+
|     FASTAPI BACKEND API     |             |  CLIENT-SIDE TS DOMAIN      |
|  - Routers: Hydrology,      |             |  - calculateRTRWHOffline()  |
|    Assessments, Reports     |             |  - Structured Sizing        |
|  - Validation: Pydantic v2  |             |  - Recommendation Logic     |
+--------------+--------------+             |  - LocalStorage Caching     |
               |                            +-----------------------------+
+--------------v--------------+
|   DOMAIN HYDROLOGY ENGINE   |
|  - RTRWH Yield & Runoff     |
|  - Artificial Recharge      |
|  - Sizing (Pits, Tanks)     |
|  - Recommendation Rules     |
|  - Engineering Assumptions  |
+--------------+--------------+
               |
+--------------v--------------+
|     PERSISTENCE LAYER       |
|  - SQLite (Local Dev / Demo)|
|  - Asyncpg / PostgreSQL     |
|    (Production Scalable)    |
|  - SQLAlchemy 2.0 Async ORM |
+-----------------------------+
```

---

## 2. Directory Structure

```
rtrwh-platform/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── assessments.py       # CRUD operations for site dossiers
│   │       ├── hydrology.py         # On-the-fly hydrological calculations
│   │       └── reports.py           # Report metadata and export endpoints
│   ├── db/
│   │   ├── database.py              # Async SQLAlchemy engine & session maker
│   │   └── models.py                # AssessmentModel ORM schema
│   ├── domain/
│   │   └── hydrology/
│   │       ├── assumptions.py       # Documented engineering assumptions
│   │       ├── rtrwh.py             # RTRWH formulas & monthly distribution
│   │       ├── recharge.py          # Groundwater recharge calculations
│   │       ├── structures.py        # Dimension calculator (Pits, Tanks, Trenches)
│   │       └── recommendation.py    # Rule-based explainable decision tree
│   ├── models/
│   │   └── schemas.py               # Pydantic validation schemas
│   ├── services/
│   │   └── calculation_service.py   # Domain orchestrator
│   ├── tests/                       # Pytest test suite (18 unit & integration tests)
│   ├── hydrology_engine.py          # Repaired legacy backward-compatibility wrapper
│   ├── main.py                      # FastAPI app entrypoint with lifespan & CORS
│   └── requirements.txt             # Pinned Python dependencies
│
├── frontend/
│   └── Hydro Refil/
│       ├── public/                  # SVG assets & icons
│       ├── src/
│       │   ├── components/
│       │   │   ├── charts/          # MonthlyRunoffChart & WaterBalanceChart
│       │   │   ├── forms/           # Step forms (Site, Roof, Rain, Demand, Soil)
│       │   │   ├── map/             # LocationPicker with Leaflet & OSM
│       │   │   ├── results/         # MetricCard, StructureCard, Formula Modal
│       │   │   └── ui/              # Navbar, Footer, Badges
│       │   ├── data/                # Static IMD rainfall & coefficient datasets
│       │   ├── domain/              # Client-side offline TypeScript engine
│       │   ├── pages/               # Dashboard, NewAssessment, Detail, List, Report
│       │   ├── services/            # Axios API client with local fallback
│       │   ├── types/               # TypeScript interface definitions
│       │   ├── App.tsx              # React Router setup
│       │   ├── main.tsx             # React DOM root
│       │   └── index.css            # Dark engineering styling system
│       ├── package.json             # Consolidated frontend package
│       ├── tailwind.config.js       # Custom colors & typography
│       └── vite.config.ts           # Vite bundler configuration
│
├── config/
│   └── hydrology-assumptions.json   # Centralized assumptions registry
├── docs/                            # Complete technical documentation suite
├── .env.example                     # Environment variables template
└── README.md                        # Project landing documentation
```
