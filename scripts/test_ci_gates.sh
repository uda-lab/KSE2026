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

# check_msg <description> <expected-rc> <actual-rc> <needle> <output>
#
# An exit code alone cannot say *why* a command failed. Several gates here fail
# with the same status for unrelated reasons — a stubbed PATH missing python3
# makes `make lint` exit 2 without ever reaching the branch under test — so a
# test asserting only the number can report `ok` while testing nothing. Every
# negative case that has a distinguishing message asserts the message too.
check_msg() {
  if [ "$2" != "$3" ]; then
    bad "$1 (want rc=$2, got $3)"
    return
  fi
  case $5 in
    *"$4"*) ok "$1 (rc=$3, matched \"$4\")" ;;
    *) bad "$1 (rc=$3 but output lacks \"$4\" — failed for the wrong reason)" ;;
  esac
}

tmp=$(mktemp -d) || exit 2
cleanup() { [ -n "${tmp:-}" ] && [ -d "$tmp" ] && rm -rf -- "$tmp"; }
trap cleanup EXIT

echo "== ChkTeX gate: REQUIRE_CHKTEX must fail when chktex is absent =="

# A PATH with the tools make needs but deliberately without chktex. A silently
# incomplete stub is the classic way this kind of test lies: if `python3` were
# missing, `make lint` would exit 2 on "command not found" and the
# REQUIRE_CHKTEX assertion below would still see the status it wants. Abort
# rather than link what happens to exist.
stub="$tmp/bin"
mkdir -p "$stub"
for b in bash sh make python3 git sed grep cat rm ls mktemp dirname pwd wc echo; do
  if ! p=$(command -v "$b" 2>/dev/null) || ! ln -sf "$p" "$stub/$b"; then
    printf 'cannot build the chktex-free stub PATH: %s is unavailable\n' "$b" >&2
    exit 2
  fi
done

# run_lint <var-for-rc> <make args...> — sets $lint_out to the combined output.
run_lint() {
  lint_out=$( (cd -- "$repo" && env -i PATH="$stub" HOME="$tmp" make lint "$@" 2>&1) )
  lint_rc=$?
}

run_lint
check "chktex absent, unset REQUIRE_CHKTEX skips and passes" 0 "$lint_rc"

run_lint REQUIRE_CHKTEX=1
check_msg "chktex absent, REQUIRE_CHKTEX=1 fails" 2 "$lint_rc" \
  "REQUIRE_CHKTEX is set but chktex is not installed" "$lint_out"

if command -v chktex >/dev/null 2>&1; then
  (cd -- "$repo" && make lint REQUIRE_CHKTEX=1 >/dev/null 2>&1)
  check "chktex present, REQUIRE_CHKTEX=1 passes" 0 "$?"
else
  echo "  skip  chktex present case (chktex not installed here)"
fi

echo "== ChkTeX gate: an empty file list must not pass silently =="
# chktex exits 0 on inputs it cannot open, so LINT_TEX going empty would lint
# nothing. Override it to the single-file case the recipe rejects.
#
# This assertion lives inside `ifdef CHKTEX`, so it is unreachable without
# chktex on PATH: run without it and make exits 2 from the REQUIRE_CHKTEX
# branch instead, which is the status this test wants and would print `ok`
# having executed nothing. Skip when chktex is absent, drop REQUIRE_CHKTEX so
# the assertion is the only thing that can fail, and assert the message.
if command -v chktex >/dev/null 2>&1; then
  out=$( (cd -- "$repo" && make lint LINT_TEX='paper/main.tex' 2>&1) )
  check_msg "LINT_TEX with no section files is rejected" 2 "$?" \
    "LINT_TEX matched only" "$out"
else
  echo "  skip  LINT_TEX assertion (needs chktex on PATH to reach the branch)"
fi

echo "== prose scanner: an empty sections/ must not shrink the gate =="
# The other half of `make lint` discovers its own file list from a glob, so it
# had the identical "passed having read almost nothing" hole: with
# paper/sections/ emptied it reported "OK (1 TeX files)" and exited 0.
pw="$tmp/prose"
mkdir -p "$pw/scripts" "$pw/paper/sections"
cp -- "$repo/scripts/check_prose_style.py" "$pw/scripts/"
cp -- "$repo/paper/main.tex" "$pw/paper/"
prose_out=$( (cd -- "$pw" && python3 scripts/check_prose_style.py 2>&1) )
check_msg "prose scanner rejects an empty sections/" 2 "$?" \
  "matched nothing" "$prose_out"

echo "== redaction gate: a missing scan directory must not shrink the scan =="
# Same class as the empty LINT_TEX list: redact_check.py used to treat a
# missing --dir as zero files, so renaming a public directory narrowed one of
# the three hard gates while it still reported success.
red=$(cd -- "$repo" && python3 scripts/redact_check.py --dir paper --dir nosuchdir 2>&1)
check_msg "redact_check rejects a missing --dir" 2 "$?" "is not a directory" "$red"

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
#
# Returns 99 if a fixture could not be created or staged. Without that, the
# rc=0 expectations below could not tell "the guard correctly ignored this
# path" from "the fixture was never staged, so the guard saw an empty tree" —
# a total staging failure would leave every negative test green.
guard_rc() {
  local d=$1
  shift
  local f
  for f in "$@"; do
    if ! mkdir -p -- "$d/$(dirname -- "$f")" 2>/dev/null \
      || ! ( : >"$d/$f" ) 2>/dev/null \
      || ! git -C "$d" add -f -- "$f" >/dev/null 2>&1; then
      echo 99
      return
    fi
    # Staging can report success and still track nothing (an ignored path
    # without -f, a path git rewrites). Require the file to be in the index.
    if [ -z "$(git -C "$d" ls-files -- "$f")" ]; then
      echo 99
      return
    fi
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

# private/ at other cases and depths. These are the ones a plain `git add .`
# tracks, because .gitignore's `private/*` rule does not cover them either.
d=$(mkrepo); check "Private/ (capitalised)" 1 "$(guard_rc "$d" "Private/leak.txt")"
d=$(mkrepo); check "PRIVATE/ (upper)" 1 "$(guard_rc "$d" "PRIVATE/leak.txt")"
d=$(mkrepo); check "nested docs/private/" 1 "$(guard_rc "$d" "docs/private/leak.txt")"
d=$(mkrepo); check "Private/README.md is NOT the exemption" 1 "$(guard_rc "$d" "Private/README.md")"
d=$(mkrepo); check "'privately/' is not private/" 0 "$(guard_rc "$d" "privately/ok.md")"

# A compressed or backed-up session log is still a session log.
d=$(mkrepo); check "gzipped .jsonl.gz" 1 "$(guard_rc "$d" "s.jsonl.gz")"
d=$(mkrepo); check "backup .jsonl.bak" 1 "$(guard_rc "$d" "s.jsonl.bak")"
d=$(mkrepo); check "compressed .NDJSON.zst" 1 "$(guard_rc "$d" "s.NDJSON.zst")"
d=$(mkrepo); check "plain .json is not JSON Lines" 0 "$(guard_rc "$d" "evidence/ok.json")"

# The staging-failure sentinel must itself work, or every rc=0 case above is
# only as trustworthy as an unchecked `git add`.
d=$(mkrepo); check "guard_rc reports 99 on an unstageable fixture" 99 "$(guard_rc "$d" "nope/")"

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
