#!/usr/bin/env python3
"""Extract formalization-size metrics from a local leray-hopf checkout.

Counts, per the pinned reference commit (check out first!):
  - .lean file count and line count under LerayHopf/
  - declaration counts (theorem / lemma / def / structure / instance)
  - occurrences of `sorry` (should be 0 on the release surface)
  - commit count and author-date range from git

Writes JSON to evidence/metrics/formalization-metrics.json and echoes it.
These numbers back the "scale" claims in the paper — never write them from
memory (claims/formalization-scope.md).

Usage:
  python3 scripts/extract_metrics.py --repo /path/to/leray-hopf \
      [--expect-commit 7c15710a7b9068a2aa105fc7c11b432e7685b7b5]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "evidence" / "metrics" / \
    "formalization-metrics.json"

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*(?:private\s+|protected\s+|noncomputable\s+|scoped\s+)*"
    r"(theorem|lemma|def|abbrev|structure|instance|inductive)\b")
SORRY_RE = re.compile(r"\bsorry\b")


def git(repo, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--src-dir", default="LerayHopf",
                    help="source subdirectory to measure (default: LerayHopf)")
    ap.add_argument("--expect-commit",
                    help="fail if HEAD does not match this commit")
    args = ap.parse_args()

    head = git(args.repo, "rev-parse", "HEAD")
    if args.expect_commit and not head.startswith(args.expect_commit):
        print(f"ERROR: HEAD is {head}, expected {args.expect_commit}. "
              "Check out the pinned commit first.", file=sys.stderr)
        return 1

    src = args.repo / args.src_dir
    decls = {}
    files = lines = code_lines = sorries = 0
    for p in sorted(src.rglob("*.lean")):
        files += 1
        in_block_comment = 0
        for line in p.read_text(errors="replace").splitlines():
            lines += 1
            stripped = line.strip()
            # approximate code-LOC: skip blanks, `--` lines, and /- ... -/ blocks
            in_block_comment += stripped.count("/-") - stripped.count("-/")
            is_comment = (in_block_comment > 0 or stripped.startswith("--")
                          or stripped.endswith("-/"))
            if stripped and not is_comment:
                code_lines += 1
            if m := DECL_RE.match(line):
                decls[m.group(1)] = decls.get(m.group(1), 0) + 1
            if SORRY_RE.search(line):
                sorries += 1

    metrics = {
        "repo": "uda-lab/leray-hopf",
        "commit": head,
        "described_by": git(args.repo, "describe", "--tags", "--always"),
        "src_dir": args.src_dir,
        "lean_files": files,
        "lean_lines_physical": lines,
        "lean_lines_code": code_lines,
        "declarations": dict(sorted(decls.items())),
        "sorry_occurrences": sorries,
        "commit_count": int(git(args.repo, "rev-list", "--count", "HEAD")),
        "first_commit_date": git(args.repo, "log", "--reverse",
                                 "--format=%aI", "--max-count=1"),
        "last_commit_date": git(args.repo, "log", "-1", "--format=%aI"),
        "note": "declaration counts are regex-based (source-text level), not "
                "elaborator-verified; sorry count is textual and may include "
                "comments/strings; lean_lines_code approximates non-blank "
                "non-comment LOC (block-comment tracking is line-granular) — "
                "state which definition the paper cites and match it against "
                "the upstream repo's own LOC figures before quoting",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))
    print(f"\nwritten to {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
