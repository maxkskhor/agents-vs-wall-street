# Backtest report (time-travel evaluation)

Floor-relative miss = |forecast − actual| / scoring floor, capped at 5.0. 
It is the accuracy-prize score we would get if Wall Street were perfect — an upper bound on the real score.

| Company | Target | Metric | Actual | Stat | Guid | LLM | Best method | Floor-rel (best) |
|---|---|---|---:|---:|---:|---:|---|---:|
| HD | FY2026Q1 | net_sales | 4.176e+04 | 4.139e+04 | 4.125e+04 | 4.125e+04 | statistical | 1.80 |
| HD | FY2026Q1 | adj_eps | 3.43 | 3.488 | 3.631 | 3.63 | statistical | 3.37 |
| HD | FY2026Q1 | comp_sales | 0.6 | 1.7 | 1 | 1 | guidance | 0.80 |
| HD | FY2025Q4 | net_sales | 3.82e+04 | 4.254e+04 | 3.781e+04 | 3.781e+04 | guidance | 2.01 |
| HD | FY2025Q4 | adj_eps | 2.72 | 3.117 | 2.507 | 2.5 | guidance | 5.00 |
| HD | FY2025Q4 | comp_sales | 0.4 | 2.95 | 3.1 | 3.1 | statistical | 5.00 |
| HD | FY2025Q3 | net_sales | 4.135e+04 | 4.345e+04 | 3.968e+04 | 3.968e+04 | guidance | 5.00 |
| HD | FY2025Q3 | adj_eps | 3.74 | 3.75 | 3.668 | 3.67 | statistical | 0.52 |
| HD | FY2025Q3 | comp_sales | 0.2 | 0.85 | 1.65 | 1.3 | statistical | 1.30 |
| HD | FY2025Q2 | net_sales | 4.528e+04 | 4.665e+04 | 4.354e+04 | 4.438e+04 | llm_analyst | 3.95 |
| HD | FY2025Q2 | adj_eps | 4.68 | 4.623 | 4.591 | 4.58 | statistical | 2.45 |
| HD | FY2025Q2 | comp_sales | 1 | -1.55 | 1.433 | 1 | llm_analyst | 0.00 |
| HD | FY2025Q1 | net_sales | 3.986e+04 | 3.774e+04 | 3.744e+04 | 3.744e+04 | statistical | 5.00 |
| HD | FY2025Q1 | adj_eps | 3.56 | — | — | 4.58 | llm_analyst | 5.00 |
| HD | FY2025Q1 | comp_sales | -0.3 | -1.1 | 1 | 1 | statistical | 1.60 |
| HD | FY2024Q4 | net_sales | 3.97e+04 | — | — | 3.897e+04 | llm_analyst | 3.72 |
| HD | FY2024Q4 | adj_eps | 3.13 | — | — | 3.74 | llm_analyst | 5.00 |
| HD | FY2024Q4 | comp_sales | 0.8 | — | -2.6 | -2.5 | llm_analyst | 5.00 |
| HD | FY2024Q3 | net_sales | 4.022e+04 | — | — | 4.42e+04 | llm_analyst | 5.00 |
| HD | FY2024Q3 | adj_eps | 3.78 | — | — | 4.58 | llm_analyst | 5.00 |
| HD | FY2024Q3 | comp_sales | -1.3 | — | -3.95 | -3.8 | llm_analyst | 5.00 |
| HD | FY2024Q2 | net_sales | 4.318e+04 | — | — | 3.763e+04 | llm_analyst | 5.00 |
| HD | FY2024Q2 | comp_sales | -3.3 | — | -0.4 | -1 | llm_analyst | 4.60 |
| HD | FY2023Q4 | net_sales | 3.479e+04 | — | — | 3.479e+04 | llm_analyst | 0.00 |
| HD | FY2023Q4 | adj_eps | 2.86 | — | — | 3.85 | llm_analyst | 5.00 |
| ADI | FY2026Q2 | revenue | 3623 | 3306 | 3500 | 3500 | guidance | 5.00 |
| ADI | FY2026Q2 | adj_eps | 3.09 | 2.474 | 2.88 | 2.88 | guidance | 5.00 |
| ADI | FY2026Q2 | adj_gross_margin | 73 | 71.55 | — | 70.3 | statistical | 2.90 |
| ADI | FY2026Q1 | revenue | 3160 | 2991 | 3100 | 3100 | guidance | 3.80 |
| ADI | FY2026Q1 | adj_eps | 2.46 | 2.134 | 2.29 | 2.29 | guidance | 5.00 |
| ADI | FY2026Q1 | adj_gross_margin | 71.2 | 70.4 | — | 68.8 | statistical | 1.60 |
| ADI | FY2025Q4 | revenue | 3076 | 2672 | 3000 | 3000 | guidance | 4.95 |
| ADI | FY2025Q4 | adj_eps | 2.26 | 1.87 | 2.22 | 2.22 | guidance | 3.54 |
| ADI | FY2025Q4 | adj_gross_margin | 69.8 | 68.45 | — | 68.2 | statistical | 2.70 |
| ADI | FY2025Q3 | revenue | 2880 | 2155 | 2750 | 2750 | guidance | 5.00 |
| ADI | FY2025Q3 | adj_eps | 2.05 | 1.401 | 1.92 | 1.92 | llm_analyst | 5.00 |
| ADI | FY2025Q3 | adj_gross_margin | 69.2 | 66.65 | — | 69.2 | llm_analyst | 0.00 |
| ADI | FY2025Q2 | revenue | 2640 | 1782 | 2500 | 2500 | guidance | 5.00 |
| ADI | FY2025Q2 | adj_eps | 1.85 | 1.026 | 1.68 | 1.68 | guidance | 5.00 |
| ADI | FY2025Q2 | adj_gross_margin | 69.4 | 63.4 | — | 68.8 | llm_analyst | 1.20 |
| ADI | FY2025Q1 | revenue | 2423 | 1916 | 2350 | 2350 | guidance | 5.00 |
| ADI | FY2025Q1 | adj_eps | 1.63 | 1.093 | 1.53 | 1.53 | guidance | 5.00 |
| ADI | FY2025Q1 | adj_gross_margin | 68.8 | 64.55 | — | 67.1 | llm_analyst | 3.40 |
| ADI | FY2024Q4 | revenue | 2443 | 2071 | 2400 | 2400 | guidance | 3.54 |
| ADI | FY2024Q4 | adj_eps | 1.67 | 1.27 | 1.63 | 1.63 | llm_analyst | 4.00 |
| ADI | FY2024Q4 | adj_gross_margin | 67.9 | 65.75 | — | 67.4 | llm_analyst | 1.00 |
| ADI | FY2024Q3 | revenue | 2312 | 2476 | 2270 | 2270 | guidance | 3.65 |
| ADI | FY2024Q3 | adj_eps | 1.58 | 1.7 | 1.5 | 1.5 | guidance | 5.00 |
| ADI | FY2024Q3 | adj_gross_margin | 67.9 | 68 | — | 66.4 | statistical | 0.20 |
| ADI | FY2024Q2 | revenue | 2159 | 2729 | 2100 | 2100 | guidance | 5.00 |
| ADI | FY2024Q2 | adj_eps | 1.4 | — | 1.26 | 1.26 | guidance | 5.00 |
| ADI | FY2024Q2 | adj_gross_margin | 66.7 | — | — | 67.8 | llm_analyst | 2.20 |
| ADI | FY2024Q1 | revenue | 2513 | 2966 | 2500 | 2500 | guidance | 1.01 |
| ADI | FY2024Q1 | adj_eps | 1.73 | — | 1.7 | 1.7 | guidance | 3.00 |
| ADI | FY2024Q1 | adj_gross_margin | 69 | — | — | 69.2 | llm_analyst | 0.40 |
| HAS | FY2025 | net_fees | 972.4 | 1085 | 973.3 | 978.6 | guidance | 0.18 |
| HAS | FY2025 | preex_eps | 1.31 | 1.891 | — | 2.47 | statistical | 5.00 |
| HAS | FY2025 | preex_op | 45.6 | 56.07 | 45 | 45 | guidance | 2.63 |
| HAS | FY2024 | net_fees | 1114 | 1409 | 1117 | 1133 | guidance | 0.56 |
| HAS | FY2024 | preex_eps | 4.03 | 8.59 | — | 4.95 | llm_analyst | 5.00 |
| HAS | FY2024 | preex_op | 105.1 | 197 | 105 | 105 | guidance | 0.19 |
| DE | FY2026Q2 | net_sales_rev | 1.337e+04 | 1.293e+04 | — | 1.442e+04 | statistical | 5.00 |
| DE | FY2026Q2 | eps | 6.55 | 5.103 | — | 5.87 | llm_analyst | 5.00 |
| DE | FY2026Q2 | ppa_op | 706 | 522.6 | — | 472 | statistical | 5.00 |
| DE | FY2026Q1 | net_sales_rev | 9611 | 7451 | — | 8508 | llm_analyst | 5.00 |
| DE | FY2026Q1 | eps | 2.42 | 2.446 | — | 1.63 | statistical | 2.16 |
| DE | FY2026Q1 | ppa_op | 139 | — | — | 338 | llm_analyst | 5.00 |
| DE | FY2025Q4 | net_sales_rev | 1.239e+04 | 8696 | — | 1.082e+04 | llm_analyst | 5.00 |
| DE | FY2025Q4 | eps | 3.93 | 2.971 | — | 3.78 | llm_analyst | 5.00 |
| DE | FY2025Q3 | net_sales_rev | 1.202e+04 | 1.023e+04 | — | 1.02e+04 | statistical | 5.00 |
| DE | FY2025Q3 | eps | 4.75 | 3.672 | — | 4.12 | llm_analyst | 5.00 |
| DE | FY2025Q3 | ppa_op | 580 | 808.5 | — | 560 | llm_analyst | 5.00 |
| DE | FY2025Q2 | net_sales_rev | 1.276e+04 | 1.185e+04 | — | 1.064e+04 | statistical | 5.00 |
| DE | FY2025Q2 | eps | 6.64 | 4.979 | — | 5.49 | llm_analyst | 5.00 |
| DE | FY2025Q2 | ppa_op | 1148 | 922.5 | — | 1254 | llm_analyst | 5.00 |
| DE | FY2025Q1 | net_sales_rev | 8508 | 1.041e+04 | — | 1.172e+04 | statistical | 5.00 |
| DE | FY2025Q1 | eps | 3.19 | 4.674 | — | 5.91 | statistical | 5.00 |
| DE | FY2025Q1 | ppa_op | 338 | — | — | 1045 | llm_analyst | 5.00 |
| DE | FY2024Q4 | net_sales_rev | 1.114e+04 | — | — | 1.171e+04 | llm_analyst | 5.00 |
| DE | FY2024Q4 | eps | 4.55 | — | — | 4.05 | llm_analyst | 5.00 |
| DE | FY2024Q4 | ppa_op | 657 | — | — | 927 | llm_analyst | 5.00 |
| DE | FY2024Q3 | net_sales_rev | 1.315e+04 | — | — | 1.371e+04 | llm_analyst | 5.00 |
| DE | FY2024Q3 | eps | 6.29 | — | — | 8.03 | llm_analyst | 5.00 |
| DE | FY2024Q3 | ppa_op | 1162 | — | — | 1650 | llm_analyst | 5.00 |
| DE | FY2024Q2 | net_sales_rev | 1.524e+04 | — | — | 1.172e+04 | llm_analyst | 5.00 |
| DE | FY2024Q2 | eps | 8.53 | — | — | 6.23 | llm_analyst | 5.00 |

## Calibrated weights
```json
{
 "money": {
  "guidance": 0.9,
  "llm_analyst": 0.1,
  "statistical": 0.0,
  "backtest_score": 4.08,
  "n": 39
 },
 "eps": {
  "guidance": 0.6,
  "llm_analyst": 0.0,
  "statistical": 0.4,
  "backtest_score": 4.408,
  "n": 29
 },
 "percent": {
  "guidance": 0.0,
  "llm_analyst": 0.6,
  "statistical": 0.4,
  "backtest_score": 2.744,
  "n": 18
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
  "n": 8,
  "median_signed": -0.8667,
  "median_abs": 2.05,
  "p80_abs": 2.7,
  "pct_actual_above": 25,
  "correction_recommended": false,
  "reason": "only 40% of periods improved (need >=50%)",
  "walk_forward_tests": 5,
  "wf_raw_median_abs": 1.3,
  "wf_corrected_median_abs": 1.1083,
  "pct_periods_improved": 40
 },
 "ADI/revenue": {
  "n": 10,
  "median_signed": 0.0267,
  "median_abs": 0.0267,
  "p80_abs": 0.0353,
  "pct_actual_above": 100,
  "correction_recommended": true,
  "reason": "walk-forward median error 76.117 -> 30.1733, 100% of periods improved",
  "walk_forward_tests": 7,
  "wf_raw_median_abs": 76.117,
  "wf_corrected_median_abs": 30.1733,
  "pct_periods_improved": 100,
  "bias_estimate": 0.026743071428571512
 },
 "ADI/adj_eps": {
  "n": 10,
  "median_signed": 0.0665,
  "median_abs": 0.0665,
  "p80_abs": 0.0742,
  "pct_actual_above": 100,
  "correction_recommended": true,
  "reason": "walk-forward median error 0.13 -> 0.0404, 71% of periods improved",
  "walk_forward_tests": 7,
  "wf_raw_median_abs": 0.13,
  "wf_corrected_median_abs": 0.0404,
  "pct_periods_improved": 71,
  "bias_estimate": 0.06
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