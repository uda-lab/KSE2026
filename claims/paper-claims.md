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

## CLM-003: Vertex 完成フェーズ（2026-07-02〜03 PT）の実請求は machine-wide 実測 ¥54,868，うち leray-hopf 単独分は ¥41,421〜41,796（導出値，75.5〜76.2%）である
- Status: candidate
- Paper location: planned
- Evidence: `evidence/metrics/vertex-completion-phase-billing.csv`・`vertex-completion-phase-billing-sku.csv`（redaction 済み集計），`scripts/extract_vertex_phase.py`（再現可能），EV-1681〜EV-2126（escrow 一次記録）
- Notes: 2 層区分（provider-billed actual / 導出値）は `analysis/cost-attribution-methodology.md`
  に従い区別して書く．leray 単独分は SKU レベル照合で同定した実効レート区間
  [160.4, 161.8] ¥/$ による導出値であり，脚注で明示する．方法・限界は
  `analysis/billing-reconciliation.md`．raw export は Git 外（sha256 記録済み）．

## CLM-004: 符号化 6 セッション上の事象統計は WEAKEN/STMT-MISMATCH 系 4 件・RECOVERY 19 件・RESOURCE 12 件・WT-CONFLICT 5 件であり，FALSE-SUCCESS（虚偽の成功報告の残存）は 0 件だった
- Status: candidate
- Paper location: planned (sections/03 or 04)
- Evidence: `evidence/session-index/` の 6 index（EV-0247，EV-0925，EV-1669，EV-2076 ほかを一次資料とする符号化），`analysis/session-coding-schema.md`
- Notes: 母集合は「符号化済み 6 セッション」であり全キャンペーンの悉皆ではない —
  本文では必ず母集合を明示する．FALSE-SUCCESS 0 件は commit 前 disk 再検証の
  規律（74aab39b）と独立 adversarial review の帰結として解釈する．

## CLM-005: 同型の盲点（プレースホルダ上の偽 statement）について，release 直前まで残存した失敗例（INC-001）とマージ前検出に成功した例（INC-002）が同一プロジェクト内に併存し，帰結を分けたのは独立 statement 検査（数値反例を含む adversarial review）の有無だった
- Status: candidate
- Paper location: planned (sections/04-incidents.tex)
- Evidence: INC-001，INC-002，EV-0925，leray-hopf#27，leray-hopf#158
- Notes: 因果の主張は「検査の有無が帰結を分けた」までに留め，反実仮想
  （検査があれば必ず防げた）へは踏み込まない（PLAN.md Phase 5 の
  過大評価チェックに対応）．INC-001 側は検査が「行われなかった」ことの
  記録が一次資料（EV-0925 の consumer verdict 過程）にある点が対比の根拠．

<!-- 以降の claim は必要に応じて追加する． -->
