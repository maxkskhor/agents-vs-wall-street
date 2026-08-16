# AGENTS.md

## Objective

Build a working, auditable earnings-forecasting agent for the Agents vs Wall
Street hackathon. Optimise for a reliable end-to-end demo, clear architecture,
and visible evidence behind every forecast.

## Working rules

- Keep changes small and scoped to the assigned component.
- Do not refactor shared files without coordinating with the team.
- Never read, print, modify, or commit `.env` or credentials.
- Do not commit generated datasets, large files, caches, or build output.
- Preserve a deterministic demo path using checked-in sample fixtures.
- Record setup and run commands in `README.md` as soon as they exist.
- Prefer simple interfaces between the agent, data tools, forecast output, and UI.
- Include source URLs and timestamps in evidence returned by tools.
- Run the relevant checks before committing.

## Initial component boundaries

- `backend/`: orchestration, tools, forecasting logic, schemas, and API
- `frontend/`: demo flow, evidence display, charts, and presentation
- `data/`: small synthetic or public fixtures safe to commit
- `scripts/`: reproducible setup, checks, evaluation, and demo commands

## Definition of done

The system can produce and display a revenue and EPS forecast for one company,
with uncertainty and traceable evidence, through a repeatable demo flow.
