---
name: run-forecast
description: Run this repo's earnings-forecasting pipeline (Python "Glasshouse" track or Node/Codex track) end-to-end, with setup checks and output verification. Use when the user wants to run, launch, or test the forecasting agent/pipeline for the Agents vs Wall Street hackathon entry.
---

# Run the forecast pipeline

This repo has **two separate pipelines** that both produce the four required
workbooks in `submission/`. `PROGRESS.md` item 1 tracks which one the team
has picked as the real entry — check it first if it's unclear which one to run.

- **Python track** (`agent/`, `.venv/bin/python -m agent ...`) — the more
  complete implementation: extraction, three estimators, backtest-calibrated
  combination, validation gates, per-company audit trail.
- **Node/Codex track** (`scripts/run-forecast-agent.mjs`, `npm run forecast`)
  — spawns one Codex CLI worker per company against the offline corpus.

## Which track to run

1. If the user names a track explicitly (or passes one via `args`, e.g.
   `python` / `node` / `codex`), use that.
2. Otherwise check `PROGRESS.md` for a team decision on which track is the
   real entry. If it says undecided, ask the user which one they mean before
   running anything — don't guess, since only one produces the numbers that
   matter for submission.

## Python track

```bash
# one-time setup — skip steps already done (check for .venv/ and .env first)
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env   # then the user must fill in ANTHROPIC_API_KEY / OPENAI_API_KEY

# check whether OPENAI_API_KEY is present WITHOUT reading or printing its value
# — never cat/echo .env or capture its contents into a variable or message
if ! grep -q '^OPENAI_API_KEY=.\+' .env 2>/dev/null; then
  echo "OPENAI_API_KEY is missing from .env"
fi

# verify API keys work before a full run
.venv/bin/python -m agent smoke

# optional: refresh consensus anchors (live web-search + offline
# live-web-evidence corpus; cached to research/)
.venv/bin/python -m agent consensus --all

# optional: time-travel backtest -> cache/calibration.json + research/backtest-report.md
.venv/bin/python -m agent backtest

# main run — research, forecast, validate, write all four workbooks
.venv/bin/python -m agent run --all
```

Useful flags: `--offline` skips the live web-search consensus lookup;
`--company HD` (or `ADI` / `HAS` / `DE`) runs a single company instead of
all four.

Consensus anchors also pull in any `challenge/offline-data/<company>/
live-web-evidence/*.md` memos present — human-researched external analyst
estimates, transcribed via LLM extraction and gated through the exact same
corroboration rules as the live web-search fetch (never trusted directly).
This runs even under `--offline`, since it only transcribes a local file and
never makes a search call; `--offline` just skips the live web-search loop.
It's a no-op for a company with no `live-web-evidence/` folder. Because
anchors are cached to `research/consensus-<TICKER>.json`, **delete the
relevant cache file(s) before a run** if `challenge/offline-data/` changed
and you want that reflected — a stale cache short-circuits both the live
fetch and the offline-corpus transcription (`load_consensus(company) or
fetch_consensus(...)` in `agent/pipeline.py`).

Before running, check `.env` actually has non-empty `ANTHROPIC_API_KEY` and
`OPENAI_API_KEY` — `smoke` will fail fast and clearly if not, so run it first
rather than jumping straight to a full `run --all`.

**If `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) turns out to be missing**, stop
and ask the user to paste it into `.env` themselves. Do not read, print,
echo, `cat`, or otherwise capture the contents of `.env` yourself, and never
copy a key into it from anywhere else (another config file, an environment
variable, the `codex` CLI's own auth, etc.) — per `AGENTS.md`: "Never read,
print, modify, or commit `.env` or credentials." The presence check above is
the one narrow exception (it only reports true/false, never the value) —
everything past that point is the user's job, not this skill's.

**After the run**, verify rather than just reporting success:
- Read the newest `logs/*.log` for errors.
- Read each `runs/<run-id>/<CO>/audit.md` and check its validation table is
  all PASS, not just that the command exited 0.
- Confirm all four files exist under `submission/`.

## Node/Codex track

Requires Node.js and an authenticated `codex` CLI on `PATH` — check
`codex --version` (or equivalent) works before running; a missing/unauthenticated
CLI is the most common failure here.

```bash
npm install
npm run test:starter   # sanity check
npm run forecast       # runs all four companies in parallel
npm run check:forecasts
```

Writes structured research to `research/`, workbooks to `submission/`, a
timestamped JSONL log to `logs/`. Check the log for `company_completed` vs
`run_failed` events per company rather than trusting a clean exit alone.

## Either way, before treating a run as submission-ready

```bash
npm run check:submission
```

This validates `entry.json`, `architecture/index.html`, and the four
workbooks — not whether the forecasts are good. If `entry.json` still has
empty required fields (check `PROGRESS.md`'s "What's left" section, which
tracks this), say so plainly rather than reporting the run as complete: a
passing forecast run does not mean the entry is submission-ready.

## Guardrails

- Never edit `challenge/templates/`, `challenge/companies.json`, or anything
  under `challenge/offline-data/` while "running" this skill — those are
  supplied inputs, not pipeline output (see `AGENTS.md`).
- Don't commit or push as part of just running the pipeline — that's a
  separate, explicit ask (see repo rule: never commit directly to `main`).
- If both tracks have been run, don't silently pick a workbook to keep in
  `submission/` — the second run overwrites the first company-by-company, so
  flag that explicitly to the user rather than letting it happen unnoticed.
