PYTHON ?= python3
PAPER ?= paper.md
OUTPUT ?= output/paper.pdf

.PHONY: all pdf count notes-count sources clean help

all: pdf

pdf: $(OUTPUT)

$(OUTPUT): $(PAPER) scripts/md2pdf.py
	@mkdir -p $(dir $(OUTPUT))
	$(PYTHON) scripts/md2pdf.py $(PAPER) $(OUTPUT)

count:
	$(PYTHON) scripts/count_words.py $(PAPER)

notes-count:
	$(PYTHON) scripts/count_notes.py notes $(PAPER)

sources:
	bash scripts/download_sources.sh sources

clean:
	rm -rf output

help:
	@echo "make              build $(OUTPUT)"
	@echo "make count        count the paper body (excluding the bibliography)"
	@echo "make notes-count  count the notes and compare them to the paper"
	@echo "make sources      download the source PDFs into sources/"
	@echo "make clean        remove output/"
