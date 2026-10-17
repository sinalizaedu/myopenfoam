#!/bin/bash
# Copy shared case files from fsi-transient-a1-patch (first-time setup).
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="../fsi-transient-a1-patch"
if [ ! -d "$SRC" ]; then
  echo "ERROR: missing $SRC — run fsi-transient-a1-patch first" >&2
  exit 1
fi

echo "=== bootstrap $(basename "$PWD") from $SRC ==="
rsync -a \
  --exclude='fluid/[0-9]*' \
  --exclude='fluid/log.*' \
  --exclude='fluid/postProcessing' \
  --exclude='fluid/processor*' \
  --exclude='fluid/constant/polyMesh' \
  --exclude='solid/[0-9]*' \
  --exclude='solid/log.*' \
  --exclude='solid/postProcessing' \
  --exclude='solid/constant/polyMesh' \
  --exclude='solid/precice-profiling' \
  --exclude='precice-run' \
  --exclude='calibration' \
  --exclude='figures' \
  --exclude='solid_meshes' \
  --exclude='Allrun' \
  --exclude='README.md' \
  --exclude='scripts/bootstrap_from_transient.sh' \
  --exclude='scripts/seed_from_baseline.sh' \
  --exclude='scripts/run_experiment_fsi.sh' \
  --exclude='scripts/apply_fsi_experiment_wall.py' \
  --exclude='scripts/build_solid_a1.sh' \
  "$SRC/" ./

# Keep experiment-specific U / controlDict
mkdir -p fluid/initial fluid/system
cp -f fluid/initial/U.experiment.fsi fluid/initial/U.experiment
cp -f fluid/system/controlDict.experiment.fsi fluid/system/controlDict.experiment
cp -f fluid/system/controlDict.experiment.fsi fluid/system/controlDict.experiment.1h

for f in init_experiment_from_baseline.py extract_metrics.py plot_iop_acp.py \
         archive_experiment_results.py; do
  if [ ! -f "scripts/$f" ] && [ -f "../doc-run-o1-patch-fluid/scripts/$f" ]; then
    cp -f "../doc-run-o1-patch-fluid/scripts/$f" "scripts/$f"
  fi
done

touch fluid/O1.foam fluid/case.foam solid/solid.foam 2>/dev/null || true
echo "=== bootstrap done ==="
