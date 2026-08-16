# Five-minute judge conversation — talk track

The judging pairs use the same rubric questions; this maps our answers. Don't
pitch — walk them through one real number's lineage.

## Opening (30s)

"One rule shaped everything: the LLM is never allowed to say a forecast
number. Models transcribe cited evidence and propose assumptions; plain
arithmetic computes all twelve numbers; and because the corpus is frozen and
dated, we ran the whole agent *as of* past earnings dates and let that backtest
choose the ensemble weights."

## Then open one audit trail (2 min)

Open `runs/<final>/HD/audit.md` on the laptop and trace ONE number bottom-up:

1. the quoted guidance sentence + doc id (data approach),
2. the catch-up arithmetic turning FY guidance + reported Q1 into a Q2 figure
   (forecasting approach / model quality),
3. the three estimator values and the weighted median with backtested weights,
4. the validation table — point at a *rejected* item if there is one
   (validation & reliability).

## Rubric question → one-line answer

- **How does it reason instead of asking a model for a number?** The model
  can only pick a cited base from the history table and itemise adjustments;
  the engine recomputes the total and rejects samples whose base isn't real.
- **Can you follow evidence → the 12 numbers?** Yes, offline: facts.json →
  decision.json → audit.md per company; every fact carries a verbatim quote
  that must contain the number (grounding gate).
- **Data currency/trust?** Frozen corpus with provenance headers; later docs
  outrank earlier (restatements); pre-announcements outrank guidance — the
  Hays 10 July trading update is the flagship example.
- **Validation?** Unit traps (pence, percentage points, USDm), magnitude bands
  vs history, cross-metric consistency (HD comps vs sales growth, Hays
  fee→profit conversion), cross-provider disagreement, red-team pass.
  Failures block the workbook writer — show the failing test.
- **Harness?** One command, five stages, JSON artifact between each; per-doc
  extraction caching makes reruns and the backtest nearly free.
- **Tooling?** Corpus index/search, extraction cache, backtest harness,
  audit renderer, 18 offline unit tests.

## The accuracy-prize argument (30s, if asked)

Scoring is relative to Wall Street with a floor and a 5.0 cap, so: anchor near
consensus (cited live snapshot), deviate only where extracted evidence pushes,
and submit medians, not means — the median is the optimal point forecast under
absolute error. All four fiscal periods have already ended, so guidance and
pre-announcements dominate over macro speculation.

## Honesty (leave time for it)

- Backtest samples are small and the LLM route is partially contaminated for
  pre-2026 quarters (deterministic routes are not).
- Extraction misses are our real risk: grounding stops hallucination, not
  omission.
- Deere PP&A operating profit has the weakest guidance signal — say so before
  they ask.
