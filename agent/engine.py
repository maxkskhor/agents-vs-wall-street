"""Deterministic combination of estimator outputs into the 12 final numbers.

Money and EPS metrics are combined with a weighted MEAN: with only 2-3 method
values a weighted median just selects one input verbatim, so weights act as a
step function and a bias-corrected guidance value that isn't the median point
cannot move the answer at all. The mean makes weights continuous and lets
every validated correction reach the workbook. Percent metrics keep the
weighted median: their weights were calibrated under it and it cleared the
backtest gate there. (The routes share evidence — all three read the same
guidance sentence — so no combiner here is robust to a bad extraction; that
risk is owned by the grounding gate, not this file.)

The combined value is then optionally shrunk toward the public consensus
anchor. The whole decision — inputs, weights, formula, intermediate values —
is returned as lineage so the audit trail can show evidence -> assumptions ->
number.
"""

from __future__ import annotations

import json
import statistics

from .config import CACHE, Company, Metric
from .estimators import Estimate

# "derived" outranks even guidance: it is a structural identity (EPS is
# arithmetically downstream of the profit line), not an opinion. Where it
# applies, the statistical and analyst routes are the weak ones — on Hays EPS
# they returned 0.33-0.76 against a truth near 1.0.
DEFAULT_WEIGHTS = {"derived": 0.6, "guidance": 0.5, "llm_analyst": 0.3,
                   "statistical": 0.2}
# final = consensus + beta * (ensemble - consensus). The scoring rule caps the
# downside of deviating at 5.0 and pays unboundedly below 1.0 for being right,
# so shrinking hard toward the benchmark (old beta 0.6) forfeited the asymmetry:
# it left 7 of 12 submissions within 1.5% of the number we are scored against.
# Deviate where our evidence route spoke; lean on the Street only where it
# abstained.
CONSENSUS_BETA = 0.85          # guidance/pre-announcement route contributed
CONSENSUS_BETA_NO_GUIDE = 0.5  # our strongest route had nothing to say
CONSENSUS_MAX_GAP = 0.10           # rel. to consensus, guidance route present
CONSENSUS_MAX_GAP_NO_GUIDE = 0.25  # no guidance: Street outranks our weak routes
CONSENSUS_MAX_GAP_PP = 3.0         # percentage points, for percent metrics


def load_calibration() -> dict:
    p = CACHE / "calibration.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}


def weighted_median(pairs: list[tuple[float, float]]) -> float:
    """pairs: (value, weight)"""
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            return v
    return pairs[-1][0]


def weighted_mean(pairs: list[tuple[float, float]]) -> float:
    """pairs: (value, weight); weights renormalise over the methods present."""
    total = sum(w for _, w in pairs)
    if not total:
        return statistics.mean(v for v, _ in pairs)
    return sum(v * w for v, w in pairs) / total


def combine_methods(kind: str, pairs: list[tuple[float, float]]) -> tuple[float, str]:
    """One combiner for production AND the backtest, so weights are always fit
    under the same function that consumes them."""
    if kind == "percent":
        return weighted_median(pairs), "weighted median of method values"
    return weighted_mean(pairs), "weighted mean of method values"


def _round(metric: Metric, v: float) -> float:
    # 4dp for eps/percent: the scoring floor on a small EPS (Hays, ~1.1p) is
    # ~0.005, so rounding to 2dp could donate up to ~0.9 score points for free
    if metric.kind == "money":
        return float(round(v))
    return round(v, 4)


def combine(company: Company, metric: Metric, estimates: list[Estimate],
            consensus_value: float | None) -> tuple[float, dict]:
    cal = load_calibration()
    weights = dict(DEFAULT_WEIGHTS)
    grid = cal.get("weights", {}).get(metric.kind, {})
    # a grid whose own backtest score is ~capped found nothing better than
    # noise — keep the priors in that case (bit us on EPS: n=14, score 4.2)
    if grid and grid.get("backtest_score", 5.0) <= 4.0:
        # backtest samples are small (n<=18), so shrink the grid-searched
        # weights halfway toward the priors instead of trusting them outright
        for m in weights:
            weights[m] = round(0.5 * weights[m] + 0.5 * grid.get(m, weights[m]), 3)

    # empirical guidance bias: e.g. ADI has beaten its revenue-guide midpoint
    # by ~3.5% on average — correct the guidance estimate by the backtested
    # mean signed error when it is measured on 3+ quarters, capped for safety
    bias_all = cal.get("guidance_bias", {})
    bias = bias_all.get(f"{company.short}/{metric.key}")
    # only corrections that passed walk-forward validation in the backtest are
    # applied; an observed bias alone is not evidence that correcting helps
    if bias and bias.get("correction_recommended") and "bias_estimate" in bias:
        b = bias["bias_estimate"]
        for e in estimates:
            if e.method == "guidance":
                before = e.value
                e.value = (e.value + b if metric.kind == "percent"
                           else e.value * (1 + b))
                e.inputs["bias_correction"] = {
                    "before": before, "applied": b, "n": bias["n"],
                    "walk_forward": bias.get("reason"),
                    "why": "walk-forward-validated bias of the guidance route "
                           "for this company/metric"}

    by_method: dict[str, float] = {}
    lineage: dict = {"methods": {}, "weights": weights}
    analyst_samples = [e for e in estimates if e.method == "llm_analyst"]
    if analyst_samples:
        med = statistics.median(e.value for e in analyst_samples)
        spread = (max(e.value for e in analyst_samples)
                  - min(e.value for e in analyst_samples))
        by_method["llm_analyst"] = med
        lineage["methods"]["llm_analyst"] = {
            "value": med, "n_samples": len(analyst_samples), "spread": spread,
            "samples": [{**e.inputs, "value": e.value} for e in analyst_samples]}
    for e in estimates:
        if e.method in ("statistical", "guidance", "derived"):
            by_method[e.method] = e.value
            # "value" last: estimator inputs may carry their own raw "value"
            lineage["methods"][e.method] = {**e.inputs, "value": e.value}

    if not by_method:
        raise RuntimeError(f"{company.short}/{metric.key}: every estimator abstained")

    pairs = [(v, weights.get(m, 0.1)) for m, v in by_method.items()]
    ensemble, how = combine_methods(metric.kind, pairs)
    lineage["ensemble"] = {"value": ensemble, "formula": how}

    # A consensus far from our evidence-built ensemble usually means the
    # providers are quoting a DIFFERENT metric definition, not that we are
    # wrong: Deere's Street "revenue" is equipment-operations only, ~1.8bn
    # below "worldwide net sales and revenues". Shrinking toward a mismatched
    # definition is worse than not anchoring, so refuse and flag it.
    if consensus_value is not None:
        # gap is measured relative to the CONSENSUS (the reference we are
        # scored against), and the limit depends on whether our strongest
        # route spoke. With guidance present the gate is a definition-mismatch
        # detector and can be tight; without it the ensemble is our weakest
        # work and has no standing to veto the Street — only an absurd gap
        # (a Deere-style different-metric quote, ~17%) should reject there.
        gap = (abs(consensus_value - ensemble) if metric.kind == "percent"
               else abs(consensus_value - ensemble) / max(abs(consensus_value), 1e-9))
        if metric.kind == "percent":
            limit = CONSENSUS_MAX_GAP_PP
        else:
            limit = (CONSENSUS_MAX_GAP if "guidance" in by_method
                     else CONSENSUS_MAX_GAP_NO_GUIDE)
        if gap > limit:
            lineage["consensus_rejected"] = {
                "consensus": consensus_value, "ensemble": ensemble, "gap": gap,
                "limit": limit,
                "why": "consensus too far from evidence-built ensemble — likely a "
                       "different metric definition; anchor not applied"}
            consensus_value = None

    final = ensemble
    if consensus_value is not None:
        # deviate less from the benchmark when our strongest evidence route
        # (guidance/pre-announcement arithmetic) had nothing to say
        beta = (CONSENSUS_BETA if "guidance" in by_method
                else CONSENSUS_BETA_NO_GUIDE)
        final = consensus_value + beta * (ensemble - consensus_value)
        lineage["consensus_blend"] = {
            "consensus": consensus_value, "beta": beta,
            "formula": f"consensus + {beta} x (ensemble - consensus)",
            "value": final}

    final = _round(metric, final)
    lineage["final"] = final
    return final, lineage
