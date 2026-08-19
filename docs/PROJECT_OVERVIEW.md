# PROJECT OVERVIEW — HydroRefil (SIH Solution)

## 1. Hackathon Problem Statement
> **Designing and development of an application for on-spot assessment of Rooftop Rainwater Harvesting (RTRWH) and Artificial Recharge potential, including calculation and sizing of appropriate RTRWH and Artificial Recharge (AR) structures.**

---

## 2. Core Problem & Engineering Gap
Across urban and rural India, field engineers, town planners, municipal surveyors, and property owners face significant challenges during on-site rainwater harvesting assessments:
1. **Lack of On-Spot Decision Support:** Assessors often rely on manual spreadsheets, back-of-the-envelope estimations, or delayed office calculations.
2. **Black-Box Sizing & Arbitrary Decisions:** Sizing of recharge pits, storage sumps, and filter chambers is frequently conducted using rule-of-thumb guesswork without hydrogeological justification.
3. **Complex GIS Dependencies:** Existing commercial GIS tools require costly proprietary software (e.g. Mapbox paid tokens, ArcGIS), heavy workstations, and reliable broadband.
4. **Failure to Address Subsoil Realities:** Structures are often proposed without verifying shallow water tables (leading to waterlogging/foundation seepage) or subsoil infiltration rates.

---

## 3. The HydroRefil Solution
**HydroRefil** is an engineered, lightweight, offline-capable digital platform designed specifically for **rapid (3–5 minute) on-spot RTRWH and Artificial Recharge evaluation**.

### Key Architectural Pillars:
- **Dual-Engine Deterministic Computation:** 100% mathematically transparent calculations implemented in both FastAPI (Python backend) and TypeScript (client-side offline domain), guaranteeing field operations even in low-connectivity areas.
- **Explainable Recommendation Engine:** Replaces opaque ML with an auditable engineering decision tree based on CGWB and BIS standards. Every recommendation provides its mathematical rationale, confidence rating, and formula substitution trace.
- **Zero-Cost GIS Integration:** Open-source OpenStreetMap and Leaflet mapping with instant GPS acquisition and built-in IMD district-level rainfall normal lookups across India.
- **Standardized Structure Sizing:** Automated calculation of indicative dimensions (L × W × D / Diameter), effective volume, gravel void porosity, and freeboard allowances.
- **Formal Dossier & Report Export:** 1-click printable and exportable field engineering dossiers complying with BIS IS 15797:2008 and CPHEEO standards.
