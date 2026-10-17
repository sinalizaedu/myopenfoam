#!/bin/bash
# Seed polyMesh + d_TM from the matching steady baseline. No simpleFoam time dump.
set -euo pipefail
cd "$(dirname "$0")/.."
CASE_NAME="$(basename "$PWD")"
BASELINE="../doc-baseline-o1-patch-fluid"

if [ ! -d "$BASELINE/fluid/constant/polyMesh" ]; then
  echo "ERROR: missing $BASELINE/fluid/constant/polyMesh" >&2
  exit 1
fi

echo "=== seed $CASE_NAME polyMesh from $BASELINE ==="
rm -rf fluid/constant/polyMesh
mkdir -p fluid/constant
cp -a "$BASELINE/fluid/constant/polyMesh" fluid/constant/polyMesh

if [ -f "$BASELINE/fluid/system/fvOptions" ]; then
  cp -f "$BASELINE/fluid/system/fvOptions" fluid/system/fvOptions
fi

mkdir -p fluid/0
cp -f fluid/initial/U.baseline fluid/0/U
cp -f fluid/initial/p.baseline fluid/0/p
touch fluid/O1.foam fluid/case.foam
echo "=== seed done: polyMesh + 0/ from U.baseline / p.baseline ==="
