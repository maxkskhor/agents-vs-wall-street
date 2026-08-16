# Glasshouse — build progress (live)

Last updated: 2026-08-16 13:35 BST, Team MYS. This branch mirrors the working
tree so the team can review in real time.

## ⚠️ Three things the team must decide (not decidable by one person)

1. **Two implementations now exist in this repo.** The Codex/Node track
   (`scripts/run-forecast-agent.mjs`, `npm run forecast`) and the Python track
   (`agent/`, `python -m agent run --all`). `entry.json` declares ONE
   `finalCommand`, and the architecture HTML must describe the system that
   actually produced the submitted numbers. Pick one before 17:15. The HTML
   currently describes the Python track.
2. **Team name is inconsistent in the repo**: `architecture/index.html` said
   "Team MYR", README says "Team MYS". Max confirmed **Team MYS** — applied to
   the HTML in this PR. Fix anywhere else it appears.
3. **Run-log timestamps predate the official start.** `logs/run-2026-08-16T09-49-*.jsonl`
   are ~09:49 UTC = ~10:49 London, before the 11:15 "building starts" line in
   SCHEDULE.md (flagged by the PM handoff note too). RULES.md treats
   competition-specific work built before the start as a disqualification risk
   for *all* prizes. Do not delete them — history must stay intact. Decide as a
   team how to present this to the organisers, and make sure the *final* run log
   unambiguously postdates 11:15 (all Python-track logs do: 11:20 UTC onward).

## Where we are

**The full pipeline works end-to-end.** `.venv/bin/python -m agent run --all`
produces all four workbooks, passes `npm run check:submission`, and writes a
per-company `audit.md` (evidence → assumptions → number) plus a timestamped log.

Current dry-run forecasts (will change slightly on the final 17:15 run after a
consensus refresh):

| Company | Metric | Forecast | Consensus anchor (gated) |
|---|---|---:|---:|
| HD | Net sales (USDm) | 47,120 | 47,300 (6 sources) |
| HD | Adjusted diluted EPS | 4.70 | 4.71 (11 sources) |
| HD | Comparable sales | 0.75% | none exists publicly |
| ADI | Revenue (USDm) | 3,931 | 3,920 (5 sources) |
| ADI | Adjusted diluted EPS | 3.33 | 3.33 (7 sources) |
| ADI | Adjusted gross margin | 73.4% | none found |
| HAS | Net fees (GBPm) | 892 | 902.3 (company-compiled) |
| HAS | Pre-exceptional basic EPS | 1.06p | 1.09p (company-compiled) |
| HAS | Pre-exceptional operating profit | 44.0 | 44.35 (company-compiled) |
| DE | Worldwide net sales and revenues | 12,668 | rejected — wrong basis (see below) |
| DE | Diluted EPS (GAAP) | 4.60 | 4.83 (13 sources) |
| DE | PP&A operating profit | 400 | none found |

Reruns are now bit-identical (deterministic evidence ordering + full prompt
caching). DE runs un-anchored: if anyone finds credible DE Q3 FY2026 consensus
numbers, put them in `research/consensus-DE.json` (copy the HAS file's shape)
and note it under humanInput in entry.json.

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

## Cross-checks against the PM research track

The PM notes in `research/HD-live-web-research.md` disagree with what our live
consensus fetch pulled, and the research is probably the better number:

- HD adjusted EPS: research found a **$4.62–4.73 band** across providers and
  says explicitly *do not average them*; our fetch stored a single **4.87**
  (ChartMill). 4.87 sits above the whole researched band and is currently
  pulling our HD EPS forecast up to 4.80. Worth reconciling before the final run.
- HD net sales: research found **$47.5bn** (Zacks); our fetch found none. Our
  forecast is 47,000 — i.e. we are already below that consensus.
- HD comp sales: research confirms **no public consensus exists** anywhere, so
  that metric is corpus-only. Matches our run (no anchor was found).
- The handoff's **date-gating warning** (searches surfacing post-earnings
  content dated 19 Aug) applies to our `agent consensus` step, which has no
  hard date gate. Anchors are cited and timestamped in `research/consensus-*.json`
  so they can be checked by hand before the final run.

## Review requests for teammates

1. Poke holes in agent/estimators.py arithmetic (catch-up + seasonal shares).
2. Read runs/<latest>/HD/audit.md — is the lineage legible to an outsider?
3. Sanity-check the DE PP&A number (500) against the segment outlook in the
   May 8-K — weakest link, fresh eyes wanted.
