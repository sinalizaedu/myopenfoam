#!/bin/bash
# Archive fluid/ into runs/<MESH>/ so ParaView can open without overwrite.
# Usage: ./scripts/archive_mesh_run.sh MESH_LEVEL
#   creates: runs/<MESH>/  (OpenFOAM case = copy of fluid/)
#            runs/<MESH>/<MESH>.foam
set -euo pipefail
cd "$(dirname "$0")/.."
MESH="${1:?MESH_LEVEL required (e.g. O1 F1)}"
DEST="runs/${MESH}"
mkdir -p "$DEST"

echo "=== archive fluid/ → ${DEST}/ (mesh=${MESH}) ==="
# Prefer rsync; fall back to cp
if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
        --exclude 'processor*' \
        --exclude 'VTK/' \
        --exclude 'dynamicCode/' \
        --exclude 'codeStream/' \
        --exclude '*.foam' \
        fluid/ "${DEST}/"
else
    rm -rf "${DEST}.tmp"
    mkdir -p "${DEST}.tmp"
    # copy essentials
    cp -a fluid/constant "${DEST}.tmp/" 2>/dev/null || true
    cp -a fluid/system "${DEST}.tmp/" 2>/dev/null || true
    cp -a fluid/0 "${DEST}.tmp/" 2>/dev/null || true
    for d in fluid/[0-9]*; do
        [ -d "$d" ] || continue
        cp -a "$d" "${DEST}.tmp/"
    done
    # postProcessing / logs helpful for probes
    [ -d fluid/postProcessing ] && cp -a fluid/postProcessing "${DEST}.tmp/" || true
    rm -rf "$DEST"
    mv "${DEST}.tmp" "$DEST"
fi

touch "${DEST}/${MESH}.foam"
# also keep a convenience link name
touch "${DEST}/case.foam"

# stamp
{
    echo "mesh: ${MESH}"
    echo "archived_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "source: $(pwd)/fluid"
} > "${DEST}/ARCHIVE.txt"

echo "ParaView: open $(pwd)/${DEST}/${MESH}.foam"
ls -la "${DEST}/${MESH}.foam"
