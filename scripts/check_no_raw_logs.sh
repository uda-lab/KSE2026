#!/usr/bin/env bash
# Guard against raw session-log leakage into tracked files (AGENTS.md rule 1).
#
# Tracked files must never contain private/ payloads other than the README
# placeholder, nor session logs in JSON Lines form. This runs in CI as a hard
# merge gate and locally via `make integrity`; keeping it in one script means
# both callers test the same predicate.
#
# The check fails closed: any inability to enumerate tracked files is an error,
# not a pass, because a silent pass here would retire the gate without anyone
# noticing.
#
# Exit status: 0 clean, 1 leakage found, 2 cannot determine.
set -uo pipefail

if ! root=$(git rev-parse --show-toplevel 2>/dev/null); then
  echo "check_no_raw_logs: not inside a git working tree" >&2
  exit 2
fi

# git ls-files reports paths relative to the current directory, so anchor at the
# root to guarantee the whole tree is inspected regardless of the caller.
if ! cd -- "$root"; then
  echo "check_no_raw_logs: cannot enter repository root $root" >&2
  exit 2
fi

if ! tmp=$(mktemp); then
  echo "check_no_raw_logs: cannot create a temporary file" >&2
  exit 2
fi
trap 'rm -f -- "$tmp"' EXIT

# -z keeps paths raw and NUL-separated. Without it git C-quotes paths holding
# newlines or quotes, and a trailing quote would stop a name such as
# "weird.jsonl" from matching a line-oriented suffix test. The exit status is
# checked separately from the read loop so a git failure cannot look like an
# empty, and therefore clean, file list.
if ! git ls-files -z >"$tmp"; then
  echo "check_no_raw_logs: git ls-files failed; cannot verify tracked files" >&2
  exit 2
fi

# The private/ test stays case-sensitive because it mirrors the .gitignore rule,
# which is itself case-sensitive. The extension test is case-folded: a log named
# SESSION.JSONL is exactly as much of a leak as session.jsonl, and neither this
# guard's first version nor the inline YAML it replaced caught the uppercase
# form.
leaked=()
while IFS= read -r -d '' path; do
  case $path in
    private/README.md) continue ;;
    private/*)
      leaked+=("$path")
      continue
      ;;
  esac
  # Bracket classes rather than ${path,,}: case folding via parameter expansion
  # needs Bash 4, and on a Bash 3.2 host (stock macOS /bin/bash) it is a fatal
  # "bad substitution" exiting 1 — which this script's own contract defines as
  # "leakage found", turning a tooling failure into a false alarm.
  case $path in
    *.[jJ][sS][oO][nN][lL] | *.[nN][dD][jJ][sS][oO][nN]) leaked+=("$path") ;;
  esac
done <"$tmp"

if [ "${#leaked[@]}" -gt 0 ]; then
  echo "raw-log leakage detected in tracked files:" >&2
  printf '%s\n' "${leaked[@]}" >&2
  echo "move these under private/ (gitignored) and untrack them" >&2
  exit 1
fi

echo "check_no_raw_logs: no raw-log leakage in tracked files"
