#!/bin/bash
# Sweep de pressao de contato da arteria oftalmica (P_contact) em on-caso-3-sf.
#
# on-caso-3-sf = "on-caso-3 Sem Forca (frontal)": IGUAL ao sweep do on-caso-3,
# mas o .inp NAO tem nenhuma compressao/forca axial vinda da frente (sem Dz
# prescrito, sem CLOAD EOM no globo). A unica carga ativa e' a P_contact
# LATERAL. Objetivo: ver se a flambagem/kink do nervo acontece apenas com a
# indentacao lateral da arteria oftalmica.
#
# Mantem Winkler = 200 kPa/m (baseline, conforme tab:casos-setup do artigo_final;
# 3F usa o mesmo k_w do 3S) e varia P_contact:
#   0      Pa : controle (sem arteria, so perturbacao lateral)
#   4517   Pa : 0.5x  (~33 mmHg)
#   9034   Pa : 1.0x baseline (~67 mmHg)
#   13551  Pa : 1.5x  (~100 mmHg)
#   18068  Pa : 2.0x  (~135 mmHg, pico sistolico)
#
# Total: 5 runs sequenciais. polyMesh gerada/reutilizada uma vez.

set -e
cd "$(dirname "$0")/.."

CASE_DIR=cases/on-caso-3-sf

declare -a SWEEP=(
    "Pc0:0"
    "Pc4517:4517"
    "Pc9034:9034"
    "Pc13551:13551"
    "Pc18068:18068"
)

echo "=== Sweep on-caso-3-sf: ${#SWEEP[@]} valores de P_contact (arteria oftalmica, LATERAL) ==="
echo "    SEM forca frontal (sem Dz, sem EOM). Winkler k=200 kPa/m (baseline), Riks ARCMAX=1.0"
date

for entry in "${SWEEP[@]}"; do
    tag="${entry%%:*}"
    pc="${entry##*:}"
    echo ""
    echo "================================================================"
    echo " [$(date +%H:%M:%S)] tag=${tag}  P_CONTACT=${pc} Pa (LATERAL)"
    echo "================================================================"
    set +e
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$(pwd)/cases:/simulation" \
        -v "$(pwd)/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/on-caso-3-sf/ccx \
        fsi-openfoam:latest \
        bash -lc "P_CONTACT=${pc} OUT_TAG=${tag} WINKLER_K=200000 ./Allrun" \
        > "brunaStuff/sweep_on-caso-3-sf_${tag}.log" 2>&1
    rc=$?
    set -e
    if [ $rc -ne 0 ]; then
        echo " AVISO: tag=${tag} Pc=${pc} Pa retornou rc=${rc} -- continuando..."
    fi
    sta="${CASE_DIR}/ccx/on-caso-3-sf_${tag}.sta"
    if [ -f "$sta" ]; then
        echo " [.sta tail]"
        tail -2 "$sta"
    fi
done

echo ""
echo "=== Sweep concluido ==="
date
ls -la "${CASE_DIR}/ccx/on-caso-3-sf_Pc"*.dat 2>/dev/null || true
echo ""
echo "Proximo passo: python3 brunaStuff/analyze_on-caso-3-sf_pcontact_sweep.py"
