#!/bin/bash
# Overnight: wait for F1 volume baseline (or finish it), then O1 IVI+ACP runs
# for patch + volume (doc-run-o1-*).
#
#   nohup ./cases/run_overnight_f1vol_then_o1_runs.sh \
#     > cases/run_overnight_f1vol_then_o1_runs.nohup.out 2>&1 &
#   tail -f cases/run_overnight_f1vol_then_o1_runs.log
set -euo pipefail

NP="${NP:-4}"
POLL_SEC="${POLL_SEC:-60}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
MASTER_LOG="$REPO/cases/run_overnight_f1vol_then_o1_runs.log"
F1_CASE="doc-baseline-f1-volume-fluid"
PATCH_RUN="doc-run-o1-patch-fluid"
VOLUME_RUN="doc-run-o1-volume-fluid"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

f1_done() {
    local slog="$REPO/cases/$F1_CASE/fluid/log.simpleFoam"
    if [ -f "$slog" ] && grep -q '^End$' "$slog" 2>/dev/null; then
        return 0
    fi
    if grep -qE 'sim5 done \(MODE=baseline|=== resume done ===' \
        "$REPO/cases/$F1_CASE/run_baseline.log" 2>/dev/null; then
        return 0
    fi
    return 1
}

f1_running() {
    local id cmd
    while read -r id; do
        [ -n "$id" ] || continue
        cmd="$(docker inspect --format '{{join .Config.Cmd " "}}' "$id" 2>/dev/null || true)"
        [[ "$cmd" == *"/simulation/${F1_CASE}"* ]] && return 0
    done < <(docker ps -q)
    return 1
}

f1_latest_time() {
    python3 - <<PY
from pathlib import Path
fluid = Path("$REPO/cases/$F1_CASE/fluid")
best = -1
for p in fluid.iterdir():
    if p.is_dir() and p.name.isdigit():
        t = int(p.name)
        if t > best:
            best = t
print(best if best >= 0 else "")
PY
}

wait_for_f1() {
    log "=== WAIT F1 volume baseline ($F1_CASE) ==="
    if f1_done; then
        log "F1 already done"
        return 0
    fi
    if f1_running; then
        log "F1 already running in Docker — polling until End"
        while f1_running || ! f1_done; do
            if f1_done; then
                log "F1 done (End in log.simpleFoam)"
                return 0
            fi
            if ! f1_running && ! f1_done; then
                log "F1 container exited without End — will resume"
                break
            fi
            lt="$(f1_latest_time)"
            log "F1 still running (latestTime=${lt:-?})"
            sleep "$POLL_SEC"
        done
    fi

    if f1_done; then
        log "F1 done"
        return 0
    fi

    log "START/RESUME $F1_CASE"
    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$F1_CASE
        if [ ! -d fluid/constant/polyMesh ]; then
            MODE=baseline ./Allrun
        elif [ ! -f fluid/log.simpleFoam ] || ! grep -q '^End\$' fluid/log.simpleFoam; then
            latest=\$(find fluid -maxdepth 1 -type d -regex '.*/[0-9]+' -printf '%f\\n' 2>/dev/null | sort -n | tail -1 || true)
            if [ -n \"\$latest\" ] && [ \"\$latest\" != \"0\" ]; then
                echo \"=== resume simpleFoam from latestTime=\${latest} ===\"
                cp -f fluid/system/controlDict fluid/system/controlDict.queue.bak
                sed -i -E 's/^(startFrom[[:space:]]+).*/\\1latestTime;/' fluid/system/controlDict
                sed -i -E \"s/^(startTime[[:space:]]+).*/\\1\${latest};\" fluid/system/controlDict
                (cd fluid && simpleFoam 2>&1 | tee -a log.simpleFoam)
                mv -f fluid/system/controlDict.queue.bak fluid/system/controlDict
                grep -q 'FOAM FATAL' fluid/log.simpleFoam && exit 1
                python3 scripts/extract_step0_metrics.py || true
                python3 scripts/save_baseline_calibration.py || true
                echo '=== resume done ==='
            else
                REUSE_MESH=1 MODE=baseline ./Allrun
            fi
        else
            python3 scripts/save_baseline_calibration.py || true
            echo '=== already End — calibration refreshed ==='
        fi
    " >>"$REPO/cases/$F1_CASE/run_baseline.log" 2>&1

    if f1_done; then
        log "OK $F1_CASE"
        return 0
    fi
    log "FAIL $F1_CASE did not reach End"
    return 1
}

ensure_f1_calibration() {
    log "=== ensure F1 calibration yaml ==="
    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$F1_CASE
        python3 scripts/save_baseline_calibration.py || true
        ls -la calibration/ || true
        cat calibration/baseline_iop.yaml 2>/dev/null || true
    " >>"$MASTER_LOG" 2>&1 || true
}

run_o1_experiment() {
    local case_dir="$1"
    local case_log="$REPO/cases/$case_dir/run_experiment_overnight.log"
    log "===== O1 EXPERIMENT $case_dir np=$NP ====="
    # Re-seed from baseline in case fields were wiped
    (
        cd "$REPO/cases/$case_dir"
        ./scripts/seed_from_baseline.sh
    ) >>"$case_log" 2>&1

    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$case_dir
        chmod +x scripts/run_experiment_1h.sh scripts/seed_from_baseline.sh Allrun
        ./scripts/run_experiment_1h.sh O1 $NP
    " >>"$case_log" 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        log "OK $case_dir experiment"
    else
        log "FAIL $case_dir experiment exit=$rc — trying until_done if available"
        if [ -x "$REPO/cases/$case_dir/scripts/run_experiment_until_done.sh" ]; then
            "${COMPOSE[@]}" bash -lc "
                set -euo pipefail
                cd /simulation/$case_dir
                ./scripts/run_experiment_until_done.sh O1 $NP
            " >>"$case_log" 2>&1
            rc=$?
            if [ "$rc" -eq 0 ]; then
                log "OK $case_dir via until_done"
            else
                log "FAIL $case_dir until_done exit=$rc"
            fi
        fi
    fi
    return "$rc"
}

log "=== OVERNIGHT START np=$NP (F1 volume baseline → O1 patch → O1 volume) ==="

wait_for_f1
ensure_f1_calibration

# O1 runs sequentially (one Docker job at a time — F1 may still be freeing cores)
run_o1_experiment "$PATCH_RUN" || log "continuing after patch failure"
run_o1_experiment "$VOLUME_RUN" || log "volume run failed"

log "=== OVERNIGHT COMPLETE ==="
log "F1 calib: $REPO/cases/$F1_CASE/calibration/baseline_iop.yaml"
log "Patch log: $REPO/cases/$PATCH_RUN/run_experiment_overnight.log"
log "Volume log: $REPO/cases/$VOLUME_RUN/run_experiment_overnight.log"
