# ARCHITECTURE DECISION RECORDS (ADR) — HydroRefil

This document records the foundational architectural decisions made during the design and development of HydroRefil for the Smart India Hackathon (SIH).

---

## ADR-01: Leaflet + OpenStreetMap over Mapbox GL JS
- **Status:** Accepted
- **Context:** The initial prototype had hardcoded placeholder Mapbox tokens (`'YOUR_MAPBOX_PUBLIC_TOKEN_HERE'`) which failed to load without a paid or registered Mapbox API account.
- **Decision:** Replace Mapbox with **Leaflet + OpenStreetMap** (`react-leaflet`).
- **Consequences:**
  - **Pros:** 100% free and open-source; zero paid API token barriers; no vendor lock-in; lightweight bundle size; reliable offline tile caching capabilities.
  - **Cons:** Standard vector styling instead of Mapbox Studio custom styles (mitigated by custom high-contrast CSS styling).

---

## ADR-02: SQLite Default with Asyncpg/PostgreSQL Scalability
- **Status:** Accepted
- **Context:** The legacy prototype connected directly to a mandatory external PostgreSQL + PostGIS server on startup (`postgres://postgres:password@localhost:5432/...`), causing immediate application crashes when run on local evaluator machines.
- **Decision:** Utilize **SQLAlchemy 2.0 Async ORM** with **SQLite (`aiosqlite`)** as the default zero-config embedded database, while keeping PostgreSQL (`asyncpg`) fully supported via the `DATABASE_URL` environment variable.
- **Consequences:**
  - **Pros:** The entire platform runs instantly on any machine with zero database server installation or Docker setup.
  - **Cons:** Advanced spatial queries are computed client-side using Turf.js rather than PostGIS SQL extensions.

---

## ADR-03: Deterministic Rule-Based Recommendations over Black-Box AI
- **Status:** Accepted
- **Context:** Sizing civil recharge pits and storage tanks requires engineering safety compliance (e.g. BIS IS 15797:2008 and CGWB guidelines).
- **Decision:** Implement a **deterministic, rule-based decision tree** with step-by-step formula substitutions and unit transparency rather than opaque neural network approximations.
- **Consequences:**
  - **Pros:** 100% explainable to SIH judges, government municipal engineers, and water-resources consultants; auditable calculation traces; zero hallucination risk.
  - **Cons:** Requires explicit codification of hydrogeological boundary conditions (which we have documented in `ASSUMPTIONS.md`).

---

## ADR-04: Dual-Engine Deterministic Architecture (Python + TypeScript)
- **Status:** Accepted
- **Context:** Field assessors frequently work in rural, peri-urban, or basement environments with degraded or absent cellular connectivity.
- **Decision:** Implement identical mathematical calculation engines in both Python (FastAPI backend) and TypeScript (`src/domain/hydrology.ts`), integrated with browser LocalStorage caching.
- **Consequences:**
  - **Pros:** The application functions seamlessly in 100% offline environments; field assessments can be conducted and reviewed even if the backend is stopped or unreachable.
  - **Cons:** Developers must maintain calculation consistency across both language implementations (enforced via developer documentation and automated tests).
