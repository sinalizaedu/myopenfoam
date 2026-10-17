#!/bin/bash
# 1) MODE=fsi on fsi-transient-a1-patch (O1 fluid + A1 solid)
# 2) On success: bootstrap fsi-run-a1-patch + IVI/ACP FSI experiment (t=5→30)
#
#   nohup ./cases/run_overnight_fsi_transient_a1.sh \
#     > cases/run_overnight_fsi_transient_a1.nohup.out 2>&1 &
#   tail -f cases/run_overnight_fsi_transient_a1.log
set -u
NP="${NP:-1}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
TRANSIENT="fsi-transient-a1-patch"
FSI_RUN="fsi-run-a1-patch"
MASTER_LOG="$REPO/cases/run_overnight_fsi_transient_a1.log"
VALID_LOG="$REPO/cases/$TRANSIENT/run_overnight_fsi.log"
EXPT_LOG="$REPO/cases/$FSI_RUN/run_experiment_overnight.log"
LOCKDIR="/tmp/fsi_transient_a1_overnight.lock"

if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  already running (lock $LOCKDIR)" | tee -a "$MASTER_LOG"
    exit 0
fi
trap 'rmdir "$LOCKDIR" 2>/dev/null || true' EXIT

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

fsi_transient_ok() {
    local logf="$1"
    [ -f "$logf" ] || return 1
    grep -q 'FOAM FATAL' "$logf" && return 1
    grep -qiE 'Floating point exception|FOAM exiting' "$logf" && return 1
    grep -q 'patch A1 transient two-way FSI done' "$logf" || return 1
    return 0
}

log "=== OVERNIGHT START: $TRANSIENT MODE=fsi (np=$NP) ==="

"${COMPOSE[@]}" bash -lc "
    set -euo pipefail
    cd /simulation/$TRANSIENT
    chmod +x Allrun Allrun.sim4 scripts/*.sh 2>/dev/null || true
    MODE=fsi PREWARM_END_TIME=\${PREWARM_END_TIME:-2} FSI_END_TIME=\${FSI_END_TIME:-2} \
        DELTA_T=\${DELTA_T:-0.05} ./Allrun
" >"$VALID_LOG" 2>&1
rc=$?

if [ "$rc" -ne 0 ] || ! fsi_transient_ok "$VALID_LOG"; then
    log "FAIL $TRANSIENT MODE=fsi rc=$rc — see $VALID_LOG"
    tail -30 "$VALID_LOG" | tee -a "$MASTER_LOG" || true
    exit 1
fi
log "OK $TRANSIENT two-way FSI validation"

log "=== bootstrap $FSI_RUN from $TRANSIENT ==="
(
    cd "$REPO/cases/$FSI_RUN"
    chmod +x scripts/*.sh Allrun 2>/dev/null || true
    ./scripts/bootstrap_from_transient.sh
    ./scripts/seed_from_baseline.sh
    ./scripts/build_solid_a1.sh
) >>"$MASTER_LOG" 2>&1 || {
    log "FAIL bootstrap/seed/solid $FSI_RUN — see $MASTER_LOG"
    exit 1
}

log "===== EXPERIMENT $FSI_RUN IVI+ACP FSI t=5→30 np=$NP ====="
"${COMPOSE[@]}" bash -lc "
    set -euo pipefail
    cd /simulation/$FSI_RUN
    chmod +x scripts/*.sh Allrun
    ./scripts/run_experiment_fsi.sh O1 $NP
" >>"$EXPT_LOG" 2>&1
rc=$?

if [ "$rc" -eq 0 ] && grep -qE '^Time = 30[[:space:]]*$' "$REPO/cases/$FSI_RUN/fluid/log.pimpleFoam" 2>/dev/null; then
    log "OK $FSI_RUN reached t=30"
else
    log "FAIL $FSI_RUN experiment rc=$rc — see $EXPT_LOG"
    tail -40 "$EXPT_LOG" | tee -a "$MASTER_LOG" || true
    exit 1
fi

log "=== OVERNIGHT COMPLETE ==="
log "validation: $VALID_LOG"
log "experiment: $EXPT_LOG"
