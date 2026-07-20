#!/usr/bin/env python3
"""Register raw session-log files into evidence/manifest.csv (PLAN.md §4).

Walks a directory of collected raw files, computes SHA-256 and stat metadata,
and appends one manifest row per file not already present (keyed by sha256).
Raw files are never modified.

Usage:
  python3 scripts/inventory_sessions.py private/raw-sessions/vps --host vps \
      [--tool claude-code] [--evidence-type primary] [--dry-run]
"""
import argparse
import csv
import hashlib
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


def load_manifest():
    with MANIFEST.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def next_evidence_id(rows) -> int:
    nums = [int(m.group(1)) for r in rows
            if (m := re.fullmatch(r"EV-(\d{4})", r["evidence_id"]))]
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

    rows = load_manifest()
    known = {r["sha256"] for r in rows}
    nxt = next_evidence_id(rows)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    new_rows = []
    for path in sorted(p for p in args.directory.rglob("*") if p.is_file()):
        digest = sha256_file(path)
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
            "original_path": str(path),
            "size_bytes": st.st_size,
            "mtime_utc": iso(st.st_mtime),
            "ctime_utc": iso(st.st_ctime),
            "session_id": m.group(1).lower() if m else "",
            "tool_or_model": args.tool,
            "collected_at_utc": now,
            "evidence_type": args.evidence_type,
            "notes": "",
        })
        nxt += 1

    if args.dry_run:
        for r in new_rows:
            print(f"{r['evidence_id']}  {r['sha256'][:12]}  {r['original_path']}")
        print(f"(dry-run) would register {len(new_rows)} file(s)")
        return 0

    if new_rows:
        with MANIFEST.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(new_rows[0].keys()))
            w.writerows(new_rows)
    print(f"registered {len(new_rows)} file(s) into {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
