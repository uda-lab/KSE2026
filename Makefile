# Build system for the KSE 2026 paper.
# Primary engine: pdflatex via latexmk (TeX Live) — matches the IEEE
# conference submission pipeline (PDF eXpress validates pdflatex output).
# Fallback: tectonic (single binary, XeTeX-based) for environments without
# TeX Live; fine for drafts, NOT for camera-ready.

LATEXMK  := $(shell command -v latexmk 2>/dev/null)
TECTONIC := $(shell command -v tectonic 2>/dev/null)
CHKTEX   := $(shell command -v chktex 2>/dev/null)

.PHONY: pdf lint verify clean

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
ifdef CHKTEX
	# informational for now (matches CI); tighten to a hard gate once drafting starts
	-chktex -q paper/main.tex paper/sections/*.tex
else
	@echo "chktex not installed; skipping LaTeX lint"
endif

verify:
	python3 scripts/verify_claim_links.py

clean:
	rm -rf build
