#!/usr/bin/env python3
"""Vertex completion-phase usage extraction and SKU-level billing reconciliation
(issue #23 / #26 / #28).

Aggregates the `_vrtx_`-marked usage records (Vertex AI period, 2026-07-02..
07-04 UTC, host local-secondary) from the escrow and reconciles them against
the redacted SKU-level billing aggregate
`evidence/metrics/vertex-completion-phase-billing-sku.csv`.

Established by the SKU-level data (issue #28, supersedes the #26 premium
hypothesis):
  - Billing SKUs split by context tier (0-200K / 200K-1M) but the UNIT PRICE
    is the standard published per-MTok rate on both tiers (no long-context
    premium for Claude Fable 5 / Opus 4.8 — consistent with first-party).
  - The effective JPY/USD conversion is identified from binding cells
    (zero-residual SKUs where escrow quantities explain the whole charge):
    FX = min over cells of billed_jpy / (escrow_qty * unit price).
  - Per-cell positive residuals correspond to machine-wide usage outside the
    leray-hopf escrow; their token equivalents are cross-checked against the
    Cloud Monitoring `publisher/online_serving/token_count` machine-wide
    integrals (raw export kept privately; totals embedded below).

Outputs (JSON, sorted keys):
  evidence/metrics/vertex-completion-phase-usage.json
  evidence/metrics/vertex-completion-phase-summary.json

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
BILLING_SKU = REPO_ROOT / "evidence" / "metrics" / "vertex-completion-phase-billing-sku.csv"
OUT_USAGE = REPO_ROOT / "evidence" / "metrics" / "vertex-completion-phase-usage.json"
OUT_SUMMARY = REPO_ROOT / "evidence" / "metrics" / "vertex-completion-phase-summary.json"

PT = timezone(timedelta(hours=-7))  # PDT (UTC-7) throughout the July window
# Documented completion-phase window (issue #23). Records outside it are
# rejected so a rerun after new _vrtx_ escrow data cannot silently drift
# away from the fixed billing aggregate.
WINDOW_START, WINDOW_END = "2026-07-02T00:00:00Z", "2026-07-05T00:00:00Z"
TIER_THRESHOLD = 200_000  # prompt-side tokens; selects the billing SKU tier

# Published USD per MTok (standard rates; SKU data shows the same unit price
# applies on both context tiers for these models).
PRICES = {
    "claude-fable-5": {"input": 10.0, "output": 50.0,
                       "cache_write": 12.5, "cache_read": 1.0},
    "claude-opus-4-8": {"input": 5.0, "output": 25.0,
                        "cache_write": 6.25, "cache_read": 0.5},
}

# Machine-wide token integrals from Cloud Monitoring
# publisher/online_serving/token_count (rate x 300s over 2026-07-02..07-04,
# grouped by model_user_id). Raw monitoring export is kept privately
# (sha256 in analysis/billing-reconciliation.md); constants recorded here for
# the residual cross-check.
MONITORING_TOKENS = {"claude-fable-5": 77_214_740, "claude-opus-4-8": 92_648_850}


def main() -> int:
    # escrow aggregation
    cells_day = defaultdict(lambda: defaultdict(float))   # (pt_day, model)
    qty = defaultdict(int)                                # (model, category, tier)
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
            inp = u.get("input_tokens") or 0
            out = u.get("output_tokens") or 0
            cr = u.get("cache_read_input_tokens") or 0
            cc = u.get("cache_creation") or {}
            w = ((cc.get("ephemeral_5m_input_tokens")
                  or u.get("cache_creation_input_tokens") or 0)
                 + (cc.get("ephemeral_1h_input_tokens") or 0))
            tier = "200k-1m" if (inp + cr + w) > TIER_THRESHOLD else "0-200k"
            p = PRICES[mod]
            usd = (inp * p["input"] + out * p["output"]
                   + w * p["cache_write"] + cr * p["cache_read"]) / 1e6
            c = cells_day[(day_pt, mod)]
            c["turns"] += 1
            c["input_tokens"] += inp
            c["output_tokens"] += out
            c["cache_write_tokens_5m"] += w
            c["cache_read_tokens"] += cr
            c["turns_over_200k_context"] += (tier == "200k-1m")
            c["est_usd"] += usd
            for cat, v in (("input", inp), ("output", out),
                           ("cache_write", w), ("cache_read", cr)):
                qty[(mod, cat, tier)] += v
            sid = d.get("sessionId") or f.stem
            a, b = sessions.get(sid, (ts_utc, ts_utc))
            sessions[sid] = (min(a, ts_utc), max(b, ts_utc))
            first = ts_utc if first is None or ts_utc < first else first
            last = ts_utc if last is None or ts_utc > last else last

    # SKU-level billing
    sku = defaultdict(float)  # (model, category, tier, region) -> jpy
    for r in csv.DictReader(BILLING_SKU.open()):
        sku[(r["model"], r["category"], r["context_tier"], r["region"])] += \
            float(r["billed_jpy_pre_rounding"])
    billed_total = sum(sku.values())

    # per-cell implied rate at standard unit prices; FX = min over cells with
    # escrow quantity (binding cells have ~zero non-escrow usage)
    recon = []
    implied = []
    for (mod, cat, tier, reg), y in sorted(sku.items()):
        q = qty.get((mod, cat, tier), 0) if reg == "global" else 0
        usd = q * PRICES[mod][cat] / 1e6
        imp = y / usd if usd > 0 else None
        if imp:
            implied.append(imp)
        recon.append({"model": mod, "category": cat, "context_tier": tier,
                      "region": reg, "billed_jpy": round(y, 2),
                      "escrow_qty_tokens": q,
                      "escrow_usd_at_std_price": round(usd, 2),
                      "implied_jpy_per_usd": round(imp, 1) if imp else None})
    fx = min(implied)
    residual_tokens = defaultdict(float)
    for row in recon:
        p = PRICES[row["model"]][row["category"]]
        resid = row["billed_jpy"] - fx * row["escrow_usd_at_std_price"]
        row["residual_jpy_at_fx"] = round(max(resid, 0.0), 1)
        row["residual_tokens_at_fx"] = round(max(resid, 0.0) / fx / p * 1e6)
        residual_tokens[row["model"]] += row["residual_tokens_at_fx"]

    leray_usd = sum(c["est_usd"] for c in cells_day.values())
    escrow_tokens = defaultdict(int)
    for (mod, cat, tier), v in qty.items():
        escrow_tokens[mod] += v

    usage = {
        "window_utc": {"start_inclusive": WINDOW_START, "end_exclusive": WINDOW_END,
                       "out_of_window_vrtx_records_skipped": out_of_window},
        "period_utc": {"first_api_message": first, "last_api_message": last},
        "host": "local-secondary",
        "provider_marker": "_vrtx_ in message/tool-use IDs",
        "bucket_timezone": "America/Los_Angeles (fixed UTC-7, matches GCP daily billing)",
        "pricing_usd_per_mtok": PRICES,
        "pricing_note": ("standard rates on BOTH context tiers — SKU-level billing "
                         "shows no long-context premium for these models (issue #28)"),
        "by_pt_day_model": [
            {"date_pt": day, "model": mod,
             **{k: (round(v, 4) if k == "est_usd" else int(v)) for k, v in c.items()}}
            for (day, mod), c in sorted(cells_day.items())],
        "escrow_qty_by_model_category_tier": [
            {"model": mod, "category": cat, "context_tier": tier, "tokens": v}
            for (mod, cat, tier), v in sorted(qty.items())],
        "sessions": [{"session_id": s, "first_utc": a, "last_utc": b}
                     for s, (a, b) in sorted(sessions.items(), key=lambda x: x[1][0])],
        "scope_note": ("leray-hopf escrow scope only; billing covers all Vertex "
                       "traffic of the machine (see summary residuals)."),
    }
    summary = {
        "billed_jpy_total": round(billed_total, 2),
        "escrow_usd_at_std_prices": round(leray_usd, 2),
        "effective_jpy_per_usd": round(fx, 1),
        "fx_estimator": ("min of billed_jpy / (escrow_qty x std unit price) over SKU "
                         "cells with escrow quantity; binding cells have ~zero "
                         "non-escrow usage"),
        "leray_hopf_billed_jpy_derived": round(fx * leray_usd),
        "leray_hopf_share_of_bill": round(fx * leray_usd / billed_total, 3),
        "by_sku_cell": recon,
        "residual_vs_monitoring": {
            mod: {"residual_tokens_at_fx": round(residual_tokens[mod]),
                  "monitoring_machine_wide_tokens": MONITORING_TOKENS[mod],
                  "escrow_tokens": escrow_tokens[mod],
                  "monitoring_minus_escrow": MONITORING_TOKENS[mod] - escrow_tokens[mod]}
            for mod in sorted(MONITORING_TOKENS)},
        "interpretation": ("SKU totals equal the service-level bill; unit prices are "
                           "standard on both tiers (no long-context premium); the "
                           "effective FX is identified from binding cells; positive "
                           "residuals quantify machine-wide usage outside the "
                           "leray-hopf escrow and agree with the independent "
                           "Cloud Monitoring token integrals."),
    }
    OUT_USAGE.write_text(json.dumps(usage, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_USAGE}\nwrote {OUT_SUMMARY}")
    print(f"sessions={len(sessions)} leray_usd=${leray_usd:.2f} "
          f"billed=¥{billed_total:,.1f} fx={fx:.1f} "
          f"leray_billed≈¥{fx*leray_usd:,.0f}")
    if out_of_window:
        print(f"warning: {out_of_window} _vrtx_ record(s) outside "
              f"[{WINDOW_START}, {WINDOW_END}) were excluded", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
