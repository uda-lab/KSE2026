# Source inventory — 資料台帳

論文が依拠する資料の所在と収集状態（PLAN.md §10: 三環境のログについて所在と収集可否を
inventory 化する）．

## セッションログ（3 系統）

| Host ID | 実体 | 想定所在 | 収集状態 | 備考 |
|---|---|---|---|---|
| vps | VPS devcontainer | `~/.claude/projects/`，`~/.hermes/` | **収集済 2026-07-20**（EV-0001〜EV-1633） | 1777 ファイル escrow（762MB），内容重複 144 を除く 1633 件を manifest 登録．Claude Code 6 プロジェクト（leray-hopf 本体 12 sessions を含む）+ Hermes orchestrator sessions/logs/relay-prompts/kanban + bash history．除外・対応表は escrow 内 SOURCES.md（gitignored）．issue #3 参照 |
| local-main | 自宅ノート PC（macOS，kuninotokotachi）※ | `~/.claude/projects/` ほか | **収集済 2026-07-20**（EV-1634〜EV-1680） | 48 ファイル escrow（33MB）中，内容重複 1 を除く 47 件登録．leray-hopf 関連は grep により 3 project dir・7 セッションに閉じることを owner が確認（subagent transcript 16 本含む）．global prompt history・plans・tasks・shell history 込み．対応表は escrow 内 SOURCES.md．issue #4 参照 |
| local-secondary | 大学 PC（当初計画の「主 local machine」）※ | 同上（要列挙） | 未着手 | #5，local-main の次に登録 |

※ host 割当ては 2026-07-20 の owner 判断で変更（当初: local-main=大学 PC の予定）．
　vps → local-main → local-secondary の直列登録順は維持（issue #4 コメント参照）．

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
