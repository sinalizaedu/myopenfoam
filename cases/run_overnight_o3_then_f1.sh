#!/bin/bash
# Overnight queue: finish O3 patch+volume, then F1 volume baseline.
#
#   nohup ./cases/run_overnight_o3_then_f1.sh > cases/run_overnight_o3_then_f1.nohup.out 2>&1 &
#   tail -f cases/run_overnight_o3_then_f1.log
set -euo pipefail

MAX_PARALLEL="${MAX_PARALLEL:-1}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
MASTER_LOG="$REPO/cases/run_overnight_o3_then_f1.log"

# Strict launch order once a slot is free.
PENDING=(
    doc-baseline-o3-volume-fluid
    doc-baseline-f1-volume-fluid
)

WATCH=(
    doc-baseline-o3-patch-fluid
    doc-baseline-o3-volume-fluid
    doc-baseline-f1-volume-fluid
)

log() {
    echo "$(date -Iseconds)  $*" | tee -a "$MASTER_LOG"
}

is_done() {
    local case_dir="$1"
    local slog="$REPO/cases/$case_dir/fluid/log.simpleFoam"
    if [ -f "$slog" ] && grep -q '^End$' "$slog" 2>/dev/null; then
        return 0
    fi
    if grep -qE 'sim[45] done \(MODE=baseline|=== resume done ===' \
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
    case "$case_dir" in
        *-f1-*)
            [ -f "$REPO/cases/doc-g2-sim1/geometry/eye_g2_fluid_fluent_F1.msh" ]
            ;;
        *)
            [ -d "$REPO/cases/$case_dir/fluid/constant/polyMesh" ] && \
                grep -q "cells:" "$REPO/cases/$case_dir/fluid/log.checkMesh" 2>/dev/null
            ;;
    esac
}

can_start() {
    local case_dir="$1"
    # O3 volume waits for O3 patch.
    if [ "$case_dir" = "doc-baseline-o3-volume-fluid" ]; then
        is_done "doc-baseline-o3-patch-fluid" || return 1
    fi
    # F1 cases wait for both O3 runs.
    case "$case_dir" in
        doc-baseline-f1-*)
            is_done "doc-baseline-o3-patch-fluid" || return 1
            is_done "doc-baseline-o3-volume-fluid" || return 1
            ;;
    esac
    return 0
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
        if [ -d fluid/constant/polyMesh ] && [ -f fluid/log.simpleFoam ]; then
            REUSE_MESH=1 MODE=baseline ./Allrun
        elif [ -d fluid/constant/polyMesh ]; then
            REUSE_MESH=1 MODE=baseline ./Allrun
        else
            MODE=baseline ./Allrun
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

launched=()
was_launched() {
    local target="$1" c
    if [ "${#launched[@]}" -eq 0 ]; then
        return 1
    fi
    for c in "${launched[@]}"; do
        [ "$c" = "$target" ] && return 0
    done
    return 1
}

log "=== OVERNIGHT QUEUE START max=$MAX_PARALLEL ==="
for c in "${WATCH[@]}"; do
    if is_done "$c"; then
        log "SKIP already done: $c"
    elif is_running "$c"; then
        log "WATCH already running: $c"
    fi
done

while true; do
    all_done=1
    for case_dir in "${WATCH[@]}"; do
        is_done "$case_dir" || all_done=0
    done

    if [ "$all_done" -eq 1 ]; then
        log "=== ALL DONE (O3 + F1) ==="
        python3 "$REPO/cases/scripts_mesh_indep_report_O1_O3.py" || true
        python3 "$REPO/cases/scripts_mesh_indep_report_F1_F2.py" || true
        break
    fi

    running="$(count_running)"
    for case_dir in "${PENDING[@]}"; do
        is_done "$case_dir" && continue
        is_running "$case_dir" && continue
        was_launched "$case_dir" && continue
        can_start "$case_dir" || continue
        if ! mesh_ready "$case_dir"; then
            log "WAIT mesh/geometry not ready: $case_dir"
            continue
        fi
        if [ "$running" -ge "$MAX_PARALLEL" ]; then
            break
        fi
        launched+=("$case_dir")
        run_case "$case_dir" &
        running=$((running + 1))
        log "LAUNCHED $case_dir (running=$running)"
        sleep 5
    done

    sleep 30
done

wait || true
