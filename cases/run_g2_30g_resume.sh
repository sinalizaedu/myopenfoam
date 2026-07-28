#!/bin/bash
# Resume G2 30G pipeline from M2 (M1 already archived).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${REPO}/cases/run_g2_30g_full.log"
DC="docker compose -f ${REPO}/docker-compose.yaml run --rm fsi bash -lc"

exec >> "$LOG" 2>&1
echo ""
echo "=== G2 30G RESUME $(date -Iseconds) — from M2 ==="

run() {
    local title="$1"; shift
    echo ""
    echo "########## ${title} $(date -Iseconds) ##########"
    "$@"
    echo "########## ${title} OK $(date -Iseconds) ##########"
}

for L in M2 M3; do
    run "mesh-indep-${L}" \
        $DC "cd /simulation/doc-g2-sim1 && ./Allclean && MESH_LEVEL=${L} ./Allrun"
    mkdir -p "${REPO}/cases/doc-g2-sim1/mesh_independence/${L}"
    cp "${REPO}/cases/doc-g2-sim1/fluid/log.simpleFoam" \
       "${REPO}/cases/doc-g2-sim1/mesh_independence/${L}/" 2>/dev/null || true
    cp "${REPO}/cases/doc-g2-sim1/fluid/log.checkMesh" \
       "${REPO}/cases/doc-g2-sim1/mesh_independence/${L}/" 2>/dev/null || true
    cp "${REPO}/cases/doc-g2-sim1/fluid/postProcessing/iop_probe/0/p" \
       "${REPO}/cases/doc-g2-sim1/mesh_independence/${L}/iop_probe_p.txt" 2>/dev/null || true
    (cd "${REPO}/cases/doc-g2-sim1" && python3 scripts/extract_step0_metrics.py) || true
done

grep -h "nCells:" "${REPO}/cases/doc-g2-sim1/mesh_independence/"*/log.checkMesh 2>/dev/null \
    | head -3 || true

run "sim2-baseline" \
    $DC "cd /simulation/doc-g2-sim2 && ./Allclean && MODE=baseline MESH_LEVEL=M1 ./Allrun"

run "sim2-experiment" \
    $DC "cd /simulation/doc-g2-sim2 && MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun"

run "sim3-baseline" \
    $DC "cd /simulation/doc-g2-sim3 && ./Allclean && MODE=baseline MESH_LEVEL=M1 ./Allrun"

run "sim3-experiment" \
    $DC "cd /simulation/doc-g2-sim3 && MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun"

run "sim4-baseline" \
    $DC "cd /simulation/doc-g2-sim4 && ./Allclean && MODE=baseline MESH_LEVEL=M1 ./Allrun"

run "sim4-experiment" \
    $DC "cd /simulation/doc-g2-sim4 && MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun"

echo ""
echo "=== ALL DONE $(date -Iseconds) ==="
