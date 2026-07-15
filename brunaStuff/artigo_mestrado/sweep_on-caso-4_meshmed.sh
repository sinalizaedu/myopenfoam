#!/bin/bash
# sweep_on-caso-4_meshmed.sh - resultado FINAL do Caso 4 na MALHA INDEPENDENTE.
#
# O estudo de independencia (analyze_mesh_independence_on-caso-4.py) mostrou que a
# malha intermediaria "meshmed" (theta,z 2x; radial 1x; ~27.6k hex / ~30k nos) ja'
# da' a solucao convergida: refinar mais (2x uniforme) muda as metricas em <=2.3%.
# A malha base 1x subestimava a resposta local em 20-72%. Logo a producao definitiva
# do Caso 4 deve rodar nesta malha.
#
# Roda os 4 estagios de SANS (S0..S3) lendo a tabela de estagios da Fase A
# (P_CSF, P_CONTACT, CONTACT_BOX ja' calibrados), na malha meshmed, e regenera o
# resumo (on-caso-4_summary_meshmed.{png,txt}).
#
# Increment do Riks afrouxado p/ 0.05 (vs 0.02 de producao) com os *CONTROLS de
# cortes automaticos ja' presentes no .inp: como a meshmed cabe na RAM (sem OOM),
# qualquer incremento grande demais e' simplesmente cortado e re-tentado. O teste
# compara o equilibrio final em lambda=1 (unico), entao o passo nao afeta o result.
#
# Uso:  bash brunaStuff/sweep_on-caso-4_meshmed.sh

set -e
set -o pipefail
cd "$(dirname "$0")/.."   # raiz do repo

IMG=fsi-openfoam:latest
MESH_VARIANT="${MESH_VARIANT:-meshmed}"  # usa blockMeshDict.$MESH_VARIANT; saidas _$MESH_VARIANT
NPROC="${NPROC:-4}"        # 4 threads: equilibrio memoria (Docker 7.7GB) x velocidade
STAGE_FILTER="${STAGE_FILTER:-}"   # tags a rodar (vazio=todas). Ex.: "S1_mild S2_upper"
# Linha de incremento do Riks (vazio=producao 0.02). Na meshmed os estagios de carga
# alta invertem elemento no passo 0.02 (patch de contato refinado -> gradiente agudo);
# passos menores (ex. 0.01/0.005) atualizam a geometria gradualmente e evitam isso.
RIKS_INC="${RIKS_INC:-}"
WINKLER_K=2000000
SYS=cases/on-caso-4/solid/system
CCX=cases/on-caso-4/ccx
INP="$CCX/on-caso-4.inp"
STAGE_JSON=brunaStuff/on-caso-4_stage_table.json

[ -f "$SYS/blockMeshDict.$MESH_VARIANT" ] || { echo "ERRO: falta $SYS/blockMeshDict.$MESH_VARIANT"; exit 1; }
[ -f "$STAGE_JSON" ] || { echo "ERRO: falta $STAGE_JSON (rode a Fase A)"; exit 1; }

# ---- backups + restauracao garantida (mesmo se algo falhar) ----
cp "$SYS/blockMeshDict" "$SYS/blockMeshDict.prodbak"
cp "$INP" "$INP.meshmedbak"
restore () {
    echo ""
    echo "=== restaurando malha base e .inp de producao ==="
    cp "$SYS/blockMeshDict.mesh1" "$SYS/blockMeshDict" 2>/dev/null || \
        cp "$SYS/blockMeshDict.prodbak" "$SYS/blockMeshDict"
    [ -f "$INP.meshmedbak" ] && mv "$INP.meshmedbak" "$INP"
    rm -f "$SYS/blockMeshDict.prodbak"
}
trap restore EXIT

# ---- instala malha independente; mantem o incremento do Riks de PRODUCAO ----
# Incremento de PRODUCAO (0.02): os estagios S1/S2/S3 (carga alta) sofrem inversao
# de elemento se o passo do Riks for grande (testado: 0.05/0.1 -> runaway + OOM ja'
# no lambda~0.3-0.4). A meshmed mantem a resolucao RADIAL da base (so refina theta,z),
# entao converge no passo 0.02 como a malha base. ~56 incrementos por estagio.
cp "$SYS/blockMeshDict.$MESH_VARIANT" "$SYS/blockMeshDict"
if [ -n "$RIKS_INC" ]; then
    sed -i -E "s|^0\.005, 1\.0, 1e-9, 0\.02, 1\.0\$|${RIKS_INC}|" "$INP"
fi
echo "malha: blockMeshDict.$MESH_VARIANT | Riks: $(grep -A1 '^\*STATIC, RIKS' "$INP" | tail -1)"

run_ccx () {  # $1=OUT_TAG $2=P_CSF $3=P_CONTACT $4=BOX $5=log
    local tag="$1" pcsf="$2" pc="$3" box="$4" log="$5"
    set +e
    docker run --rm --platform=linux/amd64 -u ubuntu \
        -e OMP_NUM_THREADS="${NPROC}" -e NUMBER_OF_CPUS="${NPROC}" \
        -v "$(pwd)/cases:/simulation" \
        -v "$(pwd)/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
        -w /simulation/on-caso-4/ccx \
        "$IMG" \
        bash -lc "export OMP_NUM_THREADS=${NPROC} NUMBER_OF_CPUS=${NPROC}; P_CSF=${pcsf} P_CONTACT=${pc} CONTACT_BOX='${box}' WINKLER_K=${WINKLER_K} OUT_TAG=${tag} REMESH=1 ./Allrun" \
        > "$log" 2>&1
    local rc=$?
    set -e
    local sta="${CCX}/on-caso-4_${tag}.sta"
    echo "      rc=${rc}  $(tail -1 "$sta" 2>/dev/null || echo NOSTA)"
}

echo "=== on-caso-4 FINAL na malha ${MESH_VARIANT}: estagios SANS ==="
date

# le (tag|P_CSF|P_CONTACT|CONTACT_BOX) da tabela (bash 3.2, sem mapfile)
python3 - "$STAGE_JSON" > /tmp/on-caso-4_meshmed_rows.txt <<'PY'
import json, sys
meta = json.load(open(sys.argv[1]))
for s in meta["stages"]:
    print(f'{s["tag"]}|{s["P_CSF"]}|{s["P_CONTACT"]}|{s["CONTACT_BOX"]}')
PY

while IFS='|' read -r tag pcsf pc box; do
    [ -z "$tag" ] && continue
    if [ -n "$STAGE_FILTER" ] && ! echo " $STAGE_FILTER " | grep -q " $tag "; then
        echo "   [skip ${tag}: fora do STAGE_FILTER]"
        continue
    fi
    echo ""
    echo "---- [$(date +%H:%M:%S)] ${tag} (${MESH_VARIANT}): P_CSF=${pcsf} P_contact=${pc} ----"
    echo "      box=${box}"
    run_ccx "${tag}_${MESH_VARIANT}" "$pcsf" "$pc" "$box" "brunaStuff/sweep_on-caso-4_${tag}_${MESH_VARIANT}.log"
done < /tmp/on-caso-4_meshmed_rows.txt

echo ""
echo "=== runs concluidos. Analise (malha ${MESH_VARIANT}) ==="
ANALYZE_SUFFIX=_${MESH_VARIANT} python3 brunaStuff/analyze_on-caso-4.py
date
