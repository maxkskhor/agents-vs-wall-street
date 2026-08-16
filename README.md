# Agents vs Wall Street

An autonomous earnings-forecasting agent built for the AI Tinkerers London
Agents vs Wall Street hackathon.

## Goal

Forecast a public company's next reported revenue and EPS using auditable data,
tools, and evidence. The demo should show the forecast, confidence, source trail,
and comparison with Wall Street consensus.

## Repository layout

```text
backend/     Agent, tools, data access, and forecast API
frontend/    Demo interface and forecast visualisation
data/        Small checked-in fixtures only; no secrets or large datasets
scripts/     Setup, development, evaluation, and demo helpers
```

## Setup

The implementation stack and commands will be added once the team chooses them.
Copy `.env.example` to `.env` for local credentials. Never commit `.env`.

## Minimum forecast output

- company and reporting period
- revenue estimate
- EPS estimate
- confidence or uncertainty range
- evidence and source timestamps
- generated-at timestamp

## Demo bar

One command starts the project, one path produces a forecast, and cached sample
data keeps the demo working if an external API is unavailable.
