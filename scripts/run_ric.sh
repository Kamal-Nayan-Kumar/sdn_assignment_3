#!/usr/bin/env bash
# run_ric.sh - Deploy and verify the O-RAN SC Near-RT RIC multi-container application
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
RIC_DIR="$ROOT/oran-sc-ric"

echo "=== [1/3] Verifying Container Runtime ==="
docker info | grep -E 'Server Version|Operating System|Architecture|CPUs|Total Memory'

echo "=== [2/3] Starting O-RAN SC RIC Multi-Container Platform ==="
cd "$RIC_DIR"
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose up -d

echo "=== [3/3] Inspecting Running Containers ==="
docker ps --filter "name=ric_" --filter "name=python_xapp_runner" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "\n[+] O-RAN SC RIC deployment ready."
