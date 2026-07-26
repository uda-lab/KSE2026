#!/usr/bin/env python3
"""Extract connector-linkage candidate conversations from a ChatGPT data export (issue #70).

Streams the export zip one shard (`conversations-NNN.json`) at a time —
`zf.open()` -> `json.load()` -> `del` -> `gc.collect()` — never extracts to
disk, and never reads `user.json` values (existence only, for the inventory).
This matters on this container: the cgroup memory limit is ~3.4 GiB and a
shard is tens of MB of JSON.

Schema facts (established by read-only inventory, re-derived and recorded
into `inventory.json` on every run rather than trusted from memory): each
conversation's `mapping` is `{node_id: {id, message, parent}}` with NO
`children` key — the tree must be rebuilt from `parent` pointers. Nodes with
`message: null` are (typically root) placeholders. `message.author.role` is
only ever `"user"` or `"assistant"` — no tool role, no connector/tool-call
payload anywhere in this export, which is why every downstream join tier in
`scripts/join_connector_linkage.py` is text-based circumstantial evidence,
never a direct Connector attestation. `message.author.name` is always null.

Per-message output is compact and text-free by default: `conversation_id,
msg_id, parent_id, role, create_time (ISO UTC), content_type, on_live_path,
text_len`, plus derived fields that never carry raw text themselves —
`url_refs`, `text_mentions`, `bare_repo_mentions` (a repo name appearing
anywhere, no URL or #number required — the per-message counterpart of the
candidate-selection token match, so a natural-language instruction like
"KSE2026 に issue を作成して" is still visible to authorization checking),
`body_hashes` (assistant only, via the shared `normalize()`/
`normalized_hash()` in `scripts/join_connector_linkage.py`), and
`instruction_signals` (user only, lexicon *hits*, not the surrounding text).
`--with-text-preview N` adds truncated previews for PRIVATE manual
verification only — never pass it when the output might leave
`/private/derived/`.

Candidate selection: a conversation is kept iff (a) at least one message has
`create_time >= --since`, AND (b) some message mentions one of the target
repo tokens (`leray-hopf`, `leray-hopf-notes`, `lean-pde`, `lean-pde-notes`,
`KSE2026` — old and new names both, since May-and-earlier history predates
the leray-hopf rename) OR the generic `uda-lab` org token. The `match_tier`
field on each kept conversation records which: `"tight"` for a specific-repo
mention, `"wide"` for a bare `uda-lab` mention with no target-repo token
matched anywhere in the conversation. Both are LITERAL SUBSTRING checks —
deliberately broader than `url_refs`/`text_mentions` below (which require a
full GitHub URL or a `repo#number` form): candidate selection needs to catch
prose references, `gh` CLI invocations (`repos/uda-lab/leray-hopf/...`), and
SSH-style git remotes for the org that never spell out
`https://github.com/...`. Empirically, the strict `github.com/uda-lab/`
substring alone under-matched the read-only inventory's established
tight=~20/wide=~79 baseline by roughly half; the bare-token substrings used
here reproduce it closely (see inventory.json for the actual recount).

Also emits `inventory.json` alongside `--out`: shard/key-set documentation
(conversation/node/message/author key sets, the observed `content_type` and
`role` enums, whether `author.name` is uniformly null) recomputed from the
actual export on every run — this is the source for the paper's Q1 schema
answer, not a hand-written claim. A `codex.json` count-only footnote is
included (86 `t-uda/*` personal-repo Codex cloud tasks per the plan's
read-only inventory; this script re-counts rather than trusting that number).

Usage:
  python3 scripts/extract_chatgpt_export.py \\
    --export /private/sources/KSE2026/OpenAI-ChatGPT-export.20270726.zip \\
    --out /private/derived/KSE2026/chatgpt-export/candidates.json \\
    [--since 2026-06-01T00:00:00+00:00] [--with-text-preview N]
"""
import argparse
import gc
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.join_connector_linkage import normalize, normalized_hash  # noqa: E402

SHARD_RE = re.compile(r"^conversations-(\d+)\.json$")

# lean-pde(-notes) were renamed to leray-hopf(-notes) on GitHub; a rename
# preserves the issue/PR number space (spot-verified separately against the
# snapshots, not assumed here), so token substitution is sufficient.
REPO_ALIAS = {
    "lean-pde-notes": "leray-hopf-notes",
    "lean-pde": "leray-hopf",
}
# Longest-first so "leray-hopf-notes" is not shadowed by a prefix match on
# "leray-hopf" (and likewise for the lean-pde pair).
TARGET_REPO_TOKENS = ["leray-hopf-notes", "leray-hopf", "lean-pde-notes", "lean-pde", "KSE2026"]
_REPO_ALT = "|".join(re.escape(t) for t in TARGET_REPO_TOKENS)

# Structured extraction for the join tiers in scripts/join_connector_linkage.py
# (need a specific issue/PR number, and optionally a comment/review anchor).
URL_REF_RE = re.compile(
    r"github\.com/uda-lab/(" + _REPO_ALT + r")/(issues|pull)/(\d+)"
    r"(?:#(issuecomment-\d+|discussion_r\d+|pullrequestreview-\d+))?",
    re.IGNORECASE)
TEXT_MENTION_RE = re.compile(r"\b(" + _REPO_ALT + r")#(\d+)\b", re.IGNORECASE)

# Broad, bare-substring tokens for candidate SELECTION only (see docstring):
# no URL or issue number required, just the token appearing anywhere.
REPO_TOKEN_RE = re.compile(r"(" + _REPO_ALT + r")", re.IGNORECASE)
WIDE_TOKEN_RE = re.compile(r"\buda-lab\b", re.IGNORECASE)

# Documented JP+EN action-verb lexicon for `instruction_signals` (user
# messages only). Extend this tuple, never special-case a conversation.
ACTION_VERB_LEXICON = (
    "起票", "投稿", "作成", "コメント", "レビュー", "提出", "報告", "依頼", "お願い",
    "post", "create", "comment", "review", "open an issue", "file an issue",
    "submit", "reply", "publish", "request review", "@codex",
)

# content_type values whose extracted text is plausible "could have been
# posted verbatim" material; thoughts/reasoning_recap are chain-of-thought,
# excluded from body_hashes (a posted GitHub body was never that).
POSTABLE_CONTENT_TYPES = {"text", "multimodal_text", "code"}

FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
HEADING_LINE_RE = re.compile(r"^\s{0,3}#{1,6}\s")


# Lowercased lookup tables so canonicalization is fully case-insensitive on
# input: both regexes above are re.IGNORECASE, so a match can arrive in any
# casing (e.g. "kse2026#61", "LERAY-HOPF"). Mapping only the two renamed
# aliases and leaving everything else in its as-matched casing (the original
# bug, PR #82 review) meant a same-repo mention could be indexed under two
# different casings and silently fail to join against the snapshot's
# canonically-cased key.
_REPO_ALIAS_LOWER = {old.lower(): new for old, new in REPO_ALIAS.items()}
_CANONICAL_BY_LOWER = {t.lower(): t for t in TARGET_REPO_TOKENS}


def canonical_repo(token: str) -> str:
    low = token.lower()
    if low in _REPO_ALIAS_LOWER:
        return _REPO_ALIAS_LOWER[low]
    return _CANONICAL_BY_LOWER.get(low, token)


def epoch_to_iso(t):
    if t is None:
        return None
    try:
        return datetime.fromtimestamp(float(t), tz=timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def extract_text(content) -> str:
    """Best-effort plain-text join across the export's observed
    content_types, for hashing/scanning only. Never stored raw except as a
    `--with-text-preview`-truncated preview."""
    if not isinstance(content, dict):
        return ""
    ct = content.get("content_type")
    if ct == "text":
        return "\n".join(p for p in (content.get("parts") or []) if isinstance(p, str))
    if ct == "multimodal_text":
        chunks = []
        for p in content.get("parts") or []:
            if isinstance(p, str):
                chunks.append(p)
            elif isinstance(p, dict) and isinstance(p.get("text"), str):
                chunks.append(p["text"])
        return "\n".join(chunks)
    if ct == "code":
        return content.get("text") or ""
    if ct == "thoughts":
        chunks = []
        for th in content.get("thoughts") or []:
            if isinstance(th, dict):
                if isinstance(th.get("content"), str):
                    chunks.append(th["content"])
                if isinstance(th.get("summary"), str):
                    chunks.append(th["summary"])
        return "\n".join(chunks)
    if ct == "reasoning_recap":
        c = content.get("content")
        return c if isinstance(c, str) else ""
    return ""


def fenced_blocks(text: str):
    return [m.group(1) for m in FENCE_RE.finditer(text)]


def minus_first_heading(text: str) -> str:
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == "":
            continue
        if HEADING_LINE_RE.match(ln):
            return "\n".join(lines[:i] + lines[i + 1:])
        break
    return text


def find_url_refs(text: str):
    refs = []
    for m in URL_REF_RE.finditer(text):
        token, kind, number, anchor = m.groups()
        refs.append({
            "repo_canonical": canonical_repo(token),
            "repo_raw": token,
            "kind": "pr" if kind.lower() == "pull" else "issue",
            "number": int(number),
            "comment_anchor_id": anchor,
        })
    return refs


def find_text_mentions(text: str):
    mentions = []
    for m in TEXT_MENTION_RE.finditer(text):
        token, number = m.groups()
        mentions.append({
            "repo_canonical": canonical_repo(token),
            "repo_raw": token,
            "number": int(number),
        })
    return mentions


def find_instruction_signals(text: str):
    low = text.lower()
    hits = []
    for verb in ACTION_VERB_LEXICON:
        needle = verb.lower()
        hit = (needle in low) if needle.isascii() else (verb in text)
        if hit:
            hits.append(verb)
    return hits


def body_hashes_for(text: str):
    hashes = {}
    h = normalized_hash(text)
    if h:
        hashes["whole"] = h
    blocks = [normalized_hash(b) for b in fenced_blocks(text)]
    blocks = sorted({b for b in blocks if b})
    if blocks:
        hashes["fenced_blocks"] = blocks
    mh = normalized_hash(minus_first_heading(text))
    if mh and mh != hashes.get("whole"):
        hashes["minus_first_heading"] = mh
    return hashes


# ---------------------------------------------------------------------------
# Tree rebuild + per-conversation extraction
# ---------------------------------------------------------------------------

def live_path_ids(mapping, current_node):
    """Ancestors of current_node (inclusive) -- the export carries no
    `children` key, so this is a parent-pointer walk, not a descent."""
    ids = set()
    node_id = current_node
    seen = set()
    while node_id is not None and node_id in mapping and node_id not in seen:
        seen.add(node_id)
        ids.add(node_id)
        node_id = mapping[node_id].get("parent")
    return ids


def update_schema(acc, conv, mapping):
    acc["conversation_keys"].update(conv.keys())
    for node in mapping.values():
        acc["node_keys"].update(node.keys())
        msg = node.get("message")
        if msg is None:
            acc["nodes_without_message"] += 1
            continue
        acc["nodes_with_message"] += 1
        acc["message_keys"].update(msg.keys())
        author = msg.get("author") or {}
        acc["author_keys"].update(author.keys())
        acc["roles"].add(author.get("role"))
        acc["author_names"].add(author.get("name"))
        content = msg.get("content") or {}
        acc["content_types"].add(content.get("content_type"))
        acc["metadata_keys"].update((msg.get("metadata") or {}).keys())


def process_conversation(conv, since_epoch, with_preview):
    """Returns a candidate conversation record, or None if it does not pass
    the --since / repo-token filter."""
    conv_id = conv.get("id") or conv.get("conversation_id")
    mapping = conv.get("mapping") or {}
    current_node = conv.get("current_node")
    live_ids = live_path_ids(mapping, current_node)

    messages = []
    conv_create_times = []
    matched_tight = False
    matched_wide = False
    matched_repos = set()

    for node_id, node in mapping.items():
        msg = node.get("message")
        if msg is None:
            continue
        author = msg.get("author") or {}
        role = author.get("role")
        if role not in ("user", "assistant"):
            continue
        content = msg.get("content") or {}
        content_type = content.get("content_type")
        text = extract_text(content)
        raw_create_time = msg.get("create_time")
        create_time_iso = epoch_to_iso(raw_create_time)
        if raw_create_time is not None:
            conv_create_times.append(raw_create_time)

        url_refs = find_url_refs(text)
        text_mentions = find_text_mentions(text)

        # Candidate-selection signal: broad bare-substring tokens (see module
        # docstring) -- a strict superset of what url_refs/text_mentions can
        # ever match, since those require a full URL or a #number suffix.
        # Stored per message (not just aggregated into matched_repos) so
        # scripts/join_connector_linkage.py's authorization check can see a
        # natural-language instruction that names the repo without a URL or
        # #number ("KSE2026 に issue を作成して") -- PR #82 review finding:
        # authorization was previously blind to exactly this phrasing because
        # it only consulted url_refs/text_mentions.
        bare_tokens = REPO_TOKEN_RE.findall(text)
        bare_repo_mentions = sorted({canonical_repo(t) for t in bare_tokens})
        if bare_repo_mentions:
            matched_tight = True
            matched_repos.update(bare_repo_mentions)
        if WIDE_TOKEN_RE.search(text):
            matched_wide = True

        rec = {
            "conversation_id": conv_id,
            "msg_id": msg.get("id") or node_id,
            "parent_id": node.get("parent"),
            "role": role,
            "create_time": create_time_iso,
            "content_type": content_type,
            "on_live_path": node_id in live_ids,
            "text_len": len(text),
            "url_refs": url_refs,
            "text_mentions": text_mentions,
            "bare_repo_mentions": bare_repo_mentions,
        }
        if role == "assistant" and content_type in POSTABLE_CONTENT_TYPES:
            hashes = body_hashes_for(text)
            if hashes:
                rec["body_hashes"] = hashes
        if role == "user":
            sigs = find_instruction_signals(text)
            if sigs:
                rec["instruction_signals"] = sigs
        if with_preview:
            rec["text_preview"] = text[:with_preview]
            rec["text_preview_truncated"] = len(text) > with_preview
        messages.append(rec)

    if not matched_tight and not matched_wide:
        return None
    if since_epoch is not None and not any(t >= since_epoch for t in conv_create_times):
        return None

    messages.sort(key=lambda r: (r["create_time"] or "", str(r["msg_id"])))
    conv_rec = {
        "conversation_id": conv_id,
        "create_time": epoch_to_iso(conv.get("create_time")),
        "update_time": epoch_to_iso(conv.get("update_time")),
        "current_node": current_node,
        "message_count": len(messages),
        "node_count": len(mapping),
        "match_tier": "tight" if matched_tight else "wide",
        "matched_repos": sorted(matched_repos),
        "default_model_slug": conv.get("default_model_slug"),
        "messages": messages,
    }
    if with_preview:
        conv_rec["title_preview"] = (conv.get("title") or "")[:with_preview]
    return conv_rec


def new_schema_acc():
    return {
        "conversation_keys": set(), "node_keys": set(), "message_keys": set(),
        "author_keys": set(), "roles": set(), "author_names": set(),
        "content_types": set(), "metadata_keys": set(),
        "nodes_without_message": 0, "nodes_with_message": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--since", default=None,
                     help="ISO8601 cutoff; keep conversations with >=1 message at/after this time")
    ap.add_argument("--with-text-preview", type=int, default=0, metavar="N",
                     help="include an N-char truncated preview per message/title, for PRIVATE "
                          "manual verification only -- never pass this if the output could leave "
                          "/private/derived/")
    args = ap.parse_args()

    since_epoch = None
    if args.since:
        try:
            since_epoch = datetime.fromisoformat(args.since).timestamp()
        except ValueError:
            print(f"error: unparsable --since {args.since!r}", file=sys.stderr)
            return 1

    if not args.export.is_file():
        print(f"error: export not found: {args.export}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)

    candidates = []
    schema_acc = new_schema_acc()
    shard_stats = []
    total_conversations = 0
    codex_footnote = None
    user_json_present = False

    with zipfile.ZipFile(args.export) as zf:
        names = zf.namelist()
        user_json_present = "user.json" in names  # existence only -- values never read
        if "codex.json" in names:
            with zf.open("codex.json") as f:
                codex_data = json.load(f)
            codex_footnote = {"count": len(codex_data) if isinstance(codex_data, list) else None}
            del codex_data
            gc.collect()

        shard_names = sorted((n for n in names if SHARD_RE.match(n)),
                              key=lambda n: int(SHARD_RE.match(n).group(1)))
        for shard in shard_names:
            with zf.open(shard) as f:
                data = json.load(f)
            shard_conv_count = len(data)
            total_conversations += shard_conv_count
            shard_node_count = 0
            shard_kept = 0
            for conv in data:
                mapping = conv.get("mapping") or {}
                shard_node_count += len(mapping)
                update_schema(schema_acc, conv, mapping)
                rec = process_conversation(conv, since_epoch, args.with_text_preview)
                if rec is not None:
                    candidates.append(rec)
                    shard_kept += 1
            shard_stats.append({"name": shard, "conversations": shard_conv_count,
                                 "nodes": shard_node_count, "kept_as_candidate": shard_kept})
            del data
            gc.collect()

    candidates.sort(key=lambda c: (c["create_time"] or "", c["conversation_id"]))

    out_doc = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "script": "scripts/extract_chatgpt_export.py",
        "params": {"since": args.since, "with_text_preview": args.with_text_preview or None},
        "source_export": args.export.name,
        "total_conversations_in_export": total_conversations,
        "candidate_conversations": len(candidates),
        "candidates_tight": sum(1 for c in candidates if c["match_tier"] == "tight"),
        "candidates_wide_only": sum(1 for c in candidates if c["match_tier"] == "wide"),
        "conversations": candidates,
    }
    args.out.write_text(json.dumps(out_doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                         encoding="utf-8")

    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_export": args.export.name,
        "shards": shard_stats,
        "total_conversations": total_conversations,
        "user_json_present": user_json_present,
        "user_json_note": "existence-only check; values are never read by this script",
        "codex_json_footnote": codex_footnote,
        "schema": {
            "conversation_keys": sorted(schema_acc["conversation_keys"]),
            "node_keys": sorted(schema_acc["node_keys"]),
            "message_keys": sorted(schema_acc["message_keys"]),
            "author_keys": sorted(schema_acc["author_keys"]),
            "roles": sorted(r for r in schema_acc["roles"] if r is not None),
            "author_names_all_null": schema_acc["author_names"] == {None},
            "content_types": sorted(t for t in schema_acc["content_types"] if t is not None),
            "message_metadata_keys": sorted(schema_acc["metadata_keys"]),
            "nodes_without_message": schema_acc["nodes_without_message"],
            "nodes_with_message": schema_acc["nodes_with_message"],
        },
    }
    inv_path = args.out.parent / "inventory.json"
    inv_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                         encoding="utf-8")

    print(f"{args.out}: {len(candidates)} candidate conversations "
          f"(tight={out_doc['candidates_tight']}, wide_only={out_doc['candidates_wide_only']}) "
          f"of {total_conversations} total", file=sys.stderr)
    print(f"{inv_path}: shard/key-set inventory (Q1 deliverable source)", file=sys.stderr)
    if args.with_text_preview:
        print("WARNING: --with-text-preview set -- output contains truncated conversation text; "
              "keep under /private/ only", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
