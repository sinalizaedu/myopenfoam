#!/bin/bash
# brunaStuff/run_on_mestrado_resume_loop.sh
#
# Roda o on-mestrado em modo resume-loop:
#   1. solids4Foam roda ate ser killed (~ 460-540 s no Rosetta-2)
#   2. controlDict ja esta com startFrom latestTime, entao reiniciar
#      apenas continua do ultimo timestep escrito.
#   3. Loop ate atingir endTime (2.5 s) ou ate o numero maximo de tentativas.
#
# Tambem mantem o guardiao anti-artoph-fsi rodando.
#
# Uso:
#   ./brunaStuff/run_on_mestrado_resume_loop.sh

set -uo pipefail

CONTAINER=${CONTAINER:-myopenfoam-fsi-run-e725dcbcdf70}
CASE_DIR=/simulation/on-mestrado
END_TIME="2.5"
MAX_ATTEMPTS=20

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "ERRO: container ${CONTAINER} nao esta rodando."
    exit 1
fi

echo "=== Pre-flight: matando solvers existentes (artoph e on-mestrado) ==="
docker exec "$CONTAINER" bash -lc '
pkill -9 -f pimpleFoam 2>/dev/null || true
pkill -9 -f solids4Foam 2>/dev/null || true
pkill -9 -f Allrun-solve 2>/dev/null || true
sleep 2
'

# Inicia guardiao se nao estiver rodando
echo "=== Iniciando guardiao anti-artoph (se necessario) ==="
docker exec "$CONTAINER" bash -lc "
touch /simulation/on-mestrado/.guard_active
if ! pgrep -f 'guardiao_v3' >/dev/null 2>&1; then
    nohup bash -c '
exec -a guardiao_v3 bash <<\"GUARD\"
LOG=/simulation/on-mestrado/guard.log
echo \"[\$(date -u +%H:%M:%S)] guardiao v3 iniciado pid=\$\$\" >> \$LOG
while [ -f /simulation/on-mestrado/.guard_active ]; do
    for pid in \$(pgrep -f \"pimpleFoam|solids4Foam\" 2>/dev/null); do
        cwd=\$(readlink /proc/\$pid/cwd 2>/dev/null || true)
        case \"\$cwd\" in
            *artoph-fsi-curva-mestrado*)
                echo \"[\$(date -u +%H:%M:%S)] kill pid=\$pid cwd=\$cwd\" >> \$LOG
                kill -KILL \$pid 2>/dev/null
            ;;
        esac
    done
    sleep 2
done
echo \"[\$(date -u +%H:%M:%S)] guardiao desativado\" >> \$LOG
GUARD
' > /tmp/guard_nohup.log 2>&1 &
    disown
    echo 'Guardiao v3 iniciado'
else
    echo 'Guardiao ja rodando'
fi
"

# Verifica se ja existe a malha; se nao, faz blockMesh+topoSet+createPatch primeiro
docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
if [ ! -f constant/polyMesh/points ] || ! ls -d [0-9.]* | grep -q '^0\\.05\\$\\|^0\\.05/\\$'; then
    echo '=== Malha ausente ou caso nao iniciado: rodando setup completo ==='
    cd ${CASE_DIR}
    ./Allclean
    cd ${CASE_DIR}/solid
    blockMesh > log.blockMesh 2>&1
    topoSet -dict system/topoSetDict_contact > log.topoSet 2>&1
    createPatch -overwrite -dict system/createPatchDict_contact > log.createPatch 2>&1
    echo 'Setup OK'
else
    echo '=== Malha e timesteps iniciais existem - resumindo direto ==='
fi
"

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

    # Compara com endTime usando bc/awk (Mac compativel)
    REACHED=$(awk -v a="${LATEST:-0}" -v b="${END_TIME}" 'BEGIN{print (a+0 >= b+0)?1:0}')
    if [ "$REACHED" = "1" ]; then
        echo "OK: simulacao ja atingiu o endTime (${LATEST} >= ${END_TIME})"
        break
    fi

    # Roda solids4Foam direto (sem wrapper Allrun, ja temos a malha)
    echo "    Rodando solids4Foam (resume from ${LATEST:-0})..."
    set +e
    docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
nohup solids4Foam >> log.solids4Foam 2>&1
echo \"solids4Foam exited with code \$?\"
"
    RC=$?
    set -e
    echo "    docker exec rc=${RC}"

    # Pega o latestTime apos o run
    NEW_LATEST=$(docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | sort -V | tail -1
" | tr -d '[:space:]')
    echo "    novo latestTime: ${NEW_LATEST}"

    # Se nao avancou nada, pode estar travado em t=0.6 - aborta
    if [ "$NEW_LATEST" = "${LATEST:-0}" ] && [ "$attempt" -gt 1 ]; then
        echo "AVISO: nenhum progresso desde ultima tentativa (${LATEST}). Esperando 5s e tentando de novo..."
        sleep 5
    fi
done

# Desativa guardiao
docker exec "$CONTAINER" bash -lc "rm -f /simulation/on-mestrado/.guard_active" 2>/dev/null || true

echo ""
echo "=== Resumo final ==="
docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}/solid
echo 'Timesteps escritos:'
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | sort -V | head -60
echo ''
echo 'Total de timesteps:'
ls -d [0-9.]* 2>/dev/null | grep -E '^[0-9.]+\$' | wc -l
echo ''
echo 'Ultimas linhas do log:'
tail -5 log.solids4Foam
"
