# Source inventory — 資料台帳

論文が依拠する資料の所在と収集状態（PLAN.md §10: 三環境のログについて所在と収集可否を
inventory 化する）．

## セッションログ（3 系統）

| Host ID | 実体 | 想定所在 | 収集状態 | 備考 |
|---|---|---|---|---|
| vps | VPS devcontainer | `~/.claude/projects/`，`~/.hermes/`．追補分: `~/.claude/history.jsonl`（→ `claude-history/`），`~/.claude/tasks/`（→ `claude-tasks/`），`~/.claude/plans/`（→ `claude-plans/`） | **収集済 2026-07-20**（EV-0001〜EV-1633）**+ 追補 2026-07-22**（EV-2127〜EV-2145） | 1777 ファイル escrow（762MB），内容重複 144 を除く 1633 件を manifest 登録．Claude Code 6 プロジェクト（leray-hopf 本体 12 sessions を含む）+ Hermes orchestrator sessions/logs/relay-prompts/kanban + bash history．追補: local 2 host と揃える種別補完（global prompt history 全量スナップショット，leray 突合 12 task dirs，leray 関連 7 plans = 33 ファイル中 sha256 重複 14 を除く 19 件登録．owner がホスト側で転送）．除外・対応表は escrow 内 SOURCES.md（gitignored）．issue #3 / #21 参照 |
| local-main | 自宅ノート PC（macOS）※ | `~/.claude/projects/` ほか | **収集済 2026-07-20**（EV-1634〜EV-1680） | 48 ファイル escrow（33MB）中，内容重複 1 を除く 47 件登録．leray-hopf 関連は grep により 3 project dir・7 セッションに閉じることを owner が確認（subagent transcript 16 本含む）．global prompt history・plans・tasks・shell history 込み．対応表は escrow 内 SOURCES.md．issue #4 参照 |
| local-secondary | 大学 PC（当初計画の「主 local machine」）※ | `~/.claude/projects/` ほか | **収集済 2026-07-21，登録 2026-07-22**（EV-1681〜EV-2126） | 455 ファイル escrow（92MB）中，内容重複 9（空 `.lock` 等）を除く 446 件登録．leray-hopf 関連は grep により 14 project dir 中 6 dir・36 top-level sessions に閉じることを owner が確認（最初期 2026-06-15 からのセッションを含む．subagent transcripts 171 本，plans 4 件，global prompt history・tasks・shell history 込み）．対応表は escrow 内 SOURCES.md（gitignored）．issue #5 参照 |

※ host 割当ては 2026-07-20 の owner 判断で変更（当初: local-main=大学 PC の予定）．
　vps → local-main → local-secondary の直列登録順は維持（issue #4 コメント参照）．

各 host で Phase 1 に列挙すべきもの: Claude Code セッション（`*.jsonl`），memory
ディレクトリ，shell history，build log，handoff 文書．

## GitHub 証跡

| 資料 | 所在 | 収集状態 |
|---|---|---|
| leray-hopf Git 履歴 | `uda-lab/leray-hopf`（public） | pinned: v0.1.0-rc1 / 7c15710a |
| leray-hopf Issues / PRs | 同上 | **収集済 2026-07-21，再収集 2026-07-24**（`evidence/repository-snapshots/leray-hopf/`: issues.json 195 件 = issue+PR，comments.json 442 件，commits.json 320 件，tags.json，releases.json，EXPORT.json = 再現手順．issue #60 で `performed_via_github_app`／`author_association` を追加，`fetched_at=2026-07-24T18:28:30+00:00`，`head_sha_at_fetch=8ef11145d5…`．PR #13，#61） |
| CI / build attestation 記録 | 同上 Actions | releases.json / tags.json に attestation メタ収集済．Actions run log 本体は未収集（必要時に export） |
| leray-hopf-notes（companion site） | `uda-lab/leray-hopf-notes` | 未収集（論文の一次資料としては不使用．参照時に個別収集） |
| KSE2026 Issues / PRs（self-snapshot） | `uda-lab/KSE2026`（**private**） | **収集済 2026-07-24，再収集 2026-07-26**（`evidence/repository-snapshots/KSE2026/`: issues.json 80 件，comments.json 127 件，commits.json 82 件，EXPORT.json = 再現手順（`name_masking_active` でマスク実施の有無を記録）．issue #79 で denylist 個人名の `<name-redacted>` マスクを exporter に追加して再収集，`fetched_at=2026-07-26T08:37:06+00:00`，`head_sha_at_fetch=e65b872e…`．作業継続中のため再収集ごとに件数が増加し得る．leray-hopf と異なり private repo のため，本 snapshot は read アクセス権を持つアカウントでのみ再現可能（`EXPORT.json` の `private: true` と `note` を参照）．issue #60，#79） |
| mediation census（派生成果物） | 本リポジトリ | `scripts/compute_mediation_census.py` で上記 2 snapshot から生成．`evidence/metrics/mediation-census.{json,csv}`．方法論と下界注記は `analysis/mediation-census-methodology.md`（issue #60）．census JSON は入力 snapshot の `head_sha_at_fetch`/`fetched_at` を自己記述しており，2026-07-26 の KSE2026 再収集（issue #79）後も再計算していない — census が対象とするのは自己記述された 2026-07-24 時点の snapshot（git 履歴から参照可能）である |

## 文献

`paper/references.bib` の各エントリは投稿前に原典と照合し，照合済みマークをここに付ける．

| bib key | 照合状態 |
|---|---|
| lerayhopf2026repo | ✓（2026-07-20，repo README と照合） |
| leray1934 | 未 |
| hopf1951 | 未 |
| agenticprs2026security | ✓（2026-07-23，arXiv abstract 照合） |
| armstrong2026degiorginashmoser | ✓（2026-07-23，arXiv abstract 照合） |
| boldo2010wave | ✓（2026-07-23，ITP 2010 出版情報照合） |
| commelin2023abstraction | ✓（2026-07-23，arXiv 照合） |
| deepmind2025alphaproof | ✓（2026-07-23，Nature 書誌 + 著者リストは PubMed 経由で照合） |
| gonthier2013oddorder | ✓（2026-07-23，ITP 2013 出版情報照合） |
| immler2012ode | ✓（2026-07-23，ITP 2012 出版情報照合） |
| leaneval2026repo | ✓（2026-07-25，`leanprover/lean-eval` README 実読） |
| leaneval2026site | ✓（2026-07-25，`lean-lang.org/eval/problems/` 実読） |
| metr2025longtasks | ✓（2026-07-23，arXiv 照合） |
| miller2026vlasov | ✓（2026-07-23，arXiv abstract 照合） |
| tauceti2026 | ✓（2026-07-23，repo 4 本を実読・pinned commit 3a933bde．論文/CITATION.cff 不在も確認） |
| vandoorn2024gns | ✓（2026-07-23，ITP 2024 LIPIcs 照合） |
| xin2025deepseekproverv2 | ✓（2026-07-23，arXiv 照合） |
| yang2023leandojo | ✓（2026-07-23，NeurIPS 2023 D&B 照合） |
| zhou2026leanatlas | **要再照合**（著者名が arXiv abstract のみ由来．投稿前に本体ページで確認） |
| moura2021lean4 | 未 |
| mathlib2020 | 未 |
