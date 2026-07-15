#!/bin/bash
# run_on-caso-3_meshindep_normF.sh
# ================================
# Estudo de independencia de malha GLOBAL do on-caso-3 com a carga arterial
# NORMALIZADA POR FORCA: o P_contact entra como *DSLOAD ... P (pressao) sobre
# CONTACT_LOCAL_SURF, mas a area A do patch focal muda com o refino. Para
# comparar a MESMA forca arterial F = P*A entre malhas, fixamos a forca-alvo
#
#     F_alvo = p_nominal * A_f100   (referencia = malha de producao)
#
# e, em cada malha, injetamos  P = F_alvo / A_malha.
#
# Carga SANS de producao: p_nominal = 9034 Pa, Dz = -1.5 mm, Winkler 200 kPa/m.
#
# NB: a malha grosseira f050 captura 0 faces no box do contact_local (o patch
#     focal e' mais fino que a celula) -> A=0 -> forca arterial = 0; portanto
#     f050 NAO consegue representar o contato arterial e e' EXCLUIDA do estudo
#     normalizado (a convergencia do contato e' aferida f100 vs f150).
#
# Reusa as scratches existentes em cases/_mi/on-caso-3__<lvl> (polyMesh +
# *_mesh.inp + *_winkler.inp ja' gerados); apenas sincroniza o deck de fisica
# com a producao (INC=500) e seta o P normalizado, depois roda ccx no container.
#
# Uso (HOST, raiz do repo):
#   bash brunaStuff/run_on-caso-3_meshindep_normF.sh [f150 ...]
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"

P_NOMINAL=9034
A_F100=$(python3 brunaStuff/contact_area.py cases/on-caso-3/solid/constant/polyMesh 2>/dev/null)
F_TARGET=$(python3 -c "print(${P_NOMINAL}*${A_F100})")
echo "=== on-caso-3 mesh-indep (forca arterial normalizada) ==="
echo "    A_f100 = ${A_F100} m^2 ; p_nominal = ${P_NOMINAL} Pa"
echo "    F_alvo = ${F_TARGET} N  (= p_nominal * A_f100)"

LEVELS="${*:-f150}"
for lvl in $LEVELS; do
    D="cases/_mi/on-caso-3__${lvl}"
    PM="$D/solid/constant/polyMesh"
    DECK="$D/ccx/on-caso-3.inp"
    if [ ! -f "$PM/points" ] || [ ! -f "$D/ccx/on-caso-3_mesh.inp" ]; then
        echo "!! $lvl: polyMesh/mesh.inp ausente -- rode build_meshindep.sh antes. Pulando."
        continue
    fi
    A=$(python3 brunaStuff/contact_area.py "$PM" 2>/dev/null)
    NF=$(python3 -c "from brunaStuff.contact_area import area_of_patch; from pathlib import Path; print(area_of_patch(Path('$PM'))[1])" 2>/dev/null)
    if python3 -c "import sys; sys.exit(0 if float('$A')>0 else 1)"; then
        P=$(python3 -c "print(int(round(${F_TARGET}/${A})))")
    else
        echo "!! $lvl: A=0 (0 faces no contact_local) -- malha nao resolve o patch focal. Pulando."
        continue
    fi
    echo ""
    echo "================================================================"
    echo " [$lvl] A=${A} m^2 (nFaces=${NF})  ->  P = F_alvo/A = ${P} Pa"
    echo "================================================================"
    # sincroniza deck de fisica com producao: INC=500 e P normalizado
    sed -i.bak -E "s|^(\*STEP, NLGEOM=YES, INC=)[0-9]+|\1500|" "$DECK"
    sed -i.bak -E "s|^CONTACT_LOCAL_SURF, P, .*$|CONTACT_LOCAL_SURF, P, ${P}|" "$DECK"
    grep -n "INC=\|CONTACT_LOCAL_SURF, P," "$DECK" | head
    # roda ccx no container (mesh.inp/winkler.inp ja' existem na scratch)
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$REPO/cases:/simulation" \
        -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w "/simulation/_mi/on-caso-3__${lvl}/ccx" \
        fsi-openfoam:latest \
        bash -lc "ccx_preCICE -i on-caso-3" \
        > "brunaStuff/meshindep_on-caso-3_${lvl}_normF.log" 2>&1
    rc=$?
    echo " [$lvl] ccx rc=${rc}"
    tail -2 "$D/ccx/on-caso-3.sta" 2>/dev/null || echo " (sem .sta)"
done
echo ""
echo "=== concluido ==="
