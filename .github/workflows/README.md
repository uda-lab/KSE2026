# CI workflows

> **If you are enabling branch protection, read
> [Contexts that must never be required](#contexts-that-must-never-be-required)
> first.** The only status context that is safe to require is **`integrity`**.
> Requiring `paper` deadlocks every pull request permanently; requiring `pdf`
> deadlocks every pull request that does not touch the manuscript. Both are
> offered by GitHub's required-checks picker and both look legitimate.

Two workflows, split by cost. `checks` is cheap and unconditional; `paper` is
expensive and conditional. This file records why the split exists, why the
expensive one is constrained, and why the TeX installation was left alone.

## The two workflows

| workflow | job / status context | trigger | installs TeX | typical duration |
| --- | --- | --- | --- | --- |
| `checks` | `integrity` | every pull request, merge-queue entries, pushes to `main`, manual dispatch | no | ~23 s |
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

There are two ways this gate could pass without actually running, and both are
closed. Neither is hypothetical: the first shipped broken in #61 and was caught
by review afterwards.

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
more than one entry, every entry is a regular file, and the number of section
files on disk matches the number git tracks. Renaming `paper/sections/` fails
the lint instead of silently emptying it.

**The same hole existed in two sibling gates and is closed the same way.**
"Discovers its own inputs, then reports success having read almost none of
them" is a property of the pattern, not of ChkTeX, so the review that produced
this section went looking for it elsewhere and found it twice:

- `check_prose_style.py` built its file list from the same glob with no
  assertion. With `paper/sections/` emptied it printed `prose style check OK
  (1 TeX files)` and exited 0. It now requires at least two files.
- `redact_check.py` treated a missing `--dir` as zero files and only errored
  when *every* directory was absent, so renaming a public directory narrowed
  one of the three hard gates while it still passed — measured at 66 files
  scanned before and 27 after, exit 0 both times. A missing scan directory is
  now an error.

All of these are covered by `make selftest`, which both workflows run. It
removes `chktex` from `PATH` and asserts the gate fails, drives the leakage
guard through its uppercase, case-variant `private/`, compressed-log, exemption
and fail-closed cases, and asserts the two file-list guards above. Each case
asserts the *reason* for a failure, not just its exit status, because several
of these gates fail with the same status for unrelated causes; where an
assertion is unreachable in the current environment the suite prints `skip`
rather than `ok`. Asserting a protection in prose is what let the previous
guard stay broken.

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
| `paper` | yes, for about a week after the last pre-#61 run | never require | the **job** name of the deleted `build.yml`. A workflow named `paper` still exists, so this looks current. It will never be reported again |
| `build` | no | not a context | the deleted **workflow**'s name. Verified over 16 sampled pre-#61 commits: each reports a check-run named `paper` — several report it twice, from the push/pull_request double-trigger #61 removed, and some also carry `copilot-pull-request-reviewer` — and none reports `build` |
| `checks` | no | not a context | a workflow name, not a job name. Nothing ever reports under it |

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
`merge_group` so that `integrity` reports for the `refs/gh-readonly-queue/...`
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
already landed. If a merge queue is ever enabled, add `merge_group` to
`paper.yml` at the same time — its path filter still applies, so non-manuscript
entries stay free.

**What no arrangement of these guards can catch.** Every ChkTeX protection here
establishes that the binary is present, executable, and reading a plausible file
list. None of them establishes that it is really checking anything: a stub on
`PATH` that exits 0 satisfies `command -v`, `--version`, `REQUIRE_CHKTEX` and
the file-list assertion simultaneously. Verified — `printf '#!/bin/sh\nexit 0\n'`
as `chktex` gives `make lint REQUIRE_CHKTEX=1` exit 0. Closing that would need an
assertion about content, such as linting a fixture with a known defect and
requiring the failure. It is recorded here rather than left for someone to
discover the way the `| head -1` defect was discovered.

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
`github.ref` is already the unique `refs/gh-readonly-queue/...` ref. That is
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
Measured on this repository over **the first runs after the #61 split, up to
commit `aeeb465` (2026-07-25)** — the sample is stated because it is a fixed
window, not a live figure; re-running the command below on a later population
gives different numbers, and the medians have already moved by a second or two:

| job | wall time | of which TeX provisioning |
| --- | --- | --- |
| old combined `build` | 95-105 s | 80-90 s |
| new `checks` | 23 s median (17-28, n=12) | none (ChkTeX install 12-13 s) |
| new `paper` | 90 s median (78-142, n=8) | 70-90 s |

```sh
gh run list --repo uda-lab/KSE2026 --workflow checks.yml \
  --status completed --json createdAt,updatedAt --limit 12
```

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
