# Issue #58 figure draft - revised design note

Status: **draft for Author review; not approved artwork**.

The revision deliberately removes the evidence lane, release/attestation sequence,
and optional ChatGPT-export linkage. Those items are either routine, one-off, or
too weakly evidenced to justify space in a paper-scale architecture figure.

## Technical harness figure

The main figure compresses the system into three layers:

1. **Author authority** - the Author defines and adjudicates the mathematical
   contract.
2. **Orchestration** - a model-independent orchestrator decomposes the issue,
   delegates bounded work, monitors progress, and selects assurance according to
   the changed artifact.
3. **Issue-scoped execution** - implementation occurs in an isolated worktree and
   passes distinct semantic and mechanical assurance.

Runtime governance is shown as a foundation under orchestration and execution,
not as a separate evidence-style lane. It retains only the operational controls
that materially shaped parallel Lean work: exclusive worktrees, a shared cache
with a global build lock, and liveness/resource cleanup.

Solid arrows show forward delegation. Red arrows show rework. The semantic return
uses a clear upper lane back to the Author and contract; the technical return is a
short local loop back to implementation. No arrow crosses a box or label.

Read-only scouting and statement refinement are compressed into one dashed,
conditional control. Individual PR gates and release steps are omitted.

## Author-intervention figure

The companion figure uses only three main elements: **Author**, **ChatGPT decision
support**, and **GitHub-mediated project execution**. It distinguishes two paths
into the project workflow:

- Author-issued text transmitted through the GitHub Connector;
- direct Author instruction or correction.

Review findings return to the Author through a separate upper lane. This expresses
the role model in issue #66 without treating message counts or transmission
channels as authority. Issue #70's proposed export reconstruction is omitted
because it is optional, time-bounded, and not itself an operational feature of the
harness.

## Paper-scale simplifications

Model names, session identifiers, issue numbers, evidence codes, individual hosts,
the release-attestation episode, and record-capture mechanics are absent. Fable's
later-phase use and the historical introduction order belong in the caption or
surrounding prose, not in the diagram topology.

Proposed alternative text for the technical figure: A synthesized three-layer
agent harness reconstructed from controls introduced over the Leray-Hopf campaign.
The Author defines and adjudicates an issue contract. A model-independent
orchestrator delegates bounded work and selects assurance. Implementation occurs
in an isolated worktree and undergoes separate semantic and mechanical review.
Semantic findings return to the Author; technical findings return to
implementation. Runtime controls support orchestration and execution.

Proposed alternative text for the companion figure: The Author retains final
authority and may intervene directly. ChatGPT supports investigation, synthesis,
recommendation, and drafting but has no independent final authority. Author-issued
instructions reach the GitHub-mediated agent workflow either directly or through
the GitHub Connector. Review findings and unresolved choices return to the Author.
