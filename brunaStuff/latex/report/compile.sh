#!/usr/bin/env bash
# Gera main.pdf nesta pasta (brunaStuff/latex/report). Requer: brew install tectonic
set -euo pipefail
cd "$(dirname "$0")"
tectonic -X compile main.tex
echo "PDF: $(pwd)/main.pdf"
