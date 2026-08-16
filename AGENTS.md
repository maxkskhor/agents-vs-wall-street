# AGENTS.md

## Objective

Build a working, auditable earnings-forecasting agent for the Agents vs Wall
Street hackathon. Optimise for a reliable end-to-end demo, clear architecture,
and visible evidence behind every forecast.

## Working rules

- Treat `RULES.md`, `SUBMISSION.md`, `JUDGING.md`, and `SCHEDULE.md` as the
  authoritative event specification.
- Keep changes small and scoped to the assigned component.
- Do not refactor shared files without coordinating with the team.
- Never read, print, modify, or commit `.env` or credentials.
- Never commit `entry.json`; it contains private team details.
- Do not commit generated datasets, large files, caches, or build output.
- Preserve the supplied files under `challenge/`, including the original
  workbook templates and frozen historical corpus.
- Never alter the `Summary` sheet structure, metric labels, units, fiscal-period
  columns, or required output filenames.
- Record setup and run commands in `README.md` as soon as they exist.
- The final command must process all four companies and create all four required
  workbooks in `submission/` during one clear run.
- Include source URLs and timestamps in evidence returned by tools.
- Keep timestamped run logs, including failures and retries, without secrets.
- Run `npm run check:submission` before the final upload.
- Manual workbook upload is required; do not automate submission to OpenStocks.

## Required outputs

- `submission/HD-FY2026Q2.xlsx`
- `submission/ADI-FY2026Q3.xlsx`
- `submission/HAS-FY2026.xlsx`
- `submission/DE-FY2026Q3.xlsx`
- a timestamped clear-run log under `logs/`
- a complete self-contained `architecture/index.html`

## Definition of done

One documented command performs the research, financial reasoning, validation,
and workbook generation for all four companies. The output passes the supplied
submission checks and can be traced from evidence through assumptions and
calculations to each of the 12 forecasts.
