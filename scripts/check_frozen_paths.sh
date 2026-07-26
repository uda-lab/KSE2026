#!/usr/bin/env bash
# Freeze gate (issue #90). Only paper/ is editable.
#
# Document-driven development is frozen. Every tracked path outside paper/ is
# read-only: analysis/, claims/, notes/, provenance/, evidence/, scripts/,
# .github/, AGENTS.md, README.md and the Makefile are kept as a record and are
# not maintained for consistency any more. Decisions live in GitHub Issues and
# pull requests, not in committed prose.
#
# This gate compares the working branch against a base ref and fails when any
# tracked file outside paper/ was added, modified, renamed or deleted.
#
# Bootstrap: the pull request that introduces this script is exempt, detected by
# the script being absent from the base ref. That exemption cannot be reused,
# because once merged the script exists in every later base.
#
# Usage: scripts/check_frozen_paths.sh [base-ref]     (default: origin/main)
# Exit:  0 clean, 1 a frozen path changed, 2 the check could not be performed.
set -uo pipefail

SELF_PATH="scripts/check_frozen_paths.sh"
EDITABLE_PREFIX="paper/"
base="${1:-origin/main}"

die() { printf 'freeze gate: %s\n' "$1" >&2; exit 2; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"

# Fail closed rather than silently passing when the base cannot be resolved: a
# shallow clone without the base ref would otherwise produce an empty diff and
# report a green gate that compared nothing.
git rev-parse --verify --quiet "$base^{commit}" >/dev/null \
  || die "base ref '$base' cannot be resolved (fetch it, or pass another ref)"

merge_base=$(git merge-base "$base" HEAD 2>/dev/null) \
  || die "no merge base between '$base' and HEAD"

if ! git cat-file -e "$merge_base:$SELF_PATH" 2>/dev/null; then
  echo "freeze gate: absent from the base ref; bootstrap change, not enforced"
  exit 0
fi

changed=$(git diff --name-only --diff-filter=ACMRD "$merge_base"...HEAD --) \
  || die "git diff against '$merge_base' failed"

violations=$(printf '%s\n' "$changed" | grep -v '^$' | grep -v "^$EDITABLE_PREFIX" || true)

if [ -n "$violations" ]; then
  echo "freeze gate FAILED: only ${EDITABLE_PREFIX} may change (issue #90)." >&2
  printf '%s\n' "$violations" | sed 's/^/  frozen: /' >&2
  echo >&2
  echo "Document-driven development is frozen. Record the decision in the Issue" >&2
  echo "or the pull request instead of editing a document." >&2
  exit 1
fi

n=$(printf '%s\n' "$changed" | grep -c '^' || true)
[ -z "$changed" ] && n=0
echo "freeze gate OK (${n} changed path(s), all under ${EDITABLE_PREFIX})"
