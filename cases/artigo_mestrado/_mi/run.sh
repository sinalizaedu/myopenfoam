#!/bin/bash
# run.sh  SCRATCH  DECK  CONTACT  WARP
# Roda o pipeline blockMesh->topoSet->createPatch->conversor->[warp]->ccx
# dentro de um diretorio scratch de estudo de malha (/simulation/_mi/<SCRATCH>).
SCRATCH=$1; DECK=$2; CONTACT=${3:-no}; WARP=${4:-no}
D=/simulation/_mi/$SCRATCH

echo "===== MI RUN $SCRATCH (deck=$DECK contact=$CONTACT warp=$WARP) ====="
cd "$D/solid" || { echo "NO_DIR $D/solid"; exit 1; }

blockMesh > log.blockMesh 2>&1 || { echo "BLOCKMESH_FAIL $SCRATCH"; tail -5 log.blockMesh; exit 1; }
topoSet -dict system/topoSetDict_perturbation > log.topoSet.pert 2>&1 || true
createPatch -overwrite -dict system/createPatchDict_perturbation > log.createPatch.pert 2>&1 || true
if [ "$CONTACT" = "yes" ]; then
    topoSet -dict system/topoSetDict_contact > log.topoSet.contact 2>&1 || true
    createPatch -overwrite -dict system/createPatchDict_contact > log.createPatch.contact 2>&1 || true
fi
NCELLS=$(grep -m1 'nCells' log.blockMesh | awk '{print $NF}')

cd "$D/ccx" || { echo "NO_DIR $D/ccx"; exit 1; }
python3 foam_polymesh_to_ccx_inp.py \
    --polymesh ../solid/constant/polyMesh \
    --out-mesh "${DECK}_mesh.inp" \
    --out-winkler "${DECK}_winkler.inp" \
    --winkler-k 200000 > log.convert 2>&1 || { echo "CONVERT_FAIL $SCRATCH"; tail -5 log.convert; exit 1; }

if [ "$WARP" = "yes" ]; then
    ZMAX=$(python3 -c "from warp_centerline_sweep import max_z; from pathlib import Path; print(max_z(Path('${DECK}_mesh.inp').read_text().splitlines()))")
    # Dura ORTOTROPICA na geometria em "J": gera orientacoes cilindricas por anel
    # axial a partir da malha RETA (antes do warp), alinhadas a tangente local da
    # mesma linha de centro varrida. So' roda se o gerador existir neste nivel.
    if [ -f gen_dura_ortho_orient.py ]; then
        python3 gen_dura_ortho_orient.py --mesh "${DECK}_mesh.inp" \
            --out "${DECK}_dura_orient.inp" \
            --theta0-deg -90 --turn-deg -53.130102 --zmax "$ZMAX" >> log.convert 2>&1
    fi
    python3 warp_centerline_sweep.py --mesh "${DECK}_mesh.inp"    --theta0-deg -90 --turn-deg -53.130102 --zmax "$ZMAX" >> log.convert 2>&1
    python3 warp_centerline_sweep.py --mesh "${DECK}_winkler.inp" --theta0-deg -90 --turn-deg -53.130102 --zmax "$ZMAX" >> log.convert 2>&1
fi

ccx_preCICE -i "$DECK" > log.ccx 2>&1
RC=$?
echo "DONE $SCRATCH ncells=$NCELLS rc=$RC"
tail -2 "$DECK.sta" 2>/dev/null || echo "no_sta"
