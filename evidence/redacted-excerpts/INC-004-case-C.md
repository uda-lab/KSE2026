# INC-004 / Case C — PR #120 の公開定理 `edge_inf_eq_schwartz_tensor` 消失のマージ前検出（2026-07-10）

- **Incident card:** `evidence/incidents/INC-004.md`
- **論文の対応箇所:** §IV「Public declarations during refactoring」（`paper/sections/04-incidents.tex`），claim CLM-008
- **Session:** `7e6156bf-4a4b-40e2-aa46-95822f4d9aa7`（host local-main，`evidence/session-index/7e6156bf-4a4b-40e2-aa46-95822f4d9aa7.md`）
- **Evidence ID:** EV-1669（メイン transcript，`claude-projects/research-lean/7e6156bf-4a4b-40e2-aa46-95822f4d9aa7.jsonl`）
- **抜粋範囲:** 同 JSONL の L436〜L513（2026-07-10T00:12〜00:39Z）
- **GitHub 側:** leray-hopf#120（`evidence/repository-snapshots/leray-hopf/issues.json`）
- **本抜粋が支える記述:** 論文の「one public theorem on the R^3 side, with no downstream users, was omitted from the theorems to reconnect and disappeared. Neither the build nor an earlier review of module structure noticed」「A separate reviewer compared the public declaration inventory before and after the refactor, statement by statement. The theorem was restored with its original statement」

表記: orchestrator = メインセッションの assistant（この session では日本語で応答），`prrev-111-1` = 宣言単位レビュー担当の reviewer agent，`glue-111` = 実装担当の coder agent．引用は原文のまま．`[…]` は省略．

## 1. 00:12:31Z — orchestrator → `prrev-111-1`: verdict の要求（L437）

> You went idle without reporting. Send your pr-review verdict now: PASS or findings (file:line, severity blocking/non-blocking, evidence), covering statement integrity of the public declarations, no new sorry/axiom/maxHeartbeats, hypothesis minimality of the generic module, deletion completeness, and docstring accuracy.

## 2. 00:12:57Z — `prrev-111-1` の verdict（L441）

> VERDICT: FINDINGS (1 blocking, 1 non-blocking). Not a clean PASS.
>
> Method: diffed every public declaration's exact statement between `main` and this branch for both lane files (not just the diff hunks — I re-extracted signatures via regex and did full-file tail diffs). Everything in both lane files from `convFormL2_extends` (R3) / `convFormL2_cont_fixedTest` (Torus) onward — including `r3ConvectionGapOp_holds`, `r3ConvectionGapOp_exists`, `r3_NSForms_exists`, `torusConvectionGap_holds`, and the tail decls — is byte-identical to main. No new `sorry`/`axiom`/`opaque`/`unsafe`/`ALLOW_*` anywhere. `set_option` count and values unchanged in both lane files vs main.
>
> BLOCKING — silent deletion of a public declaration, LerayHopf/R3/ConvectionExtension.lean:
> `edge_inf_eq_schwartz_tensor` was a public theorem on main (main:LerayHopf/R3/ConvectionExtension.lean:980-983, NOT `private`):
> ```
>   theorem edge_inf_eq_schwartz_tensor :
>       edgeSlot2 ⊓ edgeSlot3 = LinearMap.range (TensorProduct.mapIncl schwartzSpan schwartzSpan) :=
>     LerayHopf.R3.TensorIntersection.range_map_subtype_inf_range_map_subtype schwartzSpan
> ```
> It is completely absent from the new R3 file (grep confirms zero occurrences) — deleted along with its sole use site inside what's now the generic module's private `psi_agree`, with no replacement wrapper added. Evidence this is a real gap, not intentional symmetry:
>   1. Torus kept its counterpart: `edge_inf_eq_galerkin_tensor` is preserved verbatim as a thin wrapper at LerayHopf/Torus/ConvectionExtension.lean:97-105.
>   2. The new shared module's own docstring (LerayHopf/Analysis/TensorEdgeGluing.lean:55-57) explicitly claims: "the tensor-intersection identity's local name (`edge_inf_eq_schwartz_tensor`/`edge_inf_eq_galerkin_tensor` — same content, inlined here from `TensorIntersection` and re-exposed per lane under the lane's own name)" — true for Torus, false for R3.
> Nothing else in-repo currently calls it (checked via `git grep` across all of main), so this doesn't break the build, but it's an advertised public name silently dropped, contradicting both the sibling lane and the new module's own docs. Fix: add the one-line wrapper to R3 mirroring Torus's `edge_inf_eq_galerkin_tensor`.
>
> NON-BLOCKING — stale docstring, LerayHopf/Torus/ConvectionExtension.lean:39: […]

## 3. 00:13:07Z〜00:13:21Z — orchestrator: 差し戻し（L443・L444）

> pr-review が blocking 1 件（R3 側の公開定理 `edge_inf_eq_schwartz_tensor` の無断削除 — Torus 側は wrapper 保持で非対称）+ non-blocking 1 件（Torus ヘッダの `gInv` 記述が虚偽化）を検出。glue-111 に修正を差し戻します。

`glue-111` への指示（抜粋）:

> 1. BLOCKING: `edge_inf_eq_schwartz_tensor` was public on main (R3/ConvectionExtension.lean:980-983) and is now silently gone […]. Restore it in the R3 file as a one-line wrapper mirroring the Torus one, with its exact main-branch statement […]

## 4. 00:17:23Z — `glue-111` の修正報告（L458）

> Both fixed, one commit `05f3967` on `issue-111-pr1-tensor-glue`:
>
> 1. Restored `edge_inf_eq_schwartz_tensor` in R3/ConvectionExtension.lean as a one-line wrapper right after the `detDomain` wrapper, mirroring Torus's `edge_inf_eq_galerkin_tensor` exactly, same statement it had on main:
>    `edgeSlot2 ⊓ edgeSlot3 = LinearMap.range (TensorProduct.mapIncl schwartzSpan schwartzSpan)`, proved via `LerayHopf.R3.TensorIntersection.range_map_subtype_inf_range_map_subtype schwartzSpan`.
> 2. Torus/ConvectionExtension.lean header: dropped the stale `gInv — left-inverse of detDomain.subtype` bullet […]
>
> Both files build clean individually, full `lake build` (3179 jobs) green, no new warnings in either edited region.
>
> ```
> $ ./scripts/agent-preflight.sh > /tmp/preflight-111-1b.log 2>&1; echo exit=$?; tail -3 /tmp/preflight-111-1b.log
> exit=0
> OK: LerayHopf.localCompactness_R3_of_ballCompact — Core-clean (no project axioms, no sorryAx).
> AXIOM LIVE PIN OK — all 4 declarations match their pinned axiom sets (R3: 0 project axioms — KERNEL-ONLY, 𝕋³: 0 project axioms — KERNEL-ONLY).
> PREFLIGHT OK
> ```

## 5. 00:17:37Z〜00:17:43Z — orchestrator による確認と push（L461・L462）

```text
$ grep -n "edge_inf_eq_schwartz_tensor" LerayHopf/R3/ConvectionExtension.lean | head -3; git log --oneline main..HEAD
1025:theorem edge_inf_eq_schwartz_tensor :
05f3967 refactor(dedup): restore edge_inf_eq_schwartz_tensor wrapper; fix stale header list
5528204 refactor(dedup): rewire Torus ConvectionExtension onto shared TensorEdgeGluing (issue #111 PR-1, 3/3)
e39838e refactor(dedup): rewire R3 ConvectionExtension onto shared TensorEdgeGluing (issue #111 PR-1, 2/3)
5a89347 refactor(dedup): extract shared tensor/edge-gluing module (issue #111 PR-1, 1/3)
```

## 6. 00:18:08Z〜00:18:15Z — PR #120 の作成（L464・L466）

PR 本文（`gh pr create` 入力）の該当箇所:

> ## Reviews (in-house, pre-PR)
> - modularity-reviewer: PASS (import surface clean, no cycles, thin instantiations verified, no generality leaks). […]
> - pr-reviewer: 1 blocking finding — `edge_inf_eq_schwartz_tensor` silently dropped on the R3 side — fixed in 05f3967 (restored with its exact main-branch statement); 1 stale-docstring fix.

結果:

```text
https://github.com/uda-lab/lean-pde/pull/120
route: codex (dispatched)
```

## 7. 00:38:54Z — マージ（L513）

`gh pr merge 120 --merge` の本文（Bash tool 入力）:

> Gates: local preflight PREFLIGHT OK + AXIOM LIVE PIN OK (orchestrator-verified); guards pass; review evidence = @codex review comment on HEAD 05f3967 ('Didn't find any major issues' […]); in-house pr-reviewer blocking finding fixed pre-merge; modularity-reviewer PASS.

## 抜粋範囲の境界

修正 commit `05f3967` 以後，マージまでの間に `prrev-111-1` からの独立したメッセージは
メイン transcript にも同 agent の transcript（EV-1639〜EV-1668 の範囲）にも現れない．
本 transcript が示す修正後の確認は，orchestrator 自身の grep（上記 5）と PR #120 本文・
merge 本文の記載である．`prrev-111-1` の初回 verdict（上記 2）が述べる
「`convFormL2_extends`／`convFormL2_cont_fixedTest` 以降は byte-identical」は修正前の
照合結果である．
