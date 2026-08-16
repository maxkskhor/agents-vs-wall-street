"""Canonical fiscal-period arithmetic: "FY2026Q2", "FY2026H1", "FY2026"."""

from __future__ import annotations

import re

_RE = re.compile(r"^FY(\d{4})(?:Q([1-4])|H([12]))?$")


def parse(period: str) -> tuple[int, str, int | None]:
    m = _RE.match(period)
    if not m:
        raise ValueError(f"bad period {period!r}")
    fy = int(m.group(1))
    if m.group(2):
        return fy, "Q", int(m.group(2))
    if m.group(3):
        return fy, "H", int(m.group(3))
    return fy, "Y", None


def fmt(fy: int, kind: str, n: int | None) -> str:
    if kind == "Y":
        return f"FY{fy}"
    return f"FY{fy}{kind}{n}"


def prior_year(period: str) -> str:
    fy, kind, n = parse(period)
    return fmt(fy - 1, kind, n)


def shift_quarters(period: str, delta: int) -> str:
    fy, kind, n = parse(period)
    if kind != "Q":
        raise ValueError(f"{period} is not a quarter")
    idx = fy * 4 + (n - 1) + delta
    return fmt(idx // 4, "Q", idx % 4 + 1)


def quarters_of(fy: int) -> list[str]:
    return [fmt(fy, "Q", i) for i in range(1, 5)]
