"""Validation gates that run before any workbook is written.

Deterministic gates (magnitude vs history, cross-metric consistency,
conversion-ratio coherence) are blocking. Two checks are advisory only and
can never block: the analyst-sample agreement check and the red-team LLM
pass (it flagged correct values too often to be trusted with a veto; if the
model is unavailable the deterministic gates stand alone).

Band philosophy: a gate whose tolerance is wider than the maximum scoring
penalty can only catch unit errors. The scoring floor is 0.5pp / 0.5% and the
score caps at 5x the floor, so bands here are set tight enough that a miss
large enough to max out the penalty is at least in the neighbourhood of
tripping a gate — while still passing every plausible forecast (ADI is
growing ~35% y/y; Deere's segment profit halves across a cycle).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import llm, periods
from .config import Company
from .runlog import RunLog

Series = dict[str, dict[str, float]]     # metric key -> period -> value


@dataclass
class Check:
    name: str
    status: str        # "pass" | "warn" | "fail"
    detail: str


@dataclass
class ValidationReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.status != "fail" for c in self.checks)

    def add(self, name: str, ok: bool, detail: str, warn_only: bool = False):
        self.checks.append(Check(name, "pass" if ok else ("warn" if warn_only else "fail"),
                                 detail))


_BANDS = {"money": (0.70, 1.42), "eps": (0.55, 1.70)}
# segment/operating-profit lines swing far more than revenue in a cycle
_METRIC_BANDS = {"ppa_op": (0.40, 2.00), "preex_op": (0.40, 2.00)}
_PERCENT_MAX_DELTA = 4.0     # pp vs prior-year level (score caps at a 2.5pp miss)

# conversion-ratio sanity per company: numerator/denominator checked against a
# band derived from the extracted history (hardcoded bands proved wrong across
# the cycle: Hays' real FY2025 conversion was 4.7%)
_RATIOS = {
    "HAS": ("preex_op", "net_fees"),
    "DE": ("ppa_op", "net_sales_rev"),
}


def _ratio_band(series: Series, num_k: str, den_k: str) -> tuple[float, float] | None:
    """Observed margin/conversion range with modest headroom. The old 0.5x/1.5x
    multipliers produced a 23x-wide band on Deere — a gate that could not fail
    on any error that costs score. 0.8x/1.25x keeps the forecast inside the
    neighbourhood of margins the business has actually printed."""
    ratios = []
    for period, den in series.get(den_k, {}).items():
        num = series.get(num_k, {}).get(period)
        if num is not None and den:
            ratios.append(num / den)
    if len(ratios) < 2:
        return None
    return min(ratios) * 0.8, max(ratios) * 1.25


def validate(company: Company, target: str, finals: dict[str, float],
             series: Series, lineage: dict[str, dict], log: RunLog,
             red_team: bool = True) -> ValidationReport:
    rep = ValidationReport()
    by_key = {m.key: m for m in company.metrics}

    for key, metric in by_key.items():
        v = finals.get(key)
        rep.add(f"{key}: value present", v is not None and v == v,
                f"final={v}")
        if v is None:
            continue
        prior = series.get(key, {}).get(periods.prior_year(target))
        if prior is None:
            rep.add(f"{key}: prior-year base exists", False,
                    f"no reported {periods.prior_year(target)} value in fact table")
            continue
        if metric.kind == "percent":
            ok = abs(v - prior) <= _PERCENT_MAX_DELTA
            rep.add(f"{key}: plausibility vs prior year", ok,
                    f"{v}pp vs prior-year {prior}pp (max delta {_PERCENT_MAX_DELTA}pp)")
        else:
            lo, hi = _METRIC_BANDS.get(key, _BANDS[metric.kind])
            ratio = v / prior if prior else float("inf")
            rep.add(f"{key}: magnitude vs prior year", lo <= ratio <= hi,
                    f"{v} vs prior-year {prior} (ratio {ratio:.2f}, band {lo}-{hi})")

        spread_info = lineage.get(key, {}).get("methods", {}).get("llm_analyst")
        if spread_info and spread_info.get("n_samples", 0) >= 2 and v:
            rel = spread_info["spread"] / max(abs(v), 1e-9)
            rep.add(f"{key}: analyst-sample agreement", rel <= 0.15,
                    f"cross-provider spread {spread_info['spread']:.3g} ({rel:.1%} of final)",
                    warn_only=True)

    # cross-metric consistency
    if company.short == "HD":
        ns, comp = finals.get("net_sales"), finals.get("comp_sales")
        prior_ns = series.get("net_sales", {}).get(periods.prior_year(target))
        if ns and comp is not None and prior_ns:
            growth_pp = (ns / prior_ns - 1) * 100
            # the observed wedge (new stores, SRS/GMS acquisitions, FX) has run
            # 1-3pp; an 8pp limit could never fire on a scoring-relevant error
            rep.add("HD: net sales growth vs comp sales", abs(growth_pp - comp) <= 4,
                    f"sales growth {growth_pp:.1f}pp vs comps {comp:.1f}pp "
                    f"(gap covers new stores/acquisitions/FX; limit 4pp)")
    if company.short == "ADI":
        gm = finals.get("adj_gross_margin")
        if gm is not None:
            rep.add("ADI: gross margin absolute range", 55 <= gm <= 80,
                    f"adjusted gross margin {gm}% must be a percentage level (55-80)")
    ratio_rule = _RATIOS.get(company.short)
    if ratio_rule:
        num_k, den_k = ratio_rule
        num, den = finals.get(num_k), finals.get(den_k)
        band = _ratio_band(series, num_k, den_k)
        if num and den and band:
            lo, hi = band
            r = num / den
            rep.add(f"{company.short}: {num_k}/{den_k} conversion ratio", lo <= r <= hi,
                    f"ratio {r:.3f}, history-derived band {lo:.3f}-{hi:.3f}")

    if red_team and llm.available_providers():
        _red_team(company, target, finals, series, rep, log)

    for c in rep.checks:
        log.log("validate", f"{company.short} [{c.status.upper()}] {c.name}: {c.detail}")
    return rep


_RED_SYSTEM = """You are a hostile reviewer hunting for unit mistakes in an earnings forecast.
Respond with JSON only:
{"objections": [{"unit_error": true|false, "issue": "..."}]}
unit_error is true ONLY for a wrong unit or scale in the FORECAST itself:
billions vs millions, pounds vs pence, fraction vs percentage points, or a
forecast magnitude impossible for the metric. Plausibility opinions, sequential
trends and tiny rounding differences in the history are unit_error false."""


def _red_team(company: Company, target: str, finals: dict[str, float],
              series: Series, rep: ValidationReport, log: RunLog) -> None:
    provider = llm.available_providers()[0]
    hist = {k: dict(sorted(s.items())[-6:]) for k, s in series.items()}
    metrics_desc = "\n".join(f"- {m.key}: {m.label}, units {m.units}"
                             for m in company.metrics)
    try:
        resp = llm.chat_json(provider, _RED_SYSTEM, f"""Company {company.name}, forecast period {target}.
Metrics and required workbook units:
{metrics_desc}

Recent reported history (same units): {hist}

Proposed final forecasts: {finals}

List objections.""", max_tokens=1200)
        objections = resp.get("objections", [])
        for o in objections:
            # advisory only. It earned a real catch (an over-fitted Hays EPS)
            # but also blocked correct values — flagging 0.75pp comparable
            # sales as a possible fraction/percent mix-up when it matched the
            # history exactly. Deterministic gates decide; the model advises.
            rep.add(f"red-team: {o.get('issue', '?')[:70]}",
                    not bool(o.get("unit_error")), str(o.get("issue")),
                    warn_only=True)
        if not objections:
            rep.add("red-team review", True, f"no objections ({provider})")
    except llm.LLMError as e:
        rep.add("red-team review", True, f"skipped, model unavailable: {e}", warn_only=True)
        log.log("validate", f"{company.short} red-team skipped: {e}")
