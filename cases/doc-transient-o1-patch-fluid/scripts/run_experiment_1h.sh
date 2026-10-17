#!/bin/bash
# Experiment only (baseline must exist). Two-stage transient for stability; ~1 h target.
# Usage: ./scripts/run_experiment_1h.sh MESH_LEVEL [NP]
set -euo pipefail
cd "$(dirname "$0")/.."
MESH_LEVEL="${1:-M8}"
NP="${2:-4}"

stage_configs() {
    for f in U.experiment.1h controlDict.experiment.1h fvSolution.experiment.1h fvSchemes.experiment.1h; do
        base="${f%.1h}"
        case "$f" in
            U.*) cp -f "fluid/initial/$f" "fluid/initial/${base}" ;;
            *)   cp -f "fluid/system/$f" "fluid/system/${base}" ;;
        esac
    done
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
echo "=== experiment 1h: ${MESH_LEVEL} np=${NP} (stage1 0->2s dt=0.005, stage2->30s dt=0.02) ==="
if ! has_baseline_times; then
    echo "ERROR: seeded baseline missing — run ./scripts/seed_from_baseline.sh first" >&2
    exit 1
fi
if [ ! -d fluid/constant/polyMesh ]; then
    echo "ERROR: no polyMesh — run ./scripts/seed_from_baseline.sh first" >&2
    exit 1
fi
rm -rf fluid/0 fluid/processor*
MESH_LEVEL="$MESH_LEVEL" MODE=experiment REUSE_MESH=1 SKIP_SOLVE=1 ./Allrun
clean_prior_experiment_times

cp -f fluid/system/controlDict.experiment.1h fluid/system/controlDict
sed -i.bak -E \
    -e 's/^(startFrom[[:space:]]+).*/\1startTime;/' \
    -e 's/^(startTime[[:space:]]+).*/\10;/' \
    -e 's/^(endTime[[:space:]]+).*/\12;/' \
    -e 's/^(deltaT[[:space:]]+).*/\10.005;/' \
    -e 's/^(adjustTimeStep[[:space:]]+).*/\1no;/' \
    fluid/system/controlDict
rm -f fluid/system/controlDict.bak

echo "--- stage 1: t=0→2 s (dt=0.005) ---"
rm -f fluid/log.pimpleFoam
run_solver
grep -qE '^Time = 2[[:space:]]*$' fluid/log.pimpleFoam || { echo "ERROR: stage1 did not reach t=2" >&2; exit 1; }

clean_times_except '^2$'

sed -i.bak -E \
    -e 's/^(startFrom[[:space:]]+).*/\1startTime;/' \
    -e 's/^(startTime[[:space:]]+).*/\12;/' \
    -e 's/^(endTime[[:space:]]+).*/\130;/' \
    -e 's/^(deltaT[[:space:]]+).*/\10.02;/' \
    fluid/system/controlDict
rm -f fluid/system/controlDict.bak

echo "--- stage 2: t=2→30 s (dt=0.02) ---"
rm -f fluid/log.pimpleFoam
run_solver all
grep -qE '^Time = 30[[:space:]]*$' fluid/log.pimpleFoam || { echo "ERROR: stage2 did not reach t=30" >&2; exit 1; }

python3 scripts/extract_metrics.py --protocol ivi_acp || true
# archive first: plot_iop_acp.py prefers results/iop_probe_p.txt (stage1+stage2),
# else it falls back to iop_probe/0/p, which is stage1 only (0-2 s).
python3 scripts/archive_experiment_results.py || true
python3 scripts/plot_iop_acp.py || true
echo "=== experiment 1h OK (${MESH_LEVEL}) ==="
