# shellcheck shell=bash
# Sourced by A1–E1 Allrun.mesh.  Works on the host repo and in the docker
# mount (cases/ → /simulation).
CASE="$(cd ../.. && pwd)"
if [ -f "$CASE/../../brunaStuff/gen_o1_solid_bmd.py" ]; then
    BRUNA="$CASE/../../brunaStuff"
elif [ -f /opt/brunaStuff/gen_o1_solid_bmd.py ]; then
    BRUNA=/opt/brunaStuff
else
    echo "ERROR: cannot find brunaStuff" >&2
    return 1 2>/dev/null || exit 1
fi
GEN="$BRUNA/gen_o1_solid_bmd.py"
EXP="$BRUNA/o1_solid_export.py"
GEN_GMSH="$BRUNA/gen_o1_solid_gmsh_transfinite.py"
FLUID_MESH="${FLUID_MESH:-$CASE/fluid/constant/polyMesh}"
B1_CASE="${B1_CASE:-$CASE/solid_meshes/B1}"
B2_CASE="${B2_CASE:-$CASE/solid_meshes/B2}"
FLUID="${FLUID:-$CASE/fluid}"
export PYTHONPATH="$BRUNA${PYTHONPATH:+:$PYTHONPATH}"
