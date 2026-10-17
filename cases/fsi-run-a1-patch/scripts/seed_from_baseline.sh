#!/bin/bash
# Seed polyMesh + equilibrated pimpleFoam state from fsi-transient-a1-patch prewarm.
# Snapshot stored as fluid/1000 (experiment clock starts at t=5).
set -euo pipefail
cd "$(dirname "$0")/.."
CASE_NAME="$(basename "$PWD")"
BASELINE="../fsi-transient-a1-patch"
SEED_TIME=1000

if [ ! -d "$BASELINE/fluid/constant/polyMesh" ]; then
  echo "ERROR: missing $BASELINE/fluid/constant/polyMesh" >&2
  exit 1
fi

SRC="$(python3 - <<PY
from pathlib import Path
fluid = Path("$BASELINE/fluid")
candidates = []
for p in fluid.iterdir():
    if not p.is_dir():
        continue
    try:
        t = float(p.name)
    except ValueError:
        continue
    if t <= 0:
        continue
    if (p / "p").is_file() and (p / "U").is_file():
        candidates.append((t, p))
if not candidates:
    # Fall back to fluid/0 after Allrun seeds U,p from prewarm into 0/.
    zero = fluid / "0"
    if (zero / "p").is_file() and (zero / "U").is_file():
        print("0")
    else:
        raise SystemExit("ERROR: no pimple snapshot (p,U) in $BASELINE/fluid")
else:
    pref = [c for c in candidates if abs(c[0] - 2.0) < 1e-6]
    if pref:
        print(pref[0][1].name)
    else:
        low = [c for c in candidates if c[0] < 50]
        pick = max(low or candidates, key=lambda x: x[0])
        print(pick[1].name)
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
fi

if [ -f "$BASELINE/fluid/system/fvOptions" ]; then
  cp -f "$BASELINE/fluid/system/fvOptions" fluid/system/fvOptions
fi

mkdir -p fluid/0
touch fluid/O1.foam fluid/case.foam
echo "=== seed done: polyMesh + fluid/${SEED_TIME} ==="
