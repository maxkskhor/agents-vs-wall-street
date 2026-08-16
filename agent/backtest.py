"""Time-travel backtest: run the same estimators "as of" the day before each
past earnings report, score against the actual that later documents reveal,
and calibrate ensemble weights from the result.

Scoring proxy: the accuracy prize divides our miss by Wall Street's miss with a
floor (0.5pp for percents, 0.5% of the reported value otherwise). Historical
Wall Street misses are not in the corpus, so we report the FLOOR-RELATIVE miss
(our miss / floor): the score we would receive if Wall Street were perfect.
It is an upper bound on the real score and comparable across metrics.

Contamination caveat (also in the write-up): the LLM-analyst estimator may have
seen pre-cutoff actuals in training. Quarters reported in 2026 are the cleanest
window; the deterministic estimators are contamination-free by construction.
"""

from __future__ import annotations

import datetime as dt
import itertools
import json
import statistics

from . import llm, periods
from .config import CACHE, RESEARCH, Company, load_companies, get_company
from .corpus import results_docs
from .engine import weighted_median
from .estimators import guidance, llm_analyst, statistical
from .extract import build_fact_table, guidance_facts, reported_series
from .runlog import RunLog, new_run_id

BACKTEST_DOCS = 26


def _floor(kind: str, actual: float) -> float:
    if kind == "percent":
        return 0.5
    return max(abs(actual) * 0.005, 0.01)


def _report_date(facts, period: str) -> dt.date | None:
    dates = [dt.date.fromisoformat(f.published) for f in facts
             if f.fact_type == "reported" and f.period == period]
    return min(dates) if dates else None


def _targets(company: Company, series_all: dict, facts, quarters: int) -> list[str]:
    money_key = company.metrics[0].key
    kind = periods.parse(company.period)[1]
    cands = [p for p in series_all[money_key]
             if periods.parse(p)[1] == kind and p != company.period]
    cands.sort(reverse=True)
    picked = []
    for p in cands:
        if _report_date(facts, p) is not None:
            picked.append(p)
        if len(picked) >= (quarters if kind == "Q" else 2):
            break
    return picked


def run_backtest(company_short: str | None, quarters: int = 4) -> int:
    run_id = new_run_id()
    log = RunLog(run_id)
    companies = [get_company(company_short)] if company_short else load_companies()
    provider = (llm.available_providers() or [None])[0]
    if provider is None:
        log.log("backtest", "no API keys — running deterministic estimators only")

    rows: list[dict] = []
    for company in companies:
        docs = results_docs(company, limit=BACKTEST_DOCS)
        facts, _ = build_fact_table(company, docs, log, provider) if provider else ([], [])
        series_all = reported_series(company, facts)
        targets = _targets(company, series_all, facts, quarters)
        log.log("backtest", f"{company.short}: targets {targets}")

        for target in targets:
            rdate = _report_date(facts, target)
            asof = rdate - dt.timedelta(days=1)
            series = reported_series(company, facts, asof=asof)
            gfacts = guidance_facts(company, facts, asof=asof)
            for metric in company.metrics:
                actual = series_all[metric.key].get(target)
                if actual is None:
                    continue
                methods: dict[str, float] = {}
                s = statistical(metric, series[metric.key], target)
                if s:
                    methods["statistical"] = s.value
                g = guidance(metric, series[metric.key], gfacts, target)
                if g:
                    methods["guidance"] = g.value
                analysts = llm_analyst(company, metric, series[metric.key], gfacts,
                                       target, None, log, samples_per_provider=1)
                if analysts:
                    methods["llm_analyst"] = statistics.median(a.value for a in analysts)
                if not methods:
                    continue
                rows.append({
                    "company": company.short, "target": target, "asof": str(asof),
                    "metric": metric.key, "kind": metric.kind, "actual": actual,
                    "methods": methods, "floor": _floor(metric.kind, actual)})
                log.log("backtest", f"{company.short} {target} {metric.key}: "
                        f"actual={actual} " + " ".join(
                            f"{m}={v:.4g}(miss {abs(v-actual):.3g})"
                            for m, v in methods.items()))

    if not rows:
        log.log("backtest", "no scorable rows — check extraction/API keys")
        return 1

    weights = _calibrate(rows)
    bias = _guidance_bias(rows)
    CACHE.mkdir(exist_ok=True)
    (CACHE / "calibration.json").write_text(json.dumps(
        {"weights": weights, "guidance_bias": bias,
         "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
         "n_rows": len(rows)}, indent=1))
    _write_report(rows, weights, bias)
    log.log("backtest", f"calibration written: weights={weights}")
    return 0


def _floor_rel(v: float, actual: float, floor: float) -> float:
    return min(5.0, abs(v - actual) / floor)


def _calibrate(rows: list[dict]) -> dict:
    """Grid-search method weights per metric kind, minimising mean capped
    floor-relative miss of the weighted-median ensemble."""
    out: dict[str, dict] = {}
    grid = [w for w in itertools.product(range(11), repeat=3) if sum(w) == 10]
    for kind in ("money", "eps", "percent"):
        krows = [r for r in rows if r["kind"] == kind]
        if len(krows) < 3:
            continue
        best, best_score = None, float("inf")
        for wg, wl, ws in grid:
            score = 0.0
            for r in krows:
                pairs = [(v, {"guidance": wg, "llm_analyst": wl, "statistical": ws}[m])
                         for m, v in r["methods"].items()]
                if all(p[1] == 0 for p in pairs):
                    score += 5.0
                    continue
                ens = weighted_median([(v, w or 0.001) for v, w in pairs])
                score += _floor_rel(ens, r["actual"], r["floor"])
            score /= len(krows)
            if score < best_score:
                best, best_score = (wg, wl, ws), score
        if best:
            wg, wl, ws = best
            out[kind] = {"guidance": wg / 10, "llm_analyst": wl / 10,
                         "statistical": ws / 10, "backtest_score": round(best_score, 3),
                         "n": len(krows)}
    return out


def _guidance_bias(rows: list[dict]) -> dict:
    """Mean signed error of the guidance estimator per company: how much the
    company's guidance-anchored number under/over-shoots actuals."""
    out: dict[str, dict] = {}
    for r in rows:
        v = r["methods"].get("guidance")
        if v is None:
            continue
        key = f'{r["company"]}/{r["metric"]}'
        rel = ((r["actual"] - v) / abs(r["actual"])) if r["kind"] != "percent" else (r["actual"] - v)
        out.setdefault(key, []).append(rel)
    return {k: {"mean_signed": round(statistics.mean(v), 4), "n": len(v)}
            for k, v in out.items() if len(v) >= 2}


def _write_report(rows: list[dict], weights: dict, bias: dict) -> None:
    RESEARCH.mkdir(exist_ok=True)
    lines = ["# Backtest report (time-travel evaluation)", "",
             "Floor-relative miss = |forecast − actual| / scoring floor, capped at 5.0. ",
             "It is the accuracy-prize score we would get if Wall Street were perfect — "
             "an upper bound on the real score.", "",
             "| Company | Target | Metric | Actual | " +
             "Stat | Guid | LLM | Best method | Floor-rel (best) |",
             "|---|---|---|---:|---:|---:|---:|---|---:|"]
    for r in rows:
        m = r["methods"]
        best_m = min(m, key=lambda k: abs(m[k] - r["actual"]))
        cells = [f'{m.get(k):.4g}' if m.get(k) is not None else "—"
                 for k in ("statistical", "guidance", "llm_analyst")]
        lines.append(
            f'| {r["company"]} | {r["target"]} | {r["metric"]} | {r["actual"]:.4g} | '
            + " | ".join(cells) +
            f' | {best_m} | {_floor_rel(m[best_m], r["actual"], r["floor"]):.2f} |')
    lines += ["", "## Calibrated weights", "```json",
              json.dumps(weights, indent=1), "```",
              "", "## Guidance bias (actual vs guidance-anchored, signed)", "```json",
              json.dumps(bias, indent=1), "```", "",
              "Caveat: LLM-analyst rows for pre-2026 quarters may be contaminated by "
              "model training data; deterministic estimator rows are not."]
    (RESEARCH / "backtest-report.md").write_text("\n".join(lines))
