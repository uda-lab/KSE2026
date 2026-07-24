# Review history

原稿・claims への内部レビュー（PLAN.md §8 の各 reviewer 役割，および Phase 5 の
adversarial review）の実施記録．

| 日付 | レビュー種別 | 対象 | 実施者（人間 / AI+人間確認） | 結果・指摘 | 対応 |
|---|---|---|---|---|---|
| 2026-07-20 | internal scaffold review（read-only） | PR #1（Phase 0 scaffold 全体） | Claude Opus（サブエージェント）＋人間確認待ち | approve-with-fixes．should-fix 4件（redact regex の JSON 形式 false negative / redact_check の CI 未組込 / manifest への絶対パス記録 / timeline の timezone 混在ソート），nit 4件（Python 3.10 依存・EV 採番・LOC 定義・pdflatex と Unicode 数式）．事実正確性（scope doc ↔ upstream README）・CSV quoting・.gitignore 再包含・claim 検査・PLAN 整合は clean 判定 | 8件全て同 PR 内で修正（PR #1 のレビューコメント参照） |
| 2026-07-24 | professional prose / history review（read-only，3 rounds） | issue #57 改稿後の paper 全文 | `prose-final-review`（Codex subagent，執筆担当と分離） | 1巡目は同粒度反復，Section 3/4 の incident 重複，defensive prose，process residue，語彙 drift を P1 として reject．2巡目は nominal abstraction と文書への擬人化を P1 として reject．3巡目は P0/P1 ゼロで APPROVE，残る P2 copyedit 4件も反映 | abstract/introduction/body/conclusion の機能を分離し，Section 3 を control contract に限定．口語・pseudo-technical phrasing・曖昧な指示語を除去．`Reviewed-by: prose-final-review` |
| 2026-07-24 | mathematical claim-integrity review（read-only，3 rounds + closure） | paper，claims ledger，formalization scope，contribution map，INC-002 と派生分析 | `claim-final-review`（Codex subagent，執筆担当と分離） | 1巡目で浮動小数点値を certified counterexample 相当に扱う R-D 違反を P0 として reject．billing 分類，end-state 時制，符号化担当，未登録 count，scope 上限も P1．2巡目で incident card 評価表の強い残滓を P0 として reject．3巡目は P0/P1 ゼロ，ledger P2 2件を指摘．closure check で全 finding 解消を確認し APPROVE | INC-002 を構造的審査 + corroborative diagnostic + 制約付き Lean 証明へ校正し，paper/claim/card/session index/analysis を同期．課金値，resource 検出主体，claim location，attestation evidence を訂正．`Reviewed-by: claim-final-review` |
| 2026-07-24 | intended-reader / harness architecture review（read-only，3 rounds） | paper 全文，paper outline，figure spec | `audience-harness-review`（Codex subagent，執筆担当と分離） | 1巡目は end-state と全期間運用の混同，Section 3/4 重複，暗黙的な最小 contract，図の optional gate / PR / release 境界を P1 として reject．2巡目で P0/P1 ゼロの APPROVE，P2 2件を修正．3巡目で reader clarity と architecture に finding ゼロを確認し APPROVE | worktree の説明，artifact-conditioned gate，semantic/technical feedback，review-completion record，merged state と release attestation の分離を本文と issue #58 図案へ反映．`Reviewed-by: audience-harness-review` |
| 2026-07-24 | GitHub automated PR review | PR #59 head `bed2c84` から `8e2e00a` | GitHub Copilot PR reviewer + OpenAI Codex review | event-table scope，ChkTeX coverage，Section II の単複，title status，claim marker/ledger を指摘 | table scope，lint gate，見出し，decision log，conclusion と related-work ledger を同期し，照合済み `cite:<key>` verifier を追加．各 thread に回答し，修正 head を再レビュー |
| 2026-07-24 UTC / 2026-07-25 JST | prose-lint remediation review（read-only） | `8e2e00a` 以降の再レビュー findings の修正差分 | `prose-final-review` / `claim-final-review` / `audience-harness-review`（Codex subagents） | comment を除去する前の listing state 変更と，同一行の end delimiter または inline listing pair 後の prose scan 欠落を修正．claim reviewer は初回に provenance の完了時制を指摘し，日付と pending boundary を分離 | comment stripping 後に各行を prose/listing 区間へ分割し，回帰テスト 5 件を `make lint` に追加．local review と全検査を commit 前に実施し，GitHub latest-head re-review の外部結果は PR #59 に記録 |
| 2026-07-25 | scientific owner prose / harness review | PR #59 manuscript 全文 | scientific owner | survey claim への防御文，release 証明の過剰説明，非標準的なハイフン複合語，`trajectory`，Evidence strength 小節，句読法，GitHub/VPS 用語の未定義，software ceremony 偏重，Fable と既存 workflow の時系列混同を指摘．追加自動レビューを停止し owner review へ移行 | 本文を圧縮・再構成し，`weak limit`・`velocity field`・GitHub Issue・Git worktree・out of memory (OOM) を正規化．`github-driven-workflow` は Fable 以前からの owner 提供 harness，Fable は後期の orchestrator と明記．owner 最終判断待ち |
| 2026-07-25 | scientific owner follow-up review | PR #59 Section III と関連 contribution | scientific owner | model 交代後も外部の権限・merge 規則が残るという論旨は，一般的な Claude Code 利用者には非自明でないと指摘 | Fable の交代を contribution から外し，Issue scope・review decisions・merge authority を session 外へ記録した設計と，7 月 2〜3 日の再開事例に段落を差し替え |

## Phase 5 チェックリスト（実施時にコピーして使う）

- [x] Leray–Hopf 弱解存在について過剰な主張がないか（claims/formalization-scope.md 照合）
- [x] AI エージェントの効果を因果関係として過大評価していないか
- [x] 失敗例を都合よく選択していないか（incident-ranking の不採用理由を確認）
- [x] 欠損ログや不完全な再構成を事実として記述していないか（evidence_type 照合）
- [x] proprietary tool 固有の操作法を一般的方法論として誤認していないか
- [x] abstract / introduction / body / conclusion の同粒度反復を除去したか
- [x] repo 固有識別子を概念説明の後に限定したか
- [x] incident の事象 / detection and response / lesson を区別し，内部 evidence rubric は本文に露出させず PR 番号へ接続したか
- [x] harness の end-state synthesis と campaign 全期間の歴史的事実を区別したか
