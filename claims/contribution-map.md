# Contribution map

Phase 3（contribution freeze）で確定する．contribution は **3 点以内**．
各 contribution について，(a) 対応する frozen claim（CLM-NNN），(b) 先行研究に対する
差分，(c) 具体的な根拠，(d) 独立した意義，を埋める（math-claim-integrity の
contribution-list discipline に従う）．baseline の出典・照合状態は
`notes/related-work.md`（issue #42 項目 1，2026-07-23 調査）．

| # | Contribution（一文） | Claims | 先行 baseline | 具体的 gain | 独立の意義 |
|---|---|---|---|---|---|
| 1 | Leray–Hopf 弱解存在（𝕋³/ℝ³）を Lean 4 + mathlib 上で project axiom なしに形式化 | CLM-001, CLM-002, CLM-006 | 楕円型正則性の Lean 形式化 `armstrong2026degiorginashmoser`／非線形 Vlasov 方程式の平均場導出と well-posedness の AI 支援形式化 `miller2026vlasov`／Coq 波動スキーム `boldo2010wave`・Isabelle ODE `immler2012ode`．3 次元 Navier–Stokes の Leray–Hopf 弱解存在定理は調査時点（2026-07-23，CLM-006 の探索条件）で先行する machine-checked formalization を確認できず | 対象を 3 次元 Navier–Stokes の Leray–Hopf 弱解存在定理に限定して先行例との差を示す．project axiom 0 を公理検査と公開 import 検査で確認 | 形式化の到達点自体が数学的 artifact として独立に検証・再利用可能 |
| 2 | 著者，repository-local `github-driven-workflow`，session 外に記録する project state，専用 Git worktree，専門 reviewer，VPS container の資源契約を接続した agent harness と，観測された検出範囲・限界 | CLM-004, CLM-005, CLM-007, CLM-008, CLM-009, CLM-010 | TauCeti `tauceti2026`（常設 rubric pipeline）／proving benchmark 系 `xin2025deepseekproverv2`・`yang2023leandojo`・`deepmind2025alphaproof`・`zhou2026leanatlas`（主に証明探索または支援環境） | 数学的判断を著者へ，Lean/build 修正を実装 worktree へ戻す feedback split，read-only scout と declaration comparison，dispatch 時に自動注入する資源規約を具体化．Issue scope・review decisions・merge authority を repository と GitHub の artifact に残し，各 control が検出した defect を PR 記録と incident で示す | 数学的 specification，proof artifact，公開 interface，実行環境を長期 project で統治する構成を再利用可能な harness として提示 |
| 3 | 研究記録としてのセッションログ escrow・claim↔evidence 機械検査・コスト実測照合の方法論 | CLM-002, CLM-003 | 人間チームの工程管理 `gonthier2013oddorder`・`commelin2023abstraction`（証跡・コスト報告なし）／外形的 agentic PR 研究 `agenticprs2026security`・能力トレンド `metr2025longtasks`（内側の一次証跡なし）／TauCeti の cost 報告は review 推論のみ | 3 host escrow（EV 2,145 件）+ 再現スクリプト + 実請求 SKU 照合という，収集済み証跡の全量に基づく campaign 下界報告．下界性・欠損（INC-003）・条件付き数値を明示 | AI 支援研究の evidence practice として分野非依存に再利用可能 |

論文主題は method/harness を主とし，incident を検出範囲と限界の証拠として用いる
（著者指示 2026-07-24，issue #57）．contribution は3点を維持する．
