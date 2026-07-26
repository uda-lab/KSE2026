# vps-snapshot-20260710 バックアップ検証（issue #15）

VPS の 2026-07-10 時点インフラスナップショットから著者が復元・取得したバックアップ
を現行 vps escrow（EV-0001〜EV-1633）と照合し，ログローテーションで欠損した創成期
（2026-06-10〜06-18）セッションが回復できるかを検証した．**結論: 回復対象は存在しない．
当該期間の leray-hopf セッションは VPS 上にそもそも存在しなかった**（喪失ではなく非存在）．

## 検証対象

| 項目 | 値 |
|---|---|
| バックアップ | `/private/sources/KSE2026/backup-from-vps-snapshot-20260710.tar.xz` |
| sha256 | `ad71e1a93710bceeedc761b375851b5bb2c4688e6019db6846f93950febfda37` |
| サイズ / エントリ数 | 128,458,556 bytes / 18,688 entries |
| 内容 | `~/.claude/` 一式ほか（`~/.hermes/`・`~/.bash_history` は**含まれない**） |
| 検証日 | 2026-07-22（分析環境，Claude Code） |

注意: tar 内には mtime が 2026-07-21 のファイルが少数含まれる．バックアップは復元
インスタンスの稼働後に取得されたため，復元後に動いたセッション由来の更新が混入して
いる（leray-hopf 関連 dir には影響しないことを個別照合で確認済み，下記）．

## 照合手順と結果

1. **leray-hopf 関連 project dir の全ファイル照合**（tar 展開 → sha256 比較）:
   - `-workspaces-lean-pde`: バックアップ側 947 ファイル中 **943 が現 escrow と
     byte-identical，4 件（`memory/*.md`）は escrow 側がより新しい**．バックアップ
     にのみ存在するファイルは **0 件**．
   - `-workspaces-lean-pde-notes`，`-workspaces-lane-d-bochner`，
     `-home-vscode`，worktree 系 2 dir: いずれもバックアップ側にのみ存在する
     ファイルは **0 件**．
   - すなわちバックアップの leray-hopf 関連部分は現行 escrow の真部分集合．
2. **セッション mtime 分布**: バックアップ内 `-workspaces-lean-pde` の最古ファイルは
   2026-06-19（1 件），実質的な開始は 2026-06-20．6/10〜6/18 のファイルは皆無．
3. **ローテーション喪失説の排除**: バックアップ内 `.claude/.last-cleanup` は
   `2026-07-07T16:17:51Z`．30 日保持での削除下限は約 2026-06-07 であり，
   6/10〜6/18 のセッションが存在していれば 7/10 スナップショットに残っていたはず．
   残っていない以上，ローテーションによる削除では説明できない．
4. **決定的証拠 — global prompt history**: `.claude/history.jsonl`（ローテーション
   非対象，2026-04-26 まで遡及，全 1,340 prompts）において，cwd `/workspaces/lean-pde`
   での最初のプロンプトは **2026-06-19T14:48:36Z**．VPS 上の leray-hopf 作業は
   6/19 に開始しており，それ以前の作業記録が VPS に存在した形跡はない．

## 期間カバレッジの帰結

| 期間 | 一次資料 | 所在 |
|---|---|---|
| 2026-06-10（init，27 commits）〜06-14 | **セッションログ無し**（全 host） | Git/GitHub 証跡からの再構成のみ（evidence_type=reconstructed） |
| 2026-06-15〜06-18 | **有り**（local-secondary escrow，`research-lean-pde` 最初期セッション 2026-06-15〜） | EV-1681〜EV-2126 の一部（issue #5） |
| 2026-06-19 以降（VPS） | 有り（現行 vps escrow で連続） | EV-0001〜EV-1633 |

- issue #15 が期待した「6/15〜6/18 の回復」は，当該期間の実作業が local 側で行われて
  いたため VPS スナップショットには対象が無かった．同期間は local-secondary escrow が
  一次資料としてカバーする．
- 残る真の欠損は **6/10〜6/14 のセッションログ**．local-secondary の最古生存セッション
  が 6/15 であることは，同マシンの 30 日ローテーション（2026-07 中旬の cleanup で
  下限 ≈ 6/15）と整合し，**6/10〜6/14 分は local-secondary 上でローテーション削除された
  可能性が高い**（`cleanupPeriodDays=9999` 設定は 2026-07-21 で，それ以前の削除は不可逆）．
- バックアップ由来ファイルの manifest 登録は行わない（新規情報ゼロのため）．本文書と
  上記 sha256 が検証の provenance を与える．

## 派生的知見（vps escrow の補完余地）

バックアップには現行 vps escrow が収集していない種別（`~/.claude/history.jsonl`・
`tasks/`・`plans/`）が含まれていた．これらはローテーション非対象のため，**現行 live VPS
から直接収集する方が新しく完全**（local 2 host の escrow レイアウトとも揃う）．
著者側での補完収集を推奨（→ issue #2 へ報告）．
