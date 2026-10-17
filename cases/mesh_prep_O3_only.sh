#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/cases/mesh_prep_O2_O3.log"
cd "$ROOT"
for case in doc-baseline-o3-patch-fluid doc-baseline-o3-volume-fluid; do
  echo "===== $(date -Iseconds) FORCE O3 $case =====" | tee -a "$LOG"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case && ./Allclean && SKIP_SOLVE=1 ./Allrun"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case/fluid && checkMesh 2>&1 | tee log.checkMesh"
  echo "===== $(date -Iseconds) DONE $case =====" | tee -a "$LOG"
done
echo "ALL_MESH_O3_DONE $(date -Iseconds)" | tee -a "$LOG"
