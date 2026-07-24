#!/usr/bin/env python3
"""Compute a mediated/direct authorship-channel census from GitHub snapshots.

Reads evidence/repository-snapshots/<repo>/{issues,comments}.json (produced by
export_repo_snapshot.py, issue #60) and groups rows by the poster's GitHub
login and, when present, the GitHub App slug recorded in
`performed_via_github_app` — i.e. whether the item was transmitted through an
App connector (e.g. "chatgpt-codex-connector") rather than posted directly by
a PAT-holding process.

These are mechanical groupings of raw API fields, not authorship claims — see
the LOWER_BOUND_CAVEAT below before reading anything into a login or a null.
As of this writing, four (login, performed_via_github_app, is_bot_account)
combinations are observed across the two tracked repos (any combination not
present in a given snapshot simply does not appear in the output — nothing
is hardcoded per-repo):

  - login "uda-lab-agent", performed_via_github_app null, is_bot_account false
  - login "t-uda", performed_via_github_app null, is_bot_account false
  - login "t-uda", performed_via_github_app "chatgpt-codex-connector",
    is_bot_account false
  - a GitHub App bot account (login ending in "[bot]", e.g.
    "chatgpt-codex-connector[bot]") — is_bot_account true regardless of
    performed_via_github_app, since the bot account itself is the poster

Writes:
  evidence/metrics/mediation-census.json — full breakdown + source provenance
  evidence/metrics/mediation-census.csv  — flat rows: repo,item_type,login,
                                            performed_via_github_app,
                                            is_bot_account,
                                            count_exact,caveat_ref

Every count is an EXACT tally of the raw (login, performed_via_github_app)
combination, but the counts are an ASYMMETRIC and INCOMPLETE signal about
authorship, not a census: non-null performed_via_github_app rows are a
LOWER BOUND on mediated (connector-transmitted) authorship; null rows are
NOT proof of direct human authorship either way. See LOWER_BOUND_CAVEAT
below and analysis/mediation-census-methodology.md — do not quote counts
from here without also quoting the caveat.

Usage:
  python3 scripts/compute_mediation_census.py [--repo uda-lab/leray-hopf ...]
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_ROOT = ROOT / "evidence" / "repository-snapshots"
OUT_JSON = ROOT / "evidence" / "metrics" / "mediation-census.json"
OUT_CSV = ROOT / "evidence" / "metrics" / "mediation-census.csv"

LOWER_BOUND_CAVEAT = (
    "These counts are an exact tally of a raw API field combination, but as "
    "a signal about who authored an item they are asymmetric, not a "
    "complete census. `performed_via_github_app: null` does NOT prove "
    "direct human authorship: any PAT-holding process (gh CLI, an "
    "orchestrator, a harness) also yields null. Verifiable primary evidence: "
    "`gh api repos/uda-lab/KSE2026/issues/59/comments` shows comment ids "
    "5071442579 (\"Final proposal gate for head \\u2026\") and 5065764557 / "
    "5066112755 / 5071134565 / 5071234655 / 5071326489 / 5071415951 "
    "(\"@codex please review this PR\") all posted under login `t-uda` with "
    "performed_via_github_app null — i.e. null spans both possibly-direct "
    "and demonstrably-process-generated comments, so a null count is "
    "neither a lower nor an upper bound on direct human authorship. "
    "Conversely, a non-null performed_via_github_app slug IS a LOWER BOUND "
    "on mediated (connector-transmitted) authorship, but proves only the "
    "transport channel — not who composed the prose, nor whether the human "
    "read it before it was posted. No client, user-agent, IP, session id, "
    "model version, or prompt is recoverable from this data. Comment edit "
    "history is not retroactively available, and deleted/minimized comments "
    "are absent from the export. Do not infer productivity, effectiveness, "
    "or causation from these counts."
)

CAVEAT_REF = (
    "count_exact is an exact tally, not itself a bound; as an authorship "
    "signal it is asymmetric (non-null performed_via_github_app is a LOWER "
    "BOUND on mediation; null is NOT proof of direct human authorship) — "
    "see lower_bound_caveat in mediation-census.json / "
    "analysis/mediation-census-methodology.md"
)


def category_key(login, via_app_slug):
    """Return (login, via_app_slug, is_bot) — the grouping key."""
    login = login or "<none>"
    is_bot = login.endswith("[bot]")
    return (login, via_app_slug, is_bot)


def load_snapshot(repo_name):
    base = SNAPSHOT_ROOT / repo_name
    export_meta = json.loads((base / "EXPORT.json").read_text(encoding="utf-8"))
    issues = json.loads((base / "issues.json").read_text(encoding="utf-8"))
    comments = json.loads((base / "comments.json").read_text(encoding="utf-8"))
    return export_meta, issues, comments


def tally(rows):
    counts = {}
    for r in rows:
        key = category_key(r.get("user_login"), r.get("performed_via_github_app"))
        counts[key] = counts.get(key, 0) + 1
    out = []
    for (login, via_app_slug, is_bot), count in sorted(
        counts.items(), key=lambda kv: (kv[0][0], kv[0][1] or "")
    ):
        out.append({
            "login": login,
            "performed_via_github_app": via_app_slug,
            "is_bot_account": is_bot,
            "count_exact": count,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", action="append", dest="repos",
                     default=None,
                     help="repo short name under evidence/repository-snapshots/ "
                          "(repeatable; default: leray-hopf and KSE2026)")
    args = ap.parse_args()
    repo_names = args.repos or ["leray-hopf", "KSE2026"]

    by_repo = {}
    csv_rows = []
    for repo_name in repo_names:
        export_meta, issues, comments = load_snapshot(repo_name)
        issue_census = tally(issues)
        comment_census = tally(comments)
        by_repo[repo_name] = {
            "repo": export_meta["repo"],
            "private": export_meta.get("private"),
            "head_sha_at_fetch": export_meta["head_sha_at_fetch"],
            "fetched_at": export_meta["fetched_at"],
            "issues_and_prs": {"total": len(issues), "categories": issue_census},
            "comments": {"total": len(comments), "categories": comment_census},
        }
        for item_type, census in (("issue_or_pr", issue_census),
                                   ("comment", comment_census)):
            for row in census:
                csv_rows.append({
                    "repo": export_meta["repo"],
                    "item_type": item_type,
                    "login": row["login"],
                    "performed_via_github_app": row["performed_via_github_app"] or "",
                    "is_bot_account": row["is_bot_account"],
                    "count_exact": row["count_exact"],
                    "caveat_ref": CAVEAT_REF,
                })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": "grouped by (user_login, performed_via_github_app slug or "
                  "null) over issues.json and comments.json from "
                  "evidence/repository-snapshots/<repo>/; login values ending "
                  "in '[bot]' are flagged is_bot_account regardless of "
                  "performed_via_github_app.",
        "lower_bound_caveat": LOWER_BOUND_CAVEAT,
        "by_repo": by_repo,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "repo", "item_type", "login", "performed_via_github_app",
            "is_bot_account", "count_exact", "caveat_ref",
        ])
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)

    print(f"{OUT_JSON.relative_to(ROOT)}: {len(repo_names)} repo(s)", file=sys.stderr)
    print(f"{OUT_CSV.relative_to(ROOT)}: {len(csv_rows)} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
