#!/bin/bash
# Wait for O1 patch+volume baselines to finish, then run O2/O3 with REUSE_MESH=1
# (meshes pre-built via SKIP_SOLVE=1). Logs to cases/run_mesh_indep_O2_O3.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$ROOT/cases"
LOG="$CASES/run_mesh_indep_O2_O3.log"
cd "$ROOT"

o1_done() {
  local case="$1"
  local logf="$CASES/$case/fluid/log.simpleFoam"
  [ -f "$logf" ] || return 1
  grep -q "SIMPLE solution converged" "$logf" 2>/dev/null && return 0
  if grep -qE '^End$' "$logf" 2>/dev/null && ! grep -q "FOAM FATAL" "$logf" 2>/dev/null; then
    return 0
  fi
  return 1
}

last_time() {
  local logf="$1"
  grep -E '^Time = ' "$logf" 2>/dev/null | tail -1 || echo "Time = ?"
}

{
  echo "===== $(date -Iseconds) watcher started ====="
  echo "Waiting for O1 patch + volume baselines..."

  while true; do
    p_ok=0; v_ok=0
    o1_done doc-baseline-o1-patch-fluid && p_ok=1
    o1_done doc-baseline-o1-volume-fluid && v_ok=1
    pt=$(last_time "$CASES/doc-baseline-o1-patch-fluid/fluid/log.simpleFoam")
    vt=$(last_time "$CASES/doc-baseline-o1-volume-fluid/fluid/log.simpleFoam")
    echo "$(date -Iseconds) patch_ok=$p_ok ($pt)  volume_ok=$v_ok ($vt)"
    if [ "$p_ok" = 1 ] && [ "$v_ok" = 1 ]; then
      break
    fi
    sleep 30
  done

  echo "===== $(date -Iseconds) O1 done — waiting for mesh prep if still running ====="
  # Wait until mesh prep finished (flag file or log marker)
  for _ in $(seq 1 240); do
    if grep -q "ALL_MESH_PREP_DONE" "$CASES/mesh_prep_O2_O3.log" 2>/dev/null; then
      break
    fi
    echo "$(date -Iseconds) waiting mesh prep..."
    sleep 15
  done

  echo "===== $(date -Iseconds) starting O2/O3 baselines (REUSE_MESH=1) ====="

  for case in \
    doc-baseline-o2-patch-fluid \
    doc-baseline-o2-volume-fluid \
    doc-baseline-o3-patch-fluid \
    doc-baseline-o3-volume-fluid
  do
    if [ ! -d "$CASES/$case/fluid/constant/polyMesh" ]; then
      echo "WARNING: no polyMesh in $case — running SKIP_SOLVE=1 first"
      docker compose run --rm --user ubuntu fsi bash -lc \
        "cd /simulation/$case && SKIP_SOLVE=1 ./Allrun"
    fi
  done

  for case in \
    doc-baseline-o2-patch-fluid \
    doc-baseline-o2-volume-fluid \
    doc-baseline-o3-patch-fluid \
    doc-baseline-o3-volume-fluid
  do
    echo "===== $(date -Iseconds) SOLVE $case ====="
    docker compose run --rm --user ubuntu fsi bash -lc \
      "cd /simulation/$case && REUSE_MESH=1 ./Allrun"
    echo "===== $(date -Iseconds) DONE $case ====="
  done

  echo "===== $(date -Iseconds) extracting comparison report ====="
  python3 "$CASES/scripts_mesh_indep_report_O1_O3.py" || true
  echo "===== $(date -Iseconds) ALL DONE ====="
} 2>&1 | tee -a "$LOG"
