#!/bin/bash
# Seed polyMesh + pimpleFoam equilibrated state from doc-transient-o1-patch-fluid.
# Snapshot is stored as fluid/1000 so it does not collide with experiment times 1–30.
set -euo pipefail
cd "$(dirname "$0")/.."
CASE_NAME="doc-run-o1-patch-fluid"
BASELINE="../doc-transient-o1-patch-fluid"
SEED_TIME=1000

if [ ! -d "$BASELINE/fluid/constant/polyMesh" ]; then
  echo "ERROR: missing $BASELINE/fluid/constant/polyMesh" >&2
  exit 1
fi

SRC="$(python3 - <<PY
from pathlib import Path
fluid = Path("$BASELINE/fluid")
best, best_t = None, -1.0
for p in fluid.iterdir():
    if not p.is_dir():
        continue
    try:
        t = float(p.name)
    except ValueError:
        continue
    if t <= 0:
        continue
    if not (p / "p").is_file() or not (p / "U").is_file():
        continue
    if t > best_t:
        best_t, best = t, p
if best is None:
    raise SystemExit("ERROR: no pimple snapshot (p,U) in $BASELINE/fluid")
print(best.name)
PY
)"

echo "=== seed $CASE_NAME from $BASELINE (src=$SRC -> fluid/${SEED_TIME}) ==="

rm -rf fluid/constant/polyMesh
mkdir -p fluid/constant
cp -a "$BASELINE/fluid/constant/polyMesh" fluid/constant/polyMesh

for d in fluid/[0-9]*; do
  [ -e "$d" ] || continue
  rm -rf "$d"
done

mkdir -p "fluid/${SEED_TIME}"
rsync -a --exclude='polyMesh' "$BASELINE/fluid/$SRC/" "fluid/${SEED_TIME}/"

mkdir -p calibration
if [ -f "$BASELINE/calibration/baseline_iop.yaml" ]; then
  sed "s/^case:.*/case: $CASE_NAME/" \
    "$BASELINE/calibration/baseline_iop.yaml" > calibration/baseline_iop.yaml
else
  echo "WARNING: no baseline_iop.yaml in $BASELINE/calibration" >&2
fi

if [ -f "$BASELINE/fluid/system/fvOptions" ]; then
  cp -f "$BASELINE/fluid/system/fvOptions" fluid/system/fvOptions
fi

mkdir -p fluid/0
touch fluid/O1.foam fluid/case.foam
echo "=== seed done: polyMesh + fluid/${SEED_TIME} + calibration/baseline_iop.yaml ==="
