# INC-001 / Case A — `w1pTime_continuous_in_H` の consumer verdict（2026-06-28）

- **Incident card:** `evidence/incidents/INC-001.md`
- **論文の対応箇所:** §IV Case A（`paper/sections/04-incidents.tex`），claim CLM-005・CLM-008
- **Session:** `90fa24bb-c5e4-43ff-8d27-1799177561a0`（host vps，`evidence/session-index/90fa24bb-c5e4-43ff-8d27-1799177561a0.md`）
- **Evidence ID:** EV-0925（メイン transcript，`claude-projects/-workspaces-lean-pde/90fa24bb-c5e4-43ff-8d27-1799177561a0.jsonl`）
- **抜粋範囲:** 同 JSONL の L7650〜L7740（2026-06-28T07:33〜07:59Z）
- **本抜粋が支える記述:** 論文 Case A の「a later proof attempt checked only that no capstone theorem depended on it」，および card の「consumer verdict は未使用であることの利用箇所調査であり，宣言の型の soundness には踏み込んでいない」

表記: orchestrator = メインセッションの assistant．`s1-core-opus`／`wkernel-opus` = 派遣された prover agent．引用は原文（英語）のまま．`[…]` は省略．Git trailer と session URL は省いた．

## 1. 07:35:13Z — orchestrator: 攻撃対象を `w1pTime_continuous_in_H` に定める（L7652）

> Important strategic finding from the prover: **the whole foundation converges on one core, and the mollification route to it is circular.** B2 (cutoff) and the WALL A commutation *identity* are proved sorry-free, but B1 (the no-Dirac reflection) needs the trace `u(0)` — i.e. the **Bochner-valued 1D-Sobolev FTC / continuous representative**, which *is* `w1pTime_continuous_in_H`. So building the continuous rep *via* mollification is circular (B1 needs the very thing it builds). The real core is one theorem — the **direct Bochner FTC** — and it must be attacked directly, not through mollification.

## 2. 07:36:20Z — orchestrator → `wkernel-opus` 派遣 prompt 冒頭（L7666）

宣言は「Lions–Magenes の定理」として汎用の指数 `p` で言い換えられ，型の検査は課題に含まれていない．

> Attack the single months-class core that the entire final-4-axiom campaign routes through: `w1pTime_continuous_in_H` (the open sorry at `LerayHopf/Bochner/TimeSobolev.lean` ~line 544, Lions–Magenes `W^{1,p}(0,T;V,V') ↪ C([0,T];H)`). A prior prover found the mollification-via-reflection route is CIRCULAR […]
>
> YOUR JOB, in two parts:
>
> PART 1 — RESOLVE THE SOUND, NON-CIRCULAR ROUTE […] Pick the route with NO circular trace dependency and state it precisely […]
>
> PART 2 — START BUILDING the chosen route toward sorry-free `w1pTime_continuous_in_H` […]

## 3. 07:55:55Z — `wkernel-opus` 第 1 報（L7699）

> Done with the core investigation. Sound non-circular route FOUND and documented; two R1 building-block kernels PROVED sorry-free. The target stays at its single original ALLOW_SORRY (statement byte-identical, no new axiom). Honest scope: full discharge is genuinely multi-day; I closed the trace-free kernels and characterized the residual precisely.
>
> […]
>
> FILES: route doc + scratch kernel above. TimeSobolev.lean UNTOUCHED (git diff empty; 1 ALLOW_SORRY unchanged). No new axiom/opaque.

## 4. 07:58:20Z — `wkernel-opus` の consumer verdict（L7731）

> DECISIVE QUESTION RESOLVED. […]
>
> ANSWER: The sound route to removing the C axioms is (b) the STRONG-APPROXIMANT structure, NOT (a) weak-limit Lions–Magenes FTC. `w1pTime_continuous_in_H` is BYPASSED — it is off the critical path. This makes the limit-passage foundation DAYS-CLASS, not months-class.
>
> EVIDENCE (traced end-to-end):
> 1. `w1pTime_continuous_in_H` is APPLIED NOWHERE — referenced only in docstrings. It is a standalone scaffold. The real C axiom is `galerkin_limit_passage_R3` (R3/AxiomaticClosure.lean:558), applied to the WEAK LIMIT `alPkg.u` (AubinLionsAssembly.lean:84).
> 2. `alPkg.u` carries ONLY `u_aestronglyMeasurable` — no strong derivative, not even a V'-valued weak derivative. […]
> 3. The axiom's five conclusions are each obtainable WITHOUT any continuous-in-H representative of the limit: […]
>
> […]
>
> RECOMMENDATION: Redirect the campaign from "build months-class Lions–Magenes weak-FTC" to "wire the (b) strong-approximant limit passage (Temam III.3) to discharge `galerkin_limit_passage_R3`." That is the path that actually reaches the axiom removal. `w1pTime_continuous_in_H` can stay an off-critical-path scaffold (its own proof, the V'-FTC + interior-mollification route, is documented below the verdict for whoever wants to finish it, but it does NOT gate the C axioms).

## 5. 07:59:09Z — orchestrator: 計画の破棄と redirect（L7733）

> Major course-correction — and a hugely favorable one. The prover traced the actual consumer and found `w1pTime_continuous_in_H` is **applied nowhere** (docstrings only) — it's off the critical path. […] **The entire months-class Lions–Magenes / Bochner-weak-FTC machinery is bypassed** — C becomes days-class Temam-III.3 wiring of proved pieces.
>
> This is decisive enough that it must be codex-validated before the pivot […]. Let me hold the now-off-path R1 build, commit the verdict, and codex it.

## 6. 07:59:32Z — verdict の commit（L7736〜L7737）

commit message の件名（Bash tool 入力）:

> docs(bochner): consumer verdict — w1pTime_continuous_in_H is OFF critical path; C is days-class (b)-route

push 結果（07:59:37Z）:

```text
   a438304..7bb9b27  lane-bochner-f3 -> lane-bochner-f3
```

## 抜粋範囲に存在しないもの

この窓（07:33〜08:05Z）の全メッセージを通じて，宣言の仮定 `1 ≤ p ∧ 1 ≤ q` を検討する記述はない．verdict の根拠は「参照されていない」という利用箇所調査であり，型の真偽は問われていない．session index は，この transcript 全体で `theorem w1pTime_continuous_in_H` の宣言文字列が一度も現れないことを別途記録している．`p = q = 1` の反例は 2026-07-16 の issue #158（`evidence/repository-snapshots/leray-hopf/issues.json`）で初めて構成された．
