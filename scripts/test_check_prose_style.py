#!/usr/bin/env python3
"""Regression tests for the deterministic manuscript prose gate."""

import unittest

from scripts.check_prose_style import scan_lines


class ScanLinesTest(unittest.TestCase):
    def test_commented_listing_begin_does_not_suppress_prose(self) -> None:
        findings = scan_lines([
            r"% \begin{lstlisting}",
            "This has no more supporting detail.",
        ])
        self.assertEqual([(2, "casual scope phrase")], findings)

    def test_real_listing_body_is_ignored_and_scanning_resumes(self) -> None:
        findings = scan_lines([
            r"\begin{lstlisting}",
            "no more",
            r"% \end{lstlisting}",
            r"\end{lstlisting}",
            "This has no more supporting detail.",
        ])
        self.assertEqual([(5, "casual scope phrase")], findings)

    def test_prose_before_listing_begin_is_still_checked(self) -> None:
        findings = scan_lines([
            r"This has no more detail. \begin{lstlisting}",
            "no more",
            r"\end{lstlisting}",
        ])
        self.assertEqual([(1, "casual scope phrase")], findings)


if __name__ == "__main__":
    unittest.main()
