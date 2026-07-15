#!/bin/bash
# Refino RADIAL dirigido das laminas (pia/dura) do on-caso-3, com a carga
# arterial normalizada por forca. O refino radial NAO altera a grade
# circunferencial/axial da dura_outer, logo a area do patch contact_local
# permanece ~A_f100 e P=9034 ja' corresponde a F_alvo=35.4 mN.
#
# Niveis: radpia2dura3 (pia 1->2, dura 2->3) e radpia3dura4 (pia 3, dura 4).
# Carga: p_c=9034 Pa (baseline SANS), Dz=-1.5 mm, Winkler 200 kPa/m.
# Objetivo: convergencia do PICO de von Mises (secante pre-flambagem),
# corrigindo a subestimacao da malha de producao (1 celula radial na pia).
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"
PC=9034

declare -a LV=( "rad:2:3:radpia2dura3" "rad:3:4:radpia3dura4" )

for entry in "${LV[@]}"; do
    factor="${entry%:*}"; tag="${entry##*:}"
    echo "================================================================"
    echo " [$(date +%H:%M:%S)] build+run $tag (factor=$factor, P_contact=$PC)"
    echo "================================================================"
    # 1) monta scratch (host): blockMeshDict radial + deck atual + conversor
    bash brunaStuff/build_meshindep.sh on-caso-3 on-caso-3 "$factor" "$tag" yes no
    # 2) seta P_contact na copia do deck (forca normalizada; A~A_f100)
    DECK="cases/_mi/on-caso-3__${tag}/ccx/on-caso-3.inp"
    sed -i.bak -E "s|^CONTACT_LOCAL_SURF, P, .*$|CONTACT_LOCAL_SURF, P, ${PC}|" "$DECK"
    grep -n "CONTACT_LOCAL_SURF, P,\|INC=\|RIKS" "$DECK" | head
    # 3) roda pipeline (blockMesh->topoSet/createPatch->conversor->ccx) no container
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$REPO/cases:/simulation" \
        -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/_mi \
        fsi-openfoam:latest \
        bash -lc "./run.sh on-caso-3__${tag} on-caso-3 yes no" \
        > "brunaStuff/meshindep_on-caso-3_${tag}.log" 2>&1
    echo " rc=$?"
    # 4) confere area do patch e a forca efetiva
    A=$(python3 brunaStuff/contact_area.py "cases/_mi/on-caso-3__${tag}/solid/constant/polyMesh" 2>/dev/null || echo NA)
    echo " A_patch=${A} m^2  -> F = P*A = $(python3 -c "print(${PC}*${A}*1e3)" 2>/dev/null || echo NA) mN"
    tail -2 "cases/_mi/on-caso-3__${tag}/ccx/on-caso-3.sta" 2>/dev/null || echo " (sem .sta)"
done
echo ""; echo "=== concluido. Analise: secante von Mises f100 vs radial ==="
