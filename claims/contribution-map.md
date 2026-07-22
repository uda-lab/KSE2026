# Contribution map

Phase 3（contribution freeze）で確定する．contribution は **3 点以内**．
各 contribution について，(a) 対応する frozen claim（CLM-NNN），(b) 先行研究に対する
差分，(c) 具体的な根拠，(d) 独立した意義，を埋める（math-claim-integrity の
contribution-list discipline に従う）．baseline の出典・照合状態は
`notes/related-work.md`（issue #42 項目 1，2026-07-23 調査）．

| # | Contribution（一文） | Claims | 先行 baseline | 具体的 gain | 独立の意義 |
|---|---|---|---|---|---|
| 1 | Leray–Hopf 弱解存在（𝕋³/ℝ³）の kernel-only 形式化を AI エージェント主体の開発体制で完遂 | CLM-001, CLM-002 | 楕円型正則性の Lean 形式化 `armstrong2026degiorginashmoser`／AI 支援の線形運動論方程式 `miller2026vlasov`／Coq 波動スキーム `boldo2010wave`・Isabelle ODE `immler2012ode`．非線形流体 PDE の存在理論は 3 大 PA に先行例なし | 非線形・発展型（Navier–Stokes）の存在定理という未形式化クラスに到達．kernel-only（project axiom 0）で release surface を CI 強制 | 形式化の到達点自体が数学的 artifact として独立に検証・再利用可能 |
| 2 | statement-first / 独立 adversarial review / 検証ゲートの agent workflow 設計と，その検出力・限界の証跡つき報告 | CLM-004, CLM-005 | TauCeti `tauceti2026`（常設 rubric pipeline だが incident 記録なし）／proving benchmark 系 `xin2025deepseekproverv2`・`yang2023leandojo`・`deepmind2025alphaproof`・`zhou2026leanatlas`（証明探索・支援ツールでプロセス報告なし） | build green・kernel 検証では捕捉できない失敗様態（プレースホルダ上の偽 statement，公開定理の無断削除）を具体機構（数値反例つき独立審査・宣言単位 byte-diff）で捕捉した事例と，捕捉に失敗した対照例を同一プロジェクト内で対提示 | 「kernel checking が保証しないもの」の実証カタログとして，AI 形式化の信頼性設計に転移可能 |
| 3 | 研究記録としてのセッションログ escrow・claim↔evidence 機械検査・コスト実測照合の方法論 | CLM-002, CLM-003 | 人間チームの工程管理 `gonthier2013oddorder`・`commelin2023abstraction`（証跡・コスト報告なし）／外形的 agentic PR 研究 `agenticprs2026security`・能力トレンド `metr2025longtasks`（内側の一次証跡なし）／TauCeti の cost 報告は review 推論のみ | 3 host escrow（EV 2,145 件）+ 再現スクリプト + 実請求 SKU 照合という「内側からの」campaign 全量報告．下界性・欠損（INC-003）・条件付き数値を明示 | AI 支援研究の evidence practice として分野非依存に再利用可能 |

論文主題の A/B/C 判断（PLAN.md §6）は issue #35 コメントで owner が B+C 統合への
GO を表明済み（2026-07-23．claim freeze は issue #42 反映後）．
`provenance/author-decisions.md` への正式転記は Phase 3 転記 PR で実施予定であり，
転記完了までは issue #35 のコメントが一次記録である．
