# Source inventory — 資料台帳

論文が依拠する資料の所在と収集状態（PLAN.md §10: 三環境のログについて所在と収集可否を
inventory 化する）．

## セッションログ（3 系統）

| Host ID | 実体 | 想定所在 | 収集状態 | 備考 |
|---|---|---|---|---|
| vps | VPS | `~/.claude/projects/` ほか（要列挙） | 未着手 | |
| local-main | 主 local machine | 同上 | 未着手 | |
| local-secondary | 副 local machine | 同上 | 未着手 | |

各 host で Phase 1 に列挙すべきもの: Claude Code セッション（`*.jsonl`），memory
ディレクトリ，shell history，build log，handoff 文書．

## GitHub 証跡

| 資料 | 所在 | 収集状態 |
|---|---|---|
| leray-hopf Git 履歴 | `uda-lab/leray-hopf`（public） | pinned: v0.1.0-rc1 / 7c15710a |
| leray-hopf Issues / PRs | 同上 | 未収集（Phase 2 で export → `evidence/repository-snapshots/`） |
| CI / build attestation 記録 | 同上 Actions | 未収集 |
| leray-hopf-notes（companion site） | `uda-lab/leray-hopf-notes` | 未収集 |

## 文献

`paper/references.bib` の各エントリは投稿前に原典と照合し，照合済みマークをここに付ける．

| bib key | 照合状態 |
|---|---|
| lerayhopf2026repo | ✓（2026-07-20，repo README と照合） |
| leray1934 | 未 |
| hopf1951 | 未 |
| moura2021lean4 | 未 |
| mathlib2020 | 未 |
