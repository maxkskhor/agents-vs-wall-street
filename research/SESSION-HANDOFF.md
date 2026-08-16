# Session handoff — PM research track (Team MYR)

Context for the coding agent picking this up: this covers work done on the research/validation side while the forecasting pipeline was being built in parallel. Nothing here has been wired into the pipeline yet — that's the integration work this handoff is for.

## Repo state

- Pipeline already exists and has run successfully once: [agent/forecast-prompt.md](../agent/forecast-prompt.md), [agent/forecast.schema.json](../agent/forecast.schema.json), [scripts/run-forecast-agent.mjs](../scripts/run-forecast-agent.mjs). It spawns Codex CLI per company (read-only sandbox against `challenge/offline-data/`), validates output against the schema (units, bear≤value≤bull, evidence IDs exist), writes into the official `.xlsx` templates.
- Two run logs exist in `logs/` — one failed (sandbox/environment error), one succeeded end-to-end for all 4 companies.
- ⚠️ **Flagged separately to the team:** the successful run's internal timestamp is ~09:49 UTC (~10:49 London), which is before the 11:15 official "building starts" time in SCHEDULE.md. Worth the team confirming this was pipeline testing, not the run that gets submitted — the *final* run must unambiguously postdate 11:15.
- [architecture/index.html](../architecture/index.html): team identity filled in (Team MYR, members Yash Rai/Max Khor/Swareena Gurung). All 6 content sections (How it works, Research & reasoning, Design choices, Checks & tests, Reproducing the run, Known weaknesses) are still placeholder text — PM-owned, in progress.
- `entry.json`: not yet created in this checkout. It's git-ignored by design (never visible across machines) — status unknown from repo state, needs checking with the teammate handling it directly.
- `submission/`: empty except README (workbooks are gitignored, only exist on whichever machine runs the pipeline).

## Research deliverables produced this session

All in `research/` (git-ignored, working notes only):

- `HD-public-notes.md`, `ADI-public-notes.md`, `HAS-public-notes.md`, `DE-public-notes.md` — blank templates, one per company, for manual research capture (guidance, consensus, headwinds, sanity-check checklist).
- **`HD-live-web-research.md`** — the fully worked example. Live web research for Home Depot Q2 FY2026, following a strict methodology (see below). This is the pattern to replicate for ADI, Hays, and Deere if the team wants the same evidence base for all four companies.
- `HD-blindspot-scrape.md` — separate research covering the corpus's actual document gap (21 May → 14 Aug 2026): found one material item (30 July reorg, CFO now directly owns Pro strategy) and one minor bolt-on acquisition (Mingledorff's, 11 May) missing from the corpus.

## What the Home Depot research methodology established (replicate for other 3 companies)

**The corpus vs. live-web split:** `challenge/offline-data/` is 100% company-originated (filings, transcripts, slides) — there is no third-party analyst consensus anywhere in it. That's the entire reason to scrape: to get an external "Wall Street thinks X" benchmark the corpus structurally cannot contain.

**Source-checking order used** (from the finance course notes + what actually worked): Yahoo Finance/Zacks → Nasdaq → TipRanks → MarketBeat → Investing.com → Simply Wall St → Motley Fool → Visible Alpha/FactSet/LSEG/Capital IQ (paywalled, expect blocked). TipRanks and Simply Wall St returned 403 bot-detection both times — treat as reliably blocked, don't keep retrying.

**Key findings for HD specifically:**
- Earnings release confirmed: **18 Aug 2026, pre-market, call 9:00am ET.**
- Net sales consensus: **$47.5bn** (Zacks, best-corroborated) vs. a competing **$47.25bn** from an unnamed aggregator.
- Adjusted EPS consensus: **no single number** — genuine disagreement across providers, band is **$4.62–$4.73**. Do not average these into one figure; report the band.
- Total-company comp sales: **no public consensus exists anywhere**, confirmed across every source checked, twice. This metric is corpus-only — the agent has nothing external to benchmark it against.
- No new management guidance/disclosure found since the 14 Aug freeze.

## Critical methodological finding — date-gating risk

Twice during this research, live web search surfaced content that was actually dated **19 August 2026 — the day after HD's earnings release** — despite querying for pre-earnings information. One instance looked like "actual Q2 results already reported," the other was an analyst (Telsey) revising an estimate *after* seeing results. Both were caught by checking the underlying dated source and excluded.

**Implication for the pipeline:** if `agent/forecast-prompt.md` or any live-scraping tool gets built to pull external evidence automatically, it needs an explicit hard date check against the actual earnings release timestamp — not just a "recent" or "pre-earnings" instruction to the model. Post-event content can and does leak into searches that are nominally scoped to "before earnings."

## Not done yet

- Live web research for ADI, Hays (LSE:HAS), and Deere — only Home Depot has been done. Same methodology, same source order, same rigor (open underlying pages, don't average across providers, exclude anything post-event) should be applied to the other three if the team wants consensus benchmarks for all 12 metrics, not just HD's 3.
- No integration between `research/*.md` files and the actual forecasting pipeline (`agent/forecast-prompt.md` / `scripts/run-forecast-agent.mjs`) — this research currently exists as standalone reference material a human or the forecasting agent would need to be pointed at manually.
- `architecture/index.html` content sections — still placeholder, PM-owned, not a coding task.
- `entry.json` — status unverified, owned by a specific teammate, not created in this checkout.

## Suggested integration approach for the coding agent

If the goal is to fold live evidence into the actual forecast (rather than leave it as human-readable reference material):
1. Decide whether live-web retrieval becomes part of the agent's own tool-use during the run, or whether pre-scraped `research/*.md` files get concatenated into the prompt context per company.
2. If pre-scraping: replicate the HD methodology for ADI/HAS/DE before the final run, save as `research/{TICKER}-live-web-research.md`, and have `scripts/run-forecast-agent.mjs` read and inject the relevant file into `taskPrompt(company)` alongside the existing base prompt.
3. Either way, bake in the date-gating check above — whatever pulls live data needs to verify it predates each company's specific earnings release before treating it as valid evidence.
4. Keep the "don't average across consensus providers, report the range" rule from `agent/forecast-prompt.md`'s validation logic if extending it to also validate live-sourced evidence.
