#!/usr/bin/env bash
# Compile report/report.tex to PDF.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"

if command -v pdflatex >/dev/null 2>&1; then
  echo "[build] Using pdflatex..."
  pdflatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
  pdflatex -interaction=nonstopmode -halt-on-error report.tex
  echo "[build] Generated report/report.pdf successfully via pdflatex"
  exit 0
fi

if command -v tectonic >/dev/null 2>&1; then
  echo "[build] Using tectonic..."
  exec tectonic -X compile report.tex --keep-logs
fi

cat <<'EOF'
[build] No LaTeX engine found.
Install one of:
  tectonic
  pdflatex / TeX Live
EOF
exit 1
