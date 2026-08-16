# Hays plc — FY2026 forecast audit trail

| Metric | Units | Final forecast |
|---|---|---:|
| Net fees | GBPm | **893.0** |
| Pre-exceptional basic EPS | GBp | **1.0053** |
| Pre-exceptional operating profit | GBPm | **42.0** |


## Net fees (GBPm) = 893.0

- **Final** = consensus + 0.85 x (ensemble - consensus) = 902.4 + 0.85 × (891.4 − 902.4) = 893
- **Ensemble** = weighted mean of method values = 891.4 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 903.5
- sample [openai#0] base 972.4 (FY2025) → 903.5
    - -42.7 — Replace FY2025H1 with reported FY2026H1 net fees. [FY2025H1 net fees were GBP496.0m versus FY2026H1 net fees of GBP453.3m.]
    - -16.7 — Apply the reported Q3 actual-basis decline to an equal-share estimate of FY2025H2 fees. [FY2026Q3 Group net fees decreased by 7% on an actual basis; FY2025H2 was GBP476.4m, with Q3 assumed ]
    - -9.5 — Apply the reported Q4 actual-basis decline to an equal-share estimate of FY2025H2 fees. [FY2026Q4 Group net fees decreased by 4% on an actual basis; FY2025H2 was GBP476.4m, with Q4 assumed ]
- sample [openai#1] base 972.4 (FY2025) → 908.3
    - -42.7 — Replace FY2025H1 with reported FY2026H1 net fees, which were GBP42.7m lower. [FY2025H1 net fees of GBP496.0m versus FY2026H1 net fees of GBP453.3m; FY2026Q1 and Q2 like-for-like ]
    - -21.4 — Apply an approximately 5.5% decline to the FY2025H2 base, reflecting the reported FY2026Q3 and Q4 actual-basis declines of 7% and 4%. [FY2025H2 is GBP476.4m, derived from FY2025 GBP972.4m less FY2025H1 GBP496.0m; FY2026Q3 actual net fe]
- sample [openai#2] base 972.4 (FY2025) → 903.5
    - -42.7 — Reflects the reported FY2026H1 shortfall versus FY2025H1. [FY2026H1 net fees were GBP453.3m versus GBP496.0m in FY2025H1.]
    - -26.2 — Applies an approximately 5.5% decline to FY2025H2, based on the average of the reported FY2026Q3 and Q4 actual-basis declines. [FY2026Q3 total net fees decreased 7% on an actual basis and FY2026Q4 decreased 4% on an actual basis]
- sample [openai#3] base 972.4 (FY2025) → 898.8
    - -42.7 — Replace FY2025H1 with FY2026H1 actual net fees, reducing the comparable half-year by GBP42.7m. [FY2026H1 net fees were GBP453.3m versus FY2025H1 GBP496.0m.]
    - -30.9 — Apply the reported Q3 and Q4 like-for-like declines to the FY2025H2 run-rate, implying an approximately 6.5% H2 reduction. [FY2026Q3 group net fees decreased 8% YoY like-for-like; FY2026Q4 decreased 5% YoY like-for-like; FY2]
- sample [openai#4] base 972.4 (FY2025) → 898.7
    - -42.7 — Reflects the reported FY2026H1 net-fee decline versus FY2025H1. [FY2026H1 net fees of GBP453.3m versus FY2025H1 GBP496.0m.]
    - -31.0 — Applies an approximately 6.5% decline to FY2025H2, based on the reported Q3 and Q4 FY2026 like-for-like declines of 8% and 5%, respectively. [FY2025H2 is GBP476.4m (FY2025 GBP972.4m less FY2025H1 GBP496.0m); FY2026Q3 net fees decreased 8% YoY]

### statistical → 842.8
- formula: prior-year value 972.4 x (1 + median YoY growth -13.330%)

### guidance → 903.5
- formula: reported H1 453.3 + prior-year H2 476.4 x (1 + pre-announced H2 growth -5.5%)
- evidence (2026-07-10__has-ln-20260710-q4-8k__1572805.md): “On an actual basis, net fees decreased by 4% due to a weakening of sterling versus the Euro and Australian Dollar partially offset by our previously communicated action to close our operations in four countries and divest in the Czech Republic, Denmark, Hungary, Luxembourg, Roman”

- reported history used: {"FY2023": 1294.6, "FY2024": 1113.6, "FY2024H1": 583.3, "FY2025": 972.4, "FY2025H1": 496.0, "FY2026H1": 453.3}

## Pre-exceptional operating profit (GBPm) = 42.0

- **Final** = consensus + 0.85 x (ensemble - consensus) = 45.3 + 0.85 × (41.21 − 45.3) = 41.82
- **Ensemble** = weighted mean of method values = 41.21 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 46
- sample [openai#0] base 45.6 (FY2025) → 46
    - +0.4 — Lift to the top of the current consensus range, reflecting management's stated expectation. [Q4 FY2026 trading update, 10 July 2026: FY2026 pre-exceptional operating profit expected at the top ]
- sample [openai#1] base 45.6 (FY2025) → 46
    - +0.4 — Move to the top end of the latest company-compiled consensus range, reflecting management's current expectation. [Q4 FY2026 trading update: management expects FY26 pre-exceptional operating profit at the top of the]
- sample [openai#2] base 45.6 (FY2025) → 46
    - +0.4 — Raise the FY2025 base to the top of the current FY2026 consensus range, consistent with company guidance. [Q4 FY2026 trading update, 10 July 2026: FY2026 pre-exceptional operating profit expected at the top ]
- sample [openai#3] base 45.6 (FY2025) → 46
    - +0.4 — Move to the top of the current FY2026 consensus range, consistent with management's latest expectation. [Q4 FY2026 trading update dated 10 July 2026: management expects FY2026 pre-exceptional operating pro]
- sample [openai#4] base 20.1 (FY2026H1) → 46
    - +25.9 — Adds the implied H2 contribution required to reach the top end of management's FY2026 guidance range. [Q4 FY2026 trading update dated 10 July 2026: FY2026 pre-exceptional operating profit expected at the]

### statistical → 22.06
- formula: prior-year value 45.6 x (1 + median YoY growth -51.631%)

### guidance → 46
- formula: midpoint of stated guidance = 46.0
- evidence (2026-07-10__has-ln-20260710-q4-8k__1572805.md): “Our actions to deliver strong consultant net fee productivity growth and cost discipline continued to offset our lower net fees in H2 26 and we currently expect FY26 pre-exceptional operating profit will be at the top of the £37.0-46.0m consensus range (2)”

- reported history used: {"FY2023": 197.0, "FY2024": 105.1, "FY2024H1": 60.1, "FY2025": 45.6, "FY2025H1": 25.5, "FY2026H1": 20.1}

## Pre-exceptional basic EPS (GBp) = 1.0053

- **Final** = consensus + 0.5 x (ensemble - consensus) = 1.13 + 0.5 × (0.8807 − 1.13) = 1.005
- **Ensemble** = weighted mean of method values = 0.8807 (weights {'derived': 0.6, 'guidance': 0.5, 'llm_analyst': 0.3, 'statistical': 0.2})

### llm_analyst → 0.96
- sample [openai#0] base 0.46 (FY2026H1) → 0.96
    - +0.5 — Adds an H2 contribution using the latest comparable full-year H2 EPS contribution as a proxy. [FY2025 H2 contribution was 0.50 GBp, calculated as FY2025 EPS of 1.31 less FY2025H1 EPS of 0.81.]
- sample [openai#1] base 1.31 (FY2025) → 0.96
    - -0.35 — Reduce for the year-on-year decline already evident in first-half EPS. [FY2026H1 EPS was 0.46 GBp versus 0.81 GBp in FY2025H1, a decline of 0.35 GBp.]
- sample [openai#2] base 1.31 (FY2025) → 0.96
    - -0.35 — Reflects the year-on-year decline in first-half EPS, assuming the second-half contribution is unchanged from the prior year. [FY2025H1 EPS of 0.81 GBp versus FY2026H1 EPS of 0.46 GBp.]
- sample [openai#3] base 0.46 (FY2026H1) → 0.74
    - +0.28 — Adds an estimated FY2026H2 contribution using FY2025's observed H2-to-H1 EPS seasonality. [FY2025 H2 EPS was 0.50 GBp, calculated as FY2025 1.31 less FY2025H1 0.81; applying the resulting 0.6]
- sample [openai#4] base 1.31 (FY2025) → 0.96
    - -0.35 — Replace FY2025 first-half EPS with FY2026 first-half EPS while assuming the second-half contribution is unchanged. [FY2025H1 EPS was 0.81 GBp versus FY2026H1 EPS of 0.46 GBp.]
- sample [openai#5] base 0.46 (FY2026H1) → 0.96
    - +0.5 — Add an H2 contribution in line with the prior-year second-half EPS contribution. [FY2025 full-year EPS of 1.31 GBp less FY2025H1 EPS of 0.81 GBp implies FY2025H2 EPS of 0.50 GBp.]
- sample [openai#6] base 1.31 (FY2025) → 0.61
    - -0.7 — Annualise the FY2026H1 year-on-year EPS shortfall across the full year. [FY2026H1 EPS was 0.46 GBp versus FY2025H1 EPS of 0.81 GBp, a 0.35 GBp decline; twice this decline im]
- sample [openai#7] base 1.31 (FY2025) → 0.96
    - -0.35 — Reflect the weaker first-half performance year on year, assuming the second-half contribution is unchanged from FY2025. [FY2026H1 EPS of 0.46 GBp versus FY2025H1 EPS of 0.81 GBp, a decline of 0.35 GBp.]

### derived → 0.9612
- formula: forecast preex_op 42.0 x most-recent preex_eps/preex_op ratio 0.02289 (from FY2026H1: 0.46 / 20.1)

### statistical → 0.5202
- formula: prior-year value 1.31 x (1 + median YoY growth -60.289%)

- reported history used: {"FY2023": 8.59, "FY2024": 4.03, "FY2024H1": 2.37, "FY2025": 1.31, "FY2025H1": 0.81, "FY2026H1": 0.46}

## Validation

| Check | Status | Detail |
|---|---|---|
| net_fees: value present | PASS | final=893.0 |
| net_fees: magnitude vs prior year | PASS | 893.0 vs prior-year 972.4 (ratio 0.92, band 0.7-1.42) |
| net_fees: analyst-sample agreement | PASS | cross-provider spread 9.6 (1.1% of final) |
| preex_eps: value present | PASS | final=1.0053 |
| preex_eps: magnitude vs prior year | PASS | 1.0053 vs prior-year 1.31 (ratio 0.77, band 0.55-1.7) |
| preex_eps: analyst-sample agreement | WARN | cross-provider spread 0.35 (34.8% of final) |
| preex_op: value present | PASS | final=42.0 |
| preex_op: magnitude vs prior year | PASS | 42.0 vs prior-year 45.6 (ratio 0.92, band 0.4-2.0) |
| preex_op: analyst-sample agreement | PASS | cross-provider spread 0 (0.0% of final) |
| HAS: preex_op/net_fees conversion ratio | PASS | ratio 0.047, history-derived band 0.035-0.190 |
| red-team review | PASS | no objections (openai) |