# Limitations — 論文に明記する限界

Phase 4–5 で本文（sections/05-discussion.tex）へ反映する．追加を見つけたら
ここに先に登録する．

## 形式化の限界（claims/formalization-scope.md「主張してはならないこと」と同期）

- 外力なしの NSE のみ，有限 time horizon，separated-variable 弱形式．
- regularity・uniqueness は扱わない．

## 方法論・ケーススタディの限界（PLAN.md §7.6）

- 単一プロジェクト，単一チームのケーススタディであり，一般化には制約がある．
- セッションログに欠損期間があり，一部の出来事は Git/Issue/PR からの再構成である
  （各所で evidence type と confidence を明記する）．
- 使用した AI モデル・ツールは更新され続けており，同一の挙動の再現は保証できない．
- proprietary tool（Claude Code 等）固有の操作と，一般化可能な方法論の区別が必要．
- AI エージェントの効果は因果として測定されておらず，対照群がない．
- 人間（scientific owner）の監督・介入が結果に不可分に寄与している．
