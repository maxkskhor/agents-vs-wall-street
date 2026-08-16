# Analog Devices — FY2026Q3 forecast audit trail

| Metric | Units | Final forecast |
|---|---|---:|
| Revenue | USDm | **3910.0** |
| Adjusted diluted EPS | USD / share | **3.3279** |
| Adjusted gross margin | % | **73.0** |


## Revenue (USDm) = 3910.0

- **Final** = consensus + 0.85 x (ensemble - consensus) = 3910.0 + 0.85 × (3910 − 3910.0) = 3910
- **Ensemble** = weighted mean of method values = 3910 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 3900
- sample [openai#0] base 3623.465 (FY2026Q2) → 3900
    - +276.535 — Aligns the latest reported quarter with management's FY2026Q3 revenue guidance midpoint of $3.9 billion. [Guidance FY2026Q3, 2026-05-20: "we are forecasting revenue of $3.9 billion, +/- $100 million."]
- sample [openai#1] base 3623.465 (FY2026Q2) → 3900
    - +276.535 — Increase revenue to the midpoint of management's FY2026Q3 guidance. [[guidance FY2026Q3, 2026-05-20] revenue forecast of $3.9 billion, +/- $100 million.]
- sample [openai#2] base 3623.465 (FY2026Q2) → 3900
    - +276.535 — Raises revenue to the midpoint of the explicit FY2026Q3 guidance of $3.9 billion. [Guidance FY2026Q3: revenue of $3.9 billion, +/- $100 million (2026-05-20).]
- sample [openai#3] base 3623.465 (FY2026Q2) → 3900
    - +276.535 — Raises revenue to the midpoint of management's FY2026Q3 guidance. [FY2026Q3 guidance: revenue of $3.9 billion, +/- $100 million.]
- sample [openai#4] base 3623.465 (FY2026Q2) → 3900
    - +276.535 — Aligns the latest reported revenue with the midpoint of management's FY2026Q3 revenue guidance. [FY2026Q3 guidance: revenue of $3.9 billion, +/- $100 million.]

### statistical → 3691
- formula: prior-year value 2880.348 x (1 + median YoY growth +28.158%)

### guidance → 4004
- formula: midpoint of stated guidance = 3900.0
- evidence (2026-05-20__adi-us-20260520-q2-8k-2__1040614.md): “For the third quarter of fiscal 2026, we are forecasting revenue of $3.9 billion, +/- $100 million.”

- reported history used: {"FY2025H1": 5063.242, "FY2025Q1": 2423.174, "FY2025Q2": 2640.068, "FY2025Q3": 2880.348, "FY2025Q4": 3076.117, "FY2026H1": 6783.728, "FY2026Q1": 3160.063, "FY2026Q2": 3623.465}

## Adjusted gross margin (%) = 73.0

- **Ensemble** = weighted median of method values = 73 (weights {'derived': 0.6, 'guidance': 0.25, 'llm_analyst': 0.45, 'statistical': 0.3})

### llm_analyst → 73
- sample [openai#0] base 73.0 (FY2026Q2) → 72.8
    - -0.2 — Apply the recent seasonal Q2-to-Q3 margin pattern. [FY2025Q2 adjusted gross margin was 69.4% versus 69.2% in FY2025Q3, a decline of 0.2 percentage point]
- sample [openai#1] base 73.0 (FY2026Q2) → 73
    - +0.2 — Recent sequential margin momentum supports a modest upward adjustment. [Adjusted gross margin increased from 71.2% in FY2026Q1 to 73.0% in FY2026Q2.]
    - -0.2 — A small seasonal offset reflects the prior-year sequential pattern into the third quarter. [Adjusted gross margin declined from 69.4% in FY2025Q2 to 69.2% in FY2025Q3.]
- sample [openai#2] base 73.0 (FY2026Q2) → 73
    - +0.2 — Carry forward part of the recent margin expansion into the next quarter. [Adjusted gross margin increased from 71.2% in FY2026Q1 to 73.0% in FY2026Q2, following 69.8% in FY20]
    - -0.2 — Allow for potentially weaker or less favorable Q3 seasonality given the mixed historical pattern. [FY2025Q3 margin was 69.2%, down from 69.4% in FY2025Q2, although FY2024Q3 increased to 67.9% from 66]
- sample [openai#3] base 73.0 (FY2026Q2) → 72.8
    - -0.2 — Apply a modest sequential seasonal reduction ahead of the target quarter. [FY2025Q3 was 0.2 percentage points below FY2025Q2 (69.2% versus 69.4%).]
- sample [openai#4] base 73.0 (FY2026Q2) → 73.5
    - +0.5 — Apply the average FY2024Q2-to-Q3 and FY2025Q2-to-Q3 sequential movement as a limited historical seasonality adjustment. [FY2024Q2 to FY2024Q3: +1.2 percentage points; FY2025Q2 to FY2025Q3: -0.2 percentage points.]
- sample [openai#5] base 73.0 (FY2026Q2) → 73.5
    - +0.5 — Apply the average historical Q3-versus-Q2 adjusted gross-margin change as a modest seasonal continuation. [FY2024Q3 was 1.2 percentage points above FY2024Q2, while FY2025Q3 was 0.2 points below FY2025Q2; ave]
- sample [openai#6] base 73.0 (FY2026Q2) → 72.8
    - -0.2 — Apply a modest sequential seasonal reduction based on the prior-year Q2-to-Q3 movement. [FY2025Q2 to FY2025Q3 declined from 69.4% to 69.2%.]
- sample [openai#7] base 73.0 (FY2026Q2) → 73.3
    - +0.5 — Carry forward the recent sequential improvement in adjusted gross margin. [Adjusted gross margin increased from 71.2% in FY2026Q1 to 73.0% in FY2026Q2.]
    - -0.2 — Temper the sequential uplift because no FY2026Q3 guidance or pre-announcement evidence was supplied. [Guidance / pre-announcement evidence: none extracted.]

### statistical → 71.35
- formula: prior-year level 69.2 + median YoY delta +2.15pp

- reported history used: {"FY2025H1": 69.1, "FY2025Q1": 68.8, "FY2025Q2": 69.4, "FY2025Q3": 69.2, "FY2025Q4": 69.8, "FY2026H1": 72.2, "FY2026Q1": 71.2, "FY2026Q2": 73.0}

## Adjusted diluted EPS (USD / share) = 3.3279

- **Final** = consensus + 0.85 x (ensemble - consensus) = 3.34 + 0.85 × (3.326 − 3.34) = 3.328
- **Ensemble** = weighted mean of method values = 3.326 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 3.3
- sample [openai#0] base 3.09 (FY2026Q2) → 3.3
    - +0.21 — Move the base to management's midpoint guidance for the target quarter. [FY2026Q3 guidance: adjusted EPS planned at $3.30, +/-$0.15; FY2026Q2 reported adjusted EPS was $3.09]
- sample [openai#1] base 3.09 (FY2026Q2) → 3.3
    - +0.21 — Move from FY2026Q2 actual EPS to the midpoint of explicit FY2026Q3 adjusted EPS guidance. [FY2026Q3 guidance: adjusted EPS planned at $3.30, +/-$0.15, versus FY2026Q2 reported adjusted EPS of]
- sample [openai#2] base 3.09 (FY2026Q2) → 3.3
    - +0.21 — Increase to ADI's explicit FY2026Q3 adjusted EPS guidance midpoint of $3.30 from the FY2026Q2 reported adjusted EPS of $3.09. [Guidance FY2026Q3: adjusted EPS $3.30 +/-$0.15; FY2026Q2 reported adjusted diluted EPS: $3.09.]
- sample [openai#3] base 3.09 (FY2026Q2) → 3.3
    - +0.21 — Move to management's midpoint guidance for the target quarter. [FY2026Q3 guidance: adjusted EPS of $3.30, +/-$0.15, versus FY2026Q2 reported adjusted EPS of $3.09.]
- sample [openai#4] base 3.09 (FY2026Q2) → 3.3
    - +0.21 — Apply the sequential increase implied by management's FY2026Q3 adjusted EPS guidance relative to the FY2026Q2 reported result. [FY2026Q3 guidance: adjusted EPS of $3.30 +/-$0.15; FY2026Q2 history: $3.09.]

### statistical → 2.934
- formula: prior-year value 2.05 x (1 + median YoY growth +43.125%)

### guidance → 3.498
- formula: midpoint of stated guidance = 3.3
- evidence (2026-05-20__adi-us-20260520-q2-8k-2__1040614.md): “We are planning for reported EPS to be $2.60, +/-$0.15, and adjusted EPS to be $3.30, +/-$0.15.”

- reported history used: {"FY2025H1": 3.48, "FY2025Q1": 1.63, "FY2025Q2": 1.85, "FY2025Q3": 2.05, "FY2025Q4": 2.26, "FY2026H1": 5.54, "FY2026Q1": 2.46, "FY2026Q2": 3.09}

## Validation

| Check | Status | Detail |
|---|---|---|
| revenue: value present | PASS | final=3910.0 |
| revenue: magnitude vs prior year | PASS | 3910.0 vs prior-year 2880.348 (ratio 1.36, band 0.7-1.42) |
| revenue: analyst-sample agreement | PASS | cross-provider spread 0 (0.0% of final) |
| adj_eps: value present | PASS | final=3.3279 |
| adj_eps: magnitude vs prior year | PASS | 3.3279 vs prior-year 2.05 (ratio 1.62, band 0.55-1.7) |
| adj_eps: analyst-sample agreement | PASS | cross-provider spread 0 (0.0% of final) |
| adj_gross_margin: value present | PASS | final=73.0 |
| adj_gross_margin: plausibility vs prior year | PASS | 73.0pp vs prior-year 69.2pp (max delta 4.0pp) |
| adj_gross_margin: analyst-sample agreement | PASS | cross-provider spread 0.7 (1.0% of final) |
| ADI: gross margin absolute range | PASS | adjusted gross margin 73.0% must be a percentage level (55-80) |
| red-team review | PASS | no objections (openai) |