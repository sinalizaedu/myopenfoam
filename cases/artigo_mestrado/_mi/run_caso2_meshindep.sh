#!/bin/bash
# run_caso2_meshindep.sh
# ======================
# Roda blockMesh -> conversor -> CalculiX para os niveis NOVOS do estudo de
# independencia de malha do on-caso-2 (local stress + buckling mode):
#   f200          : refino GLOBAL uniforme (fator 2 -> ~38016 hexes)
#   radpia2dura3  : refino RADIAL dirigido das laminas (pia 1->2, dura 2->3)
#   radpia3dura4  : refino RADIAL dirigido das laminas (pia 1->3, dura 2->4)
#
# Os diretorios scratch ja' foram montados no HOST por:
#   bash brunaStuff/build_meshindep.sh on-caso-2 on-caso-2 2     f200         no no
#   bash brunaStuff/build_meshindep.sh on-caso-2 on-caso-2 rad:2:3 radpia2dura3 no no
#   bash brunaStuff/build_meshindep.sh on-caso-2 on-caso-2 rad:3:4 radpia3dura4 no no
#
# COMO RODAR (no HOST, a partir da raiz do repositorio):
#   docker compose run --rm fsi bash -lc 'cd /simulation/_mi && ./run_caso2_meshindep.sh'
# (./cases e' montado em /simulation; este script vive em cases/_mi/.)
#
# Opcional: rodar so' alguns niveis ->
#   docker compose run --rm fsi bash -lc 'cd /simulation/_mi && ./run_caso2_meshindep.sh f200'
#
# DEPOIS (no HOST) recomputar a convergencia (le os .frd novos automaticamente):
#   python3 brunaStuff/analyze_mesh_independence.py
#
# AVISO: os runs finos (f200 e radial) sao pesados (NLGEOM + Riks). O nivel fino
# pode divergir cedo (ARCMAX=1.0); nesse caso a SECANTE pre-flambagem ainda e'
# valida, e a leitura de CARGA PLENA fica disponivel apenas para quem atingir
# lambda~1.0.
set -e
set -o pipefail

LEVELS="${*:-f200 radpia2dura3 radpia3dura4}"
HERE="$(cd "$(dirname "$0")" && pwd)"

for tag in $LEVELS; do
    D="$HERE/on-caso-2__$tag"
    if [ ! -d "$D" ]; then
        echo "!! $D nao existe (rode build_meshindep.sh no host primeiro). Pulando."
        continue
    fi
    echo "================================================================"
    echo "== on-caso-2__$tag : blockMesh"
    echo "================================================================"
    ( cd "$D/solid" && blockMesh | tee log.blockMesh )

    echo "== on-caso-2__$tag : polyMesh -> CalculiX .inp"
    ( cd "$D/ccx" && python3 foam_polymesh_to_ccx_inp.py \
        --polymesh ../solid/constant/polyMesh \
        --out-mesh on-caso-2_mesh.inp \
        --out-winkler on-caso-2_winkler.inp \
        --winkler-k 200000 | tee log.convert )

    echo "== on-caso-2__$tag : ccx_preCICE -i on-caso-2"
    ( cd "$D/ccx" && ccx_preCICE -i on-caso-2 2>&1 | tee log.ccx )

    echo "== on-caso-2__$tag : concluido (on-caso-2.frd / .dat gerados)"
done

echo ""
echo "Pronto. No HOST, recompute a convergencia:"
echo "  python3 brunaStuff/analyze_mesh_independence.py"
