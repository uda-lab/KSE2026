# Mediation/direct census — 方法論と限界（issue #60 Wave A）

`scripts/compute_mediation_census.py` により，`evidence/repository-snapshots/{leray-hopf,KSE2026}/`
の `issues.json` / `comments.json`（`scripts/export_repo_snapshot.py`，issue #60 で
`performed_via_github_app` と `author_association` を追加）から，投稿チャネルの
機械集計を行う．出力は `evidence/metrics/mediation-census.json` と `.csv`．

## 集計方法

- **区分キー**: `(user_login, performed_via_github_app のスラグまたは null)`．
  login が `[bot]` で終わる場合は `is_bot_account = true` として区別する（投稿者
  自体が bot アカウントであるため）．
- **対象**: リポジトリ全体の issue／PR 作成（`issues.json`，`kind` を問わない）と，
  issue／PR コメント（`comments.json`，repo-wide comments endpoint）．
- **観測されたカテゴリ**: 両リポジトリとも次の 4 通りのみが出現する（ハードコード
  ではなく，データに現れた組のみを出力する）．
  1. `uda-lab-agent`（`performed_via_github_app: null`）— PAT 認証プロセスによる
     直接投稿．
  2. `t-uda`（`performed_via_github_app: null`）— 同上，owner アカウント名義．
  3. bot アカウント（`chatgpt-codex-connector[bot]`）— bot 自身が投稿したコメント．
  4. `t-uda` かつ `performed_via_github_app: chatgpt-codex-connector` — ChatGPT
     Connector 経由で `t-uda` 名義に投稿されたコメント／issue．

## 主要結果（2026-07-24 実行時点，`fetched_at` は各 snapshot の EXPORT.json 参照）

コメント，`performed_via_github_app` 別:

| repo | uda-lab-agent / null | t-uda / null | bot | t-uda via connector |
|---|---:|---:|---:|---:|
| uda-lab/leray-hopf | 190 | 146 | 69 | 37 |
| uda-lab/KSE2026 | 21 | 37 | 6 | 5 |

Issue／PR 作成:

| repo | uda-lab-agent / null | t-uda / null | t-uda via connector |
|---|---:|---:|---:|
| uda-lab/leray-hopf | 132 | 31 | 32 |
| uda-lab/KSE2026 | 54 | 1 | 6 |

leray-hopf の connector 経由 issue／PR 番号（32 件，`#1` は起業 issue を含む）:
`#1 #10 #11 #12 #13 #14 #15 #64 #82 #106 #145 #146 #147 #148 #149 #150 #151`
`#152 #153 #154 #155 #156 #157 #158 #177 #178 #184 #187 #188 #189 #191 #195`．

KSE2026 の connector 経由 issue 番号は `#23 #42 #58 #59 #60` に加え，本 issue #60
の作業中に作成された `#61` を含む 6 件（KSE2026 の件数は作業継続中のため増加し得る
— 本表は `evidence/metrics/mediation-census.json` の `fetched_at` 時点の値であり，
再実行すると増える．増加そのものが「連続的に issue が作成される」という運用の事実
であって，集計誤りではない）．

## 下界であることの注記（数値を引用する箇所には必ず併記する）

`performed_via_github_app: null` は，直接的な人間による執筆・投稿を証明しない．
gh CLI，オーケストレータ，harness など PAT を保持する任意のプロセスも null を
返す．実例: KSE2026 PR #59 で `t-uda` 名義で投稿された agent 生成コメント
（「Final proposal gate for head…」「@codex please review this PR」）は，いずれも
`performed_via_github_app: null` である．

逆に，`performed_via_github_app` が non-null（connector 経由）であることは，
**伝送チャネル** の証明に過ぎない．文面を誰が作成したか，人間が投稿前に読んだかは
この情報からは分からない．クライアント，user-agent，IP，session id，モデル
バージョン，プロンプトは本データから復元できない．コメントの編集履歴は遡って
取得できず，削除済み・minimize 済みコメントは export に含まれない．

以上より，本集計から生産性・有効性・因果関係を推論しない（PLAN.md §9 Phase 5）．

## 公開性の非対称性

`uda-lab/leray-hopf` は public repo であり，本 census は誰でも `gh api` で再現
できる．一方 `uda-lab/KSE2026` は **private repo** であり（`EXPORT.json` の
`private: true`），本 census は read アクセス権を持つアカウントでのみ再現可能で
ある．この非対称性は，`evidence/repository-snapshots/KSE2026/EXPORT.json` の
`note` フィールドにも明記されている．

## 権威に関する立場（issue #60 governing premise）

`t-uda` アカウントから発せられた判断は，文面を ChatGPT が起草したか否かに関わらず
owner 権威である（2026-07-25 owner ruling）．本 census が示すのは伝送チャネルの
下界統計のみであり，owner 権威に対する反証ではない．「最終判断は常に scientific
owner が行う」（`provenance/ai-use.md`）および「AI は著者にしない」（`AGENTS.md`）
は本集計と矛盾しない．
