# evidence/redacted-excerpts/

論文 §IV の 4 事例（Case A–D）を支える一次セッション記録の抜粋．各ファイルは
`private/raw-sessions/`（gitignored escrow）の JSONL transcript から手で選別し，
`scripts/redact_check.py` を通したもの．引用は原文のまま，省略は `[…]`，
redaction による置換は `<…>` または `~` で示す．

| ファイル | Incident | 論文 | session | Evidence ID | 窓（UTC） |
|---|---|---|---|---|---|
| `INC-001-case-A.md` | INC-001 | §IV Case A | `90fa24bb` (vps) | EV-0925 | 2026-06-28 07:33–07:59 |
| `INC-002-case-B.md` | INC-002 | §IV Case B | `90fa24bb` (vps) | EV-0925 | 2026-06-21 02:57–03:18 |
| `INC-004-case-C.md` | INC-004 | §IV Public declarations during refactoring | `7e6156bf` (local-main) | EV-1669 | 2026-07-10 00:12–00:39 |
| `INC-005-case-D.md` | INC-005 | §IV Resource availability and orchestration | `de129390` (vps) | EV-0247 | 2026-07-18 06:28–06:31, 07:32–07:52 |

各ファイルの冒頭に，出典（EV-ID・JSONL の行範囲）と，対応する incident card・claim・
論文の文を記す．INC-003（ログローテーションによる記録喪失）は「記録が存在しない」ことが
内容であり，抜粋の対象にならない．

## 選別と redaction の方針

- 論文本文と incident card が引用する事実（時刻・数値・判断）を一次記録で確認できる
  最小限の範囲に限る．抜粋範囲外の関連事象は各ファイル末尾で card への参照に留める．
- 抜粋中の path は，username を含む home directory を `~` に，session 固有の長い
  作業ディレクトリを `<scratchpad>` に置換した．Git trailer・session URL・agent の
  内部 ID の類は省いた．
- 人物は「owner（著者）」「orchestrator」「agent 名」で表記する．GitHub login は
  公開 repository（`uda-lab/leray-hopf`，旧名 `lean-pde`）に関するもののみ残る．
- 追加・変更時は `python3 scripts/redact_check.py --dir evidence/redacted-excerpts`
  で検出ゼロを確認する（denylist は `private/redact-names.txt`）．
