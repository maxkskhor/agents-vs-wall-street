"""CLI entry point.

Commands:
  run       --all | --company HD [--offline] [--asof YYYY-MM-DD] [--out DIR]
  backtest  --company HD [--quarters N]
  consensus --all | --company HD
  smoke     quick provider connectivity check

The final hackathon command is:  .venv/bin/python -m agent run --all
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from .config import RUNS, SUBMISSION, load_companies, get_company
from .runlog import RunLog, new_run_id


def _companies(args):
    if getattr(args, "all", False) or not args.company:
        return load_companies()
    return [get_company(args.company)]


def cmd_run(args) -> int:
    from .pipeline import run_company

    run_id = new_run_id()
    log = RunLog(run_id)
    asof = dt.date.fromisoformat(args.asof) if args.asof else None
    log.log("start", f"run {run_id} companies={[c.short for c in _companies(args)]} "
                     f"offline={args.offline} asof={asof or 'latest'}")
    failures = []
    for company in _companies(args):
        try:
            result = run_company(company, log, run_id, offline=args.offline, asof=asof)
            log.log("done", f"{company.short}: " + ", ".join(
                f"{m.label}={result.final[m.label]}" for m in company.metrics))
        except Exception as e:  # noqa: BLE001 - keep other companies running
            log.log("error", f"{company.short}: {type(e).__name__}: {e}")
            failures.append(company.short)
    if failures:
        log.log("end", f"FAILED for {failures}")
        return 1
    log.log("end", f"all workbooks written to {SUBMISSION}/")
    return 0


def cmd_backtest(args) -> int:
    from .backtest import run_backtest
    return run_backtest(args.company, quarters=args.quarters)


def cmd_consensus(args) -> int:
    from .consensus import fetch_consensus
    run_id = new_run_id()
    log = RunLog(run_id)
    for company in _companies(args):
        fetch_consensus(company, log)
    return 0


def cmd_smoke(args) -> int:
    from . import llm
    provs = llm.available_providers()
    print("providers with keys:", provs or "NONE - create .env (see .env.example)")
    for p in provs:
        try:
            out = llm.chat(p, "Reply with exactly: ok", "ping", use_cache=False, max_tokens=1000)
            print(f"  {p} ({llm.default_model(p)}): {out.strip()[:40]}")
        except Exception as e:  # noqa: BLE001
            print(f"  {p}: FAILED {e}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="agent")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="research, forecast and write workbooks")
    p.add_argument("--all", action="store_true")
    p.add_argument("--company")
    p.add_argument("--offline", action="store_true",
                   help="skip the live consensus lookup")
    p.add_argument("--asof", help="pretend today is this date (backtest plumbing)")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("backtest", help="time-travel evaluation on past quarters")
    p.add_argument("--company", help="default: all four")
    p.add_argument("--quarters", type=int, default=4)
    p.set_defaults(func=cmd_backtest)

    p = sub.add_parser("consensus", help="fetch public consensus anchors via web search")
    p.add_argument("--all", action="store_true")
    p.add_argument("--company")
    p.set_defaults(func=cmd_consensus)

    p = sub.add_parser("smoke", help="check API keys and models")
    p.set_defaults(func=cmd_smoke)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
