#!/usr/bin/env bash
# Build the paper without requiring `make`.
#
# Usage:
#   ./build.sh
#
# Output: output/paper.pdf
# Also prints the body word count (excluding the bibliography).

set -euo pipefail
cd "$(dirname "$0")"

mkdir -p output
python3 scripts/md2pdf.py paper.md output/paper.pdf
python3 scripts/count_words.py paper.md
