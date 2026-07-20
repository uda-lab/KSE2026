#!/usr/bin/env python3
"""Export a reproducible GitHub-evidence snapshot of uda-lab/leray-hopf.

Writes to evidence/repository-snapshots/<repo-name>/:
  commits.json    — full history: sha, author/committer login+name, dates, subject
  issues.json     — issues AND PRs (state=all): number, kind, title, body, dates,
                    labels, author login, closed_by-ish fields
  comments.json   — all issue/PR comments (repo-wide endpoint)
  releases.json   — releases; tags.json — tags
  EXPORT.json     — fetch metadata (fetched_at, head sha, tool versions)

JSON arrays (not JSONL): the repo-wide rule is that no .jsonl is ever
committed — the CI leakage guard treats the extension as raw-session-log
material. Snapshot data is regenerable public JSON, so plain arrays keep the
guard simple and strict.

Email addresses are deliberately NOT exported (repo redaction gate); authors
are identified by GitHub login (fallback: display name). Everything here is
regenerable public data — rerun this script rather than hand-editing.

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


def scrub(text: str) -> str:
    """Mask email addresses so the snapshot passes the repo redaction gate.
    (They appear e.g. in Co-Authored-By trailers quoted in PR bodies.)"""
    return EMAIL_RE.sub("<email-redacted>", text)


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

    head = gh_api(f"repos/{args.repo}/commits/HEAD", paginate=False)["sha"]

    commits = [{
        "sha": c["sha"],
        "author_login": (c.get("author") or {}).get("login"),
        "author_name": c["commit"]["author"]["name"],
        "authored_date": c["commit"]["author"]["date"],
        "committer_login": (c.get("committer") or {}).get("login"),
        "committed_date": c["commit"]["committer"]["date"],
        "subject": c["commit"]["message"].split("\n")[0],
        "parents": [p["sha"] for p in c["parents"]],
    } for c in gh_api(f"repos/{args.repo}/commits?per_page=100")]
    write_json(out / "commits.json", commits)

    issues = [{
        "number": i["number"],
        "kind": "pr" if "pull_request" in i else "issue",
        "state": i["state"],
        "title": i["title"],
        "body": scrub(i.get("body") or ""),
        "user_login": (i.get("user") or {}).get("login"),
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
        "created_at": c["created_at"],
        "updated_at": c["updated_at"],
        "body": scrub(c.get("body") or ""),
    } for c in gh_api(f"repos/{args.repo}/issues/comments?per_page=100")]
    write_json(out / "comments.json", comments)

    releases = [{
        "tag_name": r["tag_name"],
        "name": r.get("name"),
        "created_at": r["created_at"],
        "published_at": r.get("published_at"),
        "body": scrub(r.get("body") or ""),
    } for r in gh_api(f"repos/{args.repo}/releases?per_page=100")]
    write_json(out / "releases.json", releases)

    tags = [{"name": t["name"], "commit_sha": t["commit"]["sha"]}
            for t in gh_api(f"repos/{args.repo}/tags?per_page=100")]
    write_json(out / "tags.json", tags)

    meta = {
        "repo": args.repo,
        "head_sha_at_fetch": head,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {"commits": len(commits), "issues_and_prs": len(issues),
                   "comments": len(comments), "releases": len(releases),
                   "tags": len(tags)},
        "note": "regenerable public data; emails intentionally omitted; "
                "per-PR review events are fetched separately when an incident "
                "analysis needs them",
    }
    (out / "EXPORT.json").write_text(json.dumps(meta, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(meta["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
