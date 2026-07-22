# Project timeline（Phase 2）

Git commit・Issue/PR・セッションログを統合した leray-hopf 開発の時系列．
骨格は `scripts/build_timeline.py --commits-json evidence/repository-snapshots/leray-hopf/commits.json`
と `evidence/manifest.csv` から機械生成した日次集計（2026-07-22 実行）で，
キャンペーン区分と注記を手動で加えた．全期間は 2026-06-10（init）〜07-20
（v0.1.0-rc1 attestation，pinned 7c15710a）の約 6 週間．

## キャンペーン区分

| # | 期間 | 名称 | 根拠（issue/PR・commit 密度・セッション） |
|---|---|---|---|
| C0 | 06-10〜06-11 | Bootstrap（repo init） | init 日（06-10）に 27 commits，翌 06-11 に 1 commit．**セッションログ欠損期間**（全 host，ローテーション喪失．`vps-snapshot-20260710-verification.md`） |
| — | 06-12〜06-14 | 休止 | commits 0．ログも無し（欠損期間の続き） |
| C1 | 06-15〜06-18 | 初期開発（local のみ） | commits 2/1/6/9．最古の一次ログ = local-secondary `research-lean-pde` セッション（06-15〜） |
| C2 | 06-19〜07-05 | Axiom-removal キャンペーン | 06-19 leray-hopf#1（architecture audit）を起点に 06-20 だけで #2〜#31 の 30 件を起票し Stream A–D / R3・Torus lane 構造を確立．06-21 に 21 commits．07-04 #89 で T³ capstone 無条件化，07-05 #99 axiom flip → #102/#103 で kernel-only「full textbook LH」宣言．VPS の関与は 06-19 開始（同検証文書） |
| C3 | 07-06〜07-12 | 公開前リファクタリング | #104〜#143（dedup / layout / readability / pdelib-prep）．**07-10 に 72 commits のピーク**（#120〜#133 の 14 PR）．orchestration セッション `7e6156bf`（local-main，EV-1669）はこの日 |
| — | 07-13〜07-15 | 休止 | commits 0（07-14 に local-main セッション終端 1 件のみ） |
| C4 | 07-16〜07-20 | Release キャンペーン | #144〜#195．P0 release-blocker 群（#144/#146/#157/#158/#185），**soundness postmortem #158**（`w1pTime_continuous_in_H` の偽な一般化 → statement-gate 政策 #170），repo rename `lean-pde`→`leray-hopf`（#157/#171），release-attestation + v0.1.0-rc1（07-20） |

## 日次集計

- commits = author date（UTC）単位の leray-hopf commit 数（snapshot 320 件，
  `evidence/repository-snapshots/leray-hopf/commits.json`）．
- issues/PRs = 当日起票された leray-hopf issue/PR の番号帯（計 195 件，同 `issues.json`）．
- sessions(終端) = escrow の top-level セッション JSONL のうち mtime（**終端時刻の
  proxy**．長命セッションは開始日と一致しない）が当日のものの host 別本数．

| 日付 | commits | issues/PRs 起票 | sessions(終端) | 注記 |
|---|---:|---|---|---|
| 06-10 | 27 | | | **init．セッションログ欠損（全 host）** |
| 06-11 | 1 | | | 欠損期間 |
| 06-12〜06-14 | 0 | | | 休止（ログも無し） |
| 06-15 | 2 | | ls×1 | 最古の一次ログ（EV-1681 以降の一部） |
| 06-16 | 1 | | | |
| 06-17 | 6 | | ls×2 | |
| 06-18 | 9 | | | |
| 06-19 | 6 | #1 (1) | | architecture audit．VPS 初回プロンプト 14:48Z |
| 06-20 | 11 | #2–#31 (30) | | Stream A–D / lane 構造の一斉起票 |
| 06-21 | 21 | #32–#41 (10) | | spatial_compactness_R3 axiom 除去（#35） |
| 06-22 | 6 | #42–#52 (11) | | |
| 06-23 | 1 | | | |
| 06-24 | 1 | #53–#54 (2) | ls×1 | `74aab39b` の mtime 日（実終端は 06-20T04:24Z．符号化済，EV-2076） |
| 06-25 | 2 | #55–#57 (3) | | |
| 06-26 | 2 | #58–#60 (3) | | R3 convection axiom 除去で capstone 3→2（#60） |
| 06-27 | 2 | #61–#62 (2) | | |
| 06-28 | 16 | #63 (1) | | |
| 06-29 | 3 | #64 (1) | vps×1 | `90fa24bb` 終端（符号化済，EV-0925） |
| 06-30 | 8 | #65–#67 (3) | vps×1, ls×1 | |
| 07-01 | 2 | #68–#71 (4) | ls×1 | |
| 07-02 | 4 | #72–#76 (5) | ls×4, vps×1 | torus aubin_lions mode-wise 再計画（#76） |
| 07-03 | 11 | #77–#87 (11) | ls×21, vps×3 | T-AL-1〜4 連続投入 |
| 07-04 | 8 | #88–#96 (9) | vps×2, ls×2 | **T³ capstone 無条件化（#89）** |
| 07-05 | 7 | #97–#103 (7) | | **R3 axiom flip（#99）→ kernel-only（#102/#103）** |
| 07-06 | 1 | #104–#105 (2) | | |
| 07-07 | 1 | #106–#115 (10) | vps×4, lm×2 | リファクタリング umbrella #115 |
| 07-08 | 0 | | | |
| 07-09 | 11 | #116–#119 (4) | | |
| 07-10 | 72 | #120–#133 (14) | lm×2 | **commit ピーク**．`7e6156bf` 終端（符号化済，EV-1669） |
| 07-11 | 20 | #134–#142 (9) | | |
| 07-12 | 2 | #143 (1) | vps×1 | |
| 07-13〜07-15 | 0 | | lm×1 (07-14) | 休止 |
| 07-16 | 7 | #144–#161 (18) | ls×2 | release-blocker 起票，**#158 soundness postmortem** |
| 07-17 | 25 | #162–#173 (12) | lm×1, ls×1 | rename `lean-pde`→`leray-hopf`（#171） |
| 07-18 | 6 | #174–#176 (3) | vps×3 | OOM cascade の日（incident 候補） |
| 07-19 | 13 | #177–#183 (7) | | #177/#178 prose 訂正の独立再レビュー |
| 07-20 | 5 | #184–#195 (12) | lm×1, vps×1 | **v0.1.0-rc1 release-attestation**（#185/#186 で一度失敗→修正） |
| 07-21 | 0 | | ls×1 | 収集セッション `b60e5aa1`（KSE2026 側，論文作業） |

（ls = local-secondary，lm = local-main）

## 欠損とバイアスの明示

1. **06-10〜06-14 はセッションログが存在しない**（ローテーション喪失，回復不能．
   この期間の記述はすべて evidence_type=reconstructed として Git/GitHub 証跡のみ
   から行う）．
2. sessions 列は mtime（終端）proxy であり，活動日そのものではない．07-03 の
   ls×21 は local-secondary 上の `research-lean-lean-pde` 期（cwd `~/Documents/research/lean/lean-pde`．最初期 dir `research-lean-pde` = `~/Documents/research/lean-pde` とは別の実在ディレクトリ）の一斉終端で，
   実活動は 06-30〜07-03 に分布する．
3. VPS escrow は 06-19 以降を連続カバー，local-main escrow は 07-07 以降のみ
   （それ以前の local 作業は local-secondary 側に記録されている）．
