# 著者インターフェースの介入 trace（issue #60 Wave B / #66）

Wave A が確定させた伝送チャネル統計（`analysis/mediation-census-methodology.md`）を
出発点に，`人間 author ↔ ChatGPT decision-support ↔ GitHub Connector ↔ Issues/PRs ↔
実装・レビューエージェント` という経路が実際にどう動いたかを，代表的な事例に即して
記述する．役割・権限のモデルは `analysis/author-interface-model.md`．

## 0. すべての trace に係る注記

**`performed_via_github_app: chatgpt-codex-connector` の帰属は，伝送チャネルのみを
証明する．** 文面を誰が起草したか，人間が投稿前に読んだかは，このデータからは分から
ない．逆に `performed_via_github_app: null` は人間による直接執筆を証明しない
（PAT を持つ任意のプロセスも null を返す）．

以下の項目はすべて `t-uda` 名義であり，owner の 2026-07-25 の裁定により，起草者が
誰であれ owner 権威である．本書は**インターフェースの動作**を記述するものであって，
権限が共有・委譲・希薄化されたことの証拠として書かれていない．

**生産性・有効性・因果は一切推論しない**（PLAN.md §9 Phase 5）．記録が示す事象の
継起は述べるが，結果をインターフェースに帰属させない．

**出典**: `evidence/repository-snapshots/{leray-hopf,KSE2026}/{issues,comments}.json`
（`EXPORT.json` に凍結時刻を記録）と，レビュー状態・timeline・`state_reason` について
の `gh api` による読み取り．

## 1. Trace 一覧

### T1 — 最初の issue が connector 経由であり，その所見のうち 2 件が後に反転・棄却された

**anchor**: `leray-hopf#1`（関連: `leray-hopf#50`，`leray-hopf#108`，`leray-hopf#115`，
`leray-hopf#127`，`leray-hopf#142`）

1. 2026-06-19T13:54Z — session `74aab39b`（EV-2076）に，auto-mode safety classifier が
   エージェントの `git push` / `gh repo create` を hard-block したため owner 自身が
   端末で `gh repo create` を実行した記録がある．*evidence_type: primary（session index），
   confidence: 高．*
2. 2026-06-19T14:29:50Z — その 36 分後に `leray-hopf#1` が connector 経由で作成される．
   7 項目の Lean アーキテクチャ監査と 9 項目の受け入れチェックリストからなる
   （typeclass bundle，axiomatic root import，過剰に強い `_axiomatic` 命名，CI の
   axiom-leak gate，totalise された `tsum` の定義域制御，成分ごとの補題重複，
   scaffold API の隔離）．*本文と timestamp について primary／高．文面の起草者に
   ついては reconstructed／低．*
3. 2026-06-20T04:18–04:43Z — `uda-lab-agent`（null チャネル）がこれをプログラム構造へ
   変換し，「この issue = axiom 除去プログラムの Wave 0（infra unblocker）」と位置づけ，
   `leray-hopf#2`–`leray-hopf#7` を派生させる．*primary／高．*
4. 所見 2・3・4 は実装される（`LerayHopf/Core.lean`，`_axiomatic` 改名，
   axiom チェックの CI 組み込み）．
5. **反転．** 2026-07-07 の `leray-hopf#1` 上のコメントで，所見 3 は `leray-hopf#108`
   により反転したと記録される（2026-07-05 の axiom-zero 化が前提を逆転させ，この issue が
   導入した `_axiomatic` 接尾辞のほうが陳腐化した）．*primary／高．*
6. **設計上の理由による棄却．** 2026-07-10 のコメントで，所見 1 が求めた
   structure field → typeclass parameter 移行は `leray-hopf#113` の作業中に評価され，
   設計上の理由で棄却されたと記録される（多重インスタンス化される非正準 bundle は
   typeclass 解決に適合せず，bundled structure + `letI` が mathlib の慣用である）．
7. 2026-07-11T11:46:32Z — file:line 単位の再監査を経て `completed` で close．

**成立しないこと**: 監査文面を owner ではなく ChatGPT が起草したこと；所見 3 の後の
反転が予見可能であったこと；インターフェースがなければ axiom 除去プログラムが
この構造を取らなかったこと．経過時間と結果は継起としてのみ述べている．

### T2 — 6 件の connector 経由 issue が Lean ソース照合層を通り，6 件すべてが訂正された（**drift**）

**anchor**: `leray-hopf#10` `leray-hopf#11` `leray-hopf#12` `leray-hopf#13`
`leray-hopf#14` `leray-hopf#15`，umbrella `leray-hopf#9`

1. 2026-06-20T11:20:28Z–11:29:14Z — connector 経由で 6 件の issue が約 9 分間に作成され，
   `leray-hopf#9` 上のコメントがそれを告知する．*primary／高．*
2. 11:24:50–11:25:44Z — connector が `leray-hopf#10`・`leray-hopf#11`・`leray-hopf#12` に
   実装 risk 監査を投稿する．`leray-hopf#10` の監査は既に内部に「後続の進捗を踏まえた
   status 訂正」節を持つ．
3. 11:42:18Z — `uda-lab-agent`（null）が `leray-hopf#9` に，Lean に通じた read-only の
   事前照合 3 パスを `e9de67b` に対して実施した結果，issue の品質は高いが**いくつかの
   記述に訂正が必要だった**と投稿する．
4. 11:43:00–11:43:48Z — 6 件**すべて**に「事前照合による訂正」が個別に投稿される．
   - `leray-hopf#10`: 当該 ODE 部分は既に完了しており未着手ではない → readiness を
     `leray-hopf#3` と `leray-hopf#12` への blocked へ再分類．
   - `leray-hopf#11`: 進行中の別レーン（`leray-hopf#2`）と衝突する → 派遣せず，
     `leray-hopf#2` の着地後に再スコープ．
   - `leray-hopf#12`: リポジトリは既に正しく符号化しており，除去対象とされた大域形は
     存在しない．
   - `leray-hopf#13`: issue が引用する signature は簡略化されており誤り．実際の signature は
     `letI` によるインスタンス束縛を伴い，これを再現しないと elaborate しない．
   - `leray-hopf#14` / `leray-hopf#15`: 順序が逆．加えて `leray-hopf#14` が提案する
     field は axiom を**強める**という警告．
5. 12:27:05Z — 同チャネルからも `leray-hopf#10` に status 訂正／衝突回避の注記が投稿され，
   現在の issue 本文が残作業量を過大に記述しており重複・衝突編集を招きうると述べる．

**drift として成立すること**: connector 経由の issue 本文が，未着手作業量を過大に記述し
（`leray-hopf#10`，`leray-hopf#12`），未コミットの進行中作業と衝突し（`leray-hopf#11`），
Lean の signature を誤って引用した（`leray-hopf#13`）．6 件中 6 件が派遣前に scope 訂正を
要した．**同じ trace が有効な仲介も示す**: issue 作成とエージェント派遣の間に，Lean
ソースに基づく read-only の gate が置かれており，その訂正が issue 上に記録されている．

**成立しないこと**: 事前照合層がなければ訂正が見落とされたこと；無駄な作業が発生した
こと（記録はない）；インターフェースと gate の寄与の比率．

*evidence_type: 全体として primary（6 件の訂正コメントと 2 件の connector コメントは
snapshot に全文があり `gh` で再読可能）／confidence 高．reconstructed かつ低: connector
経由 issue 本文の起草者，および人間が投稿前に読んだか．*

### T3 — 唯一の自己記述的記録と，それが記録する再演（**drift + 是正**）

**anchor**: `leray-hopf#177`，`leray-hopf#178`，INC-001

1. 2026-07-19T09:29:00Z — `leray-hopf#177` が connector 経由で作成される
   （`+10/−10`，statement card の式と locator の訂正，`leray-hopf#158` を参照）．
2. 09:34:15Z — **5 分 15 秒後**に `t-uda` により merge される．`reviews = []`，
   `reviewRequests = []` を `gh` で確認．*primary／高．*
3. 10:22:56Z — `leray-hopf#178` が connector 経由で作成される（P0，`leray-hopf#177` の
   prose 訂正を完遂し独立に再レビューする）．
4. 10:24:08Z — `leray-hopf#177` 上に，両リポジトリを通じて**唯一の自己記述的記録**が
   投稿される．要旨は，当該投稿が owner の明示的な指示により認証済み GitHub connector を
   通じて ChatGPT から投稿されたものであること；commit の著者帰属を争うものではなく
   **レビュー品質のみ**に関わること；当該 PR は requested reviewer 0・submitted review 0 で
   merge されており，その後に続いた ChatGPT による事後監査は**利害関係者によるレビュー**で
   あって独立レビューの証拠として扱ってはならないこと．同コメントは残存する実質的欠陥
   （doc comment と TODO に不正な関数空間表記が残っていること，statement card の
   `hT : 0 < T` の説明が不正確であること）も記録する．
5. 10:37:21Z 以降 — `uda-lab-agent` が `leray-hopf#177`・`leray-hopf#179`・
   `leray-hopf#180` に独立レビューを投稿する．
6. 15:49:21Z — connector が `leray-hopf#178` に owner の close 判断を投稿し `completed` で
   close．
7. 再演は本文にも残っている: `paper/sections/04-incidents.tex:46-49`（`leray-hopf#170` が
   独立レビュー規則を導入した 2 日後に `leray-hopf#177` がレビューなしで merge され，
   規則はまだ運用上信頼できる状態ではなかった）．

**scope 注記**: `leray-hopf#177` の裁定は**レビューの独立性**に関するものである．
ChatGPT による事後監査は独立レビューの証拠になりえない，というのがその内容であり，
誰が決定権限を持つかについては何も述べていない（commit 帰属を争わないことを明言して
いる）．本書はこの二つを混同しない．

**成立しないこと**: 裁定の文面を誰が起草したか；「明示的な指示」自体が ChatGPT との
セッション内で起草されたか；インターフェースがレビュー欠落を引き起こしたこと
（INC-001 は同種の handoff 失敗が独立に生じることを記録している）．

*primary: PR のレビュー状態（`gh` による実測），全コメント本文，timestamp，本文の該当文 —
高．reconstructed: merge の意図，監査と訂正が同一セッションで起草されたか — 低．*

### T4 — 11 件のリリース分解が 15 秒で投稿された

**anchor**: `leray-hopf#145`（umbrella），`leray-hopf#146`–`leray-hopf#156`，
`leray-hopf#157`，`leray-hopf#158`，INC-001

1. 2026-07-16T15:09:48Z — `leray-hopf#145` が connector 経由で作成される．公開前最終
   レビューの follow-up を一箇所で追跡する umbrella で，P0/P1/P2/P3 の階層表と
   リリース gate を持ち，この issue 自体では実装しないと明記する．
2. 15:11:53Z → 15:12:08Z — **11 件**の issue（`leray-hopf#146`…`leray-hopf#156`）が
   **15 秒間**に，おおむね毎秒 1 件の間隔で作成される．いずれも `[P0]`…`[P3]` の
   事前タグ付き．個別 timestamp は `issues.json` で確認．
3. 15:19:46Z — `leray-hopf#157`（リポジトリ改名，P0）．16:17:06Z — `leray-hopf#158`，
   8,093 文字の P0 soundness postmortem．`p = q = 1` における重み付き Hilbert triple の
   spike による陽な反例と，安全な訂正計画を含む．
4. 結果: P0/P1 はすべて `completed` で close．`leray-hopf#145` の締めコメント
   （2026-07-20T05:18:45Z）が release candidate の SHA を固定する．
   `leray-hopf#154`・`leray-hopf#184`・`leray-hopf#195` はリリース後 backlog として
   open のまま（`leray-hopf#152` は 2026-07-20T11:26:50Z に `completed` で close．
   初稿は open 側に誤記していた）．

**インターフェースについて成立すること**（primary／高）: 15 秒間に毎秒 1 件という
発行間隔は，connector を通じたプログラム的発行の機械的に観測可能な証拠である．
これは**投稿機構**についてのみの証拠である．

**成立しないこと**: 分解や優先度付けが機械生成であったこと．`leray-hopf#158` の反例は
数学的に実質的であり，その起草者はこのデータからは復元できない．インターフェースが
なければリリースが gate されなかったこと．

**INC との対応**: `leray-hopf#158` は INC-001 の検出 anchor である．INC-001 は既に
`leray-hopf#158`・`leray-hopf#162`・`leray-hopf#164`・`leray-hopf#169`・
`leray-hopf#170`・`leray-hopf#177`・`leray-hopf#178` を引用しているが，本 Wave が
加えるのは，**`leray-hopf#145`・`leray-hopf#157`・`leray-hopf#158`・`leray-hopf#177`・
`leray-hopf#178` がいずれも connector 経由である**，すなわち INC-001 の GitHub 側の
検出・是正の連鎖全体がインターフェースを通っていたという点である．Lean 側の修正 PR
（`leray-hopf#162`・`leray-hopf#164`・`leray-hopf#169`・`leray-hopf#170`）は connector
経由ではない．

### T5 — レビュー所見が発され，次の巡で撤回された（**drift**）

**anchor**: `leray-hopf#174`，INC-005

1. 2026-07-18T08:45:40Z — `leray-hopf#174` への初回レビューが `CHANGES_REQUESTED` を返す
   （`gh api repos/uda-lab/leray-hopf/pulls/174/reviews` で確認）．
2. 08:53:05Z — connector コメントが第 1 点を訂正・補強する．外部 contributor に
   preflight と full build の一律実行を求める趣旨ではなかったとし，先に示した二択の
   うち「現行方針を維持してこの文書 PR でも full preflight を実行する」を**撤回する**と
   明言する．blocking finding 自体も，検証報告の自己矛盾だけでなく，内部の資源制約を
   一般 contributor 向けの禁止規則として露出させている設計そのものである，と
   再特徴づけされる．
3. 09:24:52Z — 実装側が初回 `CHANGES_REQUESTED` と訂正コメントの双方に対応したと返答．
4. さらに 2 巡のレビューを経て 13:52:51Z に merge 許可．

**drift として成立すること**: 二択の是正案を伴うレビュー所見が発され，その一方が
**7 分 25 秒後**（08:45:40Z → 08:53:05Z）に明示的に撤回され，blocking finding の
性格づけ自体も改められた．初稿は「数時間のうちに」と書いていたが誤りである．
撤回は実装側の応答（09:24:52Z）より前であり，撤回された選択肢に基づく作業は
記録上発生していない．**同一レビュー巡内の自己訂正であり，drift としては弱い方である**．

**INC との対応**: `leray-hopf#174`・`leray-hopf#175`・`leray-hopf#176` は INC-005 の
一次証拠として名指しされている．08:53Z の撤回は，07:40Z の検出および 07:47–07:51Z の
恒常対策記録（session `de129390`，EV-0247）のおよそ 1 時間後にあたる．撤回の内容
（内部コンテナの資源制約を外部 contributor への禁止として露出させてはならない）が
INC-005 の是正と同じ主題であり，同じ午前に別チャネルで到達している点は記録に値する．

**成立しないこと**: OOM 連鎖とレビュー撤回の間の因果；初回レビューが ChatGPT により
起草されたのか伝送されただけなのか；撤回がリポジトリ内に記録された何かに促されたこと．
**併存として述べるにとどめる．**

*primary: 全コメント本文，timestamp，INC-005 の時系列 — 高．reconstructed: 2 つの
系列の関係 — 低．*

### T6 — 古いリポジトリ状態に基づくレビューが 28 分後に自己訂正された（**drift**）

**anchor**: `leray-hopf#107`，`leray-hopf#106`

1. 2026-07-07T15:48:33Z — `leray-hopf#107` が open（`t-uda`，null チャネル）．追跡 issue
   `leray-hopf#106` は connector 経由．
2. 15:54:59Z — merge gate コメント（null）: 独立レビュー証拠の欠落により merge が
   ブロックされている，自動レビュー派遣が失敗した．
3. 16:04:29Z — `copilot-pull-request-reviewer[bot]` による正式 Review（`state: COMMENTED`）．
   `gh api` で確認．
4. 16:22:50Z — connector コメントが，同チャネルで先に伝送されたレビューを訂正する．**古い README の
   表示に依拠していた**とし，現在の `main` の README は両 capstone が kernel-only／
   project axiom ゼロであると述べていると認めて，判定を反転させる．
5. 16:34:02Z — `leray-hopf#107` merge，`leray-hopf#106` を `completed` で close．

**drift として成立すること**: connector 経由で伝送されたレビュー判定が，古いリポジトリ
内容に基づいており，反転を要した．

**インターフェース境界に関する所見（報告事項）**: 訂正されている「先のレビュー」自体は
**GitHub から復元できない**．`comments.json` になく，当該 PR 上の正式 Review は Copilot の
1 件のみである．先行するレビュー行為はリポジトリに痕跡を残していない．
*evidence_type: 訂正の存在と本文について primary（高）．先行レビューは**復元不能**で
あり，訂正がその存在を主張していると述べうるにとどまる．*

**成立しないこと**: connector のレビューが merge gate を満たしたこと（16:04:29Z の
Copilot レビューが 18 分先行している）；古い README 表示がどう生じたか．なお，ここで
ChatGPT のレビューがレビュー証拠として扱われている事実は，`leray-hopf#177` の裁定
（ChatGPT の事後監査は利害関係者レビューである）より時間的に前である．継起として述べる
のみで，方針の軌跡としては主張しない．

### T7 — merge 後に claim 強度を弱める指示が出され，claim 台帳へ逐語で採用された

**anchor**: `KSE2026#37`，`KSE2026#29`，`KSE2026#35`，`KSE2026#42` →
`claims/paper-claims.md`（CLM-003 / CLM-004 / CLM-005）

1. 2026-07-22T16:43:47Z — `KSE2026#37` 上の connector コメントが，freeze 前に CLM-004 と
   CLM-005 の主張強度を一段弱めるよう指示する．CLM-004 の `FALSE-SUCCESS = 0` は
   purposive sample に対する記述統計に限定し，prevalence や guardrail 有効性に用いない
   こと；「帰結として解釈」は因果推論が強すぎ `consistent with` 程度が上限であること．
   CLM-005 の「帰結を分けたのは独立 statement 検査の有無だった」は対照例 2 件からの
   因果帰属として強すぎ，`a contrast consistent with the value of independent statement review` 程度の
   観測的表現へ**弱める**こと（逐語の指定ではなく強度の上限を示す形）．
2. 16:44:02Z — `KSE2026#29`: Cloud Monitoring の token 計数と escrow の内訳の対応は
   公式の metric description だけからは自明でなく，検証不能なら FX 下界・費用区間を
   「当該 metric 解釈の下での導出」と条件付けるべきである．
3. 16:45:30Z — `KSE2026#35`: 主題統合に GO を出しつつ，チェック済みの claim freeze は
   文言・数値解釈まで最終確定した意味ではないとして，freeze を `KSE2026#42` の
   follow-up の後ろへ送る．
4. 採用の跡は worktree 内で検証できる: `claims/paper-claims.md` の CLM-004 は purposive な
   6 セッションの記述統計として書かれ，Notes に prevalence・failure rate・guardrail
   effectiveness の推定に用いない旨と *consistent with* に留める旨がある．CLM-005 の本文は
   日本語で「独立 statement 検査の価値と整合的（consistent with）な対照例」となり，
   指示が示した英語表現は `claims/paper-claims.md` の Notes に**本文の目標強度**として
   記録されている（本文そのものが当該英文であるわけではない）．CLM-003 は当該 metric 解釈の下での導出である旨を
   明示する条件を持つ．
5. `provenance/ai-use.md` に実装パスの行がある．

**有効な仲介として成立すること**: インターフェースを通じて発された指示の**内容**が，
freeze された claim 本文と Notes まで端から端まで追跡できる．
初稿は「要求された英文の文言も含めて」と書いていたが誤りである．指示は
「…程度へ弱めてください」という**強度の上限**の指定であり，逐語の文言指定ではない．
採用されたのは強度であって文字列ではない．

**成立しないこと**: この指示がなければ最終原稿で claim が過大になっていたこと
（Phase 5 の adversarial review は独立した gate である）；Cloud Monitoring の意味論に
関する技術的判断が伝送ではなく ChatGPT に由来すること．

*primary: 3 件のコメント本文と timestamp，および `claims/paper-claims.md` の現在の
記述 — 高．reconstructed: 文面の起草者，および claim 側の変更が当該指示に**応答して**
行われたこと（時系列と内容の一致に基づく推定であり，別経路の可能性は排除できない） — 中．*

### T8 — draft が落としていた失敗記録を復活させた指示

**anchor**: `KSE2026#59`，`provenance/author-decisions.md`，
`paper/sections/04-incidents.tex`，`leray-hopf#177`

1. 2026-07-24T03:08:23Z — `KSE2026#59` 上の connector コメントが独立レビュー artifact を
   記録する（起草役から分離された read-only レビュアー 3 名，`Reviewed-by:` marker 3 件）．
2. 17:44:26Z — connector コメントが「追加 agent review への owner 承認済み対応方針」を
   投稿する．8 項目を対応対象とし 4 項目を明示的に範囲外とする．その第 3 項は，
   `leray-hopf#177` の再演を記録する簡潔な一文を**復活させる**よう求め，独立レビュー
   規則が直ちには運用上信頼できるものにならなかったことを示す有用な証拠である，と
   述べる．同コメントは項目の重みも分けており，第 1・2 項は真の欠陥として必須，
   第 3 項は同等の重大性を持つ欠陥ではなく原稿のバランス訂正である，としている．
3. 採用: `provenance/author-decisions.md` に 8 項目／4 項目の切り分けが転記され，
   `provenance/ai-use.md` に実装パスの行があり，
   `paper/sections/04-incidents.tex:46-49` に復活した一文がある．

**Phase 5 にとっての意味**: これは，インターフェースを通じて伝送された指示が，
**都合のよい選択に抗して**働いた記録である — draft から除かれていた自己に不利な失敗
記録を復活させている．

**成立しないこと**: 脱落に気づいたのが誰か；他のレビュアーによって復活しなかったで
あろうこと；レビュー過程の有効性に関する何か．

*primary: 2 件のコメント本文と timestamp，`provenance/author-decisions.md` と
`paper/sections/04-incidents.tex` の現在の記述 — 高．reconstructed: 文面の起草者，
および復活が当該指示に応答して行われたこと — 中．*

### T9 — インターフェースの能力境界が記録に残っている

**anchor**: `leray-hopf#157`

2026-07-19T09:42:26Z の connector コメントは，リポジトリのファイルと issue tracker が
HEAD まで同期した一方で，**接続されている GitHub app はリポジトリの description／topics の
変更を公開しておらず，この実行環境には認証済みの `gh` CLI もない**ため，これら 2 つの
リポジトリ水準のフィールドは自動設定できなかった，と述べる．そのうえで別環境で実行
すべき具体的なコマンドを提示し，最終 release SHA と手動 attestation の手順が固まるまで
可視性を public に切り替えないよう gate を置いている．

**成立すること**（primary／高）: connector チャネルの作用域は issue／PR／コメントの面に
限られ，リポジトリ設定の変更はその外にあって別環境へ差し戻される．インターフェースが
どこで止まるかについて記録中で最も明瞭な記述である．

**成立しないこと**: 差し戻されたコマンドを誰が実行したか；この境界が常に成り立って
いたこと（ある時点の 1 つの記述にすぎない）．

### T10 — 自身が伝送した issue 本文の陳腐化に対する反復的な訂正

**anchor**: `leray-hopf#22`，`leray-hopf#64`，`leray-hopf#10`

同型の connector コメントが 3 件ある．

- `leray-hopf#22`（2026-06-21T11:25:28Z）: issue 本文が重要な点で陳腐化しているとし，
  project axiom 数は 4 のままで，これは粒度の改善であって 4→3 の削減ではないと訂正する．
  併せて，残余作業でこの issue を再 open すべきではないという停止規則を置く．
- `leray-hopf#64`（2026-06-30T03:54:05Z）: 直接対応した PR がまだないため open のままに
  すべきとし，先行 PR に対する部分進捗を項目別に会計する．timeline 上は，後継 issue が
  04:17:24Z に相互参照され，`leray-hopf#64` は 05:35:36Z に `completed` で close された．
  すなわち「open のままに」という推奨は，`leray-hopf#64` への直接対応ではなく後継 issue に
  よって約 1 時間 41 分後に置き換えられた．
- `leray-hopf#10`（2026-06-20T12:27:05Z，T2 にも登場）: 同チャネルが自ら伝送した
  issue 本文を，残作業を過大に記述していると訂正する．

**成立するパターン**: インターフェースは，自ら伝送した本文を含め，issue 本文が記述する
状態への訂正を繰り返し投稿していた．これと並行して，`uda-lab-agent` も構造的に同型の
訂正（本文が陳腐化している旨，axiom pin の訂正）を null チャネルで
`leray-hopf#9`・`leray-hopf#24`・`leray-hopf#26` に投稿している．陳腐化訂正の規律は
**インターフェースに固有ではなく**，両チャネルが担っている．

**成立しないこと**: connector 経由の本文が他より高頻度あるいは低頻度に陳腐化したこと
（比率の比較は試みておらず，データもそれを支持しない）．

*primary: 3 件のコメント本文，timestamp，`leray-hopf#64` の timeline — 高．
reconstructed: 陳腐化訂正が意識的な規律であったか偶発的であったか — 低．*

### T11 — 承認を保留し，文書上の過大表現 1 点を差し戻したレビュー

**anchor**: `leray-hopf#190`

2026-07-20T07:53:29Z の connector コメントは再レビューの結果であり，前回指摘の 3 点
（regularity scope，capstone dependency cone への限定，README title）が適切に修正された
ことを確認したうえで，1 点を残す．`docs/claims-and-scope.md` が axiom チェックスクリプトを
"a CI gate" と表現しているが，現行運用では PR ごとの CI ではなく手動 dispatch の
full-build／release-attestation で実行されるため，`a manually triggered verification gate`
等へ改めるべきである，という指摘である．そのうえで「この一点が修正されれば，内容面では
merge 可です．修正後に approve します」と述べ，**承認を保留している**．

**成立すること**（primary／高）: 定型の merge 許可とは異なり，追跡可能な推論を伴う
指摘であり，かつ承認を条件付きで保留している．指摘の対象は，`analysis/workflow-evolution.md`
および本 Wave の台帳が別途扱っている「manual attestation と PR ごとの CI の区別」と
同じ論点である．すなわち，文書が検証機構の実施頻度を過大に表現することへの是正である．

**成立しないこと**: この指摘がなければ当該表現が残ったであろうこと；指摘の文面の
起草者．

**採録の経緯**: 初稿はこの項目を「定型の merge 許可コメント」として除外していた．
独立レビューが，実際の本文は定型承認ではなく実質的な保留であると指摘し，除外理由が
事実に反することが確認されたため，trace として採録した．PLAN.md §9 Phase 5 の観点では，
除外理由が誤っている除外は，意図の有無にかかわらず選択的採録と同じ帰結を持つ．

## 2. drift の所在と，drift を水増ししていないことの確認

**drift は見つかった．** 明示的な drift 事例は
**T2**（connector 作成のバッチ 6 件全件に scope 訂正．Lean signature の誤引用と
進行中作業との衝突を含む），
**T3**（connector 作成の PR がレビュアー 0・レビュー 0 で merge され，後続監査がその訂正
自体の不備を 3 箇所指摘），
**T5**（レビュー所見が発され明示的に撤回），
**T6**（古い README 内容に依拠したレビュー判定が 28 分後に反転），
**T10**（陳腐化した issue 本文への反復的な自己訂正）である．

**drift 側を水増ししないための negative finding:**

- **connector 作成の issue で `not planned` として close されたものはない．** leray-hopf の
  connector 経由 32 件すべてについて `state_reason` を確認した．close 済みの **issue** は
  すべて `completed` であり，`leray-hopf#154`・`leray-hopf#184`・`leray-hopf#195` が
  open のまま（`leray-hopf#177` は PR であり `state_reason` は null．merge 済み）．
- **connector 作成の PR で unmerged のまま close されたものはない．** 両リポジトリに
  connector 作成の PR は `leray-hopf#177` と `KSE2026#59` の 2 件しかなく，どちらも merge
  されている．
- **数学的に誤った connector 発の主張は見つからなかった．** とくに `leray-hopf#158` の
  `p = q = 1` 反例は検討に耐え，INC-001 の是正を駆動している．

**drift 探索の範囲（全列挙）:**

- リポジトリ: `uda-lab/leray-hopf`（public），`uda-lab/KSE2026`（private，read 権限あり）．
- snapshot: 両リポジトリの `issues.json` と `comments.json` の全行をプログラムで走査
  （抽出であってサンプリングではない）．
- 番号: Wave A が列挙した leray-hopf の connector 経由 32 件と KSE2026 の 6 件，加えて
  connector 経由コメントが付いた全 issue．
- ライブ endpoint: `repos/…/issues/N`（`state_reason`），`repos/…/issues/N/timeline`，
  `repos/…/pulls/N` と `…/pulls/N/reviews`．
- キーワード走査（大文字小文字を無視，leray-hopf の全コメントと全 issue 本文，両チャネル）:
  `correction|corrected|correct my|retract|withdraw|撤回|訂正|stale|reversed|revert|
  walk back|superseded|supersedes|incorrect|mistaken|誤り|誤記|誤判定|overstat|actually,`．
- 相互参照: `claims/paper-claims.md`，`provenance/ai-use.md`，
  `provenance/author-decisions.md`，`paper/sections/*.tex`，`evidence/session-index/` の
  全 6 件，incident card の全 5 件．

**探索できていない範囲（限界）**: 削除済み・minimize 済みコメントは snapshot に含まれず
復元できない．コメントの編集履歴は遡って取得できない．正式 PR review の本文は
`comments.json` に含まれず，`leray-hopf#107` と `leray-hopf#177` についてのみライブ取得
した．ChatGPT 側の会話は evidence に一切存在しない．

## 3. 検討して採用しなかった trace（理由つき）

`analysis/incident-ranking.md` の「除外，理由つき」の形式に倣う．

| 候補 | anchor | 不採用の理由 |
|---|---|---|
| codex bot によるレビューコメント群 | KSE2026 の複数 PR | 投稿者が bot アカウントであり，`t-uda` 名義の著者インターフェースとは別のアクター．別現象 |
| `chatgpt-codex-connector[bot]` の「Codex アカウントを作成せよ」定型返信 | — | 非認可 mention に対する定型応答．**何の証拠としても引用しない** |
| 定型の merge 許可コメント 6 件 | `leray-hopf#172` `leray-hopf#175` `leray-hopf#176` `leray-hopf#181` ほか | 1〜3 文の定型承認で，追跡できる推論を含まない．個別 trace ではなく**型**として報告するに留める．**初稿はここに `leray-hopf#190` も入れていたが誤りであり，T11 として採用した．**`leray-hopf#173` も 1〜3 文には収まらないが，先行する指摘の確認に留まるため不採用 |
| `leray-hopf#82` `leray-hopf#93` `leray-hopf#115` `leray-hopf#106` | — | 定型的で結果に起伏がなく，追うべき分岐・訂正・係争がない |
| `leray-hopf#187` `leray-hopf#188` `leray-hopf#189` `leray-hopf#191` | — | 体裁・運用の issue で，記録された不一致なく数時間で close．T1–T11 に比して収量が低い |
| `leray-hopf#184` `leray-hopf#195` | — | connector 作成だがコメント 0 件で open．追うべき下流がない |
| `leray-hopf#154` | — | open だが活動は INC-005 のセッションに属し既にそちらで扱われている．インターフェースについて追加情報がない |
| `leray-hopf#99` — 先の `Reviewed-by` artifact の「所見なし」は誤りであったという自己訂正 | — | 真正の drift だが `performed_via_github_app: null`，投稿者 `uda-lab-agent`．著者インターフェースの trace ではない．自己訂正がインターフェース固有でないことの傍証として 1 行分の価値はある |
| `leray-hopf#145` の夜間自律運転の状態記録における「訂正: 誤報でした」 | — | 同上（null チャネル，`uda-lab-agent`） |
| `leray-hopf#117` — 先の blocker コメントは置き換えられたという訂正 | — | `t-uda` / null チャネル．Wave A が禁じた仮定（null＝人間直接）を置かない限りインターフェースに帰属させられない |
| `leray-hopf#21` `leray-hopf#31` の connector 完了メモ | — | 「PR #NN で完了」形式の事務処理．型としては有用だが trace ではない |
| `KSE2026#42` `KSE2026#58` `KSE2026#60` `KSE2026#61` の本文 | — | `KSE2026#60`・`KSE2026#61` は本作業自身の発注 issue（自己言及）．`KSE2026#42` の内容は T7 の結果として既に扱われている．`KSE2026#58`（図）は snapshot 時点で完了結果がない |

## 4. incident との対応と，セッションログ被覆の欠落

### 対応

- **INC-001** — GitHub 側の検出→是正の連鎖全体が connector 経由である
  （`leray-hopf#145`・`leray-hopf#157`・`leray-hopf#158`・`leray-hopf#177`・
  `leray-hopf#178`）．Lean 側の修正 PR（`leray-hopf#162`・`leray-hopf#164`・
  `leray-hopf#169`・`leray-hopf#170`）は connector 経由ではない．INC-001 自身の教訓
  （独立レビュー規則が一度で定着しなかったこと）は，`leray-hopf#177` の自己記述的
  コメント（T3）が記録している事柄そのものであり，`KSE2026#59` の第 3 項（T8）が
  本文へ復活させた事柄でもある．
- **INC-005** — `leray-hopf#174`・`leray-hopf#175`・`leray-hopf#176` が一次証拠として
  名指しされている．3 件とも connector のレビューコメントを持ち，`leray-hopf#174` が
  撤回（T5）を含む．
- **INC-002 / INC-003 / INC-004 — 対応なし．** INC-002（`leray-hopf#27`）と
  INC-004（`leray-hopf#120`）の PR には connector 経由の活動が 1 件もなく，レビューは
  `uda-lab-agent` 経由で行われている．INC-003 は GitHub 上の面を持たないログ保全の
  incident である．**この不在は報告に値する: merge 前検出が最もよく効いた 2 件の
  incident に，インターフェースは登場しない．**

### セッションログ被覆の欠落（PLAN.md §4 の報告事項）

escrow にある符号化済みセッションは 6 件である．connector の事象を対応させると:

| connector 事象 | セッション被覆 |
|---|---|
| `leray-hopf#1` 作成（2026-06-19T14:29:50Z） | 暦上は `74aab39b` の内側だが，index の事象表は**この issue の作成を記録していない**．記録されているのは 13:54Z の classifier ブロックと owner による `gh repo create` まで．**起草行為はどのログにもない** |
| `leray-hopf#10`–`leray-hopf#15` のバッチと事前照合訂正（06-20T11:20–11:43Z） | **完全な欠落**．`74aab39b` は 04:24Z に終わり，`90fa24bb` は 12:49Z に始まる．T2 全体が 8 時間 25 分の未被覆窓に落ちる．存在したことが明らかなオーケストレータセッションが escrow にない |
| 06-21T07:23–11:25Z の connector コメント群 | **被覆あり**（`90fa24bb`）．実質的に被覆された唯一の connector クラスタ |
| `leray-hopf#64`（06-30），`leray-hopf#82`（07-03），`leray-hopf#93`（07-05），`leray-hopf#106`/`leray-hopf#107`（07-07） | **欠落**（06-29T12:41Z → 07-09T18:01Z が未被覆）．T6 全体を含む |
| `leray-hopf#145`–`leray-hopf#158` のバースト（07-16T15:09–16:17Z） | **未符号化**．暦上は `de129390` の内側だが，同 index は 07-18 の OOM 区間のみを符号化すると明記しており，07-16 のリリース分解は事象表に一切現れない．T4 にセッションログの裏付けはない |
| `leray-hopf#172`/`leray-hopf#173` の承認（07-17），`leray-hopf#174` の訂正（07-18T08:53Z） | 暦上は内側だが**未符号化**．`de129390` の事象表は当該 PR を merge 済みとして結果欄に記すのみで，connector のレビューコメントと撤回は現れない |
| 07-19 の connector コメント群（**自己記述的記録を含む**） | **完全な欠落**．`de129390` は 07-18T15:49Z に終わる．T3 にセッションログの裏付けはゼロ |
| 07-20 の締めコメント群 | **完全な欠落** |
| KSE2026 の connector 項目すべて（07-22 → 07-24，T7・T8） | KSE2026 の論文作業に対する **session index が存在しない**．`evidence/session-index/` は leray-hopf 期の 6 件のみ |

**要約**: 11 件の trace のうち，符号化済みセッション区間の内側に落ちるのは T10 の一部と
`leray-hopf#64` の作成のみである．**インターフェースの唯一の自己記述的記録（T3）と
最大の connector バースト（T4）は，いずれも未被覆の窓にある．** それらについて本書が
述べたことはすべて GitHub 側の一次証拠であり，セッションログによる裏付けはない．
起草側について復元できることは何もない．

## 5. 識別子の解決可能性

`scripts/verify_claim_links.py` が認識するトークンは
`EV-\d{4}`・`INC-\d{3}`・`CLM-\d{3}`・`leray-hopf@<sha>`・`leray-hopf#<num>`・
`decl:<name>`・`cite:<key>` である．

1. **`KSE2026#<num>` は認識トークンではない．** `analysis/`・`notes/`・`paper/` では
   単に照合されずに素通りする（エラーにはならないが検証もされない）．
   `claims/paper-claims.md` の `- Evidence:` 行が KSE2026 番号**のみ**からなる場合は
   「認識可能な evidence identifier がない」として **fail する**．T7 と T8 は KSE2026 に
   のみ anchor を持つため，これらを claim 証拠にする場合は受理されるトークン
   （CLM-003/004/005 そのもの，あるいは `leray-hopf#177` と INC-001）を併記するか，
   resolver を拡張する必要がある．本書で用いた leray-hopf の番号はすべて snapshot の
   `issues.json`（195 件）に存在することを確認済みであり，解決に失敗するものはない．
2. **コメント ID は anchor 型ではない．** 自己記述的記録も，解決可能な形は
   `leray-hopf#177` とその timestamp である．本書は connector コメントを
   `leray-hopf#<issue>` + timestamp の形で参照している．
3. **他リポジトリ（notes 系）への参照は解決不能．** connector 本文には別リポジトリの
   issue 参照があるが，snapshot も resolver パターンも存在しない．本書の trace は
   いずれもそれらに荷重を置いていない．
4. **`decl:<Lean.Name>` は機械検証対象外**（issue #42 項目 5 で文書化済みの保証範囲）．
5. **snapshot の陳腐化境界**: `leray-hopf#N` は `N ≤ 195` の範囲でのみ解決し，
   `leray-hopf@<sha>` は凍結された `commits.json` に対してのみ解決する．
