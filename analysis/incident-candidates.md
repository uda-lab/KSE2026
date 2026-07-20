# Incident candidates（Phase 2 で列挙）

セッション符号化（`session-coding-schema.md`）で incident 候補と判定された出来事の
一覧．card 化（`evidence/incidents/INC-NNN.md`）前の受け皿．

## 書式

| # | 仮題 | 日時 | Event codes | 一次資料の有無 | card 化 |
|---|---|---|---|---|---|
| | | | | primary / reconstructed / none | INC-NNN or 未 |

## 既知の候補（ログ精査前のメモ．確定情報ではない）

以下はオーナー環境の運用記録から事前に把握している候補であり，Phase 2 でログから
裏付けを取るまで論文には使わない．

- 2026-07-18: codex プラグインの broker/app-server チェーン残留（14 系統，約 1.5 GB）
  により Lean ビルドが OOM を連発（コンテナ cgroup 上限 ~3.4 GiB）．恒常規約
  （sweep・headroom 確認・`.lake` ハードリンク共有・`flock` による build 直列化）が
  導入された．→ RESOURCE / RECOVERY 候補．
- 2026-05-11: umbrella #266 / PR #267 フローでの orchestrator による review 引き取り
  未遂（ユーザーが拒否し，「orchestrator は review handling を引き取らない」規約が
  恒常化）．→ HANDOFF-FAIL / RECOVERY 候補．
