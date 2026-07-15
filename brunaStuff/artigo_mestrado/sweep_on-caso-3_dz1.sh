#!/bin/bash
# Caso 3F com rampa Dz = -1.0 mm (em vez de -1.5 mm).
#
# Re-roda o sweep de pressao de contato da arteria oftalmica (P_contact) na
# malha radial OFICIAL radpia2dura3, e checa independencia de malha no ponto
# baseline (Pc9034) nas malhas mais finas radpia3dura4 e radpia4dura5.
# UNICA mudanca em relacao ao sweep do artigo: a rampa axial Dz cai de
# -1.5 mm para -1.0 mm (limite clinico do recuo cefalico). Tudo o mais
# (materiais, BCs, Winkler 200 kPa/m, PIC 1333 Pa, Riks INC=500 dl_min=1e-5)
# vem do deck de producao.
#
# Saidas com sufixo _Pc<val> em cada scratch cases/_mi/on-caso-3__<tag>/ccx.
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"
DZ="-1.00e-3"

build_and_set() {
    local tag=$1 factor=$2
    bash brunaStuff/build_meshindep.sh on-caso-3 on-caso-3 "$factor" "$tag" yes no
    local deck="cases/_mi/on-caso-3__${tag}/ccx/on-caso-3.inp"
    sed -i.bak -E "s|^ANTERIOR_GLOBO, 3, 3, .*\$|ANTERIOR_GLOBO, 3, 3, ${DZ}|" "$deck"
    echo -n "   [$tag] "; grep -m1 "ANTERIOR_GLOBO, 3, 3," "$deck"
}

run_pc() {
    local tag=$1 pc=$2
    local scr="on-caso-3__${tag}"
    local deck="cases/_mi/${scr}/ccx/on-caso-3.inp"
    sed -i.bak -E "s|^CONTACT_LOCAL_SURF, P, .*\$|CONTACT_LOCAL_SURF, P, ${pc}|" "$deck"
    echo "==== [$(date +%H:%M:%S)] $tag  P_CONTACT=$pc  Dz=$DZ ===="
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$REPO/cases:/simulation" \
        -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/_mi \
        fsi-openfoam:latest \
        bash -lc "./run.sh ${scr} on-caso-3 yes no" \
        > "brunaStuff/sweep_dz1_${tag}_Pc${pc}.log" 2>&1
    local rc=$?
    local cdir="cases/_mi/${scr}/ccx"
    for e in dat frd sta cvg; do cp -f "$cdir/on-caso-3.$e" "$cdir/on-caso-3_Pc${pc}.$e" 2>/dev/null; done
    cp -f "$cdir/log.ccx" "$cdir/log.ccx_Pc${pc}" 2>/dev/null
    echo "  rc=$rc  $(tail -1 "$cdir/on-caso-3_Pc${pc}.sta" 2>/dev/null || echo no_sta)"
}

echo "=== Caso 3F  Dz=-1.0 mm  -- build dos scratch radiais ==="; date
build_and_set radpia2dura3 rad:2:3
build_and_set radpia3dura4 rad:3:4
build_and_set radpia4dura5 rad:4:5

echo ""; echo "=== Sweep OFICIAL radpia2dura3 (5 pontos de P_contact) ==="; date
for pc in 0 4517 9034 13551 18068; do run_pc radpia2dura3 "$pc"; done

echo ""; echo "=== Independencia de malha em Pc9034 (radpia3dura4, radpia4dura5) ==="; date
run_pc radpia3dura4 9034
run_pc radpia4dura5 9034

echo ""; echo "=== TODOS OS RUNS CONCLUIDOS ==="; date
