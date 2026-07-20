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
   `make verify` を通らない参照を残さない．
5. **再構成情報と一次ログを混同しない．** ログ欠損期間の再構成には evidence type
   （primary / reconstructed）と confidence を明記する（PLAN.md §4）．
6. **AI 利用を記録する．** 原稿・分析への AI の関与（モデル，範囲，日付）は作業の
   都度 `provenance/ai-use.md` に追記する．AI は著者にしない．

## ビルドと検査

- `make pdf` — LaTeX ビルド（tectonic 優先）．原稿を触ったら必ずビルドが通ることを確認．
- `make verify` — claim ↔ evidence リンク検査．claims/ か paper/ を触ったら実行．
- `make lint` — chktex（存在する場合のみ）．
- スクリプトは Python 3 標準ライブラリのみで動くこと（依存追加は不可）．

## 原稿の規約

- 書式は IEEE conference（IEEEtran），**6ページ制限**（references 含むかは CFP 確認後に
  `notes/paper-outline.md` へ記載）．
- セクションは `paper/sections/NN-*.tex` に分割し，`main.tex` は構成のみを持つ．
- 技術的・歴史的主張を書くときは，対応する claim を `claims/paper-claims.md` に先に
  起こし，本文には `% CLAIM: CLM-NNN` コメントを付ける．
- leray-hopf の成果を記述する際は `claims/formalization-scope.md` の範囲を超える表現を
  しない（過剰主張の禁止．PLAN.md §9 Phase 5 のレビュー観点）．

## 役割分離（PLAN.md §8）

incident 分析は形式化成果の評価と独立に行う．Lean reviewer は成功を強調する記述を
先に読まず，型と数学文献から独立に確認する．単一セッションで複数役割を兼ねる場合も，
成果物（analysis/ と claims/）は役割ごとに分けて書く．
