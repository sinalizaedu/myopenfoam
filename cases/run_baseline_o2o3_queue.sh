#!/bin/bash
# Run baseline patch+volume mesh-independence cases (O2–O3, F1–F2) with MAX_PARALLEL jobs.
#
# Host:
#   ./cases/run_baseline_o2o3_queue.sh
#   tail -f cases/run_baseline_o2o3_queue.log
set -euo pipefail

MAX_PARALLEL="${MAX_PARALLEL:-2}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
MASTER_LOG="$REPO/cases/run_baseline_o2o3_queue.log"

CASES=(
    doc-baseline-o2-patch-fluid
    doc-baseline-o2-volume-fluid
    doc-baseline-o3-patch-fluid
    doc-baseline-o3-volume-fluid
    doc-baseline-f1-volume-fluid
)

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" >>"$MASTER_LOG"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*"
}

is_done() {
    local case_dir="$1"
    if rg -q 'sim[45] done \(MODE=baseline|=== resume done ===' "$REPO/cases/$case_dir/run_baseline.log" 2>/dev/null; then
        return 0
    fi
    local log="$REPO/cases/$case_dir/fluid/log.simpleFoam"
    [ -f "$log" ] || return 1
    local t
    t="$(rg '^Time = ' "$log" | tail -1 | awk '{print $3}')"
    [ "${t:-0}" -ge 1000 ]
}

is_running() {
    local case_dir="$1"
    local id cmd
    while read -r id; do
        [ -n "$id" ] || continue
        cmd="$(docker inspect --format '{{join .Config.Cmd " "}}' "$id" 2>/dev/null || true)"
        [[ "$cmd" == *"/simulation/${case_dir}"* ]] && return 0
    done < <(docker ps -q)
    return 1
}

mesh_ready() {
    local case_dir="$1"
    case "$case_dir" in
        *-f1-*)
            [ -f "$REPO/cases/doc-g2-sim1/geometry/eye_g2_fluid_fluent_F1.msh" ]
            ;;
        *)
            return 0
            ;;
    esac
}

is_pending() {
    local case_dir="$1"
    is_done "$case_dir" && return 1
    is_running "$case_dir" && return 1
    mesh_ready "$case_dir" || return 1
    return 0
}

count_running() {
    local n=0 c
    for c in "${CASES[@]}"; do
        is_running "$c" && n=$((n + 1))
    done
    echo "$n"
}

run_case() {
    local case_dir="$1"
    local case_log="$REPO/cases/$case_dir/run_baseline.log"
    log "START $case_dir"
    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$case_dir
        if [ ! -d fluid/constant/polyMesh ]; then
            ./Allrun
        elif [ ! -f fluid/log.simpleFoam ]; then
            REUSE_MESH=1 ./Allrun
        else
            latest=\$(find fluid -maxdepth 1 -type d -regex '.*/[0-9]+' -printf '%f\\n' 2>/dev/null | sort -n | tail -1 || true)
            if [ -z \"\$latest\" ]; then
                REUSE_MESH=1 ./Allrun
            else
                echo \"=== resume simpleFoam from latestTime=\${latest} ===\"
                cp fluid/system/controlDict fluid/system/controlDict.queue.bak
                sed -i -E 's/^(startFrom[[:space:]]+).*/\\1latestTime;/' fluid/system/controlDict
                sed -i -E \"s/^(startTime[[:space:]]+).*/\\1\${latest};/\" fluid/system/controlDict
                (cd fluid && simpleFoam 2>&1 | tee -a log.simpleFoam)
                mv fluid/system/controlDict.queue.bak fluid/system/controlDict
                grep -q 'FOAM FATAL' fluid/log.simpleFoam && exit 1
                python3 scripts/extract_step0_metrics.py || true
                python3 scripts/save_baseline_calibration.py || true
                echo '=== resume done ==='
            fi
        fi
    " >>"$case_log" 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        log "OK $case_dir"
    else
        log "FAIL $case_dir exit=$rc"
    fi
    return "$rc"
}

log_waiting_logged=0
log "=== QUEUE START max=$MAX_PARALLEL cases=${CASES[*]} ==="

while true; do
    pending=0
    running="$(count_running)"
    for case_dir in "${CASES[@]}"; do
        if is_done "$case_dir" || is_running "$case_dir"; then
            continue
        fi
        if ! mesh_ready "$case_dir"; then
            if [ "$log_waiting_logged" -eq 0 ]; then
                log "WAIT mesh missing for $case_dir (Fluent .msh not on disk yet)"
                log_waiting_logged=1
            fi
            pending=1
            continue
        fi
        pending=1
        if [ "$running" -ge "$MAX_PARALLEL" ]; then
            break
        fi
        run_case "$case_dir" &
        running=$((running + 1))
        sleep 5
    done

    if [ "$pending" -eq 0 ]; then
        log "=== QUEUE DONE ==="
        break
    fi

    sleep 30
done

wait || true
