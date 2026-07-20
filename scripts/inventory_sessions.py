#!/usr/bin/env python3
"""Register raw session-log files into evidence/manifest.csv (PLAN.md §4).

Walks a directory of collected raw files, computes SHA-256 and stat metadata,
and appends one manifest row per file not already present (keyed by sha256).
Raw files are never modified.

The public manifest records only the path RELATIVE to the scanned directory
(`collected_relpath`) — absolute paths can contain usernames or private
project names (PLAN.md §2). Preserve the source machine's absolute paths in
a gitignored sidecar (e.g. private/raw-sessions/<host>/SOURCES.md) at
collection time; mirror the source directory layout when copying so the
relpath stays meaningful.

Usage:
  python3 scripts/inventory_sessions.py private/raw-sessions/vps --host vps \
      [--tool claude-code] [--evidence-type primary] [--dry-run]
"""
import argparse
import csv
import fcntl
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "evidence" / "manifest.csv"
HOSTS = ("vps", "local-main", "local-secondary")
# Claude Code session files are named <uuid>.jsonl
SESSION_ID_RE = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")


def next_evidence_id(rows) -> int:
    nums = [int(m.group(1)) for r in rows
            if (m := re.fullmatch(r"EV-(\d{4,})", r["evidence_id"]))]
    return max(nums, default=0) + 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directory", type=Path, help="collected raw-file tree to register")
    ap.add_argument("--host", required=True, choices=HOSTS)
    ap.add_argument("--tool", default="claude-code",
                    help="tool_or_model column value (default: claude-code)")
    ap.add_argument("--evidence-type", default="primary",
                    choices=("primary", "reconstructed"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.directory.is_dir():
        ap.error(f"not a directory: {args.directory}")
    # fail closed: only the designated raw area may be inventoried, so relpaths
    # in the public manifest can never encode host-specific layouts. Compare
    # logical (symlink-preserving) paths: private/raw-sessions may itself be a
    # symlink into the host-mounted read-only evidence area (/private/sources).
    raw_root = Path(os.path.abspath(REPO_ROOT / "private" / "raw-sessions"))
    logical = Path(os.path.abspath(args.directory))
    if raw_root not in logical.parents and logical != raw_root:
        ap.error(f"refusing to inventory outside {raw_root} (got {logical}); "
                 "copy raw files there first (see private/README.md)")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # hash outside the lock (slow part), then read+number+append under one
    # exclusive lock so concurrent runs cannot duplicate EV numbers
    # (cross-host collection is additionally serialized by policy, issue #2)
    candidates = []
    for path in sorted(p for p in args.directory.rglob("*") if p.is_file()):
        candidates.append((path, sha256_file(path)))

    with MANIFEST.open("a+", newline="") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        rows = list(csv.DictReader(f))
        known = {r["sha256"] for r in rows}
        nxt = next_evidence_id(rows)

        new_rows = []
        for path, digest in candidates:
            if digest in known:
                print(f"skip (already registered): {path}", file=sys.stderr)
                continue
            known.add(digest)
            st = path.stat()
            m = SESSION_ID_RE.search(path.name)
            new_rows.append({
                "evidence_id": f"EV-{nxt:04d}",
                "sha256": digest,
                "host": args.host,
                "collected_relpath": path.relative_to(args.directory).as_posix(),
                "size_bytes": st.st_size,
                "mtime_utc": iso(st.st_mtime),
                # st_ctime is inode-change time on Unix, NOT creation time;
                # column name says so to keep cross-host timelines honest
                "stat_ctime_utc": iso(st.st_ctime),
                "session_id": m.group(1).lower() if m else "",
                "tool_or_model": args.tool,
                "collected_at_utc": now,
                "evidence_type": args.evidence_type,
                "notes": "",
            })
            nxt += 1

        if args.dry_run:
            for r in new_rows:
                print(f"{r['evidence_id']}  {r['sha256'][:12]}  {r['collected_relpath']}")
            print(f"(dry-run) would register {len(new_rows)} file(s)")
            return 0

        if new_rows:
            f.seek(0, 2)
            w = csv.DictWriter(f, fieldnames=list(new_rows[0].keys()))
            w.writerows(new_rows)
    print(f"registered {len(new_rows)} file(s) into {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
