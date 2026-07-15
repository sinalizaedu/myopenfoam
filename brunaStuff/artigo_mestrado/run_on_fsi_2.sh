#!/bin/bash
# Roda o on-fsi-2 dentro do container (sequencia explicita).
set -uo pipefail
ROOT=/simulation/on-fsi-2
cd "$ROOT"

echo "=== Limpando antigos ==="
rm -rf solid/[1-9]* fluid/[1-9]* solid/log.* fluid/log.* precice-* 2>/dev/null || true

echo "=== solid: blockMesh + topoSet + createPatch + checkMesh ==="
( cd solid && rm -rf 0/polyMesh constant/polyMesh
  blockMesh                                                  > log.blockMesh   2>&1
  topoSet -dict system/topoSetDict_contact                   > log.topoSet     2>&1
  createPatch -overwrite -dict system/createPatchDict_contact > log.createPatch 2>&1
  checkMesh                                                  > log.checkMesh   2>&1 ) || { echo "ERROR: solid mesh"; exit 1; }

echo "=== fluid: blockMesh + checkMesh ==="
( cd fluid && rm -rf 0/polyMesh constant/polyMesh
  blockMesh                                                  > log.blockMesh   2>&1
  checkMesh                                                  > log.checkMesh   2>&1 ) || { echo "ERROR: fluid mesh"; exit 1; }

echo "=== Iniciando solvers em paralelo (preCICE) ==="
( cd fluid && solids4Foam > log.solids4Foam 2>&1 ) &
PF=$!
( cd solid && solids4Foam > log.solids4Foam 2>&1 ) &
PS=$!
echo "    Fluid PID=$PF, Solid PID=$PS"

RC_F=0
wait $PF || RC_F=$?
RC_S=0
wait $PS || RC_S=$?

echo "=== Done. RC_F=$RC_F RC_S=$RC_S ==="
echo "--- fluid tail ---"
tail -30 fluid/log.solids4Foam || true
echo "--- solid tail ---"
tail -30 solid/log.solids4Foam || true

if grep -q "FOAM FATAL\|FOAM aborting" fluid/log.solids4Foam solid/log.solids4Foam 2>/dev/null; then
  echo "FATAL detectado:"
  grep -nE "FOAM FATAL|FOAM aborting" fluid/log.solids4Foam solid/log.solids4Foam | head
fi
exit $((RC_F + RC_S))
