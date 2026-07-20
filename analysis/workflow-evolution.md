# Workflow evolution（Phase 2 で作成）

agent orchestration の体制（役割分離，statement freeze，編集権限，スキル，モデル
escalation，資源管理）が開発期間を通じてどう変化したかを，導入時期・導入契機
（多くは incident）とともに時系列で記録する．

sections/03-agent-workflow.tex の主張は本文書で裏付けられた範囲に限る
（workflow reviewer の検査対象．PLAN.md §8）．

## 書式

| 時期 | 変更 | 契機（incident / 判断） | Evidence |
|---|---|---|---|

## 記録すべき軸（PLAN.md §7.3）

- 役割分離（architect / planner / coder / prover / reviewer）の導入と変遷
- statement freeze・編集権限の運用
- 検証スキル（axiom check，release cone check 等）の導入時期
- モデル選択・escalation の方針
- 資源管理（build lock，`.lake` 共有，メモリ headroom 規約）の導入時期
