# INC-005 / Case D — コンテナ低メモリ cascade の検出と回復（2026-07-18）

- **Incident card:** `evidence/incidents/INC-005.md`（2026-07-31 の訂正節を含む）
- **論文の対応箇所:** §IV「Resource availability and orchestration」（`paper/sections/04-incidents.tex`），claim CLM-008
- **Session:** `de129390-559a-4ecd-950e-3667cf1c1c3c`（host vps，`evidence/session-index/de129390-559a-4ecd-950e-3667cf1c1c3c.md`）
- **Evidence ID:** EV-0247（メイン transcript，`claude-projects/-tmp-hermes-worktrees-lean-pde-notes-issue-51/de129390-559a-4ecd-950e-3667cf1c1c3c.jsonl`）
- **抜粋範囲:** 同 JSONL の L7281〜L7329（2026-07-18T06:28〜06:31Z）および L7331〜L7573（07:32〜07:52Z）
- **本抜粋が支える記述:** 論文の「Monitoring had covered the visible Lean process rather than memory available to the whole container」「Roughly seventy minutes after a status check had reported the container healthy on that basis, the author's next status request arrived after an eight-minute delay, followed at once by an instruction to kill stale processes」「a memory check report 606 MiB available」「the fourteen stale chains」「A cumulative kill counter […] was read as confirmation that the out of memory (OOM) killer had terminated the builds」「raised available memory to 2.2 GiB」「The worktree returned to the original agent, the duplicate stopped, and the build completed under a global lock」

表記: owner = 著者（user メッセージ），orchestrator = メインセッションの assistant，`issue155`／`issue155b` = 派遣された implementation agent．引用は原文（日本語・コマンド出力）のまま．`[…]` は省略．`<scratchpad>` は session 固有の長い作業ディレクトリ path の置換，`~` は home directory の置換．Swap 行は host 側の値（card 参照）．

## 1. 06:28:39Z — owner の状況確認（L7283）

> 短時間と言ってもやはりコンテナのリソースでは時間がかかっているのかねぇ？　あぁ，無理に止めなくていいよ，状況を知りたいだけ

## 2. 06:28:52Z — orchestrator の `ps aux | grep -E 'lake|lean'` 出力（L7289，冒頭 3 行）

前日 07-17 起動の codex broker がこの時点で出力に現れているが，以下 3 の報告では言及されない．

```text
vscode    414083  0.0  0.5 1023020 20196 ?  Ssl  Jul17  0:00 /usr/bin/node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/app-server-broker.mjs serve --endpoint unix:/tmp/cxc-nzwzHH/broker.sock --cwd /tmp/hermes-worktrees/lean-pde-notes-issue-51 […]
vscode    419445  0.0  0.2 1014596 10740 ?  Ssl  Jul17  0:00 /usr/bin/node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/app-server-broker.mjs serve […] --cwd /workspaces/lean-pde-notes/.claude/worktrees/agent-a1ca7a1691a00fca3 […]
vscode    426718  0.0  0.2 1014324 10584 ?  Ssl  Jul17  0:00 /usr/bin/node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/app-server-broker.mjs serve […] --cwd <scratchpad>/wt-153 […]
[…]
```

## 3. 06:29:27Z — orchestrator の報告（誤診断，L7304）

> **issue155b の detached ビルド（wt-155、Torus.ConvectionExtension）**
> - 15:00 に再起動されたビルドが現在 **1896/1929** まで到達（15:28 時点、更新継続中）。[…]
> - 遅さの原因は 2 つ重なっています: (1) wt-155 は `lake exe cache get` を通していない worktree なので mathlib をソースからコンパイルしている、(2) コンテナの CPU/メモリ制約で並列度が 3〜4 プロセスに留まり、1 ファイル 20〜70 秒かかっている。[…]
> - メモリは lean プロセス合計で ~850MB 程度と cgroup 上限（3.42GiB)に対し余裕があり、OOM の危険はいまのところありません。

## 4. 06:30:55Z — owner（L7309）

> cache は worktree で共有する方針じゃなかったかね？ それだと実質フルビルドですね．まぁ良いですよ．時間はあるので．

## 5. 07:32〜07:40Z — 8 分の配送遅延と kill 指示（queue-operation 記録，L7331・L7332・L7342）

transcript の queue 操作記録（`type: queue-operation`）を時刻順に転記する．

| timestamp (UTC) | operation | content |
|---|---|---|
| 07:32:21.086Z | enqueue | `status` |
| 07:40:09.776Z | dequeue | — |
| 07:40:12.282Z | enqueue | 不要なサブエージェント・stale プロセス・codex ゾンビ・その他，無駄にメモリーを食っているものを片っ端から一度殺してください．メモリーを少しでもあけると Lean の作業も早くなるでしょう． |

## 6. 07:40:39Z — 枯渇の検出（L7352）

```text
$ free -h; cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.current
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       3.2Gi       196Mi       3.9Mi       699Mi       606Mi
Swap:          2.0Gi       110Mi       1.9Gi
---
3670016000
3567398912
```

## 7. 07:41:25Z — 残留チェーンの特定（L7367）

`readlink /proc/<pid>/cwd` の結果（15 系統中，末尾の 1 系統のみ稼働中）:

```text
414097 -> /tmp/hermes-worktrees/lean-pde-notes-issue-51
419459 -> /workspaces/lean-pde-notes/.claude/worktrees/agent-a1ca7a1691a00fca3 (deleted)
426732 -> <scratchpad>/wt-153
439647 -> <scratchpad>/wt-147
512171 -> <scratchpad>/wt-166
556278 -> <scratchpad>/nwt-65
561064 -> <scratchpad>/nwt-66
563827 -> /workspaces/lean-pde-notes/.claude/worktrees/agent-a81a93a6b0dd4253d (deleted)
579598 -> /workspaces/lean-pde-notes/.claude/worktrees/agent-aec021c65c5c8cdbf (deleted)
585295 -> <scratchpad>/nwt-68
597450 -> /workspaces/lean-pde-notes/.claude/worktrees/agent-a616e07de824a2008 (deleted)
602315 -> <scratchpad>/nwt-72
605160 -> /workspaces/lean-pde-notes/.claude/worktrees/agent-ac6e3fa980298248b (deleted)
665705 -> <scratchpad>/nwt-70
875628 -> /tmp/hermes-worktrees/notes-issue-30
```

## 8. 07:42:18Z〜07:42:49Z — 一括 kill と回復（L7377・L7384）

Bash tool 入力の description: "Kill 14 stale codex broker/app-server chains, keep active notes-issue-30 chain"．直後の計測:

```text
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       1.6Gi       276Mi       3.9Mi       2.3Gi       2.2Gi
Swap:          2.0Gi       156Mi       1.8Gi
---
3430502400
---
945303 1863MB […]/bin/lean <scratchpad>/wt-155/LerayHopf/Torus/ConvectionExtension.lean -o
386323 643MB claude --resume
945221 112MB […]/bin/lake build LerayHopf.Torus.ConvectionExtension
```

## 9. 07:44:12Z〜07:44:44Z — 累積カウンタの読み取りと当時の帰属（L7410・L7415）

```text
$ cat /sys/fs/cgroup/memory.events
low 0
high 0
max 31553152
oom 0
oom_kill 7
oom_group_kill 0
```

orchestrator → `issue155b`（07:44:44Z）:

> (1) 判明した事実: あなたのビルドが繰り返し死んでいた原因は OOM です（cgroup memory.events で oom_kill=7 を確認。ログの exit 137 = SIGKILL はすべてこれ）。直近 16:42 頃には mathlib 依存は全て built 済みで、ターゲットの LerayHopf/Torus/ConvectionExtension.lean 本体のコンパイル（RSS 1.8GB 超）まで到達した後に殺されています。[…]
> (2) owner 指示でコンテナのメモリ大掃除を実施しました: 旧 worktree に紐づく codex app-server/broker ゾンビ 14 系統（約 1〜1.5GB）を kill 済み。used 3.2Gi → 1.6Gi、available は 2.2Gi に回復しています。[…]
> (3) 指示: いますぐ `flock /tmp/lean-build.lock lake build LerayHopf.Torus.ConvectionExtension` を再実行してください […] もし再度 137 で死ぬ場合は、(a) `LEAN_NUM_THREADS=1` を付けて逐次コンパイルでピークメモリを下げる、(b) それでも駄目なら owner へのエスカレーション対象として私に報告してください […]

この帰属（7 件の kill が当日の build 死である）は 2026-07-31 の host 側 kernel log 照合（KSE2026 issue #100）で否定された．7 件はすべて 07-16 の host global OOM に帰属し，当日の kill 機構は未特定である（card の訂正節）．

## 10. 07:45:03Z — 死亡と判定されていた `issue155` の報告（L7459）

> (b) 詰まっていた点（解消済み）: 新規 worktree（wt-155）の `.lake` が空で、targeted build が mathlib ~1900 ファイルの実質フルビルドに突入し数時間かかっていた […]。1回 build を kill し、既存 clone（lean-pde、mathlib フルビルド済み 8.5G）から `cp -al` でハードリンク共有し復旧。現在は対象ファイルのみを正しくコンパイル中（`lake` 経過時間 数分、mathlib 再ビルドなし — プロセスツリーで確認済み）。

## 11. 07:45:29Z〜07:46:15Z — 二重稼働の解消（L7463・L7471・L7481）

orchestrator:

> issue155（先代・死亡と判定していた agent）が生きていて、しかもキャッシュ共有を自力で復旧し正しい targeted build 中とのこと。後継 issue155b と二重体制になっているので、即座に交通整理します。

`TaskStop` の結果（07:46:03Z）:

```text
{"message":"Successfully stopped task: trbmczr7p […]","task_id":"trbmczr7p","task_type":"in_process_teammate"}
```

残った build（07:46:15Z）:

```text
946048 flock /tmp/lean-build.lock lake
946049 […]/bin/lake build LerayHopf.Torus.ConvectionExtension
946109 […]/bin/lean <scratchpad>/wt-155/LerayHopf/Torus/ConvectionExtension.lean -o
```

## 12. 07:47:34Z — 常設指示への注入（L7491）

`~/.claude/CLAUDE.md` に追記された節（Bash tool 入力の heredoc）:

> ## 本コンテナ限定 — メモリ・プロセス衛生（恒常規約、2026-07-18 owner 指示で明文化）
>
> このコンテナは cgroup 上限 ~3.4GiB。Lean/mathlib ビルドはピーク 2〜3.4GiB に達し、**メモリが最稀少資源**。`exit 137` は原則 OOM（`cat /sys/fs/cgroup/memory.events` の `oom_kill` で確認）。以下は「思い出したら守る」メモリー任せにせず、毎回機械的に実施する:
>
> 1. **codex プラグインの broker/app-server チェーンは自動回収されない**（cwd ごとに `app-server-broker.mjs` + `codex app-server` ×2、計 60〜330MB）。codex 事前レビュー完了・worktree 撤収のたびに該当チェーンを即 kill する。放置実績: 2026-07-18 に 14 系統 ~1.5GB を溜め込み Lean ビルドが OOM 連発。
> 2. **定期 sweep**: Lean ビルド開始前・agent dispatch 前に `ps aux | grep app-server-broker` を確認し、cwd が削除済み/merge 済み worktree を指す chain を全て kill（`readlink /proc/<pid>/cwd` で判定）。
> 3. **ビルド前ヘッドルーム確認**: `free -h` で available ≥ 2GiB。不足なら先に掃除（削るのはゾンビであって稼働中ビルドではない）。
> 4. **新規 worktree に自前 `.lake` を作らせない** — mathlib フルビルド済みクローンの `.lake` を `cp -al`（ハードリンク）で共有。cold build は mathlib ~1900 ファイルの実質フルビルド（数時間 + OOM リスク）になる。
> 5. **dispatch prompt に毎回明記**: (a) `.lake` 共有方法、(b) `flock /tmp/lean-build.lock`（コンテナ全体で lean build 同時 1 個）、(c) 作業完了時に自分の codex chain を掃除すること。
> 6. OOM 再発時の縮退: `LEAN_NUM_THREADS=1` で逐次コンパイル → それでも不可なら owner へエスカレーション（モジュール分割の判断材料として報告）。

## 13. 07:48:04Z — orchestrator の経緯説明（L7501，第 1 段落）

> **いつから溜め込んでいたか**: プロセスの起動時刻から、14 系統のうち 13 系統は **昨日 7/17 の夜間波**のものでした。codex 事前レビューを worktree ごとに実行するたびに broker+app-server が 1 系統ずつ生まれ（1 worktree = 1 系統、自動回収なし）、PR が merge され worktree が用済みになっても私が一度も回収せず、**丸一日半放置**していました。[…]「コンテナ資源が最重要制約」という指示をメモリーに持ちながら、lean ビルドの並列度にしか適用せず、自分が起こしたプラグインプロセスの後始末には適用していなかった […]

## 14. 07:49:42Z — owner（L7512）

> はい．global memory にも project memory にもしっかりと刻んでください．なお，codex server が放置されていて OOM 連発を起こしたのも既に数回目です．メモリーにも入っているはずです．

## 15. 07:51:55Z — 4 層への記録完了（L7571，冒頭）

> 刻み終わりました。記録先は 4 層です：
>
> **Global memory** […] — 新規 `feedback_reap_agent_side_processes.md`：汎用規則「オーケストレーションが生む常駐サイドプロセスは完了イベントごとに reap + 重処理前に sweep」。再犯 2 回（2026-05-09 の tmux pane 版 […]、2026-07-18 の codex chain 版）を明記 […]
> **本 project memory** […] — 新規 `feedback-container-memory-hygiene.md` […]
> **lean-pde 側 project memory** — ビルド制約の正典 `project_build_env_memory_ceiling.md` に追記 […]
> **注入層** — `~/.claude/CLAUDE.md` の「本コンテナ限定 — メモリ・プロセス衛生」節 […]

global memory の実物は EV-0005（`claude-projects/-home-vscode/memory/feedback_reap_agent_side_processes.md`）として escrow に収録されている．

## 抜粋範囲外の関連事象

同日 12:42Z／13:06Z の別形態での再発（正当な単一ビルドのピーク RSS による `available` 低下）と 13:10Z の規約定着確認は，session index と card に記録されているが本抜粋には含めない．
