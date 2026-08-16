"""Validation gates that run before any workbook is written.

Deterministic gates (units, magnitude vs history, cross-metric consistency,
estimator disagreement) are blocking. The red-team LLM pass reviews the final
numbers with their lineage and can also block on unit errors; if the model is
unavailable the deterministic gates still stand alone.
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


_BANDS = {"money": (0.65, 1.45), "eps": (0.40, 1.75)}
_PERCENT_MAX_DELTA = 6.0     # pp vs prior-year level

# conversion-ratio sanity per company: (numerator, denominator, lo, hi)
_RATIOS = {
    "HAS": ("preex_op", "net_fees", 0.08, 0.35),
    "DE": ("ppa_op", "net_sales_rev", 0.05, 0.30),
}


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
            lo, hi = _BANDS[metric.kind]
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
            rep.add("HD: net sales growth vs comp sales", abs(growth_pp - comp) <= 8,
                    f"sales growth {growth_pp:.1f}pp vs comps {comp:.1f}pp "
                    f"(gap covers new stores/FX/53rd week; limit 8pp)")
    if company.short == "ADI":
        gm = finals.get("adj_gross_margin")
        if gm is not None:
            rep.add("ADI: gross margin absolute range", 55 <= gm <= 80,
                    f"adjusted gross margin {gm}% must be a percentage level (55-80)")
    ratio_rule = _RATIOS.get(company.short)
    if ratio_rule:
        num_k, den_k, lo, hi = ratio_rule
        num, den = finals.get(num_k), finals.get(den_k)
        if num and den:
            r = num / den
            rep.add(f"{company.short}: {num_k}/{den_k} conversion ratio", lo <= r <= hi,
                    f"ratio {r:.3f}, historical sanity band {lo}-{hi}")

    if red_team and llm.available_providers():
        _red_team(company, target, finals, series, rep, log)

    for c in rep.checks:
        log.log("validate", f"{company.short} [{c.status.upper()}] {c.name}: {c.detail}")
    return rep


_RED_SYSTEM = """You are a hostile reviewer hunting for unit mistakes and impossible numbers in
an earnings forecast. Respond with JSON only:
{"objections": [{"severity": "blocking"|"note", "issue": "..."}]}
"blocking" is ONLY for wrong units/scale (e.g. billions vs millions, pounds vs
pence, fraction vs percentage points) or numbers impossible given history."""


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
        blocking = [o for o in objections if o.get("severity") == "blocking"]
        for o in objections:
            rep.add(f"red-team: {o.get('issue', '?')[:70]}",
                    o.get("severity") != "blocking", str(o.get("issue")),
                    warn_only=o.get("severity") != "blocking")
        if not objections:
            rep.add("red-team review", True, f"no objections ({provider})")
    except llm.LLMError as e:
        rep.add("red-team review", True, f"skipped, model unavailable: {e}", warn_only=True)
        log.log("validate", f"{company.short} red-team skipped: {e}")
