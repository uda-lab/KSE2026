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

## CLM-002: 形式化キャンペーン（2026-06-10〜07-20，release 日終端）では，収集済みセッションログ上で確認できるだけでも output 15.1M tokens・API 換算 $6,972.83・アクティブ時間 199.1h（5 分 gap cap）の AI 計算が投入された（いずれも下界）
- Status: frozen
- Paper location: paper/sections/03-agent-workflow.tex
- Evidence: EV-0001〜EV-2126（escrow 一次記録），`evidence/metrics/usage-metrics.json`（`scripts/extract_usage.py` により再現可能）
- Notes: 一次資料は各 JSONL の `message.usage`（API レスポンス由来）．方法論・
  カバレッジ欠損（ローテーション喪失 6/10〜6/14，レビュワー側計算資源など）は
  `analysis/usage-metrics-methodology.md`．下界であることを本文でも明記する．
  キャンペーン終端は v0.1.0-rc1 release 日（2026-07-20）に固定し，07-21 以降の
  KSE2026 証跡収集・論文作業セッションは `--campaign-end` で機械的に除外
  （除外 46 レコード．issue #42 項目 4）．
  gap 閾値感度: active = 94.8h (1m) / 199.1h (5m) / 309.8h (15m)，wall-clock 総和 1,022.8h．

## CLM-003: Vertex 完成フェーズ（2026-07-02〜03 PT）の実請求は machine-wide 実測 ¥54,868（無条件）であり，escrow 上の leray-hopf 分は公表単価換算 $258.28（無条件）．leray-hopf 単独の実請求 ¥41,421〜41,796（75.5〜76.2%）は条件付き導出値である
- Status: frozen
- Paper location: paper/sections/03-agent-workflow.tex
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
- Paper location: paper/sections/01-introduction.tex, paper/sections/04-incidents.tex, paper/sections/05-discussion.tex
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

## CLM-006: 2026-07-23 時点の調査（notes/related-work.md 記載の探索条件）では，非線形流体 PDE（Navier–Stokes を含む）の存在理論の機械検証済み形式化は Lean・Coq・Isabelle/HOL のいずれにも確認できなかった（否定的・調査条件付きの主張）
- Status: frozen
- Paper location: paper/main.tex, paper/sections/01-introduction.tex
- Evidence: cite:armstrong2026degiorginashmoser, cite:miller2026vlasov,
  cite:boldo2010wave, cite:immler2012ode, cite:vandoorn2024gns;
  `notes/related-work.md`（探索語・照合した近接先行例の記録）
- Notes: **非存在の証明ではなく「調査で確認できなかった」という下界的主張**として
  書く．本文表現は "to our knowledge, no machine-checked existence theory for a
  nonlinear fluid PDE has been reported in Lean, Coq, or Isabelle/HOL" の水準に
  限定し，調査日と探索方法への脚注参照を付す．投稿直前に再検索して時点を更新する．

## CLM-007: 03 節（workflow）で述べる個別の歴史的事実（役割構成，dispatch 件数，規律・ゲートの導入時期と契機，モデル選択の推移）は，`analysis/workflow-evolution.md` の時系列表と `evidence/session-index/` の符号化 6 セッションに裏付けられた範囲に限る
- Status: frozen
- Paper location: paper/sections/03-agent-workflow.tex
- Evidence: `analysis/workflow-evolution.md`（全行 Evidence 付き時系列表），`evidence/session-index/` 6 index（EV-2076・EV-0925・EV-1669・EV-0247 ほか）
- Notes: 03 節の各主張は本 claim を経由して workflow-evolution.md / session-index の
  該当行へ解決する（本文中の `% EV-NNNN` コメントが対応行を指す）．未符号化期間の
  事実は述べない（下界主義）．2026-07-23 夜間 freeze 分 — 朝の owner 通読での
  追認対象（CLM-006 と同扱い）．

## CLM-008: 04 節（incidents）で述べる個別の incident 経緯・時刻・件数・機構の記述は，incident card INC-001〜INC-005（各 card が evidence_type と confidence を明記）に裏付けられた範囲に限る
- Status: frozen
- Paper location: paper/sections/04-incidents.tex
- Evidence: INC-001，INC-002，INC-003，INC-004，INC-005（card 内の Primary evidence が EV / snapshot へ解決）
- Notes: 04 節の各段落は本 claim を経由して該当 card へ解決する（本文中の
  `% CLAIM: CLM-008, INC-00N` タグが対応 card を指す）．card 側で reconstructed /
  medium とされた事項は本文でも同じ強度で書く（例: INC-001 の導入セッション未特定，
  INC-005 の累積カウンタ帰属限界）．2026-07-23 夜間 freeze 分 — 朝の owner 通読での
  追認対象（CLM-006/007 と同扱い）．

## CLM-009: 本 campaign の最終的な harness は，scientific scope，issue-scoped implementation，semantic statement review，Lean/kernel verification，public-declaration preservation，release attestation，resource/liveness control，evidence capture を別の責務として扱った
- Status: frozen
- Paper location: paper/sections/03-agent-workflow.tex, paper/sections/05-discussion.tex, paper/sections/06-conclusion.tex
- Evidence: EV-2076，EV-0925，EV-1669，EV-0247，INC-001，INC-002，INC-003，INC-004，INC-005，leray-hopf#158
- Notes: 個々の責務と導入時期は CLM-007/008 の一次・再構成証拠に従う．これは campaign
  終了時点の構成を合成した記述であり，全期間に同じ harness が存在したという主張では
  ない．各 control が特定の defect を観測・検出した事例は述べてよいが，生産性向上，
  一般的有効性，因果効果は主張しない．第三者向け記述は candidate recommendation とする．

## CLM-010: TauCeti は，人間が統制する roadmap と常設 review rubric の下で AI が Lean 4 数学ライブラリを著述する project として公開されている
- Status: frozen
- Paper location: paper/sections/01-introduction.tex
- Evidence: cite:tauceti2026
- Notes: `notes/related-work.md` の 2026-07-22/23 一次資料調査に基づく．書誌は
  TauCetiProject の四つの repository を照合した pinned commit
  `3a933bde5e379d3b1d4610166090f207a5a90bb2` に固定し，
  `provenance/source-inventory.md` で照合済みとする．本文では governance と
  standing rubric の存在だけを述べ，個別 control の効果は主張しない．

<!-- 以降の claim は必要に応じて追加する． -->
