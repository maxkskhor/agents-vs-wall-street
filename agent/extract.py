"""Per-document fact extraction with verbatim quote grounding.

The LLM's only job here is transcription: pull reported values, prior-year
comparatives, guidance ranges and pre-announcements for the three challenge
metrics out of ONE document at a time, each with a supporting quote. A fact is
kept only if (a) the quote actually appears in the document and (b) the value
appears in the quote (allowing $41.8bn ~ 41,765 USDm style unit rounding).
Facts are cached per document, so the fact table is assembled once and the
backtest can time-slice it for free.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, asdict

from . import llm
from .config import CACHE, Company
from .corpus import Doc
from .runlog import RunLog

PROMPT_VERSION = "v5"

MAX_DOC_CHARS = 110_000


@dataclass
class Fact:
    metric: str            # metric key, e.g. "net_sales"
    fact_type: str         # "reported" | "guidance" | "preannounce"
    period: str            # canonical, e.g. "FY2026Q1", "FY2026", "FY2026H1"
    value: float | None    # point value in workbook units (None if pure range)
    low: float | None
    high: float | None
    units: str
    doc_id: str
    published: str
    quote: str

    @property
    def mid(self) -> float:
        if self.value is not None:
            return self.value
        return (self.low + self.high) / 2  # type: ignore[operator]


_SYSTEM = """You are a meticulous financial-data extractor. You copy explicitly stated
figures out of one company document into JSON. Mechanical unit conversion is
expected (e.g. "$41.8 billion" -> 41800 when the target unit is USD millions);
inventing, estimating or deriving figures that are not stated is forbidden.
Extract generously: when in doubt whether a stated figure matches a target
metric, include it — a separate grounding step will filter."""


def _user_prompt(company: Company, doc: Doc, text: str) -> str:
    metrics_desc = "\n".join(
        f'- key "{m.key}": {m.label} (workbook units: {m.units}; phrases: {", ".join(m.aliases)})'
        for m in company.metrics)
    return f"""Document from {company.name} ({company.ticker}), published {doc.published},
type {doc.doctype}, file {doc.doc_id}.

Fiscal-calendar convention: {company.fiscal_note}

Target metrics:
{metrics_desc}

Extract every explicit statement of these metrics in the document:
1. reported results for any fiscal period (including prior-year comparatives and
   any tables of historical periods),
2. forward guidance or outlook ranges ("we expect", "guidance", "outlook"),
3. pre-announcements of results not yet formally reported (trading updates).

Rules:
- Values must be converted to the workbook units shown above (e.g. "$41.8 billion"
  with units USDm -> 41800; "13.5 billion" USDm -> 13500; percentages as points:
  "0.6%" -> 0.6; pence: "6.2p" -> 6.2). Copy the precise table figure when both a
  rounded prose figure and a precise table figure exist (prefer the table row).
- period must be canonical using the company's OWN fiscal labels:
  quarters "FY2026Q1", half-years "FY2026H1", full years "FY2026".
- For a growth-rate guidance statement that is relative (e.g. "sales growth of
  2.5% to 4.5%"), DO NOT convert to absolute values; instead record it with
  units "% growth" and metric key of the metric it refers to, fact_type
  "guidance", low/high as the percentage bounds. "Approximately flat" means 0:
  "to grow approximately flat to 4.0% from $14.69" -> units "% growth", low 0,
  high 4.0 (never record the prior-year base as the guidance value).
- Guidance stated as "X plus or minus Y" (e.g. "revenue of $3.0 billion,
  +/-$100 million"): record low = X-Y and high = X+Y in workbook units.
- Accounting negatives use parentheses: "(0.3)%" means -0.3.
- Figures reported in thousands (e.g. "$2,880,348" thousands) must be converted
  to millions (2880.348) when the workbook unit is millions.
- COMPANY-TOTAL (Group) figures only. Skip regional, country, divisional,
  sector or business-line breakdowns ("Germany net fees", "Temp & Contracting",
  "UK&I", "Private sector") — UNLESS the metric itself names a segment (e.g.
  Production & Precision Ag operating profit, which IS that segment's figure).
- Record LEVELS, never changes: "an increase of $1.8 billion" is a change, not
  a value of the metric. Growth-rate guidance is the only exception and must
  use units "% growth".
- quote: copy VERBATIM the sentence or table row containing the number
  (max ~300 chars). The value must be visible inside the quote.
- Do not invent facts. Skip vague statements without numbers.

Return ONLY a JSON array of objects:
{{"metric": key, "fact_type": "reported"|"guidance"|"preannounce",
  "period": "FY2026Q1", "value": number|null, "low": number|null,
  "high": number|null, "units": "as-recorded units", "quote": "..."}}
Return [] if nothing matches.

DOCUMENT TEXT:
<<<
{text}
>>>"""


_NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def _norm_ws(s: str) -> str:
    return re.sub(r"[\s ]+", " ", s).strip().lower()


def _quote_in_doc(quote: str, text: str) -> bool:
    q, t = _norm_ws(quote), _norm_ws(text)
    if q in t:
        return True
    # tolerate small OCR/spacing drift: require the longest 60-char chunk
    if len(q) > 60:
        mid = len(q) // 2
        return q[:60] in t or q[mid - 30:mid + 30] in t or q[-60:] in t
    return False


def _value_in_quote(value: float, quote: str, units: str = "") -> bool:
    growthish = "%" in units or "growth" in units.lower()
    if value == 0 and growthish and "flat" in quote.lower():
        return True   # "approximately flat" = 0% growth
    nums = [float(n.replace(",", "")) for n in _NUM_RE.findall(quote)]
    if not nums:
        return False
    for n in nums:
        # accounting negatives appear as "(0.3)%" so try both signs; scale
        # candidates cover billions->millions (x1000) and thousands->millions
        # (/1000), which ADI's statements use
        for signed in (n, -n):
            for cand in (signed, signed * 1000, signed / 1000,
                         signed * 100, signed / 100):
                if abs(cand - value) <= max(abs(value) * 0.006, 0.011):
                    return True
    return False


def _ground(fact: dict, text: str, metric) -> str | None:
    """Return rejection reason or None if the fact is grounded."""
    quote = fact.get("quote") or ""
    units = str(fact.get("units", ""))
    if not _quote_in_doc(quote, text):
        return "quote not found in document"

    value, low, high = fact.get("value"), fact.get("low"), fact.get("high")
    if value is None and (low is None or high is None):
        return "no value and no complete range"

    if value is not None and not _value_in_quote(float(value), quote, units):
        return f"value={value} not present in quote"
    if value is None:
        lo, hi = float(low), float(high)
        direct = (_value_in_quote(lo, quote, units)
                  and _value_in_quote(hi, quote, units))
        # "X ± Y" ranges: the quote shows the midpoint and the half-width
        pm = (_value_in_quote((lo + hi) / 2, quote, units)
              and _value_in_quote((hi - lo) / 2, quote, units))
        if not (direct or pm):
            return f"range {lo}..{hi} not present in quote (as bounds or mid±width)"

    # attribution check: money metrics must mention the metric by name in the
    # quote, otherwise a nearby number gets credited to the wrong metric
    if metric.kind == "money":
        blob = _norm_ws(quote)
        if not any(_norm_ws(a) in blob for a in metric.aliases):
            return "quote does not mention the metric (attribution)"
    return None


_PERIOD_RE = re.compile(r"^FY\d{4}(Q[1-4]|H[12])?$")


def extract_doc_facts(company: Company, doc: Doc, log: RunLog,
                      provider: str) -> tuple[list[Fact], list[dict]]:
    """Returns (grounded facts, rejected raw facts with reasons). Cached."""
    import hashlib

    text = doc.text()[:MAX_DOC_CHARS]
    user = _user_prompt(company, doc, text)
    ph = hashlib.sha256((_SYSTEM + user).encode()).hexdigest()[:10]
    cache = CACHE / "facts"
    cache.mkdir(parents=True, exist_ok=True)
    cp = cache / f"{PROMPT_VERSION}-{ph}__{provider}__{doc.doc_id}.json"
    if cp.exists():
        data = json.loads(cp.read_text())
        return [Fact(**f) for f in data["facts"]], data["rejected"]

    raw = llm.chat_json(provider, _SYSTEM, user, max_tokens=8000,
                        model=llm.extract_model(provider))
    if not isinstance(raw, list):
        raw = []

    by_key = {m.key: m for m in company.metrics}
    facts: list[Fact] = []
    rejected: list[dict] = []
    for f in raw:
        try:
            if f.get("metric") not in by_key:
                rejected.append({**f, "reason": "unknown metric"})
                continue
            if not _PERIOD_RE.match(str(f.get("period", ""))):
                rejected.append({**f, "reason": f"bad period {f.get('period')!r}"})
                continue
            if f.get("fact_type") not in ("reported", "guidance", "preannounce"):
                rejected.append({**f, "reason": "bad fact_type"})
                continue
            reason = _ground(f, text, by_key[f["metric"]])
            if reason:
                rejected.append({**f, "reason": reason})
                continue
            facts.append(Fact(
                metric=f["metric"], fact_type=f["fact_type"], period=f["period"],
                value=None if f.get("value") is None else float(f["value"]),
                low=None if f.get("low") is None else float(f["low"]),
                high=None if f.get("high") is None else float(f["high"]),
                units=str(f.get("units", "")), doc_id=doc.doc_id,
                published=doc.published.isoformat(), quote=f["quote"]))
        except (TypeError, ValueError, KeyError) as e:
            rejected.append({**f, "reason": f"parse error: {e}"})

    cp.write_text(json.dumps(
        {"facts": [asdict(f) for f in facts], "rejected": rejected}, indent=1))
    log.log("extract", f"{company.short} {doc.doc_id}: {len(facts)} facts, "
                       f"{len(rejected)} rejected")
    return facts, rejected


def build_fact_table(company: Company, docs: list[Doc], log: RunLog,
                     provider: str) -> tuple[list[Fact], list[dict]]:
    from concurrent.futures import ThreadPoolExecutor

    all_facts: list[Fact] = []
    all_rejected: list[dict] = []

    def one(doc: Doc):
        try:
            return extract_doc_facts(company, doc, log, provider)
        except llm.LLMError as e:
            log.log("extract", f"{company.short} {doc.doc_id}: EXTRACTION FAILED {e}")
            return [], []

    with ThreadPoolExecutor(max_workers=4) as pool:
        for facts, rejected in pool.map(one, docs):
            all_facts.extend(facts)
            all_rejected.extend(rejected)
    return all_facts, all_rejected


def reported_series(company: Company, facts: list[Fact],
                    asof: dt.date | None = None) -> dict[str, dict[str, float]]:
    """metric key -> {canonical period -> value}. Later documents win (restatements)."""
    candidates: dict[tuple[str, str], list[tuple[tuple, float]]] = {}
    for f in facts:
        if f.fact_type != "reported" or f.value is None:
            continue
        if asof is not None and dt.date.fromisoformat(f.published) > asof:
            continue
        blob = (f.units + " " + f.quote).lower()
        precise = 0 if ("billion" in blob or "derived" in blob) else 1
        candidates.setdefault((f.metric, f.period), []).append(
            ((f.published, precise), f.value))

    out: dict[str, dict[str, float]] = {m.key: {} for m in company.metrics}
    for (metric, period), cands in candidates.items():
        # a true value is restated across many documents; an extraction slip
        # appears once — pick the largest agreement cluster (1% tolerance),
        # then the newest / most precise member of it
        clusters: list[list[tuple[tuple, float]]] = []
        for rank, v in cands:
            for cl in clusters:
                if abs(v - cl[0][1]) <= max(abs(cl[0][1]) * 0.01, 0.011):
                    cl.append((rank, v))
                    break
            else:
                clusters.append([(rank, v)])
        best = max(clusters, key=lambda cl: (len(cl), max(r for r, _ in cl)))
        out[metric][period] = max(best, key=lambda rv: rv[0])[1]
    return out


def guidance_facts(company: Company, facts: list[Fact],
                   asof: dt.date | None = None) -> list[Fact]:
    keep = []
    for f in facts:
        if f.fact_type not in ("guidance", "preannounce"):
            continue
        if asof is not None and dt.date.fromisoformat(f.published) > asof:
            continue
        keep.append(f)
    keep.sort(key=lambda f: f.published, reverse=True)
    return keep
