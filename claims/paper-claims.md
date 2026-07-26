# Paper claims — 主張と証拠の対応表

論文中の技術的・歴史的主張は，本文書の claim として登録してから本文に書く
（AGENTS.md 規則 4）．`make verify` が本文書と `paper/` 中の `EV-` / `INC-` 参照の
解決可能性を検査する．

## 書式

```markdown
## CLM-NNN: <一文で述べた主張>
- Status: candidate | frozen | dropped
- Paper location: sections/NN-*.tex（未執筆なら planned）
- Evidence: EV-NNNN / INC-NNN / leray-hopf@<sha> / leray-hopf#<num> /
  decl:<Lean.Name> / cite:<verified-bibkey>
- Notes: 確度，再構成か一次資料か，など
```

Phase 3（contribution freeze）で `frozen` にした claim のみ本文に残す（CLM-001〜008 は
2026-07-23 に freeze．CLM-009 は content-first 改稿指示 2026-07-24 に基づく
harness synthesis，CLM-010 は同改稿の related-work 比較を追跡する）．
contribution として掲げるのは 3 点以内（PLAN.md Phase 3）．

---

## CLM-001: Leray–Hopf 弱解存在（𝕋³ および ℝ³）が Lean 4 + mathlib 上で project axiom なしに形式化された
- Status: frozen
- Paper location: paper/main.tex, paper/sections/01-introduction.tex, paper/sections/02-formalization.tex, paper/sections/06-conclusion.tex
- Evidence: leray-hopf@7c15710a7b9068a2aa105fc7c11b432e7685b7b5, decl:exists_lerayHopf_torus3, decl:exists_lerayHopf_r3, `evidence/metrics/formalization-metrics.json`（pinned commit checkout 上で `scripts/extract_metrics.py` により実測: 96 files / 42,012 lines / theorem 1,000 + lemma 58 / 315 commits．2026-07-23）, `evidence/repository-snapshots/leray-hopf/releases.json`（release-attestation run 29714844283 と exact SHA を記録）
- Notes: 範囲の上限は claims/formalization-scope.md．kernel-only の根拠は
  exact SHA 7c15710a に対する release-attestation run 29714844283 と，その
  `#print axioms` exact-pin を含む九つの検査結果．恒久 release 記録は上記
  `releases.json` snapshot から参照できる．

## CLM-002: 形式化キャンペーン（2026-06-10〜07-20，release 日終端）では，収集済みセッションログ上で確認できるだけでも output 15.1M tokens・公表 API 単価による推定コスト $6,972.83・active session time 199.1h（5 分 gap cap）の AI 計算が投入された（いずれも下界）
- Status: frozen
- Paper location: paper/sections/01-introduction.tex, paper/sections/03-agent-workflow.tex
- Evidence: EV-0001〜EV-2126（escrow 一次記録），`evidence/metrics/usage-metrics.json`（`scripts/extract_usage.py` により再現可能）
- Notes: 一次資料は各 JSONL の `message.usage`（API レスポンス由来）．方法論・
  カバレッジ欠損（ローテーション喪失 6/10〜6/14，レビュワー側計算資源など）は
  `analysis/usage-metrics-methodology.md`．下界であることを本文でも明記する．
  キャンペーン終端は v0.1.0-rc1 release 日（2026-07-20）に固定し，07-21 以降の
  KSE2026 証跡収集・論文作業セッションは `--campaign-end` で機械的に除外
  （除外 46 レコード．issue #42 項目 4）．
  gap 閾値感度: active = 94.8h (1m) / 199.1h (5m) / 309.8h (15m)，wall-clock 総和 1,022.8h．

## CLM-003: Fable 5 再公開直後の Vertex 完成フェーズ（2026-07-02〜03 PT）の実請求は machine-wide 実測 ¥54,868（無条件）であり，escrow 上の leray-hopf 分は公表単価換算 $258.28（無条件）．leray-hopf 単独の実請求 ¥41,421〜41,796（75.5〜76.2%）は条件付き導出値である
- Status: frozen
- Paper location: paper/sections/01-introduction.tex, paper/sections/03-agent-workflow.tex
- Evidence: `evidence/metrics/vertex-completion-phase-billing.csv`・`vertex-completion-phase-billing-sku.csv`（redaction 済み集計），`scripts/extract_vertex_phase.py`（再現可能），EV-1681〜EV-2126（escrow 一次記録）
- Notes: 2 層区分（provider-billed actual / 導出値）は `analysis/cost-attribution-methodology.md`
  に従い区別して書く．**条件**: 実効レート区間 [160.4, 161.8] ¥/$ の下界側は，
  Cloud Monitoring `token_count` の実測積分が escrow の
  input+output+cache_read+cache_write 合算と同一母数であるという metric 解釈に
  依存する．現行 raw export にはラベル内訳（`type`／`explicit_caching`）が残って
  おらず，この解釈は既存データからは検証できないため，本文・脚注では
  「当該 metric 解釈の下での導出」と明示する（issue #42 項目 3，owner 判断
  2026-07-23）．上界 161.8（残差非負性のみに依存）と ¥54,868・$258.28 は
  この条件に依存しない．方法・限界は `analysis/billing-reconciliation.md`．
  raw export は Git 外（sha256 記録済み）．

## CLM-004: purposive に選んだ符号化 6 セッションの記述統計として，WEAKEN/STMT-MISMATCH 系 4 件・RECOVERY 19 件・RESOURCE 12 件・WT-CONFLICT 5 件が観測され，FALSE-SUCCESS（イベント符号: 実行時の成功報告と disk 状態の不一致の残存）は観測されなかった
- Status: frozen
- Paper location: paper/sections/03-agent-workflow.tex, paper/sections/04-incidents.tex, paper/sections/05-discussion.tex
- Evidence: `evidence/session-index/` の 6 index（EV-0247，EV-0925，EV-1669，EV-2076 ほかを一次資料とする符号化），`analysis/session-coding-schema.md`
- Notes: 母集合は purposive sample（符号化済み 6 セッション）であり，全キャンペーンの
  悉皆標本でも無作為標本でもない — 本文で必ず明示し，prevalence・failure rate・
  guardrail effectiveness の推定には使わない（issue #42 項目 2）．
  FALSE-SUCCESS 非観測は，commit 前 disk 再検証や独立 adversarial review の規律と
  *consistent with* の関係にあると述べるにとどめ，帰結（因果）としては主張しない．
  イベント符号 FALSE-SUCCESS はセッション内の実行時報告に関する定義であり，
  incident 分類の `false-success-report`（文書・記録上の虚偽主張，例: INC-001 の
  「statement intact」記載）とは別概念（session-coding-schema.md の定義注記参照）．

## CLM-005: 同型の statement-scope blind spot について，release 直前の監査まで残存した例（INC-001）と，構造的審査と数値診断により無制約 signature をマージ前に棄却し，制約付き statement を Lean で証明した例（INC-002）が同一プロジェクト内に併存する — この対は独立 statement 検査の価値と整合的（consistent with）な対照例である
- Status: frozen
- Paper location: paper/sections/01-introduction.tex, paper/sections/03-agent-workflow.tex, paper/sections/04-incidents.tex, paper/sections/05-discussion.tex
- Evidence: INC-001，INC-002，EV-0925，leray-hopf#27，leray-hopf#158
- Notes: 観測事実（INC-001 では pre-release audit まで検査されず残存した／INC-002
  では構造的審査が projection 仮定の欠落を特定し，数値評価が診断を補強した）と
  反実仮想（検査さえあれば必ず防げた）を分離し，後者は主張しない
  （issue #42 項目 2，PLAN.md Phase 5 の過大評価チェックに対応）．本文の英語は
  `a contrast consistent with the value of independent statement review` 程度の
  観測的表現とする．INC-002 の近似値は certified counterexample ではなく
  corroborative diagnostic としてのみ扱う．INC-001 側で検査が「行われなかった」
  期間の記録が一次資料
  （EV-0925 の consumer verdict 過程）にある点が対比の根拠．

## CLM-006: 2026-07-23 時点の先行研究調査では，3 次元 Navier–Stokes 方程式に対する Leray–Hopf 弱解存在定理の先行する machine-checked formalization を確認できなかった（否定的・調査条件付きの主張）
- Status: frozen
- Paper location: paper/main.tex, paper/sections/01-introduction.tex
- Evidence: cite:armstrong2026degiorginashmoser, cite:miller2026vlasov,
  cite:boldo2010wave, cite:immler2012ode, cite:vandoorn2024gns;
  `notes/related-work.md`（探索語・照合した近接先行例の記録）
- Notes: 本文は "To our knowledge, no prior machine-checked formalization
  establishes Leray--Hopf weak solution existence for the three-dimensional
  Navier--Stokes equations." の水準に限定する．調査手順や非存在証明ではないという
  防御的説明は本文に置かない．投稿直前に再検索して時点を更新する．

## CLM-007: 03 節（workflow）で述べる個別の歴史的事実（役割構成，dispatch 件数，規律・ゲートの導入時期と契機，モデル選択の推移）は，`analysis/workflow-evolution.md` の時系列表と `evidence/session-index/` の符号化 6 セッションに裏付けられた範囲に限る
- Status: frozen
- Paper location: paper/main.tex, paper/sections/01-introduction.tex, paper/sections/03-agent-workflow.tex, paper/sections/05-discussion.tex, paper/sections/06-conclusion.tex
- Evidence: `analysis/workflow-evolution.md`（全行 Evidence 付き時系列表），`evidence/session-index/` 6 index（EV-2076・EV-0925・EV-1669・EV-0247 ほか）
- Notes: 03 節の各主張は本 claim を経由して workflow-evolution.md / session-index の
  該当行へ解決する（本文中の `% EV-NNNN` コメントが対応行を指す）．未符号化期間の
  事実は述べない（下界主義）．2026-07-23 夜間 freeze 分 — 朝の owner 通読での
  追認対象（CLM-006 と同扱い）．

## CLM-008: 04 節（incidents）で述べる個別の incident 経緯・時刻・件数・機構の記述は，incident card INC-001〜INC-005（各 card が evidence_type と confidence を明記）に裏付けられた範囲に限る
- Status: frozen
- Paper location: paper/main.tex, paper/sections/01-introduction.tex, paper/sections/04-incidents.tex, paper/sections/05-discussion.tex
- Evidence: INC-001，INC-002，INC-003，INC-004，INC-005（card 内の Primary evidence が EV / snapshot へ解決）
- Notes: 04 節の各段落は本 claim を経由して該当 card へ解決する（本文中の
  `% CLAIM: CLM-008, INC-00N` タグが対応 card を指す）．card 側で reconstructed /
  medium とされた事項は本文でも同じ強度で書く（例: INC-001 の導入セッション未特定，
  INC-005 の累積カウンタ帰属限界）．2026-07-23 夜間 freeze 分 — 朝の owner 通読での
  追認対象（CLM-006/007 と同扱い）．

## CLM-009: 本 project の最終 harness は，scientific owner の権限下で repository-local `github-driven-workflow` が GitHub Issue・専用 branch/Git worktree・GitHub PR を接続した．Issue scope，review decisions，merge authority は agent session 内だけでなく repository と GitHub の artifact に記録された．Fable は 7 月 2〜3 日に Vertex AI 経由で，これらの artifact から既存 workflow の orchestration を再開した．semantic statement review，Lean/kernel verification，public declaration preservation，VPS container の resource/liveness control，evidence capture は別の責務として扱われた
- Status: frozen
- Paper location: paper/main.tex, paper/sections/01-introduction.tex, paper/sections/03-agent-workflow.tex, paper/sections/05-discussion.tex, paper/sections/06-conclusion.tex
- Evidence: EV-2076，EV-0925，EV-1669，EV-0247，EV-1681〜EV-2126，INC-001，INC-002，INC-003，INC-004，INC-005，leray-hopf#158
- Notes: 個々の責務と導入時期は CLM-007/008 の一次・再構成証拠に従う．これは campaign
  終了時点の構成を合成した記述であり，全期間に同じ harness が存在したという主張では
  ない．各 control が特定の defect を観測・検出した事例は述べてよいが，生産性向上，
  一般的有効性，因果効果は主張しない．Fable の再開は session 外へ project state を
  記録した設計の観測例であり，model independence 自体を contribution としない．
  第三者向け記述は candidate recommendation とする．

## CLM-010: TauCeti は，人間が統制する roadmap と常設 review rubric の下で AI が Lean 4 数学ライブラリを著述する project として公開されている
- Status: frozen
- Paper location: paper/sections/01-introduction.tex
- Evidence: cite:tauceti2026
- Notes: `notes/related-work.md` の 2026-07-22/23 一次資料調査に基づく．書誌は
  TauCetiProject の四つの repository を照合した pinned commit
  `3a933bde5e379d3b1d4610166090f207a5a90bb2` に固定し，
  `provenance/source-inventory.md` で照合済みとする．本文では governance と
  standing rubric の存在だけを述べ，個別 control の効果は主張しない．

## CLM-011: Lean Eval は，benchmark statement・supplied dependencies・trusted scaffolding を generated workspace 側で固定し，submitted solution が comparator に受理されるかで問題を採点する theorem-completion benchmark として公開されている
- Status: frozen
- Paper location: paper/sections/01-introduction.tex
- Evidence: cite:leaneval2026repo, cite:leaneval2026site
- Notes: 2026-07-25 に issue #71 対応として `leanprover/lean-eval` README と
  `https://lean-lang.org/eval/problems/` を実読して照合した．2026-07-25 の
  review follow-up chat で owner (`t-uda`) が本 claim を freeze するよう指示した．
  本文では task 粒度と trusted workspace の固定だけを述べ，個別 leaderboard
  成績や repository-scale の完全形式化とは同一視しない．

## CLM-012: 記録された著者向け経路では scientific owner が最終権限を保持し，ChatGPT は中間的な decision-support 層として再構成される（confidence: 中）一方，owner-authorized な項目の GitHub Connector による Issue / PR への伝送は一次記録されており，ChatGPT の起草や独立した意思決定までは証明しない
- Status: frozen
- Paper location: paper/sections/03-agent-workflow.tex
- Evidence: EV-2076, EV-0925, EV-1669, EV-0247, INC-001, leray-hopf#145, leray-hopf#146, leray-hopf#158
- Notes: `analysis/author-interface-model.md` A2--A3 に基づく．`performed_via_github_app`
  は伝送チャネルを直接示すが，文面の起草者を示さない．Issue／PR の調査・統合・
  推奨・起草を ChatGPT に帰属する部分は reconstructed / confidence 中とし，
  prompt・モデル版・session・編集履歴は復元不能である．owner の最終権限と
  ChatGPT／Connector の独立権限不在を混同しない．2026-07-25 の PR #78 review
  follow-up で本文へ binding した．本 claim が述べる owner 権威は伝送チャネルと
  アカウント水準の方針に関するものであり，個別の書き込みへの事前承認の証拠強度は
  CLM-013 が別に扱う（claim 文は変更しない．issue #85）．

## CLM-013: connector 経由の Issue／PR 書き込みが owner 権威を持つのはアカウント水準の記録済み方針によるのであって，書き込みごとの事前承認の記録によるのではない．export の可視テキストから先行する repo 特定の指示を確認できたのは connector-routed universe 174 件中 54 件（31.0%）にとどまる
- Status: frozen
- Paper location: paper/sections/05-discussion.tex
- Evidence: `analysis/author-interface-model.md` §0・§8，`analysis/connector-linkage-methodology.md`（`authorization_present` の演算子的定義と実証された限界），`evidence/metrics/connector-linkage.csv`（`scripts/join_connector_linkage.py` により再現可能．内訳: `yes` 54／`yes-rejected` 4／`not-found` 27／`n/a` 89＝174），leray-hopf#178（spot-check が機械判定を反証した `yes-rejected` 行の一例），EV-2076，EV-0925，EV-1669，EV-0247
- Notes: evidence_type: reconstructed，confidence: 中．**権威と個別事前承認を分離する**
  ための claim であり，前者（authenticated `t-uda` アカウントからの書き込みは記録済み
  owner policy の下で owner 権威）は settled として再オープンしない（issue #70，
  `analysis/author-interface-model.md` §0）．本 claim が限定するのは後者だけである．
  母集団は connector 経由と判定できる 174 行であり，経路を判定できない `pr_review`
  444 行は universe から除外する．全 618 行に対する `yes` 131 件を 174 で割った
  「75.3%」は issue #83／PR #84 で訂正済みの誤記であり，本 claim では用いない．
  signal 自体の限界: 指示動詞語彙は否定文を検出できず（手動 spot-check が 4 件を
  universe 内で反証した），祖先チェーン探索に時間的上限がないため，遠い過去の
  standing instruction 一つが後続の多数の artifact を `yes` にし得る（全 618 行の
  生存 `yes` 131 件は 10 通りの起点メッセージに収斂した）．したがって「先行指示の
  存在 ≠ 個別事前承認」であり，本文もこの強度で書く．universe サイズ 174 は
  `evidence/repository-snapshots/` 取得時点の値で，再実行すれば増加し得る．
  freeze の根拠は 2026-07-26 の owner 決定（issue #85「Owner 決定」節）．
  `provenance/author-decisions.md` への対応行は PR body で提案し，適用は owner に委ねる．

<!-- 以降の claim は必要に応じて追加する． -->
