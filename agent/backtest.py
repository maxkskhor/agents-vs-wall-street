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
from .engine import combine_methods
from .estimators import guidance, llm_analyst, statistical
from .extract import build_fact_table, guidance_facts, reported_series
from .runlog import RunLog, new_run_id

BACKTEST_DOCS = 26
MIN_BIAS_OBS = 3      # observations before a bias is even estimated
MIN_WF_TESTS = 3      # walk-forward tests before a correction can be recommended


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


def run_backtest(company_short: str | None, quarters: int = 4,
                 tag: str = "") -> int:
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
    out_path = CACHE / f"calibration{tag}.json"
    out_path.write_text(json.dumps(
        {"weights": weights, "guidance_bias": bias,
         "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
         "n_rows": len(rows)}, indent=1))
    _write_report(rows, weights, bias, tag)
    log.log("backtest", f"calibration written: weights={weights}")
    return 0


def _floor_rel(v: float, actual: float, floor: float) -> float:
    return min(5.0, abs(v - actual) / floor)


def _calibrate(rows: list[dict]) -> dict:
    """Grid-search method weights per metric kind, minimising mean capped
    floor-relative miss of the ensemble — computed by the SAME combine_methods
    the engine uses in production (weighted mean for money/eps, weighted
    median for percent), so the weights are fit under the function that will
    consume them. A zero weight drops the method, exactly as an absent method
    would; a grid point that silences every available method scores 5.0."""
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
                pairs = [(v, w) for v, w in pairs if w > 0]
                if not pairs:
                    score += 5.0
                    continue
                ens, _ = combine_methods(kind, pairs)
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


def _signed_error(actual: float, estimate: float, kind: str) -> float:
    """Signed error measured in the space the correction is applied in.

    Corrections are multiplicative for money/EPS (`raw * (1 + bias)`), so the
    bias must be relative to the ESTIMATE; dividing by the actual — as this
    did originally — systematically under-corrects. Percentage metrics are
    additive and use a plain percentage-point difference, because a relative
    error is meaningless for a metric that crosses zero, like comparable sales.
    """
    if kind == "percent":
        return actual - estimate
    return (actual - estimate) / max(abs(estimate), 1e-9)


def _cap(bias: float, kind: str) -> float:
    """Small samples must not be allowed to produce large adjustments."""
    return max(-1.5, min(1.5, bias)) if kind == "percent" else max(-0.06, min(0.06, bias))


def _guidance_bias(rows: list[dict]) -> dict:
    """Per company/metric bias of the guidance route, walk-forward validated.

    A bias existing is not a reason to correct for it. A correction is only
    recommended when, replaying chronologically and estimating the bias from
    ONLY earlier periods, the corrected forecast actually beat the raw one —
    on median error and on a majority of the periods tested.
    """
    groups: dict[str, list[dict]] = {}
    for r in rows:
        if r["methods"].get("guidance") is not None:
            groups.setdefault(f'{r["company"]}/{r["metric"]}', []).append(r)

    out: dict[str, dict] = {}
    for key, rs in groups.items():
        rs = sorted(rs, key=lambda r: r["target"])
        kind = rs[0]["kind"]
        errs = [_signed_error(r["actual"], r["methods"]["guidance"], kind) for r in rs]
        record = {
            "n": len(rs),
            "median_signed": round(statistics.median(errs), 4),
            "median_abs": round(statistics.median([abs(e) for e in errs]), 4),
            "p80_abs": round(sorted(abs(e) for e in errs)[int(0.8 * (len(errs) - 1))], 4),
            "pct_actual_above": round(100 * sum(1 for e in errs if e > 0) / len(errs)),
            "correction_recommended": False,
            "reason": "",
        }

        raw_errs, corr_errs, improved, tests = [], [], 0, 0
        for i in range(1, len(rs)):
            prior = errs[:i]
            if len(prior) < MIN_BIAS_OBS:
                continue
            b = _cap(statistics.median(prior), kind)
            r = rs[i]
            est = r["methods"]["guidance"]
            corrected = est + b if kind == "percent" else est * (1 + b)
            raw_e, corr_e = abs(est - r["actual"]), abs(corrected - r["actual"])
            raw_errs.append(raw_e)
            corr_errs.append(corr_e)
            tests += 1
            improved += corr_e < raw_e
        record["walk_forward_tests"] = tests
        if tests:
            record["wf_raw_median_abs"] = round(statistics.median(raw_errs), 4)
            record["wf_corrected_median_abs"] = round(statistics.median(corr_errs), 4)
            record["pct_periods_improved"] = round(100 * improved / tests)

        if tests < MIN_WF_TESTS:
            record["reason"] = (f"insufficient walk-forward evidence "
                                f"({tests} tests, need {MIN_WF_TESTS})")
        elif record["wf_corrected_median_abs"] >= record["wf_raw_median_abs"]:
            record["reason"] = "correction did not reduce walk-forward error"
        elif record["pct_periods_improved"] < 50:
            record["reason"] = (f"only {record['pct_periods_improved']}% of periods "
                                f"improved (need >=50%)")
        else:
            record["correction_recommended"] = True
            # deployed estimate: capped MEDIAN of all signed errors (a median,
            # not a mean — the field was once mislabelled "mean_signed"). The
            # full sample is used deliberately: walk-forward proved the rolling
            # estimate helps out-of-sample; the full-sample median is simply
            # the best available estimate to carry forward from here.
            record["bias_estimate"] = _cap(statistics.median(errs), kind)
            record["reason"] = (
                f"walk-forward median error {record['wf_raw_median_abs']} -> "
                f"{record['wf_corrected_median_abs']}, "
                f"{record['pct_periods_improved']}% of periods improved")
        out[key] = record
    return out


def _write_report(rows: list[dict], weights: dict, bias: dict,
                  tag: str = "") -> None:
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
    (RESEARCH / f"backtest-report{tag}.md").write_text("\n".join(lines))
