# CI workflows

> **If you are enabling branch protection, read
> [Contexts that must never be required](#contexts-that-must-never-be-required)
> first.** The only status context that is safe to require is **`integrity`**.
> Requiring `pdf` deadlocks every pull request that does not touch the
> manuscript. Requiring `paper` — or any other job name left behind by a
> deleted workflow — deadlocks every pull request permanently. Several such
> names are offered by GitHub's required-checks picker for about a week after
> their last run, and they all look legitimate.

Two workflows, split by cost. `checks` is cheap and unconditional; `paper` is
expensive and conditional. This file records why the split exists, why the
expensive one is constrained, and why the TeX installation was left alone.

## The two workflows

| workflow | job / status context | trigger | installs TeX | typical duration |
| --- | --- | --- | --- | --- |
| `checks` | `integrity` | every pull request, merge-queue entries, pushes to `main`, manual dispatch | no | ~22 s |
| `paper` | `pdf` | pull requests and `main` pushes **that touch** `paper/**`, `Makefile` or `.github/workflows/paper.yml`; manual dispatch | yes | ~90 s |

For `paper`, `branches` and `paths` are ANDed: a push to `main` touching none of
those paths does **not** run it. Manual dispatch is unfiltered and always runs.
Tag pushes trigger neither workflow.

`checks` runs claim-link verification, the raw-log leakage guard, the redaction
scan, the prose scanner and its unit tests, and ChkTeX. `paper` runs all of
those again plus the PDF build, so that a manual dispatch, or a `main` push that
does touch the manuscript, is a complete validation on its own rather than half
of one.

ChkTeX lives in the TeX-free workflow because the Debian `chktex` package is a
standalone 240 kB binary whose only dependencies are `libc6`, `libpcre2-posix3`
and `libtinfo6`; it does not pull in TeX Live. Keeping it in `checks` means the
`make lint` gate added in #59 still runs on every pull request rather than only
on manuscript changes.

There are four ways this gate could pass without actually running, and all four
are closed. None is hypothetical: each shipped at some point in #61 or in the
fixes to it, and each was found by review afterwards rather than by inspection.

**The binary might be missing.** `make lint` skips ChkTeX when `chktex` is not
installed. The install step therefore runs under `shell: bash`, which is
`bash --noprofile --norc -eo pipefail {0}`. Without `pipefail` the default
`bash -e {0}` gives `chktex --version | head -1` the exit status of `head`,
always 0, so a missing binary goes undetected — that was the #61 defect. The
step also calls `command -v chktex`, one name per invocation, because
`command -v a b` returns 0 when *any* name resolves. CI then invokes
`make lint REQUIRE_CHKTEX=1`, which turns the skip branch into an error, so the
Makefile cannot report a pass for a gate that did not run even if the step guard
is weakened again later.

**The file list might be empty.** `chktex` exits 0 on an input it cannot open,
so a stale path would lint nothing and still pass:

```
$ chktex -q 'paper/nosuch/*.tex'; echo $?
chktex: WARNING -- Unable to open the TeX file `paper/nosuch/*.tex'.
0
```

The `Makefile` therefore expands `LINT_TEX` with `$(wildcard)` rather than
passing a glob to `chktex`, and the recipe refuses to run unless the list has
more than one entry, every entry is a regular file, and every section file git
tracks is present in the list. Renaming `paper/sections/` fails the lint instead
of silently emptying it.

That last check compares *sets*, not counts, because counts cancel: delete one
tracked section and add one untracked file and the totals still agree while a
file goes unlinted. It is deliberately one-directional — a tracked file missing
from the list is an error, an untracked new file is not, because the untracked
file is still linted and the alternative would fail every `make lint` run on a
section that has been drafted but not yet staged.

**The binary might not be checking anything.** A stub on `PATH` that exits 0
satisfies `command -v`, `--version`, `REQUIRE_CHKTEX` and every file-list
assertion at once. `make selftest` therefore lints a fixture containing a known
Warning 26 and requires the failure.

**The recipe might stop invoking it.** All of the above test the guard, not the
wiring; deleting the `chktex` line from the `lint` recipe left the entire suite
green. `make selftest` now plants a real defect in a scratch copy and requires
`make lint` itself to fail.

**The same hole existed in two sibling gates and is closed the same way.**
"Discovers its own inputs, then reports success having read almost none of
them" is a property of the pattern, not of ChkTeX, so the review that produced
this section went looking for it elsewhere and found it twice:

- `check_prose_style.py` built its file list from the same glob with no
  assertion. With `paper/sections/` emptied it printed `prose style check OK
  (1 TeX files)` and exited 0. It now requires at least two files.
- The raw-log guard's archive-suffix rule stripped one component, so
  `session.jsonl.tar.gz` — the ordinary result of archiving a log directory —
  stopped being detected. That narrowing was introduced by the commit that was
  widening the guard, and caught only because the reviewer diffed old against
  new over a fixture set rather than reading the patch. Suffixes are now
  stripped repeatedly.
- `redact_check.py` treated a missing `--dir` as zero files and only errored
  when *every* directory was absent, so renaming a public directory narrowed
  one of the three hard gates while it still passed — renaming `evidence/`
  alone took the scan from 66 files to 32, exit 0 both times. A missing scan
  directory, a `--dir` that is a regular file, and a directory that exists but
  is empty are all errors now.

All of these are covered by `make selftest`, which both workflows run — 76
cases. It removes `chktex` from `PATH` and asserts the gate fails, lints a
fixture with a known defect so that a `chktex` which checks nothing is caught,
drives the leakage guard through its uppercase, case-variant `private/`,
compressed-log, documentation-lookalike, newline-in-path, exemption and
fail-closed cases, and asserts each file-list and scan-scope guard above. Each
case asserts the *reason* for a failure, not just its exit status, because
several of these gates fail with the same status for unrelated causes; where an
assertion is unreachable in the current environment the suite prints `skip`
rather than `ok`, so a `chktex`-free host reports 68 passed with 6 skipped
blocks rather than a misleading 76.

The coverage claim is itself checked by mutation rather than asserted: deleting
or weakening each guard individually — `-f` to `-e`, `is_dir` to `exists`, the
word-count bound, the git set comparison, the scan-scope loops, each leakage
pattern — turns the suite red.

Doing that exposed a whole category the suite had been blind to. Every
assertion invoked its guard **directly**, so nothing noticed when a `make`
target stopped calling one: deleting the `chktex` line from `lint`, dropping
`leakcheck` or `redact` from `integrity`, or removing one directory from
`REDACT_DIRS` all left a full green suite. That is the same "narrower than
configured" defect once more, relocated into the file that wires the gates
together, where none of the guard-level tests look. The suite now also plants a
real defect in a scratch copy of the repository — a ChkTeX warning, a spaced
prose dash, a tracked `.jsonl`, and one redaction finding in *each* configured
scope — and requires the make target itself to fail.

Asserting a protection in prose is what let the original guard stay broken;
asserting that a *test* covers something is the same mistake one level up, and
asserting that the test covers the *wiring* is a third.

The three TeX-free gates are defined once, in the `integrity` target of the
`Makefile`, so CI and local runs cannot drift apart.

## Branch protection: which context may be required

**Require exactly one context: `integrity`.**

Not `checks`. The thing a ruleset names is the **job** name, not the workflow
name, and this repository's workflow names and job names deliberately do not
match. `checks.yml` contains a job called `integrity`; `paper.yml` contains a job
called `pdf`. Confirmed empirically rather than assumed: commit `b797810`, which
touched the manuscript inputs, reports exactly `integrity` and `pdf`, and PR #65,
which touched only `scripts/`, reports only `integrity`. Neither ever reports
`checks` or `paper`.

Requiring `checks` would therefore configure a context that is never reported,
which stays pending forever and blocks every pull request. That failure is the
one this whole split exists to prevent, so getting it wrong here would reintroduce
it through the fix.

GitHub does not report a neutral or passing status for a path-filtered workflow
whose filter does not match — it reports nothing at all. A required check that
is never reported stays pending forever, so making `paper`'s `pdf` job required
would block every pull request that does not touch the manuscript. PR #65, a
scripts-only pull request opened against the issue-61 branch, showed exactly
this: the only status reported was `integrity`, and no `paper` status existed
that a rule could ever have satisfied.

`checks` has no path filter precisely so that it always reports, which is what
makes it safe to require.

### Contexts that must never be required

Naming the wrong context is the easiest way to deadlock this repository, and the
required-checks picker actively invites it: GitHub offers any context reported in
roughly the last week, including ones that will never be reported again.

| context | offered by the picker? | verdict | why |
| --- | --- | --- | --- |
| `integrity` | yes | **require this one** | job in `checks.yml`; no path filter, so it always reports |
| `pdf` | yes | never require | job in `paper.yml`; path-filtered, so it reports nothing at all on pull requests that do not touch the manuscript |
| `paper` | yes, until ~2026-07-31 (last reported 2026-07-24) | never require | the **job** name of the deleted `build.yml`. A workflow named `paper` still exists, so this looks current. It will never be reported again |
| `apt-no-install-recommends` | yes, until ~2026-07-31 | never require | a job in the TeX-provisioning benchmark workflow, deleted once its numbers were recorded. Last reported 2026-07-24 |
| `latex-action` | yes, until ~2026-07-31 | never require | same benchmark workflow |
| `texlive-container` | yes, until ~2026-07-31 | never require | same benchmark workflow |
| `copilot-pull-request-reviewer` | yes, until ~2026-07-31 | never require | an app-supplied context, not one of ours. Last reported 2026-07-24. The Copilot workflow is still listed `active` by the API, so unlike the rows above this one may yet report again — which makes requiring it a different but equally bad idea, since it is outside this repository's control |
| `build` | no | not a context | the deleted **workflow**'s name. Verified over all 97 distinct pre-#61 head SHAs carrying a check-run: each reports `paper`, 70 of them twice or more (the push/pull_request double-trigger #61 removed), and the string `build` never appears as a check-run name anywhere in this repository's history |
| `checks` | no | not a context | a workflow name, not a job name. Nothing ever reports under it |

The general rule this table is an instance of: **deleting a workflow does not remove its job names from the picker.** They stay selectable for roughly a week after their last run, look exactly like live contexts, and can never be satisfied again. Any workflow deleted in future adds rows here for that week. This is why the reproduction command below, run against a *recent* pull request, is the authority rather than the picker.

`paper` is the dangerous one, and it is dangerous specifically because of how
this repository changed. Before #61 the workflow was named `build` and its job
was named `paper`, so `paper` is a genuine historical context. After #61 the
*workflow* is named `paper` and its job is named `pdf`. An admin scanning the
picker sees `paper`, recognises it as the name of a workflow that plainly still
exists, and selects it. Nothing will ever report it again, and every pull request
blocks forever.

The general rule, since context names will keep drifting: pick the context from
what a recent pull request actually reported, not from what looks familiar.

```sh
gh pr view <N> --repo uda-lab/KSE2026 --json statusCheckRollup \
  --jq '.statusCheckRollup | map({name, workflowName})'
```

Anything not in that output on a pull request that touches nothing special is
not safe to require.

Merge queues are the other way to hit the same failure. `checks.yml` triggers on
`merge_group` so that `integrity` reports for the `refs/heads/gh-readonly-queue/...`
ref. Without that trigger, enabling "Require merge queue" beside "Require status
checks to pass" — adjacent options in the Rulesets UI — would time out every
queue entry. Any workflow later added as a required check needs the same
trigger.

### Residual gap, stated rather than papered over

The repository has **no branch protection configured at all**, before or after
this change, so nothing here is enforced by GitHub today. This section states
the intended policy for when protection is added, and enabling it is the
repository owner's decision.

The unavoidable consequence of the split is that `paper` cannot be enforced by
branch protection. If a ruleset later requires only `integrity`, a manuscript
pull request whose PDF build failed would not be blocked by GitHub alone.

What does block it today is the merge procedure this repository actually uses:
the `github-driven-workflow` gate refuses to merge unless every *reported* check
on the pull request has succeeded, and `paper` does report on exactly the pull
requests that change the manuscript. That is a procedural gate, not a
server-side one, and it is worth knowing which is which.

Closing the gap properly would mean an always-reported job that inspects the
cumulative pull request diff and demands the PDF result only when manuscript
inputs changed. That was deliberately not built here: issue #61 asks for an
always-running lightweight required workflow plus a separate conditional PDF
workflow, and adding branch-protection plumbing for protection that does not yet
exist is outside its scope.

**Enabling a merge queue would remove that procedural gate too.** The argument
above depends on the merge being performed against the pull request, where
`paper` has reported. A merge queue merges the queue entry instead, and
`paper.yml` has no `merge_group` trigger, so the PDF would be validated only on
the pre-merge head and then again by `push: branches:[main]` after it has
already landed. If a merge queue is ever enabled, decide deliberately what to
do about `paper.yml`, and note that the obvious move does not work:
**`merge_group` cannot be path-filtered.** It accepts `types` and `branches`
only, so adding it to `paper.yml` runs the full ~90 s TeX build on *every*
queue entry, not just manuscript ones. Verified with `actionlint` 1.7.7:

```
$ actionlint mg.yml     # on: merge_group: paths: ['paper/**']
mg.yml:4:5: "paths" filter is not available for merge_group event.
it is only for push, pull_request, pull_request_target events [events]
```

The trade is therefore a TeX build per queue entry against no PDF validation
at merge time. Neither is obviously right, which is why this is left as a
decision rather than a recommendation.

**The gate that was only asserted, and now is not.** Every other ChkTeX
protection establishes that the binary is present, executable, and reading a
plausible file list. None of them establishes that it is *checking* anything: a
stub on `PATH` that exits 0 satisfies `command -v`, `--version`,
`REQUIRE_CHKTEX` and the file-list assertions simultaneously, and an earlier
revision of this file recorded that as an unavoidable residual. It was not
unavoidable. `make selftest` now lints a fixture containing a known Warning 26
and requires the failure:

```
$ printf '#!/bin/sh\nexit 0\n' > stub/chktex && chmod +x stub/chktex
$ PATH=stub:$PATH make selftest 2>&1 | grep -E 'FAIL|passed,'
  FAIL  chktex reports a known defect (rc=0 — chktex is not checking anything)
  FAIL  chktex failed but not with Warning 26:
  FAIL  make lint actually runs chktex (want rc=2, got 0)
  FAIL  make lint reads section files not reachable from main.tex (want rc=2, got 0)
72 passed, 4 failed
```

**What is still not caught.** `redact_check.py` asserts each scan directory
exists and is non-empty, but cannot tell a legitimately deleted file from a
silently lost one, so a *partial* shrink still passes. It also does not recurse
into symlinked directories, so a symlink inside a scanned scope hides its
contents. Both are stated rather than left to be discovered the way the
`| head -1` defect was.

## Why execution frequency is constrained

Two properties of the old single `build` workflow made it expensive.

It triggered on both `push` and `pull_request` with no branch restriction, so
every commit pushed to a pull-request branch ran the same job twice. Over the
last 165 runs before this change that was 96 `push` runs against 69
`pull_request` runs. `push` is now restricted to `main`, so a pull-request
branch produces one run.

It also had no `concurrency` group, so a run kept going after its commit had
been superseded. Both workflows now key concurrency on the pull request number,
falling back to `github.ref`, with `cancel-in-progress: true`. `checks.yml`
names `github.event.merge_group.head_ref` before that fallback; this is
belt-and-braces rather than load-bearing, because for a `merge_group` event
`github.ref` is already the unique `refs/heads/gh-readonly-queue/...` ref. That is
also why the term's absence from `paper.yml` is not an inconsistency to
"fix" — `paper.yml` has no `merge_group` trigger, and `github.ref` would cover
it if one were added.

Three consequences of that key are deliberate. Cancellation applies to `main` as
well, so two merges landing within one run's duration cancel the earlier
commit's run; that is acceptable because every commit reaching `main` was
already gated on its own pull request. `github.run_id` is mixed into the key for
`workflow_dispatch` only, so that a manual full validation and a push to `main`
do not share a group — otherwise a merge landing mid-dispatch would silently
cancel the operator's build, against issue #61's requirement that manual full
builds remain supported. The cost of that third term is that dispatch runs can
never cancel each other: each gets a unique group, so two rapid manual builds
both run to completion. That is the intended trade — a manual build is an
explicit request, and losing one to another is worse than paying for both.

The saving is concentrated in one step. In the old workflow the TeX Live
installation took 80-90 s while every other step finished in about 4 s total.
Measured on 2026-07-25 over every successful run of each workflow, at job level
for wall time and at step level for provisioning. Medians and sample sizes drift
as CI keeps running, so the **ranges** are the claim here and the medians are
given only as a typical value at that date:

| job | wall time | of which provisioning |
| --- | --- | --- |
| new `checks` | 17-28 s (median 22, n=22) | none; ChkTeX install 9-18 s (median 11) |
| new `paper` | 78-142 s (median 89, n=16) | TeX Live 65-110 s (median 77) |

The old combined `build` workflow, measured over its own 163 successful runs
before the split rather than over this window, had a median of 88 s with a
p10-p90 of 81-104 s. An earlier revision of this table quoted "95-105 s" for it;
only 13% of its runs actually fell in that band.

Reproducing the wall-time rows needs the run list; the provisioning rows need
step timings, which run-level JSON does not carry:

```sh
# wall time, per workflow
gh run list --repo uda-lab/KSE2026 --workflow checks.yml --status completed \
  --json createdAt,updatedAt,conclusion --limit 100

# provisioning, per run
gh api repos/uda-lab/KSE2026/actions/runs/<run-id>/jobs \
  --jq '.jobs[].steps[] | select(.name | test("TeX Live|ChkTeX")) |
        [.name, .started_at, .completed_at] | @tsv'
```

An earlier revision of this table quoted a median and an `n` as if they were
fixed, beside a command that returned a different population every time it ran.
Successive reviews caught three different versions of that mistake, which is why
the durable claim is now the range.

Cancellation was verified on run 30117462984: a second push arrived 53 s into
the TeX installation, and the run was cancelled with the lint, verification,
redaction, PDF and upload steps all skipped.

### An invariant nothing enforces

`paper`'s path list must cover every input the PDF build reads. That holds today
only because `paper/main.tex` `\input{}`s nothing outside `paper/`, the
bibliography lives in `paper/references.bib`, the document class comes from TeX
Live, and no `.latexmkrc` exists. Adding a root `.latexmkrc`, a shared `.sty` or
`.bst`, or a figures directory outside `paper/` would silently break it: the PDF
build would stop running on changes that alter the PDF, and no check would fail.
If you move build inputs, update the path list in `paper.yml` in the same
commit.

Note that `pull_request` path filters are evaluated against the pull request's
cumulative diff against its base, not against the newest commit alone. A pull
request that touches `paper/**` in any commit therefore rebuilds the PDF on
every subsequent push. That is the intended behaviour: the artifact must
correspond to the state that would be merged.

## Why a generic TeX image was not adopted

Issue #61 requires that the `apt-get --no-install-recommends` installation not
be replaced by a generic TeX image without measurement. The candidate routes
were run as sibling jobs on identical cold `ubuntu-latest` runners in a single
workflow run (30117463405) so that their timings are directly comparable.

| route | provisioning | compile | total job |
| --- | --- | --- | --- |
| `apt-get --no-install-recommends` (current) | 70 s | 2 s | 74 s |
| `xu-cheng/latex-action@v4` | 92 s (provision and compile combined) | — | 94 s |
| `docker pull texlive/texlive:latest` | 107 s | 3 s | 112 s |

The current installation is the fastest of the three. GitHub-hosted runners are
ephemeral and have no warm image cache, so a generic TeX image pays its full
pull cost on every run: `texlive/texlive:latest` is 5.53 GB, against 393 MB of
TeX actually installed by the apt subset (381 MB `/usr/share/texlive`, 12 MB
`/usr/share/texmf`). Adopting either image route would have made the expensive
job 27% to 51% slower. Both image routes did produce a PDF — the benchmark ran
`make pdf` in the container successfully — so this is a cost argument, not a
correctness one.

The third candidate, a small repository-specific GHCR image rebuilt only when
its Dockerfile changes, **was not measured.** Doing so requires publishing a
package and wiring a build-on-change workflow, which the issue lists as
optional and explicitly not required to close it. It is the one route that
could plausibly beat 70 s, since a layer holding only the packages above would
compress to well under the generic image. It was not pursued because the
saving it competes for is now bounded by roughly 70 s on the minority of pull
requests that touch the manuscript, against the standing cost of maintaining a
Dockerfile, a registry package and a rebuild workflow. If manuscript-touching
runs later become frequent enough for that trade to change, this is the
measurement to take.

The measurement scaffold used for the table above lived in
`tex-provisioning-benchmark.yml` and was removed once the numbers were
recorded; the run it produced is referenced above and remains inspectable.
