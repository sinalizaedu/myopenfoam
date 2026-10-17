#!/bin/bash
# Experiment only. Seed is doc-transient (fluid/1000) — do not re-run the passive
# 0–5 s hold. IVI tables already start at t=5, so the solver clock starts there.
# Usage: ./scripts/run_experiment_1h.sh MESH_LEVEL [NP]
# Env: START_TIME=5 (default), SKIP_INIT=1 to keep existing fields (no Allrun).
set -euo pipefail
cd "$(dirname "$0")/.."
MESH_LEVEL="${1:-M8}"
NP="${2:-4}"
START_TIME="${START_TIME:-5}"
SETTLE_START="${SETTLE_START:-4.8}"
SKIP_INIT="${SKIP_INIT:-0}"
STAGE1_END="$(python3 -c "print(int(float('${START_TIME}') + 2))")"

stage_configs() {
    for f in U.experiment.1h controlDict.experiment.1h fvSolution.experiment.1h fvSchemes.experiment.1h; do
        base="${f%.1h}"
        case "$f" in
            U.*) cp -f "fluid/initial/$f" "fluid/initial/${base}" ;;
            *)   cp -f "fluid/system/$f" "fluid/system/${base}" ;;
        esac
    done
    # Allrun copies U.experiment.robin over U.experiment — both must stay Robin.
    cp -f fluid/initial/U.experiment.1h fluid/initial/U.experiment.robin
    if ! grep -q 'codedFixedValue' fluid/initial/U.experiment.robin \
       || ! grep -q 'scleraRobinBC' fluid/initial/U.experiment.robin; then
        echo "ERROR: wall BC is not codedFixedValue scleraRobinBC" >&2
        exit 1
    fi
}

run_solver() {
    local reconstruct_mode="${1:-latest}"
    (
        cd fluid
        rm -rf processor*
        if [ "$NP" -le 1 ]; then
            pimpleFoam 2>&1 | tee -a log.pimpleFoam
        else
            decomposePar -force 2>&1 | tee -a log.decomposePar
            mpirun -np "$NP" --oversubscribe pimpleFoam -parallel 2>&1 | tee -a log.pimpleFoam
            if [ "$reconstruct_mode" = "all" ]; then
                reconstructPar 2>&1 | tee -a log.reconstructPar
            else
                reconstructPar -latestTime 2>&1 | tee -a log.reconstructPar
            fi
        fi
    )
}

clean_times_except() {
    local keep_re="$1"
    find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\.[0-9]+' -exec rm -rf {} + 2>/dev/null || true
    for d in fluid/[0-9]*; do
        [ -e "$d" ] || continue
        base="$(basename "$d")"
        [[ "$base" =~ $keep_re ]] && continue
        # Keep SIMPLE baseline dumps (50, 100, … 400); do not treat them as experiment times.
        if [[ "$base" =~ ^[0-9]+$ ]] && [ "$base" -ge 50 ]; then
            continue
        fi
        rm -rf "$d"
    done
}

# Remove prior experiment time dirs only; keep baseline steady times (e.g. 320).
clean_prior_experiment_times() {
    find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\.[0-9]+' -exec rm -rf {} + 2>/dev/null || true
}

has_baseline_times() {
    for d in fluid/[0-9]*; do
        [ -e "$d" ] || continue
        base="$(basename "$d")"
        [[ "$base" == "0" ]] && continue
        if [[ "$base" =~ ^[0-9]+$ ]] && [ "$base" -ge 50 ]; then
            return 0
        fi
    done
    return 1
}

stage_configs
echo "=== experiment 1h: ${MESH_LEVEL} np=${NP} settle=${SETTLE_START}->${START_TIME} noSlip, then Robin ${START_TIME}->30 ==="
if ! has_baseline_times; then
    echo "ERROR: seeded baseline missing — run ./scripts/seed_from_baseline.sh first" >&2
    exit 1
fi
if [ ! -d fluid/constant/polyMesh ]; then
    echo "ERROR: no polyMesh — run ./scripts/seed_from_baseline.sh first" >&2
    exit 1
fi
if [ "$SKIP_INIT" != "1" ]; then
    rm -rf fluid/0 fluid/processor*
    # Init wall as noSlip so phi/U match the transient snapshot, then swap Robin at t=5.
    cp -f fluid/initial/U.experiment.settle fluid/initial/U.experiment
    MESH_LEVEL="$MESH_LEVEL" MODE=experiment REUSE_MESH=1 SKIP_SOLVE=1 ./Allrun.sim4
    cp -f fluid/initial/U.experiment.1h fluid/initial/U.experiment
    cp -f fluid/initial/U.experiment.1h fluid/initial/U.experiment.robin
    clean_prior_experiment_times
    rm -rf "fluid/${SETTLE_START}" "fluid/${START_TIME}"
    cp -a fluid/0 "fluid/${SETTLE_START}"
fi
if [ ! -d "fluid/${SETTLE_START}" ]; then
    echo "ERROR: missing fluid/${SETTLE_START} (seed fields for BC settle)" >&2
    exit 1
fi

cp -f fluid/system/controlDict.experiment.1h fluid/system/controlDict
sed -i.bak -E \
    -e 's/^(startFrom[[:space:]]+).*/\1startTime;/' \
    -e "s/^(startTime[[:space:]]+).*/\\1${SETTLE_START};/" \
    -e "s/^(endTime[[:space:]]+).*/\\1${START_TIME};/" \
    -e 's/^(deltaT[[:space:]]+).*/\10.005;/' \
    -e 's/^(adjustTimeStep[[:space:]]+).*/\1no;/' \
    -e 's/^(writeInterval[[:space:]]+).*/\10.2;/' \
    fluid/system/controlDict
rm -f fluid/system/controlDict.bak

echo "--- settle: t=${SETTLE_START}→${START_TIME} s wall=noSlip Q_IVI=0 ---"
rm -f fluid/log.pimpleFoam
run_solver
grep -qE "^Time = ${START_TIME}[[:space:]]*$" fluid/log.pimpleFoam || { echo "ERROR: settle did not reach t=${START_TIME}" >&2; exit 1; }
if [ ! -f "fluid/${START_TIME}/U" ]; then
    echo "ERROR: settle did not write fluid/${START_TIME} (need writeInterval that hits t=${START_TIME})" >&2
    exit 1
fi

python3 scripts/apply_robin_wall.py "fluid/${START_TIME}/U"
if ! grep -q 'scleraRobinBC' "fluid/${START_TIME}/U"; then
    echo "ERROR: Robin wall not applied at t=${START_TIME}" >&2
    exit 1
fi

cp -f fluid/system/controlDict.experiment.1h fluid/system/controlDict
sed -i.bak -E \
    -e 's/^(startFrom[[:space:]]+).*/\1startTime;/' \
    -e "s/^(startTime[[:space:]]+).*/\\1${START_TIME};/" \
    -e "s/^(endTime[[:space:]]+).*/\\1${STAGE1_END};/" \
    -e 's/^(deltaT[[:space:]]+).*/\10.005;/' \
    -e 's/^(adjustTimeStep[[:space:]]+).*/\1no;/' \
    fluid/system/controlDict
rm -f fluid/system/controlDict.bak

echo "--- stage 1: t=${START_TIME}→${STAGE1_END} s wall=Robin IVI ramp ---"
rm -f fluid/log.pimpleFoam
run_solver
grep -qE "^Time = ${STAGE1_END}[[:space:]]*$" fluid/log.pimpleFoam || { echo "ERROR: stage1 did not reach t=${STAGE1_END}" >&2; exit 1; }

clean_times_except "^${STAGE1_END}$"

sed -i.bak -E \
    -e 's/^(startFrom[[:space:]]+).*/\1startTime;/' \
    -e "s/^(startTime[[:space:]]+).*/\\1${STAGE1_END};/" \
    -e 's/^(endTime[[:space:]]+).*/\130;/' \
    -e 's/^(deltaT[[:space:]]+).*/\10.02;/' \
    fluid/system/controlDict
rm -f fluid/system/controlDict.bak

echo "--- stage 2: t=${STAGE1_END}→30 s (dt=0.02) ---"
rm -f fluid/log.pimpleFoam
run_solver all
grep -qE '^Time = 30[[:space:]]*$' fluid/log.pimpleFoam || { echo "ERROR: stage2 did not reach t=30" >&2; exit 1; }

python3 scripts/extract_metrics.py --protocol ivi_acp || true
# archive first: plot_iop_acp.py prefers results/iop_probe_p.txt (stage1+stage2),
# else it falls back to iop_probe/0/p, which is stage1 only (0-2 s).
python3 scripts/archive_experiment_results.py || true
python3 scripts/plot_iop_acp.py || true
echo "=== experiment 1h OK (${MESH_LEVEL}) ==="
