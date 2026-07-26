# Harness architecture figure specification

Tracked by issue #58. The author will draw and approve the final artwork.
The paper must remain readable until that artwork is added.

## Message

The figure should show the final architecture assembled during the project.
The central idea is a division of authority: the author decides
mathematical scope, an orchestrator coordinates bounded work, specialist agents
inspect different artifacts, and repository and GitHub artifacts preserve
Issue scope, review decisions, and merge authority outside agent sessions.
The runtime and evidence systems supply the state needed to trust a result.
The caption should state briefly that individual controls entered the project
at different times.

## Layout

Use a two-column IEEE `figure*`.

Central lifecycle:

1. Author
2. GitHub Issue and, when needed, a statement card
3. Orchestrator in Claude Code
4. Implementing agent on a dedicated branch and Git worktree
5. GitHub pull request candidate
6. Applicable assurance gates
7. Main branch
8. Release commit and recorded full build

Place the author defined repository skill `github-driven-workflow` around
stages 2--7 rather than inside the orchestrator box or as a separate agent. Its
label should say that it enforces the path from Issue to Git worktree to pull
request, prohibits direct pushes to the main branch, and checks the fixed merge
conditions. The visual hierarchy should show the workflow as a
persistent governance layer outside any one agent session.

The assurance gateway is labeled `select checks by changed artifact` and
contains four controls:

- semantic statement review and counterexample search;
- Lean build, axiom check, and public import check;
- comparison of public declarations;
- completed independent review recorded on the pull request.

A read only scout and a statement card are conditional. Semantic findings
return to the author and statement card. Lean and build findings
return to the implementing Git worktree. This split should be visually
prominent because it distinguishes scientific authority from orchestration.

Show the execution environment beneath the lifecycle:

- two local computers and an isolated development container on a virtual private
  server (VPS);
- agents in separate Git worktrees;
- a shared Lean build cache and a global build lock;
- one active agent per Git worktree, process cleanup, liveness checks, and
  monitoring of available memory in the VPS container.

An evidence path should carry session, GitHub Issue, pull request, review,
build, and release records into the escrow and claim manifest.

## Drawing constraints

- Do not include model names, session IDs, evidence codes, Issue numbers, pull
  request numbers, or Lean declaration names.
- Label arrows with short actions: `scope`, `bounded contract`, `committed diff`,
  `review finding`, `attested pass`, and `append evidence`.
- Distinguish semantic feedback to the author and statement card from technical
  feedback to the Git worktree.
- Mark the scout, statement card, and declaration comparison as conditional
  rather than universal stages.
- Keep labels legible at two-column width and in grayscale.
- Supply vector PDF or SVG source and accessible alternative text.

## Caption draft

> Final harness used in the Leray--Hopf project. Under the author's
> authority, an orchestrator routes each GitHub Issue through an implementing
> Git worktree and pull request. Issue scope, review decisions, and merge
> authority remain in repository and GitHub artifacts. Checks are selected
> according to the mathematical, Lean, interface, and runtime artifacts at risk.
> The lower plane shows the shared VPS container and evidence paths. Individual
> controls entered the project at different times.

## Evidence anchors

EV-2076, EV-0925, EV-1669, EV-0247, INC-001, INC-003, INC-004, and INC-005.

## Progress and remaining work

- Complete: the paper now describes the final harness without
  depending on a rendered figure.
- Complete: `github-driven-workflow` as persistent governance outside agent
  sessions, Git worktrees, pull requests, semantic and technical feedback
  paths, the VPS container, and the evidence path are specified.
- Author TODO: draw and approve the final vector artwork.
- Author TODO: confirm the IEEE placement, caption, and accessible alternative
  text.
- Integration TODO: insert the approved figure, rebuild the PDF, and perform
  page-by-page visual inspection.
