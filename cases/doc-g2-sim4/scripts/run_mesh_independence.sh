#!/bin/bash
# Mesh independence doc-g2-sim4 (M5 coarsest … M3 finest; M1 = reference).
#
# Usage:
#   ./scripts/run_mesh_independence.sh              # all levels
#   LEVELS=M1,M2,M3 ./scripts/run_mesh_independence.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$(dirname "$0")/.."
export LEVELS="${LEVELS:-}"
python3 scripts/run_mesh_independence.py
