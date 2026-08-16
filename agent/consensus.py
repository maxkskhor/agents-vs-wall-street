"""Optional live consensus anchor via provider web-search tools.

Public analyst consensus is what the accuracy prize scores us against, so a
timestamped, cited snapshot of it is a legitimate public-information input
(RULES.md allows public research during the event). This step is strictly
optional: results are cached to research/consensus-<CO>.json, and when the
network or tools fail the pipeline simply runs un-anchored.
"""

from __future__ import annotations

import datetime as dt
import json

from . import llm
from .config import RESEARCH, Company
from .runlog import RunLog


def consensus_path(company: Company):
    return RESEARCH / f"consensus-{company.short}.json"


def load_consensus(company: Company) -> dict | None:
    p = consensus_path(company)
    if p.exists():
        return json.loads(p.read_text())
    return None


def fetch_consensus(company: Company, log: RunLog) -> dict | None:
    metrics_desc = "; ".join(f"{m.label} in {m.units}" for m in company.metrics)
    prompt = f"""Search the public web for the CURRENT Wall Street analyst consensus estimates for
{company.name} ({company.ticker}) for fiscal period {company.period}, due to be
reported in the next couple of weeks (today is {dt.date.today()}).

Metrics needed: {metrics_desc}.
Percentages as percentage points; Hays EPS in pence; money in millions.

Return ONLY JSON:
{{"<metric key>": {{"value": number|null, "source": "site/page name", "as_of": "YYYY-MM-DD"}}}}
using metric keys: {", ".join(m.key for m in company.metrics)}.
Use null when you cannot find a credible figure. Prefer figures dated within
the last month from reputable financial sites."""

    data = None
    for provider in llm.available_providers():
        try:
            data = _fetch_with(provider, prompt)
            if data:
                break
        except Exception as e:  # noqa: BLE001 - consensus is best-effort
            log.log("consensus", f"{company.short} via {provider} failed: {e}")
    if not data:
        log.log("consensus", f"{company.short}: no consensus available (running un-anchored)")
        return None

    keys = {m.key for m in company.metrics}
    clean = {k: v for k, v in data.items()
             if k in keys and isinstance(v, dict) and v.get("value") is not None}
    snapshot = {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "period": company.period, **clean}
    RESEARCH.mkdir(exist_ok=True)
    consensus_path(company).write_text(json.dumps(snapshot, indent=1))
    log.log("consensus", f"{company.short}: {[(k, v['value']) for k, v in clean.items()]}")
    return snapshot


def _fetch_with(provider: str, prompt: str) -> dict | None:
    llm.load_env()
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=llm.default_model("anthropic"), max_tokens=4000,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
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
