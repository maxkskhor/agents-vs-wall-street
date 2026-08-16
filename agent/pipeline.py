"""Per-company orchestration: retrieve -> extract -> estimate -> combine ->
validate -> write workbook + audit. Every stage leaves a JSON artifact under
runs/<run_id>/<CO>/ so any number can be traced back offline."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, asdict, field

from . import llm
from .config import RUNS, Company
from .corpus import results_docs, search
from .consensus import anchor_for, fetch_consensus, load_consensus
from .engine import combine
from .estimators import Estimate, derived, guidance, llm_analyst, statistical
from .extract import build_fact_table, guidance_facts, reported_series
from .audit import write_audit
from .runlog import RunLog
from .validate import validate
from .workbook import write_workbook

EXTRACT_DOCS = 16     # newest results-flavoured filings fed to extraction


@dataclass
class CompanyResult:
    company: str
    target: str
    final: dict[str, float] = field(default_factory=dict)     # metric label -> value
    finals_by_key: dict[str, float] = field(default_factory=dict)
    validation_ok: bool = True


def run_company(company: Company, log: RunLog, run_id: str,
                offline: bool = False, asof: dt.date | None = None,
                write: bool = True) -> CompanyResult:
    out_dir = RUNS / run_id / company.short
    out_dir.mkdir(parents=True, exist_ok=True)
    target = company.period

    providers = llm.available_providers()
    if not providers:
        raise RuntimeError("no API keys configured — create .env (see .env.example)")
    extract_provider = providers[0]

    docs = results_docs(company, asof=asof, limit=EXTRACT_DOCS)
    log.log("retrieve", f"{company.short}: {len(docs)} results docs "
                        f"({docs[0].published} back to {docs[-1].published})")

    facts, rejected = build_fact_table(company, docs, log, extract_provider)
    series = reported_series(company, facts, asof=asof)
    gfacts = guidance_facts(company, facts, asof=asof)
    (out_dir / "facts.json").write_text(json.dumps(
        {"facts": [asdict(f) for f in facts], "rejected": rejected}, indent=1))
    log.log("facts", f"{company.short}: {len(facts)} grounded facts "
                     f"({len(rejected)} rejected by grounding), "
                     f"series sizes {[f'{k}:{len(v)}' for k, v in series.items()]}, "
                     f"{len(gfacts)} guidance/preannounce")

    consensus = None
    if not offline and asof is None:
        consensus = load_consensus(company) or fetch_consensus(company, log, series)

    # raw outlook lines from the newest documents, handed to the analyst as
    # extra cited evidence (catches guidance shapes extraction cannot type,
    # e.g. Deere's per-segment sales-growth x margin outlook)
    newest = docs[0].published
    snippets = [f"[{d.doc_id}] {line}"
                for d, _, line in search(company, r"outlook|forecast|guidance|we expect", asof=asof)
                if (newest - d.published).days <= 120][:12]
    extra_evidence = "\n".join(snippets)[:5000]

    finals: dict[str, float] = {}
    lineage: dict[str, dict] = {}
    # EPS metrics may be derived from an already-forecast profit metric, so
    # order the work by dependency rather than by workbook row
    ordered = sorted(company.metrics,
                     key=lambda m: (bool(m.derive_from), m.kind == "eps"))
    for metric in ordered:
        ests: list[Estimate] = []
        d = derived(metric, series, finals, target)
        if d:
            ests.append(d)
        s = statistical(metric, series[metric.key], target)
        if s:
            ests.append(s)
        g = guidance(metric, series[metric.key], gfacts, target)
        if g:
            ests.append(g)
        # no guidance route -> the analyst carries more weight, so buy
        # stability with a larger sample count there
        n_samples = 5 if g else 8
        ests.extend(llm_analyst(company, metric, series[metric.key], gfacts,
                                target, consensus, log,
                                samples_per_provider=n_samples,
                                extra_evidence=extra_evidence))
        log.log("estimate", f"{company.short}/{metric.key}: " + "; ".join(
            f"{e.method}={e.value:.4g}" for e in ests))
        cval = anchor_for(consensus, metric.key, metric)
        finals[metric.key], lineage[metric.key] = combine(company, metric, ests, cval)
        log.log("combine", f"{company.short}/{metric.key}: final={finals[metric.key]}")

    (out_dir / "decision.json").write_text(json.dumps(
        {"target": target, "finals": finals, "lineage": lineage,
         "consensus": consensus}, indent=1, default=str))

    report = validate(company, target, finals, series, lineage, log)
    (out_dir / "validation.json").write_text(json.dumps(
        [asdict(c) for c in report.checks], indent=1))
    write_audit(company, target, finals, lineage, series, report, out_dir)

    if not report.ok:
        raise RuntimeError(
            f"{company.short}: validation FAILED — workbook not written. "
            f"See {out_dir / 'audit.md'}")

    result = CompanyResult(
        company=company.short, target=target,
        final={m.label: finals[m.key] for m in company.metrics},
        finals_by_key=finals, validation_ok=report.ok)
    if write:
        path = write_workbook(company, result.final)
        log.log("workbook", f"{company.short}: wrote {path}")
    return result
