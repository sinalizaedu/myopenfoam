#!/bin/bash
# run_caso3sf_meshindep.sh
# ========================
# Estudo de independencia de malha do on-caso-3-sf (caso 3F: SO carga lateral
# da arteria oftalmica, sem Dz/EOM). Roda blockMesh -> topoSet/createPatch
# (perturbation + contact_local) -> conversor polyMesh->.inp -> CalculiX/Riks
# para cada nivel de refino montado por build_meshindep.sh:
#
#   GLOBAL : f050 (819), f150 (16587)   [f100=4752 e' a producao em cases/on-caso-3-sf]
#   RADIAL : radpia2dura3 (~5328), radpia3dura4 (~5904)
#
# A malha e' geometricamente IDENTICA a' do on-caso-3; aqui muda so' o
# carregamento (.inp do 3F). Reusa run.sh (mesma pipeline dos demais estudos).
#
# COMO RODAR (no HOST, raiz do repo):
#   docker compose run --rm fsi bash -lc 'cd /simulation/_mi && ./run_caso3sf_meshindep.sh'
# Opcional, so' alguns niveis:
#   docker compose run --rm fsi bash -lc 'cd /simulation/_mi && ./run_caso3sf_meshindep.sh f050 f150'
#
# DEPOIS (no HOST):
#   python3 brunaStuff/analyze_on-caso-3-sf_meshindep.py
set -o pipefail

LEVELS="${*:-f050 f150 radpia2dura3 radpia3dura4}"
HERE="$(cd "$(dirname "$0")" && pwd)"

for tag in $LEVELS; do
    SCRATCH="on-caso-3-sf__$tag"
    if [ ! -d "$HERE/$SCRATCH" ]; then
        echo "!! $SCRATCH nao existe (rode build_meshindep.sh no host). Pulando."
        continue
    fi
    echo "################################################################"
    echo "## $SCRATCH"
    echo "################################################################"
    bash "$HERE/run.sh" "$SCRATCH" on-caso-3-sf yes no
done

echo ""
echo "Pronto. No HOST: python3 brunaStuff/analyze_on-caso-3-sf_meshindep.py"
