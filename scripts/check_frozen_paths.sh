#!/usr/bin/env bash
# Freeze gate (issue #90). Only paper/ is editable.
#
# Document-driven development is frozen. Every tracked path outside paper/ is
# read-only: analysis/, claims/, notes/, provenance/, evidence/, scripts/,
# .github/, AGENTS.md, README.md and the Makefile are kept as a record and are
# not maintained for consistency any more. Decisions live in GitHub Issues and
# pull requests, not in committed prose.
#
# Checks two things, because either alone leaves a hole:
#   1. committed changes between the merge base and HEAD;
#   2. staged and unstaged changes to tracked files, so a local
#      `make integrity` catches an edit that has not been committed yet.
#
# Bootstrap: the change that introduces this script is exempt. That is decided
# by whether the script exists in the BASE REF, not in the merge base. A branch
# that forked before the script landed has a merge base without it, and keying
# the exemption off the merge base would hand every such branch a permanent
# bypass with a green required check.
#
# Rename detection is disabled. `git diff --name-only` reports only the
# destination of a rename, so `git mv README.md paper/README.md` would look
# like a paper/ change while deleting a frozen file. With --no-renames the
# deletion and the addition are both reported and judged separately.
#
# Usage: scripts/check_frozen_paths.sh [base-ref]     (default: origin/main)
# Exit:  0 clean, 1 a frozen path changed, 2 the check could not be performed.
set -uo pipefail

SELF_PATH="scripts/check_frozen_paths.sh"
EDITABLE_PREFIX="paper/"
base="${1:-origin/main}"

# Owner-authorized amendments. Each entry is an exact tracked path unfrozen by
# an explicit owner decision recorded in a GitHub issue; the issue reference is
# part of the record. The gate script itself appears here because an amendment
# can only take effect by editing this list. This is tamper-evident, not
# tamper-proof: CI executes the pull request's copy of this script, so any gate
# change is enforced only through diff review.
#
# issue #100 (2026-07-31): INC-005 evidence reconciliation. Host-side records
# overturned the incident card's OOM attribution and detection narrative; the
# owner authorized correcting the affected provenance records.
FREEZE_EXEMPT_PATHS=(
  "scripts/check_frozen_paths.sh"
  "evidence/incidents/INC-005.md"
  "evidence/session-index/de129390-559a-4ecd-950e-3667cf1c1c3c.md"
  "claims/paper-claims.md"
  "analysis/incident-ranking.md"
  "analysis/incident-candidates.md"
)

die() { printf 'freeze gate: %s\n' "$1" >&2; exit 2; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"

# Fail closed rather than silently passing when the base cannot be resolved: a
# shallow clone without the base ref would otherwise produce an empty diff and
# report a green gate that compared nothing.
base_sha=$(git rev-parse --verify --quiet "$base^{commit}") \
  || die "base ref '$base' cannot be resolved (fetch it, or pass another ref)"

if ! git cat-file -e "$base_sha:$SELF_PATH" 2>/dev/null; then
  echo "freeze gate: absent from the base ref; bootstrap change, not enforced"
  exit 0
fi

merge_base=$(git merge-base "$base_sha" HEAD 2>/dev/null) \
  || die "no merge base between '$base' and HEAD"

committed=$(git diff --name-only --no-renames --diff-filter=ACMRD "$merge_base"...HEAD --) \
  || die "git diff against '$merge_base' failed"

# Tracked-only: untracked scratch files are not a repository change until they
# are added, and the committed diff catches them at that point.
pending=$(git status --porcelain --untracked-files=no -- \
          | sed 's/^...//; s/^.* -> //') \
  || die "git status failed"

exempt_filter() {
  # Drop paths present in FREEZE_EXEMPT_PATHS (exact match).
  local line keep
  while IFS= read -r line; do
    keep=1
    for e in "${FREEZE_EXEMPT_PATHS[@]}"; do
      [ "$line" = "$e" ] && { keep=0; break; }
    done
    [ "$keep" = 1 ] && printf '%s\n' "$line"
  done
}

violations=$(printf '%s\n%s\n' "$committed" "$pending" \
             | grep -v '^$' | grep -v "^$EDITABLE_PREFIX" | exempt_filter | sort -u || true)

if [ -n "$violations" ]; then
  echo "freeze gate FAILED: only ${EDITABLE_PREFIX} may change (issue #90)." >&2
  printf '%s\n' "$violations" | sed 's/^/  frozen: /' >&2
  echo >&2
  echo "Document-driven development is frozen. Record the decision in the Issue" >&2
  echo "or the pull request instead of editing a document." >&2
  exit 1
fi

n=$(printf '%s\n%s\n' "$committed" "$pending" | grep -c '^\S' || true)
echo "freeze gate OK (${n} changed path(s), all under ${EDITABLE_PREFIX} or in the owner-authorized exemption list)"
