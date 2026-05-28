#!/bin/bash
# brunaStuff/Allbuild_teste_geom.sh
#
# Builda os 3 casos de teste de trajetoria (cases/teste-geom-1, -2, -3)
# usando cada uma das 3 estrategias de extracao de centerline, e gera o PNG
# comparativo de cada um em brunaStuff/inspect_teste-geom-{1,2,3}.png.
#
# NAO roda nenhuma simulacao -- so geometria + PNG previa.
#
# Para inspecionar no ParaView depois:
#   ParaView -> File > Open > cases/teste-geom-1/teste-geom-1.foam
#   (e tambem solid/solid.foam, fluid/fluid.foam por regiao)
#
# Variaveis de ambiente opcionais:
#   PYTHON               -- python a usar (default: python3)
#   SKIP_VOXEL_SKELETON  -- se setado, pula estrategia 1 (que precisa skimage)
#   PIP_INSTALL          -- se setado como "yes", roda pip install scikit-image scipy

set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Usa venv local em brunaStuff/.venv por padrao (instalada com pip)
VENV_PY="$REPO/brunaStuff/.venv/bin/python"
if [ -n "${PYTHON:-}" ]; then
    PYTHON="${PYTHON}"
elif [ -x "$VENV_PY" ]; then
    PYTHON="$VENV_PY"
else
    PYTHON=python3
fi
echo "[python] $PYTHON"

# Cria venv automaticamente se faltar trimesh/skimage/scipy
if ! "$PYTHON" -c "import trimesh, scipy, skimage, matplotlib" 2>/dev/null; then
    echo "AVISO: trimesh/scipy/scikit-image/matplotlib faltando no $PYTHON"
    if [ "${CREATE_VENV:-yes}" = "yes" ] && [ ! -x "$VENV_PY" ]; then
        echo "Criando venv local em brunaStuff/.venv ..."
        python3 -m venv "$REPO/brunaStuff/.venv"
        "$VENV_PY" -m pip install --quiet --upgrade pip
        "$VENV_PY" -m pip install --quiet trimesh numpy scipy scikit-image matplotlib networkx shapely rtree
        PYTHON="$VENV_PY"
        echo "[python] $PYTHON"
    elif [ "${PIP_INSTALL:-}" = "yes" ]; then
        "$PYTHON" -m pip install --quiet --break-system-packages trimesh scipy scikit-image matplotlib networkx
    else
        echo "  Para criar venv automaticamente: re-rode (default ativo)."
        echo "  Ou: SKIP_VOXEL_SKELETON=1 para pular estrategia 1 e tentar so 2 e 3."
        if [ -z "${SKIP_VOXEL_SKELETON:-}" ]; then
            export SKIP_VOXEL_SKELETON=1
        fi
    fi
fi

declare -a STRATEGIES=(voxel_skeleton z_slicing tangent_marching)
declare -a NAMES=(teste-geom-1 teste-geom-2 teste-geom-3)

for i in 0 1 2; do
    strat="${STRATEGIES[$i]}"
    name="${NAMES[$i]}"
    out="cases/${name}"

    if [ "$strat" = "voxel_skeleton" ] && [ -n "${SKIP_VOXEL_SKELETON:-}" ]; then
        echo ""
        echo "====================================================================="
        echo "PULANDO ${name} (estrategia ${strat}): scikit-image nao disponivel"
        echo "====================================================================="
        continue
    fi

    echo ""
    echo "====================================================================="
    echo "BUILD ${name}  --  strategy=${strat}"
    echo "====================================================================="
    "$PYTHON" "brunaStuff/build_teste_geom.py" \
        --strategy "$strat" --out "$out"
    if [ $? -ne 0 ]; then
        echo "ERRO ao buildar ${name}"
        continue
    fi

    echo ""
    echo "  --> gerando PNG comparativo..."
    "$PYTHON" "brunaStuff/inspect_teste_geom.py" --case "$out"
done

echo ""
echo "====================================================================="
echo "PRONTO"
echo "====================================================================="
echo "PNGs comparativos:"
ls -la brunaStuff/inspect_teste-geom-*.png 2>/dev/null || true
echo ""
echo "Casos OpenFOAM (abrir cada *.foam no ParaView):"
for n in "${NAMES[@]}"; do
    if [ -d "cases/$n" ]; then
        echo "  cases/$n/${n}.foam"
    fi
done
