# 著者インターフェース上の逸脱の記録

GitHub 上に残る書き込みのうち，著者の意図から外れた，あるいは後続で訂正された事例を
記録する．役割・権限と経路の 4 類は `analysis/author-interface-model.md`．

## 1. 逸脱はどの層で生じているか

記録される逸脱は，**指示の解釈と実行**の層で生じている．権限の所在が移った事例は
記録上存在しない．具体的には次の型が観測される．

| 型 | 例 |
|---|---|
| issue 本文の scope 誤り（Lean signature の誤引用，進行中作業との衝突） | `leray-hopf#13`，`leray-hopf#14` |
| 独立レビュー無しでの merge と，その訂正自体の不備 | `leray-hopf#177`，`leray-hopf#178` |
| レビュー所見が発され，同一巡内で撤回される | `leray-hopf#174` |
| 古いリポジトリ状態に依拠したレビュー判定が反転する | 同日中の自己訂正 |
| 陳腐化した issue 本文への反復的な自己訂正 | 複数 issue |

`leray-hopf#177`（レビュアー 0・レビュー 0 での merge）は，独立レビュー規則の導入直後に
同型の handoff-failure が再発した事例であり，`evidence/incidents/INC-001.md` が
記録する．corpus 中で最も明瞭な逸脱である．

## 2. 逸脱を過大に数えないための negative finding

- **`not planned` として close された issue は無い．** close 済みの issue はすべて
  `completed` である．
- **unmerged のまま close された PR は無い．**
- **当否が確定した技術的主張は正しいものとして採録されている．** `leray-hopf#158` の
  `p = q = 1` 反例は，`evidence/incidents/INC-001.md` が statement を偽と確定させた
  根拠であり，INC-001 の是正を駆動している．本書の著者が数学的当否を独立に評価したと
  いう主張ではない（`PLAN.md` §8 は別の役割に割り当てている）．

これは「技術的な誤りが無かった」という意味ではない．上表の 1 行目のとおり，
事前照合層が派遣前に訂正した誤りが存在する．

## 3. incident との対応

| incident | 対応 |
|---|---|
| INC-001 | 検出から是正までの GitHub 上の連鎖（`leray-hopf#145`・`leray-hopf#157`・`leray-hopf#158`・`leray-hopf#177`・`leray-hopf#178`）．Lean 側の修正 PR は該当しない |
| INC-005 | `leray-hopf#174`・`leray-hopf#175`・`leray-hopf#176`．`leray-hopf#174` が撤回を含む |
| INC-002／INC-003／INC-004 | 対応なし．**この不在は報告に値する**: merge 前検出が最もよく効いた 2 件の incident に，著者インターフェースは登場しない |

## 4. 限界

セッションログの被覆には欠落があり，本書の逸脱一覧は悉皆ではない．GitHub 上に痕跡を
残さない指示・訂正は原理的に含まれない．
