#!/usr/bin/env bash
# Regression tests for the CI gate mechanisms that have no other coverage.
#
# Issue #67 requires that "the ChkTeX gate cannot pass while ChkTeX did not
# run" be verified by a test that removes the binary, rather than asserted in
# prose. It also fixed the leakage guard's uppercase-extension blind spot, and
# that behaviour needs a test or it will regress.
#
# Run with `make selftest`. Uses only scratch directories under $TMPDIR; the
# repository is never modified.
set -uo pipefail

repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd) || exit 2
guard="$repo/scripts/check_no_raw_logs.sh"

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  printf '  ok    %s\n' "$1"
}

bad() {
  fail=$((fail + 1))
  printf '  FAIL  %s\n' "$1" >&2
}

# check <description> <expected-rc> <actual-rc>
check() {
  if [ "$2" = "$3" ]; then ok "$1 (rc=$3)"; else bad "$1 (want rc=$2, got $3)"; fi
}

tmp=$(mktemp -d) || exit 2
cleanup() { [ -n "${tmp:-}" ] && [ -d "$tmp" ] && rm -rf -- "$tmp"; }
trap cleanup EXIT

echo "== ChkTeX gate: REQUIRE_CHKTEX must fail when chktex is absent =="

# A PATH with the tools make needs but deliberately without chktex.
stub="$tmp/bin"
mkdir -p "$stub"
for b in bash sh make python3 git sed grep cat rm ls mktemp dirname pwd; do
  p=$(command -v "$b" 2>/dev/null) && ln -sf "$p" "$stub/$b"
done

run_lint() {
  # Extra make arguments are passed through. Runs in the repo with a
  # chktex-free PATH so the skip branch is the one under test.
  (cd -- "$repo" && env -i PATH="$stub" HOME="$tmp" make lint "$@" >/dev/null 2>&1)
  echo $?
}

check "chktex absent, unset REQUIRE_CHKTEX skips and passes" 0 "$(run_lint)"
check "chktex absent, REQUIRE_CHKTEX=1 fails" 2 "$(run_lint REQUIRE_CHKTEX=1)"

if command -v chktex >/dev/null 2>&1; then
  (cd -- "$repo" && make lint REQUIRE_CHKTEX=1 >/dev/null 2>&1)
  check "chktex present, REQUIRE_CHKTEX=1 passes" 0 "$?"
else
  echo "  skip  chktex present case (chktex not installed here)"
fi

echo "== ChkTeX gate: an empty file list must not pass silently =="
# chktex exits 0 on inputs it cannot open, so LINT_TEX going empty would lint
# nothing. Override it to the single-file case the recipe rejects.
(cd -- "$repo" && make lint LINT_TEX='paper/main.tex' REQUIRE_CHKTEX=1 >/dev/null 2>&1)
check "LINT_TEX with no section files is rejected" 2 "$?"

echo "== leakage guard =="

mkrepo() {
  local d="$tmp/r$RANDOM$RANDOM"
  mkdir -p "$d" && git -C "$d" init -q .
  git -C "$d" config user.email t@example.invalid
  git -C "$d" config user.name t
  mkdir -p "$d/private"
  : >"$d/private/README.md"
  git -C "$d" add -f private/README.md
  git -C "$d" commit -qm init
  echo "$d"
}

# guard_rc <repo> <path-to-track...>
guard_rc() {
  local d=$1
  shift
  local f
  for f in "$@"; do
    mkdir -p -- "$d/$(dirname -- "$f")"
    : >"$d/$f"
    git -C "$d" add -f -- "$f"
  done
  (cd -- "$d" && bash "$guard" >/dev/null 2>&1)
  echo $?
}

d=$(mkrepo); check "clean tree (only private/README.md)" 0 "$(guard_rc "$d")"
d=$(mkrepo); check "private/README.md stays exempt" 0 "$(guard_rc "$d" "notes/ok.md")"
d=$(mkrepo); check "lowercase .jsonl" 1 "$(guard_rc "$d" "a.jsonl")"
d=$(mkrepo); check "UPPERCASE .JSONL" 1 "$(guard_rc "$d" "B.JSONL")"
d=$(mkrepo); check "mixed-case .JsOnL" 1 "$(guard_rc "$d" "c.JsOnL")"
d=$(mkrepo); check "lowercase .ndjson" 1 "$(guard_rc "$d" "d.ndjson")"
d=$(mkrepo); check "UPPERCASE .NDJSON" 1 "$(guard_rc "$d" "e.NDJSON")"
d=$(mkrepo); check ".jsonlx is not a log" 0 "$(guard_rc "$d" "f.jsonlx")"
d=$(mkrepo); check "nested private/ payload" 1 "$(guard_rc "$d" "private/raw/g.txt")"
d=$(mkrepo); check "filename containing a space" 1 "$(guard_rc "$d" "weird name.jsonl")"

# Fail-closed: a broken index must report "cannot determine", not "clean".
d=$(mkrepo)
printf 'garbage' >"$d/.git/index"
(cd -- "$d" && bash "$guard" >/dev/null 2>&1)
check "corrupt index fails closed" 2 "$?"

(cd -- "$tmp" && bash "$guard" >/dev/null 2>&1)
check "outside a git tree fails closed" 2 "$?"

echo
printf '%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
