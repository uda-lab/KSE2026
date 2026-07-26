#!/usr/bin/env bash
# Regression tests for the CI gate mechanisms that have no other coverage.
#
# Issue #67 requires that "the ChkTeX gate cannot pass while ChkTeX did not
# run" be verified by a test that removes the binary, rather than asserted in
# prose. It also fixed the leakage guard's uppercase-extension and
# archive-suffix blind spots, and those behaviours need tests or they will
# regress.
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

echo "== ChkTeX gate: chktex must actually be checking something =="
# Every other ChkTeX assertion establishes that the binary is present,
# executable and reading a plausible file list. None of them establishes that
# it reports defects: a stub on PATH that exits 0 satisfies command -v,
# --version, REQUIRE_CHKTEX and the file-list checks at once. Lint a fixture
# with a known Warning 26 and require the failure.
if command -v chktex >/dev/null 2>&1; then
  fixture="$tmp/known-defect.tex"
  printf '\\documentclass{article}\\begin{document}\nfoo ,bar\n\\end{document}\n' >"$fixture"
  chk_out=$(chktex -q -n8 -n9 -n12 -n13 -n17 -n36 "$fixture" 2>&1)
  chk_rc=$?
  if [ "$chk_rc" -eq 0 ]; then
    bad "chktex reports a known defect (rc=0 — chktex is not checking anything)"
  else
    ok "chktex reports a known defect (rc=$chk_rc)"
  fi
  case $chk_out in
    *"Warning 26"*) ok "chktex names the expected warning" ;;
    *) bad "chktex failed but not with Warning 26: $chk_out" ;;
  esac
else
  echo "  skip  chktex content assertion (chktex not installed here)"
fi

echo "== ChkTeX gate: the file list must be regular files and complete =="
if command -v chktex >/dev/null 2>&1; then
  # A directory is readable, and chktex exits 0 after failing to open it. This
  # is why the recipe tests -f rather than -r.
  mkdir -p "$tmp/decoy.tex"
  out=$( (cd -- "$repo" && make lint LINT_TEX="paper/main.tex $tmp/decoy.tex" 2>&1) )
  check_msg "a directory in LINT_TEX is rejected" 2 "$?" "not a regular file" "$out"

  # A tracked section absent from the lint list would go unlinted. Counting
  # cannot see this, so the recipe compares the sets.
  out=$( (cd -- "$repo" && make lint LINT_TEX='paper/main.tex paper/sections/01-introduction.tex' 2>&1) )
  check_msg "a tracked section missing from LINT_TEX is rejected" 2 "$?" \
    "tracked by git but absent" "$out"
else
  echo "  skip  LINT_TEX file-list assertions (need chktex to reach the branch)"
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

# The glob can also match something that is not a readable regular file. The
# count assertion passes in that case, so the readability check is separate.
pw2="$tmp/prose2"
mkdir -p "$pw2/scripts" "$pw2/paper/sections"
cp -- "$repo/scripts/check_prose_style.py" "$pw2/scripts/"
cp -- "$repo/paper/main.tex" "$pw2/paper/"
mkdir -p "$pw2/paper/sections/a.tex"
ln -sf /nonexistent/dangling "$pw2/paper/sections/b.tex"
prose_out=$( (cd -- "$pw2" && python3 scripts/check_prose_style.py 2>&1) )
check_msg "prose scanner rejects a non-file in the glob" 2 "$?" \
  "not a readable file" "$prose_out"

echo "== redaction gate: a missing scan directory must not shrink the scan =="
# Same class as the empty LINT_TEX list: redact_check.py used to treat a
# missing --dir as zero files, so renaming a public directory narrowed one of
# the three hard gates while it still reported success.
red=$(cd -- "$repo" && python3 scripts/redact_check.py --dir paper --dir nosuchdir 2>&1)
check_msg "redact_check rejects a missing --dir" 2 "$?" "is not a directory" "$red"

# is_dir(), not exists(): a regular file has an empty rglob, so exists() would
# accept it and contribute zero files while still reporting success.
red=$(cd -- "$repo" && python3 scripts/redact_check.py --dir paper --dir Makefile 2>&1)
check_msg "redact_check rejects a --dir that is a regular file" 2 "$?" \
  "is not a directory" "$red"

# A directory that exists but has been emptied is the same failure one step
# later: a configured scope contributing nothing, with the gate still green.
mkdir -p "$tmp/emptyscope"
red=$(cd -- "$repo" && python3 scripts/redact_check.py --dir paper --dir "$tmp/emptyscope" 2>&1)
check_msg "redact_check rejects an emptied --dir" 2 "$?" "contains no files" "$red"

# ...but a lone .gitkeep is an affirmative "intentionally empty" marker, which
# this repository already uses in six places. Rejecting it would make
# `make integrity` unpassable for a scope registered before its content exists.
mkdir -p "$tmp/keptscope"
: >"$tmp/keptscope/.gitkeep"
(cd -- "$repo" && python3 scripts/redact_check.py --dir paper --dir "$tmp/keptscope" >/dev/null 2>&1)
check "redact_check accepts a .gitkeep-only scope" 0 "$?"

# The Makefile names the scope separately from the script, so it needs its own
# assertion or a missing directory would surface only as an argparse error.
mkred=$( (cd -- "$tmp" && mkdir -p mk && cd mk && cp -- "$repo/Makefile" . \
  && mkdir -p scripts claims analysis provenance notes paper \
  && cp -- "$repo/scripts/redact_check.py" scripts/ \
  && make redact 2>&1) )
check_msg "make redact names a missing scope directory" 2 "$?" \
  "redaction scope 'evidence' is missing" "$mkred"

echo "== snapshot exporter: name-denylist scrub =="
# The exporter's scrub is gate-adjacent: a name it fails to mask lands in a
# committed snapshot and trips redact_check.py in every environment that
# holds the denylist (issue #79). Three branches need pinning: the
# denylist-absent branch (the one CI always takes) must be inert, the
# denylist-present branch must mask with literal (regex-escaped) matching,
# and scrub_tree must spare identifier fields that downstream consumers
# group on. Tests override the module's file path; the repo's own
# private/redact-names.txt (if any) is never read or required.

python3 - "$repo" "$tmp" <<'PYEOF' >/dev/null 2>&1
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
import export_repo_snapshot as m
m.NAME_DENYLIST_FILE = Path(sys.argv[2]) / "no-such-denylist.txt"
m.NAME_PATTERNS = m.load_name_patterns()
assert m.NAME_PATTERNS == []
assert m.scrub("written by Test Testname today") == "written by Test Testname today"
PYEOF
check "exporter scrub is inert when the denylist file is absent" 0 "$?"

python3 - "$repo" "$tmp" <<'PYEOF' >/dev/null 2>&1
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
import export_repo_snapshot as m
deny = Path(sys.argv[2]) / "deny.txt"
deny.write_text("# comment line\n\nTest Testname\nA.B (Test)\n", encoding="utf-8")
m.NAME_DENYLIST_FILE = deny
m.NAME_PATTERNS = m.load_name_patterns()
assert len(m.NAME_PATTERNS) == 2  # comment and blank lines ignored
assert m.scrub("by Test Testname.") == "by <name-redacted>."
assert m.scrub("A.B (Test)!") == "<name-redacted>!"
assert m.scrub("AxB (Test)") == "AxB (Test)"  # '.' is escaped, not a wildcard
assert m.scrub(m.scrub("by Test Testname.")) == "by <name-redacted>."  # idempotent
PYEOF
check "exporter scrub masks denylisted names literally when the file exists" 0 "$?"

python3 - "$repo" "$tmp" <<'PYEOF' >/dev/null 2>&1
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
import export_repo_snapshot as m
deny = Path(sys.argv[2]) / "deny.txt"
deny.write_text("Test Testname\n", encoding="utf-8")
m.NAME_DENYLIST_FILE = deny
m.NAME_PATTERNS = m.load_name_patterns()
row = {"author_name": "Test Testname", "user_login": "Test Testname",
       "sha": "Test Testname", "parents": ["Test Testname"],
       "labels": ["Test Testname"], "body": "x Test Testname y", "n": 3}
out = m.scrub_tree(row)
assert out["author_name"] == "<name-redacted>"   # content field: masked
assert out["labels"] == ["<name-redacted>"]      # nested content: masked
assert out["body"] == "x <name-redacted> y"
assert out["user_login"] == "Test Testname"      # identifier: untouched,
assert out["sha"] == "Test Testname"             # redact_check flags it loudly
assert out["parents"] == ["Test Testname"]
assert out["n"] == 3
PYEOF
check "exporter scrub_tree masks content fields but spares identifiers" 0 "$?"

echo "== wiring: the make targets must still invoke the guards =="
# Everything above invokes a guard directly, which proves the guard works and
# nothing about whether `make` still calls it. Deleting the chktex line from
# the lint recipe, or dropping leakcheck from integrity, or removing one
# directory from REDACT_DIRS, left the whole suite green. Those are the same
# "reported a pass for a narrower check than configured" defect one level up,
# in the file that wires the gates together.
#
# So: plant a real defect in a scratch copy of the repository and require the
# make target itself to fail.
wire="$tmp/wire"
mkdir -p "$wire"
if ! cp -R -- "$repo/Makefile" "$repo/scripts" "$repo/paper" "$repo/claims" \
  "$repo/analysis" "$repo/provenance" "$repo/notes" "$repo/evidence" "$wire/" 2>/dev/null; then
  bad "could not stage the wiring fixture"
else
  (cd -- "$wire" && git init -q . && git config user.email t@example.invalid \
    && git config user.name t && git add -A >/dev/null 2>&1 && git commit -qm base >/dev/null 2>&1)

  # make lint must reach chktex.
  if command -v chktex >/dev/null 2>&1; then
    sec="$wire/paper/sections/06-conclusion.tex"
    cp -- "$sec" "$sec.orig"
    printf '\nfoo ,bar\n' >>"$sec"
    out=$( (cd -- "$wire" && make lint REQUIRE_CHKTEX=1 2>&1) )
    check_msg "make lint actually runs chktex" 2 "$?" "Warning" "$out"
    mv -- "$sec.orig" "$sec"
  else
    echo "  skip  make lint runs chktex (chktex not installed here)"
  fi

  # make lint must lint the section files by name, not rely on chktex following
  # \input from main.tex. It does follow \input, so a defect in a referenced
  # section is caught either way — but an orphan section, present on disk and
  # not \input anywhere, is only read because LINT_TEX names it.
  if command -v chktex >/dev/null 2>&1; then
    printf 'orphan text ,here\n' >"$wire/paper/sections/99-orphan.tex"
    out=$( (cd -- "$wire" && make lint REQUIRE_CHKTEX=1 2>&1) )
    check_msg "make lint reads section files not reachable from main.tex" 2 "$?" \
      "99-orphan" "$out"
    rm -f -- "$wire/paper/sections/99-orphan.tex"
  else
    echo "  skip  orphan-section lint (chktex not installed here)"
  fi

  # make lint must run the scanner's own unit tests. Breaking a rule the tests
  # assert on, but which the manuscript does not contain, fails the unittest
  # while leaving the manuscript scan clean — so only the unittest wiring can
  # produce the failure.
  scanner="$wire/scripts/check_prose_style.py"
  cp -- "$scanner" "$scanner.orig"
  sed -i 's/^LISTING_END = .*/LISTING_END = r"\\end{NEVERMATCHES}"/' "$scanner"
  out=$( (cd -- "$wire" && make lint 2>&1) )
  check_msg "make lint runs the prose scanner unit tests" 2 "$?" "FAILED" "$out"
  mv -- "$scanner.orig" "$scanner"

  # make lint must reach the prose scanner.
  sec="$wire/paper/sections/06-conclusion.tex"
  cp -- "$sec" "$sec.orig"
  printf '\nspaced -- dash\n' >>"$sec"
  out=$( (cd -- "$wire" && make lint 2>&1) )
  check_msg "make lint actually runs the prose scanner" 2 "$?" "prose style check FAILED" "$out"
  mv -- "$sec.orig" "$sec"

  # make integrity must reach the leakage guard.
  printf '{"role":"user"}\n' >"$wire/evidence/planted.jsonl"
  (cd -- "$wire" && git add -f evidence/planted.jsonl >/dev/null 2>&1)
  out=$( (cd -- "$wire" && make integrity 2>&1) )
  check_msg "make integrity actually runs the leakage guard" 2 "$?" \
    "raw-log leakage detected" "$out"
  (cd -- "$wire" && git rm -q --cached evidence/planted.jsonl >/dev/null 2>&1)
  rm -f -- "$wire/evidence/planted.jsonl"

  # make integrity must reach the redaction scan, in EVERY configured scope.
  # One planted finding per directory, one target invocation each: this is what
  # catches a directory being quietly dropped from REDACT_DIRS.
  for scope in evidence claims analysis provenance notes paper; do
    mkdir -p "$wire/$scope"
    printf 'sk-ant-api03-%s\n' "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
      >"$wire/$scope/planted-secret.md"
    out=$( (cd -- "$wire" && make integrity 2>&1) )
    check_msg "make integrity scans $scope" 2 "$?" "finding" "$out"
    rm -f -- "$wire/$scope/planted-secret.md"
  done

  # `make integrity` must invoke the claim-link verifier, not merely the two
  # sibling gates. A malformed claim is invisible to the leakage and redaction
  # scans, so dropping `verify` from the target must turn this check red.
  printf '\n## CLM-999: invalid wiring fixture\n- Status: candidate\n- Paper location: planned\n- Evidence: EV-9999\n' \
    >>"$wire/claims/paper-claims.md"
  out=$( (cd -- "$wire" && make integrity 2>&1) )
  check_msg "make integrity actually runs claim-link verification" 2 "$?" \
    "EV-9999 not in evidence/manifest.csv" "$out"

fi

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
d=$(mkrepo); check "rotated .jsonl.1" 1 "$(guard_rc "$d" "s.jsonl.1")"

# Double and triple suffixes. A single-strip implementation misses all of these
# while still passing every single-suffix case above, which is how the
# narrowing got through review once already.
# One case per alternative in the suffix list. Without these, deleting any
# single alternative left the suite green while that form stopped being
# detected — the "each leakage pattern is covered by mutation" claim was false
# for seven of them.
for sfx in bz2 xz zst zip lz4 lzma br 7z Z tar gz bak old orig save part tgz tbz2 txz; do
  d=$(mkrepo); check "archive suffix .$sfx" 1 "$(guard_rc "$d" "s.jsonl.$sfx")"
done
d=$(mkrepo); check "bare trailing dot suffix" 1 "$(guard_rc "$d" "s.jsonl.")"
d=$(mkrepo); check "two-digit rotation .jsonl.42" 1 "$(guard_rc "$d" "s.jsonl.42")"
d=$(mkrepo); check "three-digit rotation .jsonl.007" 1 "$(guard_rc "$d" "s.jsonl.007")"

d=$(mkrepo); check "archived .jsonl.tar.gz" 1 "$(guard_rc "$d" "s.jsonl.tar.gz")"
d=$(mkrepo); check "backed-up .jsonl.gz.bak" 1 "$(guard_rc "$d" "s.jsonl.gz.bak")"
d=$(mkrepo); check "rotated .jsonl.gz.1" 1 "$(guard_rc "$d" "s.jsonl.gz.1")"
d=$(mkrepo); check "archived .ndjson.tar.xz" 1 "$(guard_rc "$d" "s.ndjson.tar.xz")"
d=$(mkrepo); check "date-stamped .jsonl.2026-07-25" 1 "$(guard_rc "$d" "s.jsonl.2026-07-25")"
d=$(mkrepo); check "editor backup .jsonl~" 1 "$(guard_rc "$d" "s.jsonl~")"
d=$(mkrepo); check "plain .json is not JSON Lines" 0 "$(guard_rc "$d" "evidence/ok.json")"

# Only a real archive/backup suffix is stripped. Documentation *about* a log is
# not a log, and there is no exemption mechanism to appeal to if it were flagged.
d=$(mkrepo); check "notes/transcript.jsonl.md is documentation" 0 "$(guard_rc "$d" "notes/transcript.jsonl.md")"
d=$(mkrepo); check "schema.ndjson.md is documentation" 0 "$(guard_rc "$d" "evidence/schema.ndjson.md")"

# git ls-files -z exists so that a newline in a path cannot truncate a name and
# hide the extension. #61 tested this; keep it tested.
d=$(mkrepo); check "filename containing a newline" 1 "$(guard_rc "$d" "$(printf 'weird\nname.jsonl')")"

# The staging-failure sentinel must itself work, or every rc=0 case above is
# only as trustworthy as an unchecked `git add`.
d=$(mkrepo); check "guard_rc reports 99 on an unstageable fixture" 99 "$(guard_rc "$d" "nope/")"

# Fail-closed: a broken index must report "cannot determine", not "clean".
d=$(mkrepo)
printf 'garbage' >"$d/.git/index"
(cd -- "$d" && bash "$guard" >/dev/null 2>&1)
check "corrupt index fails closed" 2 "$?"

# GIT_CEILING_DIRECTORIES stops the walk, but a ceiling equal to the current
# directory is ignored — only a strict ancestor halts it. Run from a subdirectory
# so the ceiling is genuinely above the cwd; otherwise this case is a false
# failure whenever TMPDIR sits inside a git tree.
mkdir -p "$tmp/outside"
(cd -- "$tmp/outside" && GIT_CEILING_DIRECTORIES="$tmp" bash "$guard" >/dev/null 2>&1)
check "outside a git tree fails closed" 2 "$?"

echo
printf '%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
