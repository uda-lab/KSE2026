#!/usr/bin/env python3
"""Join ChatGPT-export candidate conversations to GitHub Connector writes (issue #70).

Reads `candidates.json` (produced by `scripts/extract_chatgpt_export.py`) and
`evidence/repository-snapshots/<repo>/{issues,comments,reviews}.json` (produced
by `scripts/export_repo_snapshot.py`), and attempts to link each GitHub
Connector-routed artifact (an issue/PR creation or a comment posted with
`performed_via_github_app == "chatgpt-codex-connector"`, plus every PR review
regardless of attribution — see the reviews caveat below) to the ChatGPT
message that most plausibly produced it.

Q1 (established by schema inventory, see extractor's inventory.json): the
export carries no tool-role messages and no connector/tool-call payload, so
no join tier here is a direct attestation of a Connector write. Every tier is
text-based circumstantial evidence with a documented confidence level; this
script never asserts a tier stronger than what the data supports.

Join universe: the "connector-routed universe" is the set of issue/PR
creations and comments with `performed_via_github_app ==
"chatgpt-codex-connector"`, recomputed fresh from the snapshots on each run
(never hardcoded). PR reviews are *always* included as their own artifact
kind but are NOT part of the connector-routed universe count: the GitHub
Reviews API does not return `performed_via_github_app`, so routing cannot be
established one way or the other for them (documented, not glossed).
Non-connector-routed issues/PRs/comments ("outside-universe") are only
checked against the two exact tiers, flagged separately, and excluded from
the coverage denominator — see `--help` and the design plan for issue #70.

Tier hierarchy (first tier that fires wins; a tie within a tier is
`ambiguous`, never promoted or silently dropped):
  1. exact-id       comment_anchor_id (from a `#issuecomment-NNN` /
                     `#pullrequestreview-NNN` URL fragment in the export)
                     equals the snapshot comment/review id. Confidence high.
  2. exact-body     a normalized-hash of the artifact's posted body (or, for
                     issue/PR creation, `title\n\nbody`) equals a normalized
                     hash of a candidate message (whole message, a fenced
                     code block, or the message minus its first heading
                     line). Requires the hash to be unique on the snapshot
                     side; a snapshot-side collision downgrades the tied
                     artifacts to `ambiguous` rather than guessing. Multiple
                     matching messages on the export side are not
                     ambiguous — the earliest message wins. Confidence high.
                     Caveat: snapshot bodies are email-scrubbed by
                     export_repo_snapshot.py's `scrub()`, so a body
                     containing a scrubbed email can never hash-match.
  3. time-and-context  the artifact's `(repo, number)` is mentioned by a
                     candidate message within +/- `--window-minutes` of the
                     artifact's `created_at`, and every in-window mention of
                     that (repo, number) across all candidates comes from a
                     single conversation. Two-plus conversations in-window
                     is `ambiguous`, not a coin flip. Confidence medium.
  4. reconstructed   the artifact's `created_at` falls inside a candidate
                     conversation's message-timestamp span and that
                     conversation mentions the repo (not necessarily the
                     specific number). Never counted as exact evidence.
                     Confidence low.
  5. unmatched       none of the above.

`authorization_present` in {yes, not-found, n/a, yes-rejected}: conservative
by construction, never `no`. `yes` requires a user-role message strictly
earlier than the artifact's `created_at`, reachable by walking parent
pointers from the matched message AND from the conversation's live-path leaf
(`current_node`) — an edit-branch conversation can carry the authorizing
instruction on either branch — that carries an action-verb lexicon hit AND
mentions the artifact's repo (via `url_refs`, `text_mentions`, or the bare
`bare_repo_mentions` a natural-language instruction leaves when it names the
repo without a URL or #number). `n/a` covers `reconstructed` and `unmatched`
rows, which have no single matched message to search from. Every `yes` row
must be human-spot-checked privately (`--with-text-preview` on the
extractor) before being treated as evidence — this script only proposes the
candidate, it does not adjudicate it. `yes-rejected` is applied by
`AUTHORIZATION_SPOT_CHECK_OVERRIDES` below: a human spot-check disproved a
mechanically-produced `yes` (e.g. the instruction-verb lexicon cannot detect
negation, and hit on a sentence that actually withheld authorization) —
the public artifact must show the disproven verdict rather than either
silently repeating an unreviewed "yes" or erasing the fact that automation
flagged the row at all (PR #82 review finding).

Redaction: rows never carry raw conversation text. `conversation_id_hash` is
the first 16 hex chars of `sha256("KSE2026-i70:" + conversation_id)` — a
documented salted pseudonym, not the raw id. `--emit-public` additionally
drops the raw `conversation_id`/`msg_id` fields entirely, keeping only the
hash and `message_timestamp`.

Usage:
  python3 scripts/join_connector_linkage.py \\
    --candidates /private/derived/KSE2026/chatgpt-export/candidates.json \\
    [--snapshot-root evidence/repository-snapshots] [--window-minutes 60] \\
    --private-report /private/derived/KSE2026/chatgpt-export/linkage-report.md \\
    [--emit-public]

`--snapshot-root` is repeatable; when a repo/file exists under more than one
root, the first root that has it wins (so a private root can supply a
snapshot — e.g. leray-hopf-notes, or a reviews.json refresh for an
already-committed repo — without touching the committed one).
"""
import argparse
import csv
import hashlib
import json
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT_ROOT = REPO_ROOT / "evidence" / "repository-snapshots"
DEFAULT_PUBLIC_JSON = REPO_ROOT / "evidence" / "metrics" / "connector-linkage.json"
DEFAULT_PUBLIC_CSV = REPO_ROOT / "evidence" / "metrics" / "connector-linkage.csv"

CONNECTOR_SLUG = "chatgpt-codex-connector"
ID_SALT = "KSE2026-i70:"

# Issue #70 investigates posts from the authenticated t-uda account attributed
# to the connector -- NOT the connector's own bot identity
# (chatgpt-codex-connector[bot]) posting its own automated review comments,
# which is a distinct mediation channel with performed_via_github_app set to
# the same slug for an unrelated reason (see
# analysis/mediation-census-methodology.md and compute_mediation_census.py's
# is_bot_account convention: login suffix "[bot]"). Excluding bot-authored
# rows here matters: including them roughly doubled the leray-hopf comment
# count during development (69 bot rows vs 37 t-uda-via-connector rows) and
# would silently conflate two different provenance questions.
def _is_connector_routed_human_post(row) -> bool:
    login = row.get("user_login") or ""
    return (row.get("performed_via_github_app") == CONNECTOR_SLUG
            and not login.endswith("[bot]"))
SNAPSHOT_FILES = ("issues.json", "comments.json", "reviews.json")
UNIVERSE_KINDS = ("issue_creation", "pr_creation", "issue_comment", "pr_review")
TIERS = ("exact-id", "exact-body", "time-and-context", "reconstructed", "ambiguous", "unmatched")
WINDOW_SENSITIVITY_MINUTES = (30, 60, 120)

CAVEAT_REF = (
    "Q1 negative (no tool-role messages / connector payload in the export; "
    "see extractor inventory.json): every tier below exact-id/exact-body is "
    "circumstantial text-based evidence, not a direct attestation of a "
    "Connector write. pr_review rows are not filterable by connector "
    "routing (Reviews API omits performed_via_github_app) and are excluded "
    "from the connector-routed universe count. See "
    "analysis/connector-linkage-methodology.md."
)


# ---------------------------------------------------------------------------
# Shared normalization (imported by scripts/extract_chatgpt_export.py so both
# sides of the join hash text identically).
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """NFC -> CRLF/CR to LF -> strip trailing whitespace per line -> collapse
    runs of blank lines to one -> strip leading/trailing blank lines."""
    if not text:
        return ""
    t = unicodedata.normalize("NFC", text)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in t.split("\n")]
    collapsed = []
    prev_blank = False
    for ln in lines:
        blank = (ln == "")
        if blank and prev_blank:
            continue
        collapsed.append(ln)
        prev_blank = blank
    return "\n".join(collapsed).strip()


def normalized_hash(text: str):
    """sha256 hex digest of normalize(text), or None if the normalized text
    is shorter than 64 chars (too short to be a meaningful body match)."""
    t = normalize(text)
    if len(t) < 64:
        return None
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def conversation_id_hash(conversation_id: str) -> str:
    return hashlib.sha256((ID_SALT + conversation_id).encode("utf-8")).hexdigest()[:16]


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Snapshot loading
# ---------------------------------------------------------------------------

def discover_repos(roots):
    repos = set()
    for root in roots:
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if child.is_dir():
                    repos.add(child.name)
    return sorted(repos)


def load_repo_snapshot(repo, roots):
    """Load issues/comments/reviews for `repo`, first root that has the file
    wins per file (not per repo) so a private root can supply just
    reviews.json on top of a publicly-committed issues/comments pair."""
    data = {}
    sources = {}
    for fname in SNAPSHOT_FILES:
        key = fname.split(".")[0]
        found = None
        for root in roots:
            p = root / repo / fname
            if p.is_file():
                found = p
                break
        if found is not None:
            data[key] = json.loads(found.read_text(encoding="utf-8"))
            sources[key] = str(found)
        else:
            data[key] = []
            sources[key] = None
    return data, sources


def build_artifacts(repo, snap):
    """Return (universe, outside_universe) artifact dicts for one repo.
    `_body`/`_title` are transient (used only to compute hashes) and are
    stripped before any row is written out."""
    universe, outside = [], []
    for row in snap["issues"]:
        kind = "pr_creation" if row.get("kind") == "pr" else "issue_creation"
        connector_routed = _is_connector_routed_human_post(row)
        art = {
            "repo": repo, "artifact_kind": kind, "artifact_number": row["number"],
            "artifact_id": None, "created_at": row["created_at"],
            "connector_routed": connector_routed,
            "_body": row.get("body") or "", "_title": row.get("title") or "",
        }
        (universe if connector_routed else outside).append(art)
    for row in snap["comments"]:
        connector_routed = _is_connector_routed_human_post(row)
        art = {
            "repo": repo, "artifact_kind": "issue_comment",
            "artifact_number": row["issue_number"], "artifact_id": row["id"],
            "created_at": row["created_at"], "connector_routed": connector_routed,
            "_body": row.get("body") or "", "_title": "",
        }
        (universe if connector_routed else outside).append(art)
    for row in snap.get("reviews", []):
        art = {
            "repo": repo, "artifact_kind": "pr_review",
            "artifact_number": row["pr_number"], "artifact_id": row["id"],
            "created_at": row["submitted_at"], "connector_routed": None,
            "_body": row.get("body") or "", "_title": "",
        }
        universe.append(art)  # always in universe; excluded from the connector-routed count
    return universe, outside


def artifact_hashes(art):
    hs = set()
    h = normalized_hash(art["_body"])
    if h:
        hs.add(h)
    if art["_title"]:
        h2 = normalized_hash(f"{art['_title']}\n\n{art['_body']}")
        if h2:
            hs.add(h2)
    return hs


def artifact_key(art):
    return (art["repo"], art["artifact_kind"], art["artifact_number"], art["artifact_id"])


# Manually spot-checked authorization_present=yes candidates (issue #70,
# 2026-07-26): every "yes" this pipeline has ever produced was hand-checked
# with --with-text-preview before being trusted (see
# analysis/connector-linkage-methodology.md's authorization_present
# section). This table is an append-only, human-reviewed OVERRIDE applied
# after automatic resolution, keyed on the artifact identity -- it is not a
# live filter, and a future run's "yes" NOT listed here is UNREVIEWED and
# must be spot-checked the same way before being trusted (see the docstring
# at the top of this module). Reasons are categorical, never a text excerpt.
#
# Update 2026-07-26 (same PR, after adding bare_repo_mentions to the
# authorization check per review): the broader repo-mention signal raised
# "yes" from 3 to 134 rows tracing to only 10 distinct trigger messages
# across 7 conversations (many artifacts in one conversation share a single
# early standing instruction as their nearest qualifying ancestor -- this is
# by construction, not a bug). All 10 triggers were read. 8/10 are
# unconditional standing instructions ("review new PRs and merge when
# clean", "audit the whole repo", etc.) with no negation -- left as "yes",
# though note this only means "a repo-relevant instruction preceded it",
# not "the owner specifically pre-approved this exact write" (see
# methodology doc). The other 2/10 explicitly DEFER issue-filing pending a
# report ("don't file the issue yet -- report to me first" / "report to me
# before creating an issue"). Of the 20 rows under those two triggers, the 3
# that are literally `issue_creation` directly contradict their trigger's
# specific deferral and are overridden below; the remaining 17 (comment/
# review/PR-creation -- a different action type than what was deferred) are
# left as "yes" but flagged as a genuine interpretive ambiguity in the
# methodology doc, not silently resolved either way.
AUTHORIZATION_SPOT_CHECK_OVERRIDES = {
    ("KSE2026", "issue_creation", 61, None): "negated instruction (lexicon cannot detect negation)",
    ("KSE2026", "pr_review", 59, 4775200029): "same ancestor-chain trigger as above",
    ("KSE2026", "pr_review", 59, 4775335214): "same ancestor-chain trigger as above",
    ("leray-hopf", "issue_creation", 178, None):
        "trigger explicitly deferred issue-filing pending a report ('report to me first before creating an issue')",
    ("leray-hopf-notes", "issue_creation", 100, None):
        "trigger explicitly deferred issue-filing pending a report ('don't file the issue yet -- report first')",
    ("leray-hopf-notes", "issue_creation", 63, None):
        "trigger explicitly deferred issue-filing pending a report ('don't file the issue yet -- report first')",
}


def apply_authorization_override(art, auth):
    if auth != "yes":
        return auth, None
    reason = AUTHORIZATION_SPOT_CHECK_OVERRIDES.get(artifact_key(art))
    if reason is None:
        return auth, None
    return "yes-rejected", f"spot-check:{reason}"


# ---------------------------------------------------------------------------
# Candidate-side indices
# ---------------------------------------------------------------------------

def build_anchor_index(conversations):
    """(repo, anchor_string) -> [(conv_id, msg_id, create_time, repo_raw), ...]"""
    idx = defaultdict(list)
    for conv in conversations:
        for msg in conv["messages"]:
            for ref in msg.get("url_refs", []):
                anchor = ref.get("comment_anchor_id")
                if not anchor:
                    continue
                idx[(ref["repo_canonical"], anchor)].append(
                    (conv["conversation_id"], msg["msg_id"], msg["create_time"], ref["repo_raw"]))
    return idx


def build_message_hash_index(conversations):
    """hash -> [(conv_id, msg_id, create_time, variant), ...]"""
    idx = defaultdict(list)
    for conv in conversations:
        for msg in conv["messages"]:
            bh = msg.get("body_hashes")
            if not bh:
                continue
            for variant, val in bh.items():
                values = val if isinstance(val, list) else [val]
                for h in values:
                    idx[h].append((conv["conversation_id"], msg["msg_id"], msg["create_time"], variant))
    return idx


def build_mention_index(conversations):
    """(repo, number) -> sorted [(datetime, conv_id, msg_id, repo_raw), ...]"""
    idx = defaultdict(list)
    for conv in conversations:
        for msg in conv["messages"]:
            t = parse_iso(msg.get("create_time"))
            if t is None:
                continue
            seen = set()
            for ref in msg.get("url_refs", []) + msg.get("text_mentions", []):
                key = (ref["repo_canonical"], ref["number"])
                if key in seen:
                    continue
                seen.add(key)
                idx[key].append((t, conv["conversation_id"], msg["msg_id"], ref["repo_raw"]))
    for k in idx:
        idx[k].sort(key=lambda x: x[0])
    return idx


def build_conversation_spans(conversations):
    """conv_id -> ((min_dt, max_dt) | None, matched_repos_set)"""
    spans = {}
    for conv in conversations:
        times = [parse_iso(m["create_time"]) for m in conv["messages"] if m.get("create_time")]
        span = (min(times), max(times)) if times else None
        spans[conv["conversation_id"]] = (span, set(conv.get("matched_repos") or []))
    return spans


def build_conversation_index(conversations):
    """conv_id -> {msg_id: {parent_id, role, create_time_dt, url_refs,
    text_mentions, bare_repo_mentions, instruction_signals}}, plus
    conv_id -> current_node."""
    conv_msgs = {}
    current_node_of = {}
    for conv in conversations:
        current_node_of[conv["conversation_id"]] = conv.get("current_node")
        by_id = {}
        for msg in conv["messages"]:
            by_id[msg["msg_id"]] = {
                "parent_id": msg.get("parent_id"),
                "role": msg.get("role"),
                "create_time_dt": parse_iso(msg.get("create_time")),
                "url_refs": msg.get("url_refs", []),
                "text_mentions": msg.get("text_mentions", []),
                "bare_repo_mentions": msg.get("bare_repo_mentions", []),
                "instruction_signals": msg.get("instruction_signals", []),
            }
        conv_msgs[conv["conversation_id"]] = by_id
    return conv_msgs, current_node_of


# ---------------------------------------------------------------------------
# Tier resolution
# ---------------------------------------------------------------------------

def _exact_id(art, anchor_idx):
    if art["artifact_kind"] not in ("issue_comment", "pr_review") or art["artifact_id"] is None:
        return None
    anchor = (f"issuecomment-{art['artifact_id']}" if art["artifact_kind"] == "issue_comment"
              else f"pullrequestreview-{art['artifact_id']}")
    hits = anchor_idx.get((art["repo"], anchor))
    if not hits:
        return None
    hits_sorted = sorted(hits, key=lambda h: h[2] or "")
    conv_id, msg_id, ts, repo_raw = hits_sorted[0]
    notes = []
    if len(hits_sorted) > 1:
        notes.append(f"anchor-hits:{len(hits_sorted)}")
    if repo_raw != art["repo"]:
        notes.append(f"alias:{repo_raw}")
    return {"tier": "exact-id", "confidence": "high", "conv_id": conv_id, "msg_id": msg_id,
            "message_timestamp": ts, "notes": ";".join(notes) or None}


def _exact_body(art, snap_hash_index, msg_hash_idx):
    # Check msg_hits BEFORE deciding a snapshot-side collision matters (PR #82
    # review finding): two snapshot artifacts sharing a body hash with no
    # candidate message ever producing that hash is not evidence of anything
    # -- there is no linkage candidate to be ambiguous ABOUT. Marking it
    # ambiguous anyway blocked the artifact from ever falling through to
    # time-and-context/reconstructed, inflating the reported ambiguity count
    # on ordinary snapshot-side duplicates (e.g. repeated boilerplate review
    # bodies) that no message ever referenced.
    collide = False
    for h in artifact_hashes(art):
        msg_hits = msg_hash_idx.get(h)
        if not msg_hits:
            continue
        snap_hits = snap_hash_index.get(h, [])
        if len(snap_hits) > 1:
            collide = True
            continue
        msg_hits_sorted = sorted(msg_hits, key=lambda x: x[2] or "")
        conv_id, msg_id, ts, variant = msg_hits_sorted[0]
        notes = [f"variant:{variant}"]
        if len(msg_hits_sorted) > 1:
            notes.append(f"multihit:{len(msg_hits_sorted)}")
        return {"tier": "exact-body", "confidence": "high", "conv_id": conv_id, "msg_id": msg_id,
                "message_timestamp": ts, "notes": ";".join(notes)}
    if collide:
        return {"tier": "ambiguous", "confidence": None, "conv_id": None, "msg_id": None,
                "message_timestamp": None, "notes": "hash-collision"}
    return None


def _time_and_context(art, mention_idx, window_minutes):
    created_at = parse_iso(art["created_at"])
    if created_at is None:
        return None
    mentions = mention_idx.get((art["repo"], art["artifact_number"]), [])
    if not mentions:
        return None
    window_s = window_minutes * 60
    in_window = [m for m in mentions if abs((m[0] - created_at).total_seconds()) <= window_s]
    if not in_window:
        return None
    convs_involved = {m[1] for m in in_window}
    if len(convs_involved) > 1:
        return {"tier": "ambiguous", "confidence": None, "conv_id": None, "msg_id": None,
                "message_timestamp": None, "notes": f"multi-conversation:{len(convs_involved)}"}
    in_window.sort(key=lambda x: x[0])
    ts, conv_id, msg_id, repo_raw = in_window[0]
    notes = []
    if len(in_window) > 1:
        notes.append(f"mentions:{len(in_window)}")
    if repo_raw != art["repo"]:
        notes.append(f"alias:{repo_raw}")
    return {"tier": "time-and-context", "confidence": "medium", "conv_id": conv_id, "msg_id": msg_id,
            "message_timestamp": ts.isoformat(), "notes": ";".join(notes) or None}


def _reconstructed(art, conv_spans):
    created_at = parse_iso(art["created_at"])
    if created_at is None:
        return None
    qualifying = []
    for conv_id, (span, repos) in conv_spans.items():
        if span is None:
            continue
        lo, hi = span
        if lo <= created_at <= hi and art["repo"] in repos:
            qualifying.append(conv_id)
    if not qualifying:
        return None
    qualifying.sort()
    return {"tier": "reconstructed", "confidence": "low", "conv_id": qualifying[0], "msg_id": None,
            "message_timestamp": None,
            "notes": f"candidates:{len(qualifying)}" if len(qualifying) > 1 else None}


def resolve_artifact(art, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx, conv_spans,
                      window_minutes):
    for fn, args in (
        (_exact_id, (art, anchor_idx)),
        (_exact_body, (art, snap_hash_index, msg_hash_idx)),
        (_time_and_context, (art, mention_idx, window_minutes)),
        (_reconstructed, (art, conv_spans)),
    ):
        result = fn(*args)
        if result is not None:
            return result
    return {"tier": "unmatched", "confidence": None, "conv_id": None, "msg_id": None,
            "message_timestamp": None, "notes": None}


def ancestor_chain(conv_index, start_id):
    ids, seen, cur = [], set(), start_id
    while cur is not None and cur in conv_index and cur not in seen:
        seen.add(cur)
        ids.append(cur)
        cur = conv_index[cur]["parent_id"]
    return ids


def compute_authorization(conv_index, msg_id, current_node, created_at_dt, repo_canonical):
    if created_at_dt is None or msg_id is None:
        return "n/a"
    scope, seen = [], set()
    for start in (msg_id, current_node):
        if start is None:
            continue
        for mid in ancestor_chain(conv_index, start):
            if mid not in seen:
                seen.add(mid)
                scope.append(mid)
    for mid in scope:
        rec = conv_index.get(mid)
        if not rec or rec["role"] != "user":
            continue
        ct = rec["create_time_dt"]
        if ct is None or ct >= created_at_dt:
            continue  # not strictly earlier than the artifact -> cannot authorize it
        # bare_repo_mentions matters here specifically: a natural-language
        # instruction that names the repo without a URL or #number ("KSE2026
        # に issue を作成して") only shows up there, never in url_refs/
        # text_mentions -- omitting it made authorization systematically
        # blind to exactly that phrasing (PR #82 review finding).
        repos_mentioned = {r["repo_canonical"] for r in rec["url_refs"]} | \
            {r["repo_canonical"] for r in rec["text_mentions"]} | \
            set(rec["bare_repo_mentions"])
        if rec["instruction_signals"] and repo_canonical in repos_mentioned:
            return "yes"
    return "not-found"


# ---------------------------------------------------------------------------
# Row construction / reporting
# ---------------------------------------------------------------------------

def build_rows(universe, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx, conv_spans,
               conv_index, current_node_of, window_minutes):
    rows = []
    for art in universe:
        res = resolve_artifact(art, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx,
                                conv_spans, window_minutes)
        conv_id = res.get("conv_id")
        msg_id = res.get("msg_id")
        created_at_dt = parse_iso(art["created_at"])
        auth = "n/a"
        if conv_id is not None and msg_id is not None and res["tier"] in (
                "exact-id", "exact-body", "time-and-context"):
            auth = compute_authorization(conv_index.get(conv_id, {}), msg_id,
                                          current_node_of.get(conv_id), created_at_dt, art["repo"])
        auth, override_note = apply_authorization_override(art, auth)
        notes = res.get("notes")
        if override_note:
            notes = ";".join(x for x in (notes, override_note) if x)
        rows.append({
            "repo": art["repo"],
            "artifact_kind": art["artifact_kind"],
            "artifact_number": art["artifact_number"],
            "artifact_id": art["artifact_id"],
            "artifact_created_at": art["created_at"],
            "connector_routed": art["connector_routed"],
            "join_method": res["tier"],
            "confidence": res["confidence"],
            "conversation_id": conv_id,
            "conversation_id_hash": conversation_id_hash(conv_id) if conv_id else None,
            "msg_id": msg_id,
            "message_timestamp": res.get("message_timestamp"),
            "authorization_present": auth,
            "notes": notes,
        })
    return rows


def outside_universe_matches(outside, anchor_idx, snap_hash_index, msg_hash_idx):
    hits = []
    for art in outside:
        res = _exact_id(art, anchor_idx) or _exact_body(art, snap_hash_index, msg_hash_idx)
        if res is not None and res["tier"] in ("exact-id", "exact-body"):
            row = dict(res)
            row.update({"repo": art["repo"], "artifact_kind": art["artifact_kind"],
                        "artifact_number": art["artifact_number"], "artifact_id": art["artifact_id"]})
            row["notes"] = ";".join(x for x in (row.get("notes"), "outside-universe") if x)
            row["conversation_id_hash"] = conversation_id_hash(row["conv_id"]) if row.get("conv_id") else None
            hits.append(row)
    return hits


def coverage_table(rows, connector_only=True):
    table = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if connector_only and r["connector_routed"] is not True:
            continue
        table[(r["repo"], r["artifact_kind"])][r["join_method"]] += 1
    out = []
    for (repo, kind), tiers in sorted(table.items()):
        row = {"repo": repo, "artifact_kind": kind, "total": sum(tiers.values())}
        for t in TIERS:
            row[t] = tiers.get(t, 0)
        out.append(row)
    return out


def window_sensitivity(universe, mention_idx, anchor_idx, snap_hash_index, msg_hash_idx, widths):
    """For universe artifacts not already resolved by an exact tier, count
    how many would land in time-and-context vs ambiguous at each width."""
    remaining = []
    for art in universe:
        if _exact_id(art, anchor_idx) is not None:
            continue
        if _exact_body(art, snap_hash_index, msg_hash_idx) is not None:
            continue
        remaining.append(art)
    out = {}
    for w in widths:
        counts = defaultdict(int)
        for art in remaining:
            res = _time_and_context(art, mention_idx, w)
            if res is None:
                counts["none"] += 1
            elif res["tier"] == "ambiguous":
                counts["ambiguous"] += 1
            else:
                counts["time-and-context"] += 1
        out[w] = dict(counts)
    return out


def render_private_report(meta, coverage_all, coverage_connector, universe_size_connector,
                           outside_hits, window_sens, rows):
    lines = []
    lines.append("# Connector linkage — private join report (issue #70)")
    lines.append("")
    lines.append(f"generated_at: {meta['generated_at']}")
    lines.append(f"candidates: {meta['candidates_path']}")
    lines.append(f"snapshot_roots: {', '.join(meta['snapshot_roots'])}")
    lines.append(f"window_minutes (fixed tier assignment): {meta['window_minutes']}")
    lines.append("")
    lines.append(f"## Connector-routed universe size (recomputed): {universe_size_connector}")
    lines.append("")
    lines.append("pr_review rows are listed separately below and excluded from this count "
                  "(Reviews API omits performed_via_github_app; see script docstring).")
    lines.append("")
    lines.append("## Coverage — connector-routed universe only")
    lines.append("")
    lines.append("| repo | artifact_kind | total | " + " | ".join(TIERS) + " |")
    lines.append("|---" * (3 + len(TIERS)) + "|")
    for row in coverage_connector:
        lines.append("| " + " | ".join(str(row[k]) for k in
                      ("repo", "artifact_kind", "total", *TIERS)) + " |")
    lines.append("")
    lines.append("## Coverage — all universe rows incl. pr_review (connector routing not "
                  "asserted for pr_review)")
    lines.append("")
    lines.append("| repo | artifact_kind | total | " + " | ".join(TIERS) + " |")
    lines.append("|---" * (3 + len(TIERS)) + "|")
    for row in coverage_all:
        lines.append("| " + " | ".join(str(row[k]) for k in
                      ("repo", "artifact_kind", "total", *TIERS)) + " |")
    lines.append("")
    lines.append("## Outside-universe exact matches (flagged, not in coverage denominator)")
    lines.append("")
    if outside_hits:
        lines.append("| repo | artifact_kind | number | id | tier | conversation_id | msg_id | notes |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for h in outside_hits:
            lines.append("| " + " | ".join(str(h.get(k)) for k in
                          ("repo", "artifact_kind", "artifact_number", "artifact_id", "tier",
                           "conv_id", "msg_id", "notes")) + " |")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## Window sensitivity (unresolved-after-exact-tiers artifacts only)")
    lines.append("")
    lines.append("| window_minutes | time-and-context | ambiguous | none |")
    lines.append("|---|---|---|---|")
    for w in sorted(window_sens):
        c = window_sens[w]
        lines.append(f"| {w} | {c.get('time-and-context', 0)} | {c.get('ambiguous', 0)} | {c.get('none', 0)} |")
    lines.append("")
    lines.append("## authorization_present = yes (spot-check every row before treating as evidence)")
    lines.append("")
    yes_rows = [r for r in rows if r["authorization_present"] == "yes"]
    if yes_rows:
        lines.append("| repo | artifact_kind | number | id | tier | conversation_id | msg_id | "
                      "message_timestamp | spot_check_verdict |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for r in yes_rows:
            lines.append("| " + " | ".join(str(r.get(k)) for k in
                          ("repo", "artifact_kind", "artifact_number", "artifact_id", "join_method",
                           "conversation_id", "msg_id", "message_timestamp")) + " | TBD |")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## authorization_present = yes-rejected (already spot-checked and disproven; "
                  "see AUTHORIZATION_SPOT_CHECK_OVERRIDES)")
    lines.append("")
    rejected_rows = [r for r in rows if r["authorization_present"] == "yes-rejected"]
    if rejected_rows:
        lines.append("| repo | artifact_kind | number | id | tier | notes |")
        lines.append("|---|---|---|---|---|---|")
        for r in rejected_rows:
            lines.append("| " + " | ".join(str(r.get(k)) for k in
                          ("repo", "artifact_kind", "artifact_number", "artifact_id", "join_method",
                           "notes")) + " |")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## All rows")
    lines.append("")
    lines.append("| repo | kind | number | id | tier | confidence | auth | conversation_id_hash | "
                  "message_timestamp | notes |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(k)) for k in
                      ("repo", "artifact_kind", "artifact_number", "artifact_id", "join_method",
                       "confidence", "authorization_present", "conversation_id_hash",
                       "message_timestamp", "notes")) + " |")
    return "\n".join(lines) + "\n"


PUBLIC_ROW_FIELDS = ("conversation_id_hash", "message_timestamp", "repo", "artifact_kind",
                      "artifact_number", "artifact_id", "join_method", "confidence",
                      "authorization_present", "notes")
PUBLIC_CSV_HEADER = ("conversation_id_hash", "message_timestamp", "repository", "artifact_kind",
                      "artifact_number", "artifact_id", "join_method", "confidence",
                      "authorization_present", "notes", "caveat_ref")


def public_rows(rows):
    out = []
    for r in rows:
        out.append({k: r.get(k) for k in PUBLIC_ROW_FIELDS})
    return out


def emit_public(rows, coverage_connector, coverage_all, universe_size_connector, json_out, csv_out):
    doc = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": "scripts/join_connector_linkage.py --emit-public; see docstring for tier "
                  "definitions and the Q1 no-tool-role-message caveat",
        "caveat": CAVEAT_REF,
        "connector_routed_universe_size": universe_size_connector,
        "coverage_connector_routed_only": coverage_connector,
        "coverage_all_incl_pr_review": coverage_all,
        "rows": public_rows(rows),
    }
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                         encoding="utf-8")
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(PUBLIC_CSV_HEADER)
        for r in rows:
            writer.writerow([
                r.get("conversation_id_hash"), r.get("message_timestamp"), r.get("repo"),
                r.get("artifact_kind"), r.get("artifact_number"), r.get("artifact_id"),
                r.get("join_method"), r.get("confidence"), r.get("authorization_present"),
                r.get("notes"), CAVEAT_REF,
            ])
    return doc


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def run(candidates_path, snapshot_roots, window_minutes):
    """Core pipeline, split out from main() so tests and callers can invoke
    it without going through argparse or the filesystem CLI surface."""
    doc = json.loads(Path(candidates_path).read_text(encoding="utf-8"))
    conversations = doc["conversations"]

    anchor_idx = build_anchor_index(conversations)
    msg_hash_idx = build_message_hash_index(conversations)
    mention_idx = build_mention_index(conversations)
    conv_spans = build_conversation_spans(conversations)
    conv_index, current_node_of = build_conversation_index(conversations)

    repos = discover_repos(snapshot_roots)
    universe, outside = [], []
    snap_sources = {}
    for repo in repos:
        snap, sources = load_repo_snapshot(repo, snapshot_roots)
        snap_sources[repo] = sources
        u, o = build_artifacts(repo, snap)
        universe.extend(u)
        outside.extend(o)

    snap_hash_index = defaultdict(list)
    for art in universe + outside:
        for h in artifact_hashes(art):
            snap_hash_index[h].append(artifact_key(art))

    rows = build_rows(universe, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx, conv_spans,
                       conv_index, current_node_of, window_minutes)
    outside_hits = outside_universe_matches(outside, anchor_idx, snap_hash_index, msg_hash_idx)

    coverage_connector = coverage_table(rows, connector_only=True)
    coverage_all = coverage_table(rows, connector_only=False)
    universe_size_connector = sum(1 for a in universe if a["connector_routed"] is True)
    window_sens = window_sensitivity(universe, mention_idx, anchor_idx, snap_hash_index,
                                      msg_hash_idx, WINDOW_SENSITIVITY_MINUTES)

    return {
        "rows": rows, "outside_hits": outside_hits,
        "coverage_connector": coverage_connector, "coverage_all": coverage_all,
        "universe_size_connector": universe_size_connector, "window_sensitivity": window_sens,
        "snap_sources": snap_sources, "repos": repos,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidates", required=True, type=Path)
    ap.add_argument("--snapshot-root", dest="snapshot_roots", action="append", type=Path,
                     default=None)
    ap.add_argument("--window-minutes", type=int, default=60)
    ap.add_argument("--private-report", required=True, type=Path)
    ap.add_argument("--emit-public", action="store_true")
    ap.add_argument("--public-json-out", type=Path, default=DEFAULT_PUBLIC_JSON)
    ap.add_argument("--public-csv-out", type=Path, default=DEFAULT_PUBLIC_CSV)
    args = ap.parse_args()

    snapshot_roots = args.snapshot_roots or [DEFAULT_SNAPSHOT_ROOT]
    result = run(args.candidates, snapshot_roots, args.window_minutes)

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "candidates_path": str(args.candidates),
        "snapshot_roots": [str(r) for r in snapshot_roots],
        "window_minutes": args.window_minutes,
    }
    report = render_private_report(meta, result["coverage_all"], result["coverage_connector"],
                                    result["universe_size_connector"], result["outside_hits"],
                                    result["window_sensitivity"], result["rows"])
    args.private_report.parent.mkdir(parents=True, exist_ok=True)
    args.private_report.write_text(report, encoding="utf-8")
    print(f"{args.private_report}: {len(result['rows'])} universe rows, "
          f"{len(result['outside_hits'])} outside-universe exact matches", file=sys.stderr)
    print(f"connector-routed universe size: {result['universe_size_connector']}", file=sys.stderr)

    if args.emit_public:
        emit_public(result["rows"], result["coverage_connector"], result["coverage_all"],
                    result["universe_size_connector"], args.public_json_out, args.public_csv_out)
        print(f"{args.public_json_out}, {args.public_csv_out}: public emit written", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
