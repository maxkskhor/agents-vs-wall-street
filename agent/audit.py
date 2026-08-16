"""Render the per-company audit trail: evidence -> assumptions -> number."""

from __future__ import annotations

import json
from pathlib import Path

from .config import Company
from .validate import ValidationReport


def write_audit(company: Company, target: str, finals: dict[str, float],
                lineage: dict[str, dict], series: dict[str, dict[str, float]],
                report: ValidationReport, out_dir: Path) -> Path:
    by_key = {m.key: m for m in company.metrics}
    lines: list[str] = []
    w = lines.append
    w(f"# {company.name} — {target} forecast audit trail\n")
    w("| Metric | Units | Final forecast |")
    w("|---|---|---:|")
    for m in company.metrics:
        w(f"| {m.label} | {m.units} | **{finals[m.key]}** |")
    w("")

    for key, lin in lineage.items():
        m = by_key[key]
        w(f"\n## {m.label} ({m.units}) = {lin['final']}\n")
        if "consensus_blend" in lin:
            cb = lin["consensus_blend"]
            w(f"- **Final** = {cb['formula']} = {cb['consensus']} + "
              f"{cb['beta']} × ({lin['ensemble']['value']:.4g} − {cb['consensus']}) "
              f"= {cb['value']:.4g}")
        w(f"- **Ensemble** = {lin['ensemble']['formula']} = "
          f"{lin['ensemble']['value']:.4g} (weights {lin['weights']})")
        for method, d in lin["methods"].items():
            w(f"\n### {method} → {d['value']:.4g}")
            if "formula" in d:
                w(f"- formula: {d['formula']}")
            if "quote" in d:
                w(f"- evidence ({d.get('guidance_doc')}): “{d['quote'][:280]}”")
            if method == "llm_analyst":
                for s in d.get("samples", []):
                    base = s.get("base", {})
                    w(f"- sample [{s.get('provider')}#{s.get('sample')}] "
                      f"base {base.get('value')} ({base.get('period')}) "
                      f"→ {s.get('value'):.4g}")
                    for a in s.get("adjustments", []):
                        w(f"    - {a.get('delta'):+} — {a.get('reason')} "
                          f"[{a.get('evidence', '')[:100]}]")
        hist = dict(sorted(series.get(key, {}).items())[-8:])
        w(f"\n- reported history used: {json.dumps(hist)}")

    w("\n## Validation\n")
    w("| Check | Status | Detail |")
    w("|---|---|---|")
    for c in report.checks:
        w(f"| {c.name} | {c.status.upper()} | {c.detail} |")

    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "audit.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p
