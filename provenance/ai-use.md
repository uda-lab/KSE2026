# AI use log

本リポジトリの成果物への AI システムの関与を継続的に記録する（PLAN.md §8）．
AI は著者としない．最終判断は常に scientific owner が行う．

## 書式

| 日付 | モデル / ツール | 関与範囲 | 生成物 | 人間による確認 |
|---|---|---|---|---|

## 記録

| 日付 | モデル / ツール | 関与範囲 | 生成物 | 人間による確認 |
|---|---|---|---|---|
| 2026-07-20 | Claude Fable 5 (Claude Code) | Phase 0 scaffold 一式の生成（PLAN.md はオーナー提供の計画をそのまま収録．claims/formalization-scope.md は leray-hopf README v0.1.0-rc1 から転記） | リポジトリ初期構成，LaTeX skeleton，scripts/，各テンプレート | Claude Opus 内部レビュー + Copilot レビュー（PR #1）を経て merge．オーナー承認は PR フロー授権による |
| 2026-07-20 | Claude Opus (subagent) | PR #1 の内部レビュー（read-only，approve-with-fixes，8 findings） | レビュー所見（provenance/review-history.md，PR #1 コメント） | 所見は Fable 5 が修正として適用，Copilot レビューで再確認 |
| 2026-07-20 | Claude Fable 5 (Claude Code) | Phase 1 vps ログ収集の実行（escrow 作成，SOURCES.md，manifest 登録 EV-0001〜EV-1633，redact 検査）と PR #7 作成 | evidence/manifest.csv 追記，provenance/source-inventory.md 更新 | Copilot レビュー（PR #7）+ merge gate 検査 |
