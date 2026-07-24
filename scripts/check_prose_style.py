#!/usr/bin/env python3
"""Fail on a small set of objective prose defects in the manuscript.

This check intentionally covers only patterns that can be recognized without
judging mathematical content. Context-sensitive prose and claim strength still
require independent review.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [ROOT / "paper" / "main.tex", *sorted((ROOT / "paper" / "sections").glob("*.tex"))]

FORBIDDEN = [
    ("spaced prose dash", re.compile(r" -- ")),
    ("casual scope phrase", re.compile(r"\bno more\b", re.IGNORECASE)),
    ("decorative metaphor", re.compile(r"\bload-bearing\b", re.IGNORECASE)),
    ("casual implementation metaphor", re.compile(r"\bplumbing\b", re.IGNORECASE)),
    ("business idiom", re.compile(r"\bclosed the loop\b", re.IGNORECASE)),
    ("imprecise solution label", re.compile(r"\btrajectory\b", re.IGNORECASE)),
    ("nonstandard weak-limit spelling", re.compile(r"\bweak-limit\b", re.IGNORECASE)),
    ("hyphenated pull-request spelling", re.compile(r"\bpull-request\b", re.IGNORECASE)),
    ("paper-internal evidence rubric", re.compile(r"\bevidence strength\b", re.IGNORECASE)),
    (
        "formulaic negative framing",
        re.compile(r"\bnot\b[^.\n]{0,80}\bbut the opposite\b", re.IGNORECASE),
    ),
]

LISTING_BEGIN = r"\begin{lstlisting}"
LISTING_END = r"\end{lstlisting}"


def strip_comment(line: str) -> str:
    """Remove an unescaped LaTeX comment from one source line."""
    for i, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        j = i - 1
        while j >= 0 and line[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return line[:i]
    return line


def scan_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Return line-numbered findings while ignoring real listing bodies."""
    findings = []
    in_listing = False
    for lineno, raw in enumerate(lines, 1):
        cursor = 0
        prose_segments = []
        while cursor < len(raw):
            if in_listing:
                end_at = raw.find(LISTING_END, cursor)
                if end_at < 0:
                    break
                in_listing = False
                cursor = end_at + len(LISTING_END)
                continue

            prose_tail = strip_comment(raw[cursor:])
            begin_at = prose_tail.find(LISTING_BEGIN)
            if begin_at < 0:
                prose_segments.append(prose_tail)
                break
            prose_segments.append(prose_tail[:begin_at])
            in_listing = True
            cursor += begin_at + len(LISTING_BEGIN)

        for prose in prose_segments:
            for label, pattern in FORBIDDEN:
                if pattern.search(prose):
                    findings.append((lineno, label))
    return findings


def main() -> int:
    findings = []
    for path in TARGETS:
        source = path.read_text(encoding="utf-8").splitlines()
        for lineno, label in scan_lines(source):
            findings.append(f"{path.relative_to(ROOT)}:{lineno}: {label}")

    if findings:
        print("prose style check FAILED:")
        for finding in findings:
            print(f"  {finding}")
        return 1

    print(f"prose style check OK ({len(TARGETS)} TeX files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
