# Microsoft CMT submission metadata

Status: submitted to Microsoft CMT on 2026-08-01. The title, synchronized abstract, and named six-page manuscript were submitted from repository revision `da91668ab649c7e3f1e36ddd1dde14ca01aec703`.

## Submitted title

Formalizing Leray-Hopf in Lean 4 with AI Agents: Harness Design and Reliability Lessons

This is the plain-text rendering of the manuscript title, whose TeX source uses `Leray--Hopf`.

## Submitted abstract

Formalization projects that run for weeks require safeguards beyond the proof kernel: the kernel checks a theorem against its stated type, but it does not choose the intended statement, preserve a public interface during refactoring, or manage the agents and computing resources used to produce the proof. We report a Lean 4 and mathlib formalization, with no project axioms, of the existence of Leray-Hopf weak solutions to the unforced Navier-Stokes equations on the three-dimensional torus T^3 and on R^3; to our knowledge, no prior machine-checked formalization establishes this three-dimensional weak existence theorem. During six weeks of development, a workflow defined by the author routed GitHub Issues through isolated Git worktrees and pull requests, and a harness selected mathematical, Lean, interface, and resource checks according to the changed artifact. Four incidents show where these checks detected defects and where they did not, and a claim-to-evidence method links the paper's tagged claims to redacted session records, repository history, verification results, cost estimates, and billing records.

Character count: 1121 characters (including spaces; LF-free abstract field). The field was accepted by the CMT submission form.

## Submitted manuscript

- Byline: Tomoki Uda
- Affiliation: Nanzan University
- Format: named six-page PDF
- Repository revision: `da91668ab649c7e3f1e36ddd1dde14ca01aec703`
- Submission date: 2026-08-01

No private CMT account, submission ID, or other private submission-system data are stored here.

## Camera-ready revision

Status: camera-ready manuscript fixed on 2026-09-07 as tag `v0.1.0`, repository revision `9affe502a22bd341e42d7816174a9bb64b577914` (merge of PR #122). Release: <https://github.com/uda-lab/KSE2026/releases/tag/v0.1.0>, with the CI pdflatex artifact `KSE2026-paper-v0.1.0.pdf` (paper.yml run 34044785111).

- Byline: Tomoki Uda
- Affiliation: Nanzan University
- Format: named six-page PDF
- Content: the reviewer-response revision (issues #119 and #121; PRs #120 and #122) of the submitted revision `da91668` above

The manuscript abstract at `v0.1.0` differs from the abstract submitted to CMT on 2026-08-01 (recorded above); the current text is in `paper/main.tex` at the tagged revision. The camera-ready upload itself and any CMT-side metadata update are performed by the author and are not recorded here.
