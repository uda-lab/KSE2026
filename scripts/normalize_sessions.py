#!/usr/bin/env python3
"""Normalize a Claude Code session .jsonl into an analysis-friendly JSONL.

Reads a raw session file (never modified) and writes one compact record per
event: timestamp, event type, role, model, cwd, git branch, and a truncated
text preview. Output is NOT automatically publishable — run redact_check.py
before moving anything into evidence/.

Usage:
  python3 scripts/normalize_sessions.py RAW.jsonl -o OUT.normalized.jsonl \
      [--max-text 500]
"""
import argparse
import json
import sys
from pathlib import Path


def text_of(message) -> str:
    """Best-effort extraction of human-readable text from a message payload."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            t = block.get("type")
            if t == "text":
                parts.append(block.get("text", ""))
            elif t == "tool_use":
                parts.append(f"[tool_use:{block.get('name', '?')}]")
            elif t == "tool_result":
                parts.append("[tool_result]")
            elif t == "thinking":
                parts.append("[thinking]")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("raw", type=Path, help="raw Claude Code session .jsonl")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--max-text", type=int, default=500,
                    help="truncate text preview to this many chars (default 500)")
    args = ap.parse_args()

    n_in = n_out = n_bad = 0
    with args.raw.open() as fin, args.output.open("w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                n_bad += 1
                continue
            msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
            text = text_of(msg)
            rec = {
                "line": n_in,
                "uuid": ev.get("uuid"),
                "parentUuid": ev.get("parentUuid"),
                "sessionId": ev.get("sessionId"),
                "timestamp": ev.get("timestamp"),
                "type": ev.get("type"),
                "role": msg.get("role"),
                "model": msg.get("model"),
                "cwd": ev.get("cwd"),
                "gitBranch": ev.get("gitBranch"),
                "version": ev.get("version"),
                "text_preview": text[: args.max_text],
                "text_truncated": len(text) > args.max_text,
            }
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_out += 1

    print(f"{args.raw}: {n_in} lines -> {n_out} records "
          f"({n_bad} unparsable) -> {args.output}", file=sys.stderr)
    if n_bad:
        print("warning: unparsable lines were dropped; note this in the "
              "session index if material", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
