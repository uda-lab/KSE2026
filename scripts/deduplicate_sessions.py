#!/usr/bin/env python3
"""Report duplicate / split sessions across hosts from evidence/manifest.csv.

Two checks (PLAN.md §4 step 5):
  - identical sha256 registered more than once (exact duplicates)
  - identical session_id appearing on multiple hosts or in multiple files
    (session continued/synced across environments — needs manual reconciliation)

Read-only: prints a report, never edits the manifest.

Usage:
  python3 scripts/deduplicate_sessions.py
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "evidence" / "manifest.csv"


def main() -> int:
    with MANIFEST.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("manifest is empty; nothing to check")
        return 0

    by_sha = defaultdict(list)
    by_session = defaultdict(list)
    for r in rows:
        by_sha[r["sha256"]].append(r)
        if r["session_id"]:
            by_session[r["session_id"]].append(r)

    dup_sha = {k: v for k, v in by_sha.items() if len(v) > 1}
    multi_sess = {k: v for k, v in by_session.items() if len(v) > 1}

    print(f"rows: {len(rows)}")
    print(f"exact duplicates (same sha256): {len(dup_sha)} group(s)")
    for sha, group in sorted(dup_sha.items()):
        print(f"  {sha[:16]}…")
        for r in group:
            print(f"    {r['evidence_id']} {r['host']} {r['original_path']}")

    print(f"session_id seen in multiple files: {len(multi_sess)} group(s)")
    for sid, group in sorted(multi_sess.items()):
        hosts = sorted({r["host"] for r in group})
        print(f"  {sid} (hosts: {', '.join(hosts)})")
        for r in group:
            print(f"    {r['evidence_id']} {r['host']} {r['original_path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
