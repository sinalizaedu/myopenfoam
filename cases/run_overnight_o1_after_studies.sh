#!/bin/bash
# Wait for the O1 patch + volume diagnostic studies, then (if clean) run
# production: skip baseline unless missing End, then 30 s experiments.
#
#   nohup ./cases/run_overnight_o1_after_studies.sh \
#     > cases/run_overnight_o1_after_studies.nohup.out 2>&1 &
set -u
NP="${NP:-4}"
POLL_SEC="${POLL_SEC:-60}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
MASTER_LOG="$REPO/cases/run_overnight_o1_after_studies.log"
LOCKDIR="/tmp/o1_overnight_after_studies.lock"
PATCH_RUN="doc-run-o1-patch-fluid"
VOLUME_RUN="doc-run-o1-volume-fluid"
PATCH_BASE="doc-baseline-o1-patch-fluid"
VOLUME_BASE="doc-baseline-o1-volume-fluid"
PATCH_STUDY_LOG="$REPO/cases/$PATCH_RUN/mesh_independence/run_O1_experiment_1s_pfinal_dt005.log"
VOL_AGENT="$HOME/.cursor/projects/Users-brunaenne-Documents-repos-myopenfoam/agent-transcripts/2118672d-871d-48a7-ada4-ec6d3ba63a40/2118672d-871d-48a7-ada4-ec6d3ba63a40.jsonl"

if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  already running (lock $LOCKDIR)" | tee -a "$MASTER_LOG"
    exit 0
fi
trap 'rmdir "$LOCKDIR" 2>/dev/null || true' EXIT

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

docker_cmds() {
    docker ps -q | while read -r id; do
        [ -n "$id" ] || continue
        docker inspect --format '{{join .Config.Cmd " "}}' "$id" 2>/dev/null || true
    done
}

study_docker_running() {
    docker_cmds | grep -E \
        'END_TIME=1|run_O1_experiment_1s|diag-o1-mass-source|diag-p-source|pimpleFoamMassSource|wmake' \
        >/dev/null 2>&1
}

case_docker_running() {
    local needle="$1"
    docker_cmds | grep -F "/simulation/${needle}" >/dev/null 2>&1
}

file_age_sec() {
    local f="$1"
    if [ ! -f "$f" ]; then
        echo 999999
        return
    fi
    python3 - "$f" <<'PY'
import os, sys, time
print(int(time.time() - os.path.getmtime(sys.argv[1])))
PY
}

log_ok() {
    local f="$1"
    [ -f "$f" ] || return 1
    grep -q 'FOAM FATAL' "$f" && return 1
    grep -qiE 'Floating point exception|FOAM exiting' "$f" && return 1
    return 0
}

study_time_done() {
    local f="$1" t="$2"
    [ -f "$f" ] || return 1
    grep -qE "^Time = ${t}[[:space:]]*$" "$f" || return 1
    grep -q '^End$' "$f" || grep -q "experiment 1h OK\|MODE=experiment.*done\|End" "$f"
}

baseline_ok() {
    local case_dir="$1"
    local slog="$REPO/cases/$case_dir/fluid/log.simpleFoam"
    local yaml="$REPO/cases/$case_dir/calibration/baseline_iop.yaml"
    [ -f "$yaml" ] && grep -q '^End$' "$slog" 2>/dev/null
}

experiment_ok() {
    local case_dir="$1"
    local logf="$REPO/cases/$case_dir/fluid/log.pimpleFoam"
    grep -qE '^Time = 30[[:space:]]*$' "$logf" 2>/dev/null \
        && ! grep -q 'FOAM FATAL' "$logf" 2>/dev/null
}

run_baseline_if_needed() {
    local case_dir="$1"
    if baseline_ok "$case_dir"; then
        log "SKIP baseline $case_dir (End + calibration present)"
        return 0
    fi
    log "===== BASELINE $case_dir ====="
    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$case_dir
        chmod +x Allrun scripts/*.sh 2>/dev/null || true
        REUSE_MESH=1 MODE=baseline ./Allrun
    " >>"$REPO/cases/$case_dir/run_baseline_overnight.log" 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ] && baseline_ok "$case_dir"; then
        log "OK baseline $case_dir"
        return 0
    fi
    log "FAIL baseline $case_dir rc=$rc"
    return 1
}

run_experiment() {
    local case_dir="$1"
    local case_log="$REPO/cases/$case_dir/run_experiment_overnight.log"
    if experiment_ok "$case_dir" && [ "${FORCE_RERUN:-0}" != "1" ]; then
        # Always rerun overnight production: previous t=30 is stale vs new solver/settings.
        :
    fi
    log "===== EXPERIMENT $case_dir np=$NP ====="
    (
        cd "$REPO/cases/$case_dir"
        chmod +x scripts/*.sh Allrun
        ./scripts/seed_from_baseline.sh
    ) >>"$case_log" 2>&1

    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        export OVERNIGHT_O1=1
        cd /simulation/$case_dir
        chmod +x scripts/*.sh Allrun
        ./scripts/run_experiment_1h.sh O1 $NP
    " >>"$case_log" 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ] && experiment_ok "$case_dir"; then
        log "OK $case_dir t=30"
        return 0
    fi
    log "FAIL $case_dir experiment rc=$rc"
    return 1
}

log "=== OVERNIGHT START np=$NP (wait studies → baseline if needed → O1 patch + volume 30s) ==="

# --- wait for diagnostic studies ---
log "Waiting for in-flight O1 patch/volume studies to finish"
idle_rounds=0
while true; do
    if study_docker_running || case_docker_running "$PATCH_RUN"; then
        idle_rounds=0
        lt="$(grep -E '^Time = ' "$PATCH_STUDY_LOG" 2>/dev/null | tail -1 | awk '{print $3}' || echo '?')"
        log "study docker still running (patch 1s Time=${lt:-?})"
        sleep "$POLL_SEC"
        continue
    fi
    # If the 1s container died short of t=1, stop waiting and treat as a failed study.
    if [ -f "$PATCH_STUDY_LOG" ]; then
        if ! grep -qE '^Time = 1[[:space:]]*$' "$PATCH_STUDY_LOG" && ! grep -q '^End$' "$PATCH_STUDY_LOG"; then
            idle_rounds=$((idle_rounds + 1))
            log "patch 1s container gone but log not at t=1 (idle_rounds=$idle_rounds)"
            if [ "$idle_rounds" -ge 3 ]; then
                log "giving up on patch 1s study — will skip patch production"
                break
            fi
            sleep "$POLL_SEC"
            continue
        fi
    fi
    age="$(file_age_sec "$VOL_AGENT")"
    if [ "$age" -lt 900 ]; then
        idle_rounds=0
        log "volume-agent transcript still updating (${age}s ago) — waiting"
        sleep "$POLL_SEC"
        continue
    fi
    idle_rounds=$((idle_rounds + 1))
    # two consecutive idle polls (~2 min) after docker gone + volume agent quiet
    if [ "$idle_rounds" -ge 2 ]; then
        log "studies idle (docker gone, volume agent quiet ${age}s)"
        break
    fi
    sleep "$POLL_SEC"
done

PATCH_STUDY_OK=0
VOLUME_STUDY_OK=0

if log_ok "$PATCH_STUDY_LOG" && grep -qE '^Time = 1[[:space:]]*$|^End$' "$PATCH_STUDY_LOG"; then
    PATCH_STUDY_OK=1
    log "PATCH study OK: $PATCH_STUDY_LOG"
    # Keep 1h production on the validated pFinal settings.
    if [ -f "$REPO/cases/$PATCH_RUN/fluid/system/fvSolution.experiment" ]; then
        cp -f "$REPO/cases/$PATCH_RUN/fluid/system/fvSolution.experiment" \
            "$REPO/cases/$PATCH_RUN/fluid/system/fvSolution.experiment.1h"
        log "synced patch fvSolution.experiment.1h from study"
    fi
else
    log "PATCH study NOT clean — skipping patch production"
    if [ -f "$PATCH_STUDY_LOG" ]; then
        grep -E 'FOAM FATAL|Floating point|FOAM exiting' "$PATCH_STUDY_LOG" | tail -5 | tee -a "$MASTER_LOG" || true
    fi
fi

VOL_FV="$REPO/cases/$VOLUME_RUN/fluid/system/fvOptions.experiment"
if grep -q 'ivi_mass_injection' "$VOL_FV" 2>/dev/null \
    && grep -q 'scalarSemiImplicitSource' "$VOL_FV" 2>/dev/null; then
    # Accept volume study if latest volume/diag logs are clean (or no crash log).
    vol_bad=0
    for f in \
        "$REPO/cases/$VOLUME_RUN/mesh_independence/"*.log \
        "$REPO/cases/diag-o1-mass-source/fluid/log.pimpleFoam" \
        "$REPO/cases/diag-o1-mass-source/fluid/"*.log
    do
        [ -f "$f" ] || continue
        if grep -q 'FOAM FATAL' "$f" 2>/dev/null; then
            log "VOLUME study error in $f"
            vol_bad=1
        fi
    done
    if [ "$vol_bad" -eq 0 ]; then
        VOLUME_STUDY_OK=1
        log "VOLUME study OK (mass-source fvOptions present, no FOAM FATAL)"
    fi
else
    log "VOLUME study NOT ready (missing scalar mass sources) — skip volume production"
fi

if [ "$PATCH_STUDY_OK" -eq 1 ]; then
    run_baseline_if_needed "$PATCH_BASE" || PATCH_STUDY_OK=0
fi
if [ "$VOLUME_STUDY_OK" -eq 1 ]; then
    run_baseline_if_needed "$VOLUME_BASE" || VOLUME_STUDY_OK=0
fi

if [ "$PATCH_STUDY_OK" -eq 1 ]; then
    run_experiment "$PATCH_RUN" || log "patch experiment failed"
else
    log "skip $PATCH_RUN"
fi

if [ "$VOLUME_STUDY_OK" -eq 1 ]; then
    run_experiment "$VOLUME_RUN" || log "volume experiment failed"
else
    log "skip $VOLUME_RUN"
fi

log "=== OVERNIGHT COMPLETE ==="
log "master: $MASTER_LOG"
log "patch:  $REPO/cases/$PATCH_RUN/run_experiment_overnight.log"
log "volume: $REPO/cases/$VOLUME_RUN/run_experiment_overnight.log"
