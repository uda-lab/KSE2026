#!/usr/bin/env python3
"""Export a reproducible GitHub-evidence snapshot of uda-lab/leray-hopf.

Writes to evidence/repository-snapshots/<repo-name>/:
  commits.json    — full history: sha, author/committer login+name, dates, subject
  issues.json     — issues AND PRs (state=all): number, kind, title, body, dates,
                    labels, author login, closed_by-ish fields, author_association,
                    performed_via_github_app (slug or null)
  comments.json   — all issue/PR comments (repo-wide endpoint): as above, plus
                    author_association, performed_via_github_app (slug or null)
  releases.json   — releases; tags.json — tags
  EXPORT.json     — fetch metadata (fetched_at, head sha, tool versions)

JSON arrays (not JSONL): the repo-wide rule is that no .jsonl is ever
committed — the CI leakage guard treats the extension as raw-session-log
material. Snapshot data is regenerable structured JSON (see the `private`
note below on who can regenerate it), so plain arrays keep the guard simple
and strict.

`performed_via_github_app` records the GitHub App slug that authored the item
(e.g. "chatgpt-codex-connector") when the item was posted through an App
connector, else null. This is a LOWER BOUND on mediated authorship, not a
census: any PAT-holding process (gh CLI, an orchestrator, a harness) also
yields null, so null does not prove direct human authorship. Conversely, a
non-null slug only proves the transport channel, not who composed the text.
`html_url` is intentionally omitted — it is trivially reconstructible from
`repo` + `number`/`id` and was not needed by any downstream consumer; add it
only if a future consumer needs it and it passes redact_check.py's
PUBLIC_REPO_ALLOWLIST for the target repo.

Email addresses are deliberately NOT exported (repo redaction gate); authors
are identified by GitHub login (fallback: display name). Personal names
listed in private/redact-names.txt (untracked; same file redact_check.py
reads) are masked as <name-redacted> when that file is present at export
time. Everything here is
regenerable from the source repository via `gh api` — rerun this script
rather than hand-editing. Byte-identical regeneration of a snapshot exported
with masking active additionally requires the same private/redact-names.txt
(EXPORT.json's name_masking_active records whether masking ran). EXPORT.json records the source repo's `private`
flag: for a private repo (e.g. this paper repo's own self-snapshot), that
means the export is reproducible only by an account with read access, unlike
a public-repo snapshot such as uda-lab/leray-hopf — this asymmetry must be
stated wherever the snapshot is cited, not glossed.

Usage:
  python3 scripts/export_repo_snapshot.py [--repo uda-lab/leray-hopf]
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT_ROOT = Path(__file__).resolve().parent.parent / "evidence" / "repository-snapshots"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Mirrors redact_check.py's NAME_DENYLIST loader: one name per line, kept out
# of git in private/redact-names.txt. When the file is absent (e.g. CI, or a
# third party reproducing a public-repo snapshot), no names are masked — in
# that same environment redact_check.py cannot flag those names either, so
# gate and scrub degrade together *within one environment*. Across
# environments they can still diverge: an export made without the denylist
# passes CI and that contributor's local gate, then blocks the next
# environment that does hold the denylist (exactly the issue #79 sequence).
# EXPORT.json records name_masking_active so a reader can tell which case a
# committed snapshot is. Byte-identical regeneration of a masked snapshot
# therefore requires the same denylist file in addition to `gh api` access.
NAME_DENYLIST_FILE = Path(__file__).resolve().parent.parent / "private" / "redact-names.txt"


def load_name_patterns():
    if NAME_DENYLIST_FILE.is_file():
        names = [ln.strip()
                 for ln in NAME_DENYLIST_FILE.read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.startswith("#")]
        return [re.compile(re.escape(n)) for n in names]
    return []


NAME_PATTERNS = load_name_patterns()


def scrub(text: str) -> str:
    """Mask email addresses and denylisted personal names so the snapshot
    passes the repo redaction gate (redact_check.py). Emails appear e.g. in
    Co-Authored-By trailers quoted in PR bodies; denylisted names appear e.g.
    in host-identification handles quoted in issue comments."""
    text = EMAIL_RE.sub("<email-redacted>", text)
    for rx in NAME_PATTERNS:
        text = rx.sub("<name-redacted>", text)
    return text


# Machine identifiers that downstream consumers group or join on (e.g.
# compute_mediation_census.py groups by user_login × performed_via_github_app,
# and shas identify commits). These are excluded from scrub_tree: silently
# masking a grouping key would split/merge downstream categories instead of
# failing loudly. If a denylisted name ever appears in one of these fields,
# redact_check.py still flags the committed file and a human decides —
# fail-closed at the gate rather than silent data mutation (PR #80 review).
IDENTIFIER_KEYS = frozenset({
    "sha", "parents", "commit_sha", "head_sha_at_fetch",
    "user_login", "author_login", "committer_login",
    "performed_via_github_app",
})


def scrub_tree(obj, key=None):
    """Apply scrub() to every string value (not keys) in a JSON tree, except
    values of IDENTIFIER_KEYS.

    write_json() runs this over each exported structure, so the masking is
    authoritatively applied here for *all* string-valued fields — commit
    author display names, milestone titles, label and tag names, and any
    field a future exporter change adds — not only the free-text bodies.
    (The explicit scrub() calls in the per-field comprehensions below are
    redundant but harmless — scrub() is idempotent on its own output — and
    are kept to minimize diff churn.) Without this, a denylisted name
    appearing in e.g. a commit author_name would reach the committed
    snapshot verbatim and fail the redaction gate (PR #80 review finding)."""
    if key in IDENTIFIER_KEYS:
        return obj
    if isinstance(obj, str):
        return scrub(obj)
    if isinstance(obj, list):
        return [scrub_tree(v) for v in obj]
    if isinstance(obj, dict):
        return {k: scrub_tree(v, k) for k, v in obj.items()}
    return obj


def gh_api(path: str, paginate: bool = True):
    cmd = ["gh", "api", path, "-H", "X-GitHub-Api-Version: 2022-11-28"]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    if paginate:  # --slurp yields a list of pages
        merged = []
        for page in data:
            merged.extend(page if isinstance(page, list) else [page])
        return merged
    return data


def write_json(path: Path, rows):
    rows = scrub_tree(rows)
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, sort_keys=True, indent=1)
        f.write("\n")
    print(f"{path.name}: {len(rows)} rows", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default="uda-lab/leray-hopf")
    args = ap.parse_args()
    name = args.repo.split("/")[1]
    out = OUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)

    repo_meta = gh_api(f"repos/{args.repo}", paginate=False)
    is_private = bool(repo_meta.get("private"))

    head = gh_api(f"repos/{args.repo}/commits/HEAD", paginate=False)["sha"]

    commits = [{
        "sha": c["sha"],
        "author_login": (c.get("author") or {}).get("login"),
        "author_name": c["commit"]["author"]["name"],
        "authored_date": c["commit"]["author"]["date"],
        "committer_login": (c.get("committer") or {}).get("login"),
        "committed_date": c["commit"]["committer"]["date"],
        "subject": scrub(c["commit"]["message"].split("\n")[0]),
        "parents": [p["sha"] for p in c["parents"]],
    } for c in gh_api(f"repos/{args.repo}/commits?per_page=100")]
    write_json(out / "commits.json", commits)

    issues = [{
        "number": i["number"],
        "kind": "pr" if "pull_request" in i else "issue",
        "state": i["state"],
        "title": scrub(i["title"]),
        "body": scrub(i.get("body") or ""),
        "user_login": (i.get("user") or {}).get("login"),
        "author_association": i.get("author_association"),
        "performed_via_github_app": (i.get("performed_via_github_app") or {}).get("slug"),
        "labels": [lb["name"] for lb in i.get("labels", [])],
        "created_at": i["created_at"],
        "updated_at": i["updated_at"],
        "closed_at": i.get("closed_at"),
        "comments": i.get("comments"),
        "milestone": (i.get("milestone") or {}).get("title"),
    } for i in gh_api(f"repos/{args.repo}/issues?state=all&per_page=100")]
    write_json(out / "issues.json", issues)

    comments = [{
        "issue_number": int(c["issue_url"].rsplit("/", 1)[1]),
        "id": c["id"],
        "user_login": (c.get("user") or {}).get("login"),
        "author_association": c.get("author_association"),
        "performed_via_github_app": (c.get("performed_via_github_app") or {}).get("slug"),
        "created_at": c["created_at"],
        "updated_at": c["updated_at"],
        "body": scrub(c.get("body") or ""),
    } for c in gh_api(f"repos/{args.repo}/issues/comments?per_page=100")]
    write_json(out / "comments.json", comments)

    releases = [{
        "tag_name": r["tag_name"],
        "name": scrub(r.get("name") or "") or None,
        "created_at": r["created_at"],
        "published_at": r.get("published_at"),
        "body": scrub(r.get("body") or ""),
    } for r in gh_api(f"repos/{args.repo}/releases?per_page=100")]
    write_json(out / "releases.json", releases)

    tags = [{"name": t["name"], "commit_sha": t["commit"]["sha"]}
            for t in gh_api(f"repos/{args.repo}/tags?per_page=100")]
    write_json(out / "tags.json", tags)

    gh_version = subprocess.run(["gh", "--version"], capture_output=True,
                                text=True).stdout.splitlines()[0]
    meta = {
        "repo": args.repo,
        "private": is_private,
        "name_masking_active": bool(NAME_PATTERNS),
        "head_sha_at_fetch": head,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool_versions": {"python": sys.version.split()[0], "gh": gh_version},
        "counts": {"commits": len(commits), "issues_and_prs": len(issues),
                   "comments": len(comments), "releases": len(releases),
                   "tags": len(tags)},
        "note": "regenerable from the source repository via `gh api` (see "
                "`private` above for who can reproduce it); emails "
                "intentionally omitted; denylisted personal names masked as "
                "<name-redacted> when private/redact-names.txt was present "
                "at export time; "
                "per-PR review events are fetched separately when an incident "
                "analysis needs them; issues.json and comments.json carry "
                "performed_via_github_app (slug or null) and author_association "
                "as of this export — see script docstring for the lower-bound "
                "caveat on interpreting these fields"
                + (
                    ". REPRODUCIBILITY ASYMMETRY: this repository is private "
                    "at fetch time, so — unlike a public-repo snapshot such as "
                    "uda-lab/leray-hopf — this export is NOT publicly "
                    "re-derivable by a third party; only accounts with read "
                    "access to the repo can reproduce it via `gh api`."
                    if is_private else ""
                ),
    }
    (out / "EXPORT.json").write_text(json.dumps(meta, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(meta["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
