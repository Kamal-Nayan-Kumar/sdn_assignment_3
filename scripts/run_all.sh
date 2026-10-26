#!/usr/bin/env bash
# run_all.sh - Complete end-to-end execution of SDN Assignment 3:
# 1. Start Near-RT RIC
# 2. Execute telemetry scenarios inside python_xapp_runner
# 3. Capture screenshots
# 4. Compile LaTeX report to PDF
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)

echo "=== Step 1: Starting O-RAN SC RIC ==="
"$ROOT/scripts/run_ric.sh"

echo "\n=== Step 2: Capturing Terminal Artifacts ==="
"$ROOT/report/capture.sh"

echo "\n=== Step 3: Compiling Final PDF Report ==="
"$ROOT/report/build.sh"

echo "\n[+] Assignment 3 run complete! Deliverable ready at report/report.pdf"
