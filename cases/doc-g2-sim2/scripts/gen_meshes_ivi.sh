#!/bin/bash
# Generate doc-g2-sim2 IVI-only 30G meshes (M1/M2/M3).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${REPO}/.venv-geom/bin/python"
GEN="${REPO}/brunaStuff/gen_lamminsalo_g2.py"
for L in M1 M2 M3; do
    echo "=== sim2 IVI mesh ${L} ==="
    "$PY" "$GEN" --case doc-g2-sim2 --mesh --mesh-level "$L" --tip-refine ivi
done
echo "Done. Meshes in cases/doc-g2-sim2/geometry/"
