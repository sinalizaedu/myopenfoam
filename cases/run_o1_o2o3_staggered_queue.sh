#!/bin/bash
# Staggered baseline queue (max 2 parallel):
#   O1 patch + O2 volume  →  when one finishes start O3 patch  →  then O3 volume.
#
# Host:
#   nohup ./cases/run_o1_o2o3_staggered_queue.sh > cases/run_o1_o2o3_staggered_queue.nohup.out 2>&1 &
#   tail -f cases/run_o1_o2o3_staggered_queue.log
set -euo pipefail

MAX_PARALLEL="${MAX_PARALLEL:-2}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
MASTER_LOG="$REPO/cases/run_o1_o2o3_staggered_queue.log"

# Launch order for free slots (skip cases already done/running).
PENDING=(
    doc-baseline-o2-volume-fluid
    doc-baseline-o3-patch-fluid
    doc-baseline-o3-volume-fluid
)

# Also track O1 patch if started outside this queue (e.g. run_o1_baseline_rerun.sh).
WATCH=(
    doc-baseline-o1-patch-fluid
    doc-baseline-o2-volume-fluid
    doc-baseline-o3-patch-fluid
    doc-baseline-o3-volume-fluid
)

log() {
    echo "$(date -Iseconds)  $*" | tee -a "$MASTER_LOG"
}

is_done() {
    local case_dir="$1"
    local log="$REPO/cases/$case_dir/fluid/log.simpleFoam"
    if rg -q '^End$' "$log" 2>/dev/null; then
        return 0
    fi
    if rg -q 'sim[45] done \(MODE=baseline|=== resume done ===' \
        "$REPO/cases/$case_dir/run_baseline.log" 2>/dev/null; then
        return 0
    fi
    return 1
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
    [ -d "$REPO/cases/$case_dir/fluid/constant/polyMesh" ] && \
        grep -q "cells:" "$REPO/cases/$case_dir/fluid/log.checkMesh" 2>/dev/null
}

count_running() {
    local n=0 c
    for c in "${WATCH[@]}"; do
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
        REUSE_MESH=1 MODE=baseline ./Allrun
    " >>"$case_log" 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        log "OK $case_dir"
    else
        log "FAIL $case_dir exit=$rc"
    fi
    return "$rc"
}

started=()
is_started() {
    local target="$1"
    local c
    if [ "${#started[@]}" -eq 0 ]; then
        return 1
    fi
    for c in "${started[@]}"; do
        [ "$c" = "$target" ] && return 0
    done
    return 1
}

log "=== STAGGERED QUEUE START max=$MAX_PARALLEL pending=${PENDING[*]} ==="

while true; do
    running="$(count_running)"
    all_done=1

    for case_dir in "${WATCH[@]}"; do
        is_done "$case_dir" || all_done=0
    done

    if [ "$all_done" -eq 1 ]; then
        log "=== ALL DONE ==="
        python3 "$REPO/cases/scripts_mesh_indep_report_O1_O3.py" || true
        break
    fi

    running="$(count_running)"
    for case_dir in "${PENDING[@]}"; do
        is_done "$case_dir" && continue
        is_running "$case_dir" && continue
        is_started "$case_dir" && continue
        if ! mesh_ready "$case_dir"; then
            log "WAIT mesh not ready for $case_dir"
            continue
        fi
        if [ "$running" -ge "$MAX_PARALLEL" ]; then
            break
        fi
        started+=("$case_dir")
        run_case "$case_dir" &
        running=$((running + 1))
        log "LAUNCHED $case_dir (running=$running)"
        sleep 3
    done

    sleep 20
done

wait || true
