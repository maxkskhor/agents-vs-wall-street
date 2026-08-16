# Backtest report (time-travel evaluation)

Floor-relative miss = |forecast − actual| / scoring floor, capped at 5.0. 
It is the accuracy-prize score we would get if Wall Street were perfect — an upper bound on the real score.

| Company | Target | Metric | Actual | Stat | Guid | LLM | Best method | Floor-rel (best) |
|---|---|---|---:|---:|---:|---:|---|---:|
| HD | FY2026Q1 | net_sales | 4.176e+04 | 4.139e+04 | 4.125e+04 | 4.125e+04 | statistical | 1.80 |
| HD | FY2026Q1 | adj_eps | 3.43 | 3.488 | 3.631 | 3.62 | statistical | 3.37 |
| HD | FY2026Q1 | comp_sales | 0.6 | 1.7 | 1 | 1.4 | guidance | 0.80 |
| HD | FY2025Q4 | net_sales | 3.82e+04 | 4.254e+04 | 3.781e+04 | 4.085e+04 | guidance | 2.01 |
| HD | FY2025Q4 | adj_eps | 2.72 | 3.117 | 2.507 | 2.93 | llm_analyst | 5.00 |
| HD | FY2025Q4 | comp_sales | 0.4 | 2.8 | 3.1 | 1.1 | llm_analyst | 1.40 |
| HD | FY2025Q3 | net_sales | 4.135e+04 | 4.345e+04 | 3.968e+04 | 4.207e+04 | llm_analyst | 3.46 |
| HD | FY2025Q3 | adj_eps | 3.74 | 3.75 | 3.668 | 3.68 | statistical | 0.52 |
| HD | FY2025Q3 | comp_sales | 0.2 | 0.8 | 1.65 | 1.3 | statistical | 1.20 |
| HD | FY2025Q2 | net_sales | 4.528e+04 | 4.665e+04 | 4.354e+04 | 4.406e+04 | llm_analyst | 5.00 |
| HD | FY2025Q2 | adj_eps | 4.68 | 4.623 | 4.591 | 4.58 | statistical | 2.45 |
| HD | FY2025Q2 | comp_sales | 1 | -1.6 | 1.433 | 0.9 | llm_analyst | 0.20 |
| ADI | FY2026Q2 | revenue | 3623 | 3306 | 3500 | 3500 | guidance | 5.00 |
| ADI | FY2026Q2 | adj_eps | 3.09 | 2.474 | 2.88 | 2.93 | llm_analyst | 5.00 |
| ADI | FY2026Q2 | adj_gross_margin | 73 | 71.55 | — | 70.9 | statistical | 2.90 |
| ADI | FY2026Q1 | revenue | 3160 | 2991 | — | 2553 | statistical | 5.00 |
| ADI | FY2026Q1 | adj_eps | 2.46 | 2.134 | 2.29 | 2.24 | guidance | 5.00 |
| ADI | FY2026Q1 | adj_gross_margin | 71.2 | 70.4 | — | 69.3 | statistical | 1.60 |
| ADI | FY2025Q4 | revenue | 3076 | 2672 | 3000 | 3000 | guidance | 4.95 |
| ADI | FY2025Q4 | adj_eps | 2.26 | 1.87 | 2.22 | 2.2 | guidance | 3.54 |
| ADI | FY2025Q4 | adj_gross_margin | 69.8 | 68.45 | — | 69.3 | llm_analyst | 1.00 |
| ADI | FY2025Q3 | revenue | 2880 | 2155 | 2750 | 2750 | guidance | 5.00 |
| ADI | FY2025Q3 | adj_eps | 2.05 | 1.401 | 1.92 | 1.92 | llm_analyst | 5.00 |
| ADI | FY2025Q3 | adj_gross_margin | 69.2 | 66.65 | — | 69.2 | llm_analyst | 0.00 |
| HAS | FY2025 | net_fees | 972.4 | 1085 | 973.3 | 998.6 | guidance | 0.18 |
| HAS | FY2025 | preex_eps | 1.31 | 1.891 | — | 2.03 | statistical | 5.00 |
| HAS | FY2025 | preex_op | 45.6 | 56.07 | 45 | 35 | guidance | 2.63 |
| HAS | FY2024 | net_fees | 1114 | 1409 | 1117 | 1104 | guidance | 0.56 |
| HAS | FY2024 | preex_eps | 4.03 | 8.59 | — | 6.59 | llm_analyst | 5.00 |
| HAS | FY2024 | preex_op | 105.1 | 197 | 105 | 100.1 | guidance | 0.19 |
| DE | FY2026Q2 | net_sales_rev | 1.337e+04 | 1.293e+04 | — | 1.221e+04 | statistical | 5.00 |
| DE | FY2026Q2 | eps | 6.55 | 5.103 | — | 4.29 | statistical | 5.00 |
| DE | FY2026Q1 | net_sales_rev | 9611 | 7451 | — | 7858 | llm_analyst | 5.00 |
| DE | FY2026Q1 | eps | 2.42 | 2.446 | — | 3.39 | statistical | 2.16 |
| DE | FY2026Q1 | ppa_op | 139 | — | — | 1156 | llm_analyst | 5.00 |
| DE | FY2025Q4 | net_sales_rev | 1.239e+04 | 8696 | — | 1.064e+04 | llm_analyst | 5.00 |
| DE | FY2025Q4 | eps | 3.93 | 2.971 | — | 4 | llm_analyst | 3.56 |
| DE | FY2025Q3 | net_sales_rev | 1.202e+04 | 1.023e+04 | — | 1.185e+04 | llm_analyst | 2.76 |
| DE | FY2025Q3 | eps | 4.75 | 3.672 | — | 4.79 | llm_analyst | 1.68 |
| DE | FY2025Q3 | ppa_op | 580 | 820.6 | — | 972 | statistical | 5.00 |

## Calibrated weights
```json
{
 "money": {
  "guidance": 0.5,
  "llm_analyst": 0.3,
  "statistical": 0.2,
  "backtest_score": 3.653,
  "n": 18
 },
 "eps": {
  "guidance": 0.0,
  "llm_analyst": 0.0,
  "statistical": 1.0,
  "backtest_score": 4.179,
  "n": 14
 },
 "percent": {
  "guidance": 0.0,
  "llm_analyst": 0.6,
  "statistical": 0.4,
  "backtest_score": 1.8,
  "n": 8
 }
}
```

## Guidance bias (actual vs guidance-anchored, signed)
```json
{
 "HD/net_sales": {
  "mean_signed": 0.0253,
  "n": 4
 },
 "HD/adj_eps": {
  "mean_signed": 0.0144,
  "n": 4
 },
 "HD/comp_sales": {
  "mean_signed": -1.2458,
  "n": 4
 },
 "ADI/revenue": {
  "mean_signed": 0.0347,
  "n": 3
 },
 "ADI/adj_eps": {
  "mean_signed": 0.0545,
  "n": 4
 },
 "HAS/net_fees": {
  "mean_signed": -0.0019,
  "n": 2
 },
 "HAS/preex_op": {
  "mean_signed": 0.0071,
  "n": 2
 }
}
```

Caveat: LLM-analyst rows for pre-2026 quarters may be contaminated by model training data; deterministic estimator rows are not.