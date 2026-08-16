# Glasshouse — build progress (live)

Last updated: 2026-08-16 13:20 BST. This branch mirrors the working tree so the
team can review in real time. Ask in the group chat before editing shared files.

## Where we are

**The full pipeline works end-to-end.** `.venv/bin/python -m agent run --all`
produces all four workbooks, passes `npm run check:submission`, and writes a
per-company `audit.md` (evidence → assumptions → number) plus a timestamped log.

Current dry-run forecasts (will change slightly on the final 17:15 run after a
consensus refresh):

| Company | Metric | Forecast | Public consensus (cited) |
|---|---|---:|---:|
| HD | Net sales (USDm) | 47,000 | — |
| HD | Adjusted diluted EPS | 4.80 | 4.87 |
| HD | Comparable sales | 0.85% | — |
| ADI | Revenue (USDm) | 3,978 | 3,900 (= guide midpoint) |
| ADI | Adjusted diluted EPS | 3.33 | — |
| ADI | Adjusted gross margin | 73.4% | — |
| HAS | Net fees (GBPm) | 893 | 902.4 |
| HAS | Pre-exceptional basic EPS | 1.12p | 1.13p |
| HAS | Pre-exceptional operating profit | 43.0 | 45.3 |
| DE | Worldwide net sales and revenues | 12,818 | — (retrying fetch) |
| DE | Diluted EPS (GAAP) | 4.35 | — |
| DE | PP&A operating profit | 500 | — |

## How it works (one paragraph)

LLMs are never allowed to say a forecast number. gpt-5.6-luna transcribes cited
facts (quote-grounded: the number must appear verbatim in its quote, the quote
in its document); three estimators produce values — guidance arithmetic
(midpoints, FY catch-up, Hays H1+preannounced-H2 build-up), a no-LLM seasonal
statistical route, and a gpt-5.1 "analyst" that may only pick a cited base plus
itemised adjustments which the engine recomputes. A weighted median combines
them (weights from a time-travel backtest over past quarters), shrinks toward
live public consensus, then hard validation gates (units, magnitude bands,
cross-metric consistency, red-team) must pass before the workbook writer runs.

## Key findings from the backtest (see research/backtest-report.md)

- ADI beat its own guidance midpoint on revenue/EPS in every backtested
  quarter (~+3.5% revenue) → we tilt above consensus there, with citations.
- HD guided FY2025 comps ~1pp too optimistic → guidance route de-weighted for
  percent metrics.
- Hays FY build-up (H1 + pre-announced H2 growth) scored 0.18–0.19
  floor-relative — our best route; July trading update pre-announces
  "top of £37–46m range" operating profit.
- Deere is our weakest company: no usable quarterly guidance → statistical +
  analyst only. Declared in the write-up.

## What's left (owner: Claude session on Max's machine)

- [ ] Fill architecture/index.html placeholders: backtest table, honesty
      section, team names (NEEDS HUMAN: names + emails in entry.json too)
- [ ] Retry DE consensus fetch closer to 17:00
- [ ] 16:00 judge conversation — talk track in docs/talk-track.md
- [ ] 17:15 final run per README checklist; 17:30–18:00 manual uploads

## Review requests for teammates

1. Poke holes in agent/estimators.py arithmetic (catch-up + seasonal shares).
2. Read runs/<latest>/HD/audit.md — is the lineage legible to an outsider?
3. Sanity-check the DE PP&A number (500) against the segment outlook in the
   May 8-K — weakest link, fresh eyes wanted.
