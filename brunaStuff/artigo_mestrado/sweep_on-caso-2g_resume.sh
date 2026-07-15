#!/bin/bash
# Continua o sweep on-caso-2g a partir de k100k (k020k ja rodou).
set -e
cd "$(dirname "$0")/.."

declare -a SWEEP=(
    "k100k:100000"
    "k200k:200000"
    "k1M:1000000"
    "k5M:5000000"
)

echo "=== Continuando sweep on-caso-2g (k020k ja completou) ==="
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
        > "brunaStuff/sweep_on-caso-2g_${tag}.log" 2>&1 || echo " AVISO: tag=${tag} falhou"
    sta="cases/on-caso-2g/ccx/on-caso-2_${tag}.sta"
    if [ -f "$sta" ]; then
        echo " [.sta tail]"
        tail -2 "$sta"
    fi
done

echo ""
echo "=== Sweep concluido ==="
date
ls -la cases/on-caso-2g/ccx/on-caso-2_k*.dat 2>/dev/null
