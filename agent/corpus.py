"""Frozen-corpus index, as-of filtering and search.

Documents live under challenge/offline-data/<company>/{filings,call-transcripts,slides}
with filenames like 2026-05-19__hd-us-20260519-q1-8k__1038584.md and YAML
frontmatter carrying published_at, document_type and period.

The as-of date is the backbone of the backtest harness: every retrieval accepts
`asof` and silently hides anything published after it, so the exact same
pipeline can forecast past quarters as if it were run on that day.
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .config import Company

_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Doc:
    path: Path
    company: str          # short code
    published: dt.date
    doctype: str          # filing | call-transcript | slide
    slug: str

    @property
    def doc_id(self) -> str:
        return self.path.name

    def text(self) -> str:
        raw = self.path.read_text(encoding="utf-8", errors="replace")
        return _FRONTMATTER_RE.sub("", raw)


_TYPE_BY_DIR = {"filings": "filing", "call-transcripts": "call-transcript", "slides": "slide"}


@lru_cache(maxsize=8)
def _index_company(folder: str, short: str) -> tuple[Doc, ...]:
    docs: list[Doc] = []
    for sub, doctype in _TYPE_BY_DIR.items():
        d = Path(folder) / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            m = re.match(r"(\d{4}-\d{2}-\d{2})__(.+)__\d+\.md$", p.name)
            if not m:
                continue
            docs.append(Doc(
                path=p, company=short,
                published=dt.date.fromisoformat(m.group(1)),
                doctype=doctype, slug=m.group(2)))
    return tuple(sorted(docs, key=lambda d: d.published))


def index(company: Company, asof: dt.date | None = None) -> list[Doc]:
    docs = list(_index_company(str(company.folder), company.short))
    if asof is not None:
        docs = [d for d in docs if d.published <= asof]
    return docs


def results_docs(company: Company, asof: dt.date | None = None, limit: int = 14) -> list[Doc]:
    """Documents most likely to carry reported headline numbers and guidance:

    results-flavoured filings (8-K press releases, trading updates, prelim/final
    results), newest first. Falls back on slug keywords because doc titles are
    inside the files.
    """
    keywords = ("8k", "q1", "q2", "q3", "q4", "fy", "prelim", "results", "trading", "update")
    docs = [d for d in index(company, asof)
            if d.doctype == "filing" and any(k in d.slug for k in keywords)]
    docs.sort(key=lambda d: d.published, reverse=True)
    return docs[:limit]


def latest_transcripts(company: Company, asof: dt.date | None = None, limit: int = 3) -> list[Doc]:
    docs = [d for d in index(company, asof) if d.doctype == "call-transcript"]
    docs.sort(key=lambda d: d.published, reverse=True)
    return docs[:limit]


def search(company: Company, pattern: str, asof: dt.date | None = None,
           max_hits: int = 40) -> list[tuple[Doc, int, str]]:
    """rg search across the company corpus; returns (doc, line_no, line)."""
    by_name = {d.path.name: d for d in index(company, asof)}
    try:
        # --sort path keeps output deterministic; rg's default parallel walk
        # reshuffles hits run-to-run, which reshuffled analyst evidence
        out = subprocess.run(
            ["rg", "-i", "-n", "--no-heading", "--sort", "path", "-m", "6",
             pattern, str(company.folder)],
            capture_output=True, text=True, timeout=30).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    hits: list[tuple[Doc, int, str]] = []
    for line in out.splitlines():
        try:
            path_s, line_no, content = line.split(":", 2)
        except ValueError:
            continue
        doc = by_name.get(Path(path_s).name)
        if doc is None:      # hidden by asof or unparsable name
            continue
        hits.append((doc, int(line_no), content.strip()))
        if len(hits) >= max_hits:
            break
    # newest documents first so recency dominates; fully deterministic order
    hits.sort(key=lambda h: (h[0].published.toordinal(), h[0].doc_id, -h[1]),
              reverse=True)
    return hits
