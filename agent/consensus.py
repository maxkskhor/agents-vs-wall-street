"""Optional live consensus anchor via provider web-search tools.

Public analyst consensus is what the accuracy prize scores us against, so a
timestamped, cited snapshot of it is a legitimate public-information input
(RULES.md allows public research during the event).

External evidence gets gated exactly like extracted evidence. Providers
disagree and single-source numbers turn out to be unreproducible, so we:
  * collect each source separately with its own value, date and URL,
  * reject anything dated in the future (every target period reports after
    today, so a "consensus" dated later than today is post-release leakage —
    a failure mode our own research track observed twice),
  * reject full-year figures quoted against a quarterly target,
  * require at least two independent sources agreeing within tolerance before
    the number is allowed to anchor anything, and take their median.

A single uncorroborated source is recorded in the snapshot but never used.
That rule exists because one run produced a lone 4.87 for Home Depot adjusted
EPS that four independent providers later contradicted (4.62-4.73).
"""

from __future__ import annotations

import datetime as dt
import json
import statistics

from . import llm, periods
from .config import RESEARCH, Company
from .runlog import RunLog

# corroboration tolerance: two sources "agree" within this relative distance.
# 3% proved too loose on EPS-scale numbers — it let a lone outlier join the
# cluster and drag the anchor with it.
REL_TOL = 0.015
PCT_TOL_PP = 0.75

# independent web-search passes pooled per company before gating
SEARCH_PASSES = 3


def consensus_path(company: Company):
    return RESEARCH / f"consensus-{company.short}.json"


def load_consensus(company: Company) -> dict | None:
    p = consensus_path(company)
    if p.exists():
        return json.loads(p.read_text())
    return None


def _prompt(company: Company, today: dt.date) -> str:
    kind = periods.parse(company.period)[1]
    period_word = {"Q": "quarterly", "H": "half-year", "Y": "full-year"}[kind]
    metrics_desc = "\n".join(
        f'- key "{m.key}": {m.label}, in {m.units}'
        + (f"\n    DEFINITION: {m.definition}" if m.definition else "")
        for m in company.metrics)
    return f"""{company.name} ({company.ticker}) reports fiscal period {company.period}
in the coming days. TODAY IS {today.isoformat()} — the results are NOT out yet.

Find the CURRENT Wall Street analyst consensus estimates for this {period_word}
period, for these metrics:
{metrics_desc}

CRITICAL RULES:
- Report each source SEPARATELY with its own number. NEVER average across providers.
- Record each source's publication/as-of date. EXCLUDE anything dated after
  {today.isoformat()} — such content post-dates the release and is contaminated.
- State the basis of each figure: "{period_word} adjusted", "{period_word} GAAP",
  "full-year", or "unclear". Do not present a full-year figure as a {period_word} one.
- Percentages in percentage points; money in millions; Hays EPS in pence.
- ONLY analyst estimates for the UPCOMING period. Do NOT report the company's
  own guidance or outlook as consensus — that is not a Street estimate.
- Do NOT report a figure for an ALREADY-REPORTED period. If a page shows the
  last reported quarter's actual next to the estimate, take the estimate.
- A consensus compiled by the company itself from named sell-side analysts
  (e.g. a "company-compiled consensus" investor-relations page) IS acceptable
  and should have basis "company-compiled consensus".
- Where a DEFINITION is given, the figure MUST match that definition. If you
  cannot confirm the provider is quoting that exact measure, omit the metric.
- If no credible figure exists for a metric, omit it. Absence is a valid answer.

Check as many as load: Zacks, Nasdaq, MarketBeat, Investing.com, Barchart,
StockAnalysis, Yahoo Finance, TipRanks, Simply Wall St, Visible Alpha.

Return ONLY JSON:
{{"<metric key>": [{{"source": "...", "value": <number>, "basis": "...",
                    "as_of": "YYYY-MM-DD", "url": "..."}}, ...]}}"""


_GUIDANCE_WORDS = ("company guidance", "company outlook", "not street",
                   "company forecast", "issued guidance")
_COMPILED_WORDS = ("company-compiled", "company compiled", "analysts' consensus",
                   "analysts consensus", "compiled consensus")


def _usable(entries: list[dict], metric_kind: str, today: dt.date,
            period_word: str,
            reported: dict[str, float] | None = None,
            ) -> tuple[float | None, list[dict], list[dict]]:
    """Returns (anchor value or None, accepted entries, rejected entries).

    `reported` is the already-reported history for this metric: a "consensus"
    equal to a period the company has already published is almost always the
    last actual scraped off the same page, not an estimate for the target.
    """
    accepted, rejected = [], []
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("value"), (int, float)):
            rejected.append({**(e if isinstance(e, dict) else {"raw": e}),
                             "reason": "no numeric value"})
            continue
        as_of = str(e.get("as_of", ""))
        try:
            d = dt.date.fromisoformat(as_of)
        except ValueError:
            rejected.append({**e, "reason": f"unparsable as_of {as_of!r}"})
            continue
        if d > today:
            rejected.append({**e, "reason": "dated in the future — post-release leakage"})
            continue
        blob = (str(e.get("basis", "")) + " " + str(e.get("source", ""))).lower()
        if "full-year" in blob and period_word != "full-year":
            rejected.append({**e, "reason": "full-year figure against a shorter target period"})
            continue
        if any(w in blob for w in _GUIDANCE_WORDS):
            rejected.append({**e, "reason": "company guidance, not a Street estimate"})
            continue
        v = float(e["value"])
        hit = _matches_reported(v, metric_kind, reported)
        if hit:
            rejected.append({**e, "reason": f"equals already-reported {hit} — "
                                            f"looks like an actual, not an estimate"})
            continue
        accepted.append(e)

    # a consensus the company itself compiles from named analysts is already an
    # aggregate, so it does not need a second corroborating source
    compiled = [e for e in accepted
                if any(w in (str(e.get("basis", "")) + " " +
                             str(e.get("source", ""))).lower() for w in _COMPILED_WORDS)]
    if compiled:
        return statistics.median(e["value"] for e in compiled), accepted, rejected

    if len(accepted) < 2:
        return None, accepted, rejected

    # median over every accepted source: robust to a single outlier by
    # construction. Then require the median itself to be corroborated, so a
    # set of mutually-contradictory numbers cannot masquerade as a consensus.
    vals = [e["value"] for e in accepted]
    med = statistics.median(vals)
    tol = PCT_TOL_PP if metric_kind == "percent" else max(abs(med) * REL_TOL, 1e-9)
    if sum(1 for v in vals if abs(v - med) <= tol) < 2:
        return None, accepted, rejected
    return med, accepted, rejected


def _matches_reported(value: float, metric_kind: str,
                      reported: dict[str, float] | None) -> str | None:
    for period, rv in (reported or {}).items():
        tol = PCT_TOL_PP if metric_kind == "percent" else max(abs(rv) * REL_TOL, 1e-9)
        if abs(value - rv) <= tol:
            return period
    return None


def fetch_consensus(company: Company, log: RunLog,
                    series: dict[str, dict[str, float]] | None = None) -> dict | None:
    today = dt.date.today()
    kind = periods.parse(company.period)[1]
    period_word = {"Q": "quarterly", "H": "half-year", "Y": "full-year"}[kind]

    # a single web-search pass returns wildly variable coverage (one run found
    # six sources for the same metric, the next found none), so pool several
    # independent passes and dedupe. Corroboration is the whole point here.
    data: dict[str, list] = {}
    for provider in llm.available_providers():
        for attempt in range(SEARCH_PASSES):
            try:
                got = _fetch_with(provider, _prompt(company, today))
            except Exception as e:  # noqa: BLE001 - consensus is best-effort
                log.log("consensus", f"{company.short} via {provider} pass {attempt}: {e}")
                continue
            for key, entries in (got or {}).items():
                if isinstance(entries, dict):
                    entries = [entries]
                data.setdefault(key, []).extend(
                    e for e in entries if isinstance(e, dict))
    # dedupe on (source, rounded value): the same provider seen twice is still
    # one source and must not count as its own corroboration
    for key, entries in data.items():
        seen, unique = set(), []
        for e in entries:
            sig = (str(e.get("source", "")).strip().lower()[:40],
                   round(float(e["value"]), 4) if isinstance(e.get("value"), (int, float)) else None)
            if sig in seen:
                continue
            seen.add(sig)
            unique.append(e)
        data[key] = unique
    if not data:
        log.log("consensus", f"{company.short}: no consensus available (running un-anchored)")
        return None

    snapshot: dict = {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                      "period": company.period, "gated_on_date": today.isoformat()}
    for metric in company.metrics:
        entries = data.get(metric.key) or []
        if isinstance(entries, dict):
            entries = [entries]
        value, accepted, rejected = _usable(
            entries, metric.kind, today, period_word,
            (series or {}).get(metric.key))
        snapshot[metric.key] = {
            "value": value, "sources": accepted, "rejected": rejected,
            "corroboration": len(accepted),
            "usable": value is not None,
            "why": ("median of agreeing sources" if value is not None else
                    "not used: fewer than two independent sources agreed")}
        log.log("consensus", f"{company.short}/{metric.key}: anchor={value} "
                             f"from {len(accepted)} accepted / {len(rejected)} rejected "
                             f"({[e.get('source') for e in accepted]})")

    RESEARCH.mkdir(exist_ok=True)
    consensus_path(company).write_text(json.dumps(snapshot, indent=1))
    return snapshot


def anchor_for(consensus: dict | None, metric_key: str,
               metric=None) -> float | None:
    """The only sanctioned way to read an anchor: usable entries only."""
    if not consensus:
        return None
    if metric is not None and not getattr(metric, "consensus_usable", True):
        return None
    entry = consensus.get(metric_key)
    if not isinstance(entry, dict) or not entry.get("usable"):
        return None
    v = entry.get("value")
    return float(v) if isinstance(v, (int, float)) else None


def _fetch_with(provider: str, prompt: str) -> dict | None:
    llm.load_env()
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=llm.default_model("anthropic"), max_tokens=6000,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
            messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return llm.parse_json(text)
    if provider == "openai":
        import openai
        client = openai.OpenAI()
        resp = client.responses.create(
            model=llm.default_model("openai"),
            tools=[{"type": "web_search"}],
            input=prompt)
        return llm.parse_json(resp.output_text)
    return None
