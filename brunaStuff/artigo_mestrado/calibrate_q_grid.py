#!/usr/bin/env python3
"""Fase 1 (FLUIDO-SO) da grade de compartimentalizacao do on-caso-1.2.

Para cada celula (P_alvo, d) calibra a vazao Q que sustenta a pressao alvo,
rodando simpleFoam ESTACIONARIO standalone com o lid poroso Darcy (mesma malha
de producao). Modo PRESSAO-PRESCRITA: impoe p_inlet = P_alvo e le o Q de
drenagem no outlet -- que e' exatamente o Q a prescrever no FSI para chegar
naquela pressao (p = kappa*d*Q, com kappa fixado pela geometria do lid).

Uso:
    python3 brunaStuff/calibrate_q_grid.py          # 2 pontos extremos
    python3 brunaStuff/calibrate_q_grid.py --full   # grade 4x3 completa
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import refine_blockmesh  # noqa: E402
from check_compartmentalization import parse_cellzones, parse_internal_field  # noqa: E402
from check_velocity import parse_vector_field  # noqa: E402

CASE = REPO / "cases" / "on-caso-1.2"
SRC_FLUID = CASE / "fluid"
ROOT = CASE / "_grid_calib"

RHO = 1000.0          # kg/m^3 (LCR) -> p_kin (m^2/s^2) * RHO = Pa
NU = 1.1e-6           # m^2/s  (mu=1.1e-3 Pa.s, valor de Sadeghi Namaghi et al. 2026)

R_PIA = 1.55e-3
R_DURA = 2.35e-3
A_OUTLET = math.pi * (R_DURA ** 2 - R_PIA ** 2)

# Pontos da grade: (label, P_alvo[Pa], d[m^-2])
POINTS_2 = [
    ("P1333_d1e15", 1333.0, 1e15),
    ("P3900_d1e19", 3900.0, 1e19),
]
POINTS_FULL = [
    (f"P{int(p)}_d{d:g}", p, d)
    for p in (1333.0, 2000.0, 3000.0, 3900.0)
    for d in (1e15, 1e17, 1e19)
]


def sh(cmd: str, **kw):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=str(REPO), check=True, **kw)


def docker(inner: str):
    return sh(f'docker compose run --rm fsi bash -lc {json.dumps(inner)}')


FOAM_HEADER = (
    "FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n"
    "    object {obj};\n}}\n"
)


def write_dict(path: Path, cls: str, obj: str, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(FOAM_HEADER.format(cls=cls, obj=obj) + body)


CONTROLDICT = """
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         5000;
deltaT          1;
writeControl    timeStep;
writeInterval   5000;
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
runTimeModifiable no;

functions
{
    outletFlow
    {
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        regionType      patch;
        name            outlet_peri;
        operation       sum;
        fields          (phi);
        writeFields     false;
        writeControl    timeStep;
        writeInterval   1;
        log             false;
    }
}
"""

FVSCHEMES = """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
"""

FVSOLUTION = """
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-09;
        relTol          0.01;
        smoother        GaussSeidel;
        nCellsInCoarsestLevel 20;
    }
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-09;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 2;
    consistent      no;
    residualControl
    {
        p   1e-7;
        U   1e-8;
    }
}

relaxationFactors
{
    fields    { p   0.3; }
    equations { U   0.7; }
}
"""

FVOPTIONS = """
peri_porous
{{
    type            explicitPorositySource;
    active          true;
    explicitPorositySourceCoeffs
    {{
        selectionMode   cellZone;
        cellZone        peri_porous;
        type            DarcyForchheimer;
        DarcyForchheimerCoeffs
        {{
            d   d [0 -2 0 0 0 0 0] ({d} {d} {d});
            f   f [0 -1 0 0 0 0 0] (0 0 0);
            coordinateSystem
            {{
                type    cartesian;
                origin  (0 0 0);
                coordinateRotation {{ type axesRotation; e1 (1 0 0); e2 (0 1 0); }}
            }}
        }}
    }}
}}
"""

TRANSPORT = f"""
nu              nu  [0 2 -1 0 0 0 0] {NU:g};
transportModel  Newtonian;
"""

TURBULENCE = "simulationType laminar;\n"

FIELD_P = """
dimensions      [ 0 2 -2 0 0 0 0 ];
internalField   uniform {p_in};
boundaryField
{{
    inlet           {{ type fixedValue; value uniform {p_in}; }}
    outlet_peri     {{ type fixedValue; value uniform 0.0; }}
    fsi_pia         {{ type zeroGradient; }}
    fsi_dura        {{ type zeroGradient; }}
    lid_wall_inner  {{ type zeroGradient; }}
    lid_wall_outer  {{ type zeroGradient; }}
}}
"""

FIELD_U = """
dimensions      [ 0 1 -1 0 0 0 0 ];
internalField   uniform ( 0 0 0 );
boundaryField
{
    inlet           { type zeroGradient; }
    outlet_peri     { type zeroGradient; }
    fsi_pia         { type noSlip; }
    fsi_dura        { type noSlip; }
    lid_wall_inner  { type noSlip; }
    lid_wall_outer  { type noSlip; }
}
"""


def setup(label: str, p_pa: float, d: float) -> Path:
    ldir = ROOT / label
    sh(f'rm -rf {ldir}')
    (ldir / "system").mkdir(parents=True, exist_ok=True)
    (ldir / "constant").mkdir(parents=True, exist_ok=True)
    (ldir / "0").mkdir(parents=True, exist_ok=True)
    p_kin = p_pa / RHO
    write_dict(ldir / "system" / "controlDict", "dictionary", "controlDict", CONTROLDICT)
    write_dict(ldir / "system" / "fvSchemes", "dictionary", "fvSchemes", FVSCHEMES)
    write_dict(ldir / "system" / "fvSolution", "dictionary", "fvSolution", FVSOLUTION)
    write_dict(ldir / "system" / "fvOptions", "dictionary", "fvOptions",
               FVOPTIONS.format(d=f"{d:g}"))
    write_dict(ldir / "constant" / "transportProperties", "dictionary",
               "transportProperties", TRANSPORT)
    write_dict(ldir / "constant" / "turbulenceProperties", "dictionary",
               "turbulenceProperties", TURBULENCE)
    write_dict(ldir / "0" / "p", "volScalarField", "p", FIELD_P.format(p_in=f"{p_kin:g}"))
    write_dict(ldir / "0" / "U", "volVectorField", "U", FIELD_U)
    # malha de producao (f=1)
    refine_blockmesh.refine(
        str(SRC_FLUID / "system" / "blockMeshDict"),
        str(ldir / "system" / "blockMeshDict"), 1, 1, 1)
    return ldir


def last_time_dir(ldir: Path) -> Path:
    times = [(float(d.name), d) for d in ldir.iterdir()
             if d.is_dir() and re.fullmatch(r"\d+", d.name)]
    return max(times, key=lambda x: x[0])[1]


def parse_flow_dat(dat: Path) -> float:
    if not dat.exists():
        return float("nan")
    last = None
    for ln in dat.read_text().splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            last = s
    return float(last.split()[-1]) if last else float("nan")


def run_point(label: str, p_pa: float, d: float) -> dict:
    print(f"\n===== {label}: P_alvo={p_pa:.0f} Pa, d={d:g} =====")
    ldir = setup(label, p_pa, d)
    docker(
        f"cd on-caso-1.2/_grid_calib/{label} && "
        "blockMesh > log.blockMesh 2>&1 && "
        "simpleFoam > log.simpleFoam 2>&1 ; tail -n 3 log.simpleFoam"
    )
    cz = parse_cellzones(ldir / "constant" / "polyMesh" / "cellZones")
    tdir = last_time_dir(ldir)
    p_all = parse_internal_field(tdir / "p")
    U_all = parse_vector_field(tdir / "U")
    sas_ids, pp_ids = cz["sas"], cz["peri_porous"]
    p_sas = sum(p_all[i] for i in sas_ids) / len(sas_ids) * RHO
    q_out = parse_flow_dat(ldir / "postProcessing" / "outletFlow" / "0" / "surfaceFieldValue.dat")
    times = re.findall(r"^Time = (\d+)", (ldir / "log.simpleFoam").read_text(), re.MULTILINE)
    n_iter = int(times[-1]) if times else -1
    out = dict(label=label, p_target_pa=p_pa, d=d, p_sas_pa=p_sas,
               q_outlet=q_out, n_iter=n_iter)
    print(f"  iters={n_iter}  p_SAS={p_sas:.1f} Pa (alvo {p_pa:.0f})  "
          f"Q_dren={q_out:.4e} m3/s")
    return out


def main():
    pts = POINTS_FULL if "--full" in sys.argv else POINTS_2
    ROOT.mkdir(parents=True, exist_ok=True)
    res_path = ROOT / "calib_results.json"
    results = json.loads(res_path.read_text()) if res_path.exists() else []
    for label, p, d in pts:
        r = run_point(label, p, d)
        results = [x for x in results if x["label"] != label] + [r]
        res_path.write_text(json.dumps(results, indent=2))
    print("\n===== RESUMO CALIBRACAO =====")
    print(f"{'label':>14} {'P_alvo':>8} {'d':>8} {'p_SAS(Pa)':>10} {'Q(m3/s)':>13}")
    for x in sorted(results, key=lambda z: (z['p_target_pa'], z['d'])):
        print(f"{x['label']:>14} {x['p_target_pa']:>8.0f} {x['d']:>8.0g} "
              f"{x['p_sas_pa']:>10.1f} {x['q_outlet']:>13.4e}")
    print(f"\nresultados -> {res_path}")


if __name__ == "__main__":
    main()
