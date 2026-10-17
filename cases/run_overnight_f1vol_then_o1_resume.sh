#!/bin/bash
# Resume overnight after parent died: wait for in-flight O1 patch Docker job,
# then run O1 volume. Idempotent if patch already finished.
set -euo pipefail

NP="${NP:-4}"
POLL_SEC="${POLL_SEC:-60}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$REPO/docker-compose.yaml" run --rm --user ubuntu fsi)
MASTER_LOG="$REPO/cases/run_overnight_f1vol_then_o1_runs.log"
PATCH_RUN="doc-run-o1-patch-fluid"
VOLUME_RUN="doc-run-o1-volume-fluid"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

case_running() {
    local case_dir="$1" id cmd
    while read -r id; do
        [ -n "$id" ] || continue
        cmd="$(docker inspect --format '{{join .Config.Cmd " "}}' "$id" 2>/dev/null || true)"
        [[ "$cmd" == *"/simulation/${case_dir}"* ]] && return 0
    done < <(docker ps -q)
    return 1
}

experiment_ok() {
    local case_dir="$1"
    local logf="$REPO/cases/$case_dir/fluid/log.pimpleFoam"
    grep -qE '^Time = 30[[:space:]]*$' "$logf" 2>/dev/null \
        && ! grep -q 'FOAM FATAL' "$logf" 2>/dev/null
}

patch_latest_time() {
    # Prefer transient experiment times (fractional or processor*) over seeded baseline ints.
    python3 - <<PY || echo "?"
from pathlib import Path
fluid = Path("$REPO/cases/$PATCH_RUN/fluid")
frac, proc, seeded = [], [], []
for p in fluid.iterdir():
    if not p.is_dir():
        continue
    try:
        t = float(p.name)
    except ValueError:
        continue
    if t <= 0:
        continue
    if "." in p.name:
        frac.append(t)
    elif p.name.isdigit() and int(p.name) < 50:
        frac.append(t)
    else:
        seeded.append(t)
for root in fluid.glob("processor*"):
    for p in root.iterdir():
        if not p.is_dir():
            continue
        try:
            proc.append(float(p.name))
        except ValueError:
            pass
if proc:
    print(f"{max(proc):g}")
elif frac:
    print(f"{max(frac):g}")
elif seeded:
    print(f"{max(seeded):g}")
else:
    print("0")
PY
}

log "=== RESUME overnight: wait patch → then volume (np=$NP) ==="

if experiment_ok "$PATCH_RUN"; then
    log "Patch already OK (t=30)"
elif case_running "$PATCH_RUN"; then
    log "Patch Docker still running — polling"
    set +e
    while case_running "$PATCH_RUN"; do
        lt="$(patch_latest_time 2>/dev/null || echo '?')"
        log "Patch in flight (latest~${lt}s)"
        sleep "$POLL_SEC"
    done
    set -e
    log "Patch container exited"
else
    log "No patch container and not at t=30 — launching patch experiment"
    (
        cd "$REPO/cases/$PATCH_RUN"
        ./scripts/seed_from_baseline.sh || true
    ) >>"$REPO/cases/$PATCH_RUN/run_experiment_overnight.log" 2>&1
    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$PATCH_RUN
        chmod +x scripts/*.sh Allrun
        if [ -x scripts/run_experiment_until_done.sh ]; then
            ./scripts/run_experiment_until_done.sh O1 $NP
        else
            ./scripts/run_experiment_1h.sh O1 $NP
        fi
    " >>"$REPO/cases/$PATCH_RUN/run_experiment_overnight.log" 2>&1 || true
fi

if experiment_ok "$PATCH_RUN"; then
    log "OK $PATCH_RUN"
else
    log "WARN $PATCH_RUN not at t=30 — trying until_done"
    if [ -x "$REPO/cases/$PATCH_RUN/scripts/run_experiment_until_done.sh" ]; then
        "${COMPOSE[@]}" bash -lc "
            set -euo pipefail
            cd /simulation/$PATCH_RUN
            ./scripts/run_experiment_until_done.sh O1 $NP
        " >>"$REPO/cases/$PATCH_RUN/run_experiment_overnight.log" 2>&1 || true
    fi
    if experiment_ok "$PATCH_RUN"; then
        log "OK $PATCH_RUN via until_done"
    else
        log "FAIL $PATCH_RUN — continuing to volume anyway"
    fi
fi

if experiment_ok "$VOLUME_RUN"; then
    log "Volume already OK — skip"
elif case_running "$VOLUME_RUN"; then
    log "Volume already running — wait"
    while case_running "$VOLUME_RUN"; do
        sleep "$POLL_SEC"
    done
else
    log "===== O1 EXPERIMENT $VOLUME_RUN np=$NP ====="
    (
        cd "$REPO/cases/$VOLUME_RUN"
        ./scripts/seed_from_baseline.sh
    ) >>"$REPO/cases/$VOLUME_RUN/run_experiment_overnight.log" 2>&1
    "${COMPOSE[@]}" bash -lc "
        set -euo pipefail
        cd /simulation/$VOLUME_RUN
        chmod +x scripts/*.sh Allrun
        ./scripts/run_experiment_1h.sh O1 $NP
    " >>"$REPO/cases/$VOLUME_RUN/run_experiment_overnight.log" 2>&1 || true
    if experiment_ok "$VOLUME_RUN"; then
        log "OK $VOLUME_RUN"
    else
        log "FAIL $VOLUME_RUN"
    fi
fi

log "=== RESUME overnight COMPLETE ==="
