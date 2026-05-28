#!/bin/bash
# Re-mesh solid + coupled solve (fluid mesh kept). Use after fixing solid snappy/solidProperties.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -z "${WM_PROJECT_DIR:-}" ]]; then
  echo "ERROR: load OpenFOAM env first (Docker: docker compose run --rm fsi bash -l)" >&2
  exit 1
fi

cp -f constant/triSurface/artery_inner.stl constant/triSurface/artery_outer.stl solid/constant/triSurface/

echo "=== Clean solid polyMesh (keep blockMeshDict only) ==="
(
  cd solid/constant/polyMesh
  find . -mindepth 1 ! -name blockMeshDict -exec rm -rf {} +
)

echo "=== Re-mesh solid only ==="
(cd solid && bash ./Allmesh)

echo "=== Coupled solvers ==="
bash "${ROOT}/Allrun-solve.sh"
