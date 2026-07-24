# AGENTS.md — 本リポジトリでの作業規約

論文作業リポジトリである．コードベースではなく**証跡と原稿**を扱うため，通常の開発規約
に加えて以下を厳守する．全体計画と背景は [PLAN.md](PLAN.md)．

## 絶対規則

1. **raw ログを Git 管理下に置かない．** raw セッションログは `private/raw-sessions/`
   （gitignored）にのみ置く．`git add -f` で private/ 配下を追加することは禁止．
   コミット前に `git status` で private/ 配下や `*.jsonl` の混入がないか確認する．
2. **raw ログを変更しない．** 収集した元ファイルは read-only として扱う．正規化・
   redaction は必ず別ファイルへの出力として行う（`scripts/normalize_sessions.py`）．
3. **公開領域に置けるのは redaction 済みのもののみ．** `evidence/redacted-excerpts/`
   へ置く前に `scripts/redact_check.py` を通し，検出ゼロを確認する．secret，token，
   email，未公開 repo URL，個人名が対象．
4. **主張には証拠識別子を付ける．** `claims/paper-claims.md` の各 claim には
   `EV-NNNN` / `INC-NNN` / `leray-hopf@<sha>` / `decl:<name>` のいずれかを付ける．
   外部文献に関する歴史的主張は，`provenance/source-inventory.md` で照合済みの
   BibTeX key を `cite:<key>` として用いてよい．`make verify` を通らない参照を
   残さない．
5. **再構成情報と一次ログを混同しない．** ログ欠損期間の再構成には evidence type
   （primary / reconstructed）と confidence を明記する（PLAN.md §4）．
6. **AI 利用を記録する．** 原稿・分析への AI の関与（モデル，範囲，日付）は作業の
   都度 `provenance/ai-use.md` に追記する．AI は著者にしない．

## ビルドと検査

- `make pdf` — LaTeX ビルド（latexmk/pdflatex 優先，tectonic fallback）．原稿を触ったら必ずビルドが通ることを確認．
- `make verify` — claim ↔ evidence リンク検査．claims/ か paper/ を触ったら実行．
- `make lint` — prose scanner の unittest + `check_prose_style.py` + chktex（存在する場合のみ．
  `REQUIRE_CHKTEX=1` を付けると chktex 不在を skip ではなくエラーにする．CI はこの形で呼ぶ）．
- `make integrity` — claim リンク検査 + raw ログ漏洩ガード + 公開領域の redaction scan．
  TeX を必要としない 3 つの hard gate をまとめたもの．commit 前に **`make integrity` と
  `make lint` の両方**を通す（CI の `checks` workflow はこの 2 つを実行する）．
- スクリプトは Python 3 標準ライブラリのみで動くこと（依存追加は不可）．

CI は 2 本に分かれる．`checks`（path filter なし，TeX なし，全 PR・merge queue・
`main` への push・手動 dispatch で実行．status context は job 名の `integrity`）が
required check の対象．`paper`（`paper/**`・`Makefile`・`.github/workflows/paper.yml`
を**変更した** PR と `main` push，および手動 dispatch）が PDF をビルドする．
path filter の付いた workflow を required check にすると，該当パスを触らない PR で
status が永久に pending となり merge を塞ぐため，`paper` の `pdf` は required に
しない．削除済み workflow 由来の `paper`・`build` という context 名も picker に
残るが，これらは二度と報告されないので required にしてはならない．なお branch
protection は現状未設定であり，設定の可否は owner の判断．詳細は
[.github/workflows/README.md](.github/workflows/README.md)．

## 原稿の規約

- 書式は IEEE conference（IEEEtran），最終投稿は **6ページ以内**とする．ただし，
  内容・論旨・文章品質を確定する改稿ではページ数を合否条件にせず，圧縮は独立した
  後続段階で行う．ページ制約を理由に説明を反復したり，内容を先回りして削らない．
- セクションは `paper/sections/NN-*.tex` に分割し，`main.tex` は構成のみを持つ．
- 技術的・歴史的主張を書くときは，対応する claim を `claims/paper-claims.md` に先に
  起こし，本文には `% CLAIM: CLM-NNN` コメントを付ける．
- leray-hopf の成果を記述する際は `claims/formalization-scope.md` の範囲を超える表現を
  しない（過剰主張の禁止．PLAN.md §9 Phase 5 のレビュー観点）．
- abstract は問題・成果・方法・含意の要約，introduction は位置づけと contribution，
  本文は定義・設計・証拠，discussion は推奨と限界を担う．同じ技術的説明や列挙を
  同じ粒度で複数箇所に置かない．
- repo 固有の識別子より先に，数学的または工学的な概念を平易な語で説明する．Lean
  declaration，event code，issue/PR 番号，session ID は論旨に必要な場合だけ残す．
- incident は「守るべき不変条件／事象／検出／対策／転用可能な教訓／証拠強度」の
  順で記述し，incident の事実と一般化した推奨を同じ段落で混同しない．
- 原稿を変更した PR は，実装者と別の reviewer が全文を読み，過剰列挙，防御的否定，
  口語，比喩，擬似専門語，散文中の ` -- `，主張と証拠強度の不一致を確認する．
  `deslop-prose` 等の文脈依存レビューを機械 lint の代用にせず，両方を通す．

## 役割分離（PLAN.md §8）

incident 分析は形式化成果の評価と独立に行う．Lean reviewer は成功を強調する記述を
先に読まず，型と数学文献から独立に確認する．単一セッションで複数役割を兼ねる場合も，
成果物（analysis/ と claims/）は役割ごとに分けて書く．
