# Vertex 完成フェーズ — billing 照合（issue #23 / #26）

owner 提供の Google Cloud 側記録（reseller 請求レポート + API monitoring CSV）と
escrow セッションログを 3 軸（金額・リクエスト数・期間）で照合した．raw export は
Git 外（`/private/sources/KSE2026/GoogleCloudLog.tar.xz`，sha256
`6162cbeb49ff3c336a288c610c456d086b3be207b0c954ad788f75c1cba55da5`）に保存し，
公開領域には redaction 済み集計（`evidence/metrics/vertex-completion-phase-billing.csv`
= 日付×モデル×JPY のみ）を置く．再集計・突合は
`scripts/extract_vertex_phase.py` で再現できる（出力:
`vertex-completion-phase-usage.json` / `vertex-completion-phase-summary.json`）．

## 結果サマリ

| 軸 | billing 側 | ログ側（escrow） | 判定 |
|---|---|---|---|
| 期間 | 課金日 2 日（PT 07-02・07-03．GCP 日次課金は PT 基準で，UTC 07-04 早朝分は PT 07-03 に入る） | `_vrtx_` 初出 2026-07-02T12:06:07Z 〜 最終 07-04T06:56:33Z | **一致** |
| リクエスト数 | 推論系 StreamRawPredict ≈ 1,234（monitoring 積分．ほか RawPredict ≈ 1,082 は大半が可用性プローブで 404 = 538 件を含む．429 は 6 件のみ） | dedup 済み API メッセージ 1,154 | **整合**（差はプローブ・中断・escrow 外分） |
| 金額 | **¥54,867**（fable ¥36,121 / opus ¥18,746，credits 0） | 公表単価換算 **$258.28**（>200K long-context premium 適用時 $297.89） | **下界として整合**（下記） |

## 金額照合の詳細（PT 日×モデル）

| PT 日 | model | turns | >200K ctx | est\$ (std) | est\$ (premium) | 請求 ¥ | implied ¥/\$ (std) | (premium) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 07-02 | fable-5 | 247 | 30 | 77.87 | 85.46 | 14,741 | 189.3 | 172.5 |
| 07-02 | opus-4-8 | 151 | 24 | 22.88 | 31.41 | 4,578 | 200.0 | 145.8 |
| 07-03 | fable-5 | 372 | 13 | 115.16 | 120.91 | 21,380 | 185.7 | 176.8 |
| 07-03 | opus-4-8 | 384 | 122 | 42.37 | 60.11 | 14,168 | 334.4 | 235.7 |

implied レートがセル間で一様でないことから，単一の為替換算では説明できない．
要因は次の 3 つで，いずれも記録で裏づけがある:

1. **long-context premium（定量・部分）**: プロンプト側 200K 超のリクエスト
   （opus 07-03 は 384 中 122 turns）は公表の >200K премium（入力系 2×・出力 1.5×）
   の対象．適用で総推定は $258.28 → $297.89 に上がり，セル間の広がりは
   186–334 → 146–236 に縮む．
2. **母集合の差（定性・主要残差）**: 請求は**当該マシンの全 Vertex トラフィック**を
   含むが，escrow は leray-hopf 関連セッションのみ．全 project 混在の prompt
   history（escrow 済）には，同窓内に **escrow 対象外のセッション**が存在する —
   Vertex 環境設定の作業セッション（07-02T12:00Z 頃〜，16 prompts）と，別プロジェクト
   の issue 整理セッション（07-03T11:41Z 頃〜，PT では 07-03）など．後者は opus 07-03
   セルの残差（premium 適用後もなお implied 236 vs fable の ~175）の位置・向きと
   整合する．これらのセッションログは leray-hopf の証跡ではないため escrow 外であり，
   トークン量は本リポジトリからは定量できない．
3. **為替・reseller 条件（未確定）**: 請求は reseller 経由の JPY 建てで，適用レート・
   手数料は本資料からは特定できない．premium 適用後の blended implied は 184.2 ¥/$．

**結論**: ログ側推定 $258.28（leray-hopf 分，公表単価）は請求 ¥54,867 の**下界**として
整合する．「leray-hopf 分の実請求額」を単独で確定するには，(a) SKU レベルの
トークン数つき billing export（BigQuery detailed export），または (b) reseller の
適用為替レート，の少なくとも一方が必要（owner 判断，issue #23 継続項目）．

## 補助観測（monitoring CSV より）

- 429（rate limit）は期間全体で 6 件 — スループット制約はほぼ無かった．
- 404 = 538 件は未提供モデルへの可用性プローブと整合（escrow 内 memory
  `subagent-model-routing.md` の「全モデルをプローブした」記録どおり）．
  課金対象外（トークン消費なし）．
- 課金明細の credits / discounts は 0，通貨は JPY．

## 論文で使ってよい数字

- **provider-billed actual cost**: ¥54,867（PT 07-02〜07-03，Vertex AI 上の
  Claude Fable 5 + Claude Opus 4.8，credits 0）．ただし脚注で「同一マシンの
  escrow 外利用を含む」旨を明示する．
- **leray-hopf 分の API-equivalent（下界）**: $258.28（premium 適用 $297.89）．
- 両者を同一表で並べる場合は `analysis/cost-attribution-methodology.md` の
  区分規約に従う．
