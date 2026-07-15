#!/bin/bash
# brunaStuff/run_on_mestrado_guarded.sh
#
# Roda o on-mestrado dentro do container Docker, e ativa um "guardiao" em
# paralelo que vigia/mata qualquer pimpleFoam/solids4Foam pertencente a
# /simulation/artoph-fsi-curva-mestrado/ enquanto o on-mestrado estiver rodando.
#
# Motivacao:
#   Em rodadas anteriores, processos artoph-fsi-curva-mestrado apareceram do
#   nada (provavelmente outra sessao do agente) e bateram contra o
#   on-mestrado/solids4Foam, causando SIGKILL (exit 137) por pressao de
#   memoria/CPU no Docker VM.
#
# Uso (no host macOS):
#   chmod +x brunaStuff/run_on_mestrado_guarded.sh
#   ./brunaStuff/run_on_mestrado_guarded.sh
#
# Saidas:
#   - cases/on-mestrado/solid/log.solids4Foam (do solver)
#   - cases/on-mestrado/allrun_guarded.log (do Allrun)
#   - cases/on-mestrado/guard.log (do guardiao - lista de kills)

set -uo pipefail

CONTAINER=${CONTAINER:-myopenfoam-fsi-run-e725dcbcdf70}
CASE_DIR=/simulation/on-mestrado
GUARD_LOG_HOST=cases/on-mestrado/guard.log

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "ERRO: container ${CONTAINER} nao esta rodando."
    echo "Inicie com: docker compose run --rm fsi bash -l (em outro terminal)"
    exit 1
fi

echo "=== Limpando container de qualquer solver remanescente ==="
docker exec "$CONTAINER" bash -lc '
pkill -9 -f pimpleFoam 2>/dev/null || true
pkill -9 -f solids4Foam 2>/dev/null || true
pkill -9 -f Allrun-solve 2>/dev/null || true
sleep 2
ps -ef | grep -E "(pimpleFoam|solids4Foam|Allrun)" | grep -v grep || echo "CLEAN"
'

echo "=== Limpando on-mestrado (Allclean) ==="
docker exec "$CONTAINER" bash -lc "cd ${CASE_DIR} && ./Allclean"

echo "=== Iniciando guardiao em background ==="
> "$GUARD_LOG_HOST"
docker exec -d "$CONTAINER" bash -lc '
LOG=/simulation/on-mestrado/guard.log
{
    echo "[$(date -u +%H:%M:%S)] guardiao iniciado pid=$$"
    while [ -f /simulation/on-mestrado/.guard_active ]; do
        # mata qualquer pimpleFoam/solids4Foam cuja cwd esteja em artoph-fsi-curva-mestrado
        for pid in $(pgrep -f "pimpleFoam|solids4Foam"); do
            cwd=$(readlink /proc/$pid/cwd 2>/dev/null || true)
            case "$cwd" in
                *artoph-fsi-curva-mestrado*)
                    echo "[$(date -u +%H:%M:%S)] kill pid=$pid cwd=$cwd"
                    kill -KILL $pid 2>/dev/null
                ;;
            esac
        done
        # mata Allrun-solve.sh do artoph-fsi
        for pid in $(pgrep -f "Allrun-solve.sh"); do
            cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr "\0" " " || true)
            case "$cmdline" in
                *artoph-fsi-curva-mestrado*)
                    echo "[$(date -u +%H:%M:%S)] kill Allrun pid=$pid"
                    kill -KILL $pid 2>/dev/null
                ;;
            esac
        done
        sleep 2
    done
    echo "[$(date -u +%H:%M:%S)] guardiao desativado"
} >> "$LOG" 2>&1
'

# ativa o guardiao
docker exec "$CONTAINER" bash -lc "touch /simulation/on-mestrado/.guard_active"
sleep 1

echo "=== Rodando Allrun do on-mestrado ==="
echo "    Logs:"
echo "      cases/on-mestrado/solid/log.solids4Foam"
echo "      cases/on-mestrado/allrun_guarded.log"
echo "      cases/on-mestrado/guard.log"
echo ""

set +e
docker exec "$CONTAINER" bash -lc "cd ${CASE_DIR} && ./Allrun > allrun_guarded.log 2>&1; echo EXIT_CODE=\$? >> allrun_guarded.log"
ALLRUN_RC=$?
set -e

echo "=== Allrun terminou (rc=${ALLRUN_RC}) - desativando guardiao ==="
docker exec "$CONTAINER" bash -lc "rm -f /simulation/on-mestrado/.guard_active"
sleep 3

echo ""
echo "=== Resumo ==="
docker exec "$CONTAINER" bash -lc "
cd ${CASE_DIR}
echo '--- ultimas linhas do allrun_guarded.log ---'
tail -10 allrun_guarded.log
echo ''
echo '--- timesteps escritos ---'
ls -d solid/[0-9]* 2>/dev/null | sort -V | tail -10
echo ''
echo '--- guard.log ---'
cat solid/../guard.log 2>/dev/null || cat guard.log 2>/dev/null || true
"

exit ${ALLRUN_RC}
