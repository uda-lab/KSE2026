# コスト帰属の二層区分（issue #23）

論文中の計算資源記述は，性質の異なる次の二層を**常に区別して**提示する．

## 層 1 — API-equivalent cost（再構成推定値・下界）

- **定義**: escrow セッションログの `message.usage`（API レスポンス由来の一次記録）に
  公表 per-MTok 単価を適用した換算額．
- **対象**: 全キャンペーン（2026-06-10〜07-20，release 日終端．issue #42 項目 4）．算出は `scripts/extract_usage.py`，
  現行値は `evidence/metrics/usage-metrics.json`（$6,972.83，provider 別内訳あり）．
- **性質**: ログ欠損（6/10〜6/14 ほか）と escrow 選別のため**下界**．subscription
  期間については実支出とは無関係（定額）であり，「実請求額」とは呼ばない．
  呼称は *API-equivalent cost (reconstructed lower bound)* に統一する．

## 層 2 — provider-billed actual cost（実測値）

- **定義**: provider の請求記録に基づく実請求額．現状唯一の対象は **Vertex 完成
  フェーズ**（PT 2026-07-02〜07-03）: **¥54,868**（JPY 建て，credits/discounts 0，
  `evidence/metrics/vertex-completion-phase-billing{,-sku}.csv`）．
- **性質**: 課金主体側の実測であり最も硬い数字だが，**当該マシンの全 Vertex
  トラフィック**を含む（leray-hopf 外の利用が混在）．SKU レベル照合（#28）により
  **leray-hopf 単独分は ¥41,421〜41,796（総請求の 75.5〜76.2%，点推定 ≈¥41,796）と導出済み** — 実効レート
  区間 [160.4, 161.8] ¥/$ を SKU 残差非負制約（上界）と Monitoring 実測制約（下界）の両側から同定した
  （`billing-reconciliation.md`）．
- 呼称: machine-wide の実測は *provider-billed actual cost*，leray 単独分は
  *derived actual cost (SKU-reconciled)* と区別して呼び，導出である旨を脚注に添える．

## 提示規約

1. 二層を同一の表に載せる場合は列を分け，単位（USD 換算 / JPY 実請求）を混在させない．
2. 「この金額で証明が完成できる」等の因果・一般化主張はしない（#23 方針）．
   位置付けは *audited resource profile of the final completion campaign*．
3. Vertex 完成フェーズの形式化成果との対応（T-AL-1〜6 → leray-hopf#89 で
   `aubin_lions` 公理除去 = T³ capstone 無条件化）は `analysis/project-timeline.md`
   と issue #23 コメントの対応表を典拠とする．
4. 費用の出所（研究費・支援制度）は acknowledgment に記載し，resource profile とは
   分離する（文言は owner が `provenance/author-decisions.md` に確定させる）．
5. CLM の扱い: CLM-002（層 1）は現行のまま．層 2 を独立 claim とするかは Phase 3
   の contribution freeze で owner が判断する（それまで claim 化しない）．
