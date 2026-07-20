#!/usr/bin/env python3
"""Verify that every claim/evidence reference resolves (AGENTS.md rule 4).

Checks:
  - every `EV-NNNN` referenced in claims/, analysis/, paper/, notes/ exists in
    evidence/manifest.csv
  - every `INC-NNN` referenced anywhere has a card evidence/incidents/INC-NNN.md
  - every `CLM-NNN` referenced in paper/ is defined in claims/paper-claims.md
  - every claim defined in claims/paper-claims.md has at least one Evidence entry
Exit code 1 on any unresolved reference. Run via `make verify` (also in CI).
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence" / "manifest.csv"
CLAIMS_FILE = ROOT / "claims" / "paper-claims.md"
INCIDENT_DIR = ROOT / "evidence" / "incidents"

EV_RE = re.compile(r"\bEV-\d{4}\b")
INC_RE = re.compile(r"\bINC-\d{3}\b")
CLM_RE = re.compile(r"\bCLM-\d{3}\b")
CLM_DEF_RE = re.compile(r"^##\s+(CLM-\d{3}):", re.M)

SCAN_DIRS = ["claims", "analysis", "paper", "notes"]
PLACEHOLDER_RE = re.compile(r"(NNNN|NNN)")


def strip_placeholders(text: str) -> str:
    """Drop template lines like `EV-NNNN` so format docs don't trip the check."""
    return "\n".join(ln for ln in text.splitlines() if not PLACEHOLDER_RE.search(ln))


def main() -> int:
    known_ev = set()
    if MANIFEST.is_file():
        with MANIFEST.open(newline="") as f:
            known_ev = {r["evidence_id"] for r in csv.DictReader(f)}
    known_inc = {p.stem for p in INCIDENT_DIR.glob("INC-*.md")}
    claims_text = CLAIMS_FILE.read_text(encoding="utf-8") if CLAIMS_FILE.is_file() else ""
    known_clm = set(CLM_DEF_RE.findall(claims_text))

    errors = []

    for d in SCAN_DIRS:
        for path in sorted((ROOT / d).rglob("*")):
            if not path.is_file() or path.suffix not in (".md", ".tex"):
                continue
            text = strip_placeholders(path.read_text(encoding="utf-8", errors="replace"))
            rel = path.relative_to(ROOT)
            for ev in set(EV_RE.findall(text)) - known_ev:
                errors.append(f"{rel}: {ev} not in evidence/manifest.csv")
            for inc in set(INC_RE.findall(text)) - known_inc:
                errors.append(f"{rel}: {inc} has no card in evidence/incidents/")
            if d == "paper":
                for clm in set(CLM_RE.findall(text)) - known_clm:
                    errors.append(f"{rel}: {clm} not defined in claims/paper-claims.md")

    # every defined claim must carry at least one evidence reference
    for m in CLM_DEF_RE.finditer(claims_text):
        block_start = m.end()
        nxt = CLM_DEF_RE.search(claims_text, block_start)
        block = claims_text[block_start: nxt.start() if nxt else len(claims_text)]
        ev_line = re.search(r"^- Evidence:\s*(\S.*)$", block, re.M)
        if not ev_line or not ev_line.group(1).strip():
            errors.append(f"claims/paper-claims.md: {m.group(1)} has no Evidence entry")

    if errors:
        print("claim-link verification FAILED:")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"claim-link verification OK "
          f"(EV known: {len(known_ev)}, INC cards: {len(known_inc)}, "
          f"claims defined: {len(known_clm)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
