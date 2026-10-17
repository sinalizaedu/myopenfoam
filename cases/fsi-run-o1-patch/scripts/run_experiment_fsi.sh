#!/bin/bash
# FSI experiment: rigid settle 4.8→5 s, then two-way preCICE IVI/ACP t=5→30.
# Usage: ./scripts/run_experiment_fsi.sh MESH_LEVEL [NP]
set -euo pipefail
cd "$(dirname "$0")/.."
MESH_LEVEL="${1:-O1}"
NP="${2:-1}"
START_TIME="${START_TIME:-5}"
SETTLE_START="${SETTLE_START:-4.8}"
SKIP_INIT="${SKIP_INIT:-0}"
STAGE1_END="$(python3 -c "print(int(float('${START_TIME}') + 2))")"
REPO_ROOT="$(cd ../.. && pwd)"
VERIFY="$REPO_ROOT/brunaStuff/verify_o1_fsi_conformal.py"
[ -f "$VERIFY" ] || VERIFY="/opt/brunaStuff/verify_o1_fsi_conformal.py"

patch_control() {
    local start="$1" end="$2" dt="$3" write_ivl="${4:-1}"
    python3 - "$start" "$end" "$dt" "$write_ivl" <<'PY'
from pathlib import Path
import re, sys
start, end, dt, write_ivl = sys.argv[1:5]
for name in ("fluid/system/controlDict", "solid/system/controlDict"):
    p = Path(name)
    text = p.read_text()
    text = re.sub(r"(?m)^startFrom\s+[^;]+;", "startFrom       startTime;", text)
    text = re.sub(r"(?m)^startTime\s+[^;]+;", f"startTime       {start};", text)
    text = re.sub(r"(?m)^endTime\s+[^;]+;", f"endTime         {end};", text)
    text = re.sub(r"(?m)^deltaT\s+[^;]+;", f"deltaT          {dt};", text)
    if "fluid/" in name:
        text = re.sub(r"(?m)^writeInterval\s+[^;]+;", f"writeInterval   {write_ivl};", text)
    p.write_text(text)
coupled = float(end) - float(start)
p = Path("precice-config.xml")
text = p.read_text()
text = re.sub(r'<max-time value="[^"]+"', f'<max-time value="{coupled:g}"', text)
text = re.sub(r'<time-window-size value="[^"]+"', f'<time-window-size value="{dt}"', text)
p.write_text(text)
PY
}

prepare_fsi_fields() {
    local tdir="$1"
    local fresh="${2:-0}"
    cp -f fluid/constant/dynamicMeshDict.fsi fluid/constant/dynamicMeshDict
    cp -f fluid/system/fvSchemes.fsi fluid/system/fvSchemes
    cp -f fluid/system/fvSolution.fsi fluid/system/fvSolution
    cp -f fluid/system/controlDict.experiment.fsi fluid/system/controlDict
    cp -f fluid/initial/pointDisplacement "fluid/${tdir}/pointDisplacement"
    if [ "$fresh" = "1" ]; then
        cp -f fluid/initial/U.experiment.fsi "fluid/${tdir}/U"
    fi
    python3 scripts/apply_fsi_experiment_wall.py "fluid/${tdir}/U"
}

reset_solid_at() {
    local tdir="$1"
    rm -rf solid/[0-9]* solid/postProcessing solid/processor* solid/precice-profiling 2>/dev/null || true
    mkdir -p "solid/${tdir}"
    cp -f solid/initial/D "solid/${tdir}/D"
    cp -f solid/initial/solidForce "solid/${tdir}/solidForce"
}

run_rigid() {
    rm -f fluid/constant/dynamicMeshDict
    cp -f fluid/system/fvSchemes.experiment.1h fluid/system/fvSchemes
    cp -f fluid/system/fvSolution.experiment.1h fluid/system/fvSolution
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

run_fsi_coupled() {
    local start="$1"
    rm -rf precice-run
    find fluid -maxdepth 1 -type d -name '[0-9]*' ! -name '0' ! -name "$start" \
        -exec rm -rf {} + 2>/dev/null || true
    find solid -maxdepth 1 -type d -name '[0-9]*' ! -name "$start" \
        -exec rm -rf {} + 2>/dev/null || true
    (
        cd solid
        solids4Foam 2>&1 | tee -a log.solids4Foam
    ) &
    solid_pid=$!
    trap 'kill "$solid_pid" 2>/dev/null || true' EXIT
    sleep 5
    (
        cd fluid
        if [ "$NP" -le 1 ]; then
            pimpleFoam 2>&1 | tee -a log.pimpleFoam
        else
            decomposePar -force 2>&1 | tee -a log.decomposePar
            mpirun -np "$NP" --oversubscribe pimpleFoam -parallel 2>&1 | tee -a log.pimpleFoam
            reconstructPar -latestTime 2>&1 | tee -a log.reconstructPar
        fi
    )
    wait "$solid_pid" || true
    trap - EXIT
}

clean_prior_experiment_times() {
    find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\.[0-9]+' -exec rm -rf {} + 2>/dev/null || true
}

has_seed() {
    [ -d "fluid/${SEED_TIME:-1000}" ] || [ -d fluid/1000 ]
}

SEED_TIME=1000
echo "=== FSI experiment: ${MESH_LEVEL} np=${NP} settle ${SETTLE_START}->${START_TIME}, coupled ${START_TIME}->30 ==="

if [ ! -d fluid/constant/polyMesh ] || ! has_seed; then
    echo "ERROR: seed first — ./scripts/seed_from_baseline.sh" >&2
    exit 1
fi
if [ ! -d solid/constant/polyMesh ]; then
    echo "ERROR: solid polyMesh missing — run blockMesh on solid first" >&2
    exit 1
fi
python3 "$VERIFY" fluid/constant/polyMesh solid/constant/polyMesh --centroid-tol 1e-6

# Copy analysis scripts from doc-run if missing
for f in init_experiment_from_baseline.py extract_metrics.py plot_iop_acp.py archive_experiment_results.py sync_field_boundaries.py; do
    if [ ! -f "scripts/$f" ] && [ -f "../doc-run-o1-patch-fluid/scripts/$f" ]; then
        cp -f "../doc-run-o1-patch-fluid/scripts/$f" "scripts/$f"
    fi
done

if [ "$SKIP_INIT" != "1" ]; then
    rm -rf fluid/0 fluid/processor*
    cp -f fluid/initial/U.experiment.settle fluid/initial/U.experiment
    MESH_LEVEL="$MESH_LEVEL" MODE=experiment REUSE_MESH=1 SKIP_SOLVE=1 ./Allrun.sim4
    cp -f fluid/initial/U.experiment.fsi fluid/initial/U.experiment
    clean_prior_experiment_times
    rm -rf "fluid/${SETTLE_START}" "fluid/${START_TIME}"
    cp -a fluid/0 "fluid/${SETTLE_START}"
fi

if [ ! -d "fluid/${SETTLE_START}" ]; then
    echo "ERROR: missing fluid/${SETTLE_START}" >&2
    exit 1
fi

cp -f fluid/system/controlDict.experiment.1h fluid/system/controlDict 2>/dev/null \
    || cp -f fluid/system/controlDict.experiment fluid/system/controlDict
patch_control "$SETTLE_START" "$START_TIME" 0.005 0.2

echo "--- settle: rigid t=${SETTLE_START}→${START_TIME} ---"
rm -f fluid/log.pimpleFoam
run_rigid
grep -qE "^Time = ${START_TIME}[[:space:]]*$" fluid/log.pimpleFoam || {
    echo "ERROR: settle did not reach t=${START_TIME}" >&2; exit 1
}

prepare_fsi_fields "$START_TIME" 1
reset_solid_at "$START_TIME"
patch_control "$START_TIME" "$STAGE1_END" 0.005 0.2

echo "--- FSI stage 1: t=${START_TIME}→${STAGE1_END} (IVI ramp) ---"
rm -f fluid/log.pimpleFoam solid/log.solids4Foam
run_fsi_coupled "$START_TIME"
grep -qE "^Time = ${STAGE1_END}[[:space:]]*$" fluid/log.pimpleFoam || {
    echo "ERROR: FSI stage1 did not reach t=${STAGE1_END}" >&2; exit 1
}

prepare_fsi_fields "$STAGE1_END" 0
patch_control "$STAGE1_END" 30 0.02 1

echo "--- FSI stage 2: t=${STAGE1_END}→30 ---"
rm -f fluid/log.pimpleFoam solid/log.solids4Foam
run_fsi_coupled "$STAGE1_END"
grep -qE '^Time = 30[[:space:]]*$' fluid/log.pimpleFoam || {
    echo "ERROR: FSI stage2 did not reach t=30" >&2; exit 1
}

python3 scripts/extract_metrics.py --protocol ivi_acp 2>/dev/null || true
python3 scripts/archive_experiment_results.py 2>/dev/null || true
python3 scripts/plot_iop_acp.py 2>/dev/null || true
echo "=== FSI experiment OK (${MESH_LEVEL}) ==="
