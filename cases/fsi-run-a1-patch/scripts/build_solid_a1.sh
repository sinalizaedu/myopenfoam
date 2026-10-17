#!/bin/bash
# Install A1 solid polyMesh into fsi-run-a1-patch/solid.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="../fsi-transient-a1-patch/solid_meshes/A1"
REPO="$(cd ../.. && pwd)"
EXP="$REPO/brunaStuff/o1_solid_export.py"
[ -f "$EXP" ] || EXP="/opt/brunaStuff/o1_solid_export.py"

if [ ! -d "$SRC/constant/polyMesh" ]; then
    echo "ERROR: missing $SRC/constant/polyMesh" >&2
    exit 1
fi

echo "=== build A1 solid for $(basename "$PWD") ==="
rm -rf solid/constant/polyMesh solid/0 solid/precice-profiling
mkdir -p solid/0 solid/constant
cp -a "$SRC/constant/polyMesh" solid/constant/polyMesh
python3 "$EXP" --mode fields --case solid
mkdir -p solid/initial
cp -f solid/0/D solid/initial/D
cp -f solid/0/solidForce solid/initial/solidForce
if [ -f "$SRC/constant/mechanicalProperties" ]; then
    cp -f "$SRC/constant/mechanicalProperties" solid/constant/mechanicalProperties
fi
(cd solid && checkMesh 2>&1 | tee log.checkMesh)
echo "=== A1 solid installed ==="
