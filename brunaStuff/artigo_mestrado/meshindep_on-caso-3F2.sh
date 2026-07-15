#!/bin/bash
# meshindep_on-caso-3F2.sh
# Estudo de independencia de malha do on-caso-3F2 (3F com 2 contatos arteriais
# antissimetricos -> modo S). Constroi scratch isolados em cases/_mi/ a partir
# do caso cases/on-caso-3F2 (mesmo deck, 2 contatos, Dz=-1.0mm), trocando apenas
# o blockMeshDict, e roda cada um no container fsi-openfoam.
#
# Niveis:
#   radpia2dura3 : BASELINE (ja' rodado em cases/on-caso-3F2) -- nao re-roda aqui
#   radpia3dura4 : refino RADIAL das laminas (pia 3, dura 4)
#   radpia4dura5 : refino RADIAL das laminas (pia 4, dura 5)
#   tangax       : refino TANGENCIAL+AXIAL (fr=1 ft=2 fz=2) -> adensa o PATCH de
#                  contato (governa a forma dos lobos do S), que o refino radial
#                  nao toca.
#
# A malha base e' cases/on-caso-3/solid/system/blockMeshDict (pia n1=1, dura n1=2,
# 6 tang/quadrante, 10 axiais). radpia2dura3 = refino rad:2:3 dela.
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"
BASE_DICT="$REPO/cases/on-caso-3/solid/system/blockMeshDict"
SRC="$REPO/cases/on-caso-3F2"

build_scratch() {
    local tag=$1; shift
    local DST="$REPO/cases/_mi/on-caso-3F2__${tag}"
    rm -rf "$DST"
    mkdir -p "$DST/solid/system" "$DST/solid/constant" "$DST/ccx"
    # dicts do solid (perturbation + 2 contatos + numericos), SEM blockMeshDict
    for f in controlDict fvSchemes fvSolution \
             topoSetDict_perturbation createPatchDict_perturbation \
             topoSetDict_contact createPatchDict_contact \
             topoSetDict_contact2 createPatchDict_contact2; do
        cp "$SRC/solid/system/$f" "$DST/solid/system/"
    done
    # constant menos polyMesh
    for f in "$SRC"/solid/constant/*; do
        bn=$(basename "$f"); [ "$bn" = "polyMesh" ] && continue
        cp -R "$f" "$DST/solid/constant/" 2>/dev/null || true
    done
    # ccx: deck + conversor + Allrun
    cp "$SRC/ccx/on-caso-3F2.inp" "$SRC/ccx/foam_polymesh_to_ccx_inp.py" "$SRC/ccx/Allrun" "$DST/ccx/"
    chmod +x "$DST/ccx/Allrun"
    # blockMeshDict refinado a partir da BASE
    case "$1" in
        rad)  python3 "$REPO/brunaStuff/refine_blockmesh_radial.py" \
                  --in "$BASE_DICT" --out "$DST/solid/system/blockMeshDict" --pia "$2" --dura "$3" ;;
        dir)  python3 "$REPO/brunaStuff/refine_blockmesh.py" \
                  "$BASE_DICT" "$DST/solid/system/blockMeshDict" "$2" "$3" "$4" ;;
    esac
    echo "  scratch pronto: $DST"
}

run_scratch() {
    local tag=$1
    local SCR="on-caso-3F2__${tag}"
    echo "==== [$(date +%H:%M:%S)] RUN ${tag} ===="
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$REPO/cases:/simulation" \
        -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w "/simulation/_mi/${SCR}/ccx" \
        fsi-openfoam:latest \
        bash -lc "WINKLER_K=200000 ./Allrun" \
        > "brunaStuff/meshindep_on-caso-3F2_${tag}.log" 2>&1
    local rc=$?
    local sta="cases/_mi/${SCR}/ccx/on-caso-3F2.sta"
    echo "  rc=$rc  $(tail -1 "$sta" 2>/dev/null || echo no_sta)"
}

echo "=== on-caso-3F2 mesh independence ==="; date
echo "--- build ---"
build_scratch radpia3dura4 rad 3 4
build_scratch radpia4dura5 rad 4 5
build_scratch tangax       dir 1 2 2

echo "--- run (sequencial) ---"
run_scratch radpia3dura4
run_scratch radpia4dura5
run_scratch tangax

echo "=== CONCLUIDO ==="; date
