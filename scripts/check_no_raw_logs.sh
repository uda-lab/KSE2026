#!/usr/bin/env bash
# Guard against raw session-log leakage into tracked files (AGENTS.md rule 1).
#
# Tracked files must never contain private/ payloads other than the README
# placeholder, nor session logs in JSON Lines form. This runs in CI as a hard
# merge gate and locally via `make integrity`; keeping it in one script means
# both callers test the same predicate.
#
# Exit status: 0 clean, 1 leakage found, 2 cannot determine (no git tree).
set -uo pipefail

if ! root=$(git rev-parse --show-toplevel 2>/dev/null); then
  echo "check_no_raw_logs: not inside a git working tree" >&2
  exit 2
fi

# git ls-files is relative to the current directory, so anchor at the root to
# guarantee the whole tree is inspected regardless of the caller's location.
if ! cd -- "$root"; then
  echo "check_no_raw_logs: cannot enter repository root $root" >&2
  exit 2
fi

# grep exits 1 when nothing matches, which is the healthy case, so the pipeline
# status is deliberately not consulted: emptiness of $leaked is the verdict.
# `git ls-files` C-quotes unusual paths, so one record per line holds.
leaked=$(git ls-files \
  | grep -E '^private/|\.(jsonl|ndjson)$' \
  | grep -v '^private/README\.md$')

if [ -n "$leaked" ]; then
  echo "raw-log leakage detected in tracked files:" >&2
  printf '%s\n' "$leaked" >&2
  echo "move these under private/ (gitignored) and untrack them" >&2
  exit 1
fi

echo "check_no_raw_logs: no raw-log leakage in tracked files"
