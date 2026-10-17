#!/bin/bash
# Experiment only — retry stage2 until t=30. Never runs baseline (no simpleFoam / no mesh regen).
# Requires fluid/2 from a prior successful stage1, or baseline time dir for fresh stage1.
# Usage: ./scripts/run_experiment_until_done.sh MESH_LEVEL [NP]
# Stage2 tries dt=0.02 first (1h protocol), then smaller dt only on instability.
set -euo pipefail
cd "$(dirname "$0")/.."
MESH_LEVEL="${1:-M7}"
NP="${2:-1}"

LOG="mesh_independence/run_${MESH_LEVEL}_experiment_until_done.log"
mkdir -p mesh_independence

log() { echo "$@" | tee -a "$LOG"; }

stage_configs() {
    for f in U.experiment.1h controlDict.experiment.1h fvSolution.experiment.1h fvSchemes.experiment.1h; do
        base="${f%.1h}"
        case "$f" in
            U.*) cp -f "fluid/initial/$f" "fluid/initial/${base}" ;;
            *)   cp -f "fluid/system/$f" "fluid/system/${base}" ;;
        esac
    done
    cp -f fluid/initial/U.experiment fluid/initial/U.experiment.robin
}

run_solver() {
    (
        cd fluid
        rm -rf processor*
        if [ "$NP" -le 1 ]; then
            pimpleFoam 2>&1 | tee -a log.pimpleFoam
        else
            decomposePar -force 2>&1 | tee -a log.decomposePar
            mpirun -np "$NP" --oversubscribe pimpleFoam -parallel 2>&1 | tee -a log.pimpleFoam
            reconstructPar -latestTime 2>&1 | tee -a log.reconstructPar
        fi
    )
}

experiment_ok() {
    local log="${1:-fluid/log.pimpleFoam}"
    grep -qE '^Time = 30[[:space:]]*$' "$log" 2>/dev/null \
        && ! grep -q 'FOAM FATAL' "$log" 2>/dev/null \
        && ! grep -qiE '\bnan\b' "$log" 2>/dev/null
}

stage2_unstable() {
    local log="${1:-fluid/log.pimpleFoam}"
    grep -q 'FOAM FATAL' "$log" 2>/dev/null \
        || grep -qiE '\bnan\b' "$log" 2>/dev/null
}

stage2_failure_reason() {
    local log="${1:-fluid/log.pimpleFoam}"
    if ! grep -qE '^Time = 30[[:space:]]*$' "$log" 2>/dev/null; then
        echo "did not reach t=30"
    elif stage2_unstable "$log"; then
        echo "FOAM FATAL or NaN in solver log"
    else
        echo "unknown"
    fi
}

find_baseline_time() {
    local best=""
    local best_t=0
    for d in fluid/[0-9]*; do
        [ -e "$d" ] || continue
        base="$(basename "$d")"
        [[ "$base" =~ ^[0-9]+$ ]] || continue
        [ "$base" = "0" ] && continue
        if [ "$base" -lt 100 ] 2>/dev/null; then
            continue
        fi
        if [ "$base" -gt "$best_t" ] 2>/dev/null; then
            best_t="$base"
            best="$d"
        fi
    done
    [ -n "$best" ] && echo "$best"
}

clean_experiment_times_keep() {
    local keep_re="$1"
    find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\.[0-9]+' -exec rm -rf {} + 2>/dev/null || true
    for d in fluid/[0-9]*; do
        [ -e "$d" ] || continue
        base="$(basename "$d")"
        [[ "$base" =~ $keep_re ]] && continue
        rm -rf "$d"
    done
}

save_checkpoint() {
    local t="$1"
    rm -rf "fluid/_checkpoint_${t}"
    cp -a "fluid/${t}" "fluid/_checkpoint_${t}"
    log "  saved checkpoint fluid/_checkpoint_${t}"
}

restore_checkpoint() {
    local t="$1"
    local src="fluid/_checkpoint_${t}"
    [ -d "$src" ] && [ -f "$src/p" ] || { log "ERROR: missing checkpoint $src"; return 1; }
    clean_experiment_times_keep "^${t}$"
    rm -rf "fluid/${t}"
    cp -a "$src" "fluid/${t}"
}

ensure_checkpoint_2() {
    if [ -d fluid/_checkpoint_2 ] && [ -f fluid/_checkpoint_2/p ]; then
        return 0
    fi
    if [ -d fluid/2 ] && [ -f fluid/2/p ]; then
        save_checkpoint 2
        return 0
    fi
    return 1
}

run_stage1() {
    local dt="$1"
    log "--- stage 1: t=0->2 s (dt=${dt}) ---"
    baseline="$(find_baseline_time || true)"
    if [ -z "$baseline" ]; then
        log "ERROR: no baseline time dir (e.g. fluid/320) for stage1 seed"
        return 1
    fi
    rm -rf fluid/0 fluid/processor*
    MESH_LEVEL="$MESH_LEVEL" MODE=experiment REUSE_MESH=1 SKIP_SOLVE=1 ./Allrun | tee -a "$LOG"
    find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\.[0-9]+' -exec rm -rf {} + 2>/dev/null || true

    cp -f fluid/system/controlDict.experiment.1h fluid/system/controlDict
    sed -i.bak -E \
        -e 's/^(startFrom[[:space:]]+).*/\1startTime;/' \
        -e 's/^(startTime[[:space:]]+).*/\10;/' \
        -e 's/^(endTime[[:space:]]+).*/\12;/' \
        -e "s/^(deltaT[[:space:]]+).*/\\1${dt};/" \
        -e 's/^(adjustTimeStep[[:space:]]+).*/\1no;/' \
        fluid/system/controlDict
    rm -f fluid/system/controlDict.bak

    rm -f fluid/log.pimpleFoam
    run_solver | tee -a "$LOG"
    grep -qE '^Time = 2[[:space:]]*$' fluid/log.pimpleFoam || return 1
    clean_experiment_times_keep '^2$'
    save_checkpoint 2
}

run_stage2_from2() {
    local dt="$1"
    log "--- stage 2: t=2->30 s (dt=${dt}) ---"
    restore_checkpoint 2 || return 1
    cp -f fluid/system/controlDict.experiment.1h fluid/system/controlDict
    sed -i.bak -E \
        -e 's/^(startFrom[[:space:]]+).*/\1latestTime;/' \
        -e 's/^(endTime[[:space:]]+).*/\130;/' \
        -e "s/^(deltaT[[:space:]]+).*/\\1${dt};/" \
        -e 's/^(adjustTimeStep[[:space:]]+).*/\1no;/' \
        fluid/system/controlDict
    rm -f fluid/system/controlDict.bak

    rm -f fluid/log.pimpleFoam
    run_solver | tee -a "$LOG"
    if experiment_ok fluid/log.pimpleFoam; then
        if [ -d fluid/30 ] && [ -f fluid/30/p ]; then
            save_checkpoint 30
        fi
        return 0
    fi
    log "WARN: stage2 dt=${dt} failed — $(stage2_failure_reason fluid/log.pimpleFoam)"
    return 1
}

stage_configs
log "=== experiment until done: ${MESH_LEVEL} np=${NP} (no baseline) ==="

if ! ensure_checkpoint_2; then
    log "=== no fluid/2 — trying stage1 from baseline seed ==="
    ok=0
    for dt1 in 0.005 0.002; do
        log "===== stage1 try dt=${dt1} ====="
        if run_stage1 "$dt1"; then ok=1; break; fi
        log "WARN: stage1 failed dt=${dt1}"
    done
    [ "$ok" = "1" ] || { log "ERROR: stage1 failed — need fluid/320 or fluid/2"; exit 1; }
fi

for dt in 0.02 0.005 0.002 0.001; do
    log "===== stage2 try dt=${dt} ====="
    if run_stage2_from2 "$dt"; then
        python3 scripts/extract_metrics.py --protocol ivi_acp 2>&1 | tee -a "$LOG" || true
        python3 scripts/archive_experiment_results.py 2>&1 | tee -a "$LOG" || true
        log "=== EXPERIMENT DONE (${MESH_LEVEL}, dt2=${dt}) ==="
        exit 0
    fi
    if [ -f fluid/log.pimpleFoam ] && ! stage2_unstable fluid/log.pimpleFoam \
        && grep -qE '^Time = 30[[:space:]]*$' fluid/log.pimpleFoam; then
        log "ERROR: stage2 dt=${dt} reached t=30 without instability but failed validation — stopping"
        exit 1
    fi
done

log "ERROR: experiment failed all stage2 attempts"
exit 1
