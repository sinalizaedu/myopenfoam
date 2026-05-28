#!/bin/bash
# Coupled solve only (meshes must exist). Exits non-zero on failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
[[ -n "${WM_PROJECT_DIR:-}" ]] || { echo "ERROR: OpenFOAM env required" >&2; exit 1; }

for d in fluid/constant/polyMesh/points solid/constant/polyMesh/points; do
  [[ -f "$d" ]] || { echo "ERROR: missing mesh ($d). Run ./Allrun or ./Allrun-resume.sh first." >&2; exit 1; }
done

# Remove time directories (anything matching number(.number)? but NOT named '0').
# The previous `find -regex` was Emacs-regex by default and silently kept the
# 0.0025/0.005/... dirs around, polluting the run.
for side in fluid solid; do
  for d in "${side}"/[0-9]*; do
    [[ -d "$d" ]] || continue
    base="$(basename "$d")"
    [[ "$base" == "0" ]] && continue
    [[ "$base" =~ ^[0-9]+(\.[0-9]+)?$ ]] && rm -rf "$d"
  done
done
rm -rf fluid/processor* solid/processor* precice-run 2>/dev/null || true
find fluid solid -maxdepth 1 -name 'precice-*' -exec rm -rf {} + 2>/dev/null || true
rm -f fluid/log.pimpleFoam solid/log.solids4Foam 2>/dev/null || true
: > "${ROOT}/solid/precice-Solid-watchpoint-arteryNearestON.log"

echo "=== Coupled solvers (preCICE) ==="
(cd fluid && pimpleFoam > log.pimpleFoam 2>&1) &
PF=$!
(cd solid && solids4Foam > log.solids4Foam 2>&1) &
PS=$!
wait $PF || { echo "ERROR: pimpleFoam failed"; tail -40 fluid/log.pimpleFoam; exit 1; }
wait $PS || { echo "ERROR: solids4Foam failed"; tail -40 solid/log.solids4Foam; exit 1; }

if grep -q "FOAM FATAL\|FOAM aborting\|nan" solid/log.solids4Foam; then
  echo "ERROR: solids4Foam log contains fatal/nan"
  tail -30 solid/log.solids4Foam
  exit 1
fi
if grep -q "FOAM FATAL\|FOAM aborting" fluid/log.pimpleFoam; then
  echo "ERROR: pimpleFoam log contains fatal"
  tail -30 fluid/log.pimpleFoam
  exit 1
fi

python3 "${ROOT}/scripts/post_artoph_fsi_export_csv.py" 2>/dev/null || true
echo "=== Allrun-solve finished OK ==="
