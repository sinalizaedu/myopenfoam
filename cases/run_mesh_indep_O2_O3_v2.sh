#!/bin/bash
# Run O2/O3 baseline solves after mesh prep (REUSE_MESH=1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$ROOT/cases"
LOG="$CASES/run_mesh_indep_O2_O3_v2.log"
cd "$ROOT"

mesh_ready() {
  local case="$1"
  [ -d "$CASES/$case/fluid/constant/polyMesh" ] && \
    grep -q "cells:" "$CASES/$case/fluid/log.checkMesh" 2>/dev/null
}

{
  echo "===== $(date -Iseconds) waiting for mesh prep ====="
  for _ in $(seq 1 360); do
    if grep -q "ALL_MESH_PREP_DONE" "$CASES/mesh_prep_O2_O3.log" 2>/dev/null; then
      break
    fi
    sleep 20
  done

  for case in \
    doc-baseline-o2-patch-fluid \
    doc-baseline-o2-volume-fluid \
    doc-baseline-o3-patch-fluid \
    doc-baseline-o3-volume-fluid
  do
    if ! mesh_ready "$case"; then
      echo "ERROR: mesh not ready for $case" >&2
      exit 1
    fi
  done

  echo "===== $(date -Iseconds) starting O2/O3 baselines ====="
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

  python3 "$CASES/scripts_mesh_indep_report_O1_O3.py" || true
  echo "===== $(date -Iseconds) ALL DONE ====="
} 2>&1 | tee -a "$LOG"
