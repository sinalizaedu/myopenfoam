#!/bin/bash
# Run baseline + experiment for one MESH_LEVEL until experiment reaches t=30.
# Usage: ./scripts/run_until_converged.sh M5 [M4 ...]
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="$(cd ../.. && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm fsi bash -lc)

experiment_ok() {
    local log="$1"
    grep -qE '^Time = 30\s*$' "$log" 2>/dev/null \
        && ! grep -q 'FOAM FATAL' "$log" 2>/dev/null \
        && ! grep -qiE '\bnan\b' "$log" 2>/dev/null
}

baseline_ok() {
    local log="$1"
    grep -q 'SIMPLE solution converged' "$log" 2>/dev/null \
        && ! grep -q 'FOAM FATAL' "$log" 2>/dev/null
}

run_baseline() {
    local level="$1"
    local log="mesh_independence/${level}_baseline.log"
    local n=0
    until baseline_ok "$log"; do
        n=$((n + 1))
        echo "===== ${level} baseline attempt ${n} ====="
        rm -f "$log"
        "${COMPOSE[@]}" "cd /simulation/doc-g2-sim4 && ./Allclean && MESH_LEVEL=${level} MODE=baseline ./Allrun" \
            2>&1 | tee "$log"
        baseline_ok "$log" && break
        echo "WARN: ${level} baseline not converged — retrying"
        sleep 2
    done
    echo "OK: ${level} baseline converged"
}

run_experiment() {
    local level="$1"
    local log="mesh_independence/${level}_experiment.log"
    local attempts=(
        'DELTA_T=0.05 ADJUST_TIME_STEP=no'
        'DELTA_T=0.05 ADJUST_TIME_STEP=yes MAX_CO=1.0 MAX_DELTA_T=0.05'
        'DELTA_T=0.02 ADJUST_TIME_STEP=yes MAX_CO=0.8 MAX_DELTA_T=0.02'
        'DELTA_T=0.01 ADJUST_TIME_STEP=yes MAX_CO=0.5 MAX_DELTA_T=0.01'
        'DELTA_T=0.005 ADJUST_TIME_STEP=no'
        'DELTA_T=0.001 ADJUST_TIME_STEP=no'
    )
    local i=0
    for env in "${attempts[@]}"; do
        i=$((i + 1))
        echo "===== ${level} experiment attempt ${i}: ${env} ====="
        rm -f "$log"
        "${COMPOSE[@]}" "cd /simulation/doc-g2-sim4 && ${env} MESH_LEVEL=${level} MODE=experiment REUSE_MESH=1 ./Allrun" \
            2>&1 | tee "$log"
        cp -f "$log" "mesh_independence/${level}_experiment_attempt${i}.log"
        if experiment_ok "$log"; then
            echo "OK: ${level} experiment reached t=30 (${env})"
            return 0
        fi
        echo "WARN: ${level} experiment attempt ${i} failed"
    done
    return 1
}

for LEVEL in "$@"; do
    echo "========== ${LEVEL} =========="
    run_baseline "$LEVEL"
    until run_experiment "$LEVEL"; do
        echo "ERROR: ${LEVEL} experiment exhausted attempts — retrying from attempt 3"
        sleep 5
        # extra pass with smaller dt only
        LOG="mesh_independence/${LEVEL}_experiment.log"
        for env in \
            'DELTA_T=0.01 ADJUST_TIME_STEP=yes MAX_CO=0.3 MAX_DELTA_T=0.005' \
            'DELTA_T=0.005 ADJUST_TIME_STEP=yes MAX_CO=0.2 MAX_DELTA_T=0.002' \
            'DELTA_T=0.002 ADJUST_TIME_STEP=no'; do
            echo "===== ${LEVEL} experiment extra: ${env} ====="
            "${COMPOSE[@]}" "cd /simulation/doc-g2-sim4 && ${env} MESH_LEVEL=${LEVEL} MODE=experiment REUSE_MESH=1 ./Allrun" \
                2>&1 | tee "$LOG"
            experiment_ok "$LOG" && break 2
        done
    done
    echo "DONE: ${LEVEL}"
done
