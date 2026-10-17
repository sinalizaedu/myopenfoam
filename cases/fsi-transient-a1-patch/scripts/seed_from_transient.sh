#!/bin/bash
# Seed polyMesh from doc-transient-o1-patch-fluid when that case already has a mesh.
set -euo pipefail
cd "$(dirname "$0")/.."
CASE_NAME="$(basename "$PWD")"
SEED="../doc-transient-o1-patch-fluid"

if [ ! -d "$SEED/fluid/constant/polyMesh" ]; then
  echo "ERROR: missing $SEED/fluid/constant/polyMesh" >&2
  echo "Run MODE=baseline in doc-transient-o1-patch-fluid or fsi-transient-o1-patch first." >&2
  exit 1
fi

echo "=== seed $CASE_NAME polyMesh from $SEED ==="
rm -rf fluid/constant/polyMesh
mkdir -p fluid/constant
cp -a "$SEED/fluid/constant/polyMesh" fluid/constant/polyMesh

if [ -f "$SEED/fluid/system/fvOptions" ]; then
  cp -f "$SEED/fluid/system/fvOptions" fluid/system/fvOptions
fi

mkdir -p fluid/0
cp -f fluid/initial/U.baseline fluid/0/U
cp -f fluid/initial/p.baseline fluid/0/p
rm -f fluid/constant/dynamicMeshDict
touch fluid/O1.foam fluid/case.foam
echo "=== seed done: polyMesh + 0/ from U.baseline / p.baseline ==="
