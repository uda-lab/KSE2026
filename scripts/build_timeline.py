#!/usr/bin/env python3
"""Build a merged project timeline (PLAN.md Phase 2) as a Markdown table.

Merges, in timestamp order:
  - git commits from a local leray-hopf checkout (kind: commit), OR from an
    exported snapshot (--commits-jsonl evidence/repository-snapshots/.../commits.jsonl)
  - session events from evidence/manifest.csv (kind: session, using mtime as
    the session's end-time proxy)

Output goes to stdout; redirect into analysis/ when satisfied. Manual rows
(incidents, decisions) are added by hand afterwards in
analysis/project-timeline.md.

Usage:
  python3 scripts/build_timeline.py --repo /path/to/leray-hopf [--since 2026-01-01]
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "evidence" / "manifest.csv"


def parse_ts(ts: str) -> datetime:
    """Parse ISO-ish timestamps ('+09:00', '+0900', date-only) to aware UTC."""
    for fmt in None, "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d":
        try:
            dt = datetime.fromisoformat(ts) if fmt is None \
                else datetime.strptime(ts, fmt)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"unparsable timestamp: {ts!r}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def git_commits(repo: Path, since: str | None):
    cmd = ["git", "-C", str(repo), "log", "--reverse",
           "--date=format:%Y-%m-%dT%H:%M:%S%z", "--pretty=%H%x09%ad%x09%s"]
    if since:
        cmd.append(f"--since={since}")
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        sha, date, subject = line.split("\t", 2)
        yield {"ts": date, "kind": "commit",
               "ref": f"leray-hopf@{sha[:8]}",
               "summary": subject.replace("|", "\\|"), "evidence": ""}


def snapshot_commits(path: Path):
    import json
    with path.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            yield {"ts": c["authored_date"], "kind": "commit",
                   "ref": f"leray-hopf@{c['sha'][:8]}",
                   "summary": c["subject"].replace("|", "\\|"), "evidence": ""}


def manifest_sessions():
    if not MANIFEST.is_file():
        return
    with MANIFEST.open(newline="") as f:
        for r in csv.DictReader(f):
            yield {"ts": r["mtime_utc"], "kind": "session",
                   "ref": r["session_id"] or r["collected_relpath"],
                   "summary": f"session on {r['host']} ({r['tool_or_model']})",
                   "evidence": r["evidence_id"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, help="local leray-hopf checkout")
    ap.add_argument("--commits-jsonl", type=Path,
                    help="commits.jsonl from export_repo_snapshot.py "
                         "(alternative to --repo)")
    ap.add_argument("--since", help="only include events after this date")
    args = ap.parse_args()

    events = list(manifest_sessions())
    if args.repo:
        events += list(git_commits(args.repo, args.since))
    if args.commits_jsonl:
        events += list(snapshot_commits(args.commits_jsonl))
    # normalize mixed timezones (git author offsets vs manifest UTC) before
    # comparing or sorting
    for e in events:
        e["ts_utc"] = parse_ts(e["ts"])
    if args.since:
        since = parse_ts(args.since)
        events = [e for e in events if e["ts_utc"] >= since]
    events.sort(key=lambda e: e["ts_utc"])

    print("| 日時 (UTC) | 種別 | 参照 | 概要 | Evidence |")
    print("|---|---|---|---|---|")
    for e in events:
        ts = e["ts_utc"].isoformat(timespec="seconds")
        print(f"| {ts} | {e['kind']} | {e['ref']} | {e['summary']} | {e['evidence']} |")
    print(f"\n<!-- generated: {len(events)} events -->", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
