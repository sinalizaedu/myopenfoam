#!/bin/bash
# Run all O1/O2/O3 baseline cases (patch + volume) and emit mesh-independence report.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$ROOT/cases"
LOG="$CASES/run_all_O_mesh_indep.log"
cd "$ROOT"

CASE_LIST=(
  doc-baseline-o1-patch-fluid
  doc-baseline-o1-volume-fluid
  doc-baseline-o2-patch-fluid
  doc-baseline-o2-volume-fluid
  doc-baseline-o3-patch-fluid
  doc-baseline-o3-volume-fluid
)

log() { echo "$(date -Iseconds)  $*" | tee -a "$LOG"; }

is_done() {
  local case_dir="$1"
  local logf="$CASES/$case_dir/fluid/log.simpleFoam"
  [ -f "$logf" ] || return 1
  grep -q "SIMPLE solution converged" "$logf" 2>/dev/null && return 0
  grep -qE '^End$' "$logf" 2>/dev/null && ! grep -q "FOAM FATAL" "$logf" 2>/dev/null
}

mesh_ok() {
  local case_dir="$1"
  local level cells
  level="$(echo "$case_dir" | sed -n 's/.*-o\([123]\)-.*/\1/p')"
  [ -f "$CASES/$case_dir/fluid/log.checkMesh" ] || return 1
  cells="$(rg '^\s*cells:\s+' "$CASES/$case_dir/fluid/log.checkMesh" | awk '{print $2}')"
  [ -n "$cells" ] || return 1
  case "$level" in
    1) [ "$cells" -ge 50000 ] && [ "$cells" -le 60000 ] ;;
    2) [ "$cells" -ge 15000 ] && [ "$cells" -le 25000 ] ;;
    3) [ "$cells" -ge 100000 ] && [ "$cells" -le 150000 ] ;;
    *) return 1 ;;
  esac
}

wait_for_docker_case() {
  local case_dir="$1"
  while docker ps --format '{{.Config.Cmd}}' 2>/dev/null | tr ' ' '\n' | grep -q "/simulation/${case_dir}"; do
    log "WAIT docker still running $case_dir"
    sleep 30
  done
}

ensure_o3_volume_mesh() {
  local case_dir="doc-baseline-o3-volume-fluid"
  if mesh_ok "$case_dir"; then
    log "mesh OK $case_dir"
    return 0
  fi
  log "REGEN mesh $case_dir (stale or missing)"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case_dir && ./Allclean && SKIP_SOLVE=1 ./Allrun"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case_dir/fluid && checkMesh 2>&1 | tee log.checkMesh"
  mesh_ok "$case_dir" || { log "ERROR mesh still wrong for $case_dir"; return 1; }
}

run_case() {
  local case_dir="$1"
  wait_for_docker_case "$case_dir"
  if is_done "$case_dir"; then
    log "SKIP (done) $case_dir"
  else
    log "SOLVE $case_dir"
    docker compose run --rm --user ubuntu fsi bash -lc \
      "cd /simulation/$case_dir && REUSE_MESH=1 ./Allrun" \
      >>"$CASES/$case_dir/run_baseline.log" 2>&1
    is_done "$case_dir" || { log "FAIL $case_dir"; return 1; }
    log "OK $case_dir"
  fi
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case_dir && python3 scripts/extract_step0_metrics.py && python3 scripts/save_baseline_calibration.py" \
    >>"$CASES/$case_dir/run_baseline.log" 2>&1 || true
}

log "=== START O1/O2/O3 mesh-independence queue ==="
ensure_o3_volume_mesh

for case_dir in "${CASE_LIST[@]}"; do
  if ! mesh_ok "$case_dir"; then
    log "ERROR mesh not ready for $case_dir — abort"
    exit 1
  fi
done

for case_dir in "${CASE_LIST[@]}"; do
  run_case "$case_dir"
done

python3 "$CASES/scripts_mesh_indep_report_O1_O3.py"
log "=== ALL DONE ==="
