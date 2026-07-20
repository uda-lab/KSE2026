# Project timeline（Phase 2 で作成）

Git commit，Issue，PR，セッションログを統合した leray-hopf 開発の時系列．
`scripts/build_timeline.py` の出力を骨格とし，手動注記を加える．

## 書式

| 日時 (UTC) | 種別 | 参照 | 概要 | Evidence |
|---|---|---|---|---|
| | commit / issue / pr / session / incident / decision | leray-hopf@sha 等 | | EV-NNNN |

## 注意

- 一次ログ（primary）と再構成（reconstructed）を `Evidence` 列の manifest 登録で
  区別する（PLAN.md §4）．
- ログ欠損期間はその旨を行として明示する（欠損の隠蔽をしない）．
