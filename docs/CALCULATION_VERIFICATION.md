# CALCULATION VERIFICATION & BENCHMARK AUDIT

This document provides step-by-step manual mathematical verifications of benchmark test cases to validate that the HydroRefil calculation engine produces accurate, deterministic, and unit-consistent results.

---

## Benchmark Case A: Residential Building (Kolkata)
### Inputs:
- **Roof Area ($A$):** $200.0\text{ m}^2$
- **Roof Material:** RCC Concrete ($C = 0.85$)
- **Annual Rainfall ($P$):** $1,600.0\text{ mm}$
- **System Efficiency ($\eta$):** $0.85$
- **First Flush Depth ($d_{\text{ff}}$):** $2.0\text{ mm}$
- **Occupants:** $5\text{ people}$ at $135\text{ LPCD}$ ($40\%$ non-potable)
- **Soil Type:** Sandy Loam ($I = 12.0\text{ mm/hr}$), Water table at $12.0\text{ m}$ BGL

### Manual Step-by-Step Calculation:
1. **Gross Runoff:**
   $$V_{\text{gross}} = 1600 \times 200 \times 0.85 = \mathbf{272,000\text{ Litres}}$$
2. **Estimated Storm Events:**
   $$N_{\text{events}} = \lfloor 1600 / 10 \rfloor = 160\text{ events}$$
3. **First-Flush Diversion:**
   $$V_{\text{ff}} = 2.0\text{ mm} \times 200\text{ m}^2 \times 160 = \mathbf{64,000\text{ Litres}}$$
4. **Volume after First-Flush:**
   $$V_{\text{after}} = 272,000 - 64,000 = 208,000\text{ Litres}$$
5. **Net Harvestable Volume:**
   $$V_{\text{net}} = 208,000 \times 0.85 = \mathbf{176,800\text{ Litres}} = \mathbf{176.80\text{ m}^3}$$
6. **Annual Demand:**
   $$D_{\text{gross}} = 5 \times 135 \times 365 = 246,375\text{ Litres}$$
   $$D_{\text{target, non-potable}} = 246,375 \times 0.40 = \mathbf{98,550\text{ Litres}} = 98.55\text{ m}^3$$
7. **Demand Met Ratio:**
   $$\text{Demand Met} = \min\left(100\%, \frac{176,800}{98,550} \times 100\right) = \mathbf{100.0\%} \text{ (Surplus of } 78.25\text{ m}^3\text{)}$$
8. **Structure Sizing (Recharge Pit):**
   - Peak storm volume $V_{\text{design}} \approx (176.80 \times 0.30) = 53.04\text{ m}^3 \to \text{capped at } 50.0\text{ m}^3$
   - Gross volume $V_{\text{gross}} = 50.0 / 0.40 = 125.0\text{ m}^3$
   - Depth $d = 2.5\text{ m} \to \text{Plan Area } A = 125.0 / 2.5 = 50.0\text{ m}^2$
   - Side $L = W = \sqrt{50.0} \approx \mathbf{7.07\text{ m}}$
   - Calculated Dimensions: $7.07\text{ m (L)} \times 7.07\text{ m (W)} \times 2.50\text{ m (D)}$

### Software Output:
- $V_{\text{net}} = 176,800\text{ L}$ ($176.80\text{ m}^3$) ✓ Matches exactly
- Structure: Gravel-Filled Recharge Pit ✓ Matches exactly

---

## Benchmark Case B: High Water Table Constraint (Coastal Kerala)
### Inputs:
- **Roof Area ($A$):** $150.0\text{ m}^2$, Sheet roofing ($C = 0.90$)
- **Annual Rainfall ($P$):** $3,000.0\text{ mm}$
- **Water Table Depth:** $1.8\text{ m}$ BGL ($< 3.0\text{ m}$ limit)

### Manual Verification:
- Water table depth of $1.8\text{ m} < 3.0\text{ m}$ safety threshold.
- In-ground pit / trench is **UNFEASIBLE** (would flood basement / waterlog soil).
- Software must automatically select **Surface Storage Tank** with $0.0\text{ m}$ pit depth.

### Software Output:
- Feasibility: `HIGHLY_FEASIBLE` for storage; `NOT_RECOMMENDED` for recharge.
- Recommended Structure: **Rainwater Storage Tank (Surface / Sump)** ✓ Matches exactly
