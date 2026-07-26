# Connector linkage —方法論と限界（issue #70）

`scripts/extract_chatgpt_export.py` と `scripts/join_connector_linkage.py` により，
著者の ChatGPT データエクスポート（`/private/sources/KSE2026/OpenAI-ChatGPT-export.20270726.zip`，
409 会話，2026-07-25 エクスポート）と `evidence/repository-snapshots/{leray-hopf,
leray-hopf-notes,KSE2026}/` の GitHub snapshot を突き合わせ，GitHub Connector 経由の
書き込み（認証済み `t-uda` アカウントから `chatgpt-codex-connector` に帰属する投稿）
を ChatGPT 会話側のメッセージへ対応づけられるかを検証する．issue #60 の follow-up．
出力は `evidence/metrics/connector-linkage.json` / `.csv`（`--emit-public` で
committed snapshot から再生成，generated_at 以外は決定的）．raw エクスポートは
tracked にならず，中間生成物はすべて `/private/derived/KSE2026/chatgpt-export/`
（gitignored）に置く．

## Q1（否定的所見）: エクスポートは connector 書き込みを直接証明しない

`scripts/extract_chatgpt_export.py` が全 409 会話・19,993 メッセージを走査して
再導出したスキーマ事実（`inventory.json`，実行のたびに再計算し，決め打ちしない）:

- `message.author.role` は `user` / `assistant` の 2 値のみ．tool role は存在しない．
- `message.author.name` は全メッセージで null．
- connector／tool-call ペイロードはエクスポートのどこにも存在しない．
- ノードツリーは `{id, message, parent}` のみを持ち `children` を持たない（tree は
  parent pointer から再構築する）．root ノード（`message: null`）は 409 件で会話数と
  一致し，`message` を持つノードは 19,993 件．

**したがって本データは，ある GitHub 書き込みが Connector 経由であったことの
一次証拠を一切含まない．** 以下のすべての tier は，メッセージ本文とタイムスタンプ
から組み立てたテキストベースの状況証拠であり，一次証拠（primary）ではなく
`evidence_type: reconstructed` として扱う．confidence は tier ごとに個別に持つ
（次節）．

`codex.json` 脚注: Codex cloud tasks 86 件，すべて `t-uda/*` 個人リポジトリで
target repo への言及はゼロ（本 issue の対象外，件数のみ記録）．`user.json` は
存在確認のみ行い値は一度も読んでいない．

## 候補会話の抽出

- `--since 2026-06-01T00:00:00+00:00`（5月以前は対象外）．
- 選定条件は「対象 repo トークン（`leray-hopf`／`leray-hopf-notes`／`lean-pde`／
  `lean-pde-notes`／`KSE2026`，新旧名両方）のいずれかがベア部分文字列として出現」
  （`tight`）または「`uda-lab` という語（org 単位のワイドトークン）が出現」
  （`wide`，`tight` を満たさない場合のみ）．`url_refs`/`text_mentions`（後述）より
  意図的に広い網であり，`gh` CLI 呼び出し（`repos/uda-lab/leray-hopf/...`）や
  プレーンテキストの言及も拾う．
- 結果: 409 会話中 29 件が候補（`tight` 19，`wide` のみ 10）．開発時の read-only
  inventory が報告した概数（tight 約20，wide 込み約79，日付フィルタなし）と大筋で
  一致することを確認済み（tight はほぼ一致；wide は本抽出が `--since` で絞っている
  分小さい）．

## Tier 階層（先に成立した tier が勝ち，同 tier 内の同点は `ambiguous`）

正規化 `normalize()`（`scripts/join_connector_linkage.py`，抽出側からも import して
両側で同一関数を使う）: NFC 正規化 → CRLF/CR を LF に統一 → 各行の末尾空白を除去 →
連続する空行を1行に圧縮 → 先頭・末尾の空行を除去．ハッシュは正規化後の文字列が
64 文字未満なら `None`（短文一致を排除するフロア）．

1. **exact-id**（confidence: high）— メッセージ内の `#issuecomment-NNN` /
   `#discussion_rNNN` / `#pullrequestreview-NNN` URL フラグメントが snapshot の
   comment／review id と一致．
2. **exact-body**（confidence: high）— 投稿本文（issue／PR 作成は
   `title\n\nbody`，comment／review は `body`）の正規化ハッシュが，候補メッセージ
   側のハッシュ（メッセージ全体／各 fenced code block／先頭見出し行を除いたもの）
   のいずれかと一致．snapshot 側でハッシュが複数 artifact に衝突する場合は
   `ambiguous`（推測しない）．メッセージ側で同一ハッシュが複数メッセージにまたがる
   場合は最も早いメッセージを採用（ambiguous とはしない）．**注意**: snapshot の
   body は `scrub()` で email／denylist 名をマスクしているため，マスク対象を含む
   本文は原理的に一致し得ない．
3. **time-and-context**（confidence: medium）— artifact の `(repo, number)` が
   `created_at` の ±window 分以内に言及され，かつその window 内の全言及が単一の
   会話に由来する．2 会話以上にまたがる場合は `ambiguous`．既定 window は 60 分．
   window 感度（30/60/120 分，未解決 artifact に対する再集計）:

   | window（分） | time-and-context | ambiguous | none |
   |---:|---:|---:|---:|
   | 30 | 201 | 0 | 402 |
   | 60 | 215 | 0 | 388 |
   | 120 | 234 | 0 | 369 |

   いずれの window でも `ambiguous` は 0（2 会話以上が同一 (repo, number) を
   window 内で言及したケースは発生していない）．60 分を既定として固定する．
4. **reconstructed**（confidence: low，**exact として数えない**）— artifact の
   `created_at` が候補会話のメッセージ時刻の範囲（span）に収まり，かつその会話が
   当該 repo に言及している．番号までは要求しない，最弱の tier．
5. **unmatched** — 上記いずれも成立しない．

## Join universe と pr_review の扱い

connector-routed universe は「issue／PR 作成」と「comment」のうち
`performed_via_github_app == "chatgpt-codex-connector"` **かつ** 投稿者ログインが
`[bot]` で終わらないもの（`t-uda` 名義で connector 経由投稿されたもの）に限る．
**`chatgpt-codex-connector[bot]` という bot アカウント自身が投稿したコメント
（leray-hopf 69 件・KSE2026 相当数，`mediation-census-methodology.md` 参照）は
別の provenance の問い（bot が自動生成したレビュー文か，人間が connector 経由で
投稿した文か）であり，本 universe には含めない．** 開発中，この区別を欠いた実装で
leray-hopf のコメント件数がほぼ倍になる回帰を作り込み，本番反映前に検出・修正した
（テスト `test_bot_account_connector_comment_is_excluded_from_universe` として残す）．

`pr_review` は connector-routed universe **に含めない**が，coverage table には
独立した artifact_kind として掲載する．理由: GitHub の Reviews API は
`performed_via_github_app` を返さないため，レビューが connector 経由か否かを
判定する手段が原理的にない．`null`／欠落を「connector 経由でない証拠」として
読んではならない．

connector-routed universe サイズ（`evidence/metrics/connector-linkage.json` の
`connector_routed_universe_size`，実行のたびに committed snapshot から再計算）:
**174**（leray-hopf 32 creations + 37 comments，KSE2026 8+2 creations + 27
comments，leray-hopf-notes 22+4 creations + 42 comments）．issue #70 計画時点の
read-only inventory が報告した概数（leray-hopf 32+37=69，KSE2026 6+5=11，計約80）
より大きい．理由は3つとも実質的で，隠さず記録する:
(a) leray-hopf-notes は今回新規に追加された repo で，当時のベースラインに含まれて
いない（103/174 が leray-hopf-notes 分）．(b) leray-hopf・KSE2026 の snapshot は
issue #79（denylist masking）と issue #70 の作業の間に再取得されており，
活発に動いている repo である以上そのぶん増加している．(c) 開発中に見つけた
bot アカウント混入バグの修正前は誤って約2倍にカウントしていた（上記）．leray-hopf
単独の creations/comments 数（32/37）は，このバグ修正後は元の baseline と
完全に一致する．

## Coverage（connector-routed universe，repo × artifact_kind × tier）

| repo | kind | total | exact-id | exact-body | time-context | reconstructed | ambiguous | unmatched |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| KSE2026 | issue_comment | 27 | 0 | 0 | 0 | 5 | 0 | 22 |
| KSE2026 | issue_creation | 8 | 0 | 0 | 2 | 2 | 0 | 4 |
| KSE2026 | pr_creation | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| leray-hopf | issue_comment | 37 | 0 | 0 | 13 | 24 | 0 | 0 |
| leray-hopf | issue_creation | 31 | 0 | 0 | 26 | 5 | 0 | 0 |
| leray-hopf | pr_creation | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| leray-hopf-notes | issue_comment | 42 | 5 | 0 | 27 | 9 | 0 | 1 |
| leray-hopf-notes | issue_creation | 22 | 0 | 0 | 8 | 13 | 0 | 1 |
| leray-hopf-notes | pr_creation | 4 | 0 | 0 | 3 | 0 | 0 | 1 |

`exact-body` は全行で 0 件（本候補集合では，assistant のドラフト文が正規化ハッシュ
一致まで含めて投稿本文と一致した例が一件もなかった）．`exact-id` の 5 件はすべて
leray-hopf-notes の issue_comment．これは issue #70 計画段階の read-only inventory
が既に把握していた「厳密な `#issuecomment-` アンカーが 6 件（lean-pde-notes PR
55/57/58/59 に 5 件，lean-pde/issues/4 に 1 件）」という事実を，本パイプラインが
独立に再現したものである: universe 内の 5 件（leray-hopf-notes issue_comment）に
加え，universe 外（非 connector-routed）で `leray-hopf#4` への `alias:lean-pde`
フラグ付き exact-id 一致が 1 件あり（`evidence/metrics/connector-linkage.csv` の
notes 列，`outside-universe` コード），合計 6 件で一致する．

`pr_review` addendum（universe 外，独立集計）: KSE2026 109 件
（exact-id 0／exact-body 0／time-context 4／reconstructed 63／ambiguous 2／
unmatched 40），leray-hopf 152 件（4／0／24／106／0／18），leray-hopf-notes 183 件
（4／0／107／71／0／1）．

## エイリアス正規化（`lean-pde`／`lean-pde-notes` → `leray-hopf`／`leray-hopf-notes`）

`gh api repos/uda-lab/lean-pde` と `gh api repos/uda-lab/lean-pde-notes` は
いずれも `leray-hopf`／`leray-hopf-notes` と**同一の repository id**
（`1274442927`／`1290567163`）へリダイレクトすることを直接確認した．これは
GitHub 上の正規の rename であり，番号空間が偶然一致した別リポジトリではない．
したがって旧名トークンの単純置換のみで十分であり，番号のクロスウォークは不要
（`scripts/extract_chatgpt_export.py` の `REPO_ALIAS`）．

## `authorization_present` の演算子的定義と実証された限界

`authorization_present ∈ {yes, not-found, n/a, yes-rejected}`．`no` は返さない
（保守的定義）．`yes` の条件: `created_at` より**厳密に早い** user ロールの
メッセージが，一致したメッセージの祖先チェーン **または** 会話の live path
（`current_node` の祖先）のいずれかに存在し，かつそのメッセージが指示動詞語彙
（JP: 起票／投稿／作成／コメント／レビュー／提出／報告／依頼／お願い，EN:
post/create/comment/review/open an issue/file an issue/submit/reply/publish/
request review/@codex）にヒットし，かつ artifact の repo に言及していること
（`url_refs`／`text_mentions` の URL・`repo#number` 形，またはベアな repo 名
言及 `bare_repo_mentions` のいずれか）．`n/a` は `reconstructed` と
`unmatched`（単一の一致メッセージが存在しない）に付く．

`yes-rejected` は `AUTHORIZATION_SPOT_CHECK_OVERRIDES`
（`scripts/join_connector_linkage.py`）による上書きで，人手の spot-check が
機械判定の `yes` を**反証した**行に付く．反証した理由は消える方（`not-found`
への書き換え）でも黙って残す方（`yes` のまま）でもなく，反証されたという事実
自体を公開成果物に残す（PR #82 独立レビュー指摘）．

### 開発の経緯: `bare_repo_mentions` 追加（PR #82 独立レビュー指摘）と，その結果判明した規模

初版は `url_refs`／`text_mentions`（URL または `repo#number` 形が必要）のみを
authorization の repo 言及判定に用いていたため，「KSE2026 に issue を作成して」
のような URL も番号も伴わない自然文の指示を体系的に見落としていた（独立レビュー
指摘）．`bare_repo_mentions`（メッセージごとの，候補選定と同じベア部分文字列
一致）を authorization にも persist・使用するよう修正した結果，`yes` は
**全 618 行中 3 行から 131 行（反証後）** へ増加した．**注意: 131 は
connector-routed universe（174 行）ではなく全 618 行（`pr_review` 444 行を
含む）に対する数である．** `pr_review` は connector 経由か否かを判定できず
universe から除外されている（後述）にもかかわらず，131 のうち **77 行は
`pr_review`** であり，authorization の判定自体は universe 外の行にも等しく
行われる（`compute_authorization` はどの artifact_kind にも同じ規則を適用
する）ため，このような集計が生じる．**connector-routed universe（174 行）
だけに絞ると，`yes` は 54 行（31.0%），`yes-rejected` は 4 行（内訳は下記）．**
内訳は次の通り．

- 修正直後（反証前）の `yes` は 134 行．うち 3 行は既存の overrides（前述，
  `KSE2026 issue_creation #61` と `pr_review #59` の 2 件）でそのまま
  `yes-rejected` を維持．
- 残る 131 行は，**祖先チェーン探索の性質上わずか 10 通りの起点メッセージ**
  （7 会話）に収斂する: 1 会話内の複数 artifact が，同一の早い時点の指示を
  「一致メッセージの祖先または live path 上で最初に見つかる条件充足メッセージ」
  として共有するため（設計通りであり バグではない）．したがって **10 件の
  起点メッセージすべてを人手で全数確認した**（`--with-text-preview`）．これは
  「131 行を個別に読む」ことと同値の被覆率である．

| 起点メッセージ（先頭 8 桁） | 該当行数 | 内容の要約（カテゴリのみ，逐語引用なし） | 判定 |
|---|---:|---|---|
| `94cb6e66` | 51 | PR への追記コメント依頼＋関連 repo の参考共有 | 無条件・是認 |
| `b0fc67db` | 29 | 新規 PR の監視・批判的レビュー・コメント・クリーンなら merge 承認，という標準作業指示 | 無条件・是認 |
| `134949e3` | 17 | repo 全体監査の依頼．**「まだ issue 化はせず，いったん報告してください」と issue 化を明示的に保留** | **条件付き**（下記） |
| `2c8fdbe1` | 12 | repo 全体の公開前最終レビュー依頼 | 無条件・是認 |
| `4e42d807` | 10 | Lean 形式化品質の敵対的レビュー依頼 | 無条件・是認 |
| `7819fec3` | 9 | rename 決定の通知を issue として依頼（issue 化を明示的に**指示**） | 無条件・是認 |
| `993b92a3` | 3 | rename 後の事後レビュー依頼．**「起票する前に私にまず報告してください」と issue 化を明示的に保留** | **条件付き**（下記） |
| `073a9560` | 1 | 進捗確認とコメントの示唆 | 無条件・是認（弱い間接指示） |
| `863b6eac` | 1 | 完了報告の精査依頼 | 無条件・是認 |
| `bbb2118c` | 1 | 進捗確認・報告依頼 | 無条件・是認 |

**条件付き 2 件（`134949e3`／`993b92a3`，計 20 行）の扱い**: どちらも
「issue 化はまず保留し，報告を先に」という文言を含む．該当 20 行の artifact_kind
を確認したところ，`issue_creation` が 3 件（`leray-hopf#178`，
`leray-hopf-notes#100`，`leray-hopf-notes#63`）含まれていた．これらは
起点メッセージが明示的に保留した行為そのもの（issue 作成）と直接矛盾するため，
最初の 3 件と同型の誤検出として `AUTHORIZATION_SPOT_CHECK_OVERRIDES` に追加し
`yes-rejected` とした．残る 17 行（comment／review／PR 作成）は，保留された
行為（issue 化）とは異なる action_kind であり，機械的には矛盾しない．しかし
「報告を待ってから」という文脈全体がそれ以外の行為にも及ぶ可能性は文面だけでは
排除できず，**確信を持って是認とも反証ともしない**（`yes` のまま残すが，本節
に解釈上の未決着として記録する）．

**残る限界**:
1. 本語彙は否定を検出できない（実証済み: 本ラン（`bare_repo_mentions` 反映後）
   で機械的に `yes` と判定された候補は全 618 行中 `yes` 131 ＋ `yes-rejected` 6 の
   計 137 件．うち 6 件（4.4%）が人手確認で明確な反証を要した）．
2. `bare_repo_mentions` を含めたことで recall は改善したが precision は低下した:
   「repo 名＋指示動詞が同一会話のどこかに，時系列で先行して存在する」という
   条件は，**その指示が当該 artifact を具体的に指していたことを要求しない**．
   `yes` 判定は「関連する先行指示が存在した」ことの証拠であって，
   「その特定の書き込みを著者が個別に事前承認した」ことの証拠ではない．
   後者を機械的に判定する手段は本データにはない．
3. 祖先チェーン探索に時間的な上限（window）がない．遠い過去の一度きりの
   standing instruction が，何十件もの後続 artifact の `yes` を生み出し得る
   （上表の通り，実際に生じている）．
4. **母集団の取り違えに注意（PR #84 独立レビュー指摘，本節で訂正済み）**:
   `authorization_present` は connector-routed universe（174 行）に限らず
   全 618 行（`pr_review` 444 行を含む）に対して等しく計算される．issue #70 の
   Q3（「明示的な事前指示に遡れる `t-uda` 投稿の割合」）が問うのは
   **connector-routed universe** の分母であり，これは **54／174（31.0%，
   加えて `yes-rejected` 4／174）** である．全 618 行に対する 131／618 という
   数値は，`pr_review`（connector 経由か否かを判定できず universe から除外
   されている）77 行の `yes` を含むため，Q3 の分母としては使えない．
   下記の連携先ドキュメントを引用する際は必ず **54／174（31.0%）** の方を使う．
   これは開発時の初版（3 件から 134 件への増加時点）で見誤り，`131／174` と
   誤記した数値であり，本節と `provenance/ai-use.md` の該当行を訂正した．
   31.0% は当初の 3 件 (1.7%) よりは大きいが，誤って報告していた 75.3% ほど
   大きくはない．著者の役割モデル・mediation census・本文の既存記述へ
   反映するかどうかは，別途著者レビューを要する（issue #70 の non-goals:
   「Broad manuscript rewriting」）．本ドキュメントは所見の記録に留める．

**したがって: 本パイプラインが将来再実行されるたびに，未収載の `yes` 行は
必ず人手で再確認しなければならない．** `AUTHORIZATION_SPOT_CHECK_OVERRIDES`
は append-only の履歴であり，新しい `yes` を自動的にフィルタしない．

## セッションログ被覆窓（gate criterion 2）への寄与

セッションログの裏付けが皆無であった 3 つの窓（T2: 2026-06-20T04:24–12:49Z，T4: 2026-07-16T15:09–16:17Z，
T3: 2026-07-19 終日）のいずれについても，本エクスポートの候補会話メッセージが
時刻的に窓の内側に落ちる．具体例（`evidence/metrics/connector-linkage.csv` の該当行，
tier: time-and-context，confidence: medium）:

- T2: `leray-hopf` issue_creation/issue_comment #10/#11/#12（2026-06-20T11:21:41Z）
  および #14/#15（11:29:37Z）— §4 が記す「`leray-hopf#10`–`leray-hopf#15` の
  バッチと事前照合訂正（06-20T11:20–11:43Z）」の窓に正確に収まる．
- T4: `leray-hopf` issue_creation #149–#156（2026-07-16T15:13:43Z）— §4 が記す
  バースト窓（07-16T15:09–16:17Z）の内側．
- T3: `leray-hopf` issue_comment／pr_review #175（07-19T03:25:06Z），
  `leray-hopf-notes` pr_review #93/#94（07-19T04:48:21Z）— §4 が記す 07-19 終日
  窓の内側．

これらは `evidence_type: reconstructed`（GitHub 側一次証拠と ChatGPT 側テキストの
時刻的付合であり，起草行為そのものの一次証拠ではない），confidence は該当行の
tier（time-and-context = medium）に従う．

## 生産性・因果推論の禁止

本ドキュメントおよび `evidence/metrics/connector-linkage.{json,csv}` は，投稿
チャネルとテキストの時刻的付合を機械的に集計したものであり，生産性・有効性・
因果関係を一切主張しない（PLAN.md §9 Phase 5，`mediation-census-methodology.md`
と同一の禁止事項）．`caveat_ref` 列（CSV）／`caveat`（JSON）は本ドキュメントへの
固定ポインタである．

## 限界

- **Q1 が否定的**であるため，`exact-id`／`exact-body` 以外のすべての tier は
  状況証拠である．`time-and-context` と `reconstructed` は「言及があった」ことの
  証拠であって「起草した」ことの証拠ではない．
- `exact-body` は本ランで 0 件．正規化ハッシュ照合の網が粗いのか，実際に
  assistant のドラフトが逐語で投稿されることが稀なのかは，本データからは
  判別できない．
- `authorization_present` の語彙は否定文を検出できない（上記，実測 6/137 が
  人手確認で反証済み）．また `bare_repo_mentions` 導入後は「先行する指示の
  存在」と「その artifact 個別への事前承認」を区別できない（上記，限界 2 も
  参照）．将来の未収載 `yes` は必ず手動確認を要する．
- `pr_review` は Reviews API の制約により connector 経由か否かを判定できず，
  universe から除外している．したがって本ドキュメントの coverage 数値は
  issue／PR 作成とコメントのみを対象とし，レビューの connector 帰属については
  何も主張しない．
- 候補会話の選定（`tight`/`wide` トークン一致）はベア部分文字列一致であり，
  比喩的・無関係な文脈での repo 名言及（誤検出）と，別表記（誤字・省略形）による
  見逃し（偽陰性）の両方があり得る．手動の全数検証は行っていない．
- `evidence/repository-snapshots/*` は取得時点のスナップショットであり，本ランの
  connector-routed universe サイズ（174）は今後の repo 活動でさらに増加し得る．
  再実行すれば異なる（通常はより大きい）数値になる — これは決定性の欠如ではなく，
  対象が生きているリポジトリであることの帰結である．
- 会話ツリーの分岐（edit branch，50 会話で観測）について，`authorization_present`
  の祖先チェーン探索は一致メッセージの祖先と live path の和集合のみを見る．
  live path でも一致メッセージの祖先でもない孤立した branch 上の指示は捕捉されない．
