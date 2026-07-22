#!/usr/bin/env python3
"""Extract session usage metrics from escrowed Claude Code JSONL (issue #14).

Scans `private/raw-sessions/<host>/claude-projects/**/*.jsonl` for the three
hosts, aggregates `message.usage` (primary API-response records) per
model x UTC-date x host, converts to API-equivalent USD with a built-in
published price table, and computes per-session wall-clock / active time
with parameterized gap thresholds (sensitivity: 1/5/15 min by default).

Deduplication: the same API response appears on multiple JSONL lines (one
line per content block) sharing `message.id`; a global seen-set keyed on
`message.id` (fallback `requestId`) prevents double counting, including
identical files that exist in more than one host escrow.

Exclusions (documented in analysis/usage-metrics-methodology.md):
  - `<synthetic>` model records (harness-internal, no API usage)
  - `hermes/` orchestrator sessions (pre-leray-hopf project work, issue #14)
  - history.jsonl / tasks / plans (no usage records)

Output: evidence/metrics/usage-metrics.json (JSON, sorted keys).

Usage:
  python3 scripts/extract_usage.py [--gap-thresholds 60,300,900]
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_ROOT = REPO_ROOT / "private" / "raw-sessions"
OUT = REPO_ROOT / "evidence" / "metrics" / "usage-metrics.json"
HOSTS = ("vps", "local-main", "local-secondary")

# Published USD per MTok (platform.claude.com pricing, retrieved 2026-07-22).
# Cache multipliers per published policy: write 5m = 1.25x input,
# write 1h = 2x input, read = 0.1x input.
# claude-sonnet-5 uses the list price ($3/$15); the introductory price
# ($2/$10 through 2026-08-31) would lower the conversion — noted in the
# methodology doc. Model IDs are normalized by longest-prefix match so dated
# variants (e.g. claude-haiku-4-5-20251001) resolve to their family.
PRICES = {
    "claude-fable-5": (10.0, 50.0),
    "claude-opus-4": (5.0, 25.0),      # 4.5 / 4.6 / 4.7 / 4.8
    "claude-sonnet-5": (3.0, 15.0),
    "claude-sonnet-4": (3.0, 15.0),    # 4.5 / 4.6
    "claude-haiku-4-5": (1.0, 5.0),
}
CACHE_W_5M, CACHE_W_1H, CACHE_R = 1.25, 2.0, 0.1

TS_RE = re.compile(r'"timestamp"\s*:\s*"([^"]+)"')
SESSION_FILE_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$", re.I
)


def price_for(model: str):
    for prefix in sorted(PRICES, key=len, reverse=True):
        if model.startswith(prefix):
            return PRICES[prefix]
    return None


def parse_ts(s: str):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gap-thresholds", default="60,300,900",
                    help="comma-separated active-time gap caps in seconds")
    args = ap.parse_args()
    thresholds = [int(x.strip()) for x in args.gap_thresholds.split(",") if x.strip()]

    seen_msgs = set()
    # (model, date, host) -> dict of counters
    agg = defaultdict(lambda: defaultdict(int))
    unknown_models = defaultdict(int)
    synthetic = 0
    files_scanned = 0
    sessions = []  # per top-level session: dict(host, wall_s, active_s per thr)

    for host in HOSTS:
        root = RAW_ROOT / host / "claude-projects"
        if not root.is_dir():
            print(f"warning: missing {root}", file=sys.stderr)
            continue
        for path in sorted(root.rglob("*.jsonl")):
            files_scanned += 1
            is_toplevel = (path.parent.parent == root
                           and SESSION_FILE_RE.match(path.name))
            timestamps = []
            with path.open(errors="replace") as fh:
                for line in fh:
                    if is_toplevel:
                        m = TS_RE.search(line)
                        if m:
                            t = parse_ts(m.group(1))
                            if t is not None:
                                timestamps.append(t)
                    if '"usage"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = d.get("message") or {}
                    usage = msg.get("usage")
                    model = msg.get("model")
                    if not usage or not isinstance(usage, dict) or not model:
                        continue
                    if model == "<synthetic>":
                        synthetic += 1
                        continue
                    key = msg.get("id") or d.get("requestId")
                    if not key or key in seen_msgs:
                        continue
                    seen_msgs.add(key)
                    ts = d.get("timestamp") or ""
                    day = ts[:10] if len(ts) >= 10 else "unknown"
                    row = agg[(model, day, host)]
                    row["turns"] += 1
                    row["input_tokens"] += usage.get("input_tokens") or 0
                    row["output_tokens"] += usage.get("output_tokens") or 0
                    row["cache_read_tokens"] += usage.get("cache_read_input_tokens") or 0
                    cc = usage.get("cache_creation") or {}
                    w5 = cc.get("ephemeral_5m_input_tokens")
                    w1 = cc.get("ephemeral_1h_input_tokens")
                    if w5 is None and w1 is None:
                        # no TTL breakdown: count as 5m (lower-bound cost)
                        w5 = usage.get("cache_creation_input_tokens") or 0
                        w1 = 0
                        row["cache_write_unattributed_turns"] += 1
                    row["cache_write_5m_tokens"] += w5 or 0
                    row["cache_write_1h_tokens"] += w1 or 0
                    if price_for(model) is None:
                        unknown_models[model] += 1
            if is_toplevel and len(timestamps) >= 2:
                timestamps.sort()
                gaps = [b - a for a, b in zip(timestamps, timestamps[1:])]
                sessions.append({
                    "host": host,
                    "session_id": path.stem.lower(),
                    "wall_clock_s": round(timestamps[-1] - timestamps[0]),
                    "active_s": {str(thr): round(sum(min(g, thr) for g in gaps))
                                 for thr in thresholds},
                })

    def cost(model, row):
        p = price_for(model)
        if p is None:
            return 0.0
        pin, pout = p
        return (row["input_tokens"] * pin
                + row["output_tokens"] * pout
                + row["cache_write_5m_tokens"] * pin * CACHE_W_5M
                + row["cache_write_1h_tokens"] * pin * CACHE_W_1H
                + row["cache_read_tokens"] * pin * CACHE_R) / 1e6

    rows = []
    by_model = defaultdict(lambda: defaultdict(int))
    for (model, day, host), row in sorted(agg.items()):
        c = cost(model, row)
        rows.append({"model": model, "date_utc": day, "host": host,
                     **row, "api_cost_usd": round(c, 4)})
        bm = by_model[model]
        for k, v in row.items():
            bm[k] += v
        bm["api_cost_usd"] = round(bm.get("api_cost_usd", 0.0) + c, 4)

    totals = defaultdict(float)
    for bm in by_model.values():
        for k, v in bm.items():
            totals[k] += v
    totals = {k: (round(v, 2) if k == "api_cost_usd" else int(v))
              for k, v in totals.items()}

    time_summary = {
        "sessions_counted": len(sessions),
        "wall_clock_hours_sum": round(sum(s["wall_clock_s"] for s in sessions) / 3600, 1),
        "active_hours_by_gap_threshold_s": {
            str(thr): round(sum(s["active_s"][str(thr)] for s in sessions) / 3600, 1)
            for thr in thresholds},
    }

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "script": "scripts/extract_usage.py",
        "params": {"gap_thresholds_s": thresholds},
        "pricing_usd_per_mtok": {k: {"input": v[0], "output": v[1]} for k, v in PRICES.items()},
        "cache_multipliers": {"write_5m": CACHE_W_5M, "write_1h": CACHE_W_1H, "read": CACHE_R},
        "scan": {
            "hosts": list(HOSTS),
            "files_scanned": files_scanned,
            "deduped_api_messages": len(seen_msgs),
            "synthetic_records_excluded": synthetic,
            "unknown_model_turns": dict(unknown_models),
        },
        "totals": totals,
        "by_model": {m: dict(v) for m, v in sorted(by_model.items())},
        "by_model_date_host": rows,
        "time": time_summary,
        "sessions": sorted(sessions, key=lambda s: (s["host"], s["session_id"])),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")
    print(f"files={files_scanned} api_messages={len(seen_msgs)} "
          f"sessions={len(sessions)}")
    print(f"totals: output={totals.get('output_tokens', 0):,} tok, "
          f"cache_read={totals.get('cache_read_tokens', 0):,} tok, "
          f"api_cost=${totals.get('api_cost_usd', 0):,}")
    for thr, h in time_summary["active_hours_by_gap_threshold_s"].items():
        print(f"active({int(thr) // 60}m gap cap) = {h}h", end="  ")
    print(f"/ wall={time_summary['wall_clock_hours_sum']}h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
