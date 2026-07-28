#!/bin/bash
# G2-fluid mesh: Gmsh OCC revolve + TM clustering (quality-tuned prisms).
#
# Same geometry/anatomy as g3 fluid (AC ∪ vitreous ∪ TM). Exports hexahedra with
# explicit surface patches → compatible with gmshToFoam.
#
# Usage:
#   ./scripts/gen_mesh_g2_fluid.sh          # M1
#   ./scripts/gen_mesh_g2_fluid.sh M2 M3
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
PY="${REPO}/.venv-geom/bin/python"
GEN="${REPO}/brunaStuff/gen_lamminsalo_g2.py"
LEVELS=("${@:-M1}")

for L in "${LEVELS[@]}"; do
    echo "=== doc-g2-sim1 G2-fluid ${L} (OCC revolve + TM quality) ==="
    "$PY" "$GEN" \
        --case doc-g2-sim1 \
        --mesh \
        --structured \
        --mesh-level "$L" \
        --tip-refine none
done

echo "Done → cases/doc-g2-sim1/geometry/eye_g2_fluid_lamminsalo_{M1..M5}.msh"
