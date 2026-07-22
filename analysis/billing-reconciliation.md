# Vertex 完成フェーズ — billing 照合（issue #23 / #26 / #28）

owner 提供の Google Cloud 側記録と escrow セッションログの照合結果．第 1 弾（#26）
のサービスレベル照合を，第 2 弾（#28）の **SKU レベル請求 + モデル別 Cloud
Monitoring 実測**で拡張した（FX 下界と leray 帰属は下記のとおり metric 解釈への
条件付き．issue #42 項目 3）．raw export は Git 外
（`/private/sources/KSE2026/GoogleCloudLog.tar.xz`，更新版 sha256
`e0e38e45d6788529845b2a09a4aee107e5e3492dc3945137e02c75d27ade9088`）．
公開領域には redaction 済み集計のみを置く:
`evidence/metrics/vertex-completion-phase-billing.csv`（サービス×日次）と
`vertex-completion-phase-billing-sku.csv`（SKU×日次）．再現は
`scripts/extract_vertex_phase.py`（出力: `vertex-completion-phase-{usage,summary}.json`）．

## 確定結果

| 量 | 値 |
|---|---|
| 総請求（PT 07-02〜07-03，credits 0，JPY） | **¥54,867.9**（SKU 18 本の合計と一致 ±0．**無条件**） |
| escrow（leray-hopf 分）の公表単価換算 | **$258.28**（**無条件**） |
| 実効換算レート | **[160.4, 161.8] ¥/$**（上界 161.8 は残差非負性のみによる無条件の同定．**下界 160.4 は下記 metric 解釈への条件付き**．点推定 161.8） |
| **leray-hopf 単独の実請求（条件付き導出値）** | **¥41,421〜41,796**（点推定 ≈¥41,796，総請求の **75.5〜76.2%**．区間の下限側は同じ条件に依存） |
| escrow 外（machine-wide 残余）の相当額 | ¥13,072〜13,447（23.8〜24.5%．同条件） |

## 方法と根拠

1. **SKU 構成**: 請求は model ×（input / output / cache write TTL300s / cache read）
   × context tier（0–200K / 200K–1M）× region（global / us）の SKU に分かれる．
   **第 1 弾で置いた long-context premium 仮説は棄却された** — >200K tier の SKU は
   存在するが**単価は標準レートと同一**（hi-tier セルの implied レートが標準単価で
   161.8〜162.1 に収束する事実による．first-party の「Opus 4.8 は 1M context を
   標準単価で提供」とも整合）．
2. **実効レートの両側同定（下界は条件付き）**: 各 SKU セルの
   `implied = 請求¥ / (escrow 数量 × 標準単価)` は escrow 外利用 U ≥ 0 により常に
   FX 以上，したがって **min implied = 161.8 は FX の上界**である（codex レビュー
   指摘のとおり，これ単独では点推定にならない．この上界は無条件）．
   一方 FX を下げると各セルの残差トークンが単調増加し，machine-wide の Monitoring
   実測を超えてしまう — この制約から **下界 160.4** が得られる．
   **ただしこの下界は metric 解釈に条件付きである**: Cloud Monitoring
   `publisher/online_serving/token_count` の区間積分を「escrow の
   input+output+cache_read+cache_write 合算と同一母数の物理的上限」として扱って
   いるが，公式 metric 記述（accumulated input/output token count，`type` と
   `explicit_caching` ラベル付き）から cache token の算入方法は自明でなく，
   **手元の raw export（Metrics Explorer チャート出力）は系列 ID が opaque
   （`tex-chart-*`）でラベル内訳が残っていないため，既存データからは検証できない**
   （2026-07-23 確認，issue #42 項目 3）．よって FX ∈ [160.4, 161.8] のうち下界側，
   およびそれに依存する leray 帰属区間の下限は「当該 metric 解釈の下での導出」と
   して扱う．Metrics Explorer で Group by `type` + `explicit_caching` を付けた
   再 export が得られれば，この条件は実測で解消できる（owner 向け導線）．
   点推定として上界 161.8 を採るのは，(a) カテゴリ・モデルの異なる 3 セル
   （fable cache write hi / opus cache write hi / opus input hi）が 0.2% 以内で
   収束しており，3 セル同時に比例的な escrow 外利用を持つことは考えにくい，
   (b) その場合の残差が Monitoring gap をほぼ飽和する（83% / 96%），の 2 点による．
3. **残差 = escrow 外利用の定量化**: FX=161.8 でセル残差をトークン換算すると
   fable ≈ 3.42M / opus ≈ 20.67M．これは**独立の実測**である Cloud Monitoring
   `publisher/online_serving/token_count`（machine-wide，5 分 rate の区間積分）の
   escrow 超過分 fable 4.11M / opus 21.50M と両モデルで符合する（83% / 96%．
   点推定を FX 上界に取るため残差は最小評価となり，gap をやや下回る側に出る）．
   escrow 外利用の実体は，全 project 混在 prompt history で確認済みの
   Vertex 設定作業セッションと別プロジェクト作業（07-02〜07-03）．
4. **補助証拠**: region=us の SKU（計 ¥10.8）は region を global に設定する前の
   セットアップ痕跡と整合．リクエスト数軸は第 1 弾どおり
   （StreamRawPredict ≈ 1,234 vs escrow 1,154，429 は 6 件）．

## 論文で使ってよい数字（cost-attribution-methodology.md の区分に従う）

- **provider-billed actual cost（machine-wide，実測，無条件）**: ¥54,868
- **leray-hopf 単独の実請求（条件付き導出値）**: ¥41,421〜41,796（= FX 区間 ×
  $258.28，点推定 ≈¥41,796）．脚注で「SKU レベル照合で同定した実効レート区間に
  よる導出値であり，区間の下限側は Monitoring token_count が cache token を含む
  という metric 解釈に依存する」と明示する．
- **API-equivalent（全キャンペーン下界，無条件）**: $6,972.83
  （`usage-metrics.json`，campaign end 07-20）．うち Vertex 期間 $258.28．

## 残る限界

- 実効レート区間 [160.4, 161.8] は請求からの同定値であり，reseller の公称レート・
  手数料率の内訳（Google 月次レート + 手数料等）はこの資料からは分解できない
  （必要なら reseller へ照会，issue #23 owner 判断）．公称レートが判明すれば
  点推定は不要になる．
- escrow 外利用のセッションログは leray-hopf の証跡ではないため取得しない
  （トークン量は上記のとおり残差と monitoring で十分に拘束されている）．
