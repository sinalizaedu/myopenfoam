#!/bin/bash
# G2 sim1–4 with 30G lumen tip refinement (generate meshes on host first).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${REPO}/cases/run_g2_30g_pipeline.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== G2 30G pipeline $(date -Iseconds) ==="

run_case() {
    local dir="$1"; shift
    echo ""
    echo "===== ${dir} $* ====="
    docker compose -f "${REPO}/docker-compose.yaml" run --rm fsi bash -lc \
        "cd /simulation/${dir} && $*"
}

# 1) Mesh independence (sim1 M1–M3 steady IOP)
python3 "${REPO}/cases/doc-g2-sim1/scripts/run_mesh_independence.py"

# 2) Sim1 production baseline (M1)
run_case doc-g2-sim1 "MESH_LEVEL=M1 ./Allrun"

# 3) Sim2 IVI baseline + experiment
run_case doc-g2-sim2 "./Allclean && MODE=baseline MESH_LEVEL=M1 ./Allrun"
run_case doc-g2-sim2 "MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun"

# 4) Sim3 ACP
run_case doc-g2-sim3 "./Allclean && MODE=baseline MESH_LEVEL=M1 ./Allrun"
run_case doc-g2-sim3 "MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun"

# 5) Sim4 IVI+ACP
run_case doc-g2-sim4 "./Allclean && MODE=baseline MESH_LEVEL=M1 ./Allrun"
run_case doc-g2-sim4 "MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun"

echo "=== pipeline done $(date -Iseconds) ==="
