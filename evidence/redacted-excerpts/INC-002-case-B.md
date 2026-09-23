# INC-002 / Case B — PR #27 `galerkinConvection_antisymm` のマージ前 adjudication（2026-06-21）

- **Incident card:** `evidence/incidents/INC-002.md`
- **論文の対応箇所:** §IV Case B（`paper/sections/04-incidents.tex`），claim CLM-005・CLM-008
- **Session:** `90fa24bb-c5e4-43ff-8d27-1799177561a0`（host vps，`evidence/session-index/90fa24bb-c5e4-43ff-8d27-1799177561a0.md`）
- **Evidence ID:** EV-0925（メイン transcript，`claude-projects/-workspaces-lean-pde/90fa24bb-c5e4-43ff-8d27-1799177561a0.jsonl`）
- **抜粋範囲:** 同 JSONL の L991〜L1039（2026-06-21T02:57〜03:18Z）
- **GitHub 側:** leray-hopf#27（`evidence/repository-snapshots/leray-hopf/issues.json`）
- **本抜粋が支える記述:** 論文 Case B の「Two proof revisions had attempted the unrestricted statement before an independent reviewer identified this missing closure condition」「A numerical diagnostic showed a discrepancy of approximately 80.7 without the projection hypotheses and about 10^-13 with them」「removed the placeholder before merge」

表記: orchestrator = メインセッションの assistant．prover／adjudicator／reviewer = `Agent` tool で派遣された subagent（報告は task-notification または tool result として transcript に現れる）．引用は原文（英語）のまま．`[…]` は省略．

## 1. 02:57:08Z — prover（3rd pass）の報告: statement が偽である旨の blocker note（L991）

> **antisymm status: honest blocker (not proved).** I determined `galerkinConvection_antisymm` is **false as currently stated** (arbitrary `v w : L2VF`). The proposed `(k,l) ↦ (k,-(k+l))` self-bijection of `fourierBox n` does not exist: `box × box` is not invariant under it (`neg_mem_fourierBox` covers only `k ↦ -k`; concrete witness `k=(1,0,0), l=(1,1,0) ⇒ -(k+l)=(-2,-1,0) ∉ box` for `n=1`). The box truncation breaks the `l ↔ m` IBP reindex, and finite support of `u` does not rescue it. The statement needs `v, w ∈ Vₙ` (a signature change owned by lean-coder). I left a precise `ALLOW_SORRY` documenting exactly this (1 remaining sorry, line 234) […]

## 2. 02:58:12Z — orchestrator: マージ保留と adjudication の決定（L993）

> **But** it surfaced a statement-gate issue and left **one `ALLOW_SORRY` on a statement it believes is FALSE**: `galerkinConvection_antisymm` for arbitrary `v,w` (the `fourierBox` reindex genuinely fails; it claims the statement needs `v,w ∈ Vₙ`). That's a problem — discipline forbids a sorry on a false statement; if it's false-as-stated, the *statement* must be fixed (add `v,w ∈ Vₙ`) before merge, not papered with a sorry. The agent itself requested independent confirmation.
>
> So I won't merge it yet. Adjudicating the crux (is `galerkinConvection_antisymm` genuinely false-as-stated, and is `galerkinConvection_bound` sound?), then routing the statement fix.

## 3. 02:58:35Z — adjudicator の派遣 prompt 冒頭（L994）

> You are an INDEPENDENT statement-gate adjudicator for PR #27 (3rd revision) in repo uda-lab/lean-pde (branch lane-t/torus3-nsforms, Issue #22, T³ convection form). […] The two prior revisions were unsound; be adversarial.

## 4. 03:00:41Z — adjudication の結果（L1002）

> **ADJUDICATION: ANTISYMM-FALSE-NEEDS-Vₙ**
>
> `galerkinConvection_antisymm` (TorusConvectionForm.lean:232–234) is **genuinely FALSE as stated** for arbitrary `v w : L2VF`. Independently confirmed two ways:
>
> 1. **Structural:** `fourierBox n = Icc(−n,n)³` (GalerkinProjection.lean:41). The summand reads `ŵ_i(−(k+l))` with `k,l ∈ box` but `−(k+l)` ranges over `[−2n,2n]³ ⊋ box`. The `l↔m` IBP reindex that drives antisymmetry needs `box×box` invariant under `(k,l)↦(k,−(k+l))`, which it is not […]. Author's witness is arithmetically correct: n=1, k=(1,0,0), l=(1,1,0) ⇒ −(k+l)=(−2,−1,0)∉box.
> 2. **Numerical (my independent reproduction):** with a genuinely div-free `u`, arbitrary v,w give `galConv u v w = 56.69 ≠ −24.03 = −galConv u w v` (diff 80.7). Restricting v,w to Vₙ (box support): both = −50.9597 (diff 1.2e-13). So it is false-as-stated and **true under `velocityProjection_n n v = v`, `velocityProjection_n n w = w`** […]
>
> The `ALLOW_SORRY` documentation is an accurate blocker note, not a false-blocker — it correctly says "false as stated, needs Vₙ." **However, per discipline, a `sorry` parked on a statement the author has proven false is itself a defect** (sorry ⊢ False; a landmine even though quarantined). The correct action is exactly what the note prescribes: **fix the signature first** (add the two `Vₙ` hypotheses), then the sorry becomes legitimate. Adding `v,w∈Vₙ` is a **faithful fix, not a weakening**: the `Torus3NSForms.b_antisymm` field […] needs unrestricted antisymmetry, but it is witnessed by the genuine `∫(u·∇)v·w` form […]; the truncated `galerkinConvection` only ever needs to agree with `b` on `Vₙ` via `b_galerkin` […]. The new lemma has **zero downstream consumers** today, so the signature change breaks nothing.
>
> […]
>
> ```
> theorem galerkinConvection_antisymm (n : ℕ) (u : L2Sigma) (v w : L2VF)
>     (hv : velocityProjection_n n v = v) (hw : velocityProjection_n n w = w) :
>     galerkinConvection n (u : L2VF) v w = -galerkinConvection n (u : L2VF) w v
> ```

## 5. 03:01:39Z — orchestrator → prover: signature 修正と証明の派遣（L1006）

> Finish PR #27 (issue #22, T³ convection) by discharging the last `sorry`: `galerkinConvection_antisymm` […]. An independent adjudication CONFIRMED (structurally + numerically) that the lemma is FALSE for arbitrary `v,w` and TRUE under `v,w ∈ Vₙ`, and AUTHORIZED the faithful signature fix below. […] REMOVE the `-- ALLOW_SORRY` (the statement is now TRUE).

## 6. 03:13:32Z — prover の完了報告（L1020）

> **Task complete.** PR #27's last `sorry` (`galerkinConvection_antisymm`) is discharged; `LerayHopf/TorusConvectionForm.lean` is now sorry-free.
>
> […]
>
> ### Signature fix (adjudication-authorized)
> `galerkinConvection_antisymm` gained two finite-support hypotheses:
> `(hv : velocityProjection_n n v = v) (hw : velocityProjection_n n w = w)`. The `u` slot is unchanged (`u : L2Sigma`, carrying `DivFreeL2 u`). No external callers exist (grep-verified), so nothing downstream breaks. The `-- ALLOW_SORRY` was removed (statement is now TRUE).
>
> ### Proof (sorry-free)
> Per fixed `k`: restrict both inner `l`-sums from `fourierBox n` to the `σ_k`-invariant set `C_k = box.filter (-(k+l) ∈ box)` (coefficients vanish outside the box via `coeff_zero_outside_box`); reindex the swapped sum by the involution `l ↦ -(k+l)` (`Finset.sum_nbij'`); combine `lₐ + (-(k+l))ₐ = -kₐ`; kill via `∑_a kₐ ûₐ(k) = 0` (`DivFreeL2 u`). […]
>
> ### Remaining sorry
> **None** in `TorusConvectionForm.lean` […]
>
> ### Checks (verified locally — exit codes)
> - `check-no-sorry.sh` → 0
> - `check-no-axiom.sh` → 0
> - `check-theorem-names.sh` → 0
> - `flock /tmp/lean-build.lock lake build LerayHopf.TorusConvectionForm` → BUILD_EXIT=0 (green)
> - downstream `lake build LerayHopf.AxiomaticClosure` → BUILD_EXIT=0 (green)
>
> Committed (`0219ae6` […]) and pushed to `lane-t/torus3-nsforms`; PR #27 body updated to reflect sorry-free status.

## 7. 03:17:14Z〜03:17:44Z — 最終レビューとマージ（L1035〜L1037）

orchestrator:

> #27 antisymm review: **APPROVE** — sound. The blessed `Vₙ` signature, genuine full-strength antisymmetry, `hv`/`hw` load-bearing in the box→`C_k` restriction, the `l↦-(k+l)` involution correctly discharged through `sum_nbij'`, and the `∑ₐ kₐûₐ(k)=0` div-free kill applied verbatim. File sorry-free, axiom-clean, both CI checks green, MERGEABLE.

`gh pr merge 27 […] --squash` の結果（03:17:44Z）:

```text
M27=0
   f0c55ce..56b9cfc  main       -> origin/main
```

## 注記

差 80.7／1.2e-13 は adjudicator が自前で行った数値再現であり，certified counterexample ではない（card および論文本文と同じ扱い）．先行 2 revision の差分自体は本抜粋に含まれない（card の Confidence 欄参照）．
