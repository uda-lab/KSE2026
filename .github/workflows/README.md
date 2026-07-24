# CI workflows

Two workflows, split by cost. `checks` is cheap and unconditional; `paper` is
expensive and conditional. This file records why the split exists, why the
expensive one is constrained, and why the TeX installation was left alone.

## The two workflows

| workflow | trigger | installs TeX | typical duration |
| --- | --- | --- | --- |
| `checks` | every pull request, pushes to `main`, manual dispatch | no | ~22 s |
| `paper` | pull requests and `main` pushes touching `paper/**`, `Makefile` or `.github/workflows/paper.yml`; manual dispatch | yes | ~100 s |

`checks` runs claim-link verification, the raw-log leakage guard, the redaction
scan, the prose scanner and its unit tests, and ChkTeX. `paper` runs all of
those again plus the PDF build, so that a manual dispatch or a `main` push is a
complete validation on its own rather than half of one.

ChkTeX lives in the TeX-free workflow because the Debian `chktex` package is a
standalone 240 kB binary whose only dependencies are `libc6`, `libpcre2-posix3`
and `libtinfo6`; it does not pull in TeX Live. Keeping it in `checks` means the
`make lint` gate added in #59 still runs on every pull request rather than only
on manuscript changes. The install step calls `chktex --version` so that a
silently failed install fails the job instead of letting `make lint` take its
"chktex not installed; skipping" branch and pass a weaker gate.

The three TeX-free gates are defined once, in the `integrity` target of the
`Makefile`, so CI and local runs cannot drift apart.

## Branch protection: which workflow may be required

**The `checks` workflow is the one to require. `paper` must not be required.**

The status context to name in a ruleset is the **job** name, not the workflow
name. The job in `checks.yml` is `integrity`, so the required check to configure
is `integrity` — confirmed on PR #65, where `gh pr checks` reported the context
as `integrity`. Naming `checks` would configure a context that never reports and
would itself cause the permanent-pending failure described below.

GitHub does not report a neutral or passing status for a path-filtered workflow
whose filter does not match — it reports nothing at all. A required check that
is never reported stays pending forever, so making `paper`'s `pdf` job required
would block every pull request that does not touch the manuscript. PR #65, a
scripts-only pull request opened against the issue-61 branch, showed exactly
this: the only status reported was `integrity`, and no `paper` status existed
that a rule could ever have satisfied.

`checks` has no path filter precisely so that it always reports, which is what
makes it safe to require.

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

## Why execution frequency is constrained

Two properties of the old single `build` workflow made it expensive.

It triggered on both `push` and `pull_request` with no branch restriction, so
every commit pushed to a pull-request branch ran the same job twice. Over the
last 165 runs before this change that was 96 `push` runs against 69
`pull_request` runs. `push` is now restricted to `main`, so a pull-request
branch produces one run.

It also had no `concurrency` group, so a run kept going after its commit had
been superseded. Both workflows now key concurrency on the pull request number,
falling back to the ref, with `cancel-in-progress: true`.

The saving is concentrated in one step. In the old workflow the TeX Live
installation took 80-90 s while every other step finished in about 4 s total.
Measured on this repository:

| job | wall time | of which TeX provisioning |
| --- | --- | --- |
| old combined `build` | 95-105 s | 80-90 s |
| new `checks` | 22 s | none (ChkTeX install 12 s) |
| new `paper` | ~100 s | 70-90 s |

Cancellation was verified on run 30117462984: a second push arrived 53 s into
the TeX installation, and the run was cancelled with the lint, verification,
redaction, PDF and upload steps all skipped.

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
