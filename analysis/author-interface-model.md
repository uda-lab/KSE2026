# 著者インターフェースの役割・権限モデルと passage 監査台帳（issue #60 Wave B / #66）

本書は，本プロジェクトの監督経路に登場する各アクターの**分離可能な機能**を，
**分割不能な最終権限**から切り分けて記述し，リポジトリ内の役割・権限・人間行為に
関する記述を一件ずつ監査した台帳を持つ．監査対象は `fe8fbeb`（Wave A merge 後の
`main`）時点のファイル内容であり，**行番号は全件その時点の実ファイルに対して再導出
した**（PR #59・#64 により旧調査の行番号は失効している）．

Wave A の伝送チャネル統計は `analysis/mediation-census-methodology.md`，
代表的な介入の trace は `analysis/author-interface-traces.md` にある．

## 0. 前提（本書で再議論しない事項）

scientific owner は 2026-07-25 に，**`t-uda` アカウントから発せられた判断は，文面を
ChatGPT が起草したか否かに関わらず owner 権威である**と定めた．
「最終判断は常に scientific owner が行う」（`provenance/ai-use.md:4`）および
「AI は著者にしない」（`AGENTS.md:24`）はいずれも真のまま維持される．

`performed_via_github_app` は**伝送チャネルの証拠であって，文面の起草者の証拠では
ない**（`analysis/mediation-census-methodology.md` の「下界であることの注記」）．
したがって本監査は connector 統計を owner 権威に対する反証として扱わない．
**既定の処置は「変更なし」**であり，`scientific owner` の語の書き換えは検討対象外と
する．なお本裁定そのものは本リポジトリ内に再導出可能な記録を持たない．その事実と
含意は §7 の限界に記す．

この前提そのものを `provenance/author-decisions.md` へ転記するか否かは owner の判断で
あり，本 Wave の範囲外である（Wave A も同じ状態で保留している．
`analysis/mediation-census-methodology.md` の「権威に関する立場」節）．

## 1. アクターと機能

### 不変条件

最終権限の所在は**ただ一つ**，人間の scientific owner であり，分割・委譲・共有
されない．他のアクターはいずれも**分離可能な機能**を担うにとどまり，その出力は
owner が採用するまで効力を持たない．

分離可能性の判定基準は次の通り: **別のアクターがその機能を実行しても，結果に対する
答責主体が変わらないなら，その機能は分離可能である．** 「決定」はこの基準を満たさ
ない．調査・統合・推奨・起草・伝送はいずれも満たす．

### A1 — 人間の scientific owner（GitHub アカウント `t-uda`）

- **機能**: theorem scope，claim 強度，contribution 構成，incident 採否，タイトル，
  レビュー方針，merge，公開に関する最終権限．
- **証拠（primary）**: `provenance/author-decisions.md` の 18 行（各行に日付と根拠）；
  `provenance/review-history.md:14-17`（owner 自身による原稿通読レビュー 3 件と，agent review と owner triage の複合行 1 件）；
  `evidence/session-index/90fa24bb-...` の分岐点記録（同 index が内容つきで特記する
  `AskUserQuestion` 方針分岐 3 件．同セッションの `AskUserQuestion` 呼び出し総数は
  8 件であり，3 件は特記されたものの数であって総数ではない）；`evidence/session-index/74aab39b-...`
  （safety classifier に阻まれた後 owner が端末で `gh repo create` を直接実行，EV-2076）；
  `evidence/session-index/de129390-...`（leray-hopf の PR に対する owner 3 巡レビュー．
  下記の限定を参照）；
  raw transcript の 2026-07-10T00:37:21Z・2026-07-18T06:30:55Z・07:40:10Z・07:49:42Z
  （EV-1669，EV-0247）．
- **推定に依存する部分**: 本 corpus で最も証拠の厚いアクターであるが，「なし」ではない．
  上記のうち **`leray-hopf#174` の 3 巡レビューは投稿チャネルが未確定**である．
  `gh api repos/uda-lab/leray-hopf/pulls/174/reviews` は `t-uda` の正式 Review 4 件
  （`CHANGES_REQUESTED` ×3，`APPROVED` ×1）を返すが，**Reviews endpoint は
  `performed_via_github_app` を露出しない**（当該フィールドは値が `null` なのではなく
  **キーごと応答に存在しない**．`gh api … | jq '[.[]|has("performed_via_github_app")]'`
  が全件 `false` を返すことで確認でき，`chatgpt-codex-connector[bot]` 自身の Review でも
  同じである）．
  さらに同レビュー系列の 1 巡目は 7 分 25 秒後に **connector 帰属のコメント**で訂正
  されている（`analysis/author-interface-traces.md` の T5）．したがってこの記録は
  「owner 権威によるレビューが 3 巡行われた」ことの primary 証拠ではあるが，
  **「人間が仲介なしに入力した」ことの証拠ではない**．
  *evidence_type: レビューの存在・回数・判定は primary（高）．チャネルは
  reconstructed 以前に**未確定**．*

### A2 — ChatGPT decision-support

- **機能**: リポジトリ状態の調査，作業単位への統合と優先度付け，推奨，issue／PR
  文面の起草．owner が発する判断のための準備を担う．
- **証拠（primary，artifact の存在について）**: leray-hopf の connector 経由
  issue／PR 32 件と KSE2026 の 6 件（`analysis/mediation-census-methodology.md`，
  `evidence/repository-snapshots/*/issues.json` から再導出可能）．単なる伝送では
  なく調査・統合を伴うことの内容証拠: `leray-hopf#145`（優先度階層付きのリリース
  umbrella），`leray-hopf#146`（owner へ "Required decision" を提示する P0 blocker），
  `leray-hopf#158`（INC-001 の検出 artifact となった `p = q = 1` の陽な反例構成）．
- **推定（evidence_type: reconstructed，confidence: 中）**: これらの**文面を
  ChatGPT が起草したこと**．`performed_via_github_app` は伝送のみを証明する．
  prompt，モデルバージョン，session id，編集履歴はいずれも復元できない．
  伝送の帰属自体は primary／confidence 高．
- **明示的に成立しないこと**: ChatGPT が何かを決定したこと．`leray-hopf#146` が
  owner に選択を求める形式を取っていることは，むしろ反対方向の積極証拠である．

### A3 — GitHub Connector（`chatgpt-codex-connector` GitHub App）

- **機能（本書が扱う範囲）**: `t-uda` 名義の投稿については伝送のみ．owner のアカウント
  identity の下でテキストをリポジトリへ運ぶ．
- **証拠（primary）**: `performed_via_github_app` フィールドそのもの；
  `evidence/repository-snapshots/*/EXPORT.json`．
- **重要な限定**: 同じ App slug は `t-uda` 名義の投稿だけに付くのではない．snapshot 上，
  `performed_via_github_app = chatgpt-codex-connector` を持つコメントは leray-hopf で
  106 件，KSE2026 で 12 件あり，そのうち **leray-hopf 69 件・KSE2026 7 件は
  `user_login = chatgpt-codex-connector[bot]`**，すなわち bot アカウント自身が
  生成したレビュー文である（`evidence/repository-snapshots/*/comments.json` から
  `user_login` と `performed_via_github_app` を交差集計すれば再現できる）．したがって
  「App slug は伝送のみを意味する」は **`t-uda` 名義の行に限った読み**であり，slug
  単独ではアクターの機能を決めない．A3 の「伝送のみ」は本書が扱う `t-uda` 名義の項目
  — コメント 37+5 件および issue／PR 作成 32+6 件 — についての限定であって，
  slug 一般についての主張ではない．
  *evidence_type: 交差集計は primary（高）．`t-uda` 名義の connector 投稿の文面を
  ChatGPT が起草したことは A2 と同じく reconstructed／confidence 中．*
  （`AGENTS.md:24` の通り，AI はいずれも著者としない．ここで述べているのは生成への
  関与の有無であって著者性の配分ではない．）

### A4 — Claude / Fable オーケストレータ

- **機能**: 限定作業の派遣，gate 判定，commit と merge の実行，人間との対話．
  Lean ソースを自ら編集しない．
- **証拠（primary）**: `evidence/session-index/` の各 role 記録；
  `analysis/workflow-evolution.md:20`；`paper/sections/03-agent-workflow.tex:32-33`．
- **権限に関する注記**: オーケストレータは merge の**実行**を持つが，外部規則
  （`paper/sections/03-agent-workflow.tex:36-40`）によって裁量ではなく機械的手続きに
  制約されている．`provenance/ai-use.md` には owner 判断前の merge を明示的に
  差し控えた記録が複数ある．

### A5 — 実装エージェント

- **機能**: 単一の Git worktree 内での実装と，PR による候補の返却．worktree 外への
  編集権限を持たない．
- **証拠（primary）**: `evidence/session-index/` の role 割当て；`INC-005` の経緯；
  `paper/sections/03-agent-workflow.tex:34-37, 89-93`．

### A6 — レビュアー（証拠上の地位が異なる 3 種）

- **エージェント adjudicator**: statement review，構造レビュー，宣言インベントリ比較．
  証拠: `evidence/incidents/INC-002.md:37`，`evidence/incidents/INC-004.md:10`．
- **外部自動レビュアー**（`chatgpt-codex-connector[bot]`，GitHub Copilot）: PR diff
  レビュー．証拠: `provenance/review-history.md:12`．
- **レビュアーとしての owner**: 原稿通読．証拠: `provenance/review-history.md:14-17`．
  これは A1 の**権限**機能とは別の**人間行為**であり，同一人物が担う点に注意する．

### 機能と権限の対応表

| 機能 | 担当しうるアクター | 分離可能か | 主な証拠 |
|---|---|---|---|
| 調査 | A2, A4, A5, A6 | 可 | `leray-hopf#1`，`leray-hopf#158` |
| 統合・優先度付け | A2, A4 | 可 | `leray-hopf#145` |
| 推奨 | A2, A6 | 可 | `leray-hopf#146`（"Required decision"） |
| 起草 | A2, A4, A5 | 可 | `provenance/ai-use.md` の執筆担当行 |
| 伝送 | A3；A1；および `t-uda` の PAT を用いうるプロセス（A4 と推定．*reconstructed／中* — census が明記するとおり，`null` チャネルの投稿主体は当該データからは確定しない） | 可 | `analysis/mediation-census-methodology.md` |
| 判断の台帳への転記 | A4 | 可 | `provenance/ai-use.md`（「文言・判断は owner…転記のみ agent」） |
| **最終判断** | **A1 のみ** | **不可** | `provenance/author-decisions.md:3-4` と全 18 行 |

### レビュアーが検証するであろう 2 点

1. **本監査を発注した `KSE2026#60` 自体が connector 経由で作成されている**
   （`evidence/repository-snapshots/KSE2026/issues.json` で確認可能）．前提の下では
   これも owner 権威であり，本監査の charter 自体が監査対象パターンの一例である．
   読者に発見させるより明示するほうが強い．
2. **アカウント identity だけでは判断を標識できない．** `KSE2026#59` 上の
   `t-uda` / `null` コメントは snapshot 上 **13 件**あり，うち
   `analysis/mediation-census-methodology.md` が comment id を挙げて一次確認手順を
   記録している 7 件は，**文面が定型のワークフロー通知**（review 依頼・gate 報告）で
   ある．*evidence_type: 文面の定型性は primary（高）．「harness が投稿した」という
   投稿主体の帰属は reconstructed／confidence 中 — 同 methodology が明記するとおり，
   本データ単独では誰または何が投稿したかを証明できない．* 本リポジトリは
   権限を**台帳に記録された判断**（`provenance/author-decisions.md`）に置くことで既に
   これを正しく扱っている．モデルもその通り述べる: 権限は台帳上の判断に付着し，
   アカウントはそれが発される経路である．逆ではない．

## 2. 台帳

対象は `paper/**/*.tex`，`claims/*.md`，`analysis/*.md`，`provenance/*.md`，
`notes/*.md`，`evidence/**/*.md`，`AGENTS.md`，`PLAN.md`，`README.md`，
`.github/workflows/README.md` の 48 ファイル．役割・権限・人間行為に関する実質的な
passage **282 件**を掲載する（下表の行数を機械計数した値）．

**掲載の網羅性について（限界の明示）**: 抽出は `owner` / `supervis` / `author` /
`reviewer` / `human` / `independent review` / 「人間」/「判断」/「権限」/「レビュア」/
「著者」等の語彙走査に基づく．**証明された網羅ではない**: 初稿は「168 件」と誤計数して
おり，独立レビューの各巡で `paper/sections/04-incidents.tex:113-114`，
`evidence/incidents/INC-004.md` の 2 行，`provenance/source-inventory.md` の 4 行，さらに
`analysis/workflow-evolution.md` 3 行・`analysis/incident-candidates.md` 3 行・
`analysis/session-coding-schema.md` 2 行・`notes/reviewer-questions.md` 2 行・
`notes/related-work.md` 1 行・`evidence/session-index/74aab39b` 2 行の抜けを指摘されて
追加している（計 20 行）．下のファイル単位の帰属表により**ファイルの取りこぼしは
解消した**が，各ファイル内での passage の取りこぼしが残っている可能性は依然として
排除できない（§7）．

**ファイル単位の帰属（48 ファイル全件）**: 台帳に行を持たないファイルは以下の **4 件**
だけであり，残る 44 ファイルはいずれも 1 行以上を持つ．「走査したが該当なし」と「走査
していない」を読者が区別できるよう，4 件の理由を明示する．

| 台帳に行を持たないファイル | 理由 |
|---|---|
| `paper/sections/02-formalization.tex` | 役割・権限・人間行為の passage が実際に 0 件．唯一の候補語 `manual build attestation` は CI の dispatch モード名であって人手ビルドではない（`claims/formalization-scope.md` の同語も同じ理由で不採録だが，同ファイルは別の passage で 1 行を持つ） |
| `analysis/project-timeline.md` | 唯一の候補語は `author date`（git のコミットメタデータ）であり，著者性とは無関係 |
| `analysis/unresolved-questions.md` | 候補語の出現が 0 件（走査で確認） |
| `evidence/README.md` | 候補語の出現が 0 件（走査で確認） |

**行としては採らなかった語（誤検出の列挙）**: `.github/workflows/README.md` の
`manual dispatch`（＝`workflow_dispatch`）；`notes/related-work.md`・
`provenance/source-inventory.md` の「著者名」（文献の著者欄）；
`analysis/session-coding-schema.md:16` と incident card の event code 語彙
（`WT-CONFLICT` の `ownership` 等）；`PLAN.md` のディレクトリ一覧と card テンプレート．
これらを含むファイルは，いずれも別の passage で台帳に行を持つ．

分類記号: **AUT** = 権限 · **ACT** = 人間行為 · **ROL** = 役割定義 ·
**ATR** = 帰属 · **DSC** = 開示規則

### `AGENTS.md`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| AGENTS.md:16 | 「主張には証拠識別子を付ける」 | DSC | 変更なし | チャネル中立の証拠規則 |
| AGENTS.md:21-22 | 「再構成情報と一次ログを混同しない…evidence type…と confidence を明記」 | DSC | 変更なし | 規則 5．本監査自身がこれに従う |
| AGENTS.md:23-24 | 「原稿・分析への AI の関与…を `provenance/ai-use.md` に追記する」 | DSC | **owner 判断** | **未解決項目 3**．選択肢は §4.3．**裁定の対象は開示 scope のみ**であり，同じ範囲に含まれる 24 行末尾の「AI は著者にしない」は §0 の通り不変で，裁定の対象ではない |
| AGENTS.md:24 | 「AI は著者にしない．」 | AUT/ATR | 変更なし | 前提がこれを真として再確認．著者性は人に帰属し，起草支援では移転しない |
| AGENTS.md:40-41 | 「branch protection は現状未設定であり，設定の可否は owner の判断」 | AUT | 変更なし | 設定判断の所在が正しい |
| AGENTS.md:52-53 | 「`claims/formalization-scope.md` の範囲を超える表現をしない」 | DSC | 変更なし | claim 強度規則 |
| AGENTS.md:61-63 | 「実装者と別の reviewer が全文を読み…両方を通す」 | ROL | 変更なし | レビュアー独立性規則．正確 |
| AGENTS.md:65 | 「## 役割分離（PLAN.md §8）」 | ROL | 変更なし | 見出し |
| AGENTS.md:67-68 | 「Lean reviewer は成功を強調する記述を先に読まず…独立に確認する」 | ROL | 変更なし | 役割定義．権限主張なし |
| AGENTS.md:68-69 | 「単一セッションで複数役割を兼ねる場合も，成果物…は役割ごとに分けて書く」 | ROL | 変更なし | 役割兼務を明示的に織り込んだ定式化であり，既に誠実 |

### `PLAN.md`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| PLAN.md:10 | 「複数の AI エージェント，オーケストレーション，役割分離，検証スキルを用いて」 | ROL | 変更なし | 範囲記述 |
| PLAN.md:119 | 「agent 間の責任境界または handoff の失敗」 | ROL | 変更なし | incident 分類項目 |
| PLAN.md:148,150 | 「論文の主題を確定するための判断基準」「…判断する」 | AUT | 変更なし | 判断は owner．§8 が割り当てる |
| PLAN.md:177 | 「scientific authority，issue-scoped work unit，statement review…」 | AUT/ROL | 変更なし | 第 3 節の構成方針．実際の Section III と一致 |
| PLAN.md:185 | 「人的監督の役割を同じ強度で明記する」 | DSC | 変更なし | 現 `05-discussion.tex:60` の限界記述で充足 |
| PLAN.md:192-193 | 「Scientific owner / final editor — 数学的主張，形式化範囲，論文上の最終判断を担当する．」 | AUT/ROL | **変更なし** | 分割不能な最終権限の正典的記述．起草チャネルの影響を受けない |
| PLAN.md:195-196 | 「Evidence curator — …raw log は変更しない．」 | ROL | 変更なし | 機能であって権限ではない |
| PLAN.md:198-199 | 「Incident analyst — …形式化成果への評価とは独立して作業する．」 | ROL | 変更なし | 独立性規則 |
| PLAN.md:201-202 | 「Lean and mathematics reviewer — …独立に確認する．」 | ROL | 変更なし | 機能 |
| PLAN.md:204-205 | 「Workflow reviewer — …ログで裏付けられているか確認する．」 | ROL | 変更なし | 機能．本監査はその一実施例 |
| PLAN.md:207-209 | 「Prose and format editor — …」 | ROL | 変更なし | 機能 |
| PLAN.md:211 | 「AI システムは著者とはせず，使用モデル，使用範囲，原稿生成またはレビューへの関与を…記録する．」 | AUT/DSC | **owner 判断** | **未解決項目 3**．`AGENTS.md:23-24` と対であり，§4.3 の scope 問題が同様に及ぶ．§4.3 が述べるとおり 3 passage は同一の裁定で整合させる必要があるため，本行を「変更なし」に置くことはできない |
| PLAN.md:230 | 「大幅改稿で contribution の階層が変わる場合は scientific owner の指示を記録し」 | AUT | 変更なし | 2026-07-24 に実行済（`provenance/author-decisions.md`） |
| PLAN.md:256 | 「内容と owner review が収束した後，6ページ上限へ圧縮する」 | AUT | 変更なし | owner review 下の順序付け |
| PLAN.md:276 | 「AI 利用記録と人間による最終判断の責任範囲が明示されている．」 | AUT/DSC | 変更なし | 完了条件．前提こそがこれを充足可能にする |

### `README.md` · `.github/workflows/README.md`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| README.md:17-18 | 「参照 commit の更新は Scientific owner の判断で行い，…に記録する．」 | AUT | 変更なし | 権限の所在が正しい |
| README.md:44 | 「`provenance/` — AI 利用記録，資料台帳，著者判断，レビュー履歴」 | ATR | 変更なし | ディレクトリ説明 |
| .github/workflows/README.md:56 | "repository owner's decision."（branch protection） | AUT | 変更なし | `AGENTS.md:41` と対応 |

### `paper/main.tex`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| main.tex:36 | `\author{\IEEEauthorblockN{Anonymous Author(s)}}` | ATR | **B3 へ回付** | B1 の処置ではないが重要: byline は**既に匿名**である．匿名化スイッチの既定値設計はこの事実に合わせる（§5 と `notes/deanonymization-checklist.md`） |
| main.tex:50 | "a workflow defined by the owner routed GitHub Issues through isolated Git worktrees and pull requests" | AUT/ATR | 変更なし | `provenance/author-decisions.md`（owner 提供 harness，Fable 以前）と一致 |
| main.tex:53-54 | "Four incidents show where these checks detected defects and where they did not." | ACT | 変更なし | 検出を**検査**に帰属させており人間に帰属させていない．意図的に非断定で正確 |

### `paper/sections/01-introduction.tex`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| 01:33-35 | "Human teams coordinated through blueprints in the Odd Order Theorem and the Liquid Tensor Experiment" | ROL | 変更なし | 先行研究について |
| 01:36-37 | "TauCeti uses human governance and a standing review rubric for a Lean library written by AI" | ROL | 変更なし | CLM-010 / `cite:tauceti2026` に裏付け |
| 01:38-40 | "examines one deep formalization under a single scientific owner and retains evidence about its incidents" | AUT | 変更なし | "single scientific owner" は正確であり，TauCeti のレビュアー体制との対比軸そのもの |
| 01:58-59 | "A harness defined by the owner that connects GitHub Issues, Git worktrees, pull requests, specialist agents…" | AUT/ATR | 変更なし | contribution 2．著者判断の記録と整合 |
| 01:60-61 | "Issue scope, review decisions, and merge authority are recorded outside agent sessions." | AUT/DSC | 変更なし | GitHub artifact で検証可能 |

### `paper/sections/03-agent-workflow.tex`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| 03:4-5 | "% Do not add a rendered figure … until the author supplies the artwork." | ROL | 変更なし | コメント．`notes/harness-figure-spec.md` と一致 |
| 03:12-14 | "This section describes the harness at the end of the project. Its controls were introduced incrementally" | DSC | 変更なし | 終状態であることの開示 |
| 03:23 | "\subsection{Owner authority and the GitHub workflow}" | AUT | 変更なし | 見出しは正確 |
| 03:25 | "The scientific owner retained authority over theorem scope." | **AUT** | **変更なし** | 論文中で最も権限主張の重い一文．前提が直接保護する．証拠は `provenance/author-decisions.md` の各行と `leray-hopf#146`（owner へ向けた "Required decision"） |
| 03:25-30 | "A GitHub Issue defined each unit of work… The statement card exposed the mathematical contract to review." | ROL | 変更なし | 機構であって権限ではない |
| 03:32-33 | "The main orchestrator assigned agents and checked their returned artifacts without editing Lean files itself." | ROL | 変更なし | primary: session-index 各件，`analysis/workflow-evolution.md:20` |
| 03:36-37 | "Direct pushes to the main branch were prohibited." | ROL | 変更なし | ワークフロー規則 |
| 03:37-40 | "A PR could merge only after … an independent reviewer had left an attributable result, and all review threads were resolved." | ROL/DSC | 変更なし | merge gate．反例は `04:46-49` で自己開示済 |
| 03:42-45 | "Issue scope, review decisions, and merge authority were recorded in repository and GitHub artifacts rather than retained only in an agent session." | AUT/DSC | 変更なし | CLM-009 |
| 03:44-45 | "When Fable~5 resumed orchestration through Google Cloud's Vertex AI on July~2--3, it continued the existing workflow from those artifacts." | ATR | 変更なし | owner 判断により意図的に格下げ済．現状のままで正確 |
| 03:49-50 | "Questions about mathematical meaning returned to the owner and statement card." | AUT/ROL | 変更なし | feedback split．権限と実行の境界そのもの |
| 03:51-54 | "the orchestrator first assigned a scout that could inspect repository assumptions but not edit them… Inspection roles had no edit authority." | ROL | 変更なし | primary: session-index の role 割当て |
| 03:59-62 | "An agent independent of the implementer checked whether the proposition matched the intended mathematics…" | ROL/ACT | 変更なし | 人間ではなく**エージェント**に帰属．INC-002 に照らし正確 |
| 03:63-64 | "Section~\ref{sec:incidents} contrasts a defect found by this procedure before merge with one that remained until release preparation." | ACT | 変更なし | 手続きへの帰属 |
| 03:74-78 | "Refactoring was checked against the preceding inventory of public declarations… therefore detected an unreferenced theorem omitted during refactoring." | ACT | 変更なし | 実行者はエージェント reviewer（INC-004）．**検査**への帰属で正しい |
| 03:81-84 | "A review request alone was insufficient. The PR needed the reviewer's identity and result." | ROL/DSC | 変更なし | 帰属可能性の規則 |
| 03:87-93 | "Each Git worktree had one active implementing owner… The orchestrator first checked the agent and its process state" | ROL | 変更なし | ここでの "owner" は**worktree の** owner（エージェント）．"implementing" により曖昧性は解消されている．用語衝突は Wave C の任意の微修正候補であり欠陥ではない |
| 03:95-100 | "Before starting one, the harness checked memory available… These requirements were placed in standing agent instructions" | ROL | 変更なし | INC-005 の恒常対策 |
| 03:105-108 | "Claim identifiers connect paper statements to those sources, while reconstructed intervals remain distinguishable from primary session evidence." | DSC | 変更なし | 規則 5 の遵守を読者へ明示 |
| 03:126-133 | "six sessions were selected … and coded independently of the formal result… They do not estimate rates" | ROL/DSC | 変更なし | 独立性 + 推論禁止のガード |

### `paper/sections/04-incidents.tex`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| 04:6-10 | "A successful Lean build establishes that the declarations … are well typed. It does not determine whether a theorem states the intended mathematics" | DSC | 変更なし | 枠組み |
| 04:12-15 | "The sample is neither random nor exhaustive, so the cases document observed failures … without estimating failure rates or causal effects." | DSC | 変更なし | 推論禁止のガード |
| 04:22 | "\emph{Case A. A false generalization detected before release.}" | ACT | 変更なし | 受動・アクター中立．該当する検出は `leray-hopf#158` によるもので，これは connector 経由である（次行および `analysis/author-interface-traces.md` の T4） |
| 04:32-33 | "During release preparation, a statement reviewer tested the boundary case \(p=q=1\)." | **ACT** | **変更なし（証拠注記）** | ここでの "statement reviewer" は `leray-hopf#158`，`t-uda` 名義・connector 経由．本文は "a statement reviewer" であり "the owner" とも "a human" とも書いていないため，人間検出を過剰主張していない．Wave C はこれ以上限定しないことを推奨 |
| 04:35-39 | "The problem was therefore the proposition, not a difficult proof… PR~\#162… PR~\#170 added a statement card and regression checks" | ACT | 変更なし | `leray-hopf#162`，`leray-hopf#170` に解決 |
| 04:46-49 | "Two days after PR~\#170 introduced the independent review rule, PR~\#177 merged a documentation correction with no requested or submitted review. The rule was not yet operationally reliable." | ACT/DSC | 変更なし | 自己に不利な開示であり誠実性を強める．`leray-hopf#177` 自体が connector 作成である点は `analysis/author-interface-traces.md` の T3 |
| 04:51-56 | "Two proof revisions had attempted this unrestricted statement before an independent reviewer identified the missing closure condition." | ACT | 変更なし | INC-002．adjudicator はエージェントであり本文も "an independent reviewer" と書く |
| 04:58-65 | "The reviewer tested inputs outside the intended subspace… They were not a certified counterexample." | ACT/DSC | 変更なし | 証拠強度の較正は適用済 |
| 04:69-71 | "Case B shows a defect caught by that review… The pair is informative but is not a controlled comparison." | ACT/DSC | 変更なし | "caught by that review" は人間ではなくレビューへの帰属 |
| 04:76-80 | "The refactored code built successfully, but one unreferenced public theorem had disappeared. No downstream dependency failed" | ACT | 変更なし | INC-004 |
| 04:82-86 | "A separate reviewer compared the public declaration inventory before and after the refactor." | ACT/ROL | 変更なし | 実行者はエージェント．中立な語 |
| 04:99-100 | "the orchestrator misclassified a slow agent as inactive and assigned a replacement to the same Git worktree" | ACT | 変更なし | INC-005，primary |
| 04:106-107 | "Monitoring had covered the visible Lean process rather than memory available to the entire container." | ACT/DSC | 変更なし | INC-005 |
| 04:107-108 | "An owner requested a status check when only 606\,MiB remained available." | **ACT** | **変更なし（§4.1(b)，Wave C 申し送り）** | raw transcript 2026-07-18T07:40:10.101Z の owner 発話は `status` の 1 語．逐語の主張は**要求**であって**検出**ではなく，証拠が支えるのはまさにその範囲．ただし PR #59 が `incidental` と「オーケストレータの監視によるものではない」の 2 限定を落としたため，監視不備の文の直後にこの文が来ることで**能動的な読みが可能になっている**（§4.1(b)）．本 PR では `paper/sections/04-incidents.tex` を変更せず，限定の復元を Wave C／owner へ申し送る |
| 04:108-110 | "Inspection of each process working directory identified the fourteen stale chains, and the Linux control group counter confirmed intervention by the out of memory (OOM) killer." | ACT | 変更なし | エージェント実行．検査への帰属 |
| 04:111-112 | "Because that counter was cumulative, it identifies the mechanism but not the number of kills in this incident." | DSC | 変更なし | INC-005 の confidence 注記を本文へ持ち込んでいる |
| 04:113-114 | "Ownership returned to the original agent, the duplicate stopped, and the build completed under a global lock." | **ROL/ACT** | 変更なし | 所有権の移動をエージェント間の事象として述べており，人間の行為に帰属させていない．初稿はこの行を落としていた（独立レビュー指摘．台帳の網羅性のため追加） |
| 04:117-121 | "An orchestrator must observe the complete process tree and available memory… The standing instructions now require cleanup" | ROL | 変更なし | 推奨 |
| 04:122-124 | "Monitoring available memory also detected a later peak caused by one legitimate build" | ACT | 変更なし | INC-005 |

### `paper/sections/05-discussion.tex`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| 05:6-8 | "recommendations for projects in which agents develop a substantial formalization under a mathematical owner. They do not establish the causal effectiveness of the harness." | AUT/DSC | 変更なし | 因果否定 + owner 枠組み |
| 05:11 | "\emph{Keep mathematical authority outside the implementation role.}" | AUT | 変更なし | 推奨自体が前提の肯定する権限分離である |
| 05:13-16 | "The scientific owner should approve a statement contract before implementation when the scope is delicate, and a reviewer who did not write the proof should test its hypotheses" | AUT/ROL | 変更なし | 規範的．owner 承認が分割不能な機能 |
| 05:20-26 | "Its mathematical value came from routing semantic findings to the owner and statement contract, while returning implementation findings to the worktree." | AUT/ROL | 変更なし | feedback split の推奨高度での再掲 |
| 05:28-32 | "A scout inspected repository assumptions without edit permission… These roles received only the authority needed for their task." | ROL/AUT | 変更なし | 最小権限原則 |
| 05:32-33 | "The declaration comparison in PR~\#120 found a missing theorem after both the build and a structural review had passed." | ACT | 変更なし | INC-004，`leray-hopf#120` |
| 05:36-42 | "Recording an incident in an agent's memory was insufficient because later agents and tools could change." | ROL | 変更なし | INC-005 の教訓 |
| 05:46-47 | "The study concerns one project under one scientific owner." | AUT/DSC | 変更なし | 一般化可能性の限界 |
| 05:47-50 | "their coded events cannot estimate failure prevalence or the effectiveness of a control… the observations do not identify causal effects." | DSC | 変更なし | 推論禁止 |
| 05:52-54 | "The session record has gaps… Reconstructed events are distinguished from primary session evidence and carry an explicit confidence assessment." | DSC | 変更なし | INC-003，規則 5 |
| 05:54-58 | "The models and proprietary tools also changed outside the project's control, which limits behavioral reproducibility." | DSC | 変更なし | 再現性の限界 |
| 05:60-61 | "The owner's supervision was part of the harness and cannot be separated from its outcome." | **AUT/DSC** | **変更なし（§4.2）** | PR #59 による "direct supervision" 文の置換後の文．**不可分性**を主張し**直接性**を主張していないため，仲介証拠が反証しうる主張を含まない．ここに仲介の限定を加えることこそが禁じられた drift にあたる |
| 05:61-65 | "Section~\ref{sec:formalization} bounds the mathematical result… The paper makes no claim about uniqueness or higher regularity." | DSC | 変更なし | scope ガード |
| 05:67-69 | "Redacted evidence excerpts, claim-to-evidence manifests, and scripts … are available in the paper repository." | DSC | **B3 へ回付** | 役割・権限の問題ではないが，`uda-lab/KSE2026` は private で bib entry も DOI もなく，読者にとって解決不能．owner 判断事項（§5.3） |

### `paper/sections/06-conclusion.tex`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| 06:8-9 | "The engineering contribution is a concrete division of responsibility. The scientific owner controls theorem scope." | AUT | 変更なし | `03:25` の結論高度での再掲．前提が保護する |
| 06:9-10 | "Issue scope, review decisions, and merge authority are preserved in repository and GitHub artifacts." | AUT/DSC | 変更なし | CLM-009 |
| 06:11-13 | "An orchestrator assigns bounded work… Specialist reviewers assess the statement, Lean assumptions, and public declarations." | ROL | 変更なし | 役割の要約 |
| 06:15-16 | "These observations come from one supervised project and require evaluation elsewhere." | DSC | 変更なし | 一般化の限界．"supervised" はチャネル中立 |

### `claims/`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| claims/limitations.md:19 | 「人間（scientific owner）の監督・介入が結果に不可分に寄与している．」 | AUT/DSC | 変更なし | `05:60` の台帳側の出所．チャネル中立で同じ理由 |
| claims/contribution-map.md:12 | 「scientific owner，repository-local `github-driven-workflow`…を接続した agent harness」 | AUT/ATR | 変更なし | contribution 2 の対応付け |
| claims/contribution-map.md:12（続） | 「数学的判断を owner へ，Lean/build 修正を実装 worktree へ戻す feedback split」 | AUT/ROL | 変更なし | feedback split |
| claims/contribution-map.md:16 | 「（owner 指示 2026-07-24，issue #57）．contribution は3点を維持する．」 | AUT | 変更なし | owner 指示の記録 |
| claims/formalization-scope.md:17 | 「参照 commit を更新する場合は `provenance/author-decisions.md` に記録し」 | AUT | 変更なし | 判断を owner 台帳へ回す |
| claims/paper-claims.md:19 | 「CLM-009 は content-first 改稿指示 2026-07-24 に基づく」 | AUT | 変更なし | owner 指示 |
| claims/paper-claims.md:56 | 「明示する（issue #42 項目 3，owner 判断…）」 | AUT | 変更なし | owner 裁定による条件付け |
| claims/paper-claims.md:99 | CLM-007 の本文（「03 節で述べる個別の歴史的事実…に裏付けられた範囲に限る」） | DSC | 変更なし | 限定 claim．本監査は 03 節がこの範囲内に留まることを確認した |
| claims/paper-claims.md:105 | 「2026-07-23 夜間 freeze 分 — 朝の owner 通読での追認対象」 | AUT | 変更なし | 追認の保留を誠実に記録している |
| claims/paper-claims.md:115 | （同上，CLM-008） | AUT | 変更なし | 同上 |
| claims/paper-claims.md:118 | CLM-009: 「scientific owner の権限下で repository-local `github-driven-workflow` が…」 | **AUT** | **変更なし** | frozen 済．Sections I/III/V/VI の権限アンカー |
| claims/paper-claims.md:129 | CLM-010: 「人間が統制する roadmap と常設 review rubric の下で AI が…」 | ROL | 変更なし | TauCeti について |

### `analysis/`

`analysis/mediation-census-methodology.md` は issue #60 Wave A，すなわち本 Wave と同一の
発注系列の成果物である．下表のうち同ファイルの各行の「変更なし」は**書式・帰属の点検の
結果**であって，内容の質に対する独立な評価ではない（`PLAN.md` §8．
`provenance/ai-use.md:49` の行と同じ扱い）．

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| workflow-evolution.md:3 | 「体制（役割分離，statement freeze，編集権限…）」 | ROL | 変更なし | 範囲 |
| workflow-evolution.md:20 | 「**orchestrator は Lean を直接編集しない**（全実装を delegate）」 | ROL | 変更なし | EV-2076 |
| workflow-evolution.md:23 | 「worktree/編集権限の設計的衝突回避」 | ROL | 変更なし | EV-2076 |
| workflow-evolution.md:24 | 「auto-mode safety classifier の hard-block を owner 手動実行で回避した摩擦」 | **ACT** | **変更なし** | 仲介のない人間行為として確定している稀少例．owner が端末で `gh repo create` を実行（EV-2076） |
| workflow-evolution.md:25 | 「**独立アジュディケータ（実装と別系統の agent）による PR 単位審査**を運用．初日に PR #20 の過強 statement…をマージ前検出」 | ROL/ACT | 変更なし | 検出をレビュー体制に帰属させており人間に帰属させていない（独立レビュー指摘により追加） |
| workflow-evolution.md:26 | 「**構造的審査と数値診断を含む adversarial review** が projection closure 仮定を欠く `ALLOW_SORRY` signature をマージ前に棄却」 | ACT | 変更なし | 同上．棄却の主体は review であってエージェント個体でも人間でもない（独立レビュー指摘により追加） |
| workflow-evolution.md:29 | 「5 role 構成へ拡張: coder×2・scout・reviewer×2」 | ROL | 変更なし | EV-1669 |
| workflow-evolution.md:30 | 「**宣言単位 byte-diff 悉皆レビュー**が公開定理の無断削除をマージ前検出し，以後 12 PR 全件の標準ゲートに」 | ACT | 変更なし | 検出は gate への帰属．INC-004 と整合（独立レビュー指摘により追加） |
| workflow-evolution.md:31 | 「レビュー見落とし 19 分停滞…を **user 指摘で発覚**」 | **ACT** | **変更なし（証拠の増強を推奨）** | 未解決項目 1a の分析層での生存分．raw transcript から逐語で裏付けた（§4.1）．Evidence セルに 2026-07-10T00:37:21Z / 00:43:22Z を追記する任意改善が可能 |
| workflow-evolution.md:32 | 「**preflight の軽量化**… | user の処理時間懸念 → 調査で過剰と判明」 | ACT | 変更なし | 人間発意・エージェント調査．**懸念**として書かれており所見として書かれていない点が正しい |
| workflow-evolution.md:34 | 「コンテナ資源管理の恒常規約…」 | ROL | 変更なし | INC-005 |
| workflow-evolution.md:36 | 「**manual full-build attestation による release 発行**」 | ACT | 変更なし | "manual" は CI の手動 dispatch を指し，人手ビルドではない．過剰主張なし |
| workflow-evolution.md:47 | 「いずれも人手介入で解消．」 | **ACT** | **変更なし（証拠注記）** | escalation 失敗 2 件をまとめた一文．**人間の行為として確定しているのは 2026-06-19 の safety-classifier hard-block（EV-2076．owner が端末で `gh repo create` を実行）のみ**である．2026-06-29 のレビューデーモン model 設定不備（EV-0925）については，修正主体が人間かオーケストレータかを本 corpus から確定できない．「いずれも」は前者の証拠強度を後者へ波及させうる（独立レビュー指摘） |
| workflow-evolution.md:51-54 | 「規律の多くは**事前設計ではなく incident 駆動**で導入されている」 | DSC | 変更なし | 事後合理化を防ぐ観察 |
| workflow-evolution.md:55-57 | 「FALSE-SUCCESS 0 件…因果の断定はしない」 | DSC | 変更なし | 因果否定 |
| incident-ranking.md:7 | 「**採否の確定は Phase 3 で owner が行う**．」 | AUT | 変更なし | 実行済 |
| incident-ranking.md:15 | 「**検出契機が owner の一言だった点は監視設計の教訓として一級**」 | ACT/AUT | 変更なし | INC-005 を正確に特徴づけている．owner の発話は**契機**であって検出ではない（§4.1(b) で逐語確認） |
| incident-ranking.md:36 | 「issue #33，owner 判断 2026-07-23」 | AUT | 変更なし | owner 裁定 |
| incident-ranking.md:50 | 「判断は Phase 3 で owner が…記録する．」 | AUT | 変更なし | 実行済 |
| incident-candidates.md:20 | 「公開定理…の無断削除を byte-diff 悉皆レビューがマージ前検出，wrapper 復元」 | ACT | 変更なし | 検出をレビュー機構へ帰属．INC-004（独立レビュー指摘により追加） |
| incident-candidates.md:21 | 「codex レビューの top-level コメント応答を監視が見落とし 19 分停滞…3 経路監視 `watch-pr-gates.sh` に刷新」 | ACT | 変更なし | 見落としを監視スクリプトに帰属．§4.1(a) の user 指摘とは別文（独立レビュー指摘により追加） |
| incident-candidates.md:26 | 「lean-prover が…誤主張 → Codex adversarial review が overstated/false と指摘 → 修正担当 prover が socket error で死亡し…」 | ROL/ACT | 変更なし | 名前付きエージェントと外部レビューへの帰属．人間行為の主張なし（独立レビュー指摘により追加） |
| incident-candidates.md:28 | 「owner がチャット内で明示承認した…owner が端末で直接実行して回避」 | ACT | 変更なし | `workflow-evolution.md:24` と同一事象．primary，直接 |
| session-coding-schema.md:24 | 「関与 model / tool，役割（architect / planner / coder / prover / reviewer / orchestrator）」 | ROL | 変更なし | `evidence/session-index/` の役割語彙の定義元．人間の役割を含まない（独立レビュー指摘により追加） |
| session-coding-schema.md:31 | 「符号化は incident analyst が行い，形式化成果の評価と独立に進める（PLAN.md §8）」 | ROL/DSC | 変更なし | `PLAN.md:198-199` と同趣旨の役割分離規定．重複だが独立に成立している（独立レビュー指摘により追加） |
| mediation-census-methodology.md:8-12 | 「著者性の signal としては非対称であり，census ではない」 | DSC | 変更なし | Wave A の注記．本書はこれを前提として引用しており，質の評価は行わない（同一発注系列のため独立でない） |
| mediation-census-methodology.md:26-29 | 「`user_login = t-uda`, `performed_via_github_app = chatgpt-codex-connector`」 | ATR | 変更なし | 生の API 組であり解釈を含まない |
| mediation-census-methodology.md:69-79 | 「「直接」という語は二通りに読め，本データはこの二通りに異なる答えを返す」 | DSC | **変更なし（項目 2 の主要入力）** | §4.2 が用いる語義の切り分けの出典．質の評価は行わない（同一発注系列のため独立でない）．該当語は既に本文から消えているため paper 側の処置は生じない |
| mediation-census-methodology.md:82-90 | 「comment id …「@codex please review this PR」…すべて `user.login = t-uda`，`performed_via_github_app = null`」 | ATR/DSC | 変更なし | 重要な含意: `t-uda` 名義のコメントの一部は harness 投稿の定型通知であり判断ではない．権限を**記録された判断**に置く現行設計を支持する．権限の希薄化ではない |
| mediation-census-methodology.md:115-124 | 「…owner 権威である」という前提の下で…「最終判断は常に scientific owner が行う」…は本集計と矛盾しない」 | AUT | 変更なし | Wave A が前提とその無矛盾性を既に記録している．Wave B は再議論しない．残る論点は前提を `provenance/author-decisions.md` の行にするか否かのみで，これは owner の判断 |
| billing-reconciliation.md:3 | 「owner 提供の Google Cloud 側記録」 | ACT/ATR | 変更なし | owner がデータを提供 |
| billing-reconciliation.md:48,78 | 「owner 向け導線」「issue #23 owner 判断」 | AUT | 変更なし | 保留中の owner 判断 |
| cost-attribution-methodology.md:37 | 「文言は owner が `provenance/author-decisions.md` に確定させる」 | AUT | 変更なし | 実行済 |
| cost-attribution-methodology.md:39 | 「contribution freeze で owner が判断する（それまで claim 化しない）」 | AUT | 変更なし | 実行済 |
| usage-metrics-methodology.md:48,63 | 「PoC 集計（2026-07-21 owner 報告）」「owner 報告（2026-07-22）」 | ATR | 変更なし | owner の回想を「報告」として型付けしており正しい |
| usage-metrics-methodology.md:79 | 「routing 判断は escrow 内 memory…」 | ROL | 変更なし | ツール層の routing |
| vps-snapshot-20260710-verification.md:3 | 「owner が復元・取得したバックアップ」 | ACT | 変更なし | owner のホスト操作 |
| vps-snapshot-20260710-verification.md:66 | 「owner 側での補完収集を推奨」 | AUT | 変更なし | owner への推奨 |

### `evidence/incidents/`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| INC-001.md:10 | 「2026-07-16，公開前の soundness postmortem（issue #158）における独立レビューで，`p = q = 1` の陽な反例が構成され偽と確定した」 | **ACT** | **変更なし（証拠注記）** | `leray-hopf#158` は `t-uda` 名義・connector 経由．card は「独立レビュー」と書き人間の打鍵を主張していないため正確．チャネルを Notes に記録する追記が任意で有効 |
| INC-001.md:11 | 「PR #177…（requested reviewer 0・submitted review 0 でマージ）で…同種の handoff-failure を再演し，issue #178…で残存する誤記を検出・修正」 | ACT/ROL | 変更なし | `leray-hopf#177`・`leray-hopf#178` とも connector 作成．corpus 中で最も明瞭な drift 事例であり `analysis/author-interface-traces.md` の T3 に対応 |
| INC-001.md:110-112 | 「独立 reviewer による再レビューと reviewed commit SHA の記録を完了して」 | ROL | 変更なし | 収束記録 |
| INC-002.md:6 | 「独立アジュディケータが…構造的に判定し…著者は先行 2 revision がいずれも unsound だったことを自認した」 | ACT/ATR | 変更なし | 注意: ここでの「著者」は **lean-prover 役のエージェント**（INC-002.md:35 で明示的に曖昧性解消済）．人間著者との用語衝突は括弧書きで封じ込められている |
| INC-002.md:10 | 「独立アジュディケータによる adversarial review が…指摘した」 | ACT | 変更なし | エージェントへの帰属 |
| INC-002.md:16 | 「著者自身の「先行 2 revision が unsound だった」という認識は session-index 記録に基づく」 | ATR/DSC | 変更なし | 証拠型付けあり |
| INC-002.md:35 | 「著者（lean-prover 役のエージェント）は，この命題を…2 度試み」 | ATR | 変更なし | 明示的に曖昧性解消済 |
| INC-002.md:37 | 「独立アジュディケータ（adversarial review 役のエージェント）が PR #27 をマージ前レビューし」 | ROL/ACT | 変更なし | 完全に特定されている |
| INC-003.md:12 | 「全 host で `cleanupPeriodDays = 9999`（2026-07-21 owner 設定）」 | ACT | 変更なし | owner の設定行為 |
| INC-003.md:42 | 「owner が全 host の…」 | ACT | 変更なし | 同上 |
| INC-004.md:6 | 「レビュアー `prrev-111-1` が宣言単位の byte-diff 照合を実施したところ…検出した」 | ACT | 変更なし | 名前付きエージェント |
| INC-004.md:10 | 「レビュアー `prrev-111-1` が，動的スポーンした 8 体の deep-verify subagent を用いて…検出した」 | ACT | 変更なし | エージェント帰属，primary |
| INC-004.md:11 | 「実装コーダー `glue-111` が…復元し再コミット…レビュアーが再検証を実施し…PASS 判定，PR #120 をマージした」 | ROL/ACT | 変更なし | 名前付きエージェントと役割への帰属．人間行為の主張なし（独立レビュー指摘により追加） |
| INC-004.md:37 | 「modularity-reviewer が import 構造・循環・thin instantiation の健全性を検査し PASS 判定を出した」 | ROL/ACT | 変更なし | 同上．検査範囲の限界も併記されており正確（独立レビュー指摘により追加） |
| INC-005.md:10 | 「オーケストレータの自発的監視ではなく，**owner の "status" 一言（07:40Z）を契機に** `free -h` が実行され…発覚した」 | **ACT** | **変更なし — 逐語確認済** | raw transcript 2026-07-18T07:40:10.101Z の user メッセージ本文は正確に `status`．card は owner が**契機**を与え，検出はオーケストレータが行ったと正しく述べている |
| INC-005.md:12 | 「owner の再犯指摘を受け **4 層**に恒常対策を記録」 | ACT | 変更なし | 逐語確認済 |
| INC-005.md:15 | 「Evidence type: primary … ／一部 secondary（…owner 報告…によるもの）」 | DSC | 変更なし | 規則 5 遵守 |
| INC-005.md:27 | 「進捗監視は誤診断（~850MB で安全と判定）を挟み，発覚の契機は owner の一言だった」 | ACT | 変更なし | 同上 |
| INC-005.md:48 | 「5. **07:40Z（発覚）:** owner の "status" 一言を契機に `free -h` が実行され」 | ACT | 変更なし | 同上 |
| INC-005.md:62 | 「9. …owner が「同種の放置 OOM は数回目」と再犯を指摘．」 | ACT | 変更なし | 逐語確認済 |
| INC-005.md:45-47（経緯 step 4） | 「06:28–06:31Z（誤診断）: オーケストレータは…RSS ~850MB のみを見て…報告した」 | ACT | **変更要（記載漏れ）** | **新規所見．** card は同 window のオーケストレータ誤診断のみを記録し，その前後の owner 発話 2 件を落としている．(i) 06:28:39.808Z の owner 問い合わせがこの status 確認の**契機**であり，オーケストレータの自発的監視ではない．(ii) 06:30:55.545Z に owner が `.lake` cache 共有方針の逸脱（trigger 原因 (b)）を指摘し，**同じ発話の中で明示的に不問としている**（「まぁ良いですよ．時間はあるので．」）．逐語確認済（§4.1(b)）．経緯へ primary 証拠として追加することを推奨するが，**「人間による検出」として記録してはならない**（観測と，行動しない判断の対）．**適用は Wave C** |
| TEMPLATE.md:10 | "How the problem was detected:" | DSC | 変更なし | テンプレート項目 |

### `evidence/session-index/`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| 668d1710:8 / a400c3c0:8 | 「**役割**: なし（実質的な作業セッションではない）」 | ROL | 変更なし | 空役割の記録 |
| 74aab39b:8 | 「## 関与 model・tool・役割」 | ROL | 変更なし | 見出し |
| 74aab39b:12 | 「役割は orchestrator（…**ユーザーとの対話**）で一貫」 | ROL | 変更なし | ユーザー対話をオーケストレータ機能として明示 |
| 74aab39b:20 | 「Codex adversarial review (xhigh) が上記 unsoundness 主張を overstated/false と指摘」 | ACT/ATR | 変更なし | 外部レビューへの帰属．`7e6156bf:18` と同型（独立レビュー指摘により追加） |
| 74aab39b:28 | 「メインセッション自身が，PR ワークフロー導入に向けた**権限設定待ち**の最中に socket エラーで異常終了」 | ROL | 変更なし | ここでの「権限」はリポジトリ設定であって著者権限ではない（独立レビュー指摘により追加） |
| 74aab39b:26 | 「owner がチャット内で明示承認したにもかかわらず，auto-mode safety classifier が…hard-block．結局 owner が端末で直接 `gh repo create` を実行」 | ACT/AUT | 変更なし | owner の承認が**ツール**に阻まれ，その後直接行使された．権限が owner にあり，チャネルは付随的であることの明快な実例 |
| 74aab39b:37 | 「インフラ：2026-06-19 に local-only 運用から GitHub…へ移行」 | ROL | 変更なし | 時系列 |
| 7e6156bf:6 | 「オーケストレーター本体は `claude-fable-5`…opus 出動は 0 件」 | ROL | 変更なし | model／role 記録 |
| 7e6156bf:7 | 「オーケストレーター本体＝orchestrator／architect…`map-plancherel`＝scout（read-only 事前調査）…`prrev-111-1`＝reviewer」 | ROL | 変更なし | 役割割当ての全体像．`03:51-54` の出所 |
| 7e6156bf:15 | 「レビューは早期に完了していたが約19分間マージが進まず，**ユーザーの指摘で発覚**」 | **ACT** | **変更なし — 逐語確認済** | §4.1．raw transcript 2026-07-10T00:37:21.889Z + 00:43:22.204Z |
| 7e6156bf:16 | 「監視スクリプトを…3経路を全て見る `watch-pr-gates.sh` に刷新」 | ACT | 変更なし | 回復 |
| 7e6156bf:18 | 「codex に再依頼（`@codex please review`）し20分以内に応答を得て解消」 | ACT | 変更なし | harness による review 依頼 |
| 90fa24bb:8 | 「**役割**: orchestrator（自らは Lean を直接編集せず…統括）」 | ROL | 変更なし | 役割記録 |
| 90fa24bb:16 | 「独立アジュディケータが PR #27 の…signature に projection closure 仮定が欠けると構造的に判定」 | ACT | 変更なし | INC-002 の出所 |
| 90fa24bb:26 | 「補足で確認した分岐点（AskUserQuestion，方針判断であり単独では code 化しない）：…夜間自律バーンの起動可否，…終了判断，…押し切りか撤退かの判断」 | **AUT** | **変更なし — 強い支持** | エージェントが**方針**決定を人間へエスカレーションした記録が 3 点．決定権限が人間にあったことのセッション内・非仲介の primary 証拠 |
| 90fa24bb:32 | 「**わずか数分の再検証**（07:58–07:59）で…計画全体を破棄」 | ACT | 変更なし | エージェントの自己修正 |
| de129390:8 | 「**役割**: orchestrator（…複数の named agent…を派遣・監督）」 | ROL | 変更なし | ここでの「監督」はオーケストレータによる**エージェント**監督であり owner 監督ではない．内部文書内で衝突の危険はない |
| de129390:17 | 「owner の "status" 一言を契機にオーケストレータが `free -h` を実行し…**owner からの検出ではなく，owner の一言が契機になった点が特徴**」 | **ACT** | **変更なし — corpus 中で最も精密な定式化** | owner による検出を明示的に否定しつつ owner による契機を肯定する．raw log の示す通り．Wave C はこの行を正典的表現として保存すべき |
| de129390:23 | 「owner から「同種の放置 OOM は数回目」と指摘（お叱り）を受け」 | ACT | 変更なし | 逐語確認済 |
| de129390:30 | 「#174（…owner 3巡レビュー対応後）」 | ACT | **変更なし（証拠注記）** | レビューの存在・回数・判定は primary（`pulls/174/reviews` に `t-uda` の正式 Review 4 件）．ただし **Reviews endpoint は `performed_via_github_app` をキーごと返さない**ため投稿チャネルは未確定であり，同系列の 1 巡目は connector 帰属コメントで訂正されている（T5）．本行を「非仲介の人間入力」の証拠として用いてはならない |
| de129390:37 | 「**confidence**: 中〜高…152 件のサブエージェント transcript…は…要約経由でのみ参照しており，個別ファイルは未読」 | DSC | 変更なし | 規則 5 遵守 |

### `notes/`

| file:line | quote | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| harness-figure-spec.md:3 | "The scientific owner will draw and approve the final artwork." | AUT/ACT | 変更なし | 著者判断の記録と一致 |
| harness-figure-spec.md:9-12 | "a division of authority: the scientific owner decides mathematical scope, an orchestrator coordinates bounded work, specialist agents inspect different artifacts" | **AUT/ROL** | **変更なし** | 図の主題．`03:25` + `06:8-9` と同一 |
| harness-figure-spec.md:11-12 | "repository and GitHub artifacts preserve Issue scope, review decisions, and merge authority outside agent sessions" | AUT | 変更なし | CLM-009 |
| harness-figure-spec.md:23 | "1. Scientific owner"（lifecycle stage 1） | AUT/ROL | 変更なし | owner が lifecycle の起点．正しい |
| harness-figure-spec.md:32-37 | "Place the owner defined repository skill `github-driven-workflow` around stages 2--7… a persistent governance layer outside any one agent session." | AUT/ATR | 変更なし | owner 提供・Fable 以前という著者判断を反映 |
| harness-figure-spec.md:47-50 | "Semantic findings return to the scientific owner and statement card… because it distinguishes scientific authority from orchestration." | AUT/ROL | 変更なし | 権限と実行の境界の可視化 |
| harness-figure-spec.md:58-59 | "one active owner per Git worktree" | ROL | 変更なし | worktree の owner＝エージェント．`03:89` と同じ無害な衝突 |
| harness-figure-spec.md:70-71 | "Distinguish semantic feedback to the owner and statement card from technical feedback to the Git worktree." | AUT/ROL | 変更なし | 作図制約 |
| harness-figure-spec.md:79-85 | "Under the scientific owner's authority, an orchestrator routes each GitHub Issue…" | AUT | 変更なし | caption 草案 |
| harness-figure-spec.md:98-100 | "Owner TODO: draw and approve the final vector artwork. / Owner TODO: confirm the IEEE placement, caption…" | AUT/ACT | 変更なし | 未了の owner タスク |
| paper-outline.md:4 | 「owner review が収束した後に Phase 5.5 で6ページへ圧縮する」 | AUT | 変更なし | 著者判断に対応 |
| paper-outline.md:11 | 「owner 権限，session 外に project state を残す `github-driven-workflow`…Fable の再開は補助的な観測例として一度だけ記す」 | AUT/ATR | 変更なし | 実際の Section III と著者判断に一致 |
| paper-outline.md:31 | 「### ビルド環境の方針（owner 指示 2026-07-20）」 | AUT | 変更なし | 著者判断に対応 |
| related-work.md:8 | 「## 1. TauCeti（owner 指定の比較対象）」 | AUT | 変更なし | 比較対象は owner が指定 |
| related-work.md:13 | 「人間は roadmap（`TauCetiRoadmap`…）」 | ROL | 変更なし | TauCeti について |
| related-work.md:27 | 「2 human steering … claim レベル（**単一 owner が「何を主張してよいか」を統制**…）」 | AUT | 変更なし | owner 権限を contribution の差分たらしめている比較軸．希薄化は related work の論証を損なう |
| related-work.md:28 | 「3 役割分離 … 実装 agent と独立 adversarial reviewer の分離を incident 対で事後実証」 | ROL/DSC | 変更なし | 「事後実証」という誠実な枠付け |
| related-work.md:45 | 「単一著者が単一 AI を指揮する形態で，multi-agent 統治・証跡・incident 報告は無い」 | ROL/ATR | 変更なし | 先行研究の体制記述．本プロジェクトの著者性についての主張ではない（独立レビュー指摘により追加） |
| related-work.md:61-64 | 「いずれも人間チーム + blueprint．本プロジェクトは**単一 owner が agent 著述の実装と独立 agent 審査を統治し**」 | AUT | 変更なし | 同上 |
| reviewer-questions.md:8 | 「AI エージェントの寄与は測定されているのか？ | 因果測定はない．対照群なしのケーススタディであると明言」 | DSC | 変更なし | 因果推論の禁止を想定質問の回答方針として明記．`04:12-15`・`05:47-50` と同一方向（独立レビュー指摘により追加） |
| reviewer-questions.md:12 | 「kernel-only の確認は誰がどう行ったのか？ | release cone check + build attestation の仕組みを引用」 | ACT/ATR | 変更なし | 「誰が」を機構へ回付する回答方針であり，人間行為を過剰主張していない（独立レビュー指摘により追加） |
| title-and-abstract.md:8 | 「最終判断は issue #57 の PR review で owner が行う．」 | AUT | 変更なし | 著者判断・レビュー履歴で実行済 |
| title-and-abstract.md:18 | 「主題判断（PLAN.md §6）とタイトルは整合させる．」 | AUT | 変更なし | 整合規則 |

### `provenance/ai-use.md`

| file:line | quote（要約） | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| ai-use.md:3 | 「本リポジトリの**成果物**への AI システムの関与を継続的に記録する」 | DSC | **owner 判断** | **未解決項目 3**: `AGENTS.md:23` の「原稿・分析への関与」より広い．**両者の scope は同一ではない**（§4.3）．3 passage 同時の裁定が要るため「変更なし」には置かない |
| ai-use.md:4 | 「AI は著者としない．**最終判断は常に scientific owner が行う．**」 | **AUT** | **変更なし** | 権限に関する正典文．前提が逐語で肯定する |
| ai-use.md:8, 13 | 「人間による確認」（列見出し ×2） | DSC | 変更なし | 確認列 |
| ai-use.md:15 | 「Phase 0 scaffold…オーナー承認は PR フローの授権による」 | AUT | 変更なし | ワークフローによる授権であることを明示 |
| ai-use.md:16 | 「PR #1 の内部レビュー…所見は Fable 5 が修正として適用」 | ATR | 変更なし | エージェント間 |
| ai-use.md:17 | 「Phase 1 vps ログ収集…Copilot レビュー + merge gate 検査」 | ATR | 変更なし | 定型 |
| ai-use.md:18 | 「local-main 収集分（**owner が収集・転送**）…判断は owner」 | ACT/AUT | 変更なし | owner のホスト操作 |
| ai-use.md:19 | 「local-secondary…（owner 側 Claude Code session が収集，**owner が転送**）」 | ACT | 変更なし | エージェントが収集し owner が転送，と正確に型付け |
| ai-use.md:20 | 「スナップショット復元・バックアップ取得は owner」 | ACT | 変更なし | owner 行為 |
| ai-use.md:21 | 「CLM の freeze 判断は owner（Phase 3）」 | AUT | 変更なし | 実行済 |
| ai-use.md:22 | 「incident の card 化・論文採否は owner（Phase 3）」 | AUT | 変更なし | 実行済 |
| ai-use.md:23 | 「（owner がホスト側転送…）…レビュワー切替は owner 指示 2026-07-22」 | ACT/AUT | 変更なし | owner 行為 + owner 裁定 |
| ai-use.md:24 | 「期間の事実関係は owner 報告」 | ATR | 変更なし | 回想として型付け |
| ai-use.md:25 | 「owner 提供 Google Cloud ログ…解釈確認は owner」 | ACT/AUT | 変更なし | owner 提供データ + owner 解釈 |
| ai-use.md:26 | 「SKU データ・monitoring export の提供は owner」 | ACT | 変更なし | owner 行為 |
| ai-use.md:27 | 「owner 確定の acknowledgment 文言…**文言・判断は owner（issue #23 コメント），転記のみ agent**」 | **AUT/ATR** | **変更なし — 模範例** | **判断**（owner）と**転記**（agent）の分離として既存で最も明快．`KSE2026#23` は connector 作成だが，前提の下でなお owner 権威．本行はアクターモデルが一般化すべき雛形 |
| ai-use.md:28 | 「card 本文は一次資料からの再構成で，採否の確定は Phase 3 で owner」 | AUT/DSC | 変更なし | 再構成であることを明記 |
| ai-use.md:29 | 「card 化判断と重要性評価の方向づけは owner（issue #33 本文引用）」 | AUT | 変更なし | owner の方向づけ |
| ai-use.md:30 | 「リストは owner 承認済，freeze は issue #35 回答後…freeze 判断は owner」 | AUT | 変更なし | 実行済 |
| ai-use.md:31 | 「formalization-scope.md の出典訂正…」 | ATR | 変更なし | エージェント所見．権限主張なし |
| ai-use.md:32 | 「workflow-evolution.md の記入…未符号化期間は下界主義で不記載」 | DSC | 変更なし | 下界主義 |
| ai-use.md:33 | 「…確認は **owner 立会いの計画セッション**で実施…校正方針は owner 指定」 | ACT/AUT | 変更なし | owner 立会いの検証 |
| ai-use.md:34 | 「repo hygiene…」 | ATR | 変更なし | 定型 |
| ai-use.md:35 | 「TauCeti（**owner 提供 URL**）…一次資料の指定は owner」 | AUT | 変更なし | 比較対象の指定は owner |
| ai-use.md:36 | 「**全判断は owner**…転記と freeze 作業のみ agent．」 | **AUT/ATR** | **変更なし — 模範例** | 判断／転記の分離の 2 例目 |
| ai-use.md:37 | 「執筆は subagent，数値校正・文言調整はオーケストレータ」 | ATR | 変更なし | 起草の帰属 |
| ai-use.md:38 | 「執筆は subagent…検収・投入はオーケストレータ」 | ATR | 変更なし | 同上 |
| ai-use.md:39 | 「sections 01/05/06 + abstract の draft 投入…」 | ATR | 変更なし | 同上 |
| ai-use.md:40 | 「issue #57 の content-first 全面改稿…**scientific owner の最終判断は PR 上で待機し，merge は実施しない**」 | **AUT** | **変更なし** | merge を owner へ明示的に留保 |
| ai-use.md:41 | 「PR #59 の自動独立差分レビュー…**scientific owner の判断前に merge は行わない**」 | AUT | 変更なし | 同上 |
| ai-use.md:42 | 「owner review への移行後は追加の GitHub 自動レビューを依頼しない」 | AUT | 変更なし | 著者判断に対応 |
| ai-use.md:43 | 「owner review 指摘の実装…時系列を **owner 訂正に従って**分離」 | AUT/ACT | 変更なし | owner が実質的な史実訂正を行った |
| ai-use.md:44 | 「owner follow-up に従い，Fable 交代を…contribution とする記述を除去…**owner が論旨と差し替え方針を確認**」 | AUT | 変更なし | owner がエージェント提案の contribution 枠組みを棄却．強い権限証拠 |
| ai-use.md:45 | 「PR #59 の **scientific owner review 7 項目**を反映…owner review を根拠に修正」 | AUT | 変更なし | 項目化された owner レビュー |
| ai-use.md:46 | 「**owner がGitHubコメントで採否を指定**．本 PR 対象外の4項目は変更せず」 | AUT | 変更なし | owner がエージェント所見を項目別に採否判定 |
| ai-use.md:47 | 「Codex からの引き継ぎ差分を **owner の8項目に対して逐一照合**…merge は行わない」 | AUT | 変更なし | 同上 |
| ai-use.md:48 | 「issue #61 の CI 実行頻度削減…採否を判断」 | ROL | 変更なし | 実装記録 |
| ai-use.md:49 | 「独立レビュー経路は owner 指示…により…read-only Claude subagent 2 名に切替．**指示の根拠として owner が挙げた…は本 agent が独立検証した事実ではなく，むしろ矛盾する一次証拠がある**」 | **AUT/DSC** | 変更なし | owner 指示とその根拠の証拠状態を分けて記録している．**評価上の注記**: 本行は issue #60 の Wave A，すなわち本 Wave と同一の発注系列の記録であり，本書の著者による評価は独立ではない．「変更なし」の判定は書式・帰属の点検にとどめ，質の評価は行わない（`PLAN.md` §8）．本行は owner 確認待ちの項目を含む |

### `provenance/author-decisions.md`

| file:line | quote（要約） | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| author-decisions.md:1 | 「# Author decisions — 著者判断の記録」 | AUT | 変更なし | 表題 |
| author-decisions.md:3-4 | 「**scientific owner による確定判断のみを記録する**（提案・候補は notes/ へ）．各判断には日付と根拠を付ける．」 | **AUT/DSC** | **変更なし** | 本リポジトリの権限台帳の契約．**チャネルではなく判断を記録する**器であり，前提に対して正しい道具 |
| author-decisions.md:8 | 「参照対象を leray-hopf v0.1.0-rc1 に暫定固定」 | AUT | 変更なし | owner 判断 |
| author-decisions.md:9 | 「ビルド主系を TeX Live pdflatex + latexmk に決定 | owner 指示」 | AUT | 変更なし | 同上 |
| author-decisions.md:10 | 「研究費 acknowledgment 文言を確定 | owner 指示（issue #23 コメント）」 | AUT | 変更なし | `KSE2026#23` は connector 作成．前提により owner 権威．**`paper/` に未挿入であり B3 の対象**（§5.1 で `\else` 分岐へ配置．既定の `\anonymoustrue` では依然として描画されないため，「first-page footnote に記載」の完全な履行はスイッチを倒す判断待ちである） |
| author-decisions.md:11 | 「reseller 公称レート照会は保留 | owner 判断」 | AUT | 変更なし | 同上 |
| author-decisions.md:12 | 「**論文主題を B + C 統合に確定** | owner GO」 | AUT | 変更なし | 同上 |
| author-decisions.md:13 | 「**contribution 3 点の大枠を確定** | owner GO」 | AUT | 変更なし | 同上 |
| author-decisions.md:14 | 「**incident 採否を確定** | owner GO」 | AUT | 変更なし | 同上 |
| author-decisions.md:15 | 「**タイトルを確定** | owner（issue #35 コメント…→ チャットで合体形を確定）」 | AUT | 変更なし | 混成チャネルだがいずれも owner |
| author-decisions.md:16 | 「**claim freeze の前提条件**…freeze 作業自体は夜間自律実行を owner 承認」 | AUT | 変更なし | **実行**の明示的委譲であって判断の委譲ではない |
| author-decisions.md:17 | 「**FX 下界の扱い** | owner（チャット判断 2026-07-23）」 | AUT | 変更なし | チャネルはチャット，主体は owner |
| author-decisions.md:18 | 「**content-first 全面改稿** | owner の改稿指示．…事後改訂する権限を明示的に付与」 | AUT | 変更なし | 裁量範囲の付与であり権限の保持は変わらない |
| author-decisions.md:19 | 「**タイトル確定を再検討対象へ戻す**…最終確定は owner review まで保留」 | AUT | 変更なし | 同上 |
| author-decisions.md:20 | 「**ページ制約の段階分離** | owner の改稿指示」 | AUT | 変更なし | 同上 |
| author-decisions.md:21 | 「**主図を別 issue #58 で owner が清書** | …最終 artwork の採否と清書は owner」 | AUT/ACT | 変更なし | owner による将来の行為 |
| author-decisions.md:22 | 「**owner review へ移行し，追加の Codex/Copilot 自動レビューを停止** | owner の本文レビュー」 | AUT | 変更なし | owner が原稿を読みレビュー方針を裁定 |
| author-decisions.md:23 | 「**`github-driven-workflow` は Fable 登場以前からの owner 提供 harness** | owner の時系列・権限関係の訂正」 | **AUT/ATR** | **変更なし** | エージェントが持ち込んだ由来の誤りを owner が訂正した記録．権威の物語をエージェントが設定したという見方への直接の反証 |
| author-decisions.md:24 | 「**Fable の交代を harness contribution として強調しない** | owner review で…新規性を棄却」 | AUT | 変更なし | owner がエージェント提案の contribution を棄却 |
| author-decisions.md:25 | 「**追加 agent review の対応範囲** | owner が PR #59 コメントで8項目を採用し，4項目を…範囲外と明示」 | AUT | 変更なし | owner がエージェント所見を項目別に採否判定 |

### `provenance/review-history.md`

| file:line | quote（要約） | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| review-history.md:3 | 「原稿・claims への内部レビュー…の実施記録」 | ROL | 変更なし | 範囲 |
| review-history.md:6 | 「実施者（**人間 / AI+人間確認**）」（列見出し） | ROL/DSC | 変更なし | 人間と AI+確認を明示的に区別する列．良い器 |
| review-history.md:8 | 「Claude Opus（サブエージェント）＋**人間確認待ち**」 | DSC | 変更なし | 保留状態を誠実に記録．2026-07-20 以来未了であり，owner が閉じたいなら任意で対応 |
| review-history.md:9-11 | 「`prose-final-review` / `claim-final-review` / `audience-harness-review`（Codex subagent，**執筆担当と分離**）」 | ROL | 変更なし | レビュアーごとに独立性を記録 |
| review-history.md:12 | 「GitHub Copilot PR reviewer + OpenAI Codex review」 | ATR | 変更なし | 外部自動レビュー |
| review-history.md:13 | 「prose-lint remediation review（read-only）」 | ROL | 変更なし | 定型 |
| review-history.md:14 | 「scientific owner prose / harness review | …| **scientific owner** | …時系列混同を指摘」 | **AUT/ACT** | **変更なし** | owner による原稿通読レビュー．人間行為，primary |
| review-history.md:15 | 「scientific owner follow-up review | …| scientific owner | …非自明でないと指摘」 | AUT/ACT | 変更なし | 同上 |
| review-history.md:16 | 「scientific owner latest-head review | …| scientific owner | …別監査事項は issue #60 へ分離」 | AUT/ACT | 変更なし | 同上．issue #60 を生んだ行為そのもの |
| review-history.md:17 | 「additional agent review and owner triage | …| Claude Code (Opus 5) review + **scientific owner**」 | AUT | 変更なし | 複合行として正しい |
| review-history.md:20-28 | Phase 5 チェックリスト（全 `[x]`） | DSC | 変更なし | 自己監査記録 |

### `provenance/source-inventory.md`

初稿はこのファイルを「文献の著者欄のみ」として除外していたが，owner の行為・判断を
述べる passage が 4 件ある（独立レビュー指摘により追加）．

| file:line | quote（要約） | 分類 | 処置 | 理由 |
|---|---|---|---|---|
| source-inventory.md:10 | 「追補: …33 ファイル中…19 件登録．**owner がホスト側で転送**」 | ACT | 変更なし | owner の実行行為への帰属．primary（escrow 手順の記録） |
| source-inventory.md:11 | 「leray-hopf 関連は grep により 3 project dir・7 セッションに閉じることを **owner が確認**」 | ACT | 変更なし | 確認行為であって判断ではない．書きぶりが正確 |
| source-inventory.md:12 | 「…14 project dir 中 6 dir・36 top-level sessions に閉じることを **owner が確認**」 | ACT | 変更なし | 同上 |
| source-inventory.md:14 | 「※ host 割当ては 2026-07-20 の **owner 判断**で変更（当初: local-main=大学 PC の予定）」 | **AUT** | 変更なし | owner 判断として正しく標識されている．`provenance/ai-use.md:18` と同型 |

## 3. 処置の集計

| 処置 | 件数 |
|---|---|
| 変更なし | 276．内訳のうち特記すべき 5 件: 「変更なし（証拠注記）」3 件（`paper/sections/04-incidents.tex:32-33`，`evidence/incidents/INC-001.md:10`，`evidence/session-index/de129390:30`），**`paper/sections/04-incidents.tex:107-108`**（「変更なし（§4.1(b)，Wave C 申し送り）」．§4.1(b) は限定語の復元を Wave C／owner へ申し送っている），および **`analysis/workflow-evolution.md:31`**（「変更なし（証拠の増強を推奨）」．Evidence セルへの timestamp 追記を推奨している）．**「変更なし」は本 Wave の処置であって「問題なし」ではない** |
| **変更要** | **1** — `evidence/incidents/INC-005.md` 経緯 step 4（2026-07-18T06:28:39Z / 06:30:55Z の owner 発話を記載していない） |
| **owner 判断** | **3** — 規則 6 の**開示 scope のみ**（項目 3）が及ぶ 3 passage: `AGENTS.md:23-24`，`PLAN.md:211`，`provenance/ai-use.md:3`．§4.3 のとおり同一の裁定で同時に整合させる必要があり，3 件を分離して 1 件だけ未解決とすることはできない．`AGENTS.md:24` 末尾の「AI は著者にしない」は §0 の通り不変であり，裁定の対象ではない |
| B3 へ回付（B1 の処置ではない） | 2 — `paper/main.tex:36`，`paper/sections/05-discussion.tex:67-69` |
| 台帳の行数 | **282** |

**権限に関する記述で弱める必要のあった passage は 1 件もない．** 検査した
`scientific owner` / owner 権威 / 最終判断に関する passage は，すべて仲介の証拠の下で
そのまま維持される．**この null 結果の射程には限界がある**: §0 が既定処置を「変更なし」に
固定し，唯一利用できた反証材料（伝送チャネルの証拠）を裁定によって射程外に置いている
以上，「弱める必要があった」と判定されうる経路は最初から狭い．本結果は，*裁定が
検証可能なまま残した範囲において* 弱めるべき passage がなかったことを述べるにとどまり，
権威記述一般の健全性を示すものではない（§7 の限界も参照）．

なお初稿はここに「corpus の不正確さは人間行為を過小に記す方向である」と書いていたが，
独立レビューの指摘を受けて**撤回する**．その一般化は唯一の「変更要」1 件に依拠して
おり，しかもその 1 件は §4.1(b) の通り「人間による検出」ではなく「人間による観測と，
その場での明示的な不問」である．282 行のうち 1 行から corpus 全体の偏りの方向を
導くことはできない．

## 4. 未解決とされた 3 項目

### 前置き — 項目 1・2 の本文は既に存在しない

issue #60 と本 Wave の指示は，項目 1（"until the supervisor caught the discrepancy" と
"an incidental owner status check"）と項目 2（"the scientific owner's direct
supervision" の "direct"）が現在の本文に存在することを前提としている．**これは
PR #59（`fc912b9`）によって既に失効している．** `fe8fbeb` 時点で確認した:

| 項目 | 旧文 | `fe8fbeb` の現状 |
|---|---|---|
| 1a | `03-agent-workflow.tex`（`85627c0`）: "stalling a merge until the supervisor caught the discrepancy" | **削除**．`supervisor`／`caught` は同ファイルに 1 件も現れない |
| 1b | `04-incidents.tex`（`1b2788a`）: "Detection was triggered not by the orchestration's own monitoring but by an incidental owner status check" | **書き換え**．現 `04:107-108` は "An owner requested a status check when only 606\,MiB remained available." |
| 2 | `05-discussion.tex`（`85627c0`）: "the scientific owner's **direct** supervision is inseparable from the reported outcomes" | **書き換え，"direct" は消滅**．現 `05:60-61` は "The owner's supervision was part of the harness and cannot be separated from its outcome." |

生きているのは項目 3 のみである．ただし分析層の主張（`analysis/workflow-evolution.md:31`，
INC-005，`analysis/incident-ranking.md:15`）は存続しており，Wave C が本文の復活を検討
しうるため，1 と 2 も証拠に基づいて調査した．

### 4.1 項目 1 — 「supervisor が食い違いを捉えた」／「偶発的な owner の status 確認」

**(a) merge 監視の停滞．** session `7e6156bf`（local-main，EV-1669）で人間が Claude Code
セッションへ直接（仲介なしで）2 通を入力している:

- `2026-07-10T00:37:21.889Z` — 「勝手なゲート監視スクリプトを設定しませんか？ とっくに終わっています」
- `2026-07-10T00:43:22.204Z` — レビューが完了しているのにマージが進まないのは監視スクリプトの
  不正確さによる停滞ではないか，という確認であった旨の補足．

`00:18:42Z` から `00:37:21Z` の間，オーケストレータは外部入力を受けていない．回復
（3 経路を見る監視への刷新）は `00:37–00:43Z` に打刻されている．

**成立すること**（evidence_type: **primary**，confidence: **高**）: 人間が独立に，
レビュー完了と merge 停滞の併存を観察し，原因を監視の欠陥と正しく推定した．検出
チャネルは**人間からセッションへの直接入力**であり，connector 経由でもエージェント
提示でも CI 提示でもない．削除された文 "stalling a merge until the supervisor caught
the discrepancy" は**正確**であった．削除は harness 中心への再構成に伴う構成上の理由に
よるもので，裏付け不足によるものではない．

**同じ交換に記録されている，反対方向の事実**: 2 通目は，1 通目がオーケストレータに
**意図と逆に読まれた**ことへの訂正である．owner 自身が，1 通目は一文字欠けており意味が
真逆に取られた，質問提案ではなく確認がしたかったのだと述べている．すなわちこの窓には
「人間による正しい原因推定」と「エージェントによる著者意図の取り違え」が同居しており，
後者は issue #60 の問い 3 が求める drift の一例である（ただしチャネルは connector では
なくセッション直接入力なので `analysis/author-interface-traces.md` の trace 集合には
含めていない）．初稿は前者のみを記していた．

**成立しないこと**: 人間がどのようにして気づいたか（PR ページを見ていたのか，通知が
あったのか，経過時間から推測したのか）は記録されていない．

**推奨処置**: `paper/` は**変更なし**（該当文は既に存在せず，復活も推奨しない．
Section III は merge 監視の叙述を持たず，復活は owner が除去を求めた process residue の
再導入になる）．`analysis/workflow-evolution.md:31` の Evidence セルに上記 2 つの
timestamp を加える任意の増強のみ．**confidence: 高．**

**(b) INC-005 の status 確認．** session `de129390`（vps，EV-0247）の
`2026-07-18T07:40:10.101Z`，owner のメッセージ本文は `status` の 1 語である．
その後オーケストレータが `free -h` を実行し available 606 MiB を発見した．

**成立すること**（primary，高）: owner は**定型的な契機**を与えたのであって検出をした
のではない．`INC-005.md:10`・`:27`，`analysis/incident-ranking.md:15`，とりわけ
`evidence/session-index/de129390-...`（「owner からの検出ではなく，owner の一言が契機に
なった点が特徴」）はいずれも正確である．

**現本文の含意についての訂正（独立レビュー指摘）**: 初稿はここで，現 `04:107` の
"An owner requested a status check" を旧本文より「弱い」表現と述べていた．**これは
方向を取り違えている．** 削除されたのは PR #59（`fc912b9`）が落とした
"Detection came from an incidental owner status check, not …" の一文であり，
`incidental` と「オーケストレータ自身の監視によるものではない」という 2 つの限定が
同時に消えている（`git show fc912b9 -- paper/sections/04-incidents.tex` で確認できる）．
残った現本文は，監視の不備を述べる文の**直後**に owner の行為を置き，しかもその行為を
owner が知りえなかった 606 MiB という数値に索引づけている．逐語の主張としては依然
誤りではないが，「owner が気づいて確認を求めた」という**能動的な読みが初めて可能に
なっている**．それを妨げていたのが `incidental` である．

**したがって処置は「変更なし」だが，含意の弱化ではなく強化として記録する．**
Wave C の候補として，`incidental` に相当する限定（例: "A routine owner status check
prompted a memory check"）の復元を owner へ申し送る．本 PR では
`paper/sections/04-incidents.tex` を変更せず（§0 の範囲外であり，かつ復元の可否は
owner の判断である），`paper/main.tex` の匿名化メタデータ分岐だけを変更した．

**成立しないこと**: owner がメモリー状態を検出したという主張は何も支持されず，corpus も
それを主張していない．

**新規所見 — card が同一 window の owner 発話 2 件を落としている．** 逐語で確認した
（初稿はこれを「実在する人間検出の過小記載」と書いたが，独立レビューの指摘を受けて
下記の通り**再特徴づけする**）．

- `2026-07-18T06:28:39.808Z`（owner）: ビルドがコンテナ資源で長引いているのか，
  無理に止めなくてよい，状況を知りたいだけ，という趣旨の問い合わせ．
  **`INC-005` の 06:28–06:31Z の status 確認はこれを契機としている**のであって，
  オーケストレータの自発的監視ではない．card はこの契機を記していない．
- `2026-07-18T06:30:55.545Z`（owner，全文）: 「cache は worktree で共有する方針じゃ
  なかったかね？ それだと実質フルビルドですね．**まぁ良いですよ．時間はあるので．**」
  owner は `.lake` 共有方針からの逸脱（trigger 原因 (b)）を**観測している**が，
  同じ発話の中で**明示的に不問としており，対処を求めていない**．OOM が表面化するのは
  この約 70 分後である．

したがってこれは「人間が検出し対処した」事例では**ない**．正確には「人間が方針逸脱を
観測し，その場では許容する判断を下した」事例であり，trigger 原因 (b) がその後 70 分
存続したことの説明の一部でもある．**処置: 変更要**（経緯に上記 2 点を primary 証拠と
して追加する）．ただし **Wave C は「人間による検出」として書いてはならない** —
観測と，行動しないという判断の対として書くこと．**confidence: 高**（逐語・timestamp
付き，既に EV-0247 として引用されている同一 transcript）．**適用は Wave C**．

**「検出は connector 経由だったか」への答え**: 否．両事象とも，チャネルは Claude Code
セッションへの人間の直接入力であった．connector 経由チャネルが有意なのは別の場面である
（`analysis/author-interface-traces.md`）．

### 4.2 項目 2 — `05-discussion.tex` の "direct"

**状態: "direct" は既に消えている**（前置きの表を参照）．

**仮に残っていた場合に証拠が言うこと．** 仲介 census は "direct" を真に多義な語に
する．

- *読み 1（GitHub App を介さない）*: leray-hopf の `t-uda` 名義 issue／PR 作成 63 件の
  うち **32 件が connector 経由**である（`leray-hopf#1` — 最初の architecture 監査，
  `leray-hopf#145`–`leray-hopf#158` のリリース前 umbrella 全体，および owner に
  "Required decision" を提示する `leray-hopf#146` を含む）．`t-uda` コメント 183 件の
  うち 37 件が connector 経由．この読みの下では，"direct" は監督経路のうち GitHub
  artifact 側について実質的な過大主張になっていた．
- *読み 2（人間が文面を起草し読んだ）*: census は何も画定しない．逆向きにも，
  `analysis/mediation-census-methodology.md` は `null` のコメント 7 件について，その文面が
  定型のワークフロー通知であることを一次確認手順つきで記録している（`KSE2026#59` 上の
  `t-uda`／`null` コメントは全部で 13 件で，うち 7 件が id つきで挙げられている）．投稿
  主体そのものは同データからは確定しない．いずれにせよ `null` は「人間の手打ち」を
  意味しない．
- *census が全く測っていない第 3 のチャネル*: セッション内の監督（`AskUserQuestion`
  による方針エスカレーション — session index が特記する 3 点，同セッションの呼び出し
  総数は 8 件 — と，07-10 と 07-18 のセッション内介入）は GitHub 上に痕跡を残さない．
  これらは transcript にしか現れないため census の対象外である．
- *census が測っていないが GitHub 上には残る第 4 のチャネル*: **正式 PR Review**．
  `comments.json` は Review オブジェクトを含まず，Reviews endpoint は
  `performed_via_github_app` を**キーごと返さない**（値が `null` なのではない．
  `chatgpt-codex-connector[bot]` 自身の Review でも同じである）．
  したがって PR Review のチャネルは **未確定**であって「非仲介」ではない．
  `leray-hopf#174` の owner 3 巡レビューがこれにあたり，その 1 巡目は 7 分 25 秒後に
  connector 帰属のコメントで訂正されている（T5）．**初稿はこれを「人間の直接入力で
  GitHub に痕跡を残さない」と書いていたが，二重に誤りであり撤回する** — 痕跡は
  Reviews endpoint に残っており，チャネルは確定していない．

すなわち監督は実際に混成であった: **`t-uda` 名義の** GitHub 作業単位の作成のおよそ半分
（63 件中 32 件）は connector 経由であり，セッション内の舵取り（`AskUserQuestion`，
transcript 上の介入）は GitHub に痕跡を残さない非仲介の入力である．**PR Review の
チャネルは，上記のとおり非仲介とも仲介とも判定できない．** なお leray-hopf の
issue／PR 全 195 件を分母に取れば connector 経由は 16% であって，「およそ半分」は
`t-uda` 名義に限った比である．

**成立しないこと**: **誰が決めたか**については何も言えない．`leray-hopf#146` が最も
分かりやすい例で，これは owner に選択を求める connector 経由の issue である．connector は
準備し伝送した．決定はしていない．

**推奨処置: 変更なし．** 現在の文は**不可分性**を主張しており，これは証拠のどの読みでも
支持され，かつチャネルについて沈黙しているため，いかなる仲介事実によっても反証されない．
"(tool-assisted)" 等を加えることは (i) 本 Wave が禁じた drift にあたり，(ii) owner が
除去した process residue を再導入する．指示が挙げた再現性上の懸念（監督負荷を読者が
誤って見積もる）は，過大主張の除去によって既に解消されている．**confidence: 本文の
処置について高．背後のチャネル構成比については中**（census は非対称な signal の正確な
計数であり，セッション内チャネルは GitHub からは列挙できない）．

### 4.3 項目 3 — `AGENTS.md` 規則 6 の開示 scope（owner 判断．ここでは決めない）

**問い．** 規則 6（`AGENTS.md:23-24`）は「**原稿・分析への** AI の関与（モデル，範囲，
日付）」の記録を求める．`t-uda` アカウントから発せられた判断のうち**文面**を ChatGPT が
起草したものは，原稿でも分析成果物でもなく，原稿・分析作業を**指示する**ガバナンス
指示である．規則 6 はここに及ぶか．

**owner が手元に置くべき 2 つの文面上の complication．**

1. **リポジトリは既に 3 つの一致しない scope を述べている．** `AGENTS.md:23` は
   「原稿・分析への関与」，`provenance/ai-use.md:3` は「本リポジトリの**成果物**への
   AI システムの関与」，`PLAN.md:211` は「原稿生成またはレビューへの関与」である．
   「成果物」が最も広く，`provenance/author-decisions.md` に記録された判断（これも
   リポジトリの成果物である）を既に含みうる．裁定は 3 箇所を同時に扱わないと乖離する．
2. **`provenance/author-decisions.md:3-4` は別の器である．** 「scientific owner による
   確定判断のみを記録する．各判断には日付と根拠を付ける．」根拠列は既に緩い形で
   チャネルを記録している（「issue #23 コメント」「チャット判断」「owner の改稿指示」）．
   したがってチャネル開示には，AI 利用ログに触れない第 2 の受け皿が存在する．

**選択肢と帰結．**

**A — 規則 6 は判断の文面に及ばない．どこも変更しない．**
- *帰結*: 現行文の最も素直な読み．「原稿・分析」は 2 つの成果物クラスを名指しており，
  判断はそのいずれでもない．作業ゼロ．`provenance/ai-use.md` は**成果物**への AI 寄与の
  ログという性格を保ち，これは投稿先の AI 開示方針が通常問う対象と一致する．
- *費用*: `provenance/author-decisions.md` を監査する読者は，どの owner 判断が ChatGPT の
  支援の下で起草されたかをリポジトリから判別できない．
- *risk*: KSE の AI 開示要件が「原稿への関与」ではなく「研究プロセスへの AI の関与」で
  書かれていた場合，A は開示不足になる．

**B — 規則 6 は判断の文面に及ぶ．`provenance/ai-use.md` に記録する．**
- *帰結*: 透明性を 1 箇所に最大化する．connector 経由の判断（KSE2026 の 6 件，leray-hopf の
  32 件，計 38 件の issue／PR 作成と 42 件のコメント）について遡及行が必要になる．
- *費用*: 遡及的再構成は**大部分が導出不能**である．`performed_via_github_app` は伝送を
  証明し起草を証明しない（census 自身の注記）．大半の行は「チャネル: connector，起草:
  不明」となり，知識を増やさずに分量だけを増やす．さらに，伝送メタデータを著者性の主張と
  読み違える読者を招く — これは前提が明示的に禁じている誤読である．
- *risk*: **AI 利用**表に owner の判断を並べる構造そのものが，AI が決定に参加したという
  推論を招く．3 案中で drift の risk が最も高い．

**C — 規則 6 は判断の文面に及ばないが，`provenance/author-decisions.md` にチャネル
表記の約束を追加する．**
- *帰結*: `ai-use.md` を成果物に限定したまま（A の素直さを保ったまま），監督インター
  フェースを権限が既に記録されている場所で可視化する．具体的には根拠列の書式を拡張し，
  各行にチャネルを明示する（`GitHub issue #N via connector` / `GitHub comment, direct` /
  `chat` / `in-session`）．`author-decisions.md:10` は既にその方向を示唆しており
  （「owner 指示（issue #23 コメント）」），connector の詳細だけが欠けている．
- *費用*: 2026-07-25 の前提そのものを owner が確定判断として記録する必要がある
  （Wave A が保留として記録済）．既存 18 行の根拠セルの小規模な後付けが要るが，
  これらは snapshot からすべて導出可能である．
- *risk*: 最小．チャネルがチャネルとして，それが運んだ判断の隣に，権限台帳の中に
  記録される — 前提が主張する意味論そのものである．

**本書は推奨を行わない．** 3 案とも前提と両立する．上記の *risk* 行は**本書の著者に
よる評価**であって owner の判断ではなく，順位付けとして読まれるべきではない．
事実として検証可能な差は 1 点のみで，B だけが復元不能な再構成（各判断の起草者の
事後特定）を要求する，というものである．いずれを採る場合でも
`AGENTS.md:23`，`PLAN.md:211`，`provenance/ai-use.md:3` は同一の変更で整合させるべきである．

## 5. B3（公開メタデータ）への引き継ぎ事項

台帳の過程で B3 側の前提に誤りが見つかったため，ここに記録する．

### 5.1 byline は既に匿名である

`paper/main.tex` の byline は本 PR 適用**前**（`fe8fbeb`，当時の 36 行目）から
`\author{\IEEEauthorblockN{Anonymous Author(s)}}` である．**初稿は「PR #59
（`fc912b9`）で導入された」と書いていたが誤りであり，訂正する**: `git show
4bf508d:paper/main.tex` の 39 行目が既に同じ blind byline であり，byline は
リポジトリ最初の LaTeX scaffold から一度も実名だったことがない．`fc912b9` が行った
のは後続の `\IEEEauthorblockA{\todo{Affiliation …}}` 行の除去である．したがって「匿名化スイッチは現状の**非匿名**出力を既定とする」という
指示の前提は成り立たない．今日の出力は既に匿名側である．本 PR 適用後の当該行は
`\ifanonymous` 分岐の内側へ移っている（現在位置は
`notes/deanonymization-checklist.md` §2 の #1 を参照）．

本 Wave の採った設計: スイッチの既定を `\anonymoustrue` とし，**今日の PDF を保存する**．
研究費 acknowledgment（`provenance/author-decisions.md:10` で 2026-07-22 に確定，
`paper/` には未挿入）は非匿名分岐に置き，既定では描画されない．`\anonymousfalse` への
1 行変更で byline と acknowledgment が同時に現れる．非匿名分岐の実名 byline は owner が
供給する必要があり，`% TODO(owner)` として残してある．詳細と leak 一覧は
`notes/deanonymization-checklist.md`．

### 5.2 acknowledgment は IEEEtran conference mode で既定では消える

IEEEtran は conference mode で `\thanks` を破棄する．ログには
`** WARNING: \thanks is locked out when in conference mode` が素の `\typeout` として
出るのみで，LaTeX の警告機構にも `latexmk` の警告要約にも乗らない．
`\IEEEoverridecommandlockouts` を宣言しないと，acknowledgment は**通常の警告走査に
掛からないまま**描画されない（実測で確認．`notes/deanonymization-checklist.md` §1）．
本 Wave はこれを preamble に追加した（`\anonymoustrue` の下では出力に影響しない）．

### 5.3 artifact 可用性の齟齬（owner 判断，本 Wave では決めない）

`paper/sections/05-discussion.tex:67-69` は「redacted evidence excerpts, claim-to-evidence
manifests, and scripts …are available in the paper repository」と読者に告げる．しかし
`uda-lab/KSE2026` は private であり（`evidence/repository-snapshots/KSE2026/EXPORT.json`），
`paper/` 内にその bib entry も URL も DOI も存在しない（grep 済）．論文は当該リポジトリを
一度も名指ししていない．したがってこの一文は現状の読者にとって**指示対象すら特定できず，
3 つの artifact クラスのいずれも取得できない**．

読者が実際に到達できるのは public な `uda-lab/leray-hopf`（Lean ソース，タグ，
Sections IV–V で引用される PR 番号）であり，これは形式化の claim を支えるが，
evidence 手法の claim（contribution 3 が依拠する）を支えない．

選択肢と費用の対比は `notes/deanonymization-checklist.md` に置いた．**本 Wave は
選択せず，当該文にも触れていない．**

## 6. 新規 claim の候補（登録は行わない）

本監査の新規成果物は `paper/main.tex` の匿名化メタデータ分岐を除き `paper/` の外にあり，
新規の claim-bearing manuscript prose は導入していないため，新規 claim は**必要ない**．
台帳から導かれうる候補 3 件は PR 本文で owner へ提示するにとどめ，
`claims/paper-claims.md` には登録しない（`Status: candidate` の登録も凍結も owner の
行為であり，`paper/` 側の本文を待たせる副作用がある）．候補の内容と証拠識別子は
本 PR（`KSE2026#68`）の本文を参照．

**この選択は保守側に振れている**: `claims/paper-claims.md:11` は `Status: candidate` を
正当な非凍結状態として定義しており，issue #66 が範囲外としているのは **freeze** だけで
ある．したがって candidate 登録は規則上は可能で，登録すれば候補が `make verify` の
対象となりリポジトリ内に残る．本 Wave が登録を見送るのは「登録もまた owner の行為で
ある」という読みによるものであり，owner はこの自己限定を覆してよい．

## 7. 本書の限界

- 台帳は `fe8fbeb`（本 PR 適用**前**）時点の固定である．したがって `paper/main.tex` の
  3 行は本 PR の匿名化スイッチによって既に移動している（現在位置は
  `notes/deanonymization-checklist.md` §2 を参照．同節は `main.tex` については行番号ではなく
  `\ifanonymous` / `\thanks{` という grep 可能な構文を anchor とし，行番号を補助表示に
  留めている）．他のファイルは本 PR で変更していないため一致する．
- 検出チャネルの判定に用いた raw transcript は `private/raw-sessions/`（gitignored）に
  あり，第三者は再現できない．本書が引用したのは timestamp と短い運用上の発話のみで，
  いずれも `scripts/redact_check.py` を通している．
- `KSE2026#<num>` は `scripts/verify_claim_links.py` の認識トークンではないため，
  本書中の KSE2026 参照は機械検証されない（`leray-hopf#<num>`，`EV-`，`INC-` は検証
  される）．KSE2026 側の identifier は本文の主張の荷重を担わせていない．
- ChatGPT 側の会話は evidence に存在しない．A2 の「起草」機能は再構成であり
  confidence 中である．
- **§3 の null 結果（弱めるべき権威 passage は 1 件もない）は，前提の射程に依存する．**
  §0 が既定処置を「変更なし」に固定し，唯一利用できた反証材料（伝送チャネルの証拠）を
  裁定によって射程外に置いている以上，「弱める必要がある」と判定されうる経路は最初から
  狭い．本書の null 結果は *裁定が検証可能なまま残した範囲について* 成り立つのであって，
  権威記述一般の健全性を示さない．
- **前提となった 2026-07-25 の裁定そのものは，本リポジトリ内に再導出可能な記録を
  持たない．** `provenance/author-decisions.md` は owner 判断に「日付と根拠」を求めるが
  （`:3-4`），本裁定は同ファイルに未記載である．本書は owner 未確認の事項を確定判断と
  して記録しない方針により，同ファイルへの追記を行っていない（§0）．したがって
  第三者は，裁定の存在自体を本リポジトリだけでは検証できない．
- **A3 の「伝送のみ」は `t-uda` 名義の投稿に限った読みである．** 同じ App slug は
  `chatgpt-codex-connector[bot]` 名義の生成テキストにも付く（§1 A3 の交差集計）．
  slug 単独ではアクターの機能を決めない．
