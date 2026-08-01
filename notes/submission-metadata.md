# Microsoft CMT submission metadata

Status: abstract synchronized with the manuscript (2026-08-01, issue #109;
decision record in issue #73; evidence-coverage narrowing per the owner review
on PR #110 and issue #111 item 1). Byline and repository reference remain
pending (#73).

## Proposed title

Formalizing Leray-Hopf in Lean 4 with AI Agents: Harness Design and Reliability Lessons

This is the plain-text rendering of the current manuscript title, whose TeX source uses `Leray--Hopf`.

## Abstract

Formalization projects that run for weeks require safeguards beyond the proof kernel: the kernel checks a theorem against its stated type, but it does not choose the intended statement, preserve a public interface during refactoring, or manage the agents and computing resources used to produce the proof. We report a Lean 4 and mathlib formalization, with no project axioms, of the existence of Leray-Hopf weak solutions to the unforced Navier-Stokes equations on the three-dimensional torus T^3 and on R^3; to our knowledge, no prior machine-checked formalization establishes this three-dimensional weak existence theorem. During six weeks of development, a workflow defined by the author routed GitHub Issues through isolated Git worktrees and pull requests, and a harness selected mathematical, Lean, interface, and resource checks according to the changed artifact. Four incidents show where these checks detected defects and where they did not, and a claim-to-evidence method links the paper's tagged claims to redacted session records, repository history, verification results, cost estimates, and billing records.

Character count: 1121 characters (including spaces; LF-free abstract field).

Counting method: count the exact one-paragraph, LF-free plain-text field with Python 3 `len()` and POSIX `wc -m`; exclude the heading, metadata, and trailing file newline.

The final text must be pasted into CMT and checked against CMT's own character counter before submission. It contains no LaTeX commands. ASCII punctuation is used for portability.

## Synchronization note

This abstract is the plain-text rendering of the manuscript abstract as of PR #110, which is the six-page revision of PR #106 with one deliberate correction: the evidence-coverage phrase is narrowed to "the paper's tagged claims" (owner review on PR #110; issue #111 item 1), applied to `paper/main.tex` in the same PR. The mathematical-scope details deliberately live in Section 2 of the manuscript, not here. If the author changes the manuscript title or abstract, re-derive this field from the manuscript and update the character count. The earlier draft's deferral of the novelty claim ended when the Related Work baseline stabilized; the claim (CLM-006) is now included. PR #76 changed submission anonymity and provenance, not this metadata text.
