# 著者インターフェースと provenance のモデル

著者と ChatGPT の関係，および GitHub 上に残る書き込みの経路について，証拠が支持する
範囲を述べる．代表的な逸脱の記録は `analysis/author-interface-traces.md`．
伝送チャネルの集計は `analysis/mediation-census-methodology.md`．

## 1. 役割

判断の権限と責任は著者が持つ．ChatGPT は調査・統合・推奨・起草を担う decision
support であり，独立の権限を持たない．AI は著者にしない
（`AGENTS.md:24`，`provenance/ai-use.md:4`）．

`performed_via_github_app` は**伝送チャネルの証拠であって，文面の起草者の証拠では
ない**．したがって connector 統計を権限の所在に対する反証として扱わない．

## 2. GitHub 上の経路 4 類

記録が実際に区別できるのは次の 4 類である．判定は `performed_via_github_app` と
`user_login` の**組**で行う．

| 類 | 判定 | 注意 |
|---|---|---|
| 1. GitHub App 属性を持つ著者アカウントの書き込み | `user_login` が著者アカウントで，かつ当該 Issue／comment の `performed_via_github_app` が non-null | App 属性は伝送を示すのみ |
| 2. Codex レビュー bot | `user_login = chatgpt-codex-connector[bot]` | 類 1 に畳み込まない．別主体である |
| 3. 経路不明の著者アカウントの書き込み・formal review | `performed_via_github_app` が null，または当該 endpoint に同等フィールドが存在しない | 「不明」のまま保持する |
| 4. agent アカウントの書き込み | `user_login` が `uda-lab-agent` 等 | 別枠として保持する |

**フィールド単独では類 1 と類 2 を分離できない．** snapshot の
`issues.json`／`comments.json` で `performed_via_github_app` が non-null の行は 287 行
あり，値はすべて `chatgpt-codex-connector` の 1 種である．内訳は
`user_login = t-uda` が 174 行，`user_login = chatgpt-codex-connector[bot]` が 113 行で
あって，**同じ App 属性が著者アカウントの書き込みと bot 自身のレビューの両方に付く**．

`reviews.json`（formal review）には `performed_via_github_app` に相当するフィールドが
存在しない．したがって formal review の経路は類 3 として扱う．

`chatgpt-codex-connector` は **API レベルの識別子**であって製品名ではなく，
ChatGPT／Codex の全経路を代表するものでもない．引用する場合は
`performed_via_github_app = chatgpt-codex-connector` の形で，API フィールド値である
ことが分かるように書く．

**推論の禁止**: フィールドが null であることから ChatGPT App・`gh`・Web UI・PAT・
他 agent のいずれかを，`user_login` や文体を根拠に推論しない．

## 3. 証拠の強度

| 事項 | evidence_type | confidence |
|---|---|---|
| 伝送の帰属（上表の類の判定） | primary | 高 |
| Issue／PR の調査・統合・推奨・起草を ChatGPT に帰属すること | reconstructed | 中 |

ChatGPT 側の会話は evidence に存在しない．prompt・モデル版・session・編集履歴は
復元不能である．

## 4. 本モデルが述べないこと

- **文面を誰が起草したか．** 伝送チャネルの記録からは決まらない．
- **個別の書き込みに対する事前承認．** 「事前承認」は本 project で定義された概念では
  なく，論文では定義・推定・議論のいずれも行わない．connector 経路の linkage 解析は
  `analysis/connector-linkage-methodology.md` に留め，本文へは持ち込まない．
- **類 3 の実際の経路．** 記録が支持しないため不明とする．
