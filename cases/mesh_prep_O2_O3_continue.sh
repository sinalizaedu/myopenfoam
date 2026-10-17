#!/bin/bash
# Continue mesh prep for O2/O3 cases (skip if log.checkMesh already exists).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$ROOT/cases"
LOG="$CASES/mesh_prep_O2_O3.log"
cd "$ROOT"

for case in \
  doc-baseline-o2-patch-fluid \
  doc-baseline-o2-volume-fluid \
  doc-baseline-o3-patch-fluid \
  doc-baseline-o3-volume-fluid
do
  if [ -f "$CASES/$case/fluid/log.checkMesh" ] && grep -q "Mesh OK" "$CASES/$case/fluid/log.checkMesh"; then
    echo "===== $(date -Iseconds) SKIP (ready) $case =====" | tee -a "$LOG"
    continue
  fi
  echo "===== $(date -Iseconds) CLEAN+SKIP_SOLVE $case =====" | tee -a "$LOG"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case && ./Allclean && SKIP_SOLVE=1 ./Allrun"
  docker compose run --rm --user ubuntu fsi bash -lc \
    "cd /simulation/$case/fluid && checkMesh 2>&1 | tee log.checkMesh"
  echo "===== $(date -Iseconds) DONE $case =====" | tee -a "$LOG"
done
echo "ALL_MESH_PREP_DONE $(date -Iseconds)" | tee -a "$LOG"
