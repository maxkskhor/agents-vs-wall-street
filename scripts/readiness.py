"""Pre-submission readiness check.

Covers what the official `npm run check:submission` does not: secrets, repo
completeness, HTML constraints from ENTRY.md, and whether the declared final
commit and command actually match reality.

    .venv/bin/python scripts/readiness.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
checks: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, bool(ok), detail))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


# --- secrets and privacy -----------------------------------------------------
tracked = git("ls-files").splitlines()
check("`.env` is not tracked", ".env" not in tracked)
check("`entry.json` is not tracked", "entry.json" not in tracked)
html = (ROOT / "architecture/index.html").read_text()
emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html)
check("no email addresses in the architecture HTML", not emails, str(emails[:3]))
secretish = [f for f in tracked
             if re.search(r"(^|/)\.env($|\.)|secret|credential", f, re.I)
             and not f.endswith(".env.example")]
# the template must be tracked; it carries variable names and no values
example = (ROOT / ".env.example").read_text()
check("`.env.example` has names but no values",
      all(not line.split("=", 1)[1].strip()
          for line in example.splitlines()
          if "=" in line and not line.startswith("#")))
check("no secret-looking files tracked", not secretish, str(secretish[:3]))

# --- entry.json --------------------------------------------------------------
entry_path = ROOT / "entry.json"
if entry_path.exists():
    entry = json.loads(entry_path.read_text())
    members = entry.get("teamMembers", [])
    check("entry.json: every member has name and email",
          bool(members) and all(m.get("name") and m.get("email") for m in members),
          f"{len(members)} members")
    check("entry.json: emailUseConfirmed is true", entry.get("emailUseConfirmed") is True)
    sub = entry.get("submission", {})
    check("entry.json: repository URL set", bool(sub.get("repositoryUrl")))
    check("entry.json: final command set", bool(sub.get("finalCommand")))
    final_commit = sub.get("finalCommit", "")
    head = git("rev-parse", "HEAD")
    check("entry.json: finalCommit set", bool(final_commit),
          "FILL AT 17:15" if not final_commit else final_commit[:12])
    if final_commit:
        check("entry.json: finalCommit matches HEAD", head.startswith(final_commit),
              f"HEAD={head[:12]}")
        check("finalCommit is pushed",
              git("branch", "-r", "--contains", final_commit) != "")
else:
    check("entry.json exists", False, "run npm run setup:entry")

# --- architecture HTML (constraints from ENTRY.md) ---------------------------
check("HTML under 2 MB", len(html.encode()) < 2_000_000, f"{len(html.encode()) // 1024} KB")
check("HTML has no <script> (preview does not run them)", "<script" not in html.lower())
check("HTML has no external assets",
      not re.search(r'(src|href)\s*=\s*"https?://', html))
placeholders = re.findall(r'fill-me">([^<]*)', html)
check("HTML has no unfilled placeholders", not placeholders, str(placeholders))
check("HTML names the team", "Team MYS" in html)

# --- workbooks ---------------------------------------------------------------
expected = ["HD-FY2026Q2.xlsx", "ADI-FY2026Q3.xlsx", "HAS-FY2026.xlsx", "DE-FY2026Q3.xlsx"]
missing = [f for f in expected if not (ROOT / "submission" / f).exists()]
check("all four workbooks present", not missing, str(missing))

# --- repo completeness -------------------------------------------------------
for f in ["README.md", "requirements.txt", ".env.example", "agent/__main__.py",
          "cache/calibration.json", "research/backtest-report.md"]:
    check(f"tracked: {f}", f in tracked)
check("a run log is tracked", any(t.startswith("logs/run-") for t in tracked))
check("working tree is clean", git("status", "--porcelain") == "",
      git("status", "--porcelain")[:80])

# --- report ------------------------------------------------------------------
pad = max(len(n) for n, _, _ in checks)
fails = 0
for name, ok, detail in checks:
    if not ok:
        fails += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name:{pad}s}" + (f"  [{detail}]" if detail else ""))
print(f"\n{len(checks) - fails}/{len(checks)} passed")
sys.exit(1 if fails else 0)
