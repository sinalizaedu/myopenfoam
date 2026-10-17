#!/usr/bin/env bash
# Run O1 diagnostic cases ONE AT A TIME (avoids OOM / exit 137).
# Skips cases that already have reconstructed t=1 fields.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

CASES=(
  diag-o1-patch-1s-active      # reference: patch inlet BC
  diag-o1-volume-1s-active     # baseline: volume + Darcy in needle
  diag-o1-volume-1s-nodarcy    # ablation: correction 1 only
  diag-o1-volume-1s-fix        # full fix: corrections 1 + 2
)

ARCHIVE="T1: Volume vs Patch"

run_case() {
  local C="$1"
  local fluid="/simulation/$ARCHIVE/$C/fluid"
  echo ""
  echo "========== $C =========="
  docker compose run --rm --user ubuntu fsi bash -lc "
    set -euo pipefail
    cd $fluid
    if [ -f 1/p ]; then echo 'SKIP: t=1 already present'; exit 0; fi
    # nodarcy/fix need ivi zone carved out of vitreous
    if [ -f system/topoSetDict.iviZone ] && ! grep -q 'action  subtract' constant/polyMesh/cellZones 2>/dev/null; then
      topoSet -dict system/topoSetDict.iviZone -constant >> log.topoSet.iviZone 2>&1 || true
    fi
    rm -rf processor* postProcessing
    for d in [0-9]*; do [ \"\$d\" = 0 ] || [ ! -d \"\$d\" ] || rm -rf \"\$d\"; done
    sed -i 's/startFrom       latestTime;/startFrom       startTime;/' system/controlDict
    decomposePar -force > log.decomposePar 2>&1
    SECONDS=0
    mpirun -np 4 --oversubscribe /simulation/_bin/pimpleFoamMassSource -parallel > log.pimpleFoam 2>&1
    echo WALL_SECONDS=\$SECONDS >> log.pimpleFoam
    reconstructPar -latestTime > log.reconstructPar 2>&1
    grep -qE '^Time = 1(\.0*)?[[:space:]]*\$' log.pimpleFoam
    grep -q '^End\$' log.pimpleFoam
    echo DONE $C in \${SECONDS}s
  "
}

TOTAL_START=$SECONDS
for C in "${CASES[@]}"; do
  run_case "$C"
done
ELAPSED=$((SECONDS - TOTAL_START))
echo ""
echo "Queue finished in ${ELAPSED}s ($(($ELAPSED / 60)) min)"
