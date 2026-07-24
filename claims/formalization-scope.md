# Formalization scope（参照固定）

論文が言及してよい形式化成果の**上限**を定める．本文書に書かれていないことを
論文で主張してはならない（AGENTS.md 規則 4，PLAN.md Phase 5）．

## Pinned reference

- Repository: `uda-lab/leray-hopf`（public）
- Release tag: `v0.1.0-rc1`（"release-candidate build attestation"，published 2026-07-20）
- Commit: `7c15710a7b9068a2aa105fc7c11b432e7685b7b5`
- 出典: pinned commit の `README.md`（"What is actually proved" の claims table と
  Honest scope callout を含む．scope の一次資料はこちら．本文書はその要約であり，
  齟齬がある場合は pinned commit の `README.md` が優先）．
  注: 旧記載の `docs/claims-and-scope.md` は pinned commit に存在しない
  （tree 全走査で確認，issue #38）．

参照 commit を更新する場合は `provenance/author-decisions.md` に記録し，本文書・
README.md・`paper/references.bib` を同時に更新する．

## 主張してよいこと（pinned commit の README に基づく）

1. **二つの capstone 存在定理**が証明され machine-checked である：
   - `decl:exists_lerayHopf_torus3`（`LerayHopf/Torus/GalerkinODECapstone.lean`）—
     単位周期トーラス 𝕋³ 上，任意の divergence-free な `u₀ : L²`，`ν > 0`，`T > 0` に
     対する Leray–Hopf 弱解の存在．
   - `decl:exists_lerayHopf_r3`（`LerayHopf/R3/GalerkinODECapstone.lean`）— ℝ³ 上の同様の存在．
2. **kernel-only**：`#print axioms` は標準 kernel axiom（`propext`,
   `Classical.choice`, `Quot.sound`）のみ．project axiom ゼロ，`sorryAx` なし．
3. 解構造体の field として，divergence-free 性，weak Navier–Stokes identity，
   energy inequality，initial-value trace が明示的に含まれる．
4. release surface（`import LerayHopf`）は sorry-free / project-axiom-free で，CI
   （`scripts/check-release-cone.sh`）で強制されている．
5. 特定 commit の toolchain-exact な検証は manual build attestation による．

## 主張してはならないこと（repo 自身が明示的に否定している）

- smoothness / energy-class を超える higher regularity
- 解の uniqueness / non-uniqueness
- 外力付き方程式（形式化対象は外力なし）
- `[0, ∞)` 上で一様に有効な単一の解（有限 time horizon `[0, T]`，`T` は任意だが固定）
- 一般の space-time test function に対する弱形式（separated-variable 形式
  `ψ(t)·w(x)` のみ）
- `LerayHopf.Experimental` 配下の内容（release surface から到達不能，capstone に不要）

## Pinned metrics

- pinned commit で `scripts/extract_metrics.py` により 96 files，42,012 lines，
  theorem 1,000 + lemma 58 を実測済み．生成物は
  `evidence/metrics/formalization-metrics.json`．本文ではこの実測値を上限とし，
  記憶や moving branch の値を用いない．
