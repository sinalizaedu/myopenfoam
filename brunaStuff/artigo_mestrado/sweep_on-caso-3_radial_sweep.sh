#!/bin/bash
# Sweep OFICIAL do on-caso-3 na malha RADIAL radpia2dura3 (pia 1->2, dura 2->3).
# UNICA coisa trocada em relacao a producao: a resolucao radial das laminas.
# O refino radial NAO altera a grade circunferencial/axial da dura_outer, logo
# a area do patch contact_local permanece ~A_f100 e P=p_c gera EXATAMENTE a
# mesma forca arterial da producao. Tudo o mais (materiais, BCs, Dz=-1.5,
# Winkler 200k, Riks INC=500 dl_min=1e-5) vem do deck de producao copiado.
#
# Objetivo: tabela limpa em lambda=1.0 (sem o snap artefato de 9034 da malha
# de producao com 1 celula radial na pia).
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"
TAG=radpia2dura3
FACTOR=rad:2:3
SCR="on-caso-3__${TAG}"
DECK="cases/_mi/${SCR}/ccx/on-caso-3.inp"

declare -a SWEEP=( 0 4517 9034 13551 18068 )

echo "=== Sweep 3S RADIAL ($TAG) — so a malha muda ==="; date

# 1) monta o scratch radial UMA vez (blockMeshDict radial + deck producao)
bash brunaStuff/build_meshindep.sh on-caso-3 on-caso-3 "$FACTOR" "$TAG" yes no

for pc in "${SWEEP[@]}"; do
    echo ""; echo "==== [$(date +%H:%M:%S)] P_CONTACT=$pc ===="
    # seta a pressao de contato no deck do scratch
    sed -i.bak -E "s|^CONTACT_LOCAL_SURF, P, .*$|CONTACT_LOCAL_SURF, P, ${pc}|" "$DECK"
    grep -n "CONTACT_LOCAL_SURF, P," "$DECK" | head -1
    # roda pipeline completo (blockMesh->topoSet/createPatch->conversor->ccx)
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$REPO/cases:/simulation" \
        -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/_mi \
        fsi-openfoam:latest \
        bash -lc "./run.sh ${SCR} on-caso-3 yes no" \
        > "brunaStuff/sweep_radial_Pc${pc}.log" 2>&1
    rc=$?
    # salva outputs com sufixo por pressao (mesmo se ccx rc!=0)
    CDIR="cases/_mi/${SCR}/ccx"
    for e in dat frd sta cvg; do cp -f "$CDIR/on-caso-3.$e" "$CDIR/on-caso-3_Pc${pc}.$e" 2>/dev/null; done
    cp -f "$CDIR/log.ccx" "$CDIR/log.ccx_Pc${pc}" 2>/dev/null
    A=$(python3 brunaStuff/contact_area.py "cases/_mi/${SCR}/solid/constant/polyMesh" 2>/dev/null || echo NA)
    echo "  rc=$rc  A_patch=${A} m^2  F=P*A=$(python3 -c "print(${pc}*${A}*1e3)" 2>/dev/null || echo NA) mN"
    echo "  $(tail -1 "$CDIR/on-caso-3_Pc${pc}.sta" 2>/dev/null || echo no_sta)"
done
echo ""; echo "=== sweep radial concluido ==="; date
