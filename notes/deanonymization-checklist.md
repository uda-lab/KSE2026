# De-anonymization checklist — KSE 2026 投稿 artifact（issue #60 Wave B / #66）

投稿の匿名化は **owner の判断として保留**されている（`provenance/author-decisions.md`
には未記載．保留自体は決定済みであり，本書は再質問しない）．本書は，匿名化を採る場合に
**何を変える必要があるか**を列挙するだけであり，匿名化が採用されたことを前提としない．

参照するスイッチは `paper/main.tex` の `\ifanonymous`（§1）．行番号は `issue-66-author-interface`
ブランチ（`fe8fbeb` + 本 PR）時点のもの．`analysis/author-interface-model.md` の台帳は
`fe8fbeb`（本 PR 適用**前**）を基準としているため，`paper/main.tex` については両者の
行番号が一致しない．一致しないのは同ファイルのみである．

**「投稿 artifact」の範囲**: `paper/main.tex`，`paper/sections/*.tex`，
`paper/references.bib`，およびそれらから生成される `build/main.pdf`．*source-only* と
記した行は，LaTeX ソースを PDF と併せて提出する場合にのみ問題になる
（KSE 2026 の artifact／supplementary 方針は未確認．`notes/paper-outline.md`，
`analysis/unresolved-questions.md`）．

**リポジトリの可視性（`gh repo view` で確認，2026-07-25）**: `uda-lab/leray-hopf` は
**public**，`uda-lab/KSE2026` は **private**．

## 1. スイッチの設計と，その既定値がこうなっている理由

本 PR 適用前の `paper/main.tex:36` は PR #59（`fc912b9`）以降 `\author{\IEEEauthorblockN{Anonymous
Author(s)}}` であり，**byline は既に匿名**である．したがって「スイッチは現状の非匿名
出力を既定とする」という当初の想定は成立しない．今日の出力はすでに匿名側にある．

本 PR が採った設計:

- `\anonymoustrue` を既定とする．**今日の PDF を保存する**ためであり，保留中の判断を
  先取りするためではない．
- 研究費 acknowledgment は非匿名分岐に置く．文言は `provenance/author-decisions.md` で
  2026-07-22 に確定済みで，`paper/` にはこれまで挿入されていなかった．grant number は
  公開検索可能であり著者を特定しうるため，匿名分岐で抑止するのが正しい．
- `\anonymoustrue` → `\anonymousfalse` の **1 行変更**で byline と acknowledgment が
  同時に現れる．
- 非匿名分岐の実名 byline は owner が供給する必要がある．未供給のまま flip すると
  `TODO: REAL BYLINE NOT YET SUPPLIED` が誌面に出る．これは意図的で，匿名の
  placeholder のまま acknowledgment（検索可能な助成番号）だけが出るという最悪の
  組合せを黙って通さないためである．flip と byline 記入は同時に行うこと．

技術的に落とせない点が 3 つある．

1. **`\IEEEoverridecommandlockouts` が必要．** IEEEtran は conference mode で `\thanks` の
   引数を沈黙のうちに破棄する（ログに `typeout` が出るだけで警告にはならない）．
   これを宣言しないと acknowledgment は**警告なしに消える**．preamble に置いてあり，
   コマンドを再束縛するだけなので `\anonymoustrue` の下では出力に影響しない．
2. **`\thanks` は `\author{}` の引数の内側に置く．** IEEEtran は `\thanks` の本文を
   蓄積して `\maketitle` で第 1 段第 1 列の**無標**脚注として出力する．`\maketitle` の後に
   `\footnote` を置くと，本文中の番号付き脚注になってしまう．
3. `\newif` / `\anonymoustrue` / `\ifanonymous` / `\IEEEoverridecommandlockouts` の
   行末 `%` は必須．無いと ChkTeX の Warning 1（command terminated with space）で
   `make lint` が落ちる．

## 2. 漏洩箇所の一覧

「PDF に出るか」は，文字列が提出 PDF に到達するか（`.tex` / `.bib` ソースにのみ存在するか）
の区別である．

#1・#2 が指す `paper/main.tex` の箇所は本 PR 自身が書き換えた領域であり，行番号は本 PR の
途中で実際に一度移動した．そのためこの 2 件は行番号ではなく **grep で一意に引ける LaTeX
構文**を主 anchor とし，行番号は補助として括弧に添える．`\ifanonymous` と `\thanks{` は
いずれも `main.tex` 内で一意である．#3 以降が指すファイルは本 PR で変更しておらず，
行番号をそのまま anchor として用いる．

| # | 位置（anchor） | 漏洩する文字列 | 種別 | PDF に出るか | 匿名化時の対応 | スイッチで解決するか |
|---|---|---|---|---|---|---|
| 1 | `paper/main.tex` の `\ifanonymous` … `\fi` ブロック全体（現 51-62 行．実名 byline は `\else` 分岐の `\author{...}`，現 59 行） | byline | identity | 出る | `\anonymoustrue` が `Anonymous Author(s)` を出す．実名 byline は非匿名分岐にしか現れない | **する** |
| 2 | `paper/main.tex` の `\thanks{` の引数（`\else` 分岐内，現 60-61 行） | `This work was supported by JST-Mirai Program Grant Number JPMJMI22G1, Japan.` | funder | 出る（第 1 ページ脚注） | 全体を抑止．grant number は公開検索により PI と国を特定しうる | **する** |
| 3 | `paper/references.bib:6` | `author = {{uda-lab}}` | identity / repo | 出る（参考文献欄に表示） | 匿名化した組織名に置換するか，entry を落としてタグのみで参照する | しない — 個別対応 |
| 4 | `paper/references.bib:10` | `\url{https://github.com/uda-lab/leray-hopf}` | repo / identity | 出る（URL がそのまま） | URL を除去し，省略するか匿名アーカイブのリンクに置換する | しない — 個別対応 |
| 5 | `paper/references.bib:11` | `Release tag v0.1.0-rc1, commit 7c15710a` | repo | 出る | SHA は public repo に一意であり，検索すれば owner に到達する．#3・#4 を処理しても SHA を残すと漏れる | しない — 個別対応 |
| 6 | `paper/sections/01-introduction.tex:16-17` | `\cite{...,lerayhopf2026repo}` | self-citation | 出る | #3–#5 の解決後に参照先を差し替えるか落とす | しない — 個別対応 |
| 7 | `paper/sections/02-formalization.tex:16-17` | `commit \texttt{7c15710a}, tagged \texttt{v0.1.0-rc1}~\cite{lerayhopf2026repo}` | repo / self-citation | 出る | #5 と同じ | しない — 個別対応 |
| 8 | `paper/sections/02-formalization.tex:123` | `\texttt{7c15710a} under tag \texttt{v0.1.0-rc1}` | repo | 出る | #5 と同じ | しない — 個別対応 |
| 9 | `paper/sections/02-formalization.tex:6` | `% leray-hopf v0.1.0-rc1, commit 7c15710a` | repo | 出ない — *source-only* | ソース提出時に除去 | しない — 個別対応 |
| 10 | `paper/sections/02-formalization.tex:18` | `% CLAIM: CLM-001 (leray-hopf@7c15710a…)` — 40 桁 SHA | repo | 出ない — *source-only* | ソース提出時に除去．`paper/` 内で唯一の完全長 SHA | しない — 個別対応 |
| 11 | `paper/sections/02-formalization.tex:89` | `% CLAIM: CLM-001 (… measured at leray-hopf@7c15710a)` | repo | 出ない — *source-only* | 同上 | しない — 個別対応 |
| 12 | `paper/sections/02-formalization.tex:91` | `% source: leray-hopf@7c15710a docs/architecture.md` | repo | 出ない — *source-only* | 同上 | しない — 個別対応 |
| 13 | `paper/sections/04-incidents.tex:17-18` | "All PR numbers in this paper refer to the leray-hopf repository~\cite{lerayhopf2026repo}." | repo / self-citation | 出る | この一文が #14–#20 を解決可能にしている．除去するか参照先を匿名にする | しない — 個別対応 |
| 14 | `paper/sections/04-incidents.tex:38` | `PR~\#162`，`PR~\#170` | repo | 出る | 番号は public な `uda-lab/leray-hopf` で解決し owner に到達する | しない — 個別対応 |
| 15 | `paper/sections/04-incidents.tex:46` | `PR~\#170` | repo | 出る | #14 と同じ | しない — 個別対応 |
| 16 | `paper/sections/04-incidents.tex:47` | `PR~\#177` | repo | 出る | #14 と同じ | しない — 個別対応 |
| 17 | `paper/sections/04-incidents.tex:63` | `PR~\#27` | repo | 出る | #14 と同じ | しない — 個別対応 |
| 18 | `paper/sections/04-incidents.tex:76` | `PR~\#120` | repo | 出る | #14 と同じ | しない — 個別対応 |
| 19 | `paper/sections/04-incidents.tex:115` | `PRs~\#174, \#175, and \#176` | repo | 出る | #14 と同じ | しない — 個別対応 |
| 20 | `paper/sections/05-discussion.tex:32` | `PR~\#120` | repo | 出る | #14 と同じ．Section IV 以外で唯一の PR 参照 | しない — 個別対応 |
| 21 | `paper/sections/05-discussion.tex:67-68` | "available in the paper repository" | repo | 出る | 匿名化時にこの語句が `uda-lab/KSE2026` を指してはならない．なお現状は何も指せていない（§3） | しない — **owner 判断** |
| 22 | `paper/sections/03-agent-workflow.tex:34`，`paper/sections/05-discussion.tex:21` | `\texttt{github-driven-workflow}` | repo | 出る | プロジェクト固有の skill 名であり，検索により著者の公開リポジトリと相関しうる．一般名で記述するか残すかは判断事項 | しない — 個別対応 |
| 23 | `paper/sections/03-agent-workflow.tex:110-124` | 期間・JPY 建て費用・USD 費用・token 数・時間 | affiliation（弱） | 出る | JPY 建ての請求と JST 助成が併存すると著者を日本に局在させる．#2 の抑止で大半は解消するが，期間は public repo の commit 日付と一致する | 部分的（#2 のみ） |
| 24 | `paper/sections/03-agent-workflow.tex:44,117-119` | モデル名・クラウドベンダー名 | affiliation（極弱） | 出る | ベンダー名であって identity ではない．対応不要．完全性のため記載 | 該当なし |
| 25 | `paper/sections/03-agent-workflow.tex:17-20,96`，`paper/sections/04-incidents.tex:96`，`paper/sections/06-conclusion.tex:13` | VPS，コンテナのメモリー上限 | affiliation（極弱） | 出る | 環境の指紋であって識別子ではない．対応不要 | 該当なし |
| 26 | ビルド出力の `/CreationDate`，`/ModDate` | `+09'00'` のタイムゾーン offset | affiliation（弱） | 出る（PDF メタデータ） | camera-ready を `SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE` 付きでビルドするか `\pdfinfoomitdate=1` を置く | しない — **ビルド側で個別対応** |

### 検査して不在を確認した項目（対応不要）

`paper/` 配下に，メールアドレスなし（正規表現で 0 件）；session UUID なし（0 件）；
GitHub ログイン名・`KSE2026` の文字列なし（`uda` の hit は `references.bib` の 2 行のみ）；
`\IEEEauthorblockA` の所属ブロックなし；機関名・部局名・都市名なし；URL は 2 件のみ
（`references.bib:10` は漏洩，もう 1 件は第三者文献であり漏洩ではない）；
PDF メタデータの `/Author` `/Title` `/Subject` `/Keywords` はすべて空
（`hyperref` を `pdfusetitle` なしで読み込んでいるため byline が document info に
複製されない．ビルド済み PDF で確認）；`/Producer` と `/PTEX.Fullbanner` は TeX Live の
バージョンのみを開示；PDF 内にファイルパス・ユーザー名・ホスト名なし；
`paper/figures/` と `paper/tables/` は `.gitkeep` のみで画像 EXIF の面がない．

### camera-ready 時の注意（先回りの警告）

`Makefile` の `REDACT_DIRS` は `paper` を含み，`scripts/redact_check.py` はメール
アドレスを検出する．**`\IEEEauthorblockA{}` に連絡先メールを書くと
`make redact` / `make integrity` が落ちる．** また `private/redact-names.txt` に
著者名を登録している場合，実名 byline は同じ gate で落ちる．flip と同時に gate の
扱いを決めること．

## 3. artifact 可用性の齟齬（owner 判断．本 PR では決めない）

### 該当箇所

`paper/sections/05-discussion.tex:67-69`（論文の最終段落）:

> Redacted evidence excerpts, claim-to-evidence manifests, and scripts for the
> reported metrics are available in the paper repository. Raw session logs are
> withheld to protect the people and systems recorded in them.

### 確認した事実（いずれも直接検査．推測ではない）

- `uda-lab/KSE2026` は **private**（`gh repo view` および
  `evidence/repository-snapshots/KSE2026/EXPORT.json` の `private: true`）．
- `paper/` 配下に文字列 `KSE2026` は **0 件**．論文は当該リポジトリを一度も名指ししない．
- `paper/references.bib` の entry 19 件のうち，論文リポジトリに対応するものは **なし**．
  ビルド済み `.bbl` の引用キー 17 件にも該当なし．
- `paper/` 内の URL は 2 件のみで，KSE2026 の URL は存在しない．
- リポジトリ全体に `zenodo` / `doi.org` / archival の文字列は **0 件**．DOI は存在しない．
- 相互確認: `provenance/source-inventory.md` は既に `uda-lab/KSE2026` を private と
  記録し，snapshot の再現には read 権限が要ると注記している．
- `uda-lab/leray-hopf` は public であり，Lean ソース，タグ，Sections IV–V が引用する
  PR 番号を保持するが，`evidence/`・`evidence/manifest.csv`・metrics 抽出スクリプトは
  **保持していない**．

### 約束していること vs 読者が今日得られるもの

**約束**: (i) redaction 済み evidence 抜粋，(ii) claim–evidence manifest，
(iii) 報告した metric を生成したスクリプト，の 3 クラスが *available* であり，かつ
"the paper repository" という定冠詞句が，読者に指示対象を特定できることを前提している．

**今日得られるもの: 3 クラスのいずれも得られず，指示対象すら特定できない．** 独立な
2 つの失敗が重なっている — 提出 artifact 内でリポジトリが一度も名指し・引用・リンク
されていないこと，および仮に読者が leray-hopf の引用から推測しても private repo は
404 を返すこと．読者が実際に到達できるのは public な `uda-lab/leray-hopf`（Lean ソース，
release タグ，Sections IV–V の PR 番号）であり，これは形式化の claim（CLM-001）を
支えるが，evidence 手法の claim（CLM-002・CLM-003・CLM-004）を支えない．後者は
`paper/sections/01-introduction.tex` の contribution 3 が依拠する部分である．
これは `AGENTS.md` がレビューで検出するよう求めている主張と証拠強度の不一致にあたる．

**併せて訂正が要る箇所**: `scripts/redact_check.py` の public repo allowlist は
「public で citable なリポジトリ」というコメントの下に `uda-lab/KSE2026` を含んでいる．
このコメントは今日の事実と異なる．`paper/` に KSE2026 の URL を書き足すと，読者が
到達できないまま `make redact` は黙って通る．どの選択肢を採る場合でも，この
コメントを訂正するか entry を外すこと．

### 選択肢の対比（**本 PR は選択しない．当該文にも触れていない**）

| | 費用 | owner が負う継続的責務 | 匿名レビューとの関係 | `paper/` の変更 | bib の変更 |
|---|---|---|---|---|---|
| **1. `uda-lab/KSE2026` を public にする** | 機構的には小．公開対象には `analysis/author-interface-model.md` が引用する owner の生発話（`private/raw-sessions/` 由来）も含まれる点に注意．内容レビューは大 — snapshot（issue/コメント本文），`analysis/`，`provenance/`，`PLAN.md`，`AGENTS.md` 等の内部統治記録すべてに公開前点検が要る（`make redact` だけでは足りない）．`private/` は gitignored なので raw ログは既に除外 | 内部統治記録の恒久的な公開；タグを固定しない限り `main` が投稿後も動き続けること；以後の全 commit での redaction 規律 | **強く不利**．`uda-lab` 所有の public repo は即座に匿名性を破る．履歴の commit メタデータに著者名が残り，履歴を書き換えない限り除去できない．匿名化を採るなら別途 anonymized mirror が要る（保守対象が 2 つになる） | `05-discussion.tex:67-68` でリポジトリを名指しし引用する | `@misc` entry を追加し，タグを固定．加えて `provenance/source-inventory.md` に行を足す（`cite:<key>` は bib への存在と inventory の ✓ の両方を要求する） |
| **2. snapshot に archival DOI を発行する** | 中．選択肢 1 と同じ内容レビューに加え deposit 作業．Zenodo の GitHub 連携は public repo を要求するため，private のままなら curated tarball の手動アップロードになる | 不変で恒久的な引用可能 snapshot．誤りは撤回できず新バージョンで上書きするのみ．選択肢 1 の「`main` が動き続ける」問題は解決する | **注意すれば両立可能**．deposit のメタデータ（著者・所属）は投稿者の統制下にあり，レビュー時点で匿名のレコードにしうる．匿名化を後に採る場合の適合度が最も高い | 選択肢 1 と同じ一文の修正．host ではなく DOI を引用する | `doi` フィールド付きの entry と inventory 行．DOI は `\url` より安定し IEEEtran での見栄えもよい |
| **3. 読者が実際に到達できる範囲だけを述べるよう一文を弱める** | 最小．`05-discussion.tex` の 1 文のみ．リポジトリ側の作業ゼロ | なし | 中立．リポジトリ側の追加作業なしに匿名化と両立し，匿名化の判断が下りた後にどちらへも戻せる | `05-discussion.tex:67-68` の書き換え．**本 PR では実施していない**．`01-introduction.tex` の contribution 3 の記述も併せて調整が要る可能性があり，その場合は Wave C の範囲 | なし |
| **4. 請求に応じて提供する** | 最小 | 期限のない個人的義務．IEEE のデータ可用性方針でも評価が下がりつつあり，レビュー時点では誰も検証できない | 請求時点で匿名性が破れる（chair 経由でなければ）．二重盲検の期間中は実質使えない | 同じ一文の修正 | なし |
| **5. artifact を分割する** — evidence を含まない `scripts/` のみ公開し，抜粋と manifest の節を書き換える | 小〜中．`scripts/` は標準ライブラリのみの Python/shell でセッション内容を含まないため，公開前点検は軽い | 小さな恒久的公開面．evidence corpus を露出せずに metric 計算の再現性は提供できる | GitHub URL については選択肢 1 と同じ問題．ただし規模が小さくレビュー時の匿名 supplementary bundle として配布しうる | 一文を分割する．スクリプトには実在するポインタを与え，抜粋と manifest は選択肢 1–4 のいずれかに従う | スクリプト bundle の entry 1 件 |
| **6. 何もしない** | ゼロ | — | — | — | — |

何もしない場合，提出 PDF に解決不能な約束が残る．**選択は owner のものであり，
本 PR では行っていない．`paper/sections/05-discussion.tex:67-69` は未変更である．**

## 4. 併せて気づいた投稿準備上の未了事項（報告のみ，本 PR では対応しない）

1. **参考文献 5 件が未照合または要再照合．** `provenance/source-inventory.md` に
   4 件が「未」，1 件が「要再照合」（arXiv の abstract ページのみを見ており，
   引用を凍結する前に確認せよ）と記録されている．5 件とも `.bbl` に出ている．
   `paper/references.bib` の冒頭コメント自身が「投稿前に実際の刊行物と照合せよ」と
   述べている．
2. **`scripts/redact_check.py` の allowlist が `uda-lab/KSE2026` を public かつ citable と
   ラベルしている．** §3 参照．読者が追えない URL を素通りさせる live な gate である．
3. **CFP 未確認事項 2 件がいずれも hard constraint．** 参考文献が 6 ページに算入されるか，
   および二重盲検か（`notes/paper-outline.md`，`analysis/unresolved-questions.md`）．
   本文は現在ちょうど 6 ページであり，スイッチを flip して所属ブロックを足す場合の
   ページ予算に余裕がない．`\thanks` 脚注は第 1 ページの余白を消費するがページ数は
   増やさないことを実測で確認済み（§5）．
4. **`tectonic` が本コンテナに未導入**であり `Makefile` の fallback 経路は未検証．
   camera-ready は pdflatex 指定なので致命的ではないが，TeX Live のない環境では
   `make pdf` が `$(error)` で止まる．
5. **主図が未挿入．** `paper/figures/` は `.gitkeep` のみで，論文に `\includegraphics` は
   1 つもない．owner が別 issue で清書する扱い（`provenance/author-decisions.md`）．
6. **PDF のビルド時刻が再現的でない**（`/CreationDate` に実時刻と `+09'00'`）．
   一覧の #26．匿名化の判断とは独立に `Makefile` 側で直す価値がある
   （`make pdf` の出力が非決定的である点も同時に解消する）．

## 5. スイッチの実測結果

`\anonymoustrue`（本 PR の既定）と `\anonymousfalse` の両分岐をビルドして確認した結果は
PR 本文および `provenance/ai-use.md` の行に記録する．要点:

- `\anonymoustrue` の出力は本 PR 適用前の PDF と一致する（生成時刻を除く）．
- `\anonymousfalse` では acknowledgment が第 1 ページ第 1 列に無標脚注として現れ，
  ページ数は 6 のまま変わらない．
- grant number は `\mbox` で囲んである．囲まないと pdfTeX が脚注の行末で
  ハイフン分割し，助成番号が事実として誤った表記になる．
