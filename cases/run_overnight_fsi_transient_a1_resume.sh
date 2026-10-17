#!/bin/bash
# Resume A1 coupled FSI from finished prewarm, then fsi-run-a1-patch on success.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
TRANSIENT="fsi-transient-a1-patch"
FSI_RUN="fsi-run-a1-patch"
MASTER_LOG="$REPO/cases/run_overnight_fsi_transient_a1.log"
VALID_LOG="$REPO/cases/$TRANSIENT/run_overnight_fsi.log"
EXPT_LOG="$REPO/cases/$FSI_RUN/run_experiment_overnight.log"
NP="${NP:-1}"

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"; }

coupled_ok() {
    local fluid="$REPO/cases/$TRANSIENT/fluid/log.pimpleFoam"
    [ -f "$fluid" ] || return 1
    grep -q 'FOAM FATAL' "$fluid" && return 1
    grep -qiE 'Floating point exception|FOAM exiting' "$fluid" && return 1
    grep -qE '^Time = 2[[:space:]]*$' "$fluid" || return 1
    grep -q 'patch A1 transient two-way FSI done' "$VALID_LOG" || return 1
    return 0
}

log "=== RESUME $TRANSIENT MODE=fsi REUSE_MESH=1 FLUID_PREWARM=0 ==="
"${COMPOSE[@]}" bash -lc "
    set -euo pipefail
    cd /simulation/$TRANSIENT
    chmod +x Allrun Allrun.sim4 scripts/*.sh
    MODE=fsi REUSE_MESH=1 FLUID_PREWARM=0 PREWARM_END_TIME=2 FSI_END_TIME=2 DELTA_T=0.05 ./Allrun
" >>"$VALID_LOG" 2>&1
rc=$?

if [ "$rc" -ne 0 ] || ! coupled_ok; then
    log "FAIL $TRANSIENT coupled FSI rc=$rc — not starting $FSI_RUN"
    tail -40 "$REPO/cases/$TRANSIENT/fluid/log.pimpleFoam" | tee -a "$MASTER_LOG" || true
    exit 1
fi
log "OK $TRANSIENT two-way FSI reached t=2"

log "=== bootstrap $FSI_RUN ==="
(
    cd "$REPO/cases/$FSI_RUN"
    chmod +x scripts/*.sh Allrun
    ./scripts/bootstrap_from_transient.sh
    ./scripts/seed_from_baseline.sh
    ./scripts/build_solid_a1.sh
) >>"$MASTER_LOG" 2>&1 || { log "FAIL bootstrap $FSI_RUN"; exit 1; }

log "===== EXPERIMENT $FSI_RUN t=5→30 ====="
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
    log "FAIL $FSI_RUN rc=$rc — see $EXPT_LOG"
    exit 1
fi
log "=== OVERNIGHT COMPLETE ==="
