#!/usr/bin/env bash
# Exporta cada cellZone do caso sólido para VTK separado — ParaView abre só íris, só lente, etc.
# (No leitor .foam costuma vir um único internalMesh; patches são só contorno.)
#
# OpenFOAM v2512: usar -cellZone <nome> (não existe -cellZones).
#
# Uso na raiz do repositório:
#   bash brunaStuff/export_solid_zones_to_vtk.sh
# Ou com caminho absoluto do caso sólido:
#   bash brunaStuff/export_solid_zones_to_vtk.sh /caminho/para/cases/eye-fsi-tc0/solid
#
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SOLID="${1:-$REPO/cases/eye-fsi-tc0/solid}"
cd "$SOLID"

echo ">>> Caso: $SOLID"
echo ">>> Exportando zonas: lens, iris, sclera, cornea (campo D, último tempo)..."

for z in lens iris sclera cornea; do
  foamToVTK -cellZone "$z" -latestTime -fields '(D)' -name "VTK_${z}" -overwrite
done

echo ">>> Abra no ParaView, por exemplo:"
echo "    $SOLID/VTK_iris/*/internal.vtu"
echo "    (Colorize por D ou mag(D); escala só dessa zona.)"
