# Mediation/direct census — 方法論と限界（issue #60 Wave A）

`scripts/compute_mediation_census.py` により，`evidence/repository-snapshots/{leray-hopf,KSE2026}/`
の `issues.json` / `comments.json`（`scripts/export_repo_snapshot.py`，issue #60 で
`performed_via_github_app` と `author_association` を追加）から，投稿チャネルの
機械集計を行う．出力は `evidence/metrics/mediation-census.json` と `.csv`．

**本ページの数値は API フィールドの正確な件数（`count_exact`）だが，著者性の
signal としては非対称であり，census（悉皆調査）ではない．** non-null な
`performed_via_github_app` は仲介の下界（LOWER BOUND）だが，null は人間直接執筆
の証明にならない．理由は「下界であることの注記」節に述べる．以下の各表もその
注記を前提として読むこと（表の直前に短い再掲を置く）．

## 集計方法

区分キーは `(user_login, performed_via_github_app のスラグまたは null, is_bot_account)`
という **API フィールドの機械的な組**であり，それ自体は誰が文面を書いたかの主張では
ない（解釈は下記「下界であることの注記」節でのみ行う）．login が `[bot]` で終わる
場合は `is_bot_account = true` とする（投稿者自体が bot アカウントであるため）．

- **対象**: リポジトリ全体の issue／PR 作成（`issues.json`，`kind` を問わない）と，
  issue／PR コメント（`comments.json`，repo-wide comments endpoint）．
- **観測された組**: 両リポジトリとも次の 4 通りのみが出現する（ハードコードでは
  なく，データに現れた組のみを出力する）．
  1. `user_login = uda-lab-agent`, `performed_via_github_app = null`
  2. `user_login = t-uda`, `performed_via_github_app = null`
  3. `user_login = t-uda`, `performed_via_github_app = chatgpt-codex-connector`
  4. `user_login = chatgpt-codex-connector[bot]`（`is_bot_account = true`），
     `performed_via_github_app = chatgpt-codex-connector`

  上記のラベルは GitHub API が返す値をそのまま転記したものであり，「直接投稿」
  「PAT 認証」「著者名義」等の解釈語をここでは使わない．null が直接的な人間執筆を
  意味しないことは下記の通り．

## 主要結果（`fetched_at` は本 census JSON（`evidence/metrics/mediation-census.json`）
が入力として自己記述する値が正: leray-hopf 2026-07-24T18:28:30Z, KSE2026
2026-07-24T18:41:10Z（`head_sha_at_fetch: fc912b92…`）．KSE2026 は census 作成 PR 内で
最初の取得から追加で 1 度再取得されている（計 2 回 fetch）．さらにその後，KSE2026
snapshot は issue #79 の再収集（2026-07-26）で前進したため，**現行 tree の
`evidence/repository-snapshots/KSE2026/EXPORT.json` は census の入力を指さない** —
census 入力の snapshot は git 履歴 `git show e65b872:evidence/repository-snapshots/KSE2026/EXPORT.json`
で参照できる．census は再計算していない）

**以下は正確な件数だが，著者性の signal としては非対称．`performed_via_github_app:
null` は人間による直接執筆を証明せず，non-null は仲介の下界だが伝送チャネルの
証明に過ぎない（詳細は次節）．**

コメント，`performed_via_github_app` 別:

| repo | uda-lab-agent / null | t-uda / null | bot | t-uda via connector |
|---|---:|---:|---:|---:|
| uda-lab/leray-hopf | 190 | 146 | 69 | 37 |
| uda-lab/KSE2026 | 22 | 38 | 7 | 5 |

Issue／PR 作成:

| repo | uda-lab-agent / null | t-uda / null | t-uda via connector |
|---|---:|---:|---:|
| uda-lab/leray-hopf | 132 | 31 | 32 |
| uda-lab/KSE2026 | 58 | 1 | 6 |

leray-hopf の connector 経由 issue／PR 番号（32 件，`#1` は最初に作成された
issue = founding issue を含む）:
`#1 #10 #11 #12 #13 #14 #15 #64 #82 #106 #145 #146 #147 #148 #149 #150 #151`
`#152 #153 #154 #155 #156 #157 #158 #177 #178 #184 #187 #188 #189 #191 #195`．

KSE2026 の connector 経由 issue 番号は `#23 #42 #58 #59 #60` に加え，本 issue #60
の作業中に作成された `#61` を含む 6 件．KSE2026 の件数は作業継続中のため本表より
増加し得る（`fetched_at` 時点のスナップショット固定値であり，再実行すると増える）．

## 下界であることの注記（数値を引用する箇所には必ず併記する）

**「直接（direct）」という語は二通りに読め，本データはこの二通りに異なる答えを
返す．下界／上界を主張する前に，どちらの意味かを明示すること．**

1. 「直接」＝ GitHub App を介さず投稿されたこと，の意味で読む場合．
   `performed_via_github_app: null` はこの性質の**正確な件数**であり，
   gh CLI，オーケストレータ，harness など PAT を保持する任意のプロセスも null
   を返すため，**人間が直接キー入力したコメント数の上界**になる（null の一部
   または全部がプロセス投稿である可能性があるため）．
2. 「直接」＝ 文面を人間が起草したこと，の意味で読む場合．null はどちらの方向
   にも境界にならない．connector 経由のコメントでも人間が文面を一字一句起草
   した可能性はあり，null のコメントでも agent が文面を生成した可能性がある．
   検証可能な一次資料: `gh api repos/uda-lab/KSE2026/issues/59/comments` を
   実行すると，comment id `5071442579`（「Final proposal gate for head…」）
   および `5065764557` / `5066112755` / `5071134565` / `5071234655` /
   `5071326489` / `5071415951`（いずれも「@codex please review this PR」）
   が，すべて `user.login = t-uda`，`performed_via_github_app = null` で
   投稿されていることを確認できる（本 PR 作成時に著者自身が上記コマンドで
   直接確認した一次資料であり，`provenance/ai-use.md` の記載に依拠したもの
   ではない）．これらの文面は定型的なワークフロー通知（review 依頼・gate
   報告）であり，null が「人間の手打ち」と「プロセス生成」の両方にまたがる
   ことを示す（ただし本データ単独では，誰または何が実際に投稿したかを証明
   できない）．

逆に，`performed_via_github_app` が non-null（connector 経由）であることは，
意味 1 の下では仲介の下界になるが，意味 2 の下では **伝送チャネル** の証明に
過ぎない．文面を誰が作成したか，人間が投稿前に読んだかはこの情報からは分から
ない．クライアント，user-agent，IP，session id，モデルバージョン，プロンプト
は本データから復元できない．コメントの編集履歴は遡って
取得できず，削除済み・minimize 済みコメントは export に含まれない．

以上より，本集計から生産性・有効性・因果関係を推論しない（PLAN.md §9 Phase 5）．

`evidence/metrics/mediation-census.csv` の各行は `count_exact` 列（この API
フィールドの組についての正確な件数であり，それ自体は下界でも上界でもないことを
列名で明示）と `caveat_ref` 列（上記の非対称性を要約し本節への固定ポインタと
する文字列）を持つ．JSON 側は `authorship_signal_caveat` フィールドに本節と
同内容を格納する（フィールド名は「下界」限定ではなく非対称性全体を指す）．

## 公開性の非対称性

`uda-lab/leray-hopf` は public repo であり，本 census は誰でも `gh api` で再現
できる．一方 `uda-lab/KSE2026` は **private repo** であり（`EXPORT.json` の
`private: true`），本 census は read アクセス権を持つアカウントでのみ再現可能で
ある．この非対称性は，`evidence/repository-snapshots/KSE2026/EXPORT.json` の
`note` フィールドにも明記されている．

## 権威に関する立場（issue #60 Wave A dispatch の前提）

issue #60 の Wave A 作業指示は，「`t-uda` アカウントから発せられた判断は，文面を
ChatGPT が起草したか否かに関わらず著者権威である」という前提の下で本 census を
作成するよう求めている．この前提そのものの正式な記録化（`provenance/author-
decisions.md` への転記や著者による確定）は本 PR の範囲外であり，未実施である
（記録化の要否は著者判断待ち）．本 census が示すのは伝送チャネルの下界統計のみ
であり，上記前提の真偽を証明も反証もしない．「最終判断は常に著者が
行う」（`provenance/ai-use.md`）および「AI は著者にしない」（`AGENTS.md`）は本集計
と矛盾しない．
