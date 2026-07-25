# CI workflows

This repository uses two workflows with different cost and trigger policies.
`checks` is the always-running, TeX-free gate. `paper` is the conditional PDF
build. The current operational contract is recorded here; review history and
mutation experiments belong in PR #69 and its evidence comments.

## The two workflows

| workflow | job / status context | trigger | TeX | timeout |
| --- | --- | --- | --- | --- |
| `checks` | `integrity` | every pull request, merge-queue entry, push to `main`, manual dispatch | no | 10 min |
| `paper` | `pdf` | pull requests and `main` pushes touching the listed manuscript paths; manual dispatch | yes | 20 min |

`checks` runs:

- `make integrity` — claim-link verification, raw-log leakage detection, and
  the redaction scan;
- `make lint REQUIRE_CHKTEX=1` — the prose scanner, its unit tests, and ChkTeX;
- `make selftest` — regression tests for the gate mechanisms themselves.

`paper` repeats those checks, then runs `make pdf` and uploads `build/main.pdf`.
Pull-request artifacts are retained for 7 days; `main` and manual-dispatch
artifacts for 30 days.

The `paper` path filter is currently:

```text
paper/**
Makefile
.github/workflows/paper.yml
```

For `paper`, a `push` branch filter and the path filter are combined: a push to
`main` that touches none of those paths does not run the workflow. Manual
dispatch is unfiltered. Tag pushes trigger neither workflow. The path list must
cover every input read by the PDF build; adding a root `.latexmkrc`, shared
`.sty`, bibliography, or figures directory outside `paper/` requires updating
the workflow and this invariant together.

## Gate contract

ChkTeX is installed in the TeX-free job as a standalone package. Its install
step uses `shell: bash`, which enables `pipefail`; the two required binaries are
checked and executed separately. CI passes `REQUIRE_CHKTEX=1`, so an absent
ChkTeX cannot be silently converted into a successful skip.

The Makefile also validates the ChkTeX input list before invoking it: the list
must contain regular files, and every tracked `paper/sections/*.tex` file must
be present. The prose scanner and redaction scanner apply analogous checks so a
missing or empty configured scope cannot narrow a green run.

`make selftest` exercises both the individual guards and their wiring. It
checks that ChkTeX reads a known-defect fixture, that `make lint` and
`make integrity` still invoke their configured checks, that each public
redaction directory is scanned, that the raw-log guard detects case variants,
archive/backup/rotation suffixes, and nested `private/` paths, and that broken
Git metadata fails closed. The current suite reports 81 cases. The claim-link
verifier is an existing Python program outside this PR's implementation diff;
the suite verifies that `make integrity` invokes it with a malformed-claim
fixture, while its internal parser semantics remain a separate follow-up test
surface.

The raw-log guard treats tracked JSON Lines files and their compressed,
rotated, backed-up, and archive-suffixed forms as leakage. It exempts only the
tracked `private/README.md` placeholder. Documentation such as
`transcript.jsonl.md` is not a log. The redaction scan covers exactly the
directories named by `REDACT_DIRS` in `Makefile`:

```text
evidence claims analysis provenance notes paper
```

## Branch protection and status contexts

If branch protection is enabled, require exactly `integrity`. It is an
unfiltered job in `checks.yml`, so it reports for every pull request. Do not
require `pdf`: the path-filtered `paper` workflow reports nothing for unrelated
pull requests. The repository currently has no branch protection configured;
enabling it remains an owner decision.

| name | status | reason |
| --- | --- | --- |
| `integrity` | require | live, unfiltered job in `checks.yml` |
| `pdf` | never require | conditional job in `paper.yml` |
| `paper` | never require | historical job name from the deleted `build.yml`; a workflow with this name is still present, so the picker is misleading |
| `apt-no-install-recommends`, `latex-action`, `texlive-container` | never require | historical jobs from the removed TeX provisioning benchmark |
| `copilot-pull-request-reviewer` | never require | external app context outside this repository's control |
| `build`, `checks` | not status contexts | workflow names, not job names |

GitHub can keep historical job names in the required-check picker for a short
period. Select a required context from a recent pull request's actual check
run, not from a familiar workflow name:

```sh
gh pr view <N> --repo uda-lab/KSE2026 --json statusCheckRollup \
  --jq '.statusCheckRollup | map({name, workflowName})'
```

`checks.yml` also listens for `merge_group`, so `integrity` reports for a merge
queue entry. `paper.yml` is intentionally not a required check and has no
`merge_group` trigger: GitHub does not support path filters on `merge_group`,
so adding that trigger would run the expensive TeX build for every queue entry.
If a merge queue is enabled, the owner must choose deliberately between that
cost and accepting that the conditional PDF build is post-merge validation.

There is no server-side conditional required-check job today. Consequently,
requiring only `integrity` would not by itself block a manuscript PR whose PDF
build fails. The repository's current merge procedure checks every status that
was actually reported, so `paper` failures block manuscript merges when the
workflow runs. A future always-running aggregator could make that policy
server-enforced; adding it is outside this CI follow-up.

## Concurrency and frequency

Both workflows cancel an older run when a newer run for the same PR, merge
queue entry, or ref starts. This applies to pushes to `main`, which is safe
because a commit reaches `main` only after its pull request checks. Manual
dispatch includes `github.run_id` in its group, so an operator's full run is
not cancelled by a push and separate manual runs do not cancel each other.

The observed median durations as of 2026-07-25 were approximately 22 seconds
for `checks` and 89 seconds for `paper`, including about 77 seconds of TeX
provisioning. The path split keeps that provisioning off unrelated pull
requests. The jobs have explicit timeouts so a wedged package install cannot
hold a required check for GitHub's full default timeout.

The workflow intentionally does not create release archives. Tag pushes do not
trigger either workflow; durable publication artifacts require a separate
archival decision.
