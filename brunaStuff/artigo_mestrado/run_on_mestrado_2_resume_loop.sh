#!/bin/bash
# brunaStuff/run_on_mestrado_2_resume_loop.sh
#
# Roda o on-mestrado-2 em modo resume-loop:
#   1. solids4Foam roda ate ser killed (~ 460-540 s no Rosetta-2 do macOS)
#   2. controlDict ja esta com startFrom latestTime, entao reiniciar
#      apenas continua do ultimo timestep escrito.
#   3. Loop ate atingir endTime (2.5 s) ou ate o numero maximo de tentativas.
#
# Diferenca para o on-mestrado original:
#   - usa um container persistente (criado com `docker compose run -d` se nao
#     houver) -> docker exec eh muito mais barato que docker compose run --rm
#   - case dir = /simulation/on-mestrado-2
#
# Uso:
#   ./brunaStuff/run_on_mestrado_2_resume_loop.sh

set -uo pipefail

CASE_DIR=/simulation/on-mestrado-2
END_TIME="2.5"
MAX_ATTEMPTS=30
CONTAINER_NAME="om2-resume"

# ---- garante container persistente ---------------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "=== Iniciando container persistente ${CONTAINER_NAME} ==="
    # Mata se existir mas estiver parado
    docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
    # docker compose run -d cria um container detached que fica vivo via tail -f /dev/null
    docker compose run -d --rm --name "${CONTAINER_NAME}" fsi bash -c 'tail -f /dev/null'
    sleep 2
fi

CONTAINER=${CONTAINER_NAME}
echo "Container ativo: ${CONTAINER}"

# ---- pre-flight: mata solvers orfaos -------------------------------------
echo "=== Pre-flight: matando solvers existentes ==="
docker exec "$CONTAINER" bash -lc '
pkill -9 -f solids4Foam 2>/dev/null || true
pkill -9 -f pimpleFoam 2>/dev/null || true
sleep 1
'

# ---- garante setup (blockMesh + topoSet + createPatch) -------------------
docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
if [ ! -f constant/polyMesh/points ]; then
    echo '=== Setup: blockMesh + topoSet + createPatch ==='
    blockMesh > log.blockMesh 2>&1
    topoSet -dict system/topoSetDict_contact > log.topoSet 2>&1
    createPatch -overwrite -dict system/createPatchDict_contact > log.createPatch 2>&1
    echo 'Setup OK'
else
    echo '=== Malha ja existe - resumindo direto ==='
fi
"

# ---- loop principal -------------------------------------------------------
attempt=0
while true; do
    attempt=$((attempt+1))
    if [ "$attempt" -gt "$MAX_ATTEMPTS" ]; then
        echo "ERRO: numero maximo de tentativas (${MAX_ATTEMPTS}) atingido."
        break
    fi

    # Verifica latest time
    LATEST=$(docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | sort -V | tail -1
" | tr -d '[:space:]')

    echo ""
    echo "=== Tentativa ${attempt}: latestTime = ${LATEST:-0} (alvo: ${END_TIME}) ==="

    REACHED=$(awk -v a="${LATEST:-0}" -v b="${END_TIME}" 'BEGIN{print (a+0 >= b+0)?1:0}')
    if [ "$REACHED" = "1" ]; then
        echo "OK: simulacao atingiu o endTime (${LATEST} >= ${END_TIME})"
        break
    fi

    echo "    Rodando solids4Foam (resume from ${LATEST:-0})..."
    set +e
    docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
nohup solids4Foam >> log.solids4Foam 2>&1
echo 'solids4Foam exit code:' \$?
"
    RC=$?
    set -e
    echo "    docker exec rc=${RC}"

    NEW_LATEST=$(docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | sort -V | tail -1
" | tr -d '[:space:]')
    echo "    novo latestTime: ${NEW_LATEST}"

    if [ "$NEW_LATEST" = "${LATEST:-0}" ]; then
        if [ "$attempt" -gt 2 ]; then
            echo "ERRO: 2+ tentativas seguidas sem progresso (preso em ${LATEST}). Abortando."
            break
        fi
        echo "AVISO: sem progresso. Esperando 5s..."
        sleep 5
    fi
done

# ---- resumo final ---------------------------------------------------------
echo ""
echo "=== Resumo final on-mestrado-2 ==="
docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
echo 'Timesteps escritos:'
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | sort -V
echo ''
echo 'Total de timesteps:'
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | wc -l
echo ''
echo 'Ultimas linhas do log:'
tail -8 log.solids4Foam
"
