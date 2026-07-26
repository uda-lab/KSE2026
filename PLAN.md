# KSE 2026 AI4Math Paper Repository Scaffold Plan

## 1. 目的

本リポジトリは，`uda-lab/leray-hopf` における Leray–Hopf 弱解存在の Lean 4 形式化について，KSE 2026 AI4Math 向け論文を作成するための独立した作業環境とする．

論文の暫定的な中心課題は，次の二点である．

1. 三次元トーラスおよび全空間上の Leray–Hopf 型弱解存在を，Lean 4 と mathlib 上で project axiom なしに形式化した学術的成果．
2. 複数の AI エージェント，オーケストレーション，役割分離，検証スキルを用いて，大規模な解析学形式化を進めた方法と，その過程で発生した重大な失敗および回復の記録．

ただし，第二点の具体的な比重と主張は，保存されている Claude Code セッションログを精査した後に確定する．現時点では，成功事例のみを選択的に記述せず，重大インシデント，誤報，設計の破綻，資源不足，復旧過程を含む実証的ケーススタディとして構成する可能性を残す．

## 2. 基本方針

論文原稿を先に固定せず，まず証跡を保存，整理，評価する．

Lean リポジトリの文書，Git 履歴，Issue，Pull Request，CI 記録，Claude Code セッションログを相互に照合し，各主張を一次資料へ遡れる状態にする．原稿中の技術的または歴史的な主張には，対応する commit，session，issue，ログ断片，または Lean declaration を割り当てる．

生ログは原則として公開 Git 履歴へ直接追加しない．認証情報，個人情報，未公開リポジトリ情報，モデル内部の不要な出力を含む可能性があるため，raw data は非公開領域に保存し，論文リポジトリにはハッシュ，manifest，編集済み抜粋，分析結果のみを格納する．

## 3. リポジトリ構成

```text
kse2026-leray-hopf-paper/
├── README.md
├── PLAN.md
├── AGENTS.md
├── .gitignore
│
├── paper/
│   ├── main.tex
│   ├── sections/
│   │   ├── 01-introduction.tex
│   │   ├── 02-formalization.tex
│   │   ├── 03-agent-workflow.tex
│   │   ├── 04-incidents.tex
│   │   ├── 05-discussion.tex
│   │   └── 06-conclusion.tex
│   ├── figures/
│   ├── tables/
│   └── references.bib
│
├── claims/
│   ├── paper-claims.md
│   ├── formalization-scope.md
│   ├── contribution-map.md
│   └── limitations.md
│
├── evidence/
│   ├── manifest.csv
│   ├── repository-snapshots/
│   ├── session-index/
│   ├── redacted-excerpts/
│   ├── incidents/
│   └── metrics/
│
├── analysis/
│   ├── project-timeline.md
│   ├── session-coding-schema.md
│   ├── incident-candidates.md
│   ├── incident-ranking.md
│   ├── workflow-evolution.md
│   └── unresolved-questions.md
│
├── provenance/
│   ├── ai-use.md
│   ├── source-inventory.md
│   ├── author-decisions.md
│   └── review-history.md
│
├── scripts/
│   ├── inventory_sessions.py
│   ├── normalize_sessions.py
│   ├── deduplicate_sessions.py
│   ├── redact_check.py
│   ├── build_timeline.py
│   ├── extract_metrics.py
│   └── verify_claim_links.py
│
├── private/
│   └── raw-sessions/       # gitignored
│       ├── vps/
│       ├── local-main/
│       └── local-secondary/
│
└── notes/
    ├── title-and-abstract.md
    ├── paper-outline.md
    ├── related-work.md
    └── reviewer-questions.md
```

## 4. セッションログ収集

ログは VPS，主 local machine，副 local machine の三系統から収集する．元ファイルを変更せず，コピー時点の SHA-256，元の絶対パス，ホスト識別子，ファイルサイズ，作成時刻，更新時刻，推定セッション ID，使用ツールまたはモデルを `evidence/manifest.csv` に記録する．

収集作業は次の順序で行う．

1. 各環境で Claude Code 関連ディレクトリとログ形式を列挙する．
2. 元ファイルを read-only として退避する．
3. ファイル単位のハッシュと manifest を生成する．
4. セッション ID，timestamp，working directory，Git commit，branch 名を抽出する．
5. 三環境間で重複または分割されたセッションを照合する．
6. secret，token，email address，private repository URL，個人名を検査する．
7. 分析用に正規化した JSONL または Markdown を生成する．
8. 公開可能な抜粋のみを `evidence/redacted-excerpts/` に保存する．

ログが欠損している期間については，Git commit，Issue，PR，`docs/STATUS.md`，handoff 文書，shell history，build log から可能な範囲で再構成する．再構成情報と一次ログを混同せず，証拠の種類と確度を明記する．

## 5. インシデント分析

各セッションを単に要約するのではなく，次の分類で出来事を符号化する．

* 数学的意味の誤り
* Lean statement と自然言語上の意図の不一致
* theorem weakening，vacuous discharge，assumption smuggling
* proof engineering の行き詰まり
* agent 間の責任境界または handoff の失敗
* build 成功報告と実際の状態の不一致
* worktree，branch，file ownership の衝突
* memory exhaustion，swap，build lock，cold build などの資源問題
* モデル選択または escalation の失敗
* 検出，隔離，修正，再発防止に成功した事例

各重大インシデントについて，次の incident card を作成する．

```text
Incident ID:
Date and environment:
Trigger:
Immediate symptom:
Underlying cause:
Affected theorem, file, or campaign:
Why existing checks failed:
How the problem was detected:
Recovery procedure:
Permanent guardrail introduced:
Generalisable lesson:
Primary evidence:
Confidence of reconstruction:
```

重要度は，影響範囲，検出困難性，回復費用，再発可能性，一般化可能性，一次資料の完全性によって評価する．

Lean ビルドのメモリー不足事例については，単なる環境トラブルとして処理せず，大規模形式化における resource-aware orchestration の問題として検討する．具体的には，full build と incremental build の区別，build serialization，warm cache，CI への過剰な依存，エージェントによる無制御な再試行が，開発の信頼性と計算資源へどのように影響したかを整理する．

## 6. 論文の主題を確定するための判断基準

ログ分析後，論文を次のいずれに近づけるかを判断する．

### A. 形式化成果中心

数学的形式化と Lean アーキテクチャを主題とし，AI エージェントは実装方法として簡潔に扱う．

### B. AI 支援形式化の方法論中心

Leray–Hopf 形式化を非自明な実証対象とし，役割分離，statement-first workflow，adversarial review，検証ゲート，資源管理を中心的 contribution とする．

### C. 重大インシデントと回復のケーススタディ

AI 支援形式化では，kernel checking や build success だけでは防げない失敗が存在することを，複数の実例と回復策によって示す．

B を主題とし，C の incident は harness design の検出範囲と限界を検討する証拠として
組み込む．incident の経過自体を論文の中心にせず，第三者が再利用できる設計原理を
先に提示する．数学的形式化成果は，論文全体の信頼性を支える中心的 artifact とする．

## 7. 暫定的な論文構成

1. Introduction
   問題設定，形式化規模，AI 支援形式化における信頼性の課題を述べる．

2. Formalization Target and Verified Results
   弱解の定義，二つの capstone theorem，正確な scope，主要な解析的難所を示す．

3. Harness Design for Agent-Assisted Formalization
   scientific authority，issue-scoped work unit，statement review，artifact ごとの検証
   gate，worktree ownership，資源管理，証跡保全を，読者が再利用できる構成として説明する．

4. Failures, Incidents, and Recovery
   代表例を，不変条件，事象，検出，対策，教訓，証拠強度の共通順序で分析する．

5. Recommendations and Limitations
   観測された設計を candidate recommendation として整理し，単一プロジェクト，
   ログ欠損，モデル更新，因果比較の欠如，人的監督の役割を同じ強度で明記する．

6. Conclusion
   大規模 AI 支援形式化に必要な，証明検査を超えた工程上の信頼性管理をまとめる．

## 8. 執筆体制

* 著者 / final editor
  数学的主張，形式化範囲，論文上の最終判断を担当する．

* Evidence curator
  セッションログと GitHub 証跡を収集し，manifest と provenance を管理する．raw log は変更しない．

* Incident analyst
  ログを時系列化し，重大事例を分類する．形式化成果への評価とは独立して作業する．

* Lean and mathematics reviewer
  論文中の自然言語主張を Lean declaration と照合する．成功を強調する記述を先に読まず，型と数学文献を独立に確認する．

* Workflow reviewer
  agent orchestration に関する主張が，単なる印象または事後合理化ではなく，ログで裏付けられているか確認する．

* Prose and format editor
  読者導線，英語表現，重複，図表，引用を調整する．内容と論旨のレビューが完了した
  後に，独立した圧縮段階で6ページ制限へ合わせる．

AI システムは著者とはせず，使用モデル，使用範囲，原稿生成またはレビューへの関与を `provenance/ai-use.md` に継続的に記録する．

## 9. 作業段階

### Phase 0: Scaffold

paper repo を private repository として作成し，ファイル構成，LaTeX build，BibTeX，lint，PDF artifact generation を整える．

### Phase 1: Evidence preservation

三環境のセッションログを収集し，raw data，hash，manifest を固定する．この段階では論文用の物語を選ばない．

### Phase 2: Timeline and incident reconstruction

Git commit，Issue，PR，ログを統合した project timeline を作成し，incident candidate を列挙する．

### Phase 3: Contribution freeze

論文で主張する contribution を3点以内に絞り，各主張を一次資料へ対応付ける．
大幅改稿で contribution の階層が変わる場合は著者の指示を記録し，
claim と contribution map を本文より先に再 freeze する．

### Phase 4: Drafting

数学的結果，harness design，incident evidence を別々に執筆し，最後に統合する．
abstract，introduction，本文，discussion，conclusion に異なる役割を与え，同じ説明を
同じ粒度で反復しない．ページ数は記録するが，内容・論旨・文章品質が確定するまで
圧縮しない．ログや repo 固有の経過は，一般化可能な設計知見へ変換する．

### Phase 5: Adversarial review

次の点を重点的に確認する．

* Leray–Hopf 弱解存在について過剰な主張がないか．
* AI エージェントの効果を因果関係として過大評価していないか．
* 失敗例を都合よく選択していないか．
* 欠損ログや不完全な再構成を事実として記述していないか．
* proprietary tool 固有の操作法を一般的方法論として誤認していないか．
* AI for Math に関心のある harness 初学者が，repo を参照せず論旨を理解できるか．
* incident の事実，導入した control，観測された効果，第三者への推奨が区別されているか．
* abstract・introduction・本文・discussion・conclusion が説明を反復していないか．
* 口語，防御的否定，装飾的列挙，ダッシュ，擬似専門語が主張を代行していないか．

### Phase 5.5: Compression and layout

内容と owner review が収束した後，6ページ上限へ圧縮する．削除候補は重複，補助的な
運用数値，本文で再利用されない分類から選び，主張の資格条件，数学的 scope，
第三者向け教訓を削らない．incident の evidence type と confidence は incident card
に保持し，本文では内部 rubric の小見出しを置かず，対応する PR と必要な資格条件を示す．

### Phase 6: Submission snapshot

論文が参照する `leray-hopf` の commit または release tag を固定し，paper source，evidence manifest，artifact link の整合性を確認する．

## 10. 完了条件

scaffold の完成条件は，次の通りとする．

* LaTeX 原稿が再現可能に build できる．
* `leray-hopf` の参照 commit が固定されている．
* 三環境のログについて，所在と収集可否が inventory 化されている．
* raw log が Git 管理対象から除外されている．
* 全ての paper claim に evidence identifier を付けられる．
* 重大インシデント候補が少なくとも一覧化されている．
* ログ分析後に論文構成を変更できるよう，原稿と証跡分析が分離されている．
* AI 利用記録と人間による最終判断の責任範囲が明示されている．
