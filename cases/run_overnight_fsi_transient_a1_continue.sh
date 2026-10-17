#!/bin/bash
# Wait for the in-flight fsi-transient-a1-patch Allrun container, then
# bootstrap + run fsi-run-a1-patch if coupled FSI reached endTime.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
TRANSIENT="fsi-transient-a1-patch"
FSI_RUN="fsi-run-a1-patch"
MASTER_LOG="$REPO/cases/run_overnight_fsi_transient_a1.log"
VALID_LOG="$REPO/cases/$TRANSIENT/run_overnight_fsi.log"
EXPT_LOG="$REPO/cases/$FSI_RUN/run_experiment_overnight.log"
CONTAINER="${WAIT_CONTAINER:-myopenfoam-fsi-run-715c96191f05}"
NP="${NP:-1}"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

coupled_ok() {
    local fluid="$REPO/cases/$TRANSIENT/fluid/log.pimpleFoam"
    local solid="$REPO/cases/$TRANSIENT/solid/log.solids4Foam"
    [ -f "$fluid" ] || return 1
    [ -f "$solid" ] || return 1
    grep -q 'FOAM FATAL' "$fluid" "$solid" && return 1
    grep -qiE 'Floating point exception|FOAM exiting' "$fluid" "$solid" && return 1
    grep -qE '^Time = 2[[:space:]]*$' "$fluid" || return 1
    return 0
}

log "=== WAIT: $CONTAINER then continue $FSI_RUN ==="
while docker ps -q --filter "name=^${CONTAINER}$" | grep -q .; do
    last="$(grep -E '^Time = ' "$REPO/cases/$TRANSIENT/fluid/log.pimpleFoam.prewarm" 2>/dev/null | tail -1 || true)"
    fsi_t="$(grep -E '^Time = ' "$REPO/cases/$TRANSIENT/fluid/log.pimpleFoam" 2>/dev/null | tail -1 || true)"
    log "still running ($last / fsi $fsi_t)"
    sleep 60
done

log "container $CONTAINER gone — checking coupled FSI"
if ! coupled_ok; then
    log "FAIL $TRANSIENT coupled FSI did not reach t=2 — not starting $FSI_RUN"
    tail -40 "$REPO/cases/$TRANSIENT/fluid/log.pimpleFoam" 2>/dev/null | tee -a "$MASTER_LOG" || true
    tail -20 "$REPO/cases/$TRANSIENT/solid/log.solids4Foam" 2>/dev/null | tee -a "$MASTER_LOG" || true
    rmdir /tmp/fsi_transient_a1_overnight.lock 2>/dev/null || true
    exit 1
fi
log "OK $TRANSIENT two-way FSI reached t=2"

log "=== bootstrap $FSI_RUN from $TRANSIENT ==="
(
    cd "$REPO/cases/$FSI_RUN"
    chmod +x scripts/*.sh Allrun 2>/dev/null || true
    ./scripts/bootstrap_from_transient.sh
    ./scripts/seed_from_baseline.sh
    ./scripts/build_solid_a1.sh
) >>"$MASTER_LOG" 2>&1 || {
    log "FAIL bootstrap/seed/solid $FSI_RUN"
    rmdir /tmp/fsi_transient_a1_overnight.lock 2>/dev/null || true
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
    rmdir /tmp/fsi_transient_a1_overnight.lock 2>/dev/null || true
    exit 1
fi

log "=== OVERNIGHT COMPLETE ==="
log "validation: $VALID_LOG"
log "experiment: $EXPT_LOG"
rmdir /tmp/fsi_transient_a1_overnight.lock 2>/dev/null || true
