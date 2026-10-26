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

# 2. Code and resources under code/
CODE="$STAGE/code"
mkdir -p "$CODE"

echo "[submit] Copying scripts and report source..."
cp -r "$ROOT/scripts" "$CODE/"
cp -r "$ROOT/report" "$CODE/"
cp "$ROOT/README.md" "$CODE/"

echo "[submit] Copying O-RAN SC RIC directory (excluding .git)..."
mkdir -p "$CODE/oran-sc-ric"
rsync -av --exclude='.git' "$ROOT/oran-sc-ric/" "$CODE/oran-sc-ric/" >/dev/null

echo "[submit] Generating zip bundle: $OUT"
rm -f "$OUT"
(cd "$STAGE" && zip -r "$OUT" report.pdf code/ >/dev/null)
rm -rf "$STAGE"

ls -lh "$OUT"
echo "[submit] Submission bundle created successfully!"
