# Session coding schema（符号化スキーマ）

各セッションの出来事を要約ではなく符号で記録する（PLAN.md §5）．
符号化結果は `evidence/session-index/` に置く．

## Event codes

| Code | 意味 |
|---|---|
| MATH-ERR | 数学的意味の誤り |
| STMT-MISMATCH | Lean statement と自然言語上の意図の不一致 |
| WEAKEN | theorem weakening / vacuous discharge / assumption smuggling |
| PROOF-STUCK | proof engineering の行き詰まり |
| HANDOFF-FAIL | agent 間の責任境界または handoff の失敗 |
| FALSE-SUCCESS | build 成功報告と実際の状態の不一致 |
| WT-CONFLICT | worktree / branch / file ownership の衝突 |
| RESOURCE | memory exhaustion / swap / build lock / cold build 等の資源問題 |
| MODEL-ESC | モデル選択または escalation の失敗 |
| RECOVERY | 検出・隔離・修正・再発防止に成功した事例 |

## 1 セッションあたりの記録項目

- session_id（manifest と一致させる），host，日時範囲，working directory
- 関与 model / tool，役割（architect / planner / coder / prover / reviewer / orchestrator）
- event 列: `[code, 発生位置（行番号 or timestamp）, 一行説明, incident候補? yes/no]`
- 成果: 触れた Lean ファイル・定理，commit / PR への接続
- coder（符号化担当者）と confidence

## 運用

- 符号化は incident analyst が行い，形式化成果の評価と独立に進める（PLAN.md §8）．
- incident 候補（yes 判定）は `analysis/incident-candidates.md` へ転記する．
