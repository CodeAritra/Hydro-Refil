# ENGINEERING & HYDROLOGICAL METHODOLOGY — HydroRefil

## 1. Fundamental Unit Relationship
A foundational physical principle in hydrology:
$$\mathbf{1\text{ mm of rainfall over } 1\text{ m}^2 \text{ of catchment area} = 1\text{ Litre of water}}$$

**Mathematical Proof:**
$$1\text{ mm} = 10^{-3}\text{ m}$$
$$\text{Volume} = \text{Area } (m^2) \times \text{Depth } (m) = 1\text{ m}^2 \times 10^{-3}\text{ m} = 10^{-3}\text{ m}^3$$
$$\text{Since } 1\text{ m}^3 = 1,000\text{ Litres:}$$
$$\text{Volume} = 10^{-3} \times 1,000\text{ Litres} = \mathbf{1\text{ Litre}}$$

---

## 2. Rooftop Rainwater Harvesting Model

### 2.1 Gross Runoff Potential ($V_{\text{gross}}$)
$$V_{\text{gross}} = P \times A \times C$$
Where:
- $P$ = Annual normal rainfall ($mm$)
- $A$ = Rooftop catchment plan area ($m^2$)
- $C$ = Runoff coefficient (dimensionless, $0.0 < C \le 1.0$)

### 2.2 First-Flush Diversion Loss ($V_{\text{ff}}$)
In accordance with **IS 15797:2008 Clause 6**, the first $2.0\text{ mm}$ of rainfall per event carries the highest concentration of dust, bird droppings, and atmospheric pollutants and must be diverted away from storage:
$$V_{\text{ff}} = d_{\text{ff}} \times A \times N_{\text{events}}$$
Where:
- $d_{\text{ff}} = 2.0\text{ mm}$ (Standard first-flush abstraction)
- $N_{\text{events}} \approx \max(1, \lfloor P / 10 \rfloor)$ (Estimated storm events per year based on IMD climatological averages)

### 2.3 Net Harvestable Yield ($V_{\text{net}}$)
$$V_{\text{net}} = (V_{\text{gross}} - V_{\text{ff}}) \times \eta_{\text{system}}$$
Where:
- $\eta_{\text{system}} = 0.85$ ($85\%$ collection efficiency accounting for gutter transmission, filter resistance, and minor splashing per CGWB 2007 guidelines).

---

## 3. Water Balance & Demand Fulfillment

### 3.1 Total Annual Water Demand ($D_{\text{annual}}$)
$$D_{\text{annual}} = (N_{\text{people}} \times q_{\text{lpcd}} + D_{\text{additional}}) \times 365$$
Where $q_{\text{lpcd}}$ is the per-capita daily consumption norm:
- Urban Residential: $135\text{ LPCD}$ (IS 1172 / CPHEEO)
- Rural Domestic: $70\text{ LPCD}$ (Jal Jeevan Mission norm)
- Institutional / School: $45\text{ LPCD}$ (IS 1172)

### 3.2 Non-Potable Target Harvest Demand ($D_{\text{target}}$)
$$D_{\text{target}} = D_{\text{annual}} \times f_{\text{non-potable}}$$
Default $f_{\text{non-potable}} = 0.40$ ($40\%$ for toilet flushing, landscaping, and washing).

### 3.3 Demand Met Ratio
$$\text{Demand Met } (\%) = \min\left(100\%, \frac{V_{\text{net}}}{D_{\text{target}}} \times 100\right)$$

---

## 4. Artificial Groundwater Recharge Sizing

### 4.1 Safety Feasibility Guards (CGWB 2007)
1. **Groundwater Table Guard:** If water table depth $< 3.0\text{ m}$ BGL, artificial recharge structures are flagged **UNFEASIBLE / NOT RECOMMENDED** due to waterlogging and foundation seepage risks. Surface storage tanks are selected instead.
2. **Infiltration Guard:** If soil infiltration $I < 1.0\text{ mm/hr}$, surface pits are marked ineffective. Deep injection recharge shafts or surface sumps are recommended.

### 4.2 Gravel-Filled Recharge Pit Sizing
A recharge pit is filled with graded gravel and coarse sand. Because the gravel occupies space, the pit's gross volume must account for gravel void porosity ($\phi = 0.40$ or $40\%$ void space):
$$V_{\text{gross}} = \frac{V_{\text{design}}}{\phi_{\text{gravel}}} = \frac{V_{\text{design}}}{0.40} = 2.5 \times V_{\text{design}}$$
$$\text{Plan Area } (A_{\text{pit}}) = \frac{V_{\text{gross}}}{\text{Depth } (d_{\text{pit}})}$$
$$\text{Square Side } (L = W) = \sqrt{A_{\text{pit}}}$$

### 4.3 Continuous Recharge Trench Sizing
$$\text{Length } (L) = \frac{V_{\text{gross}}}{\text{Width } (1.0\text{ m}) \times \text{Depth } (1.5\text{ m})}$$

### 4.4 Rainwater Storage Sump / Tank Sizing
$$V_{\text{tank, req}} = V_{\text{design}} \times (1 + \text{Freeboard Fraction } 0.10)$$
$$\text{Plan Area } = \frac{V_{\text{tank, req}}}{\text{Depth } (\le 3.0\text{ m})}$$
$$\text{Side } = \sqrt{\text{Plan Area}}$$

---

## 5. Standard Institutional Citations
1. **BIS IS 15797:2008** — *Rooftop Rainwater Harvesting: Guidelines*, Bureau of Indian Standards, New Delhi.
2. **CGWB (2007)** — *Manual on Artificial Recharge of Ground Water*, Central Ground Water Board, Ministry of Water Resources, Govt. of India.
3. **CGWB (2013)** — *Master Plan for Artificial Recharge to Ground Water in India*, CGWB, Faridabad.
4. **CPHEEO (2000)** — *Manual on Water Supply and Treatment*, Ministry of Urban Development, New Delhi.
5. **BIS IS 1172:1993** — *Code of Basic Requirements for Water Supply, Drainage and Sanitation*, BIS, New Delhi.
