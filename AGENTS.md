# AGENTS.md — 作業規約

## 凍結（issue #90）

**文書ドリブン開発は凍結されている．編集してよいのは `paper/` だけである．**

`paper/` 以外の追跡ファイル（`analysis/`・`claims/`・`notes/`・`provenance/`・
`evidence/`・`scripts/`・`.github/`・`README.md`・本ファイル・`Makefile`）を変更しては
ならない．これらは記録として残すが以後保守せず，相互の整合性も追わない．凍結された
文書の記述が現状と食い違っていても，**直さない**．

決定・判断・経緯の記録は GitHub の Issue と PR に残す．文書に書かない．新しい文書を
作らない．文書間の整合性を取る作業に時間を使わない．

`scripts/check_frozen_paths.sh` がこれを強制する（`make frozen`，CI の `checks`）．

## 絶対規則

1. **raw ログを Git 管理下に置かない．** raw セッションログは `private/raw-sessions/`
   （gitignored）にのみ置く．`git add -f` で `private/` 配下を追加しない．コミット前に
   `git status` で `private/` 配下や `*.jsonl` の混入がないか確認する．
2. **raw ログを変更しない．** 収集済みの元ファイルは read-only として扱う．
3. **公開領域に置けるのは redaction 済みのものだけ．** secret・token・email・未公開
   repo URL・個人名が対象．
4. **AI を著者にしない．** 最終判断は常に著者が行う．

## ビルドと検査

- `make pdf` — LaTeX ビルド．原稿を触ったらビルドが通ることを確認する．
- `make frozen` — 凍結ゲート．`paper/` 以外が変更されていないことを検査する．
- `make integrity` — claim リンク検査 + raw ログ漏洩ガード + redaction scan + 凍結ゲート．
- `make lint` — prose scanner + `check_prose_style.py` + chktex．
- `make selftest` — gate 機構自体の回帰テスト．
- commit 前に `make integrity` と `make lint` の両方を通す．

CI は `checks`（path filter なし，required check の対象．status context は `integrity`）と
`paper`（`paper/**` を変更した PR で PDF をビルド）の 2 本．path filter の付いた
workflow を required check にしない．

## 原稿の規約

- 書式は IEEE conference（IEEEtran），最終投稿は 6 ページ以内．
- セクションは `paper/sections/NN-*.tex` に分割し，`main.tex` は構成のみを持つ．
- 形式化の成果を記述する際に過剰主張をしない．
- abstract は問題・成果・方法・含意，introduction は位置づけと contribution，本文は
  定義・設計・証拠，discussion は推奨と限界を担う．同じ説明を同じ粒度で複数箇所に
  置かない．
- repo 固有の識別子より先に，数学的・工学的な概念を平易な語で説明する．
- 人物の役割は「著者（author）」で統一する．
- 散文中に ` -- ` を書かない．過剰列挙・防御的否定・口語・比喩・擬似専門語を避ける．
- 原稿を変更した PR は，実装者と別の reviewer が全文を読む．機械 lint で代用しない．
