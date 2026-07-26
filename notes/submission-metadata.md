# Microsoft CMT submission metadata

Status: draft pending final claim/Related Work stabilization.

## Proposed title

Formalizing Leray-Hopf in Lean 4 with AI Agents: Harness Design and Reliability Lessons

This is the plain-text rendering of the current manuscript title, whose TeX source uses `Leray--Hopf`.

## Abstract

Large formalization projects require assurance beyond a proof kernel and a successful build. We present a Lean 4 and mathlib artifact containing machine-checked declarations for the existence of Leray-Hopf weak solutions of the unforced incompressible Navier-Stokes equations on the three-dimensional torus and on R^3; at the pinned release, these declarations use no project axioms. The paper also studies a repository-level, agent-orchestrated workflow connecting Issues, isolated Git worktrees, pull requests, specialist review, declaration checks, and runtime controls. Lean's kernel checks a declaration against its type, and a successful build checks compilation, but neither establishes that the proposition expresses the intended mathematics, that public declarations survive refactoring, or that project decisions and review results are recorded under the intended governance. We therefore use an incident-driven assurance and provenance methodology: claims are linked to formal declarations, repository history, redacted session records, incident cards, verification results, and resource and cost records, while reconstructed events and evidence gaps are marked explicitly. The study covers one supervised project and six purposively coded sessions; these records do not estimate failure prevalence or causal guardrail effectiveness. The formalized result concerns the unforced equations on an arbitrary fixed finite interval [0,T] with T > 0, the stated energy-class conditions, and only test functions of the form psi(t)w(x). A formalized weak solution includes a divergence-free velocity field, the weak Navier-Stokes identity, an energy inequality, and an initial-value trace in L2. It does not address uniqueness or higher regularity. Models and tools changed during the project, raw logs are withheld, and human supervision is inseparable from the observed outcome.

Character count: 1882 characters (including spaces; LF-free abstract field).

Counting method: count the exact one-paragraph, LF-free plain-text field with Python 3 `len()` and POSIX `wc -m`; exclude the heading, metadata, and trailing file newline.

The final text must be pasted into CMT and checked against CMT's own character counter before submission. It contains no LaTeX commands. ASCII punctuation is used for portability.

## Synchronization note

The title and the formal-scope sentence must be synchronized if the author changes the manuscript title or the frozen claim/scope records. The draft intentionally makes no Related Work-specific novelty claim, so PR #74 and the remaining Issue #42 baseline work do not require a wording change here; the status remains pending their final stabilization. PR #76 changes submission anonymity and provenance, not this metadata text.
