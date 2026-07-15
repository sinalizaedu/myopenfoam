#!/bin/bash
# Sweep de rigidez da gordura orbital (Winkler k) em on-caso-2g.
#
# Roda 5 valores cobrindo a fisiologia:
#   20 kPa/m  : gordura jovem muito macia (1/10 baseline)
#   100 kPa/m : gordura jovem            (1/2 baseline)
#   200 kPa/m : baseline atual
#   1 MPa/m   : gordura envelhecida      (5x baseline)
#   5 MPa/m   : gordura SANS-like dura   (25x baseline)
#
# Total: 5 x ~6.5 min ~= 32 min.
# A polyMesh e' gerada uma vez e reutilizada (so o Winkler regera por k).

set -e
cd "$(dirname "$0")/.."

CASE_DIR=cases/on-caso-2g

# Pares: tag : k(Pa/m)
declare -a SWEEP=(
    "k020k:20000"
    "k100k:100000"
    "k200k:200000"
    "k1M:1000000"
    "k5M:5000000"
)

echo "=== Sweep on-caso-2g: ${#SWEEP[@]} valores de Winkler k ==="
date

for entry in "${SWEEP[@]}"; do
    tag="${entry%%:*}"
    k="${entry##*:}"
    echo ""
    echo "================================================================"
    echo " [$(date +%H:%M:%S)] Rodando tag=${tag}, k=${k} Pa/m"
    echo "================================================================"
    docker compose run --rm fsi bash -lc \
        "cd /simulation/on-caso-2g/ccx && WINKLER_K=${k} OUT_TAG=${tag} ./Allrun" \
        > "brunaStuff/sweep_on-caso-2g_${tag}.log" 2>&1
    rc=$?
    if [ $rc -ne 0 ]; then
        echo " AVISO: tag=${tag} k=${k} retornou ${rc} -- continuando..."
    fi
    # ultima linha do .sta para mostrar lambda atingido
    sta="${CASE_DIR}/ccx/on-caso-2_${tag}.sta"
    if [ -f "$sta" ]; then
        echo " [.sta tail]"
        tail -2 "$sta"
    fi
done

echo ""
echo "=== Sweep concluido ==="
date
ls -la "${CASE_DIR}/ccx/on-caso-2_k"*.dat 2>/dev/null
