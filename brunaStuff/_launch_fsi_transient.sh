#!/bin/bash
# Launcher para rodar o FSI transiente em background dentro do container.
# Uso (dentro do container):  ./_launch_fsi_transient.sh <case_dir>
set -uo pipefail
CASE_DIR="$1"
cd "$CASE_DIR" || { echo "ERROR: cd $CASE_DIR"; exit 2; }

rm -rf precice-Fluid-* precice-Solid-* precice-run 2>/dev/null || true
rm -f fluid/log.solids4Foam solid/log.solids4Foam 2>/dev/null || true

echo "$(date -Is) starting fluid solids4Foam in $CASE_DIR/fluid"
( cd fluid && nohup solids4Foam > log.solids4Foam 2>&1 < /dev/null & echo $! > .pid )
echo "$(date -Is) starting solid solids4Foam in $CASE_DIR/solid"
( cd solid && nohup solids4Foam > log.solids4Foam 2>&1 < /dev/null & echo $! > .pid )
sleep 0.5
echo "fluid pid=$(cat fluid/.pid)  solid pid=$(cat solid/.pid)"
