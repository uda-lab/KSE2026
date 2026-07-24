# Harness architecture figure specification

Tracked by issue #58. The scientific owner will draw and approve the final artwork.
The paper must remain readable until that artwork is added.

## Message

The figure presents a synthesized end-state architecture reconstructed from
controls introduced at different stages, not a configuration that existed
throughout the campaign. It separates scientific authority, implementation,
semantic adjudication, mechanical verification, runtime governance, and
evidence capture.

## Layout

Use a two-column IEEE `figure*`.

Central lifecycle:

1. Scientific owner
2. Issue and statement contract
3. Orchestrator
4. Issue-scoped implementing worktree
5. Pull request candidate
6. Applicable assurance gates
7. Merged project state
8. Release candidate
9. Full-build attestation
10. Attested release artifact

The assurance gateway is labeled `select gates by changed artifact` and
contains four distinct controls:

- semantic statement review and counterexample search;
- Lean build, axiom pin, and release-surface check;
- public-declaration comparison;
- review-completion record.

A read-only scout and a statement contract are conditional controls, used when
repository assumptions or mathematical scope require them. Semantic findings
return to the scientific owner and statement contract. Implementation and
mechanical findings return to the issue worktree. PR assurance advances a
candidate into the merged project state; release-candidate attestation is a
separate full-build boundary.

Two horizontal rails span the lifecycle:

- operational substrate: exclusive worktree ownership, liveness checks, shared
  build cache, global build lock, process cleanup, and available-memory monitoring;
- evidence rail: session, issue, PR, review, build, and release artifacts flow to
  the escrow/manifest and then to paper claims.

## Drawing constraints

- Use generic reader-facing terms, not model names, session IDs, EV codes, issue
  numbers, or Lean declaration names.
- Label arrows with short actions: `scope`, `bounded contract`, `committed diff`,
  `review finding`, `attested pass`, and `append evidence`.
- Distinguish semantic feedback to the owner/contract from technical feedback
  to the worktree.
- Mark the scout, statement contract, and declaration comparison as conditional
  rather than universal stages.
- Keep labels legible at two-column width and in grayscale.
- Supply vector PDF or SVG source and accessible alternative text.

## Caption draft

> Synthesized end-state architecture reconstructed from controls introduced at
> different stages of the Leray--Hopf campaign. Scientific authority,
> implementation, semantic adjudication, mechanical verification, runtime
> governance, and evidence capture follow separate paths; applicable checks are
> selected by the changed artifact, and release attestation occurs after pull-
> request assurance.

## Evidence anchors

EV-2076, EV-0925, EV-1669, EV-0247, INC-001, INC-003, INC-004, and INC-005.

## Progress and remaining work

- Complete: the paper now describes the synthesized end-state harness without
  depending on a rendered figure.
- Complete: lifecycle, conditional controls, feedback paths, operational rail,
  evidence rail, PR-assurance boundary, and release-attestation boundary are
  specified.
- Owner TODO: draw and approve the final vector artwork.
- Owner TODO: confirm the IEEE placement, caption, and accessible alternative
  text.
- Integration TODO: insert the approved figure, rebuild the PDF, and perform
  page-by-page visual inspection.
