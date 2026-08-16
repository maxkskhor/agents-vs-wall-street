"""Three independent estimators per metric.

Each returns an Estimate whose `value` is COMPUTED here in plain arithmetic
from cited inputs — including the LLM-analyst estimator, where the model may
only propose a cited base figure plus itemised adjustments; the final number is
recomputed deterministically from those parts. Estimators abstain (return None)
rather than guess when their inputs are missing.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from . import llm, periods
from .config import Company, Metric
from .extract import Fact
from .runlog import RunLog

Series = dict[str, float]          # canonical period -> value


@dataclass
class Estimate:
    metric: str
    method: str                    # "statistical" | "guidance" | "llm_analyst"
    value: float
    inputs: dict = field(default_factory=dict)   # assumptions + citations (lineage)


# ---------------------------------------------------------------- statistical

def _yoy_pairs(series: Series, target: str, max_pairs: int = 4):
    """Latest (current, prior-year) pairs strictly before the target period."""
    fy, kind, n = periods.parse(target)
    pairs = []
    if kind == "Q":
        p = target
        for _ in range(12):
            p = periods.shift_quarters(p, -1)
            prior = periods.prior_year(p)
            if p in series and prior in series:
                pairs.append((p, series[p], prior, series[prior]))
            if len(pairs) >= max_pairs:
                break
    else:
        for y in range(fy - 1, fy - 5, -1):
            cur, prior = periods.fmt(y, kind, n), periods.fmt(y - 1, kind, n)
            if cur in series and prior in series:
                pairs.append((cur, series[cur], prior, series[prior]))
            if len(pairs) >= max_pairs - 1:
                break
    return pairs


def statistical(metric: Metric, series: Series, target: str) -> Estimate | None:
    base_period = periods.prior_year(target)
    base = series.get(base_period)
    if base is None:
        return None
    pairs = _yoy_pairs(series, target)
    if metric.kind == "percent":
        deltas = [cur - prior for _, cur, _, prior in pairs]
        step = statistics.median(deltas) if deltas else 0.0
        value = base + step
        how = f"prior-year level {base} + median YoY delta {step:+.2f}pp"
    else:
        growths = [cur / prior - 1 for _, cur, _, prior in pairs if prior]
        g = statistics.median(growths) if growths else 0.0
        value = base * (1 + g)
        how = f"prior-year value {base} x (1 + median YoY growth {g:+.3%})"
    return Estimate(metric.key, "statistical", value, {
        "base_period": base_period, "base_value": base,
        "yoy_pairs": [{"period": p, "value": v, "prior": pv} for p, v, _, pv in pairs],
        "formula": how})


# ------------------------------------------------------------------ guidance

def _pick_guidance(metric: Metric, gfacts: list[Fact], target: str,
                   series: Series) -> Fact | None:
    """Newest guidance/preannounce fact for this metric aimed at the target
    period or the target fiscal year. Prefers plausible-scale facts (a stray
    '£15m contribution' must not outrank real guidance), adjusted wording for
    adjusted metrics, pre-announcements over guidance, and newer over older."""
    fy = periods.parse(target)[0]
    cands = [f for f in gfacts
             if f.metric == metric.key and periods.parse(f.period)[0] == fy]
    if not cands:
        return None
    wants_adj = metric.key.startswith(("adj", "preex"))
    prior = series.get(periods.prior_year(target))

    def plausible(f: Fact) -> bool:
        if "growth" in f.units or prior in (None, 0):
            return True
        return 0.4 <= abs(f.mid / prior) <= 2.5

    def score(f: Fact) -> tuple:
        return (
            plausible(f),
            f.period == target,                          # exact period beats FY
            f.published,
            f.fact_type == "preannounce",
            f.value is not None,     # "top of range" point beats the raw range
            (not wants_adj) or ("adjust" in f.quote.lower()
                                or "pre-exceptional" in f.quote.lower()),
        )
    best = max(cands, key=score)
    return best if plausible(best) else None


def guidance(metric: Metric, series: Series, gfacts: list[Fact],
             target: str) -> Estimate | None:
    if periods.parse(target)[1] == "Y" and metric.kind == "money":
        derived = _fy_from_halves(metric, series, gfacts, target)
        if derived is not None:
            return derived
    g = _pick_guidance(metric, gfacts, target, series)
    if g is None:
        return None
    tfy, tkind, tn = periods.parse(target)
    lineage = {"guidance_doc": g.doc_id, "guidance_period": g.period,
               "guidance_units": g.units, "quote": g.quote,
               "fact_type": g.fact_type}

    is_growth = "growth" in g.units
    mid = g.mid

    if not is_growth and g.period == target:
        # direct absolute guidance / pre-announcement for the target period
        lineage["formula"] = f"midpoint of stated {g.fact_type} = {mid}"
        return Estimate(metric.key, "guidance", mid, lineage)

    if not is_growth and g.period != target and tkind == "Q":
        # absolute FY guidance level; percent levels carry over, money needs a
        # seasonal share of the year
        if metric.kind == "percent":
            lineage["formula"] = f"FY guidance level {mid} applied to {target}"
            return Estimate(metric.key, "guidance", mid, lineage)
        share = _seasonal_share(series, target)
        if share is None:
            return None
        value = mid * share["share"]
        lineage.update(share)
        lineage["formula"] = f"FY guidance {mid} x seasonal share {share['share']:.3f}"
        return Estimate(metric.key, "guidance", value, lineage)

    if is_growth:
        gfy = periods.parse(g.period)[0]
        base_prior = periods.prior_year(target)
        if metric.kind == "percent":
            # growth guidance for a percent metric == the expected level in pp
            if tkind == "Q" and periods.parse(g.period)[1] == "Y":
                got = _fy_catchup_percent(series, target, mid)
                if got is not None:
                    lineage.update(got)
                    return Estimate(metric.key, "guidance", got["value"], lineage)
            lineage["formula"] = f"guided level midpoint {mid}pp"
            return Estimate(metric.key, "guidance", mid, lineage)
        base = series.get(base_prior)
        if base is None:
            return None
        if tkind == "Q" and periods.parse(g.period)[1] == "Y":
            got = _fy_catchup_money(series, target, mid)
            if got is not None:
                lineage.update(got)
                return Estimate(metric.key, "guidance", got["value"], lineage)
        value = base * (1 + mid / 100)
        lineage["formula"] = (f"prior-year {base_prior} value {base} x "
                              f"(1 + guided growth midpoint {mid}%)")
        return Estimate(metric.key, "guidance", value, lineage)
    return None


def _fy_from_halves(metric: Metric, series: Series, gfacts: list[Fact],
                    target: str) -> Estimate | None:
    """Hays-style full-year build-up: reported H1 + prior-year H2 scaled by the
    quarterly growth rates that trading updates pre-announce for Q3/Q4."""
    tfy = periods.parse(target)[0]
    h1_cur = series.get(f"FY{tfy}H1")
    fy_prior = series.get(f"FY{tfy - 1}")
    h1_prior = series.get(f"FY{tfy - 1}H1")
    if None in (h1_cur, fy_prior, h1_prior):
        return None
    picks: list[Fact] = []
    for q in (3, 4):
        cands = [f for f in gfacts
                 if f.metric == metric.key and f.period == f"FY{tfy}Q{q}"
                 and "growth" in f.units]
        if cands:
            # reported money is FX-actual, so prefer the actual-basis figure
            # over like-for-like when the update states both
            cands.sort(key=lambda f: ("actual" in f.quote.lower(), f.published),
                       reverse=True)
            picks.append(cands[0])
    if not picks:
        return None
    g = statistics.mean(f.mid for f in picks)
    h2_prior = fy_prior - h1_prior
    value = h1_cur + h2_prior * (1 + g / 100)
    return Estimate(metric.key, "guidance", value, {
        "formula": (f"reported H1 {h1_cur} + prior-year H2 {h2_prior:.1f} x "
                    f"(1 + pre-announced H2 growth {g:.1f}%)"),
        "h2_growth_quotes": [{"period": f.period, "growth": f.mid,
                              "doc": f.doc_id, "quote": f.quote[:200]}
                             for f in picks],
        "fact_type": "preannounce", "guidance_doc": picks[-1].doc_id,
        "quote": picks[-1].quote})


def _seasonal_share(series: Series, target: str) -> dict | None:
    """Median historical share of the target quarter in its fiscal year."""
    tfy, _, tn = periods.parse(target)
    shares = []
    for y in range(tfy - 1, tfy - 4, -1):
        qs = periods.quarters_of(y)
        if all(q in series for q in qs):
            total = sum(series[q] for q in qs)
            if total:
                shares.append(series[periods.fmt(y, "Q", tn)] / total)
    if not shares:
        return None
    return {"share": statistics.median(shares), "share_years_used": len(shares)}


def _fy_catchup_money(series: Series, target: str, growth_mid_pct: float) -> dict | None:
    """FY growth guidance + already-reported quarters -> implied target quarter."""
    tfy, _, tn = periods.parse(target)
    prior_qs = periods.quarters_of(tfy - 1)
    if not all(q in series for q in prior_qs):
        return None
    prior_total = sum(series[q] for q in prior_qs)
    fy_target_total = prior_total * (1 + growth_mid_pct / 100)
    reported = {q: series[q] for q in periods.quarters_of(tfy)[:tn - 1] if q in series}
    if len(reported) != tn - 1:
        return None
    remaining = fy_target_total - sum(reported.values())
    prior_remaining = sum(series[q] for q in prior_qs[tn - 1:])
    if not prior_remaining:
        return None
    value = series[prior_qs[tn - 1]] * remaining / prior_remaining
    return {"value": value,
            "formula": (f"FY{tfy} implied total {fy_target_total:.0f} (prior {prior_total:.0f} "
                        f"x 1+{growth_mid_pct}%), minus reported {sum(reported.values()):.0f}, "
                        f"remaining spread over prior-year remaining quarters"),
            "reported_quarters": reported, "prior_quarters": {q: series[q] for q in prior_qs}}


def _fy_catchup_percent(series: Series, target: str, level_mid: float) -> dict | None:
    tfy, _, tn = periods.parse(target)
    reported = {q: series[q] for q in periods.quarters_of(tfy)[:tn - 1] if q in series}
    if len(reported) != tn - 1:
        return None
    # FY average ~ equal-weight quarter average
    value = (4 * level_mid - sum(reported.values())) / (4 - (tn - 1))
    return {"value": value,
            "formula": (f"FY guided level {level_mid}pp with reported quarters "
                        f"{reported} -> remaining-quarter level"),
            "reported_quarters": reported}


# ------------------------------------------------------------ derived ratio

def derived(metric: Metric, all_series: dict[str, Series], finals: dict[str, float],
            target: str) -> Estimate | None:
    """Derive one metric from another already-forecast metric using the most
    recent observed ratio between them (declared via Metric.derive_from).

    Hays' pre-exceptional EPS is operating profit after fixed interest and tax,
    so the ratio drifts as profit falls — the newest observation is the honest
    one, not the median of a decade.
    """
    src = metric.derive_from
    if not src or src not in finals:
        return None
    num, den = all_series.get(metric.key, {}), all_series.get(src, {})
    shared = sorted(set(num) & set(den))
    if not shared:
        return None
    ref = shared[-1]
    if not den[ref]:
        return None
    ratio = num[ref] / den[ref]
    return Estimate(metric.key, "derived", ratio * finals[src], {
        "formula": (f"forecast {src} {finals[src]} x most-recent {metric.key}/{src} "
                    f"ratio {ratio:.5f} (from {ref}: {num[ref]} / {den[ref]})"),
        "ratio_period": ref, "ratio": ratio, "source_metric": src,
        "source_forecast": finals[src]})


# --------------------------------------------------------------- llm analyst

def _backtest_bias_note(company: Company, metric: Metric) -> str:
    """Empirical finding from our own time-travel backtest, stated to the
    analyst as evidence (e.g. ADI's actuals beat its guide midpoint ~3.5%)."""
    import json as _json
    from .config import CACHE
    p = CACHE / "calibration.json"
    if not p.exists():
        return ""
    bias = _json.loads(p.read_text()).get("guidance_bias", {}).get(
        f"{company.short}/{metric.key}")
    if not bias or bias.get("n", 0) < 3:
        return ""
    b = bias["mean_signed"]
    unit = "percentage points" if metric.kind == "percent" else "relative"
    return (f"Backtest finding (our own time-travel evaluation over {bias['n']} past "
            f"periods): this company's reported {metric.label} differed from a "
            f"guidance-anchored estimate by {b:+.3f} ({unit}) on average — i.e. it "
            f"{'beat' if b > 0 else 'missed'} guidance-based expectations. Weigh this "
            f"pattern when sizing adjustments.")


_ANALYST_SYSTEM = """You are a sell-side equity analyst. You never state a final forecast directly.
You propose (1) a base figure copied from the evidence table and (2) a short
list of itemised adjustments, each with a magnitude and a reason grounded in
the evidence supplied. The final number is computed by the caller as
base + sum of adjustments. Respond with JSON only."""


def _series_table(series: Series) -> str:
    rows = sorted(series.items())
    return "\n".join(f"  {p}: {v}" for p, v in rows[-14:])


def llm_analyst(company: Company, metric: Metric, series: Series,
                gfacts: list[Fact], target: str, consensus: dict | None,
                log: RunLog, samples_per_provider: int = 2,
                extra_evidence: str = "") -> list[Estimate]:
    providers = llm.available_providers()
    if not providers:
        return []
    gtxt = "\n".join(
        f'- [{f.fact_type} {f.period}, {f.doc_id}] "{f.quote}"'
        for f in gfacts if f.metric == metric.key)[:4000] or "  (none extracted)"
    if extra_evidence:
        gtxt += ("\n\nRecent outlook excerpts from the newest filings "
                 "(verbatim, may cover other metrics):\n" + extra_evidence)
    bias = _backtest_bias_note(company, metric)
    if bias:
        gtxt += "\n\n" + bias
    # Deliberately NOT shown the consensus anchor: it is applied once,
    # deterministically, in the engine. Feeding it here too double-counted it
    # and let a mis-defined anchor drag the analyst samples with it, which
    # defeated the gate that is supposed to catch exactly that.
    ctxt = ""
    base_prompt = f"""Company: {company.name} ({company.ticker}). {company.fiscal_note}

Forecast target: {metric.label} ({metric.units}) for {target}.
Enter percentages in percentage points; Hays EPS in pence.

Reported history ({metric.label}, {metric.units}):
{_series_table(series)}

Guidance / pre-announcement evidence:
{gtxt}
{ctxt}

Propose:
{{"base": {{"period": "<period the base is copied from>", "value": <number from history above>,
           "why": "<one line>"}},
 "adjustments": [{{"delta": <signed number in {metric.units}>,
                  "reason": "<one line>",
                  "evidence": "<which quote/period above supports this>"}}],
 "confidence": "low"|"medium"|"high"}}
Use at most 4 adjustments. Base MUST equal one of the history values above."""

    out: list[Estimate] = []
    for provider in providers:
        for k in range(samples_per_provider):
            try:
                resp = llm.chat_json(
                    provider, _ANALYST_SYSTEM,
                    base_prompt + f"\n(sample {k + 1}; think independently)",
                    temperature=0.5, max_tokens=2000)
                base_v = float(resp["base"]["value"])
                # the proposed base must be a real historical value
                if not any(abs(base_v - v) <= max(abs(v) * 0.002, 0.005)
                           for v in series.values()):
                    log.log("analyst", f"{company.short}/{metric.key} {provider}#{k}: "
                                       f"base {base_v} not in history — rejected")
                    continue
                deltas = [float(a["delta"]) for a in resp.get("adjustments", [])]
                value = base_v + sum(deltas)
                out.append(Estimate(metric.key, "llm_analyst", value, {
                    "provider": provider, "sample": k,
                    "base": resp["base"], "adjustments": resp.get("adjustments", []),
                    "confidence": resp.get("confidence"),
                    "formula": f"base {base_v} + adjustments {deltas}"}))
            except (llm.LLMError, KeyError, TypeError, ValueError) as e:
                log.log("analyst", f"{company.short}/{metric.key} {provider}#{k}: {e}")
    return out
