# Bias Model Handoff

## Purpose

Build a generic, evidence-backed bias-testing layer using the frozen offline corpus across all four companies.

The model should answer:

1. Does management systematically guide conservatively or optimistically?
2. Does our agent systematically overestimate or underestimate specific metrics?
3. What is the normal error margin for each company, metric and source?
4. Does a historical correction improve forecasts in leakage-safe backtesting?

This is a calibration and validation layer, not a replacement for the underlying forecasting process.

## Agreed scope

### MVP

- Management guidance versus subsequent reported actuals
- Agent-generated historical forecasts versus subsequent actuals
- Directional bias and forecast-error distributions
- Initial, reaffirmed, updated and final guidance vintages
- Metric-definition and contamination controls
- Recency weighting
- Walk-forward validation
- A recommendation to apply or withhold correction

### Not part of the MVP

- Claims about historical Wall Street-consensus bias
- Automated sentiment-driven forecast changes
- DCF or valuation modelling
- Bespoke calculations for individual companies
- Pooling incompatible metrics to increase sample size

Current public consensus can remain a separate pre-event sanity check when its date and metric definition are verifiable. The offline corpus is not assumed to contain a complete point-in-time history of Wall Street consensus.

## Why the offline corpus is sufficient

The corpus can support historical management guidance, subsequent actuals, guidance revisions, metric definitions, contamination events and leakage-controlled historical simulations of the agent.

It therefore supports management-guidance bias and internal-model bias. It should not be presented as complete analyst-consensus backtesting unless dated consensus observations are independently available.

## Evidence repository

Create one structured observation per:

```text
company × metric × reporting period × source × forecast vintage
```

Required fields:

```text
company
reporting_period
forecast_cutoff
metric
units
metric_type
definition_tag
source_type
guidance_vintage
estimate_low
estimate_high
estimate_midpoint
estimate_date
actual_value
actual_report_date
estimate_source_path
actual_source_path
contamination_flag
contamination_reason
verification_status
```

MVP source types:

```text
management_guidance
agent_forecast
```

Metric types:

```text
currency
per_share
percentage_point
```

Definition tags must distinguish GAAP/adjusted, quarterly/annual, total-company/geography, consolidated/segment, reported/pre-exceptional and original/redefined segments.

Examples:

```text
adjusted-diluted-eps-quarterly
gaap-diluted-eps-quarterly
total-company-comparable-sales-quarterly
us-comparable-sales-quarterly
pre-exceptional-operating-profit-annual
```

## Source hierarchy

Use offline documents in this order:

1. Official earnings releases and regulatory filings
2. Official investor presentations
3. Earnings-call management presentations
4. Earnings-call Q&A

Search results are leads, not evidence. Every numeric estimate and actual must link to its source document and publication date.

## Leakage prevention

For every simulated historical forecast:

```text
document publication date < simulated forecast cutoff
```

The agent must not access the target period's earnings release, filing, earnings call, later commentary revealing the result, or retrospective documents containing the actual.

Each run must log its cutoff and included/excluded evidence. Bias calculations for a historical test period may use only actuals reported before that period's estimate date.

## Backtest routes

### 1. Management-guidance bias

For each historical period, compare the latest eligible management guidance with the subsequent actual.

For numeric ranges:

```text
guidance midpoint = (low + high) / 2
range width = high - low
```

Retain low, high, midpoint and range width. Do not convert qualitative statements into invented numeric guidance.

### 2. Agent walk-forward bias

For each historical target period:

1. Set a pre-results forecast cutoff.
2. Restrict the corpus to information available before the cutoff.
3. Run the current forecasting method.
4. Save its forecast, assumptions and evidence.
5. Compare it with the subsequently reported actual.
6. Move chronologically to the next period.

This measures the bias of the complete forecasting process rather than only management guidance.

## Error definitions

### Currency and per-share metrics

```text
signed error = (actual - estimate) / |estimate|
absolute error = |signed error|
```

- Positive signed error: estimate was too low
- Negative signed error: estimate was too high

### Percentage metrics

Use percentage-point error:

```text
signed error = actual - estimate
absolute error = |actual - estimate|
```

Do not use relative percentage error for metrics near zero, such as comparable sales.

## Required diagnostics

Calculate independently for each compatible group:

```text
company × metric × definition × source type × guidance vintage
```

Report:

- Sample size
- Median signed error
- Recency-weighted median signed error
- Median absolute error
- 80th-percentile absolute error
- RMSE
- Percentage of estimates below actual
- Percentage of estimates above actual
- Raw versus corrected walk-forward error
- Percentage of walk-forward periods improved

Use medians as the primary measures because unusual quarters can distort averages.

## Recency weighting

Use a transparent decay function so recent comparable periods matter more. Select and document the half-life through backtesting. Do not use recency weighting to pool incompatible observations.

## Bias correction

For currency and per-share metrics:

```text
adjusted forecast = raw forecast × (1 + validated bias)
```

For percentage metrics:

```text
adjusted forecast = raw forecast + validated bias
```

Always retain and display the raw forecast.

### Correction gate

Recommend applying a correction only when:

- At least five clean comparable observations exist
- Corrected walk-forward error is lower than raw error
- At least 50% of tested periods improve
- Metric definitions are consistent
- No material structural break invalidates the history

Otherwise return:

```text
correction recommended: no
reason: insufficient or unstable evidence
```

Validate correction caps through walk-forward testing to prevent small samples from causing excessive movements.

## Contamination and structural breaks

Exclude by default, but preserve and report, observations affected by:

- Major acquisitions or divestitures
- Restatements
- Metric redefinitions
- Segment reorganisations
- Exceptional accounting changes
- Unforeseeable one-off events
- Missing or ambiguous units
- Guidance that does not match the reported metric

Excluded records must include a reason and must not be silently deleted.

## Qualitative features: phase two

Potential features include raised/lowered/reaffirmed/withdrawn guidance, widened or narrowed ranges, guidance age, material developments after guidance, hedging language and call-over-call language changes.

Initially, these features should affect confidence or source weighting—not directly move the forecast. Automated sentiment corrections should only be promoted if they improve leakage-safe walk-forward results.

## Required output per target metric

```text
Company:
Metric:
Definition:
Raw forecast:
Forecast source:

Clean historical observations:
Median historical bias:
Typical absolute error:
80% historical error band:
Actual-above-estimate rate:

Walk-forward raw error:
Walk-forward corrected error:
Periods improved:

Correction recommended: Yes / No
Applied correction:
Adjusted forecast:
Reason:

Structural-break warning:
Evidence sources:
```

## Engineering acceptance criteria

- One generic framework works across all four companies.
- Every estimate and actual has a traceable source and date.
- Historical tests cannot access post-cutoff documents.
- GAAP and adjusted metrics are never mixed.
- Quarterly and annual metrics are never mixed.
- Percentage metrics use percentage-point errors.
- Contaminated observations are excluded by default and reported.
- Sample size and uncertainty are always visible.
- Corrections are withheld when walk-forward tests do not improve accuracy.
- Raw forecasts remain visible beside adjusted forecasts.
- Results can be reproduced from a logged command.

## Suggested delivery sequence

1. Define the observation schema and metric-definition tags.
2. Build extraction for management guidance and reported actuals.
3. Add cutoff enforcement and source logging.
4. Calculate robust bias and error statistics.
5. Add management-guidance walk-forward tests.
6. Add historical agent forecast simulations.
7. Implement the correction gate and caps.
8. Add qualitative confidence features only if time permits.

## Architecture and judging summary

> We use the frozen corpus to run leakage-controlled historical simulations. We separately measure management-guidance bias and our agent's own forecasting bias by company, metric, definition and guidance vintage. Corrections are only applied when they improve walk-forward accuracy; otherwise, the system reports the observed pattern and leaves the forecast unchanged.

