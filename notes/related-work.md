# Related work（調査済み — issue #42 項目 1，2026-07-23）

各項目は一次資料（arXiv/出版ページ・mathlib docs・リポジトリ実体）を WebFetch で
実読して照合済み．未照合・未確認の点は各所に明示する（名称から推測しない）．
bib エントリは `paper/references.bib`．確定した比較は
`claims/contribution-map.md` の baseline 列に転記済み．

## 1. TauCeti（著者指定の比較対象）

**実体**（一次資料: TauCetiProject の 4 repo を 2026-07-22/23 に実読）:
論文でも単一結果でもなく，Lean FRO と Mathlib Initiative が incubate する
**AI 著述の Lean 4 数学ライブラリ**（mathlib 下流）．コードは全て AI が書き，
人間は roadmap（`TauCetiRoadmap`，13 領域．「partial differential equations」は
項目として存在するが流体方程式への言及は取得できた範囲に無い — **unknown であり
absent ではない**）と review rubric（`TauCetiReview`，10 独立観点，うち 4 が
blocking）を統制する．論文・preprint・CITATION.cff は無い（検索・API で確認）．
書誌は pinned commit `3a933bde5e379d3b1d4610166090f207a5a90bb2`（2026-07-22 HEAD）
で固定（bib: `tauceti2026`）．

**8 軸比較の要点**（coverage: 軸 2/3/4/5/8 = addressed，軸 1 = 部分
（PDE 重複は unknown），軸 6 = 部分（`TauCetiData` は存在確認のみ・中身未検証），
軸 7 = **not addressed**）:

| 軸 | TauCeti | 本プロジェクト | 差分 |
|---|---|---|---|
| 1 project-scale | 広さ優先（13 roadmap 並行） | 深さ優先（capstone 2 定理・凍結 scope） | 最適化目標が直交．PDE 領域の重複は一次資料から不明 |
| 2 human steering | roadmap レベル（reviewer チームが「何をやるか」を統制） | claim レベル（単一著者が「何を主張してよいか」を統制，非主張リスト付き） | 統制対象が組織 vs 編集 |
| 3 役割分離 | 常設の named rubric pipeline（10 観点・4 blocking，実装と審査は別 AI） | 実装 agent と独立 adversarial reviewer の分離を incident 対（INC-001/002）で事後実証 | 事前仕様化された pipeline vs 事例で実証された分離 |
| 4 PA feedback | kernel 検証 + mathlib linter 全套 + axiom allowlist を rubric 前に機械実行 | `#print axioms` + `check-release-cone.sh`（release surface 限定 guard） | ライブラリ横断 lint vs 単一結果の release cone |
| 5 artifact governance | ライセンス/公開性 + PR 状態機械 | claim↔evidence の機械検査（EV/INC/CLM + `make verify`） | 統治対象が「プロセス状態」vs「主張の出所」 |
| 6 session 証跡保全 | `TauCetiData`（review 判定のアーカイブと記載．**中身未検証**） | raw セッションログ自体を 3 host から escrow（EV-0001〜）し一次証拠に | 判定の保存 vs 生ログの保存（TauCeti 側は視界限定） |
| 7 incident recovery | **一次資料に該当なし**（CI の crash 耐性設計はあるが，命名された incident 記録・失敗様態分類は無い） | INC card 5 枚 + 符号化スキーマ + 対照対（CLM-005） | 本プロジェクト側の独自性が最も立つ軸 |
| 8 cost reporting | `tauceti-review-costs`（review 推論コストのみ，行/PR/日次粒度，運用目的） | キャンペーン全体（実装+review），下界明示 + 実請求照合，証拠目的（CLM-002/003） | 両者とも報告あり（当初想定を訂正）．範囲と目的が異なる |

## 2. 解析学・PDE の形式化（proof assistants）

- **mathlib の現状**: Gagliardo–Nirenberg–Sobolev 不等式は形式化済み
  （`vandoorn2024gns`，ITP 2024）だが，同論文自身が「Sobolev 空間の一般理論は
  未形式化」と明記．
- **近接する 2026 年の先行研究（今回の調査で発見）**:
  - `armstrong2026degiorginashmoser` — De Giorgi–Nash–Moser 理論の Lean 形式化
    （楕円型の正則性理論．existence/発展型ではない．AI 著述とは書かれていない）．
  - `miller2026vlasov` — **最も近い先行例**．Vlasov 方程式の平均場導出の
    AI 支援 Lean 形式化（well-posedness/存在/一意性/安定性）．対象は非線形
    Vlasov 方程式であり，流体方程式ではない．単一著者が単一 AI を指揮する形態で，
    multi-agent 統治・証跡・incident 報告は無い．
- **Coq/Isabelle**: 3 次元 Navier–Stokes の Leray–Hopf 弱解存在定理に
  対応する先行形式化は見当たらない．近接例は
  `boldo2010wave`（1-D 線形波動方程式の数値スキーム収束，Coq）と
  `immler2012ode`（ODE の Picard–Lindelöf，Isabelle/HOL）．
  LeanMillenniumPrizeProblems repo は Navier–Stokes の**問題文**のみ
  （検索スニペットで確認．直接引用するなら要 WebFetch）．

**差分**: 3 次元 Navier–Stokes の Leray–Hopf 弱解存在定理に対象を限定すると，
調査範囲では先行する machine-checked formalization を確認できなかった．

## 3. 大規模形式化の工程管理

- `gonthier2013oddorder` — Odd Order Theorem（Coq，15 人・6 年）．
- `commelin2023abstraction` — Liquid Tensor Experiment の方法論論文
  （spec 駆動 blueprint，人間十数人）．

**差分**: いずれも人間チーム + blueprint．本プロジェクトは単一著者が
agent 著述の実装と独立 agent 審査を統治し，blueprint の役割は
formalization-scope.md（凍結 scope）が担う．

## 4. LLM/agentic theorem proving

`xin2025deepseekproverv2`（whole-proof RL），`yang2023leandojo`（ReProver/
premise retrieval），`deepmind2025alphaproof`（AlphaProof，Nature 2026），
`zhou2026leanatlas`（human-AI 協調環境．著者名は arXiv abstract のみ照合 —
投稿前に要再確認）．

**差分（論文で立てる主張）**: いずれも証明探索ベンチマークまたはセッション単位の
支援ツールの報告であり，**project-scale の開発プロセス**（多セッション incident
回復・statement 単位の adversarial review・キャンペーン規模のコスト照合）を
一次証跡つきで報告するものは無い．

## 5. AI-agent ソフトウェア工学の実証研究

- `metr2025longtasks` — 自律タスク時間の能力トレンド測定（フレーミング引用）．
- `agenticprs2026security` — GitHub 上の agentic PR の外形的実証研究．

**差分**: 外側（メタデータ横断）からの集計研究に対し，本プロジェクトは内側
（escrow ログ・命名 incident・請求照合）からの単一キャンペーン報告．

## 未確認事項（投稿前チェックリスト）

- [ ] `zhou2026leanatlas` の著者名を arXiv ページ本体で再照合
- [ ] LeanMillenniumPrizeProblems を直接引用する場合は repo を WebFetch で実査
- [ ] TauCetiData の中身（生ログか判定のみか）は未検証のまま —
  本文では「review 判定のアーカイブと記載されている」以上を主張しない
