# Paper claims — 主張と証拠の対応表

論文中の技術的・歴史的主張は，本文書の claim として登録してから本文に書く
（AGENTS.md 規則 4）．`make verify` が本文書と `paper/` 中の `EV-` / `INC-` 参照の
解決可能性を検査する．

## 書式

```markdown
## CLM-NNN: <一文で述べた主張>
- Status: candidate | frozen | dropped
- Paper location: sections/NN-*.tex（未執筆なら planned）
- Evidence: EV-NNNN / INC-NNN / leray-hopf@<sha> / leray-hopf#<num> / decl:<Lean.Name>
- Notes: 確度，再構成か一次資料か，など
```

Phase 3（contribution freeze）で `frozen` にした claim のみ本文に残す．
contribution として掲げるのは 3 点以内（PLAN.md Phase 3）．

---

## CLM-001: Leray–Hopf 弱解存在（𝕋³ および ℝ³）が Lean 4 + mathlib 上で project axiom なしに形式化された
- Status: candidate
- Paper location: planned (sections/02-formalization.tex)
- Evidence: leray-hopf@7c15710a7b9068a2aa105fc7c11b432e7685b7b5, decl:exists_lerayHopf_torus3, decl:exists_lerayHopf_r3
- Notes: 範囲の上限は claims/formalization-scope.md．kernel-only の根拠は release
  attestation と `#print axioms`（Phase 2 で attestation run へのリンクを EV 化する）．

## CLM-002: 形式化キャンペーン（2026-06-10〜07-21）では，収集済みセッションログ上で確認できるだけでも output 15.1M tokens・API 換算 $6,980・アクティブ時間 199.7h（5 分 gap cap）の AI 計算が投入された（いずれも下界）
- Status: candidate
- Paper location: planned
- Evidence: EV-0001〜EV-2126（escrow 一次記録），`evidence/metrics/usage-metrics.json`（`scripts/extract_usage.py` により再現可能）
- Notes: 一次資料は各 JSONL の `message.usage`（API レスポンス由来）．方法論・
  カバレッジ欠損（ローテーション喪失 6/10〜6/14，レビュワー側計算資源など）は
  `analysis/usage-metrics-methodology.md`．下界であることを本文でも明記する．
  gap 閾値感度: active = 95.3h (1m) / 199.7h (5m) / 310.5h (15m)，wall-clock 総和 1,023.5h．

<!-- 以降の claim はログ分析（Phase 2）後に追加する． -->
