# Workflow evolution（Phase 2 で作成）

agent orchestration の体制（役割分離，statement freeze，編集権限，スキル，モデル
escalation，資源管理）が開発期間を通じてどう変化したかを，導入時期・導入契機
（多くは incident）とともに時系列で記録する．

sections/03-agent-workflow.tex の主張は本文書で裏付けられた範囲に限る
（workflow reviewer の検査対象．PLAN.md §8）．

**下界主義**: 本表は符号化済み 6 セッション（`evidence/session-index/`）と
incident card・GitHub snapshot で裏付けられた変更のみを記載する．未符号化期間
（特に 06-10〜14 の喪失期間，INC-003）の変更は記録しない．「導入時期」は
一次資料上で最初に確認できる時点であり，実際の導入がそれ以前である可能性を
排除しない．

## 時系列表

| 時期 | 変更 | 契機（incident / 判断） | Evidence |
|---|---|---|---|
| 2026-06-15 | **orchestrator は Lean を直接編集しない**（全実装を delegate）方針を明言．lean-planner（statement gate）／lean-prover・lean-coder（実装）／Codex adversarial review（soundness 最終ゲート）の 3 層構成を確立 | 設計判断（現存最古セッション冒頭から） | EV-2076（session `74aab39b`，107 dispatches: coder 47 / prover 45 / planner 12 / Explore 3） |
| 2026-06-15 | **no-smuggle statement gate**: planner が過大主張（`tendsto_id` の全称形は基底の性質上偽）を statement 段階で弱形に修正 | 同上（gate が初日から機能した実例） | EV-2076（WEAKEN 06-15T10:14） |
| 2026-06-16〜19 | **死亡 prover の disk 再検証規律**: サブエージェント異常死（計 8 回）の残骸は disk 状態を再検証してから信頼し，破損分は committed-green へ revert．commit 前 `#print axioms` exact-pin 確認と併せ FALSE-SUCCESS 0 件を維持 | prover の反復死（SSL/socket/idle-timeout）という環境 incident | EV-2076（RESOURCE 06-16〜19，補足欄） |
| 2026-06-17 | **worktree/編集権限の設計的衝突回避**: 「各 stream は自分のファイルのみ新規作成，root import はまとめて 1 回」ルール | 競合の予見（未然回避） | EV-2076（WT-CONFLICT 06-17T05:38） |
| 2026-06-19 | **local-only 運用から GitHub への移行**（`uda-lab/lean-pde`，現 leray-hopf，への push と VPS バックアップ開始）．PR ベースの `/github-driven-workflow` はこの時点では権限設定待ちで未開始（同セッション内 PR 0 件） | インフラ判断．auto-mode safety classifier の hard-block（MODEL-ESC）を owner 手動実行で回避した摩擦を含む | EV-2076（MODEL-ESC 06-19T13:54，成果欄） |
| 2026-06-20 | **独立アジュディケータ（実装と別系統の agent）による PR 単位審査**を運用．初日に PR #20 の過強 statement（`p,q<1` で証明不能）をマージ前検出 | PR 運用開始と同時（検出実績が即日発生） | EV-0925（STMT-MISMATCH 06-20T13:54）／incident 候補 #1 |
| 2026-06-21 | **構造的審査と数値診断を含む adversarial review** が projection closure 仮定を欠く `ALLOW_SORRY` signature をマージ前に棄却（差 80.7 / `Vₙ` 制約下 1e-13 は corroborative な近似値，制約付き statement は Lean で証明） | INC-002（検出成功により手法が定着） | EV-0925，INC-002 |
| 2026-06-27 | **CI からローカル検証（`lake build` + `flock` 直列化）へ切替** | GitHub Actions 課金上限到達（RESOURCE） | EV-0925（06-27T23:31）／incident 候補 #7 |
| 2026-06-29 | **レビューデーモンのモデル設定検証**: codex デーモンが未対応モデル固定でレビュー即時エラー → 設定修正・復旧確認の手順が確立 | MODEL-ESC（インフラ設定不備） | EV-0925（06-29T11:00〜12:41） |
| 2026-07-09〜10 | **5 role 構成へ拡張**: coder×2・scout（read-only 事前調査）・reviewer×2（構造審査 / 宣言単位 byte-diff 審査）．reviewer は検証専用 subagent 8 体を動的スポーン | 大規模リファクタ（12 PR）の悉皆検証需要 | EV-1639〜EV-1669（session `7e6156bf`） |
| 2026-07-10 | **宣言単位 byte-diff 悉皆レビュー**が公開定理の無断削除をマージ前検出し，以後 12 PR 全件の標準ゲートに | INC-004 | EV-1669，INC-004 |
| 2026-07-10 | **PR 監視の 3 経路化**（formal Review / bot top-level コメント / `Reviewed-by:` マーカーを全て見る `watch-pr-gates.sh`） | レビュー見落とし 19 分停滞（HANDOFF-FAIL）を user 指摘で発覚 | EV-1669（07-10T00:18〜00:43）／incident 候補 #6 |
| 2026-07-10 | **preflight の軽量化**: 中間 commit は `lake build` green のみ，フル preflight（axiom-live 込み）は最終 commit 後 1 回＋独立検証 1 回 | user の処理時間懸念 → 調査で過剰と判明 | EV-1669（07-10T10:01〜10:02） |
| 2026-07-17 | **statement card 必須化と回帰 guard の CI 組込み**（`check-statement-cards.sh`，`docs/statement-gates.md` の 3 独立 gate・adversarial substitution 要件） | INC-001（release 前 postmortem，issue #158 / PR #170） | INC-001，`evidence/repository-snapshots/leray-hopf/issues.json` |
| 2026-07-18 | **コンテナ資源管理の恒常規約**: サイドプロセス sweep・ビルド前 `available` ≥ 2GiB 確認・`.lake` ハードリンク共有・`flock` 直列化・dispatch prompt への明記・`LEAN_NUM_THREADS=1` 縮退．判断基準を `used` から `available` へ変更し閾値報告を義務化 | INC-005（OOM cascade．横展開失敗の診断から recall 非依存の注入層へ） | EV-0247，INC-005 |
| 2026-07-17 | **release surface の分離と静的 guard の CI 化**: 未完成モジュールを `LerayHopf.Experimental` へ分離し，root import の release cone を lake 非依存で検査する `check-release-cone.sh` を導入（issue #147 / PR #162）．full build は release candidate 時の 1 回に集約 | INC-001 postmortem と同日の pre-release-polish 系列 | INC-001，`evidence/repository-snapshots/leray-hopf/issues.json`（#147/#162） |
| 2026-07-20 | **manual full-build attestation による release 発行**: v0.1.0-rc1（attested release run） | release 準備（07-17 導入の政策群の帰結） | `evidence/repository-snapshots/leray-hopf/{tags,releases}.json`，`claims/formalization-scope.md` |

## モデル選択・escalation の推移（軸別まとめ）

- 06-15〜20: メイン orchestrator は opus-4-8，サブエージェント 104/107 件は
  opus-4-8[1m]，Explore 3 件のみ haiku（EV-2076）．
- 06-20〜29: orchestrator opus-4-8 大半 + 軽量タスクに sonnet（EV-0925）．
- 07-09〜10: orchestrator は fable-5，teammate 5 体 + 検証 subagent 8 体は全て
  sonnet．opus escalation の判断点は複数回あったが発動 0 件（EV-1669）．
- 07-15〜18: orchestrator fable-5（EV-0247）．
- escalation の失敗様態は 2 件: safety classifier の hard-block（06-19，EV-2076）と
  レビューデーモンのモデル設定不備（06-29，EV-0925）．いずれも人手介入で解消．

## 観察（03 節の主張範囲）

- 規律の多くは**事前設計ではなく incident 駆動**で導入されている（byte-diff 悉皆 ←
  INC-004，statement card ← INC-001，資源規約 ← INC-005，3 経路監視 ← 見落とし停滞）．
  例外は初日から存在した「orchestrator 非編集」「statement gate」「disk 再検証」の
  3 規律（EV-2076）．
- FALSE-SUCCESS 0 件（CLM-004）は「成功報告を信頼せず disk/`#print axioms` を
  再検証する」規律の帰結として解釈できる（因果の断定はしない．CLM-005 と同じ
  ヘッジ水準を保つ）．
