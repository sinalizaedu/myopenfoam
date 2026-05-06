#!/bin/bash
# pipe-lens-spring — postProcess.sh
# ──────────────────────────────────────────────────────────────────────────
# Run AFTER a completed Allrun to extract key metrics for the FSI checklist.
# Execute from inside the case directory (or the Docker container shell).
#
#   Key quantities to check:
#     |D|_max          — maximum displacement magnitude in solid (µm)
#     Force_x          — net axial force on disc (N)
#     Δp_lens          — upstream – downstream mean pressure on disc (Pa)
#     Q_zonula         — volumetric flow rate through outlet (m³/s)
#     phi@FSI ≈ 0      — impermeable disc check
# ──────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")"

LATEST_TIME=$(ls -1d solid/[0-9]* 2>/dev/null | grep -v "^solid/0$" | sort -n | tail -1)
if [ -z "$LATEST_TIME" ]; then
    echo "No time directories found in solid/ — run Allrun first."
    exit 1
fi
echo "Latest time: $LATEST_TIME"
echo ""

# ── |D|_max ─────────────────────────────────────────────────────────────
echo "=== |D|_max ==="
postProcess -case solid -func "mag(D)" -latestTime 2>&1 | grep -i "max\|magnitude" | tail -5 || \
    echo "  (run: postProcess -func 'mag(D)' -latestTime inside solid/)"

echo ""

# ── Forces on disc faces ─────────────────────────────────────────────────
echo "=== Force on disc faces ==="
postProcess -case fluid -func "forces(patches=(interface_upstream interface_downstream))" \
            -latestTime 2>&1 | grep -i "force\|Sum" | tail -10 || \
    echo "  (run: postProcess -func 'forces(...)' inside fluid/)"

echo ""

# ── Mean pressure on each face ───────────────────────────────────────────
echo "=== Pressure at FSI patches (last time step) ==="
grep -a "areaAverage.*interface_upstream"   fluid/log.pimpleFoam | tail -1 || true
grep -a "areaAverage.*interface_downstream" fluid/log.pimpleFoam | tail -1 || true
grep -a "pressureUpstream"   fluid/log.pimpleFoam | tail -3 || true
grep -a "pressureDownstream" fluid/log.pimpleFoam | tail -3 || true

echo ""

# ── Zonula flow (Q_zonula) ───────────────────────────────────────────────
echo "=== Q_zonula (outlet) — last 5 time steps ==="
grep -a "flowRateZonula" fluid/log.pimpleFoam | tail -5 || echo "  N/A"

echo ""

# ── Impermeable disc check ───────────────────────────────────────────────
echo "=== Impermeable check (phi at FSI patches, last 5 steps) ==="
echo "  interface_upstream:"
grep -a "flowRateLensUpstream"   fluid/log.pimpleFoam | tail -5 || echo "  N/A"
echo "  interface_downstream:"
grep -a "flowRateLensDownstream" fluid/log.pimpleFoam | tail -5 || echo "  N/A"

echo ""

# ── No fixedDisplacement ─────────────────────────────────────────────────
echo "=== Design constraint: no fixedDisplacement ==="
if grep -r "fixedDisplacement" solid/0/ solid/constant/ 2>/dev/null | grep -v "^Binary"; then
    echo "  [FAIL] fixedDisplacement found!"
else
    echo "  [OK]   No fixedDisplacement"
fi

echo ""
echo "=== Done. Load solid/$LATEST_TIME/D and fluid/$LATEST_TIME/p in ParaView. ==="
