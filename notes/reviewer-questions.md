# Reviewer questions — 想定質問と回答方針

査読者から来そうな質問を先回りして列挙し，本文・limitations での扱いを決める．

| # | 想定質問 | 回答方針 | 反映先 |
|---|---|---|---|
| 1 | 形式化は本当に「Leray–Hopf 弱解」か？弱形式の定式化は標準的か？ | separated-variable 形式である制限を明示し，docs/claims-and-scope.md を引く | §2, limitations |
| 2 | AI エージェントの寄与は測定されているのか？ | 因果測定はない．対照群なしのケーススタディであると明言 | §6 limitations |
| 3 | 失敗事例の選択にバイアスはないか？ | incident-ranking に不採用理由を残し，選定基準を本文に書く | §4 |
| 4 | ログが欠損しているのにどう信頼するのか？ | evidence_type（primary/reconstructed）と confidence の区別を説明 | §4–6 |
| 5 | Claude Code 固有の話で一般化できるのか？ | ツール非依存の設計知見に変換して提示（PLAN.md Phase 4） | §3, §5 |
| 6 | kernel-only の確認は誰がどう行ったのか？ | release cone check + build attestation の仕組みを引用 | §2, §5 |

（追記していく）
