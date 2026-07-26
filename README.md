# KSE 2026 AI4Math — Leray–Hopf formalization paper

[`uda-lab/leray-hopf`](https://github.com/uda-lab/leray-hopf)（Navier–Stokes 方程式の
Leray–Hopf 弱解存在の Lean 4 + mathlib 形式化）に関する KSE 2026 AI4Math 向け論文の
作業リポジトリ．

## 凍結（issue #90）

**文書ドリブン開発は凍結されている．編集してよいのは `paper/` だけである．**

`analysis/`・`claims/`・`notes/`・`provenance/`・`evidence/`・`scripts/`・`.github/`・
`AGENTS.md`・本ファイル・`Makefile` は記録として残すが，以後保守しない．整合性も追わない．
決定・判断の記録は GitHub の Issue と PR に残す．文書に書かない．

`scripts/check_frozen_paths.sh` が強制する．`paper/` 以外の追跡ファイルを変更した PR は
CI で落ちる．

## 参照対象（pinned reference）

| 項目 | 値 |
|---|---|
| Repository | `uda-lab/leray-hopf` |
| Release tag | `v0.1.0-rc1` (2026-07-20) |
| Commit | `7c15710a7b9068a2aa105fc7c11b432e7685b7b5` |

## ビルド

```sh
make pdf      # paper/main.tex → build/main.pdf
make lint     # prose scanner + chktex
make verify   # claims ↔ evidence の対応検査
make frozen   # 凍結ゲート（paper/ 以外が変わっていないか）
make integrity
make selftest
make clean
```

主エンジンは pdflatex（latexmk 経由）．CI は `checks`（TeX 不要，全 PR）と
`paper`（PDF ビルド）の 2 本．
