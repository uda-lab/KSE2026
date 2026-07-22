# Incident candidates（Phase 2 で列挙）

セッション符号化（`session-coding-schema.md`）で incident 候補と判定された出来事の
一覧．card 化（`evidence/incidents/INC-NNN.md`）前の受け皿．

## 書式

| # | 仮題 | 日時 | Event codes | 一次資料の有無 | card 化 |
|---|---|---|---|---|---|
| | | | | primary / reconstructed / none | INC-NNN or 未 |

## 候補一覧（2026-07-22 更新，セッション符号化 3 本 + GitHub 証跡より）

| # | 仮題 | 日時 | Event codes | 一次資料の有無 | card 化 |
|---|---|---|---|---|---|
| 1 | PR #20 `W1pTime.ofHValuedDeriv` の過強 statement（`p,q<1` で証明不能）を独立アジュディケータがマージ前検出，`hp,hq` 追加で修正 | 2026-06-20 | STMT-MISMATCH / RECOVERY | **primary**（EV-0925 = session `90fa24bb`，leray-hopf#20） | 未 |
| 2 | PR #27 T³ antisymm の `ALLOW_SORRY` が偽命題上に置かれる（無制約 `v,w` で反例，先行 2 revision は unsound）．`Vₙ` 制限に修正 | 2026-06-21 | WEAKEN / RECOVERY | **primary**（EV-0925，leray-hopf#27） | 未 |
| 3 | `convFormH1_eq_convFormSchwartz`（B5）の符号誤りで偽命題化，定義側の負号除去で修正 | 2026-06-26 | MATH-ERR / RECOVERY | **primary**（EV-0925） | 未 |
| 4 | **`w1pTime_continuous_in_H` の偽な一般化**（release 前 soundness postmortem）．6/28 の直接攻撃キャンペーンでも宣言の型は独立精査されず（consumer verdict は「未使用」判定のみ），7/16 の release レビューで発覚し statement-gate 政策が導入された | 2026-06-28〜07-16 | STMT-MISMATCH / WEAKEN / RECOVERY | **primary**（EV-0925 に 6/28 の傍証）+ reconstructed（leray-hopf#158/#170，postmortem） | 未 |
| 5 | PR #120 で main 上の公開定理 `edge_inf_eq_schwartz_tensor` の無断削除を byte-diff 悉皆レビューがマージ前検出，wrapper 復元 | 2026-07-10 | WEAKEN / RECOVERY | **primary**（EV-1669 = session `7e6156bf`，leray-hopf#120） | 未 |
| 6 | codex レビューの top-level コメント応答を監視が見落とし 19 分停滞（formal Review イベントのみポーリング）．3 経路監視 `watch-pr-gates.sh` に刷新して再発なし | 2026-07-10 | HANDOFF-FAIL / RECOVERY | **primary**（EV-1669） | 未 |
| 7 | GitHub Actions 課金上限到達で CI 即時失敗，ローカル検証（`lake build` + `flock`）へ切替 | 2026-06-27 | RESOURCE / RECOVERY | **primary**（EV-0925） | 未 |
| 8 | codex プラグインの broker/app-server チェーン残留（14 系統，~1.5GB）により Lean ビルドが OOM 連発（cgroup ~3.4GiB）．sweep・headroom 確認・`.lake` ハードリンク共有・`flock` 直列化の恒常規約を導入 | 2026-07-18 | RESOURCE / RECOVERY | reconstructed（owner 運用記録）．**primary 候補**: vps の 7/18 終端セッション 3 本（EV 特定は card 化時に実施） | 未 |
| 9 | **ログローテーション（`cleanupPeriodDays` 30 日既定）による研究記録の不可逆喪失**．創成期 6/10〜6/14 を全 host で喪失（local-secondary 上での削除が有力）．VPS 7/10 スナップショット復元試行は「VPS には当該期間の記録が元々無い」ことの確定という負の結果．`cleanupPeriodDays=9999`（2026-07-21）で以後停止．メタ・インシデント | 2026-06〜07 | LOSS / RECOVERY | primary（`analysis/vps-snapshot-20260710-verification.md`，escrow 全域） | 未 |
| 10 | release-attestation の check-axioms-live が Experimental モジュール未ビルドで失敗（P0 release-blocker）→ 翌ビルド修正で v0.1.0-rc1 発行 | 2026-07-20 | RESOURCE / RECOVERY | reconstructed（leray-hopf#185/#186）．primary は 7/20 終端セッションに含まれる可能性 | 未 |
| 11 | lean-prover が P2（Aubin–Lions 簡約）を「数学的に unsound」と誤主張して TODO に記載 → Codex adversarial review が overstated/false と指摘 → 修正担当 prover が socket error で死亡し虚偽記述＋非コンパイル状態が残置 → orchestrator が disk 検証のうえ honest-partial へ復元 | 2026-06-16 | MATH-ERR / HANDOFF-FAIL / RECOVERY | **primary**（EV-2076 = session `74aab39b`） | 未 |
| 12 | 長時間 lean-prover がのべ 8 回 SSL/socket/idle-timeout（13 分〜3.5h）で死亡（深夜帯ローカル回線の反復パターン）．全件 commit 前に disk 再検証で検出・隔離され FALSE-SUCCESS は 0 件 | 2026-06-16〜06-19 | RESOURCE / RECOVERY | **primary**（EV-2076） | 未 |
| 13 | owner がチャット内で明示承認した `uda-lab` への `git push`/`gh repo create` を auto-mode safety classifier が hard-block．owner が端末で直接実行して回避（GitHub 移行 = local-only 運用の終了点での摩擦） | 2026-06-19 | MODEL-ESC / RECOVERY | **primary**（EV-2076） | 未 |

### 対象外へ整理

- 2026-05-11 の orchestrator review 引き取り未遂（umbrella #266 / PR #267）: Hermes
  sessions は 2026-05-28 で終了しており leray-hopf（init 6/10）開始前の**別プロジェクト
  事案**と確認（issue #16 の注記どおり）．leray-hopf 開発の incident としては扱わない．
  運用規約の背景として言及する場合は reconstructed 扱い．
