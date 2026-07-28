#!/bin/bash
# Export OpenFOAM case for ParaView (Mac): case.foam + VTK fields.
set -euo pipefail
cd "$(dirname "$0")/.."
FLUID=fluid

touch "${FLUID}/case.foam"

rm -rf "${FLUID}/VTK"
(
    cd "${FLUID}"
    echo "=== foamToVTK constant (mesh + p) ==="
    foamToVTK -constant -fields '(p)' 2>&1 | tee log.foamToVTK.constant
    echo "=== foamToVTK latestTime ==="
    foamToVTK -latestTime -fields '(p U)' 2>&1 | tee log.foamToVTK.latest
    for T in 0 5 11 15 21 30; do
        if [ -d "${T}" ]; then
            echo "=== foamToVTK time ${T} ==="
            foamToVTK -time "${T}" -fields '(p U)' 2>&1 | tee -a log.foamToVTK.times
        fi
    done
)

echo ""
echo "ParaView:"
echo "  Fields:  ${FLUID}/case.foam"
echo "  Mesh:    Representation → Surface With Edges (or Wireframe)"
echo "  VTK:     ${FLUID}/VTK/constant/constant.vtm and ${FLUID}/VTK/<time>/<time>.vtm"
