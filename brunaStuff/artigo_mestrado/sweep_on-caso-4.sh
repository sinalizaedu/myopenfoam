#!/bin/bash
# sweep_on-caso-4.sh - orquestra o caso 4 (inchaco SANS dirige area+forca de contato).
#
# Duas fases:
#   phaseA : runs INCHACO-ONLY (P_CONTACT=0), varrendo P_CSF pelos estagios de
#            SANS. Produz os .frd usados para MEDIR a distensao da bainha.
#            Ao final chama measure_on-caso-4_swelling.py, que escreve a tabela
#            de estagios (brunaStuff/on-caso-4_stage_table.json) com, por estagio:
#            P_CSF, CONTACT_BOX (area) e P_CONTACT (forca) ancorados no inchaco.
#   phaseB : runs ACOPLADOS, lendo a tabela da Fase A: cada estagio roda com seu
#            P_CSF + box de contato ampliado + P_contact derivado da interferencia.
#            Produz os .frd usados por analyze_on-caso-4.py.
#   all    : phaseA, depois phaseB (default).
#
# Uso:
#   bash brunaStuff/sweep_on-caso-4.sh            # all
#   bash brunaStuff/sweep_on-caso-4.sh phaseA
#   bash brunaStuff/sweep_on-caso-4.sh phaseB
#
# Requer: imagem docker fsi-openfoam:latest e cases/_lib/libsolids4FoamModels.so.

set -e
cd "$(dirname "$0")/.."   # raiz do repo

PHASE="${1:-all}"
IMG=fsi-openfoam:latest
WINKLER_K=2000000          # SANS: gordura orbital 2 MPa/m
STAGE_JSON=brunaStuff/on-caso-4_stage_table.json

# Estagios de SANS: tag_faseA  tag_faseB  P_CSF[Pa]
declare -a STAGES=(
    "swell_S0 S0_baseline 1333"
    "swell_S1 S1_mild     2400"
    "swell_S2 S2_upper    3800"
    "swell_S3 S3_severe   5500"
)

run_ccx () {
    # $1=OUT_TAG  $2=P_CSF  $3=P_CONTACT  $4=CONTACT_BOX(optional)  $5=logfile
    local tag="$1" pcsf="$2" pc="$3" box="$4" log="$5"
    local boxenv=""
    if [ -n "$box" ]; then
        boxenv="CONTACT_BOX='${box}'"
    fi
    set +e
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -v "$(pwd)/cases:/simulation" \
        -v "$(pwd)/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/on-caso-4/ccx \
        "$IMG" \
        bash -lc "P_CSF=${pcsf} P_CONTACT=${pc} ${boxenv} WINKLER_K=${WINKLER_K} OUT_TAG=${tag} REMESH=1 ./Allrun" \
        > "$log" 2>&1
    local rc=$?
    set -e
    if [ $rc -ne 0 ]; then
        echo "   AVISO: tag=${tag} retornou rc=${rc} (veja ${log})"
    fi
    local sta="cases/on-caso-4/ccx/on-caso-4_${tag}.sta"
    if [ -f "$sta" ]; then
        echo "   [.sta tail] $(tail -1 "$sta")"
    fi
}

do_phaseA () {
    echo "=== on-caso-4 FASE A: inchaco-only (P_CONTACT=0), varrendo P_CSF ==="
    date
    for entry in "${STAGES[@]}"; do
        read -r atag btag pcsf <<< "$entry"
        echo ""
        echo "---- [$(date +%H:%M:%S)] FaseA ${atag}: P_CSF=${pcsf} Pa, P_CONTACT=0 ----"
        run_ccx "$atag" "$pcsf" "0" "" "brunaStuff/sweep_on-caso-4_${atag}.log"
    done
    echo ""
    echo "=== Fase A concluida. Medindo inchaco -> tabela de estagios ==="
    python3 brunaStuff/measure_on-caso-4_swelling.py
}

do_phaseB () {
    echo "=== on-caso-4 FASE B: runs acoplados (inchaco + contato ancorado) ==="
    if [ ! -f "$STAGE_JSON" ]; then
        echo "ERRO: ${STAGE_JSON} nao existe. Rode a Fase A primeiro:"
        echo "  bash brunaStuff/sweep_on-caso-4.sh phaseA"
        exit 1
    fi
    date
    # extrai (tag|P_CSF|P_CONTACT|CONTACT_BOX) da tabela JSON (compat. bash 3.2,
    # sem mapfile). Cada linha: tag|P_CSF|P_CONTACT|CONTACT_BOX
    python3 - "$STAGE_JSON" > /tmp/on-caso-4_rows.txt <<'PY'
import json, sys
meta = json.load(open(sys.argv[1]))
for s in meta["stages"]:
    print(f'{s["tag"]}|{s["P_CSF"]}|{s["P_CONTACT"]}|{s["CONTACT_BOX"]}')
PY
    while IFS='|' read -r tag pcsf pc box; do
        [ -z "$tag" ] && continue
        echo ""
        echo "---- [$(date +%H:%M:%S)] FaseB ${tag}: P_CSF=${pcsf} P_contact=${pc} ----"
        echo "      box=${box}"
        run_ccx "$tag" "$pcsf" "$pc" "$box" "brunaStuff/sweep_on-caso-4_${tag}.log"
    done < /tmp/on-caso-4_rows.txt
    echo ""
    echo "=== Fase B concluida. Analise:  python3 brunaStuff/analyze_on-caso-4.py ==="
}

case "$PHASE" in
    phaseA) do_phaseA ;;
    phaseB) do_phaseB ;;
    all)    do_phaseA; echo ""; do_phaseB ;;
    *) echo "fase desconhecida: $PHASE (use phaseA|phaseB|all)"; exit 2 ;;
esac

echo ""
echo "=== sweep_on-caso-4 (${PHASE}) concluido ==="
date
