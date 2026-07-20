# Unresolved questions

分析中に生じた未解決の疑問．解決したら回答と evidence を付けて closed へ移す．

## Open

- [ ] 三環境（vps / local-main / local-secondary）それぞれのログの所在と網羅期間は？
      （Phase 1 の inventory で確定）
- [ ] ログ欠損期間はどこか？Git/Issue/PR でどこまで再構成できるか？
- [ ] KSE 2026 CFP の残項目: references のページ算入・double-blind・artifact 提出
      （主要項目は 2026-07-20 確認済み → `notes/paper-outline.md`．
      **投稿締切 2026-07-31 (extended)** — Phase 1–4 の日程をこれに合わせて圧縮する）
- [ ] leray-hopf の開発開始時点はいつか（最初の commit / セッション）？
- [ ] local-main（自宅ノート PC）の欠損（#4，PR #8）: (a) `~/.claude/todos/` が不存在で
      旧形式 todo が残っていない（新形式 `~/.claude/tasks/` は収集済．旧形式データの
      有無は不明）．(b) leray-hopf の build log が恒久ファイルとして残存しない（lake は
      build log を保存しない）— build 結果は CI attestation（Phase 2 収集予定）で
      reconstructed として補えるか？ (c) セッション 81ef94ea は収集作業自体の live
      セッションで，escrow は 2026-07-20T15:10:05Z 時点の途中状態（以降の末尾は
      local-main 上の原本にのみ存在）．

## Closed

（なし）
