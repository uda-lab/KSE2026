# private/ — raw データ置き場（Git 管理外）

このディレクトリは `.gitignore` により **本 README 以外すべて Git 管理外**．
raw セッションログ，未 redaction の抜粋，認証情報を含みうる一切のファイルはここに置く．

## 物理レイアウト（2026-07-21 owner 決定，issue #9）

リポジトリ内のパスは互換のため維持しつつ，実体は host bind-mount に置く:

```text
private/raw-sessions -> /private/sources/KSE2026/raw-sessions/   (symlink)
├── vps/                # VPS 由来（~/.claude/projects/ + ~/.hermes/ の選別コピー）
├── local-main/         # 主 local machine 由来
└── local-secondary/    # 副 local machine 由来
private/derived      -> /private/derived/KSE2026/                (symlink)
                        # normalize_sessions.py 等の中間生成物（JSONL はここ止まり）
```

- `/private/sources` は**コンテナ内 read-only**．書込（転送・移設）はホスト側から行う．
  これにより escrow の不変性が chmod より強く保証され，コンテナ再構築からも独立する．
- local 2 環境からの転送はホスト側の `/private/sources/KSE2026/raw-sessions/<host>/`
  へ直接 rsync/scp する（コンテナを経由しない）．収集元のディレクトリ構造を保つこと．
- `.jsonl` はリポジトリ全域でコミット禁止（CI が強制）．公開するのは
  `evidence/redacted-excerpts/` の選別済み Markdown のみ．

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
