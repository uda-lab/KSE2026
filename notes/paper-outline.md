# Paper outline — content-first revision

現在の改稿ではページ配分を固定しない．各 section は次の機能を担い，内容・論旨・
owner review が収束した後に Phase 5.5 で6ページへ圧縮する．

| Section | Reader-facing function |
|---|---|
| Abstract | 問題，形式化成果，harness 方法，限定された含意を各一度だけ要約 |
| 1. Introduction | AI-for-Math 上の問題設定，先行研究，3 contribution，paper map |
| 2. Formalization | capstone，正確な scope，解析的構成，pinned build と公理検査 |
| 3. Harness Design | owner 権限，model-independent な orchestrator 役を規律する `github-driven-workflow`，Opus→Fable の交代，Git worktree，VPS コンテナ，artifact 別検査，証跡 |
| 4. Incidents | 事象→検出・対策→教訓を明示し，PR 番号へ接続する事例分析 |
| 5. Engineering Implications and Limitations | AI for Math に固有の設計知見と，因果・一般化・再現性の限界 |
| 6. Conclusion | 数学的成果と工程上の含意を一段抽象化して結ぶ |

図 #58 は Section 3 の opening overview 直後に配置する．本文は図がなくても完結させる．

## CFP 確認事項（2026-07-20 確認．出典: kse2026.kse-conferences.org）

- [x] **締切: 2026-07-31（extended）**．notification 08-31，camera-ready 09-10．
- [x] 書式: 「LaTeX series format as described at IEEE's website」＝ IEEE conference
      template（IEEEtran conference class で適合），最終稿は **6ページ以内**．
- [x] 投稿: CMT（https://cmt3.research.microsoft.com/KSE2026 ）．AI4Math session は
      本体 CFP のガイドラインを参照する形式．
- [x] proceedings は IEEE・DBLP 等へ submit（例年 IEEE Xplore）．選抜論文は
      Vietnam Journal of Computer Science 特集の可能性．
- [ ] references が 6 ページに算入されるか **明記なし**（安全側: 算入と想定）
- [ ] double-blind か **明記なし**（≥3 reviewers とのみ記載．CMT 投稿画面で確認）
- [ ] artifact / supplementary の提出可否 明記なし

### ビルド環境の方針（owner 指示 2026-07-20）

主系は TeX Live の **pdflatex + latexmk**（IEEE 投稿パイプラインと一致）．tectonic は
TeX Live の無い環境での draft 用 fallback．camera-ready は必ず pdflatex で生成する．

**数式の Unicode 方針（internal review 指摘 #8）**: leray-hopf の文書は 𝕋³/ℝ³/ν/L²
等の Unicode 数学記号を多用するが，pdflatex はソース中の Unicode 数学文字を扱えない．
本文に転記する際は必ず LaTeX マクロ（`\mathbb{T}^3`，`\mathbb{R}^3`，`\nu`，`L^2`）に
書き換える．Lean コード listing 中の Unicode は `listings` の `literate` 置換で対応
（Phase 4 で必要になった時点で main.tex に定義を足す）．
