# evidence/

公開可能な証跡のみを置く．raw ログは `private/raw-sessions/`（gitignored）．

- `manifest.csv` — 収集した証拠アイテムの台帳．`scripts/inventory_sessions.py` が
  追記する．列: `evidence_id`（EV-NNNN，連番），`sha256`，`host`
  （vps / local-main / local-secondary），`collected_relpath`，`size_bytes`，
  `mtime_utc`，`ctime_utc`，`session_id`（推定），`tool_or_model`，
  `collected_at_utc`，`evidence_type`（primary / reconstructed），`notes`．
  **PLAN.md §4 からの意図的な逸脱**: 元の絶対パスは username や非公開プロジェクト名を
  含みうるため，公開 manifest にはスキャン root からの相対パスのみを記録する．
  収集元マシン上の絶対パスとの対応は，収集時に
  `private/raw-sessions/<host>/SOURCES.md`（gitignored）へ記録すること．
- `repository-snapshots/` — leray-hopf 等の Git 証跡スナップショット（commit list，
  issue/PR エクスポートなど機械抽出物）．
- `session-index/` — セッション単位の索引（正規化メタデータ．本文は含まない）．
- `redacted-excerpts/` — redaction 済み抜粋のみ．置く前に
  `python3 scripts/redact_check.py <file>` で検出ゼロを確認（AGENTS.md 規則 3）．
- `incidents/` — incident card（`INC-NNN.md`）．書式は `incidents/TEMPLATE.md`．
- `metrics/` — `scripts/extract_metrics.py` の出力（行数，宣言数，コミット統計等）．

原則: このディレクトリ配下のファイルは**機械的に再生成可能**か，**redaction 検査済み**の
いずれかであること．
