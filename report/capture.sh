#!/usr/bin/env bash
# Capture terminal screenshots for the LaTeX report.
#
# Each figure's command is run inside a clean subshell and converted
# to an ANSI transcript, which is then rendered to a styled PNG
# in report/figs/ by render_term.py.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$HERE")
FIGS="$HERE/figs"
LOGS="$HERE/.logs"
RENDER="$HERE/render_term.py"
PY="python3"

mkdir -p "$FIGS" "$LOGS"

shot() {
  local name=$1 title=$2 cmdline=$3 body=$4
  local log="$LOGS/$name.ansi"

  printf "\033[1;36m$\033[0m \033[1m%s\033[0m\n\n" "$cmdline" > "$log"
  eval "$body" >> "$log" 2>&1 || true
  printf "\n" >> "$log"

  echo "[capture] $name -> $FIGS/$name.png"
  "$PY" "$RENDER" "$log" "$FIGS/$name.png" --title "$title"
}

echo "=== Capturing Report Figures ==="

# 1. Docker Runtime
shot fig_docker_info "docker info" \
  "docker info | grep -E 'Server Version|Operating System|Architecture|CPUs|Total Memory'" \
  "docker info | grep -E 'Server Version|Operating System|Architecture|CPUs|Total Memory|Kernel Version'"

# 2. RIC Container Deployment
shot fig_ric_up "docker compose up -d" \
  "cd oran-sc-ric && docker compose up -d" \
  "cd '$ROOT/oran-sc-ric' && docker compose ps"

# 3. Docker PS Table
shot fig_ric_ps "docker ps" \
  "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'" \
  "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"

# 4. Network Inspection
shot fig_network_inspect "docker network inspect oran-sc-ric_ric_network" \
  "docker network inspect oran-sc-ric_ric_network" \
  "docker network inspect oran-sc-ric_ric_network | jq -r '.[0].Containers[] | {Name: .Name, IPv4Address: .IPv4Address}' | head -n 35"

# 5. Subscription Manager Log
shot fig_submgr_log "docker logs ric_submgr" \
  "docker logs --tail 15 ric_submgr" \
  "docker logs --tail 15 ric_submgr | fold -s -w 90"

# 6. E2 Manager Log
shot fig_e2mgr_log "docker logs ric_e2mgr" \
  "docker logs --tail 10 ric_e2mgr" \
  "docker logs --tail 10 ric_e2mgr | fold -s -w 90"

# 7. E2 Termination Log
shot fig_e2term_log "docker logs ric_e2term" \
  "docker logs --tail 10 ric_e2term && docker exec ric_e2term cat /proc/net/sctp/eps" \
  "echo '=== e2term process log ===' && docker logs --tail 5 ric_e2term | fold -s -w 90 && echo '\n=== SCTP Endpoints in e2term container ===' && docker exec ric_e2term cat /proc/net/sctp/eps"

# 8. DBAAS Redis Keys
shot fig_dbaas_keys "docker exec ric_dbaas redis-cli keys '*'" \
  "docker exec ric_dbaas redis-cli keys '*'" \
  "echo '=== RNIB Redis Database Keys ===' && docker exec ric_dbaas redis-cli keys '*' && echo '\n=== E2T Instance Record ===' && docker exec ric_dbaas redis-cli get '{e2Manager},E2TInstance:10.0.2.10:38000' | fold -s -w 90"

# 9. Routing Table
shot fig_rtmgr_routes "cat oran-sc-ric/ric/configs/routes.rtg" \
  "cat oran-sc-ric/ric/configs/routes.rtg" \
  "cat '$ROOT/oran-sc-ric/ric/configs/routes.rtg'"

# 10. Default Throughput xApp
shot fig_xapp_run_default "simple_mon_xapp.py --metrics=DRB.UEThpDl,DRB.UEThpUl" \
  "docker compose exec python_xapp_runner ./simple_mon_xapp.py --metrics=DRB.UEThpDl,DRB.UEThpUl" \
  "docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode default --iterations 3"

# 11. Modified Metrics xApp
shot fig_xapp_run_modified "simple_mon_xapp.py (Modified: RLC Volumes & Reliability)" \
  "docker compose exec python_xapp_runner ./simple_mon_xapp.py --metrics=DRB.RlcSduTransmittedVolumeDL,DRB.RlcSduTransmittedVolumeUL,DRB.RlcPacketDropRateDl,DRB.PacketSuccessRateUlgNBUu" \
  "docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode modified --iterations 3"

# 12. Advanced Style 5 xApp
shot fig_xapp_kpm_advanced "kpm_mon_xapp.py --kpm_report_style=5" \
  "docker compose exec python_xapp_runner ./kpm_mon_xapp.py --kpm_report_style=5" \
  "docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode ue_level --iterations 3"

# 13. Pytest E2AP Bugfix Verification
shot fig_pytest_e2ap "pytest tests/test_e2ap.py" \
  "docker exec python_xapp_runner pytest /opt/ric-plt-xapp-frame-py/tests/test_e2ap.py" \
  "docker exec python_xapp_runner pytest /opt/ric-plt-xapp-frame-py/tests/test_e2ap.py -v --disable-warnings"

echo "=== All figures captured successfully! ==="
ls -lh "$FIGS"
