# KSE 2026 AI4Math — Leray–Hopf formalization paper

[`uda-lab/leray-hopf`](https://github.com/uda-lab/leray-hopf)（Navier–Stokes 方程式の
Leray–Hopf 弱解存在の Lean 4 + mathlib 形式化）に関する KSE 2026 AI4Math 向け論文の
作業リポジトリ．全体計画は [PLAN.md](PLAN.md)，エージェント向け作業規約は
[AGENTS.md](AGENTS.md) を参照．

## 参照対象（pinned reference）

| 項目 | 値 |
|---|---|
| Repository | `uda-lab/leray-hopf` |
| Release tag | `v0.1.0-rc1` (release-candidate build attestation, 2026-07-20) |
| Commit | `7c15710a7b9068a2aa105fc7c11b432e7685b7b5` |

正確な形式化 scope は [claims/formalization-scope.md](claims/formalization-scope.md)
に記載する．参照 commit の更新は Scientific owner の判断で行い，
`provenance/author-decisions.md` に記録する．

## ビルド

```sh
make pdf      # paper/main.tex → build/main.pdf（latexmk/pdflatex 優先，tectonic fallback）
make lint     # chktex（導入済みの場合）
make verify   # claims ↔ evidence の対応検査（scripts/verify_claim_links.py）
make clean
```

主エンジンは pdflatex（latexmk 経由，IEEE の投稿パイプラインに一致）．ローカルに
TeX 環境が無い場合は，単一バイナリの
[tectonic](https://tectonic-typesetting.github.io/)（`~/.local/bin` へ配置）で
draft ビルドできる（camera-ready は pdflatex）．CI（`.github/workflows/build.yml`）は
push ごとに PDF artifact を生成する．

## ディレクトリ

- `paper/` — LaTeX 原稿（IEEE conference 書式，6ページ制限）
- `claims/` — 論文で主張する内容と，その根拠への対応表
- `evidence/` — manifest，編集済み抜粋，incident card，メトリクス（**公開可能なもののみ**）
- `analysis/` — timeline，セッション符号化，incident 候補の分析
- `provenance/` — AI 利用記録，資料台帳，著者判断，レビュー履歴
- `scripts/` — ログ収集・正規化・検査用スクリプト（Python 3 標準ライブラリのみ）
- `private/` — **gitignored**．raw セッションログ置き場（[private/README.md](private/README.md)）
- `notes/` — 執筆用ノート

## 証拠識別子の規約

- `EV-NNNN` — 証拠アイテム．`evidence/manifest.csv` の `evidence_id` 列に対応．
- `INC-NNN` — 重大インシデント．`evidence/incidents/INC-NNN.md`（card 書式は
  `evidence/incidents/TEMPLATE.md`）．
- commit / issue / PR / Lean declaration への参照は
  `leray-hopf@<sha>` / `leray-hopf#<num>` / `decl:<Lean.Name>` 形式で書く．

`make verify` が claims と paper 中の `EV-` / `INC-` 参照の解決可能性を検査する．

## 作業状況

- [x] Phase 0: Scaffold
- [x] Phase 1: Evidence preservation（3 host 収集済: EV-0001〜EV-2145）
- [x] Phase 2: Timeline and incident reconstruction（session index 6 本，INC-001〜005，
  usage/billing 照合）
- [ ] Phase 3: Contribution freeze（進行中: 主題 B+C 統合・incident 採否・タイトルは
  issue #35 で確定済み．claim freeze = 全 CLM の frozen 化は issue #42 校正の反映後）
- [ ] Phase 4: Drafting（進行中）
- [ ] Phase 5: Adversarial review
- [ ] Phase 6: Submission snapshot
