#!/bin/bash
# Serial queue: wait for running O1-patch experiment, then run O1-volume.
# Transients are already done. Never start a second fsi container while one is up.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$REPO/cases/run_o1_serial_queue.log"
PATCH_CID="${PATCH_CID:-9b240fd8e4cc}"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$LOG"; }

fsi_running() {
    docker ps --format '{{.Names}} {{.Command}}' | grep -F 'myopenfoam-fsi-run' >/dev/null 2>&1
}

log "queue start: wait patch cid=$PATCH_CID then volume"
log "checklist: transient-o1-patch DONE | transient-o1-volume DONE | run-o1-patch WAIT | run-o1-volume QUEUED"

if docker ps -q --filter "id=$PATCH_CID" | grep -q .; then
    log "waiting for patch container $PATCH_CID"
    docker wait "$PATCH_CID" | tee -a "$LOG"
else
    log "patch container already gone — check whether experiment finished"
fi

PATCH_LOG="$REPO/cases/doc-run-o1-patch-fluid/fluid/log.pimpleFoam"
if [ -f "$PATCH_LOG" ] && grep -qE '^Time = 30[[:space:]]*$' "$PATCH_LOG" && ! grep -q 'FOAM FATAL' "$PATCH_LOG"; then
    log "run-o1-patch DONE (t=30, no FOAM FATAL)"
else
    log "ERROR: run-o1-patch did not finish cleanly — not starting volume"
    exit 1
fi

if fsi_running; then
    log "ERROR: another fsi container is still up — abort volume"
    docker ps --format '{{.Names}} {{.Status}} {{.Command}}' | tee -a "$LOG"
    exit 1
fi

log "re-seed + run o1-volume (single job)"
"$REPO/cases/doc-run-o1-volume-fluid/scripts/seed_from_baseline.sh" | tee -a "$LOG"

"${COMPOSE[@]}" bash -lc \
  'cd /simulation/doc-run-o1-volume-fluid && MASS_SOURCE_SOLVER=/simulation/_bin/pimpleFoamMassSource ./scripts/run_experiment_1h.sh O1 4' \
  | tee -a "$LOG"

VOL_LOG="$REPO/cases/doc-run-o1-volume-fluid/fluid/log.pimpleFoam"
if [ -f "$VOL_LOG" ] && grep -qE '^Time = 30[[:space:]]*$' "$VOL_LOG" && ! grep -q 'FOAM FATAL' "$VOL_LOG"; then
    log "run-o1-volume DONE"
    log "checklist: transient-o1-patch DONE | transient-o1-volume DONE | run-o1-patch DONE | run-o1-volume DONE"
    exit 0
fi
log "ERROR: run-o1-volume did not finish cleanly"
exit 1
