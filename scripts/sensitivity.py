"""Sensitivity check: how much do the twelve submitted numbers move when a
defensible choice changes?

Runs the whole pipeline once per candidate analyst model and prints every
forecast side by side, plus the spread as a share of the median. Nothing is
written to submission/.

    .venv/bin/python scripts/sensitivity.py gpt-5.6-luna gpt-5.6-terra gpt-5.6-sol
"""

from __future__ import annotations

import os
import statistics
import sys

from agent.config import load_companies
from agent.pipeline import run_company
from agent.runlog import RunLog, new_run_id


def main(models: list[str]) -> int:
    run_id = new_run_id() + "-sensitivity"
    log = RunLog(run_id)
    results: dict[str, dict[tuple[str, str], float]] = {}

    for model in models:
        os.environ["ANALYST_MODEL"] = model
        vals: dict[tuple[str, str], float] = {}
        for company in load_companies():
            try:
                r = run_company(company, log, f"{run_id}-{model}", write=False)
                for m in company.metrics:
                    vals[(company.short, m.key)] = r.finals_by_key[m.key]
            except Exception as e:  # noqa: BLE001 - a variant failing is data too
                log.log("sensitivity", f"{model} {company.short}: {type(e).__name__}: {e}")
        results[model] = vals

    keys = sorted({k for v in results.values() for k in v})
    width = max(len(m) for m in models) + 2
    header = f"{'metric':26s}" + "".join(f"{m:>{width}s}" for m in models)
    print("\n" + header + f"{'spread':>10s}")
    print("-" * len(header + "    spread"))
    spreads = []
    for k in keys:
        row = [results[m].get(k) for m in models]
        got = [v for v in row if v is not None]
        cells = "".join(f"{('—' if v is None else f'{v:g}'):>{width}s}" for v in row)
        if len(got) > 1 and statistics.median(got):
            spread = (max(got) - min(got)) / abs(statistics.median(got))
            spreads.append((spread, k))
            s = f"{spread:9.1%}"
        else:
            s = f"{'—':>9s}"
        print(f"{k[0] + '/' + k[1]:26s}{cells}{s}")

    if spreads:
        spreads.sort(reverse=True)
        print(f"\nmedian spread across metrics: {statistics.median(s for s, _ in spreads):.1%}")
        print("most sensitive:")
        for s, k in spreads[:3]:
            print(f"  {k[0]}/{k[1]:22s} {s:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["gpt-5.6-luna"]))
