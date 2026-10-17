#!/bin/bash
# Force-regenerate O2/O3 meshes after blockMeshDict scale change.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$ROOT/cases"
LOG="$CASES/mesh_prep_O2_O3.log"
cd "$ROOT"

CASES_TO_BUILD=(
  doc-baseline-o2-volume-fluid
  doc-baseline-o3-patch-fluid
  doc-baseline-o3-volume-fluid
)

for case in "${CASES_TO_BUILD[@]}"; do
  echo "===== $(date -Iseconds) FORCE CLEAN+SKIP_SOLVE $case =====" | tee -a "$LOG"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case && ./Allclean && SKIP_SOLVE=1 ./Allrun"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case/fluid && checkMesh 2>&1 | tee log.checkMesh"
  echo "===== $(date -Iseconds) DONE $case =====" | tee -a "$LOG"
done
echo "ALL_MESH_PREP_DONE $(date -Iseconds)" | tee -a "$LOG"
