#!/usr/bin/env python3
"""Vertex completion-phase usage extraction and billing reconciliation (issue #23/#26).

Re-aggregates the `_vrtx_`-marked usage records (Vertex AI period,
2026-07-02..07-04 UTC, host local-secondary) from the escrow, bucketed by
**America/Los_Angeles (PT) day** to match Google Cloud billing's daily
granularity, and reconciles against the redacted billing aggregate
`evidence/metrics/vertex-completion-phase-billing.csv`.

Two cost rules are computed from the published per-MTok prices:
  - `std`:  input x1, output x1, cache write x1.25 (all 5m TTL), cache read x0.1
  - `long_context_rule`: requests whose prompt-side tokens (input + cache
    write + cache read) exceed 200K are charged at input-family x2 /
    output x1.5 (the published >200K long-context premium), others as `std`.

Outputs (JSON, sorted keys):
  evidence/metrics/vertex-completion-phase-usage.json
  evidence/metrics/vertex-completion-phase-summary.json

Both are derived artifacts; the authoritative raw inputs are the escrow
session logs (EV-registered) and the owner-provided Google Cloud export
(kept privately, sha256 recorded in analysis/billing-reconciliation.md).

Usage:
  python3 scripts/extract_vertex_phase.py
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT = REPO_ROOT / "private" / "raw-sessions" / "local-secondary" / "claude-projects"
BILLING = REPO_ROOT / "evidence" / "metrics" / "vertex-completion-phase-billing.csv"
OUT_USAGE = REPO_ROOT / "evidence" / "metrics" / "vertex-completion-phase-usage.json"
OUT_SUMMARY = REPO_ROOT / "evidence" / "metrics" / "vertex-completion-phase-summary.json"

PT = timezone(timedelta(hours=-7))  # PDT (UTC-7) throughout the July window
# Documented completion-phase window (issue #23). Records outside it are
# rejected so a rerun after new _vrtx_ escrow data cannot silently drift
# away from the fixed two-day billing CSV.
WINDOW_START, WINDOW_END = "2026-07-02T00:00:00Z", "2026-07-05T00:00:00Z"
PRICES = {"claude-fable-5": (10.0, 50.0), "claude-opus-4-8": (5.0, 25.0)}
CACHE_W, CACHE_R = 1.25, 0.1
LONG_CTX_THRESHOLD = 200_000
LONG_IN_MULT, LONG_OUT_MULT = 2.0, 1.5


def main() -> int:
    cells = defaultdict(lambda: defaultdict(float))
    sessions = {}
    first = last = None
    out_of_window = 0
    seen = set()
    for f in sorted(ROOT.rglob("*.jsonl")):
        for line in f.open(errors="replace"):
            if "_vrtx_" not in line or '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            m = d.get("message") or {}
            u, mod, mid = m.get("usage"), m.get("model"), (m.get("id") or "")
            if not u or not mod or "_vrtx_" not in mid or mid in seen:
                continue
            seen.add(mid)
            ts_utc = d.get("timestamp")
            if not (WINDOW_START <= ts_utc < WINDOW_END):
                out_of_window += 1
                continue
            dt = datetime.fromisoformat(ts_utc.replace("Z", "+00:00"))
            day_pt = dt.astimezone(PT).date().isoformat()
            pin, pout = PRICES[mod]
            inp = u.get("input_tokens") or 0
            out = u.get("output_tokens") or 0
            cr = u.get("cache_read_input_tokens") or 0
            cc = u.get("cache_creation") or {}
            w = ((cc.get("ephemeral_5m_input_tokens")
                  or u.get("cache_creation_input_tokens") or 0)
                 + (cc.get("ephemeral_1h_input_tokens") or 0))
            std = (inp * pin + out * pout + w * pin * CACHE_W + cr * pin * CACHE_R) / 1e6
            ctx = inp + cr + w
            if ctx > LONG_CTX_THRESHOLD:
                prem = (inp * pin * LONG_IN_MULT + out * pout * LONG_OUT_MULT
                        + w * pin * CACHE_W * LONG_IN_MULT
                        + cr * pin * CACHE_R * LONG_IN_MULT) / 1e6
            else:
                prem = std
            c = cells[(day_pt, mod)]
            c["turns"] += 1
            c["input_tokens"] += inp
            c["output_tokens"] += out
            c["cache_write_tokens_5m"] += w
            c["cache_read_tokens"] += cr
            c["turns_over_200k_context"] += (ctx > LONG_CTX_THRESHOLD)
            c["est_usd_std"] += std
            c["est_usd_long_context_rule"] += prem
            sid = d.get("sessionId") or f.stem
            a, b = sessions.get(sid, (ts_utc, ts_utc))
            sessions[sid] = (min(a, ts_utc), max(b, ts_utc))
            first = ts_utc if first is None or ts_utc < first else first
            last = ts_utc if last is None or ts_utc > last else last

    billed = {}
    if BILLING.is_file():
        for r in csv.DictReader(BILLING.open()):
            billed[(r["date_pt"], r["model"])] = int(r["billed_jpy"])

    rows, recon = [], []
    for (day, mod), c in sorted(cells.items()):
        row = {"date_pt": day, "model": mod,
               **{k: (round(v, 4) if k.startswith("est_") else int(v))
                  for k, v in c.items()}}
        rows.append(row)
        y = billed.get((day, mod))
        recon.append({
            "date_pt": day, "model": mod, "billed_jpy": y,
            "est_usd_std": round(c["est_usd_std"], 2),
            "est_usd_long_context_rule": round(c["est_usd_long_context_rule"], 2),
            "implied_jpy_per_usd_std":
                round(y / c["est_usd_std"], 1) if y else None,
            "implied_jpy_per_usd_long_context_rule":
                round(y / c["est_usd_long_context_rule"], 1) if y else None,
        })

    usage = {
        "window_utc": {"start_inclusive": WINDOW_START, "end_exclusive": WINDOW_END,
                       "out_of_window_vrtx_records_skipped": out_of_window},
        "period_utc": {"first_api_message": first, "last_api_message": last},
        "host": "local-secondary",
        "provider_marker": "_vrtx_ in message/tool-use IDs",
        "bucket_timezone": "America/Los_Angeles (fixed UTC-7, matches GCP daily billing)",
        "pricing_usd_per_mtok": {k: {"input": v[0], "output": v[1]} for k, v in PRICES.items()},
        "cost_rules": {
            "std": {"cache_write_5m": CACHE_W, "cache_read": CACHE_R},
            "long_context_rule": {"threshold_prompt_tokens": LONG_CTX_THRESHOLD,
                                  "input_family_mult": LONG_IN_MULT,
                                  "output_mult": LONG_OUT_MULT},
        },
        "by_pt_day_model": rows,
        "sessions": [{"session_id": s, "first_utc": a, "last_utc": b}
                     for s, (a, b) in sorted(sessions.items(), key=lambda x: x[1][0])],
        "scope_note": ("leray-hopf escrow scope only. Machine-wide Vertex usage in the "
                       "same window (setup / unrelated-project sessions, evidenced in "
                       "global prompt history) is billed but not in this aggregate — "
                       "see analysis/billing-reconciliation.md."),
    }
    tot_std = round(sum(c["est_usd_std"] for c in cells.values()), 2)
    tot_prem = round(sum(c["est_usd_long_context_rule"] for c in cells.values()), 2)
    tot_y = sum(v for v in billed.values()) if billed else None
    summary = {
        "billed_jpy_total": tot_y,
        "est_usd_std_total": tot_std,
        "est_usd_long_context_rule_total": tot_prem,
        "blended_implied_jpy_per_usd":
            {"std": round(tot_y / tot_std, 1) if tot_y else None,
             "long_context_rule": round(tot_y / tot_prem, 1) if tot_y else None},
        "by_cell": recon,
        "interpretation": ("Log-side estimates are LOWER BOUNDS on billed usage: the "
                           "billing covers all Vertex traffic of the machine while the "
                           "escrow covers only leray-hopf-related sessions. Residuals "
                           "per cell (esp. opus 2026-07-03) are consistent with the "
                           "known unescrowed sessions; see billing-reconciliation.md."),
    }
    OUT_USAGE.write_text(json.dumps(usage, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_USAGE}\nwrote {OUT_SUMMARY}")
    print(f"cells={len(rows)} sessions={len(sessions)} "
          f"std=${tot_std} long_ctx=${tot_prem} billed=¥{tot_y}")
    if out_of_window:
        print(f"warning: {out_of_window} _vrtx_ record(s) outside "
              f"[{WINDOW_START}, {WINDOW_END}) were excluded", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
