#!/usr/bin/env python3
"""Scan files for material that must not appear in the public repo.

Checks for secrets/tokens, email addresses, private repository URLs, and
personal names (PLAN.md §4 step 6). Exit code 1 if anything is found — wired
for use as a gate before placing files under evidence/redacted-excerpts/.

Patterns err toward false positives; every hit needs a human decision.
Extend NAME_DENYLIST with the project's personal-name list (kept out of git:
put one name per line in private/redact-names.txt).

Usage:
  python3 scripts/redact_check.py FILE [FILE ...]
  python3 scripts/redact_check.py --dir evidence/redacted-excerpts
"""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NAME_DENYLIST_FILE = REPO_ROOT / "private" / "redact-names.txt"

PATTERNS = [
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}")),
    ("openai-key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer-token", re.compile(r"[Bb]earer\s+[A-Za-z0-9._~+/-]{20,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("ssh-url", re.compile(r"git@[A-Za-z0-9.-]+:[A-Za-z0-9._/-]+")),
    # quotes around the key are optional so JSON forms ("api_key": "...") match too
    ("generic-secret-assign",
     re.compile(r"(?i)['\"]?(api[_-]?key|token|secret|password)['\"]?\s*[=:]\s*['\"][^'\"]{8,}")),
]

# Repos that are public and citable; any other owner/repo URL is flagged.
# lean-pde(-notes) are the former names of leray-hopf(-notes) — public redirects.
PUBLIC_REPO_ALLOWLIST = re.compile(
    r"github\.com/(uda-lab/(leray-hopf|leray-hopf-notes|lean-pde|lean-pde-notes"
    r"|KSE2026)|leanprover|leanprover-community)([/#?].*)?$"
)
GITHUB_URL = re.compile(r"https?://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")


def mask(s: str) -> str:
    """Masked preview so the scanner itself never echoes a full secret."""
    if len(s) <= 12:
        return s[:4] + "…"
    return f"{s[:8]}…{s[-4:]} (len {len(s)})"


def load_name_denylist():
    if NAME_DENYLIST_FILE.is_file():
        names = [ln.strip()
                 for ln in NAME_DENYLIST_FILE.read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.startswith("#")]
        return [(f"name:{n}", re.compile(re.escape(n))) for n in names]
    return []


def scan_file(path: Path, extra_patterns) -> int:
    hits = 0
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"ERROR reading {path}: {e}", file=sys.stderr)
        return 1
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, rx in PATTERNS + extra_patterns:
            for m in rx.finditer(line):
                print(f"{path}:{lineno}: [{label}] {mask(m.group(0))}")
                hits += 1
        for m in GITHUB_URL.finditer(line):
            if not PUBLIC_REPO_ALLOWLIST.search(m.group(0)):
                print(f"{path}:{lineno}: [non-allowlisted-repo-url] {m.group(0)}")
                hits += 1
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--dir", type=Path, action="append", default=[],
                    help="recursively scan a directory (repeatable)")
    args = ap.parse_args()

    targets = list(args.files)
    for d in args.dir:
        targets += [p for p in sorted(d.rglob("*"))
                    if p.is_file() and p.name != ".gitkeep"]
    if not targets:
        ap.error("nothing to scan")

    extra = load_name_denylist()
    total = sum(scan_file(p, extra) for p in targets)
    print(f"\n{len(targets)} file(s) scanned, {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
