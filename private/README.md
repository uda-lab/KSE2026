# private/ — raw データ置き場（Git 管理外）

このディレクトリは `.gitignore` により **本 README 以外すべて Git 管理外**．
raw セッションログ，未 redaction の抜粋，認証情報を含みうる一切のファイルはここに置く．

```text
private/raw-sessions/
├── vps/                # VPS 由来（~/.claude/projects/ 等のコピー）
├── local-main/         # 主 local machine 由来
└── local-secondary/    # 副 local machine 由来
```

## 規約（AGENTS.md 規則 1–3）

- 収集時に各 host ディレクトリ直下へ `SOURCES.md`（gitignored）を作り，
  **収集元マシン上の絶対パス**と収集先 relpath の対応を記録する（公開 manifest には
  相対パスしか載らないため，これが唯一の対応表になる）．
- 収集元パスに含まれる username・非公開プロジェクト名は `private/redact-names.txt`
  （1 行 1 語）に追加し，`scripts/redact_check.py` の denylist として効かせる．
- 収集した元ファイルは **read-only**（`chmod -R a-w`）とし，以後変更しない．
- 収集直後に `python3 scripts/inventory_sessions.py private/raw-sessions/<host> --host <host>`
  を実行して `evidence/manifest.csv` に登録する．
- ここから公開領域（`evidence/`）へ出せるのは，`scripts/normalize_sessions.py` で
  正規化し `scripts/redact_check.py` を通過したものだけ．
- `git add -f` によるコミットは禁止．
