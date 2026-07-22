# Usage メトリクス — 方法論と限界（issue #14）

`scripts/extract_usage.py` により，manifest 登録済み escrow（EV-0001〜EV-2126 の
`claude-projects/**/*.jsonl`）から Claude Code セッションのトークン消費・API 換算
コスト・所要時間を機械集計する．出力は `evidence/metrics/usage-metrics.json`．

## 集計方法

- **一次記録**: 各 JSONL 行の `message.usage`（API レスポンス由来）．同一 API
  レスポンスは複数行（content block ごと）に現れ `message.id` を共有するため，
  **`message.id` による全域 dedup** を行う（検証: 同一 id の行間で usage 値は不変．
  複数 host に同一ファイルが存在する場合の二重計上も同時に防がれる）．
- **集計軸**: model × UTC 日付 × host．subagent transcript も API 呼び出しとして
  計上する（別ファイル・別 message.id）．
- **単価**: 公表単価（platform.claude.com，2026-07-22 参照）を script に内蔵．
  cache write 5m = 1.25×input，write 1h = 2×input，read = 0.1×input．
  TTL 内訳が無い cache_creation は 5m として計上（コスト下界側）．
- **時間**: top-level セッションファイル（`claude-projects/<proj>/<uuid>.jsonl`）
  ごとに wall-clock（最初と最後のタイムスタンプ差）と active 時間
  （連続イベント間 gap を閾値で打ち切った総和）を算出．感度分析として
  gap 閾値 1 / 5 / 15 分の 3 通りを出力に含める．subagent の活動は親セッションの
  時間窓に概ね含まれるため時間集計には独立計上しない．

## 主要結果（2026-07-22 実行，EV-0001〜EV-2126 時点）

| 指標 | 値 |
|---|---|
| 走査ファイル / dedup 後 API メッセージ数 | 809 / 48,733 |
| output tokens | 15.1M |
| cache read tokens | 8.78B |
| **API 換算コスト** | **$6,980**（内訳: Opus 4.8 $3,513，Fable 5 $1,756，Sonnet 5 $1,297，Sonnet 4.6 $410，Haiku 4.5 $5） |
| top-level セッション数 | 61 |
| wall-clock 総和 | 1,023.5h |
| active（gap cap 1m / 5m / 15m） | 95.3h / 199.7h / 310.5h |

モデル別・日次の内訳は `evidence/metrics/usage-metrics.json` の
`by_model` / `by_model_date_host` を参照．

## PoC 集計（2026-07-21 owner 報告）との差異

PoC（600 sessions, output 67.6M, ≈$19,157, active(5m) 389.7h）と本集計は
**対象範囲と計数方法が異なる**:

1. **スコープ**: PoC は live マシンの `~/.claude/projects/` 全体（leray-hopf と
   無関係のプロジェクトを含む）に対する概算．本集計は escrow に選別済みの
   leray-hopf 関連ディレクトリのみ（論文で主張すべき範囲）．
2. **計数**: PoC は行単位（同一 API レスポンスが平均 ~2.9 行に重複）．本集計は
   `message.id` dedup 済み．

論文には本集計（再現可能・evidence 対応済み）のみを用いる．

## Provider 区分 — VertexAI 経由期間（2026-07-02〜07-04）

owner 報告（2026-07-22）により，Fable 5 再公開直後の一時期，local-secondary の
作業の一部が subscription ではなく Google Compute 上の **VertexAI 経由**で実施
されていたことが判明した．Vertex 経由の API レスポンスは message / tool-use ID
に `_vrtx_` プレフィックス（`msg_vrtx_…` / `toolu_vrtx_…`）を持つため，
`extract_usage.py` は全メッセージを `provider = vertex / first-party` に機械判別
して集計する（出力 JSON の `by_provider` と各行の `provider` 列）．

| provider | 期間 | turns | output tok | API 換算 |
|---|---|---:|---:|---:|
| vertex | 2026-07-02〜07-04（local-secondary，`research-lean-lean-pde` 17 sessions） | 1,154 | 802,530 | **$258.28**（fable-5 $193.02 / opus-4-8 $65.25） |
| first-party | 全期間 | 47,579 | 14,346,785 | $6,722.29 |

- **Google Cloud 側記録との突合キー**: 日次×モデル×メッセージ数・トークン内訳
  （input 186,836 / output 802,530 / cache write 12,024,194 全量 5m TTL /
  cache read 131,232,324）．単価は公表 per-MTok 表（Vertex も同一）で換算．
- 傍証: vertex 行は `service_tier` 欠落・`inference_geo` 空．当時のモデル可用性
  （該当デプロイでは fable-5 と opus-4-8 のみ）と routing 判断は escrow 内 memory
  `subagent-model-routing.md`（EV 登録済）に記録がある．
- 限界: ログ外の消費（CLI 可用性プローブ等の微小分），課税・通貨換算，Claude 以外の
  Vertex 費用は本集計に含まれない．Google Cloud 側の billing/monitoring 統計の
  evidence 化は owner が別途判断（issue #24）．

## 既知のカバレッジ欠損（本集計は下界）

1. **ログローテーション**: 2026-06-10〜06-14 のセッションは全 host で喪失
   （`vps-snapshot-20260710-verification.md`）．VPS 側は 6/19 に作業開始のため
   6/19 以降は連続．
2. **local-secondary の途中状態**: 収集時 live だったセッション `b60e5aa1` は
   2026-07-21T02:06Z 時点までの部分記録．
3. **レビュワー側計算資源**: codex / copilot レビューの推論コストは対象外
   （回数のみ GitHub snapshot から計上可能）．
4. **Hermes orchestrator sessions は除外**（2026-04-27〜05-28 の別プロジェクト
   作業であることを 2026-07-21 に確認済み．leray-hopf 期間と重複しない）．
5. **単価の注意**: claude-sonnet-5 は定価（$3/$15）で換算．2026-08-31 まで
   導入価格（$2/$10）が適用される期間だが，換算は定価で統一（差は総額の 1% 未満）．
   `<synthetic>` レコード（188 件）は API 呼び出しではないため除外．

以上より，掲載する消費量・コスト・時間はいずれも**下界**である．
