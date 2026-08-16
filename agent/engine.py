"""Deterministic combination of estimator outputs into the 12 final numbers.

Method estimates are combined with a weighted median (robust to one bad
estimator), then optionally shrunk toward the public consensus anchor. The
whole decision — inputs, weights, formula, intermediate values — is returned
as lineage so the audit trail can show evidence -> assumptions -> number.
"""

from __future__ import annotations

import json
import statistics

from .config import CACHE, Company, Metric
from .estimators import Estimate

DEFAULT_WEIGHTS = {"guidance": 0.5, "llm_analyst": 0.3, "statistical": 0.2}
CONSENSUS_BETA = 0.6   # final = consensus + beta * (ensemble - consensus)


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


def _round(metric: Metric, v: float) -> float:
    if metric.kind == "money":
        return float(round(v))
    return round(v, 2)


def combine(company: Company, metric: Metric, estimates: list[Estimate],
            consensus_value: float | None) -> tuple[float, dict]:
    cal = load_calibration()
    weights = dict(DEFAULT_WEIGHTS)
    weights.update(cal.get("weights", {}).get(metric.kind, {}))

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
            "samples": [{"value": e.value, **e.inputs} for e in analyst_samples]}
    for e in estimates:
        if e.method in ("statistical", "guidance"):
            by_method[e.method] = e.value
            lineage["methods"][e.method] = {"value": e.value, **e.inputs}

    if not by_method:
        raise RuntimeError(f"{company.short}/{metric.key}: every estimator abstained")

    pairs = [(v, weights.get(m, 0.1)) for m, v in by_method.items()]
    ensemble = weighted_median(pairs)
    lineage["ensemble"] = {"value": ensemble,
                           "formula": "weighted median of method values"}

    final = ensemble
    if consensus_value is not None:
        final = consensus_value + CONSENSUS_BETA * (ensemble - consensus_value)
        lineage["consensus_blend"] = {
            "consensus": consensus_value, "beta": CONSENSUS_BETA,
            "formula": f"consensus + {CONSENSUS_BETA} x (ensemble - consensus)",
            "value": final}

    final = _round(metric, final)
    lineage["final"] = final
    return final, lineage
