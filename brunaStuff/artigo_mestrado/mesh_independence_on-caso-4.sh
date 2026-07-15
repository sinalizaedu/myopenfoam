#!/bin/bash
# mesh_independence_on-caso-4.sh - estudo de independencia de malha do on-caso-4.
#
# Roda UM estagio representativo (S2_upper: P_CSF=3800, P_contact=18068, mesmo
# patch de contato em metros) em malhas de resolucoes crescentes (fator 1x/2x/3x
# nas contagens de celula do blockMesh) e compara as metricas. Como o patch de
# contato e' definido por um box em METROS e as cargas sao PRESSOES (Pa), so a
# discretizacao muda -> teste de independencia valido. Winkler e' area-ponderado
# (k_i = k*area_nodal), entao a rigidez total da fundacao se mantem.
#
# Uso:  bash brunaStuff/mesh_independence_on-caso-4.sh "1 2 3"
#       (default: "1 2 3"; fator 1 reaproveita on-caso-4_S2_upper.frd se existir)

set -e
cd "$(dirname "$0")/.."   # raiz do repo

FACTORS="${1:-1 2}"       # 1x (base) vs 2x (elemento pela metade em r,theta,z)
NPROC="${NPROC:-4}"        # threads spooles. Docker tem so 7.7 GB -> 8 threads
                           # estouravam a RAM (OOM kill) na malha 2x. 4 e' o
                           # equilibrio memoria x velocidade.
IMG=fsi-openfoam:latest
SYS=cases/on-caso-4/solid/system
CCX=cases/on-caso-4/ccx

# Estagio do estudo: BASELINE S0 (carga menor -> contato estavel -> Riks tolera
# incrementos grandes -> poucos incrementos -> viavel na malha fina). Independencia
# de malha mede ERRO DE DISCRETIZACAO, valido em qualquer estagio bem convergido.
REUSE_FRD="$CCX/on-caso-4_S0_baseline.frd"   # mesh1 = run de producao do S0
PCSF=1333
PCONTACT=9034.0
BOX='(2.3941e-03 -5.3702e-04 2.0840e-02) (2.6000e-03 5.3702e-04 2.4160e-02)'

# garante os dicts refinados
[ -f "$SYS/blockMeshDict.mesh1" ] || cp "$SYS/blockMeshDict" "$SYS/blockMeshDict.mesh1"
[ -f "$SYS/blockMeshDict.mesh2" ] || python3 brunaStuff/refine_blockmesh.py "$SYS/blockMeshDict.mesh1" "$SYS/blockMeshDict.mesh2" 2
[ -f "$SYS/blockMeshDict.mesh3" ] || python3 brunaStuff/refine_blockmesh.py "$SYS/blockMeshDict.mesh1" "$SYS/blockMeshDict.mesh3" 3

# Afrouxa o teto de incremento do Riks SO para o estudo de malha (0.02 -> 0.1). O
# teste compara o EQUILIBRIO FINAL em lambda=1 (unico p/ problema estatico). No
# baseline S0 a carga e' baixa e o contato e' estavel, entao incrementos grandes
# convergem (no S2, com o dobro da pressao, o passo grande causava inversao de
# elemento). Cortes automaticos (min 1e-9) garantem robustez. Restaurado ao final.
INP="$CCX/on-caso-4.inp"
cp "$INP" "$INP.meshbak"
sed -i -E 's|^0\.005, 1\.0, 1e-9, 0\.02, 1\.0$|0.02, 1.0, 1e-9, 0.1, 1.0|' "$INP"
echo "Riks (estudo de malha): $(grep -A1 '^\*STATIC, RIKS' "$INP" | tail -1)"

run_mesh () {
    local n="$1"
    # fator 1: reaproveita o run de producao do estagio (mesma fisica) se ja existe
    if [ "$n" = "1" ] && [ -f "$REUSE_FRD" ]; then
        echo "   [mesh1] reaproveitando $(basename "$REUSE_FRD") -> on-caso-4_mesh1.frd"
        cp "$REUSE_FRD" "$CCX/on-caso-4_mesh1.frd"
        cp "${REUSE_FRD%.frd}.dat" "$CCX/on-caso-4_mesh1.dat" 2>/dev/null || true
        return
    fi
    echo "   [mesh${n}] instalando blockMeshDict.mesh${n} e rodando ccx..."
    cp "$SYS/blockMeshDict.mesh${n}" "$SYS/blockMeshDict"
    set +e
    # OMP_NUM_THREADS paraleliza o solver direto spooles (malhas finas tem milhares
    # de DOF; single-thread fica inviavel). NUMBER_OF_CPUS idem p/ montagem.
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -e OMP_NUM_THREADS="${NPROC}" -e NUMBER_OF_CPUS="${NPROC}" \
        -v "$(pwd)/cases:/simulation" \
        -v "$(pwd)/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/on-caso-4/ccx \
        "$IMG" \
        bash -lc "export OMP_NUM_THREADS=${NPROC} NUMBER_OF_CPUS=${NPROC}; P_CSF=${PCSF} P_CONTACT=${PCONTACT} CONTACT_BOX='${BOX}' WINKLER_K=2000000 OUT_TAG=mesh${n} REMESH=1 ./Allrun" \
        > "brunaStuff/mesh_indep_on-caso-4_mesh${n}.log" 2>&1
    local rc=$?
    set -e
    echo "      mesh${n} rc=${rc}  $(tail -1 ${CCX}/on-caso-4_mesh${n}.sta 2>/dev/null || echo NOSTA)"
    # numero de elementos da malha (do log do blockMesh)
    grep -E "cells:|nCells" "brunaStuff/mesh_indep_on-caso-4_mesh${n}.log" | head -1 | sed 's/^/      /'
}

echo "=== on-caso-4: independencia de malha (estagio S0_baseline) ==="
date
for n in $FACTORS; do
    echo ""
    echo "---- [$(date +%H:%M:%S)] malha fator ${n}x ----"
    run_mesh "$n"
done

# restaura a malha base e o .inp de producao
cp "$SYS/blockMeshDict.mesh1" "$SYS/blockMeshDict"
[ -f "$INP.meshbak" ] && mv "$INP.meshbak" "$INP"
echo ""
echo "=== runs concluidos. Analise: python3 brunaStuff/analyze_mesh_independence_on-caso-4.py ==="
python3 brunaStuff/analyze_mesh_independence_on-caso-4.py
date
