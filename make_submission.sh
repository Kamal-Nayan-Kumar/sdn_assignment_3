#!/usr/bin/env bash
# make_submission.sh - Package SDN Assignment 3 submission bundle
set -eu

ROOT=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-"$ROOT/sdn_assignment3_submission.zip"}
TMP_DIR="/private/var/folders/xf/h6j_p9x14lb4nw22yl7xyth80000gn/T/opencode"
mkdir -p "$TMP_DIR"
STAGE=$(mktemp -d "$TMP_DIR/submission.XXXXXX")

echo "[submit] Staging in $STAGE"

# 1. Top-level report.pdf
if [ -f "$ROOT/report/report.pdf" ]; then
  cp "$ROOT/report/report.pdf" "$STAGE/report.pdf"
  echo "[submit] Attached report.pdf at archive root"
else
  echo "[submit] ERROR: report/report.pdf missing. Building..."
  "$ROOT/report/build.sh"
  cp "$ROOT/report/report.pdf" "$STAGE/report.pdf"
fi

# 2. Everything else under code/
CODE="$STAGE/code"
mkdir -p "$CODE"

echo "[submit] Copying scripts, README, and make_submission..."
cp -r "$ROOT/scripts" "$CODE/"
cp "$ROOT/README.md" "$CODE/"
cp "$ROOT/make_submission.sh" "$CODE/"

echo "[submit] Copying clean report sources..."
mkdir -p "$CODE/report/figs"
cp "$ROOT/report/report.tex" "$CODE/report/"
cp "$ROOT/report/logo.jpeg" "$CODE/report/"
cp "$ROOT/report/build.sh" "$CODE/report/"
cp "$ROOT/report/capture.sh" "$CODE/report/"
cp "$ROOT/report/render_term.py" "$CODE/report/"
cp "$ROOT/report/figs"/*.png "$CODE/report/figs/"

echo "[submit] Copying O-RAN SC RIC directory..."
mkdir -p "$CODE/oran-sc-ric"
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  "$ROOT/oran-sc-ric/" "$CODE/oran-sc-ric/" >/dev/null

echo "[submit] Generating zip bundle: $OUT"
rm -f "$OUT"
(cd "$STAGE" && zip -r "$OUT" report.pdf code/ >/dev/null)
rm -rf "$STAGE"

ls -lh "$OUT"
echo "[submit] Submission bundle created successfully!"
