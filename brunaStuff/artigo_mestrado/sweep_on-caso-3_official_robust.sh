#!/bin/bash
# Re-run oficial do sweep 3S com Riks robusto (dl_min=1e-8, INC=1500) para
# tracar limit points sem stall numerico. Forca a copia dos outputs com sufixo
# _<tag> MESMO quando ccx retorna rc!=0 (limit point -> "increment too small"),
# para que o ponto que sofre snap genuino ainda salve seu melhor estado.
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"

declare -a SWEEP=( "Pc0:0" "Pc4517:4517" "Pc9034:9034" "Pc13551:13551" "Pc18068:18068" )

echo "=== Sweep 3S OFICIAL (Riks robusto dl_min=1e-8 INC=1500) ==="
date
for entry in "${SWEEP[@]}"; do
    tag="${entry%%:*}"; pc="${entry##*:}"
    echo ""; echo "==== [$(date +%H:%M:%S)] tag=$tag P_CONTACT=$pc ===="
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$REPO/cases:/simulation" \
        -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/on-caso-3/ccx \
        fsi-openfoam:latest \
        bash -lc "P_CONTACT=${pc} OUT_TAG=${tag} WINKLER_K=200000 ./Allrun; rc=\$?; for e in dat frd sta cvg; do cp -f on-caso-3.\$e on-caso-3_${tag}.\$e 2>/dev/null; done; cp -f log.ccx log.ccx_${tag} 2>/dev/null; echo CCX_DONE rc=\$rc" \
        > "brunaStuff/sweep_robust_${tag}.log" 2>&1
    echo "  $(tail -1 cases/on-caso-3/ccx/on-caso-3_${tag}.sta 2>/dev/null)"
    echo "  $(grep -h 'CCX_DONE' brunaStuff/sweep_robust_${tag}.log | tail -1)"
done
echo ""; echo "=== sweep robusto concluido ==="; date
