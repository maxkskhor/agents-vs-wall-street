"""Timestamped run logging to stdout and a log file under logs/."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

from .config import LOGS


class RunLog:
    def __init__(self, run_id: str, path: Path | None = None):
        self.run_id = run_id
        LOGS.mkdir(exist_ok=True)
        self.path = path or (LOGS / f"run-{run_id}.log")
        self._fh = open(self.path, "a", encoding="utf-8")

    def log(self, stage: str, message: str) -> None:
        ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"{ts} [{stage}] {message}"
        print(line, flush=True)
        self._fh.write(line + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


def new_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
