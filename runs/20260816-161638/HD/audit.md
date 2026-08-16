# Home Depot — FY2026Q2 forecast audit trail

| Metric | Units | Final forecast |
|---|---|---:|
| Net sales | USDm | **46876.0** |
| Adjusted diluted EPS | USD / share | **4.7343** |
| Comparable sales, total company | % | **1.1333** |


## Net sales (USDm) = 46876.0

- **Final** = consensus + 0.85 x (ensemble - consensus) = 47325.0 + 0.85 × (4.68e+04 − 47325.0) = 4.688e+04
- **Ensemble** = weighted mean of method values = 4.68e+04 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 4.686e+04
- sample [openai#0] base 45277.0 (FY2025Q2) → 4.686e+04
    - +1132.0 — Applies the low end of management's FY2026 total-sales-growth outlook to the prior-year comparable quarter. [FY2026 guidance: total sales growth of approximately 2.5% to 4.5%.]
    - +454.0 — Adds support for growth above the guidance floor, reflecting the stronger-than-floor performance already reported in FY2026Q1. [FY2026Q1 net sales were USD 41,765m versus USD 39,856m in FY2025Q1, approximately 4.8% year over yea]
- sample [openai#1] base 45277.0 (FY2025Q2) → 4.686e+04
    - +1584.7 — Apply the midpoint of FY2026 total sales growth guidance (3.5%) to the prior-year comparative quarter as a proxy for quarterly growth. [FY2026 guidance: total sales growth approximately 2.5% to 4.5%; FY2025Q2 net sales were USD 45,277.0]
- sample [openai#2] base 45277.0 (FY2025Q2) → 4.686e+04
    - +1131.9 — Apply the low end of current FY2026 sales-growth guidance to the prior-year comparative. [FY2026 guidance: total sales growth approximately 2.5% to 4.5% (2026-05-19).]
    - +452.8 — Add the one-percentage-point uplift from the guidance floor to its midpoint, reflecting the central FY2026 growth assumption. [FY2026 guidance range of approximately 2.5% to 4.5% (2026-05-19).]
- sample [openai#3] base 45277.0 (FY2025Q2) → 4.745e+04
    - +2169.0 — Apply FY2026Q1 year-over-year growth of approximately 4.8% to the prior-year Q2 base as a near-term run-rate proxy. [FY2026Q1 sales were 41,765.0 versus FY2025Q1 sales of 39,856.0; FY2025Q2 sales were 45,277.0.]
- sample [openai#4] base 45277.0 (FY2025Q2) → 4.686e+04
    - +1585.0 — Apply the midpoint of the current FY2026 total-sales-growth guidance range to the prior-year comparable quarter. [FY2026 guidance: total sales growth of approximately 2.5% to 4.5%; midpoint 3.5% × FY2025Q2 sales of]

### statistical → 4.7e+04
- formula: prior-year value 45277.0 x (1 + median YoY growth +3.806%)

### guidance → 4.668e+04
- formula: FY2026 implied total 170447 (prior 164683 x 1+3.5%), minus reported 41765, remaining spread over prior-year remaining quarters
- evidence (2026-05-19__hd-us-20260519-q1-8k-2__1038586.md): “•Total sales growth of approximately 2.5% to 4.5%”

- reported history used: {"FY2024Q4": 39704.0, "FY2025": 164683.0, "FY2025H1": 85133.0, "FY2025Q1": 39856.0, "FY2025Q2": 45277.0, "FY2025Q3": 41352.0, "FY2025Q4": 38198.0, "FY2026Q1": 41765.0}

## Comparable sales, total company (%) = 1.1333

- **Ensemble** = weighted median of method values = 1.133 (weights {'derived': 0.6, 'guidance': 0.25, 'llm_analyst': 0.45, 'statistical': 0.3})

### llm_analyst → 1
- sample [openai#0] base 0.6 (FY2026Q1) → 1
    - +0.4 — Move toward the midpoint of management's FY2026 comparable-sales guidance range. [FY2026 guidance: comparable sales growth of approximately flat to 2.0%, implying a 1.0% midpoint.]
- sample [openai#1] base 0.6 (FY2026Q1) → 1
    - +0.4 — Move toward the midpoint of management's FY2026 comparable-sales guidance range. [FY2026 guidance: comparable sales growth approximately flat to 2.0%; FY2026Q1 reported comparable sa]
- sample [openai#2] base 0.6 (FY2026Q1) → 1
    - +0.4 — Move toward the midpoint of management's FY2026 comparable-sales guidance range of approximately flat to 2.0%. [FY2026 guidance: "Comparable sales growth of approximately flat to 2.0%"]
- sample [openai#3] base 0.6 (FY2026Q1) → 1
    - +0.4 — Move toward the midpoint of management's FY2026 comparable-sales guidance range of approximately flat to 2.0%. [FY2026 guidance: "Comparable sales growth of approximately flat to 2.0%"]
- sample [openai#4] base 0.6 (FY2026Q1) → 1
    - +0.4 — Move toward the midpoint of management's FY2026 comparable-sales growth guidance range of approximately flat to 2.0%. [FY2026 guidance: "Comparable sales growth of approximately flat to 2.0%"; FY2026Q1 reported comparab]

### statistical → 2.2
- formula: prior-year level 1.0 + median YoY delta +1.20pp

### guidance → 1.133
- formula: FY guided level 1.0pp with reported quarters {'FY2026Q1': 0.6} -> remaining-quarter level
- evidence (2026-05-19__hd-us-20260519-q1-8k-2__1038586.md): “•Comparable sales growth of approximately flat to 2.0%”

- reported history used: {"FY2024Q4": 0.8, "FY2025": 0.3, "FY2025H1": 0.4, "FY2025Q1": -0.3, "FY2025Q2": 1.0, "FY2025Q3": 0.2, "FY2025Q4": 0.4, "FY2026Q1": 0.6}

## Adjusted diluted EPS (USD / share) = 4.7343

- **Final** = consensus + 0.85 x (ensemble - consensus) = 4.73 + 0.85 × (4.735 − 4.73) = 4.734
- **Ensemble** = weighted mean of method values = 4.735 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 4.64
- sample [openai#0] base 4.68 (FY2025Q2) → 4.73
    - -0.13 — Apply the latest observed year-over-year EPS decline as a near-term performance signal. [FY2026Q1 adjusted diluted EPS was $3.43 versus $3.56 in FY2025Q1.]
    - +0.18 — Allow for recovery in the remaining quarters consistent with the midpoint of FY2026 adjusted EPS guidance of approximately flat to 4.0% growth. [FY2026 guidance calls for adjusted diluted EPS to grow approximately flat to 4.0% from $14.69 in FY2]
- sample [openai#1] base 4.68 (FY2025Q2) → 4.6
    - -0.13 — Apply the latest observed year-over-year EPS decline as a conservative near-term run-rate adjustment. [FY2026Q1 adjusted diluted EPS was $3.43 versus $3.56 in FY2025Q1.]
    - +0.05 — Partially offset the Q1 decline because management maintained a full-year outlook for approximately flat to 4.0% EPS growth. [FY2026 guidance: adjusted diluted EPS to grow approximately flat to 4.0% from $14.69 in FY2025.]
- sample [openai#2] base 4.68 (FY2025Q2) → 4.62
    - -0.13 — Apply the year-over-year decline observed in the latest reported quarter. [FY2026Q1 adjusted diluted EPS was $3.43 versus $3.56 in FY2025Q1.]
    - +0.07 — Allow for partial recovery consistent with the midpoint of FY2026 adjusted EPS guidance of approximately flat to 4.0% growth. [FY2026 guidance calls for adjusted diluted EPS growth of approximately flat to 4.0% from $14.69 in F]
- sample [openai#3] base 4.68 (FY2025Q2) → 4.68
    - -0.13 — Apply the latest observed year-over-year EPS decline as a near-term momentum adjustment. [FY2026Q1 EPS was $3.43 versus $3.56 in FY2025Q1, a $0.13 decline.]
    - +0.13 — Allow for recovery in the remaining fiscal year consistent with achieving the low end of management's flat full-year EPS guidance after the Q1 decline. [Management guided FY2026 adjusted diluted EPS to grow approximately flat to 4.0% from $14.69 in FY20]
- sample [openai#4] base 4.68 (FY2025Q2) → 4.64
    - +0.09 — Lift toward the midpoint of management's FY2026 adjusted EPS growth range, implying approximately 2% year-over-year growth. [FY2026 guidance: adjusted diluted EPS to grow approximately flat to 4.0% from $14.69 in fiscal 2025.]
    - -0.13 — Reduce for the latest reported quarterly run rate, which was below the prior-year comparable. [FY2026Q1 adjusted diluted EPS was $3.43 versus $3.56 in FY2025Q1.]

### statistical → 4.57
- formula: prior-year value 4.68 x (1 + median YoY growth -2.355%)

### guidance → 4.858
- formula: FY2026 implied total 15 (prior 15 x 1+2.0%), minus reported 3, remaining spread over prior-year remaining quarters
- evidence (2026-05-19__hd-us-20260519-q1-8k-2__1038586.md): “•Adjusted diluted earnings-per-share to grow approximately flat to 4.0% from $14.69 in fiscal 2025”

- reported history used: {"FY2024Q4": 3.13, "FY2025": 14.69, "FY2025H1": 8.24, "FY2025Q1": 3.56, "FY2025Q2": 4.68, "FY2025Q3": 3.74, "FY2025Q4": 2.72, "FY2026Q1": 3.43}

## Validation

| Check | Status | Detail |
|---|---|---|
| net_sales: value present | PASS | final=46876.0 |
| net_sales: magnitude vs prior year | PASS | 46876.0 vs prior-year 45277.0 (ratio 1.04, band 0.7-1.42) |
| net_sales: analyst-sample agreement | PASS | cross-provider spread 584 (1.2% of final) |
| adj_eps: value present | PASS | final=4.7343 |
| adj_eps: magnitude vs prior year | PASS | 4.7343 vs prior-year 4.68 (ratio 1.01, band 0.55-1.7) |
| adj_eps: analyst-sample agreement | PASS | cross-provider spread 0.13 (2.7% of final) |
| comp_sales: value present | PASS | final=1.1333 |
| comp_sales: plausibility vs prior year | PASS | 1.1333pp vs prior-year 1.0pp (max delta 4.0pp) |
| comp_sales: analyst-sample agreement | PASS | cross-provider spread 0 (0.0% of final) |
| HD: net sales growth vs comp sales | PASS | sales growth 3.5pp vs comps 1.1pp (gap covers new stores/acquisitions/FX; limit 4pp) |
| red-team review | PASS | no objections (openai) |