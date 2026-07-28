#!/bin/bash
# Mesh independence: doc-g2-sim2 IVI (M1/M2/M3), baseline + experiment per level.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${REPO}/cases/doc-g2-sim2/mesh_independence/run.log"
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "=== sim2 IVI mesh independence $(date -Iseconds) ==="
"${REPO}/.venv-geom/bin/python" \
    "${REPO}/cases/doc-g2-sim2/scripts/run_mesh_independence.py"
echo "=== DONE $(date -Iseconds) ==="
