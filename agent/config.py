"""Company and challenge configuration.

Loads the official challenge spec from challenge/companies.json and layers on
the per-company knowledge the pipeline needs: corpus folder, fiscal-calendar
conventions, metric aliases used for retrieval and extraction, and validation
bounds. Nothing here contains forecasts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHALLENGE = REPO_ROOT / "challenge"
OFFLINE_DATA = CHALLENGE / "offline-data"
TEMPLATES = CHALLENGE / "templates"
SUBMISSION = REPO_ROOT / "submission"
RUNS = REPO_ROOT / "runs"
LOGS = REPO_ROOT / "logs"
RESEARCH = REPO_ROOT / "research"
CACHE = REPO_ROOT / "cache"


@dataclass
class Metric:
    label: str          # exact label from companies.json / workbook Summary sheet
    units: str          # exact units string
    key: str            # short machine key, e.g. "net_sales"
    kind: str           # "money" | "eps" | "percent"
    aliases: list[str] = field(default_factory=list)  # phrases used in filings


@dataclass
class Company:
    name: str
    ticker: str         # challenge ticker, e.g. "HD" or "LSE:HAS"
    short: str          # folder-friendly short code: HD, ADI, HAS, DE
    period: str         # target period label, e.g. "FY2026Q2"
    output_file: str
    folder: Path        # corpus folder
    fiscal_note: str    # how the company labels fiscal periods, for prompts
    metrics: list[Metric] = field(default_factory=list)

    @property
    def template(self) -> Path:
        return TEMPLATES / self.output_file


_METRIC_EXTRAS: dict[tuple[str, str], dict] = {
    ("HD", "Net sales"): dict(
        key="net_sales", kind="money",
        aliases=["net sales", "sales of $", "reported sales", "total sales"]),
    ("HD", "Adjusted diluted EPS"): dict(
        key="adj_eps", kind="eps",
        aliases=["adjusted diluted earnings per share", "adjusted diluted EPS"]),
    ("HD", "Comparable sales, total company"): dict(
        key="comp_sales", kind="percent",
        aliases=["comparable sales", "comp sales"]),
    ("ADI", "Revenue"): dict(
        key="revenue", kind="money",
        aliases=["revenue"]),
    ("ADI", "Adjusted diluted EPS"): dict(
        key="adj_eps", kind="eps",
        aliases=["adjusted EPS", "adjusted diluted EPS", "adjusted diluted earnings per share"]),
    ("ADI", "Adjusted gross margin"): dict(
        key="adj_gross_margin", kind="percent",
        aliases=["adjusted gross margin", "gross margin"]),
    ("HAS", "Net fees"): dict(
        key="net_fees", kind="money",
        aliases=["net fees", "Group net fees"]),
    ("HAS", "Pre-exceptional basic EPS"): dict(
        key="preex_eps", kind="eps",
        aliases=["basic earnings per share (pre-exceptional", "pre-exceptional basic EPS",
                 "basic EPS (pre-exceptional"]),
    ("HAS", "Pre-exceptional operating profit"): dict(
        key="preex_op", kind="money",
        aliases=["pre-exceptional operating profit", "operating profit (pre-exceptional",
                 "operating profit before exceptional"]),
    ("DE", "Worldwide net sales and revenues"): dict(
        key="net_sales_rev", kind="money",
        aliases=["worldwide net sales and revenues", "net sales and revenues"]),
    ("DE", "Diluted EPS (GAAP)"): dict(
        key="eps", kind="eps",
        aliases=["per diluted share", "diluted EPS", "net income per share"]),
    ("DE", "Production & Precision Ag operating profit"): dict(
        key="ppa_op", kind="money",
        aliases=["production & precision ag", "production and precision ag",
                 "production & precision agriculture"]),
}

_COMPANY_EXTRAS: dict[str, dict] = {
    "HD": dict(
        short="HD", folder="home-depot",
        fiscal_note=(
            "Home Depot's fiscal year ends late January/early February of the following "
            "calendar year. 'First quarter fiscal 2026' = FY2026Q1 (ended May 2026); the "
            "target FY2026Q2 ended early August 2026. Fiscal 2025 Q2 is the prior-year "
            "comparative.")),
    "ADI": dict(
        short="ADI", folder="analog-devices",
        fiscal_note=(
            "Analog Devices' fiscal year ends around the start of November. "
            "'Third quarter fiscal 2026' = FY2026Q3 (ended ~1 August 2026). ADI issues "
            "explicit next-quarter guidance for revenue, adjusted gross margin and "
            "adjusted EPS in each quarterly release.")),
    "LSE:HAS": dict(
        short="HAS", folder="hays",
        fiscal_note=(
            "Hays plc's fiscal year ends 30 June. FY2026 = year ended 30 June 2026. Hays "
            "reports quarterly trading updates with net-fee growth and a full-year "
            "results announcement in late August. Net fees are like-for-like; EPS is "
            "reported in pence (GBp). Q4 FY2026 trading update was published July 2026.")),
    "DE": dict(
        short="DE", folder="deere",
        fiscal_note=(
            "Deere & Company's fiscal year ends around the start of November. "
            "'Third quarter fiscal 2026' = FY2026Q3 (ended late July 2026). Deere guides "
            "full-year net income and per-segment sales growth/operating margin rather "
            "than quarterly EPS.")),
}


def load_companies() -> list[Company]:
    spec = json.loads((CHALLENGE / "companies.json").read_text())
    companies: list[Company] = []
    for c in spec["companies"]:
        extra = _COMPANY_EXTRAS[c["ticker"]]
        metrics = []
        for m in c["metrics"]:
            mx = _METRIC_EXTRAS[(extra["short"], m["label"])]
            metrics.append(Metric(label=m["label"], units=m["units"], **mx))
        companies.append(Company(
            name=c["company"], ticker=c["ticker"], short=extra["short"],
            period=c["period"], output_file=c["outputFile"],
            folder=OFFLINE_DATA / extra["folder"],
            fiscal_note=extra["fiscal_note"], metrics=metrics))
    return companies


def get_company(short: str) -> Company:
    for c in load_companies():
        if c.short == short.upper():
            return c
    raise KeyError(f"unknown company short code: {short}")
