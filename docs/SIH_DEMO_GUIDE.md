# SMART INDIA HACKATHON (SIH) — 3-MINUTE DEMO GUIDE

**Problem Statement:**
> *Designing and development of an application for on-spot assessment of Rooftop Rainwater Harvesting (RTRWH) and Artificial Recharge potential, including calculation and sizing of appropriate RTRWH and Artificial Recharge (AR) structures.*

---

## ⏱️ Minute 0:00 – 0:45: The Problem & Solution Overview
1. **Open Dashboard (`http://localhost:5173`)**
   - **Statement:** *"Respected Judges, across India, field engineers assess rooftop rainwater harvesting with delayed manual spreadsheets and arbitrary sizing guesswork. HydroRefil solves this with an instant, on-spot digital decision support system compliant with CGWB and BIS IS 15797:2008 standards."*
   - Highlight the KPI cards: Total Evaluated Sites, Harvest Potential in $m^3$ and Litres, Catchment Area, and 100% Engineering Compliance.

---

## ⏱️ Minute 0:45 – 1:45: On-Spot Field Assessment & GIS Intelligence
1. **Click "Start Assessment" or "Load 1-Click Sample for Presentation"**
2. **Show the 6-Step Rapid Wizard:**
   - **Step 1 (Site):** Enter Building / Campus Name (e.g. *Kendriya Vidyalaya Campus*).
   - **Step 2 (Location / Map):**
     - Select a district from the **Quick Select Indian District** dropdown (e.g. *New Delhi — 790 mm* or *Kolkata — 1600 mm*).
     - Point out the **real-time Leaflet OpenStreetMap integration**, GPS acquisition, and auto-populated IMD climatological normal rainfall.
   - **Step 3 (Roof):** Enter Roof Area (e.g. $850\text{ m}^2$) and choose material (RCC slab $C=0.85$ or CGI Sheet $C=0.90$).
   - **Step 4 (Rainfall):** Explain the automated 12-month South-West monsoon hydrograph distribution.
   - **Step 5 (Demand):** Enter occupant count (e.g. 45 people at 45 LPCD) and non-potable domestic target ratio.
   - **Step 6 (Subsoil):** Select soil classification (Sandy Loam, Infiltration $12\text{ mm/hr}$) and water table depth ($14.5\text{ m}$ BGL).
3. **Point to the Live Calculation Dock on the right:**
   - Show how yield, structure recommendation, and demand met percentage update **in real-time as inputs change**.

---

## ⏱️ Minute 1:45 – 2:30: Sizing, Transparency & Explainability
1. **Click "Execute Assessment & Save"**
2. **Walkthrough Results Screen:**
   - **Net Harvest Potential:** $221\text{ m}^3 / \text{year}$ ($221,000\text{ Litres}$).
   - **Recommended Structure:** *Gravel-Filled Recharge Pit* with calculated indicative dimensions: $4.69\text{ m (L)} \times 4.69\text{ m (W)} \times 2.50\text{ m (D)}$ accounting for $40\%$ gravel void porosity and $0.30\text{ m}$ freeboard.
   - **Interactive Hydrograph:** Monthly rainfall line vs. harvestable runoff bars vs. consumption demand line.
   - **Water Balance Chart:** Clear visual comparison between harvest, demand, and aquifer recharge.
3. **Click "Inspect Formulas" (KEY JUDGE-FRIENDLY FEATURE):**
   - **Show the Mathematical Audit Trail:** Open the modal to show every equation, substituted numerical values, unit relationships, and citations (BIS IS 15797:2008 & CGWB 2007). Emphasize: *"HydroRefil is not a black box — every metric is 100% mathematically transparent and auditable."*

---

## ⏱️ Minute 2:30 – 3:00: Field Report & Offline Resilience
1. **Click "Generate Field Report"**
   - Show the clean, formal engineering dossier with site info, metrics table, structure sizing, and official sign-off blocks.
   - Click **"Print / Save as PDF"** to demonstrate one-click field export.
2. **Concluding Key Highlights:**
   - **Offline Resilience:** Works completely offline in remote field areas without internet.
   - **Zero Proprietary Cost:** Uses open-source OpenStreetMap (no paid Mapbox tokens).
   - **Production-Quality Architecture:** FastAPI backend + React 19 frontend + 18 passing Pytest automated tests.
