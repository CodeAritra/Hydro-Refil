# SOFTWARE REQUIREMENTS SPECIFICATION — HydroRefil

## 1. Functional Requirements (FR)

### FR-01 — Site & Property Assessment Creation
- **FR-01.1:** System shall enable users to initialize an assessment record containing: Site Identifier, Assessor Name, Agency / Organization, and Field Remarks.
- **FR-01.2:** System shall assign a unique UUID identifier and UTC timestamp to each assessment dossier.

### FR-02 — Geographic Location & GIS Capture
- **FR-02.1:** System shall provide an interactive map interface using Leaflet and OpenStreetMap.
- **FR-02.2:** System shall support acquiring real-time field coordinates via the W3C Geolocation API.
- **FR-02.3:** System shall support manual coordinate (Latitude/Longitude) inputs with bi-directional synchronization to the map marker.
- **FR-02.4:** System shall provide a curated Indian district selector that auto-fills geographic coordinates and IMD climatological normal annual rainfall.

### FR-03 — Catchment & Rooftop Characterization
- **FR-03.1:** System shall capture effective rooftop catchment area in square meters ($m^2$) with automatic square feet conversion.
- **FR-03.2:** System shall provide selectable standard roofing materials with verified runoff coefficients ($C$):
  - Reinforced Cement Concrete (RCC): $C = 0.85$ (Range: $0.80 - 0.90$)
  - Corrugated Galvanized Iron / Metal: $C = 0.90$ (Range: $0.85 - 0.95$)
  - Clay / Country Tiles: $C = 0.80$ (Range: $0.75 - 0.85$)
  - Asbestos Cement Sheet: $C = 0.75$ (Range: $0.70 - 0.80$)
  - Thatched / Grass Roof: $C = 0.40$ (Range: $0.30 - 0.50$)
  - Green / Vegetated Roof: $C = 0.30$ (Range: $0.15 - 0.50$)
- **FR-03.3:** System shall support downpipe count and first-flush diverter configuration (IS 15797:2008 standard).

### FR-04 — Rainfall Data & Monthly Hydrograph
- **FR-04.1:** System shall accept annual normal rainfall in millimeters ($mm/year$).
- **FR-04.2:** System shall generate a 12-month synthetic rainfall and harvest hydrograph modeled on the Indian South-West monsoon distribution.

### FR-05 — Water Consumption & Balance Modelling
- **FR-05.1:** System shall calculate user water demand based on occupant count and Indian per-capita norms (IS 1172:1993 / CPHEEO 135 LPCD for urban; 70 LPCD for rural; 45 LPCD for educational/office).
- **FR-05.2:** System shall compute percentage of non-potable domestic demand met by harvested rainwater.

### FR-06 — Artificial Recharge Potential Assessment
- **FR-06.1:** System shall evaluate subsoil infiltration capacity based on USDA/CGWB soil classification ($mm/hr$) or field test entry.
- **FR-06.2:** System shall enforce a safety guard: if groundwater depth $< 3.0\text{ m}$ BGL, artificial recharge structures are marked `NOT_RECOMMENDED` to prevent waterlogging.

### FR-07 — Structure Sizing & Dimension Calculations
- **FR-07.1:** System shall compute indicative structural dimensions (Length, Width, Depth, or Diameter), effective volume, gravel void porosity ($40\%$), and freeboard ($0.25 - 0.50\text{ m}$).
- **FR-07.2:** Structures supported: Surface/Sump Storage Tank, Gravel-Filled Recharge Pit, Continuous Recharge Trench, and Bore-well Recharge Shaft.

### FR-08 — Explainability & Engineering Audit Trail
- **FR-08.1:** System shall provide an interactive Formula Inspection Modal displaying exact equations, substituted numerical values, unit relationships, and standard citations.

### FR-09 — Field Dossier & PDF Export
- **FR-09.1:** System shall generate a print-ready, professional engineering field report formatted with official disclaimers, signature blocks, and tabular summaries.

---

## 2. Non-Functional Requirements (NFR)

- **NFR-01 (Offline Capability):** The core calculation engine must run entirely in the browser using client-side TypeScript if the backend server or internet is unreachable.
- **NFR-02 (Performance):** Hydrological calculations must complete in $< 50\text{ ms}$ on mobile/tablet devices.
- **NFR-03 (Zero Proprietary Cost):** The system must not require paid API tokens (such as paid Mapbox keys).
- **NFR-04 (Security):** No hardcoded credentials; input sanitization against injection; safe CORS headers.
- **NFR-05 (Accessibility & UX):** High-contrast dark engineering theme, responsive layouts across mobile, tablet, and desktop viewports.
