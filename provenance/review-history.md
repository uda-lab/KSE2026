# Review history

原稿・claims への内部レビュー（PLAN.md §8 の各 reviewer 役割，および Phase 5 の
adversarial review）の実施記録．

| 日付 | レビュー種別 | 対象 | 実施者（人間 / AI+人間確認） | 結果・指摘 | 対応 |
|---|---|---|---|---|---|
| 2026-07-20 | internal scaffold review（read-only） | PR #1（Phase 0 scaffold 全体） | Claude Opus（サブエージェント）＋人間確認待ち | approve-with-fixes．should-fix 4件（redact regex の JSON 形式 false negative / redact_check の CI 未組込 / manifest への絶対パス記録 / timeline の timezone 混在ソート），nit 4件（Python 3.10 依存・EV 採番・LOC 定義・pdflatex と Unicode 数式）．事実正確性（scope doc ↔ upstream README）・CSV quoting・.gitignore 再包含・claim 検査・PLAN 整合は clean 判定 | 8件全て同 PR 内で修正（PR #1 のレビューコメント参照） |

## Phase 5 チェックリスト（実施時にコピーして使う）

- [ ] Leray–Hopf 弱解存在について過剰な主張がないか（claims/formalization-scope.md 照合）
- [ ] AI エージェントの効果を因果関係として過大評価していないか
- [ ] 失敗例を都合よく選択していないか（incident-ranking の不採用理由を確認）
- [ ] 欠損ログや不完全な再構成を事実として記述していないか（evidence_type 照合）
- [ ] proprietary tool 固有の操作法を一般的方法論として誤認していないか
