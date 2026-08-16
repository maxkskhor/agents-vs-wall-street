# Backtest report (time-travel evaluation)

Floor-relative miss = |forecast − actual| / scoring floor, capped at 5.0. 
It is the accuracy-prize score we would get if Wall Street were perfect — an upper bound on the real score.

| Company | Target | Metric | Actual | Stat | Guid | LLM | Best method | Floor-rel (best) |
|---|---|---|---:|---:|---:|---:|---|---:|
| HD | FY2026Q1 | net_sales | 4.176e+04 | 4.139e+04 | 4.125e+04 | 4.225e+04 | statistical | 1.80 |
| HD | FY2026Q1 | adj_eps | 3.43 | 3.488 | 3.631 | 3.682 | statistical | 3.37 |
| HD | FY2026Q1 | comp_sales | 0.6 | 1.7 | 1 | -0.246 | guidance | 0.80 |
| HD | FY2025Q4 | net_sales | 3.82e+04 | 4.254e+04 | 3.781e+04 | 3.876e+04 | guidance | 2.01 |
| HD | FY2025Q4 | adj_eps | 2.72 | 3.117 | 2.507 | 2.512 | llm_analyst | 5.00 |
| HD | FY2025Q4 | comp_sales | 0.4 | 2.8 | 3.1 | 2.154 | llm_analyst | 3.51 |
| HD | FY2025Q3 | net_sales | 4.135e+04 | 4.345e+04 | 3.968e+04 | 4.238e+04 | llm_analyst | 4.96 |
| HD | FY2025Q3 | adj_eps | 3.74 | 3.75 | 3.668 | 3.71 | statistical | 0.52 |
| HD | FY2025Q3 | comp_sales | 0.2 | 0.8 | 1.65 | 0.254 | llm_analyst | 0.11 |
| HD | FY2025Q2 | net_sales | 4.528e+04 | 4.665e+04 | 4.354e+04 | 4.549e+04 | llm_analyst | 0.96 |
| HD | FY2025Q2 | adj_eps | 4.68 | 4.623 | 4.591 | 4.591 | statistical | 2.45 |
| HD | FY2025Q2 | comp_sales | 1 | -1.6 | 1.433 | -0.246 | guidance | 0.87 |
| HD | FY2025Q1 | net_sales | 3.986e+04 | 3.774e+04 | 3.744e+04 | 3.835e+04 | llm_analyst | 5.00 |
| HD | FY2025Q1 | adj_eps | 3.56 | — | — | 4.591 | llm_analyst | 5.00 |
| HD | FY2025Q1 | comp_sales | -0.3 | -2.6 | 1 | -0.246 | llm_analyst | 0.11 |
| HD | FY2024Q4 | net_sales | 3.97e+04 | — | — | 3.994e+04 | llm_analyst | 1.19 |
| HD | FY2024Q4 | adj_eps | 3.13 | — | — | 3.795 | llm_analyst | 5.00 |
| HD | FY2024Q4 | comp_sales | 0.8 | — | -2.5 | -3.746 | guidance | 5.00 |
| ADI | FY2026Q2 | revenue | 3623 | 3306 | 3500 | 3622 | llm_analyst | 0.05 |
| ADI | FY2026Q2 | adj_eps | 3.09 | 2.474 | 2.88 | 3.035 | llm_analyst | 3.53 |
| ADI | FY2026Q2 | adj_gross_margin | 73 | 71.55 | — | 71.2 | statistical | 2.90 |
| ADI | FY2026Q1 | revenue | 3160 | 2991 | — | 2508 | statistical | 5.00 |
| ADI | FY2026Q1 | adj_eps | 2.46 | 2.134 | 2.29 | 2.41 | llm_analyst | 4.07 |
| ADI | FY2026Q1 | adj_gross_margin | 71.2 | 70.4 | — | 69.9 | statistical | 1.60 |
| ADI | FY2025Q4 | revenue | 3076 | 2672 | 3000 | 3105 | llm_analyst | 1.88 |
| ADI | FY2025Q4 | adj_eps | 2.26 | 1.87 | 2.22 | 2.34 | guidance | 3.54 |
| ADI | FY2025Q4 | adj_gross_margin | 69.8 | 68.45 | — | 68.9 | llm_analyst | 1.80 |
| ADI | FY2025Q3 | revenue | 2880 | 2155 | 2750 | 2846 | llm_analyst | 2.37 |
| ADI | FY2025Q3 | adj_eps | 2.05 | 1.401 | 1.92 | 2.02 | llm_analyst | 2.93 |
| ADI | FY2025Q3 | adj_gross_margin | 69.2 | 66.65 | — | 69.4 | llm_analyst | 0.40 |
| ADI | FY2025Q2 | revenue | 2640 | 1782 | 2500 | 2588 | llm_analyst | 3.98 |
| ADI | FY2025Q2 | adj_eps | 1.85 | 1.026 | 1.68 | 1.77 | llm_analyst | 5.00 |
| ADI | FY2025Q2 | adj_gross_margin | 69.4 | 63.4 | — | 67.8 | llm_analyst | 3.20 |
| ADI | FY2025Q1 | revenue | 2423 | 1916 | 2350 | 2432 | llm_analyst | 0.75 |
| ADI | FY2025Q1 | adj_eps | 1.63 | 1.093 | 1.53 | 1.584 | llm_analyst | 4.60 |
| ADI | FY2025Q1 | adj_gross_margin | 68.8 | 64.55 | — | 69 | llm_analyst | 0.40 |
| HAS | FY2025 | net_fees | 972.4 | 1085 | 973.3 | 978.6 | guidance | 0.18 |
| HAS | FY2025 | preex_eps | 1.31 | 1.891 | — | 2.47 | statistical | 5.00 |
| HAS | FY2025 | preex_op | 45.6 | 56.07 | 45 | 45 | guidance | 2.63 |
| HAS | FY2024 | net_fees | 1114 | 1409 | 1117 | 1133 | guidance | 0.56 |
| HAS | FY2024 | preex_eps | 4.03 | 8.59 | — | 6.85 | llm_analyst | 5.00 |
| HAS | FY2024 | preex_op | 105.1 | 197 | 105 | 105 | guidance | 0.19 |
| DE | FY2026Q2 | net_sales_rev | 1.337e+04 | 1.293e+04 | — | 1.442e+04 | statistical | 5.00 |
| DE | FY2026Q2 | eps | 6.55 | 5.103 | — | 5.1 | statistical | 5.00 |
| DE | FY2026Q2 | ppa_op | 706 | — | — | 381 | llm_analyst | 5.00 |
| DE | FY2026Q1 | net_sales_rev | 9611 | 7451 | — | 7515 | llm_analyst | 5.00 |
| DE | FY2026Q1 | eps | 2.42 | 2.446 | — | 3.56 | statistical | 2.16 |
| DE | FY2026Q1 | ppa_op | 139 | — | — | 560.7 | llm_analyst | 5.00 |
| DE | FY2025Q4 | net_sales_rev | 1.239e+04 | 8696 | — | 1.018e+04 | llm_analyst | 5.00 |
| DE | FY2025Q4 | eps | 3.93 | 2.971 | — | 3.01 | llm_analyst | 5.00 |
| DE | FY2025Q3 | net_sales_rev | 1.202e+04 | 1.023e+04 | — | 1.02e+04 | statistical | 5.00 |
| DE | FY2025Q3 | eps | 4.75 | 3.672 | — | 4.19 | llm_analyst | 5.00 |
| DE | FY2025Q3 | ppa_op | 580 | 820.6 | — | 819.3 | llm_analyst | 5.00 |
| DE | FY2025Q2 | net_sales_rev | 1.276e+04 | 1.185e+04 | — | 1.063e+04 | statistical | 5.00 |
| DE | FY2025Q2 | eps | 6.64 | 4.979 | — | 5.49 | llm_analyst | 5.00 |
| DE | FY2025Q2 | ppa_op | 1148 | 1165 | — | 1250 | statistical | 3.01 |
| DE | FY2025Q1 | net_sales_rev | 8508 | 1.041e+04 | — | 1.172e+04 | statistical | 5.00 |
| DE | FY2025Q1 | eps | 3.19 | 4.674 | — | 5.91 | statistical | 5.00 |
| DE | FY2025Q1 | ppa_op | 338 | — | — | 1045 | llm_analyst | 5.00 |

## Calibrated weights
```json
{
 "money": {
  "guidance": 0.0,
  "llm_analyst": 0.6,
  "statistical": 0.4,
  "backtest_score": 3.479,
  "n": 27
 },
 "eps": {
  "guidance": 0.0,
  "llm_analyst": 0.0,
  "statistical": 1.0,
  "backtest_score": 4.425,
  "n": 20
 },
 "percent": {
  "guidance": 0.0,
  "llm_analyst": 0.6,
  "statistical": 0.4,
  "backtest_score": 2.076,
  "n": 12
 }
}
```

## Guidance bias (actual vs guidance-anchored, signed)
```json
{
 "HD/net_sales": {
  "n": 5,
  "median_signed": 0.04,
  "median_abs": 0.04,
  "p80_abs": 0.0422,
  "pct_actual_above": 100,
  "correction_recommended": false,
  "reason": "insufficient walk-forward evidence (2 tests, need 3)",
  "walk_forward_tests": 2,
  "wf_raw_median_abs": 448.81,
  "wf_corrected_median_abs": 1197.407,
  "pct_periods_improved": 0
 },
 "HD/adj_eps": {
  "n": 4,
  "median_signed": 0.0195,
  "median_abs": 0.0375,
  "p80_abs": 0.0554,
  "pct_actual_above": 75,
  "correction_recommended": false,
  "reason": "insufficient walk-forward evidence (1 tests, need 3)",
  "walk_forward_tests": 1,
  "wf_raw_median_abs": 0.2012,
  "wf_corrected_median_abs": 0.2726,
  "pct_periods_improved": 0
 },
 "HD/comp_sales": {
  "n": 6,
  "median_signed": -0.8667,
  "median_abs": 1.375,
  "p80_abs": 2.7,
  "pct_actual_above": 17,
  "correction_recommended": true,
  "reason": "walk-forward median error 1.45 -> 1.0167, 67% of periods improved",
  "walk_forward_tests": 3,
  "wf_raw_median_abs": 1.45,
  "wf_corrected_median_abs": 1.0167,
  "pct_periods_improved": 67,
  "mean_signed": -0.8666666666666667
 },
 "ADI/revenue": {
  "n": 5,
  "median_signed": 0.0353,
  "median_abs": 0.0353,
  "p80_abs": 0.0474,
  "pct_actual_above": 100,
  "correction_recommended": false,
  "reason": "insufficient walk-forward evidence (2 tests, need 3)",
  "walk_forward_tests": 2,
  "wf_raw_median_abs": 99.791,
  "wf_corrected_median_abs": 40.0279,
  "pct_periods_improved": 100
 },
 "ADI/adj_eps": {
  "n": 6,
  "median_signed": 0.0703,
  "median_abs": 0.0703,
  "p80_abs": 0.0742,
  "pct_actual_above": 100,
  "correction_recommended": true,
  "reason": "walk-forward median error 0.17 -> 0.0372, 67% of periods improved",
  "walk_forward_tests": 3,
  "wf_raw_median_abs": 0.17,
  "wf_corrected_median_abs": 0.0372,
  "pct_periods_improved": 67,
  "mean_signed": 0.06
 },
 "HAS/net_fees": {
  "n": 2,
  "median_signed": -0.0019,
  "median_abs": 0.0019,
  "p80_abs": 0.0009,
  "pct_actual_above": 0,
  "correction_recommended": false,
  "reason": "insufficient walk-forward evidence (0 tests, need 3)",
  "walk_forward_tests": 0
 },
 "HAS/preex_op": {
  "n": 2,
  "median_signed": 0.0071,
  "median_abs": 0.0071,
  "p80_abs": 0.001,
  "pct_actual_above": 100,
  "correction_recommended": false,
  "reason": "insufficient walk-forward evidence (0 tests, need 3)",
  "walk_forward_tests": 0
 }
}
```

Caveat: LLM-analyst rows for pre-2026 quarters may be contaminated by model training data; deterministic estimator rows are not.