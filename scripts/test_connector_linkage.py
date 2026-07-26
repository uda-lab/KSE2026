#!/usr/bin/env python3
"""Regression tests for the connector-linkage pipeline (issue #70).

Every fixture below is hand-authored/synthetic. None of it is an excerpt of
the real ChatGPT export or real repository snapshots -- see AGENTS.md/plan
for issue #70 on why real conversation text must never appear in a tracked
file.

Run: python3 -m unittest scripts.test_connector_linkage
"""
import json
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

from scripts.extract_chatgpt_export import (
    canonical_repo,
    find_text_mentions,
    find_url_refs,
    process_conversation,
)
from scripts.join_connector_linkage import (
    AUTHORIZATION_SPOT_CHECK_OVERRIDES,
    PUBLIC_CSV_HEADER,
    PUBLIC_ROW_FIELDS,
    apply_authorization_override,
    artifact_hashes,
    artifact_key,
    build_anchor_index,
    build_artifacts,
    build_conversation_index,
    build_conversation_spans,
    build_message_hash_index,
    build_mention_index,
    build_rows,
    compute_authorization,
    emit_public,
    normalize,
    normalized_hash,
    parse_iso,
    resolve_artifact,
)


# ---------------------------------------------------------------------------
# Synthetic fixture builders
# ---------------------------------------------------------------------------

def synthetic_node(node_id, parent, role=None, text=None, create_time=None,
                    content_type="text"):
    if role is None:
        return {"id": node_id, "message": None, "parent": parent}
    return {
        "id": node_id,
        "parent": parent,
        "message": {
            "id": node_id,
            "author": {"role": role, "name": None},
            "content": {"content_type": content_type, "parts": [text or ""]},
            "create_time": create_time,
            "metadata": {},
        },
    }


def synthetic_conversation(conv_id, nodes, current_node, create_time=1000.0, update_time=2000.0):
    return {
        "id": conv_id,
        "create_time": create_time,
        "update_time": update_time,
        "current_node": current_node,
        "default_model_slug": "gpt-test",
        "mapping": {n["id"]: n for n in nodes},
    }


def mk_msg(msg_id, parent_id, role, create_time, url_refs=None, text_mentions=None,
           body_hashes=None, instruction_signals=None, content_type="text",
           bare_repo_mentions=None):
    return {
        "conversation_id": "conv",
        "msg_id": msg_id,
        "parent_id": parent_id,
        "role": role,
        "create_time": create_time,
        "content_type": content_type,
        "on_live_path": True,
        "text_len": 100,
        "url_refs": url_refs or [],
        "text_mentions": text_mentions or [],
        "bare_repo_mentions": bare_repo_mentions or [],
        **({"body_hashes": body_hashes} if body_hashes else {}),
        **({"instruction_signals": instruction_signals} if instruction_signals else {}),
    }


def mk_conv_record(conversation_id, messages, current_node=None):
    matched_repos = set()
    for m in messages:
        matched_repos.update(r["repo_canonical"] for r in m.get("url_refs", []))
        matched_repos.update(r["repo_canonical"] for r in m.get("text_mentions", []))
        matched_repos.update(m.get("bare_repo_mentions", []))
    for m in messages:
        m["conversation_id"] = conversation_id
    return {
        "conversation_id": conversation_id,
        "create_time": messages[0]["create_time"] if messages else None,
        "update_time": messages[-1]["create_time"] if messages else None,
        "current_node": current_node or (messages[-1]["msg_id"] if messages else None),
        "message_count": len(messages),
        "node_count": len(messages) + 1,
        "match_tier": "tight" if matched_repos else "wide",
        "matched_repos": sorted(matched_repos),
        "default_model_slug": "gpt-test",
        "messages": messages,
    }


def mk_artifact(repo, kind, number, artifact_id, created_at, connector_routed=True,
                 body="", title=""):
    return {
        "repo": repo, "artifact_kind": kind, "artifact_number": number,
        "artifact_id": artifact_id, "created_at": created_at,
        "connector_routed": connector_routed, "_body": body, "_title": title,
    }


LONG_BODY_A = (
    "Alpha paragraph body that is long enough\n"
    "to survive the sixty-four character minimum\n"
    "length gate for hashing purposes here."
)
LONG_BODY_B = (
    "Bravo paragraph body that is also long enough\n"
    "to survive the sixty-four character minimum\n"
    "length gate for hashing here too."
)


# ---------------------------------------------------------------------------
# Extractor: tree rebuild + live path
# ---------------------------------------------------------------------------

class TreeRebuildTest(unittest.TestCase):
    def test_live_path_and_branch_marking(self):
        # root -> n1(user) -> n2(assistant) -> {n3(user, abandoned branch),
        #                                        n4(user, live branch)}
        nodes = [
            synthetic_node("root", None),
            synthetic_node("n1", "root", "user", "see leray-hopf#1 please create it",
                            create_time=1000.0),
            synthetic_node("n2", "n1", "assistant", "ok, drafting now", create_time=1001.0),
            synthetic_node("n3", "n2", "user", "actually never mind (abandoned)",
                            create_time=1002.0),
            synthetic_node("n4", "n2", "user", "go ahead and post it (live branch)",
                            create_time=1003.0),
        ]
        conv = synthetic_conversation("conv-tree", nodes, current_node="n4")
        rec = process_conversation(conv, since_epoch=None, with_preview=0)
        self.assertIsNotNone(rec)
        by_id = {m["msg_id"]: m for m in rec["messages"]}
        self.assertTrue(by_id["n1"]["on_live_path"])
        self.assertTrue(by_id["n2"]["on_live_path"])
        self.assertTrue(by_id["n4"]["on_live_path"])
        self.assertFalse(by_id["n3"]["on_live_path"])
        # root has no message and must not appear as a message record
        self.assertNotIn("root", by_id)

    def test_since_filter_drops_stale_conversation(self):
        nodes = [
            synthetic_node("root", None),
            synthetic_node("n1", "root", "user", "leray-hopf#1 mention", create_time=1000.0),
        ]
        conv = synthetic_conversation("conv-old", nodes, current_node="n1")
        since_epoch = 5000.0  # after the only message's create_time
        rec = process_conversation(conv, since_epoch=since_epoch, with_preview=0)
        self.assertIsNone(rec)

    def test_no_repo_mention_is_dropped(self):
        nodes = [
            synthetic_node("root", None),
            synthetic_node("n1", "root", "user", "unrelated chit-chat", create_time=1000.0),
        ]
        conv = synthetic_conversation("conv-unrelated", nodes, current_node="n1")
        rec = process_conversation(conv, since_epoch=None, with_preview=0)
        self.assertIsNone(rec)


# ---------------------------------------------------------------------------
# Extractor: alias canonicalization / url_refs / text_mentions
# ---------------------------------------------------------------------------

class AliasCanonicalizationTest(unittest.TestCase):
    def test_canonical_repo_maps_old_names(self):
        self.assertEqual(canonical_repo("lean-pde"), "leray-hopf")
        self.assertEqual(canonical_repo("lean-pde-notes"), "leray-hopf-notes")
        self.assertEqual(canonical_repo("leray-hopf"), "leray-hopf")
        self.assertEqual(canonical_repo("KSE2026"), "KSE2026")

    def test_canonical_repo_normalizes_casing_of_non_alias_tokens(self):
        # Regression (PR #82 review): only the two renamed aliases were
        # casing-normalized; a same-repo mention like "kse2026" or
        # "LERAY-HOPF" used to keep its as-matched casing and silently fail
        # to join against the snapshot's canonically-cased key.
        self.assertEqual(canonical_repo("kse2026"), "KSE2026")
        self.assertEqual(canonical_repo("Kse2026"), "KSE2026")
        self.assertEqual(canonical_repo("LERAY-HOPF"), "leray-hopf")
        self.assertEqual(canonical_repo("Leray-Hopf-Notes"), "leray-hopf-notes")
        self.assertEqual(canonical_repo("LEAN-PDE"), "leray-hopf")

    def test_text_mention_alias_canonicalized(self):
        mentions = find_text_mentions("please see lean-pde#42 for context")
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["repo_canonical"], "leray-hopf")
        self.assertEqual(mentions[0]["repo_raw"], "lean-pde")
        self.assertEqual(mentions[0]["number"], 42)

    def test_url_ref_anchor_extraction(self):
        refs = find_url_refs(
            "posted at https://github.com/uda-lab/leray-hopf/issues/145#issuecomment-4756429826")
        self.assertEqual(len(refs), 1)
        r = refs[0]
        self.assertEqual(r["repo_canonical"], "leray-hopf")
        self.assertEqual(r["kind"], "issue")
        self.assertEqual(r["number"], 145)
        self.assertEqual(r["comment_anchor_id"], "issuecomment-4756429826")

    def test_url_ref_pull_kind(self):
        refs = find_url_refs("https://github.com/uda-lab/lean-pde-notes/pull/59")
        self.assertEqual(refs[0]["kind"], "pr")
        self.assertEqual(refs[0]["repo_canonical"], "leray-hopf-notes")
        self.assertEqual(refs[0]["repo_raw"], "lean-pde-notes")


# ---------------------------------------------------------------------------
# Joiner: normalize()
# ---------------------------------------------------------------------------

class NormalizeTest(unittest.TestCase):
    def test_idempotent(self):
        t = "Hello\r\n\r\n\r\nWorld  \n\ntrailing space here   \n\n\n"
        once = normalize(t)
        twice = normalize(once)
        self.assertEqual(once, twice)

    def test_crlf_converted(self):
        self.assertEqual(normalize("a\r\nb\r\n"), "a\nb")

    def test_cr_only_converted(self):
        self.assertEqual(normalize("a\rb"), "a\nb")

    def test_blank_run_collapsed_to_one(self):
        self.assertEqual(normalize("a\n\n\n\nb"), "a\n\nb")

    def test_trailing_whitespace_and_outer_blank_lines_stripped(self):
        self.assertEqual(normalize("\n\nhello   \nworld\t\n\n"), "hello\nworld")

    def test_short_body_hash_rejected(self):
        self.assertIsNone(normalized_hash("too short"))

    def test_long_body_hash_accepted(self):
        self.assertIsNotNone(normalized_hash(LONG_BODY_A))

    def test_hash_matches_after_crlf_normalization(self):
        crlf_version = LONG_BODY_A.replace("\n", "\r\n")
        self.assertNotEqual(LONG_BODY_A, crlf_version)
        self.assertEqual(normalized_hash(LONG_BODY_A), normalized_hash(crlf_version))


# ---------------------------------------------------------------------------
# Joiner: tier resolution
# ---------------------------------------------------------------------------

class TierResolutionTest(unittest.TestCase):
    def _resolve(self, artifact, conversations, window_minutes=60):
        anchor_idx = build_anchor_index(conversations)
        msg_hash_idx = build_message_hash_index(conversations)
        mention_idx = build_mention_index(conversations)
        conv_spans = build_conversation_spans(conversations)
        snap_hash_index = defaultdict(list)
        for h in artifact_hashes(artifact):
            snap_hash_index[h].append(artifact_key(artifact))
        return resolve_artifact(artifact, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx,
                                 conv_spans, window_minutes)

    def test_exact_id_fires(self):
        msg = mk_msg("m1", None, "assistant", "2026-06-21T07:00:00+00:00",
                      url_refs=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                 "kind": "issue", "number": 10, "comment_anchor_id":
                                 "issuecomment-999"}])
        conv = mk_conv_record("conv-a", [msg])
        art = mk_artifact("leray-hopf", "issue_comment", 10, 999,
                           "2026-06-21T07:05:00+00:00", body=LONG_BODY_A)
        res = self._resolve(art, [conv])
        self.assertEqual(res["tier"], "exact-id")
        self.assertEqual(res["confidence"], "high")
        self.assertEqual(res["conv_id"], "conv-a")

    def test_exact_body_fires_and_is_preferred_over_time_context(self):
        # Same message also mentions the artifact's (repo, number) so a
        # weaker tier would also fire -- exact-body must win.
        msg = mk_msg("m1", None, "assistant", "2026-06-21T07:00:00+00:00",
                      url_refs=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                 "kind": "issue", "number": 11, "comment_anchor_id": None}],
                      body_hashes={"whole": normalized_hash(LONG_BODY_A)})
        conv = mk_conv_record("conv-b", [msg])
        art = mk_artifact("leray-hopf", "issue_comment", 11, 1000,
                           "2026-06-21T07:05:00+00:00", body=LONG_BODY_A)
        res = self._resolve(art, [conv])
        self.assertEqual(res["tier"], "exact-body")
        self.assertEqual(res["confidence"], "high")

    def test_exact_body_snapshot_collision_is_ambiguous(self):
        msg = mk_msg("m1", None, "assistant", "2026-06-21T07:00:00+00:00",
                      body_hashes={"whole": normalized_hash(LONG_BODY_A)})
        conv = mk_conv_record("conv-c", [msg])
        art = mk_artifact("leray-hopf", "issue_comment", 12, 1001,
                           "2026-06-21T07:05:00+00:00", body=LONG_BODY_A)
        # Two different snapshot artifacts share the identical body -> the
        # snapshot-side hash index has a collision for that hash.
        anchor_idx = build_anchor_index([conv])
        msg_hash_idx = build_message_hash_index([conv])
        mention_idx = build_mention_index([conv])
        conv_spans = build_conversation_spans([conv])
        other = mk_artifact("leray-hopf", "issue_comment", 13, 1002,
                             "2026-06-21T09:00:00+00:00", body=LONG_BODY_A)
        snap_hash_index = defaultdict(list)
        for a in (art, other):
            for h in artifact_hashes(a):
                snap_hash_index[h].append(artifact_key(a))
        res = resolve_artifact(art, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx,
                                conv_spans, 60)
        self.assertEqual(res["tier"], "ambiguous")
        self.assertEqual(res["notes"], "hash-collision")

    def test_exact_body_collision_without_message_evidence_falls_through(self):
        # Regression (PR #82 review): a snapshot-side hash collision alone
        # (two artifacts sharing a body, e.g. repeated boilerplate review
        # text) is not evidence of anything if no candidate message ever
        # produced that hash -- there is no linkage candidate to be
        # ambiguous ABOUT. Must fall through to a weaker tier, not stay
        # "ambiguous" forever.
        art = mk_artifact("leray-hopf", "issue_comment", 14, 2001,
                           "2026-06-21T07:05:00+00:00", body=LONG_BODY_A)
        other = mk_artifact("leray-hopf", "issue_comment", 15, 2002,
                             "2026-06-21T09:00:00+00:00", body=LONG_BODY_A)
        # A message exists but mentions a completely different (repo, number)
        # -- it will not hash-match either artifact's body.
        msg = mk_msg("m1", None, "user", "2026-06-21T06:50:00+00:00",
                      text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                       "number": 14}])
        conv = mk_conv_record("conv-nohit", [msg])
        anchor_idx = build_anchor_index([conv])
        msg_hash_idx = build_message_hash_index([conv])  # empty: msg has no body_hashes
        mention_idx = build_mention_index([conv])
        conv_spans = build_conversation_spans([conv])
        snap_hash_index = defaultdict(list)
        for a in (art, other):
            for h in artifact_hashes(a):
                snap_hash_index[h].append(artifact_key(a))
        res = resolve_artifact(art, anchor_idx, snap_hash_index, msg_hash_idx, mention_idx,
                                conv_spans, 60)
        # Falls through past exact-body to time-and-context (mention in window).
        self.assertEqual(res["tier"], "time-and-context")

    def test_short_body_never_reaches_exact_body(self):
        # Identical short text on both sides must NOT hash-match (below the
        # 64-char floor) -- the artifact should fall through to unmatched.
        msg = mk_msg("m1", None, "assistant", "2026-06-21T07:00:00+00:00")
        conv = mk_conv_record("conv-short", [msg])
        art = mk_artifact("leray-hopf", "issue_comment", 14, 1003,
                           "2026-06-21T07:05:00+00:00", body="too short")
        res = self._resolve(art, [conv])
        self.assertNotEqual(res["tier"], "exact-body")

    def test_time_and_context_single_conversation_fires(self):
        msg = mk_msg("m1", None, "user", "2026-06-21T07:00:00+00:00",
                      text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                       "number": 20}])
        conv = mk_conv_record("conv-d", [msg])
        art = mk_artifact("leray-hopf", "issue_creation", 20, None,
                           "2026-06-21T07:20:00+00:00", body="")
        res = self._resolve(art, [conv], window_minutes=60)
        self.assertEqual(res["tier"], "time-and-context")
        self.assertEqual(res["confidence"], "medium")

    def test_time_and_context_two_conversations_is_ambiguous(self):
        msg1 = mk_msg("m1", None, "user", "2026-06-21T07:00:00+00:00",
                       text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                        "number": 21}])
        msg2 = mk_msg("m2", None, "user", "2026-06-21T07:10:00+00:00",
                       text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                        "number": 21}])
        conv1 = mk_conv_record("conv-e1", [msg1])
        conv2 = mk_conv_record("conv-e2", [msg2])
        art = mk_artifact("leray-hopf", "issue_creation", 21, None,
                           "2026-06-21T07:20:00+00:00", body="")
        res = self._resolve(art, [conv1, conv2], window_minutes=60)
        self.assertEqual(res["tier"], "ambiguous")
        self.assertTrue(res["notes"].startswith("multi-conversation:"))

    def test_time_and_context_outside_window_falls_through(self):
        msg = mk_msg("m1", None, "user", "2026-06-21T01:00:00+00:00",
                      text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                       "number": 22}])
        conv = mk_conv_record("conv-f", [msg])
        art = mk_artifact("leray-hopf", "issue_creation", 22, None,
                           "2026-06-21T07:20:00+00:00", body="")
        res = self._resolve(art, [conv], window_minutes=60)
        self.assertNotEqual(res["tier"], "time-and-context")

    def test_reconstructed_fires_on_span_and_repo_mention_only(self):
        msg1 = mk_msg("m1", None, "user", "2026-06-01T00:00:00+00:00",
                       text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                        "number": 999}])
        msg2 = mk_msg("m2", "m1", "assistant", "2026-06-30T00:00:00+00:00")
        conv = mk_conv_record("conv-g", [msg1, msg2])
        art = mk_artifact("leray-hopf", "issue_creation", 30, None,
                           "2026-06-15T00:00:00+00:00", body="")
        res = self._resolve(art, [conv], window_minutes=60)
        self.assertEqual(res["tier"], "reconstructed")
        self.assertEqual(res["confidence"], "low")

    def test_reconstructed_multiple_conversations_notes_candidates_count(self):
        msg_a = mk_msg("ma", None, "user", "2026-06-01T00:00:00+00:00",
                        text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                         "number": 999}])
        msg_a2 = mk_msg("ma2", "ma", "assistant", "2026-06-30T00:00:00+00:00")
        conv_a = mk_conv_record("conv-h1", [msg_a, msg_a2])
        msg_b = mk_msg("mb", None, "user", "2026-06-02T00:00:00+00:00",
                        text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                         "number": 999}])
        msg_b2 = mk_msg("mb2", "mb", "assistant", "2026-06-29T00:00:00+00:00")
        conv_b = mk_conv_record("conv-h2", [msg_b, msg_b2])
        art = mk_artifact("leray-hopf", "issue_creation", 31, None,
                           "2026-06-15T00:00:00+00:00", body="")
        res = self._resolve(art, [conv_a, conv_b], window_minutes=60)
        self.assertEqual(res["tier"], "reconstructed")
        self.assertEqual(res["notes"], "candidates:2")

    def test_unmatched_when_nothing_fires(self):
        conv = mk_conv_record("conv-i", [mk_msg("m1", None, "user", "2020-01-01T00:00:00+00:00")])
        art = mk_artifact("leray-hopf", "issue_creation", 999, None,
                           "2026-06-15T00:00:00+00:00", body="")
        res = self._resolve(art, [conv], window_minutes=60)
        self.assertEqual(res["tier"], "unmatched")
        self.assertIsNone(res["confidence"])


# ---------------------------------------------------------------------------
# Joiner: authorization_present
# ---------------------------------------------------------------------------

class AuthorizationTest(unittest.TestCase):
    def test_yes_when_earlier_instruction_with_signal_and_repo(self):
        msgs = [
            mk_msg("u1", None, "user", "2026-06-21T06:00:00+00:00",
                   text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                    "number": 40}],
                   instruction_signals=["post"]),
            mk_msg("a1", "u1", "assistant", "2026-06-21T06:05:00+00:00"),
        ]
        conv = mk_conv_record("conv-auth-1", msgs, current_node="a1")
        conv_index, current_node_of = build_conversation_index([conv])
        created_at = parse_iso("2026-06-21T07:00:00+00:00")
        result = compute_authorization(conv_index["conv-auth-1"], "a1",
                                        current_node_of["conv-auth-1"], created_at, "leray-hopf")
        self.assertEqual(result, "yes")

    def test_not_found_when_instruction_is_later(self):
        # instruction message occurs AFTER created_at -- must not count.
        msgs = [
            mk_msg("a1", None, "assistant", "2026-06-21T06:00:00+00:00"),
            mk_msg("u1", "a1", "user", "2026-06-21T08:00:00+00:00",
                   text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                    "number": 41}],
                   instruction_signals=["post"]),
        ]
        conv = mk_conv_record("conv-auth-2", msgs, current_node="u1")
        conv_index, current_node_of = build_conversation_index([conv])
        created_at = parse_iso("2026-06-21T07:00:00+00:00")  # before the u1 instruction
        result = compute_authorization(conv_index["conv-auth-2"], "a1",
                                        current_node_of["conv-auth-2"], created_at, "leray-hopf")
        self.assertEqual(result, "not-found")

    def test_not_found_when_no_signal(self):
        msgs = [
            mk_msg("u1", None, "user", "2026-06-21T06:00:00+00:00",
                   text_mentions=[{"repo_canonical": "leray-hopf", "repo_raw": "leray-hopf",
                                    "number": 42}]),  # no instruction_signals
            mk_msg("a1", "u1", "assistant", "2026-06-21T06:05:00+00:00"),
        ]
        conv = mk_conv_record("conv-auth-3", msgs, current_node="a1")
        conv_index, current_node_of = build_conversation_index([conv])
        created_at = parse_iso("2026-06-21T07:00:00+00:00")
        result = compute_authorization(conv_index["conv-auth-3"], "a1",
                                        current_node_of["conv-auth-3"], created_at, "leray-hopf")
        self.assertEqual(result, "not-found")

    def test_n_a_when_no_matched_message(self):
        conv = mk_conv_record("conv-auth-4", [mk_msg("u1", None, "user",
                                                       "2026-06-21T06:00:00+00:00")])
        conv_index, current_node_of = build_conversation_index([conv])
        created_at = parse_iso("2026-06-21T07:00:00+00:00")
        result = compute_authorization(conv_index["conv-auth-4"], None,
                                        current_node_of["conv-auth-4"], created_at, "leray-hopf")
        self.assertEqual(result, "n/a")

    def test_yes_via_bare_repo_mention_without_url_or_number(self):
        # Regression (PR #82 review): a natural-language instruction like
        # "KSE2026 に issue を作成して" names the repo but has no URL and no
        # #number, so it only shows up in bare_repo_mentions -- url_refs and
        # text_mentions are both empty for it. Authorization must still see it.
        msgs = [
            mk_msg("u1", None, "user", "2026-06-21T06:00:00+00:00",
                   bare_repo_mentions=["KSE2026"], instruction_signals=["作成"]),
            mk_msg("a1", "u1", "assistant", "2026-06-21T06:05:00+00:00"),
        ]
        conv = mk_conv_record("conv-auth-5", msgs, current_node="a1")
        conv_index, current_node_of = build_conversation_index([conv])
        created_at = parse_iso("2026-06-21T07:00:00+00:00")
        result = compute_authorization(conv_index["conv-auth-5"], "a1",
                                        current_node_of["conv-auth-5"], created_at, "KSE2026")
        self.assertEqual(result, "yes")


class AuthorizationOverrideTest(unittest.TestCase):
    def test_override_downgrades_yes_to_yes_rejected(self):
        repo, kind, number, aid = next(iter(AUTHORIZATION_SPOT_CHECK_OVERRIDES))
        art = {"repo": repo, "artifact_kind": kind, "artifact_number": number,
               "artifact_id": aid}
        auth, note = apply_authorization_override(art, "yes")
        self.assertEqual(auth, "yes-rejected")
        self.assertTrue(note.startswith("spot-check:"))

    def test_override_is_a_no_op_for_not_found_and_n_a(self):
        art = {"repo": "leray-hopf", "artifact_kind": "issue_creation",
               "artifact_number": 999999, "artifact_id": None}
        for auth in ("not-found", "n/a"):
            got, note = apply_authorization_override(art, auth)
            self.assertEqual(got, auth)
            self.assertIsNone(note)

    def test_override_is_a_no_op_for_unlisted_yes(self):
        # A "yes" on an artifact NOT in the override table is an unreviewed
        # candidate and must be passed through unchanged (never silently
        # rejected by a table that hasn't actually reviewed it).
        art = {"repo": "leray-hopf", "artifact_kind": "issue_creation",
               "artifact_number": 999999, "artifact_id": None}
        auth, note = apply_authorization_override(art, "yes")
        self.assertEqual(auth, "yes")
        self.assertIsNone(note)

    def test_build_rows_applies_override_end_to_end(self):
        # Artifact identity matches an AUTHORIZATION_SPOT_CHECK_OVERRIDES
        # entry; the message drives a genuine mechanical "yes" (earlier
        # instruction, signal, repo mention via text_mentions AND
        # bare_repo_mentions, in-window) which build_rows must then
        # downgrade to "yes-rejected".
        repo, kind, number, aid = ("KSE2026", "issue_creation", 61, None)
        art = mk_artifact(repo, kind, number, aid, "2026-06-21T07:00:00+00:00", body="")
        msgs = [
            mk_msg("u1", None, "user", "2026-06-21T06:00:00+00:00",
                   text_mentions=[{"repo_canonical": repo, "repo_raw": repo, "number": number}],
                   bare_repo_mentions=[repo], instruction_signals=["post"]),
        ]
        conv = mk_conv_record("conv-override", msgs, current_node="u1")
        anchor_idx = build_anchor_index([conv])
        msg_hash_idx = build_message_hash_index([conv])
        mention_idx = build_mention_index([conv])
        conv_spans = build_conversation_spans([conv])
        conv_index, current_node_of = build_conversation_index([conv])
        rows = build_rows([art], anchor_idx, {}, msg_hash_idx, mention_idx, conv_spans,
                           conv_index, current_node_of, 60)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["join_method"], "time-and-context")
        self.assertEqual(rows[0]["authorization_present"], "yes-rejected")
        self.assertIn("spot-check:", rows[0]["notes"])


# ---------------------------------------------------------------------------
# Exporter build_artifacts (connector-routed vs outside-universe / reviews caveat)
# ---------------------------------------------------------------------------

class BuildArtifactsTest(unittest.TestCase):
    def test_connector_routed_split_and_reviews_always_universe(self):
        snap = {
            "issues": [
                {"number": 1, "kind": "issue", "created_at": "2026-06-01T00:00:00Z",
                 "performed_via_github_app": "chatgpt-codex-connector", "body": "x", "title": "t"},
                {"number": 2, "kind": "pr", "created_at": "2026-06-02T00:00:00Z",
                 "performed_via_github_app": None, "body": "y", "title": "t2"},
            ],
            "comments": [
                {"issue_number": 1, "id": 100, "created_at": "2026-06-01T01:00:00Z",
                 "performed_via_github_app": "chatgpt-codex-connector", "body": "z"},
            ],
            "reviews": [
                {"pr_number": 2, "id": 200, "submitted_at": "2026-06-02T01:00:00Z", "body": "r"},
            ],
        }
        universe, outside = build_artifacts("leray-hopf", snap)
        kinds = sorted((a["artifact_kind"], a["connector_routed"]) for a in universe)
        self.assertIn(("issue_creation", True), kinds)
        self.assertIn(("issue_comment", True), kinds)
        self.assertIn(("pr_review", None), kinds)  # reviews: routing not determinable
        self.assertEqual(len(outside), 1)  # the non-connector PR creation
        self.assertEqual(outside[0]["artifact_kind"], "pr_creation")

    def test_bot_account_connector_comment_is_excluded_from_universe(self):
        # performed_via_github_app == the connector slug on a comment posted
        # by the bot ACCOUNT itself (login ending "[bot]") is a different
        # provenance question from a t-uda post routed through the connector
        # -- issue #70 is about the latter only. Regression for a bug where
        # both were folded into one count (roughly doubling leray-hopf).
        snap = {
            "issues": [],
            "comments": [
                {"issue_number": 1, "id": 1, "created_at": "2026-06-01T00:00:00Z",
                 "performed_via_github_app": "chatgpt-codex-connector",
                 "user_login": "t-uda", "body": "human post via connector"},
                {"issue_number": 1, "id": 2, "created_at": "2026-06-01T00:00:00Z",
                 "performed_via_github_app": "chatgpt-codex-connector",
                 "user_login": "chatgpt-codex-connector[bot]", "body": "bot's own comment"},
            ],
            "reviews": [],
        }
        universe, outside = build_artifacts("leray-hopf", snap)
        self.assertEqual(len(universe), 1)
        self.assertEqual(universe[0]["artifact_id"], 1)
        self.assertEqual(len(outside), 1)
        self.assertEqual(outside[0]["artifact_id"], 2)


# ---------------------------------------------------------------------------
# Public emit: no text keys, only the documented columns
# ---------------------------------------------------------------------------

class PublicEmitTest(unittest.TestCase):
    def test_public_emit_has_no_text_keys(self):
        rows = [{
            "repo": "leray-hopf", "artifact_kind": "issue_comment", "artifact_number": 1,
            "artifact_id": 100, "artifact_created_at": "2026-06-01T00:00:00Z",
            "connector_routed": True, "join_method": "exact-id", "confidence": "high",
            "conversation_id": "conv-real-id-should-not-leak",
            "conversation_id_hash": "abc123", "msg_id": "should-not-leak-either",
            "message_timestamp": "2026-06-01T00:00:00Z", "authorization_present": "yes",
            "notes": "alias:lean-pde",
        }]
        with tempfile.TemporaryDirectory() as td:
            json_out = Path(td) / "connector-linkage.json"
            csv_out = Path(td) / "connector-linkage.csv"
            emit_public(rows, [], [], 1, json_out, csv_out)

            doc = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(len(doc["rows"]), 1)
            row = doc["rows"][0]
            self.assertEqual(set(row.keys()), set(PUBLIC_ROW_FIELDS))
            self.assertNotIn("conversation_id", row)
            self.assertNotIn("msg_id", row)
            # sanity: the raw (unhashed) conversation id string must not
            # appear anywhere in the serialized public JSON.
            raw_json_text = json_out.read_text(encoding="utf-8")
            self.assertNotIn("conv-real-id-should-not-leak", raw_json_text)
            self.assertNotIn("should-not-leak-either", raw_json_text)

            csv_text = csv_out.read_text(encoding="utf-8")
            header = csv_text.splitlines()[0].split(",")
            self.assertEqual(header, list(PUBLIC_CSV_HEADER))
            self.assertNotIn("conv-real-id-should-not-leak", csv_text)


if __name__ == "__main__":
    unittest.main()
