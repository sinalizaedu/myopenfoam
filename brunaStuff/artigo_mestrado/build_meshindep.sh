#!/bin/bash
# build_meshindep.sh CASE DECK FACTOR TAG CONTACT WARP
# Monta um diretorio scratch isolado em cases/_mi/<CASE>__<TAG> com o
# blockMeshDict escalado por FACTOR, pronto para rodar blockMesh->ccx no
# container. NAO toca nos casos de producao.
#
#   CASE    : nome do caso de producao (ex.: on-caso-2)
#   DECK    : nome do deck .inp dentro de ccx (ex.: on-caso-2, on-caso-2.2)
#   FACTOR  : refino do blockMeshDict. Duas formas:
#               <inteiro>      -> refino GLOBAL uniforme (refine_blockmesh.py)
#                                 ex.: 2  (fator 2 em r,theta,z -> 8x celulas)
#               rad:<P>:<D>    -> refino RADIAL DIRIGIDO das laminas
#                                 (refine_blockmesh_radial.py): P celulas
#                                 radiais na pia, D na dura, resto intacto.
#                                 ex.: rad:2:3  (pia 1->2, dura 2->3)
#   TAG     : sufixo do scratch (ex.: f200, radpia2dura3)
#   CONTACT : "yes" se o caso usa patch contact_local (on-caso-3)
#   WARP    : "yes" se aplica sweep em J (on-caso-2.2)
set -e
CASE=$1; DECK=$2; FACTOR=$3; TAG=$4; CONTACT=${5:-no}; WARP=${6:-no}

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/cases/$CASE"
DST="$REPO/cases/_mi/${CASE}__${TAG}"

rm -rf "$DST"
mkdir -p "$DST/solid/system" "$DST/solid/constant" "$DST/ccx"

# --- solid/system: dicts necessarios p/ blockMesh+topoSet+createPatch ---
for f in controlDict fvSchemes fvSolution \
         topoSetDict_perturbation createPatchDict_perturbation; do
    cp "$SRC/solid/system/$f" "$DST/solid/system/" 2>/dev/null || true
done
if [ "$CONTACT" = "yes" ]; then
    cp "$SRC/solid/system/topoSetDict_contact"    "$DST/solid/system/"
    cp "$SRC/solid/system/createPatchDict_contact" "$DST/solid/system/"
fi

# --- solid/constant: tudo menos polyMesh (sera gerado pelo blockMesh) ---
for f in "$SRC"/solid/constant/*; do
    bn=$(basename "$f")
    [ "$bn" = "polyMesh" ] && continue
    cp -R "$f" "$DST/solid/constant/" 2>/dev/null || true
done

# --- blockMeshDict escalado (global uniforme OU radial dirigido) ---
SRC_DICT="$SRC/solid/system/blockMeshDict"
DST_DICT="$DST/solid/system/blockMeshDict"
case "$FACTOR" in
    rad:*:*)
        PIA_R=$(echo "$FACTOR" | cut -d: -f2)
        DURA_R=$(echo "$FACTOR" | cut -d: -f3)
        python3 "$REPO/brunaStuff/refine_blockmesh_radial.py" \
            --in "$SRC_DICT" --out "$DST_DICT" --pia "$PIA_R" --dura "$DURA_R"
        ;;
    *)
        python3 "$REPO/brunaStuff/refine_blockmesh.py" \
            "$SRC_DICT" "$DST_DICT" "$FACTOR"
        ;;
esac

# --- ccx: deck + conversor (+ warp se necessario) ---
# Usa SEMPRE o conversor superset (on-caso-3), que gera DURA_INNER_SURF
# (interface dura<->sas, necessaria p/ o *DSLOAD da PIC) alem das surfaces
# por patch. O conversor antigo de on-caso-2 nao gera DURA_INNER_SURF.
cp "$SRC/ccx/$DECK.inp" "$DST/ccx/"
cp "$REPO/cases/on-caso-3/ccx/foam_polymesh_to_ccx_inp.py" "$DST/ccx/"
if [ "$WARP" = "yes" ]; then
    cp "$SRC/ccx/warp_centerline_sweep.py" "$DST/ccx/"
fi

echo "build_meshindep: $DST pronto (factor=$FACTOR contact=$CONTACT warp=$WARP)"
