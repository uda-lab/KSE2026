# Build system for the KSE 2026 paper.
# Prefers tectonic (single binary, runs BibTeX automatically); falls back to
# latexmk if tectonic is absent. Both write the PDF to build/.

TECTONIC := $(shell command -v tectonic 2>/dev/null)
LATEXMK  := $(shell command -v latexmk 2>/dev/null)
CHKTEX   := $(shell command -v chktex 2>/dev/null)

.PHONY: pdf lint verify clean

pdf:
ifdef TECTONIC
	mkdir -p build
	cd paper && tectonic --outdir ../build main.tex
else ifdef LATEXMK
	mkdir -p build
	cd paper && latexmk -pdf -outdir=../build main.tex
else
	$(error No LaTeX engine found: install tectonic (single binary) or latexmk)
endif
	@echo "==> build/main.pdf"

lint:
ifdef CHKTEX
	chktex -q paper/main.tex paper/sections/*.tex
else
	@echo "chktex not installed; skipping LaTeX lint"
endif

verify:
	python3 scripts/verify_claim_links.py

clean:
	rm -rf build
