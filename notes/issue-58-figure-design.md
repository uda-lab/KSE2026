# Issue #58 figure draft — design note

Status: **draft for scientific-owner review; not approved artwork**.

Two candidate figures are supplied. The recommended main-paper figure is
`leray-hopf-agent-harness-draft.svg`, which emphasises the technical harness.
`author-interface-provenance-draft.svg` is a separate communication/provenance
figure informed by issues #66 and #70. Keeping them separate avoids making
authority, transmission, implementation, and evidence arrows look interchangeable.

## Visual hierarchy

The lifecycle is the upper left-to-right path. The scientific owner sits above it
as the source of mathematical scope and merge authority. The owner-defined GitHub
workflow encloses the Issue, orchestrator, implementation worktree, pull-request
candidate, and assurance gateway. This boundary predates the later Fable phases;
the orchestrator is model-independent, with Fable shown only as a later-phase
implementation.

Colour and headings separate scientific authority, orchestration, implementation,
semantic review, mechanical verification, runtime governance, and evidence
capture. Shape and line style preserve the distinctions in grayscale.

## Arrow semantics

Solid dark arrows are forward lifecycle transitions. Red arrows are findings that
require rework: semantic findings return to both the scientific owner and the
statement contract, whereas implementation or mechanical findings return to the
issue-scoped worktree. Dotted teal arrows append records to the evidence rail.
The release-candidate full build is deliberately separated from pull-request
assurance.

## Conditional and mandatory controls

The main lifecycle and artifact-selected assurance gateway are mandatory. Dashed
boxes are conditional: read-only scouting, statement-contract refinement, and
public-declaration comparison run only when repository assumptions, mathematical
scope, or the changed public interface require them. Semantic review,
Lean/build/axiom/release-surface checks, and the review-completion record remain
available gateway controls, selected according to the changed artifact.

## Paper-scale simplifications

The execution plane is compressed into four groups rather than showing individual
hosts, processes, locks, or caches. Evidence events are aggregated by record type
instead of drawing one edge from every lifecycle node. The assurance controls are
grouped under one gateway, and detailed retry loops are reduced to two feedback
paths. Repository-specific model names, session identifiers, evidence codes, Issue
numbers, and Lean declaration names are omitted.

## Proposed accessible alternative text

Synthesized end-state architecture reconstructed from controls introduced at
different stages of the Leray--Hopf campaign, rather than one unchanged campaign
configuration. The scientific owner scopes a GitHub Issue and, when required, a
statement contract. A model-independent orchestrator routes work through an
issue-scoped Git worktree, pull-request candidate, artifact-selected assurance
gates, merged project state, release candidate, full-build attestation, and
attested release artifact. Semantic findings return to the owner and contract;
implementation and mechanical findings return to the worktree. Separate rails
show runtime governance and the capture of session, Issue, pull-request, review,
build, and release evidence into a manifest that supports paper claims.

## Companion communication/provenance figure

The companion figure separates the owner's undivided final authority from the
separable functions of ChatGPT decision support, Connector transmission, direct
human intervention, orchestration, implementation, and review. It also shows issue
#70's proposed ChatGPT-export linkage as a dashed, time-bounded conditional path;
the drawing does not imply that the export exists, that a join will succeed, or
that Connector attribution identifies who drafted a message.

Proposed alternative text: The human scientific owner holds final authority.
ChatGPT may investigate, synthesise, recommend, and draft; the GitHub Connector
may transmit owner-issued text, while the owner can intervene directly. GitHub
Issues and pull requests route work to orchestrators, implementers, and reviewers,
whose findings return to the owner. Repository records flow to an evidence
manifest. A private ChatGPT export may optionally support confidence-graded links
to GitHub writes, but raw data remain private and channel evidence alone does not
establish drafting authorship.
