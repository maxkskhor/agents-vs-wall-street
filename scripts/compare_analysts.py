"""Compare candidate analyst models on identical backtest rows.

Usage:  .venv/bin/python scripts/compare_analysts.py rep_luna.md=luna rep_terra.md=terra ...

Reports mean and median floor-relative miss, head-to-head wins on identical
rows, and a two-sided sign test so we can tell a real difference from noise.
An earlier comparison of two models was reported as a win when it was in fact
within noise; this script exists so that cannot happen silently again.
"""

from __future__ import annotations

import math
import re
import statistics
import sys

ROW = re.compile(
    r"\| (\w+) \| (FY\S+) \| (\w+) \| ([-\d.e+]+) \| ([-\d.e+—]+) \| ([-\d.e+—]+) \| ([-\d.e+—]+) \|")
PERCENT_METRICS = {"comp_sales", "adj_gross_margin"}


def parse(path: str) -> dict:
    rows = {}
    for line in open(path):
        m = ROW.match(line)
        if not m:
            continue
        co, tgt, met, actual, _stat, _guid, llm = m.groups()
        rows[(co, tgt, met)] = {
            "actual": float(actual),
            "llm": None if llm == "—" else float(llm)}
    return rows


def floor_rel(v: float, actual: float, metric: str) -> float:
    floor = 0.5 if metric in PERCENT_METRICS else max(abs(actual) * 0.005, 0.01)
    return min(5.0, abs(v - actual) / floor)


def sign_test(wins: int, losses: int) -> float:
    """Two-sided exact binomial p-value for wins vs losses under p=0.5."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main(args: list[str]) -> int:
    models = {}
    for arg in args:
        path, _, name = arg.partition("=")
        models[name or path] = parse(path)

    print(f"{'model':12s} {'n':>4s} {'mean':>7s} {'median':>7s}")
    for name, rows in models.items():
        vals = [floor_rel(r["llm"], r["actual"], k[2])
                for k, r in rows.items() if r["llm"] is not None]
        print(f"{name:12s} {len(vals):4d} {statistics.mean(vals):7.3f} "
              f"{statistics.median(vals):7.3f}")

    names = list(models)
    print("\nhead-to-head on identical rows (two-sided sign test):")
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            common = [k for k in models[a] if k in models[b]
                      and models[a][k]["llm"] is not None
                      and models[b][k]["llm"] is not None]
            wa = wb = 0
            for k in common:
                ea = abs(models[a][k]["llm"] - models[a][k]["actual"])
                eb = abs(models[b][k]["llm"] - models[b][k]["actual"])
                if ea < eb - 1e-9:
                    wa += 1
                elif eb < ea - 1e-9:
                    wb += 1
            p = sign_test(wa, wb)
            verdict = "SIGNIFICANT" if p < 0.05 else "within noise"
            print(f"  {a:10s} {wa:3d} - {wb:<3d} {b:10s}  n={len(common):3d}  "
                  f"p={p:.3f}  {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
