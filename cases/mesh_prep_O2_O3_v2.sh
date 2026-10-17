#!/bin/bash
# Regenerate O2/O3 polyMesh after blockMeshDict scale (0.7× / 1.3× O1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$ROOT/cases"
LOG="$CASES/mesh_prep_O2_O3.log"
cd "$ROOT"

{
  echo "===== $(date -Iseconds) mesh prep O2/O3 (0.7× / 1.3× O1) ====="
  for case in \
    doc-baseline-o2-patch-fluid \
    doc-baseline-o2-volume-fluid \
    doc-baseline-o3-patch-fluid \
    doc-baseline-o3-volume-fluid
  do
    echo "===== $(date -Iseconds) CLEAN+SKIP_SOLVE $case ====="
    docker compose run --rm --user ubuntu fsi bash -lc \
      "cd /simulation/$case && ./Allclean && SKIP_SOLVE=1 ./Allrun"
    docker compose run --rm --user ubuntu fsi bash -lc \
      "cd /simulation/$case/fluid && checkMesh 2>&1 | tee log.checkMesh"
    echo "===== $(date -Iseconds) DONE $case ====="
  done
  echo "ALL_MESH_PREP_DONE $(date -Iseconds)"
} 2>&1 | tee "$LOG"
