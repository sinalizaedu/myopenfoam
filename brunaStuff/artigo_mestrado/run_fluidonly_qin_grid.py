#!/usr/bin/env python3
"""Track A: grade FLUIDO-SO DIRIGIDA POR VAZAO (Q_in prescrita).

Para cada (PIC alvo, d) prescreve Q_in = vazao calibrada (calib_results.json,
q_outlet) no inlet via flowRateInletVelocity e le a PIC media que EMERGE no
bulk do SAS. Objetivo: demonstrar que, com a Q_in calibrada, a PIC do bulk
fica sempre proxima do alvo (P ~ invariante e consistente) -- a direcao fisica
Q_in -> PIC, complementar a calibracao pressao-prescrita.

simpleFoam estacionario, lid Darcy d, malha de producao.

Uso:
    python3 brunaStuff/run_fluidonly_qin_grid.py            # grade 4x3
    python3 brunaStuff/run_fluidonly_qin_grid.py P1333_d1e15
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import refine_blockmesh  # noqa: E402
import calibrate_q_grid as cg  # noqa: E402
from check_compartmentalization import parse_cellzones, parse_internal_field  # noqa: E402

CASE = REPO / "cases" / "on-caso-1.2"
SRC_FLUID = CASE / "fluid"
ROOT = CASE / "_grid_qin_fluid"
CALIB = CASE / "_grid_calib" / "calib_results.json"
RHO = 1000.0

PICS = [1333.0, 2000.0, 3000.0, 3900.0]
DS = [1e15, 1e17, 1e19]


def dlabel(d: float) -> str:
    return f"{d:.0e}".replace("e+0", "e").replace("e+", "e")


def load_qin_map() -> dict:
    rows = json.loads(CALIB.read_text())
    m = {}
    for r in rows:
        m[(round(r["p_target_pa"]), round(math.log10(r["d"])))] = r["q_outlet"]
    return m


QMAP = load_qin_map()


def qin_for(p_pa: float, d: float) -> float:
    return QMAP[(round(p_pa), round(math.log10(d)))]


CONTROLDICT = """
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         400;
deltaT          1;
writeControl    timeStep;
writeInterval   400;
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
runTimeModifiable no;
"""

FVSOLUTION = """
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-08;
        relTol          0.05;
        smoother        GaussSeidel;
        nCellsInCoarsestLevel 20;
        maxIter         100;
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
    residualControl { p 1e-6; U 1e-7; }
}
relaxationFactors
{
    fields    { p   0.3; }
    equations { U   0.7; }
}
"""

FIELD_U = """
dimensions      [ 0 1 -1 0 0 0 0 ];
internalField   uniform ( 0 0 0 );
boundaryField
{{
    inlet           {{ type flowRateInletVelocity; volumetricFlowRate constant {q}; value uniform (0 0 3e-6); }}
    outlet_peri     {{ type pressureInletOutletVelocity; value uniform (0 0 0); }}
    fsi_pia         {{ type noSlip; }}
    fsi_dura        {{ type noSlip; }}
    lid_wall_inner  {{ type noSlip; }}
    lid_wall_outer  {{ type noSlip; }}
}}
"""

FIELD_P = """
dimensions      [ 0 2 -2 0 0 0 0 ];
internalField   uniform 0.0;
boundaryField
{
    inlet           { type zeroGradient; }
    outlet_peri     { type fixedValue; value uniform 0.0; }
    fsi_pia         { type zeroGradient; }
    fsi_dura        { type zeroGradient; }
    lid_wall_inner  { type zeroGradient; }
    lid_wall_outer  { type zeroGradient; }
}
"""


def setup(label: str, p_pa: float, d: float, q_in: float) -> Path:
    ldir = ROOT / label
    cg.sh(f"rm -rf {ldir}")
    (ldir / "system").mkdir(parents=True, exist_ok=True)
    (ldir / "constant").mkdir(parents=True, exist_ok=True)
    (ldir / "0").mkdir(parents=True, exist_ok=True)
    cg.write_dict(ldir / "system" / "controlDict", "dictionary", "controlDict", CONTROLDICT)
    cg.write_dict(ldir / "system" / "fvSchemes", "dictionary", "fvSchemes", cg.FVSCHEMES)
    cg.write_dict(ldir / "system" / "fvSolution", "dictionary", "fvSolution", FVSOLUTION)
    cg.write_dict(ldir / "system" / "fvOptions", "dictionary", "fvOptions",
                  cg.FVOPTIONS.format(d=f"{d:g}"))
    cg.write_dict(ldir / "constant" / "transportProperties", "dictionary",
                  "transportProperties", cg.TRANSPORT)
    cg.write_dict(ldir / "constant" / "turbulenceProperties", "dictionary",
                  "turbulenceProperties", cg.TURBULENCE)
    cg.write_dict(ldir / "0" / "p", "volScalarField", "p", FIELD_P)
    cg.write_dict(ldir / "0" / "U", "volVectorField", "U", FIELD_U.format(q=f"{q_in:g}"))
    refine_blockmesh.refine(str(SRC_FLUID / "system" / "blockMeshDict"),
                            str(ldir / "system" / "blockMeshDict"), 1, 1, 1)
    return ldir


def run_point(label: str, p_pa: float, d: float) -> dict:
    q_in = qin_for(p_pa, d)
    print(f"\n===== {label}: PIC_alvo={p_pa:.0f} Pa, d={d:g}, Q_in={q_in:.4e} m3/s =====")
    ldir = setup(label, p_pa, d, q_in)
    cg.docker(
        f"cd on-caso-1.2/_grid_qin_fluid/{label} && "
        "blockMesh > log.blockMesh 2>&1 && "
        "simpleFoam > log.simpleFoam 2>&1 ; tail -n 2 log.simpleFoam"
    )
    cz = parse_cellzones(ldir / "constant" / "polyMesh" / "cellZones")
    tdir = cg.last_time_dir(ldir)
    p_all = parse_internal_field(tdir / "p")
    sas = [p_all[i] for i in cz["sas"]]
    pp = [p_all[i] for i in cz["peri_porous"]]
    p_sas = sum(sas) / len(sas) * RHO
    p_sas_min, p_sas_max = min(sas) * RHO, max(sas) * RHO
    delta_lid = (sum(sas) / len(sas) - sum(pp) / len(pp)) * RHO
    out = dict(label=label, p_target_pa=p_pa, d=d, q_in=q_in,
               pic_bulk_pa=p_sas, pic_sas_min=p_sas_min, pic_sas_max=p_sas_max,
               pic_sas_spread=p_sas_max - p_sas_min, delta_p_lid=delta_lid,
               dev_pct=100 * (p_sas - p_pa) / p_pa)
    print(f"  -> PIC_bulk={p_sas:.1f} Pa (alvo {p_pa:.0f}, desvio {out['dev_pct']:+.2f}%), "
          f"spread no SAS={out['pic_sas_spread']:.2f} Pa, Dp_lid={delta_lid:.1f} Pa")
    return out


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    pts = [(f"P{int(p)}_d{dlabel(d)}", p, d) for p in PICS for d in DS]
    if arg:
        pts = [t for t in pts if t[0] == arg]
    results = []
    for label, p, d in pts:
        results.append(run_point(label, p, d))
    out = ROOT / "qin_grid_results.json"
    prev = json.loads(out.read_text()) if out.exists() else []
    prev = [x for x in prev if x["label"] not in {r["label"] for r in results}] + results
    out.write_text(json.dumps(prev, indent=2))
    print("\n===== RESUMO Track A (Q_in -> PIC emergente) =====")
    print(f"{'label':>14} {'alvo':>6} {'d':>6} {'Q_in':>11} {'PIC_bulk':>9} "
          f"{'desvio':>8} {'spread':>7}")
    for x in sorted(prev, key=lambda z: (z['p_target_pa'], z['d'])):
        print(f"{x['label']:>14} {x['p_target_pa']:>6.0f} {x['d']:>6.0g} "
              f"{x['q_in']:>11.3e} {x['pic_bulk_pa']:>9.1f} "
              f"{x['dev_pct']:>+7.2f}% {x['pic_sas_spread']:>7.2f}")
    print(f"\nresultados -> {out}")


if __name__ == "__main__":
    main()
