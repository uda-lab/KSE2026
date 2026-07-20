# Paper outline — ページ配分（Phase 3 で確定）

暫定構成は PLAN.md §7．6ページ制限（IEEE conference）での配分案:

| Section | ファイル | ページ目安 |
|---|---|---|
| 1. Introduction | 01-introduction.tex | 0.75 |
| 2. Formalization Target and Verified Results | 02-formalization.tex | 1.5 |
| 3. Agent-Orchestrated Development Workflow | 03-agent-workflow.tex | 1.0 |
| 4. Failures, Incidents, and Recovery | 04-incidents.tex | 1.25 |
| 5. Verification and Governance + Discussion | 05-discussion.tex | 1.0 |
| 6. Conclusion + refs | 06-conclusion.tex | 0.5 |

注: PLAN.md §7 では Verification and Governance と Discussion は別 section だが，
ページ制約により 05-discussion.tex に統合する案を暫定採用（Phase 3 で確定し
author-decisions.md へ）．

## CFP 確認事項（2026-07-20 確認．出典: kse2026.kse-conferences.org）

- [x] **締切: 2026-07-31（extended）**．notification 08-31，camera-ready 09-10．
- [x] 書式: 「LaTeX series format as described at IEEE's website」＝ IEEE conference
      template（IEEEtran conference class で適合），**6ページ以内**．
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
