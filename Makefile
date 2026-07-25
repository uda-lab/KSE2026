# Build system for the KSE 2026 paper.
# Primary engine: pdflatex via latexmk (TeX Live) — matches the IEEE
# conference submission pipeline (PDF eXpress validates pdflatex output).
# Fallback: tectonic (single binary, XeTeX-based) for environments without
# TeX Live; fine for drafts, NOT for camera-ready.

# Set REQUIRE_CHKTEX=1 to turn the "chktex not installed" skip into an error.
# CI sets it, so `make lint` cannot report a pass for a gate that never ran.
LATEXMK  := $(shell command -v latexmk 2>/dev/null)
TECTONIC := $(shell command -v tectonic 2>/dev/null)
CHKTEX   := $(shell command -v chktex 2>/dev/null)

# Public directories the redaction scan must cover. CI and local runs read the
# list from here so the gate cannot drift between them.
REDACT_DIRS := evidence claims analysis provenance notes paper

# Files ChkTeX must lint. Expanded here rather than passed as a glob because
# chktex exits 0 when it cannot open an input: an unmatched glob, or a renamed
# sections/ directory, would otherwise produce a passing lint that read nothing.
# The recipe asserts the list is plausible before invoking chktex.
LINT_TEX := paper/main.tex $(wildcard paper/sections/*.tex)

.PHONY: pdf lint verify leakcheck redact integrity selftest clean

pdf:
ifdef LATEXMK
	mkdir -p build
	cd paper && latexmk -pdf -interaction=nonstopmode -outdir=../build main.tex
else ifdef TECTONIC
	mkdir -p build
	@echo "NOTE: building with tectonic (XeTeX) — draft only; camera-ready must use pdflatex"
	cd paper && tectonic --outdir ../build main.tex
else
	$(error No LaTeX engine found: install TeX Live (latexmk) or tectonic)
endif
	@echo "==> build/main.pdf"

lint:
	python3 -m unittest scripts.test_check_prose_style
	python3 scripts/check_prose_style.py
ifdef CHKTEX
	@# chktex exits 0 on an input it cannot open, so an empty or stale file list
	@# would lint nothing and still pass. Assert the list before trusting it.
	@if [ $(words $(LINT_TEX)) -lt 2 ]; then \
		echo "error: LINT_TEX matched only '$(LINT_TEX)';" >&2; \
		echo "paper/sections/*.tex found no files — has the layout moved?" >&2; \
		exit 1; \
	fi
	@# -f, not -r: a directory and /dev/null are both readable, and chktex exits
	@# 0 after failing to open either of them.
	@for f in $(LINT_TEX); do \
		[ -f "$$f" ] || { echo "error: $$f is not a regular file" >&2; exit 1; }; \
	done
	@# The assertions above only prove the list is non-trivial. This one proves it
	@# is complete: every section file git tracks must actually be in LINT_TEX.
	@#
	@# Compare the sets, not the counts. Counting cancels — delete one tracked
	@# section and add one untracked file and the totals still match while a file
	@# goes unlinted. Note the direction: a tracked file missing from LINT_TEX is
	@# an error, but an untracked new file is not, because it is still linted.
	@# Requiring the reverse would fail every `make lint` run on a section that
	@# has been written but not yet staged, which is the normal drafting state.
	@#
	@# :(glob) stops the pattern crossing / into subdirectories, where git's
	@# default pathspec would match paper/sections/sub/a.tex and report a file as
	@# missing that is merely nested.
	@if git rev-parse --git-dir >/dev/null 2>&1; then \
		for t in $$(git ls-files -- ':(glob)paper/sections/*.tex' 2>/dev/null); do \
			case " $(LINT_TEX) " in \
				*" $$t "*) ;; \
				*) echo "error: $$t is tracked by git but absent from the lint list;" >&2; \
					echo "it would go unlinted — has it been deleted from disk?" >&2; \
					exit 1 ;; \
			esac; \
		done; \
	fi
	@# ChkTeX warnings 8/9/12/13/17/36 are disabled because they conflate
	@# correct name/range dashes, math delimiters, and IEEE macros with prose
	@# defects. check_prose_style.py owns spaced prose dashes.
	chktex -q -n8 -n9 -n12 -n13 -n17 -n36 $(LINT_TEX)
else
	@if [ -n "$(REQUIRE_CHKTEX)" ]; then \
		echo "error: REQUIRE_CHKTEX is set but chktex is not installed;" >&2; \
		echo "refusing to report a pass for a lint gate that did not run" >&2; \
		exit 1; \
	fi
	@echo "chktex not installed; skipping LaTeX lint"
endif

verify:
	python3 scripts/verify_claim_links.py

leakcheck:
	bash scripts/check_no_raw_logs.sh

# The scope assertion lives in redact_check.py so that a direct invocation is
# guarded too, but assert it here as well: this recipe is what CI runs, and a
# missing directory should name itself rather than surface as an argparse error.
redact:
	@for d in $(REDACT_DIRS); do \
		[ -d "$$d" ] || { \
			echo "error: redaction scope '$$d' is missing;" >&2; \
			echo "refusing to report a pass for a narrower scan than configured" >&2; \
			exit 1; }; \
	done
	python3 scripts/redact_check.py $(REDACT_DIRS:%=--dir %)

# The three content gates that need no TeX. Kept as one target so the
# lightweight CI workflow and a manual full build run an identical set.
integrity: verify leakcheck redact

# Regression tests for the gate mechanisms themselves: that the ChkTeX gate
# fails when chktex is absent, and that the leakage guard catches uppercase
# extensions and fails closed. Separate from `lint` because it shells out to
# scratch git repositories.
selftest:
	bash scripts/test_ci_gates.sh

clean:
	rm -rf build
