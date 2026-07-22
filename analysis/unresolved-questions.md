# Unresolved questions

分析中に生じた未解決の疑問．解決したら回答と evidence を付けて closed へ移す．

## Open

- [ ] 三環境（vps / local-main / local-secondary）それぞれのログの所在と網羅期間は？
      （Phase 1 の inventory で確定）
- [ ] ログ欠損期間はどこか？Git/Issue/PR でどこまで再構成できるか？
      （2026-07-22 更新: セッションログの真の欠損は **2026-06-10〜06-14 のみ**に確定．
      6/15〜6/18 は local-secondary escrow がカバー，VPS 側 6/10〜6/18 は喪失ではなく
      非存在 — `vps-snapshot-20260710-verification.md`．残タスクは 6/10〜6/14 の
      Git/GitHub 証跡からの再構成（evidence_type=reconstructed）のみ）
- [ ] KSE 2026 CFP の残項目: references のページ算入・double-blind・artifact 提出
      （主要項目は 2026-07-20 確認済み → `notes/paper-outline.md`．
      **投稿締切 2026-07-31 (extended)** — Phase 1–4 の日程をこれに合わせて圧縮する）
## Closed

- [x] **VPS 7/10 スナップショットから創成期ログを回復できるか？** → 回復対象なし．
      当該期間の leray-hopf セッションは VPS 上に元々存在しなかった（作業は local 側）．
      根拠: バックアップは現行 escrow の真部分集合（新規ファイル 0 件），かつ
      ローテーション非対象の global prompt history で VPS 初回プロンプトが
      2026-06-19T14:48:36Z と確定．詳細は
      [vps-snapshot-20260710-verification.md](vps-snapshot-20260710-verification.md)（issue #15）．
- [x] **leray-hopf の開発開始時点はいつか（最初の commit / セッション）？** →
      最初の commit は 2026-06-10（init 日 27 commits，git 密度分析 2026-07-21）．
      現存する最初のセッションログは 2026-06-15（local-secondary，`research-lean-pde`，
      EV-1681〜EV-2126 の一部）．VPS でのセッション開始は 2026-06-19（同上検証文書）．
      6/10〜6/14 のセッションログは現存しない（上記 Open 項参照）．
