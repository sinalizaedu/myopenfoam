#!/bin/bash
# Generate doc-g2-sim1 bulk meshes for doc-g2-sim4 (incl. lean M8).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
SIM4="$(cd "$(dirname "$0")/.." && pwd)"
"${REPO}/cases/doc-g2-sim1/scripts/gen_mesh_g2_fluid.sh" M8 M5 M4 M1 M2 M3
mkdir -p "${SIM4}/geometry"
for L in M8 M5 M4 M1 M2 M3; do
  ln -sfn "../../doc-g2-sim1/geometry/eye_g2_fluid_lamminsalo_${L}.msh" \
    "${SIM4}/geometry/eye_g2_fluid_lamminsalo_${L}.msh"
done
echo "Symlinked M8,M5,M4,M1–M3 → doc-g2-sim4/geometry/"
