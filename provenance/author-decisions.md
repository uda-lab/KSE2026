# Author decisions — 著者判断の記録

scientific owner による確定判断のみを記録する（提案・候補は notes/ へ）．
各判断には日付と根拠を付ける．

| 日付 | 判断 | 根拠 / 備考 |
|---|---|---|
| 2026-07-20 | 参照対象を leray-hopf v0.1.0-rc1（7c15710a）に暫定固定 | scaffold 時点の最新 release tag．Phase 6 で最終固定を再確認 |
| 2026-07-20 | ビルド主系を TeX Live pdflatex + latexmk に決定（tectonic は draft fallback） | owner 指示．IEEE 投稿パイプライン（PDF eXpress 等）は pdflatex 出力前提のため |
| 2026-07-22 | 研究費 acknowledgment 文言を確定: "This work was supported by JST-Mirai Program Grant Number JPMJMI22G1, Japan." | owner 指示（issue #23 コメント）．resource analysis とは分離して first-page footnote / acknowledgment に記載（`analysis/cost-attribution-methodology.md` 提示規約 4） |
| 2026-07-22 | reseller 公称レート照会は保留のまま先へ進む | owner 判断（issue #23 コメント）．実効レート区間 [160.4, 161.8] ¥/$ で論文用途は充足．請求書到着時に外部一致検証へ格上げ可 |
| 2026-07-23 | **論文主題を B + C 統合に確定**（AI 支援形式化の方法論 + incident ケーススタディ．形式化成果 CLM-001 は全節を支える中心 artifact） | owner GO（issue #35 判断 1，補足コメント 2026-07-23 でも「B+C 統合…への GO は維持」と再確認）．PLAN.md §6 の統合条件（強い失敗事例 + 再発防止策の対）は INC-001×INC-002 / INC-004 / INC-005 で成立 |
| 2026-07-23 | **contribution 3 点の大枠を確定**: (1) Leray–Hopf 弱解存在の kernel-only 形式化を agent 主体開発で完遂，(2) kernel/build では防げない失敗様態の分類と防御の実証（statement-first / adversarial review / 検証ゲート），(3) セッションログ保全・定量化の方法論（escrow + manifest + 再現スクリプト + 実請求照合） | owner GO（issue #35 判断 2 + 補足コメント）．baseline 対応は `claims/contribution-map.md`（issue #47）．最終英文は Phase 4 原稿で確定し，abstract に反映 |
| 2026-07-23 | **incident 採否を確定**: INC-001 主例 / INC-002 対照例 / INC-005 resource 節主例 / INC-004 短例（紙幅次第で表内 1 行へ格下げ可）/ INC-003 は方法論節で言及 | owner GO（issue #35 判断 4 + 補足コメント）．`analysis/incident-ranking.md` v2 のとおり |
| 2026-07-23 | **タイトルを確定**: *Formalizing Leray–Hopf in Lean 4 with AI Agents: Workflow, Incidents, and Recovery* | owner（issue #35 コメント: 案 2 preferred・合体形も OK → チャットで合体形を確定 2026-07-23）．abstract は claim freeze 後に起草し frozen claim のみで構成 |
| 2026-07-23 | **claim freeze の前提条件**: CLM-002〜005 は issue #42 の校正（期間分離・条件付き化・強度弱化）を反映した文言で freeze する．freeze 作業自体は夜間自律実行を owner 承認 | owner（issue #35 補足コメント 2026-07-23 + チャット判断: 「夜間に freeze まで実施」）．校正の実装は PR #44 |
| 2026-07-23 | **FX 下界の扱い**: Monitoring `token_count` の metric 解釈が既存 export から検証不能と確認されたため，[160.4, 161.8] の下界側は条件付き表記で維持（撤回しない）．¥54,868・$258.28 は無条件 | owner（チャット判断 2026-07-23）．再 export（Group by type + explicit_caching）が得られれば無条件化できる |
