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

# Owner-authorized amendments. Each entry is "path:blob-sha" — an exact
# tracked path unfrozen by an explicit owner decision recorded in a GitHub
# issue, pinned to the git blob hash of the authorized result. The exemption
# admits only that exact content: the one transition the owner approved passes
# the gate, and any later edit (or deletion) of the same path hashes
# differently and is a violation again. The amendment is therefore one-shot,
# not an ongoing bypass, and the pinned hash doubles as an audit record of
# what was authorized.
#
# The gate script itself cannot be hash-pinned (the pin would have to include
# itself), so it carries a plain self-exemption below. That is tamper-evident,
# not tamper-proof — CI executes the pull request's copy of this script, so
# every gate change is enforced only through diff review; pinning would add no
# protection there either.
#
# issue #100 (2026-07-31): INC-005 evidence reconciliation. Host-side records
# overturned the incident card's OOM attribution and detection narrative; the
# owner authorized correcting the affected provenance records.
#
# issue #109 (2026-08-01): the owner authorized synchronizing the CMT abstract
# draft with the post-#106 manuscript abstract (decision record in issue #73).
FREEZE_EXEMPT_PINNED=(
  "notes/submission-metadata.md:984c10c174bca20abf0477f1b7ab6381786e11e5"
  "evidence/incidents/INC-005.md:468838e6516409137c0acb880f962d41a3e87425"
  "evidence/session-index/de129390-559a-4ecd-950e-3667cf1c1c3c.md:6f0e3ab9b8e79f5f3452a212fa00fb1198bd3333"
  "claims/paper-claims.md:74b0041a54c029d375cceadf92c9795abb760e32"
  "analysis/incident-ranking.md:f669c68ea3a2ffa3381fdf8b997752909261f69c"
  "analysis/incident-candidates.md:1ad4ab9df88fa2173f127f54354f7c333360ae80"
)
FREEZE_EXEMPT_UNPINNED=(
  "scripts/check_frozen_paths.sh"
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
  # Drop a path only when it is exempt: unpinned entries match by path alone;
  # pinned entries additionally require the working-tree content to hash to
  # the authorized blob (a missing file fails the hash and stays a violation).
  local line keep e p h
  while IFS= read -r line; do
    keep=1
    for e in "${FREEZE_EXEMPT_UNPINNED[@]}"; do
      [ "$line" = "$e" ] && { keep=0; break; }
    done
    if [ "$keep" = 1 ]; then
      for e in "${FREEZE_EXEMPT_PINNED[@]}"; do
        p="${e%:*}"; h="${e##*:}"
        if [ "$line" = "$p" ] && [ -f "$line" ] \
           && [ "$(git hash-object -- "$line" 2>/dev/null)" = "$h" ]; then
          keep=0; break
        fi
      done
    fi
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
