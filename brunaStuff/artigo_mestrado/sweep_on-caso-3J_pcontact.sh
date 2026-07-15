#!/bin/bash
# Sweep de pressao de contato da arteria oftalmica (P_contact) em on-caso-3J.
#
# Caso 3J = GEOMETRIA do Caso 2J (tortuosidade em "J") + CARGAS do Caso 3F
# (compressao axial clinica Dy=-1.0 mm + P_contact focal + PIC 1333 Pa).
# Mantem Winkler = 200 kPa/m (baseline) e varia P_contact:
#   0      Pa : controle (sem arteria oftalmica)
#   4517   Pa : 0.5x  (~33 mmHg, diastole baixa)
#   9034   Pa : 1.0x baseline (~67 mmHg, pressao arterial media oftalmica)
#   13551  Pa : 1.5x  (~100 mmHg, hipertensivo leve)
#   18068  Pa : 2.0x  (~135 mmHg, pico sistolico)
#
# A polyMesh (com patch de contato) e' gerada uma vez e reutilizada; o warp em
# "J" e a dura ortotropica sao regerados a cada run (deterministicos).

set -e
cd "$(dirname "$0")/.."

CASE_DIR=cases/on-caso-3J

declare -a SWEEP=(
    "Pc0:0"
    "Pc4517:4517"
    "Pc9034:9034"
    "Pc13551:13551"
    "Pc18068:18068"
)

echo "=== Sweep on-caso-3J: ${#SWEEP[@]} valores de P_contact (arteria oftalmica) ==="
echo "    Geometria em J + Winkler 200 kPa/m, SAS solido, dura ortotropica, Dy=-1.0 mm"
date

for entry in "${SWEEP[@]}"; do
    tag="${entry%%:*}"
    pc="${entry##*:}"
    echo ""
    echo "================================================================"
    echo " [$(date +%H:%M:%S)] tag=${tag}  P_CONTACT=${pc} Pa"
    echo "================================================================"
    set +e
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$(pwd)/cases:/simulation" \
        -v "$(pwd)/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/on-caso-3J/ccx \
        fsi-openfoam:latest \
        bash -lc "P_CONTACT=${pc} OUT_TAG=${tag} WINKLER_K=200000 ./Allrun" \
        > "brunaStuff/sweep_on-caso-3J_${tag}.log" 2>&1
    rc=$?
    set -e
    if [ $rc -ne 0 ]; then
        echo " AVISO: tag=${tag} Pc=${pc} Pa retornou rc=${rc} -- continuando..."
    fi
    sta="${CASE_DIR}/ccx/on-caso-3J_${tag}.sta"
    if [ -f "$sta" ]; then
        echo " [.sta tail]"
        tail -2 "$sta"
    fi
done

echo ""
echo "=== Sweep concluido ==="
date
ls -la "${CASE_DIR}/ccx/on-caso-3J_Pc"*.dat 2>/dev/null || true
