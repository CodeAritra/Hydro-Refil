# ENGINEERING ASSUMPTIONS & TRACEABILITY REGISTRY

All engineering parameters used in HydroRefil are registered with their numerical value, unit, reference standard, and domain confidence rating.

---

## 1. Runoff Coefficients ($C$)
*Source: CGWB Master Plan for Artificial Recharge (2005/2013), Table 3.2; BIS IS 15797:2008*

| Roofing Catchment Type | Default $C$ | Validated Range | Confidence | Applicability / Design Notes |
|---|---|---|---|---|
| **RCC / Concrete Slab** | **0.85** | 0.80 – 0.90 | HIGH | Flat or gently pitched RCC rooftop with standard maintenance. |
| **Corrugated Metal (CGI)** | **0.90** | 0.85 – 0.95 | HIGH | Galvanized iron or aluminum-zinc sheets. Smooth, impermeable. |
| **Clay / Country Tiles** | **0.80** | 0.75 – 0.85 | MEDIUM | Sloped roofs with terracotta tiles. Minor absorption in tile bodies. |
| **Asbestos Cement Sheet** | **0.75** | 0.70 – 0.80 | MEDIUM | Corrugated AC sheets. Suitable for recharge; non-potable only. |
| **Thatched / Grass Roof** | **0.40** | 0.30 – 0.50 | LOW | Traditional organic thatch. High retention; requires filtration. |
| **Green / Vegetated Roof** | **0.30** | 0.15 – 0.50 | LOW | Engineered soil substrate with sedum/plants. High retention. |

---

## 2. Collection & Loss Parameters
*Source: IS 15797:2008 Section 6; CGWB 2007 Guidelines*

| Parameter | Value | Unit | Citation |
|---|---|---|---|
| **System Collection Efficiency ($\eta$)** | **0.85** | Dimensionless | CGWB (2007) standard for well-maintained filter & gutter networks |
| **First-Flush Diverter Abstraction** | **2.0** | $mm$ per event | IS 15797:2008 Clause 6 standard first-flush volume |
| **Gravel Void Porosity ($\phi$)** | **0.40** | Dimensionless | Standard geotechnical void fraction for graded 40–20 mm gravel fill |
| **Recharge Freeboard ($h_{\text{free}}$)** | **0.30** | $m$ | Civil engineering safety margin above maximum ponding level |
| **Tank Freeboard Fraction** | **0.10** | Dimensionless | 10% volume allowance for overflow surge protection |

---

## 3. Subsoil Infiltration Capacities
*Source: CGWB Manual on Artificial Recharge (2007), Table 4.1*

| Soil Classification | Default Infiltration ($mm/hr$) | Indicative Range ($mm/hr$) | Suitability for In-Ground Recharge |
|---|---|---|---|
| **Gravel / Coarse Sand** | **50.0** | 30 – 100 | Excellent (High percolation capacity) |
| **Fine to Medium Sand** | **25.0** | 10 – 50 | Very Good (Ideal for standard recharge pits) |
| **Sandy Loam** | **12.0** | 5 – 20 | Good (Suitable for recharge pits & trenches) |
| **Loam** | **7.0** | 3 – 12 | Moderate (Recharge trenches preferred) |
| **Clay Loam** | **3.0** | 1 – 6 | Low (Requires deep shaft or large trench) |
| **Clay / Silt Layer** | **1.0** | 0.5 – 3 | Very Low (In-ground pits not recommended) |
| **Black Cotton (Vertisol)**| **0.5** | 0.1 – 2 | Problematic (High swelling; surface tank preferred)|
| **Unknown / Untested** | **5.0** | — | Conservative default (Field test required) |

---

## 4. Domestic & Institutional Water Demand Norms
*Source: BIS IS 1172:1993; CPHEEO Water Supply Manual (2000); Jal Jeevan Mission (2019)*

| Occupancy Category | Standard Norm | Unit | Governing Standard |
|---|---|---|---|
| **Urban Residential** | **135** | LPCD ($L/\text{person/day}$) | IS 1172 Table 1 / CPHEEO |
| **Rural Residential** | **70** | LPCD | Jal Jeevan Mission Guidelines |
| **Educational / Day School**| **45** | LPCD | IS 1172 Table 1 |
| **Office / Commercial** | **45** | LPCD | IS 1172 Table 1 |
| **Hostel / Boarding** | **135** | LPCD | IS 1172 Table 1 |
