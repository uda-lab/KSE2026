# Contribution map

Phase 3（contribution freeze）で確定する．contribution は **3 点以内**．
各 contribution について，(a) 対応する frozen claim（CLM-NNN），(b) 先行研究に対する
差分，(c) 具体的な根拠，(d) 独立した意義，を埋める（math-claim-integrity の
contribution-list discipline に従う）．baseline の出典・照合状態は
`notes/related-work.md`（issue #42 項目 1，2026-07-23 調査）．

| # | Contribution（一文） | Claims | 先行 baseline | 具体的 gain | 独立の意義 |
|---|---|---|---|---|---|
| 1 | Leray–Hopf 弱解存在（𝕋³/ℝ³）の kernel-only 形式化を AI エージェント主体の開発体制で完遂 | CLM-001, CLM-002, CLM-006 | 楕円型正則性の Lean 形式化 `armstrong2026degiorginashmoser`／AI 支援の線形運動論方程式 `miller2026vlasov`／Coq 波動スキーム `boldo2010wave`・Isabelle ODE `immler2012ode`．非線形流体 PDE の存在理論は調査時点（2026-07-23，CLM-006 の探索条件）で 3 大 PA に確認できず | 非線形・発展型（Navier–Stokes）の存在定理という，調査で先行例が確認できなかったクラスに到達．kernel-only（project axiom 0）で release surface を CI 強制 | 形式化の到達点自体が数学的 artifact として独立に検証・再利用可能 |
| 2 | scientific authority，issue-scoped work，独立 semantic review，artifact 別 verification，worktree/resource governance を分離した agent harness と，観測された検出範囲・限界 | CLM-004, CLM-005, CLM-007, CLM-008, CLM-009, CLM-010 | TauCeti `tauceti2026`（常設 rubric pipeline）／proving benchmark 系 `xin2025deepseekproverv2`・`yang2023leandojo`・`deepmind2025alphaproof`・`zhou2026leanatlas`（主に証明探索または支援環境） | statement の意味，kernel assumption，公開 declaration の存続，release surface，runtime viability を別の artifact と control で扱い，構造的 statement 審査，declaration comparison，owner-triggered resource inspection が具体的 defect を検出した事例と，その後の standing monitoring control を記録 | 数学的 specification と proof artifact を長期 campaign で統治する構成を，incident の列挙ではなく再利用可能な harness として提示 |
| 3 | 研究記録としてのセッションログ escrow・claim↔evidence 機械検査・コスト実測照合の方法論 | CLM-002, CLM-003 | 人間チームの工程管理 `gonthier2013oddorder`・`commelin2023abstraction`（証跡・コスト報告なし）／外形的 agentic PR 研究 `agenticprs2026security`・能力トレンド `metr2025longtasks`（内側の一次証跡なし）／TauCeti の cost 報告は review 推論のみ | 3 host escrow（EV 2,145 件）+ 再現スクリプト + 実請求 SKU 照合という，収集済み証跡の全量に基づく campaign 下界報告．下界性・欠損（INC-003）・条件付き数値を明示 | AI 支援研究の evidence practice として分野非依存に再利用可能 |

論文主題は method/harness を主とし，incident を検出範囲と限界の証拠として用いる
（owner 指示 2026-07-24，issue #57）．contribution は3点を維持する．
