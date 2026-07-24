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
    (
        "formulaic negative framing",
        re.compile(r"\bnot\b[^.\n]{0,80}\bbut the opposite\b", re.IGNORECASE),
    ),
]


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


def main() -> int:
    findings = []
    for path in TARGETS:
        in_listing = False
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if r"\begin{lstlisting}" in raw:
                in_listing = True
                continue
            if r"\end{lstlisting}" in raw:
                in_listing = False
                continue
            if in_listing:
                continue
            line = strip_comment(raw)
            for label, pattern in FORBIDDEN:
                if pattern.search(line):
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
