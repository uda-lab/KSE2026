# Author decisions — 著者判断の記録

著者による確定判断のみを記録する（提案・候補は notes/ へ）．
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
| 2026-07-24 | **content-first 全面改稿**: method/harness を主，incident をその検出範囲と限界の証拠として再配置する．想定読者は AI for Math に関心がある harness 初学者の数学者．同じ粒度の反復，repo 固有識別子への依存，口語・過剰列挙・ダッシュを除去し，独立 prose/claim/audience review を必須化する | owner の改稿指示．過去の B+C の比重，section 配分，exact-six-page drafting を事後改訂する権限を明示的に付与 |
| 2026-07-24 | **2026-07-23 のタイトル確定を再検討対象へ戻す**: harness-led 改稿に整合する新タイトルを PR #59 で提案し，最終確定は owner review まで保留する | owner は既存の repo 内決定事項を本改稿で一律に事後改訂してよいと明示．旧タイトルは当時の決定記録として残し，新タイトルの status は `notes/title-and-abstract.md` に proposal として記録 |
| 2026-07-24 | **ページ制約の段階分離**: KSE の最終6ページ上限は維持するが，内容・論旨・文章品質を確定する PR ではページ数を acceptance gate にしない．圧縮は独立した後続段階で行う | owner の改稿指示．issue #57 の旧 acceptance を更新 |
| 2026-07-24 | **主図を別 issue #58 で owner が清書**: 本改稿 PR は synthesized end-state harness の図案・挿入位置を記録し，未完成画像を本文に置かない | owner の改稿指示．最終 artwork の採否と清書は owner |
| 2026-07-25 | **owner review へ移行し，追加の Codex/Copilot 自動レビューを停止**: 防御的な review 痕跡，非標準的なハイフン複合語，過剰なコロン・セミコロン，repo 識別子中心の説明を本文から除く．一般的な software ceremony ではなく，owner が準備した `github-driven-workflow`，Git worktree，専門役割，VPS container の実態を中心にする | owner の本文レビュー．追加自動レビューの費用対効果が低いとの判断を受け，以後の品質判断は owner review に委ねる |
| 2026-07-25 | **`github-driven-workflow` は Fable 登場以前からの owner 提供 harness**: Fable は後期に既存の model-independent な orchestrator 役を担ったのであり，workflow の成立主体・所有者・設計者として書かない | owner の時系列・権限関係の訂正．paper，claim ledger，contribution map，figure spec の全てでこの関係を維持する |
| 2026-07-25 | **Fable の交代を harness contribution として強調しない**: 一般的な Claude Code 利用では model 交代後も外部の権限と merge 規則が残ることは非自明ではない．本文では，Issue scope・review decisions・merge authority を agent session 外へ記録し，Fable が 7 月 2〜3 日にその記録から既存 workflow を再開した事実だけを補助例として述べる | owner review で「model-independent な authority」という抽象的論旨の新規性を棄却．Fable は Section III の一例に限定し，abstract・contribution・conclusion・図案では強調しない |
| 2026-07-25 | **追加 agent review の対応範囲**: scanner fail-open，release attestation の区別，PR #177 の再発，claim location と abstract map，citation 改行，未使用 macro，残る copy/reference 2件を PR #59 で修正する．Introduction の Section VI 列挙，strict local ChkTeX，prose blacklist escape hatch，multiline Evidence parser は approval blocker としない | owner が PR #59 コメントで8項目を採用し，4項目を本 PR の必須範囲外と明示 |
| 2026-07-25 | **初回投稿は非匿名（通常の著者表示）で行う**: KSE 2026 AI4Math の Call for Papers および Microsoft CMT submission form には blind review の要求が明示されていない．conference が後日明示的な反対指示を出さない限り，通常の著者情報付き manuscript で投稿する | owner 判断．技術的には anonymity switch を残すが，非匿名を初期値とし，匿名出力は submission target としない |
