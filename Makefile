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

.PHONY: pdf lint verify leakcheck redact integrity clean

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
	# ChkTeX warnings 8/9/12/13/17/36 are disabled because they conflate
	# correct name/range dashes, math delimiters, and IEEE macros with prose
	# defects. check_prose_style.py owns spaced prose dashes.
	chktex -q -n8 -n9 -n12 -n13 -n17 -n36 paper/main.tex paper/sections/*.tex
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

redact:
	python3 scripts/redact_check.py $(REDACT_DIRS:%=--dir %)

# The three content gates that need no TeX. Kept as one target so the
# lightweight CI workflow and a manual full build run an identical set.
integrity: verify leakcheck redact

clean:
	rm -rf build
