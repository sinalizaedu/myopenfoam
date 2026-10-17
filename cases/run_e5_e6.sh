#!/bin/bash
# E5 (WP1.3 Yeoh pretension) + E6 (WP1.4/1.5 Yeoh pilots)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"

echo "=== E5 — WP1.3 pretension (Yeoh) ==="
python3 "$ROOT/wp1.3/scripts/run_e5_yeoh.py"

echo "=== E6 — WP1.4 (14 biometry cases) ==="
python3 "$ROOT/wp1.4/scripts/run_pilot_yeoh.py"

echo "=== E6 — WP1.5 (human + rabbit) ==="
python3 "$ROOT/wp1.5/scripts/run_pilot_yeoh.py"

echo "=== E5+E6 complete ==="
echo "  E5: $ROOT/wp1.3/output_e5_yeoh/RESULTS.md"
echo "  WP1.4: $ROOT/wp1.4/output_pilot_yeoh/RESULTS.md"
echo "  WP1.5: $ROOT/wp1.5/output_pilot_yeoh/RESULTS.md"
