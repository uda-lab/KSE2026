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
| 2026-07-21 | Claude Fable 5 (Claude Code) | escrow の /private/sources 移設対応（ガード二重化は Copilot 指摘の反映），vps 全 1633 hash の移設後再検証，local-main 収集分（owner が収集・転送）の manifest 登録 EV-1634〜EV-1680 | scripts/inventory_sessions.py 修正（PR #10），manifest 追記・source-inventory 更新（PR #11 予定） | Copilot レビュー + merge gate 検査．収集・host 割当て変更の判断は owner |
| 2026-07-22 | Claude Fable 5 (Claude Code) | local-secondary 収集分（owner 側 Claude Code session `b60e5aa1` が収集，owner が転送）の manifest 登録 EV-1681〜EV-2126（446 件，sha256 重複 9 件スキップ） | evidence/manifest.csv 追記，provenance/source-inventory.md 更新（PR #17） | Copilot レビュー + merge gate 検査．収集・選別の判断は owner 側セッション記録（escrow 内 SOURCES.md）による |
| 2026-07-22 | Claude Fable 5 (Claude Code) | VPS 7/10 スナップショットバックアップの検証（sha256 全照合，history.jsonl 分析）と負の結果の記録（issue #15） | analysis/vps-snapshot-20260710-verification.md，unresolved-questions.md・incident-candidates.md 更新 | Copilot レビュー + merge gate 検査．スナップショット復元・バックアップ取得は owner |
| 2026-07-22 | Claude Fable 5 (Claude Code) | usage メトリクス抽出スクリプトの実装と escrow 全域集計（issue #14，message.id dedup・単価内蔵・gap 感度分析），方法論文書と CLM-002 起草 | scripts/extract_usage.py，evidence/metrics/usage-metrics.json，analysis/usage-metrics-methodology.md，claims/paper-claims.md 追記 | Copilot レビュー + merge gate 検査．単価は公表値（2026-07-22 参照）を転記，CLM の freeze 判断は owner（Phase 3） |
| 2026-07-22 | Claude Fable 5 (Claude Code, orchestrator + 3 coding subagents) | Phase 2 timeline 構築（キャンペーン区分・日次集計）とセッション符号化 3 本（`74aab39b`/`90fa24bb`/`7e6156bf`，subagent が raw transcript を精査し符号化），incident 候補 13 件の一次資料対応付け（issue #16） | analysis/project-timeline.md，evidence/session-index/ 3 ファイル，incident-candidates.md・unresolved-questions.md 更新 | Copilot レビュー + merge gate 検査．incident の card 化・論文採否は owner（Phase 3） |
| 2026-07-22 | Claude Fable 5 (Claude Code) | vps escrow 追補分（owner がホスト側転送: history/tasks/plans，コピー前 inode 検証）の manifest 登録 EV-2127〜EV-2145（19 件，sha256 重複 14 件スキップ）(issue #21) | evidence/manifest.csv 追記，provenance/source-inventory.md 更新 | codex 内部レビュー（/codex:review）+ codex 独立レビュー + merge gate 検査（レビュワー切替は owner 指示 2026-07-22） |
