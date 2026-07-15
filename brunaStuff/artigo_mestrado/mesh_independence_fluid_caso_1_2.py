#!/usr/bin/env python3
"""Estudo de INDEPENDENCIA DE MALHA do on-caso-1.2 (lado FLUIDO / OpenFOAM).

Analogo ao estudo do solido (mesh_independence_caso_1_2.py), mas para a malha do
LCR (SAS perioptico + tampa porosa Darcy). A grandeza de interesse (QoI) e' a
resposta HIDRODINAMICA do escoamento de LCR sob a carga de
compartimentalizacao do SANS (gradiente de pressao atraves do espaco
subaracnoideo com drenagem perineural obstruida).

A forma metodologicamente correta de avaliar independencia de malha e' VARIAR SO
A MALHA mantendo as condicoes de contorno e o coeficiente de Darcy FIXOS. No FSI
completo mudariam ao mesmo tempo a malha do fluido, o mapeamento RBF do preCICE e
o proprio carregamento (deslocamento da bainha) -> estudo confundido. Por isso
rodamos o FLUIDO STANDALONE (sem preCICE, sem CalculiX), com:

  - inlet (z=0, cisterna quiasmatica): p_kin = 1.333 (= 1333 Pa) fixedValue;
  - outlet_peri (z=30.5): p = 0 (referencia venosa episcleral);
  - paredes fsi_pia / fsi_dura: noSlip ESTACIONARIAS (malha fixa, sem mover);
  - lid_wall_inner / lid_wall_outer: noSlip;
  - zona peri_porous: Darcy d=1e16 m^-2 (regime compartimentalizado SANS),
    identica ao caso de producao (fvOptions explicitPorositySource);
  - solver: simpleFoam (estacionario, laminar; Re<<1 -> creeping flow).

Para cada nivel de refino f (fator inteiro multiplicativo das divisoes do
blockMesh, uniforme em r/theta/z):
  1. (host)      escreve um caso OpenFOAM standalone com blockMeshDict escalado;
  2. (container) blockMesh + simpleFoam;
  3. (host)      extrai as QoIs:
       - Q_dren  : vazao de drenagem no outlet_peri (sum(phi), m^3/s) -- a
                   metrica fisica central deste trabalho (drenagem de LCR);
       - U_max   : |U| maximo na zona SAS (m/s);
       - dp_lid  : queda de pressao no lid = <p>_SAS - <p>_peri (Pa).

Saidas:
  cases/on-caso-1.2/_mesh_indep_fluid/f<N>/   (casos standalone)
  cases/on-caso-1.2/_mesh_indep_fluid/results.json

Uso:
    python3 brunaStuff/mesh_independence_fluid_caso_1_2.py            # f=1,2,3,4
    python3 brunaStuff/mesh_independence_fluid_caso_1_2.py 1 2 3
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
ROOT = CASE / "_mesh_indep_fluid"

# Carga / regime fixos (iguais ao caso de producao)
P_INLET_KIN = 1.333    # p_kin no inlet = 1333 Pa / rho (cisterna quiasmatica)
D_DARCY = 1e16         # coeficiente de Darcy no lid (regime SANS compartimentalizado)
RHO = 1000.0           # kg/m^3 (LCR) -> converte p_kin para Pa

# Geometria do anel de drenagem (cross-check de vazao)
R_PIA = 1.55e-3
R_DURA = 2.35e-3
A_OUTLET = math.pi * (R_DURA ** 2 - R_PIA ** 2)


# ---------------------------------------------------------------------------
def sh(cmd: str, **kw):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=str(REPO), check=True, **kw)


def docker(inner: str):
    return sh(f'docker compose run --rm fsi bash -lc {json.dumps(inner)}')


# ---------------------------------------------------------------------------
# Dicionarios do caso standalone (escritos por nivel)
# ---------------------------------------------------------------------------
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
endTime         3000;
deltaT          1;
writeControl    timeStep;
writeInterval   3000;
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
    inletFlow
    {
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        regionType      patch;
        name            inlet;
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
        p   1e-6;
        U   1e-7;
    }
}

// SIMPLE classico com sub-relaxacao forte: converge de forma MONOTONA e evita
// o ciclo-limite que o SIMPLEC (consistent yes) sofre na malha fina (f3).
relaxationFactors
{
    fields
    {
        p   0.3;
    }
    equations
    {
        U   0.7;
    }
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

TRANSPORT = """
nu              nu  [0 2 -1 0 0 0 0] 1.0e-6;
transportModel  Newtonian;
"""

TURBULENCE = "simulationType laminar;\n"

FIELD_P = """
dimensions      [ 0 2 -2 0 0 0 0 ];
internalField   uniform 0.0;
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
    // Escoamento dirigido por pressao (p fixo nas duas extremidades): U
    // extrapolado (zeroGradient) e' mais estavel que pressureInletOutletVelocity,
    // que oscila na malha fina (BC alterna inlet/outlet com fluxo quase nulo).
    inlet           { type zeroGradient; }
    outlet_peri     { type zeroGradient; }
    fsi_pia         { type noSlip; }
    fsi_dura        { type noSlip; }
    lid_wall_inner  { type noSlip; }
    lid_wall_outer  { type noSlip; }
}
"""


def setup_level(f: int) -> Path:
    ldir = ROOT / f"f{f}"
    # limpa restos de runs anteriores
    sh(f'rm -rf {ldir}')
    (ldir / "system").mkdir(parents=True, exist_ok=True)
    (ldir / "constant").mkdir(parents=True, exist_ok=True)
    (ldir / "0").mkdir(parents=True, exist_ok=True)

    write_dict(ldir / "system" / "controlDict", "dictionary", "controlDict", CONTROLDICT)
    write_dict(ldir / "system" / "fvSchemes", "dictionary", "fvSchemes", FVSCHEMES)
    write_dict(ldir / "system" / "fvSolution", "dictionary", "fvSolution", FVSOLUTION)
    write_dict(ldir / "system" / "fvOptions", "dictionary", "fvOptions",
               FVOPTIONS.format(d=f"{D_DARCY:g}"))
    write_dict(ldir / "constant" / "transportProperties", "dictionary",
               "transportProperties", TRANSPORT)
    write_dict(ldir / "constant" / "turbulenceProperties", "dictionary",
               "turbulenceProperties", TURBULENCE)
    write_dict(ldir / "0" / "p", "volScalarField", "p",
               FIELD_P.format(p_in=f"{P_INLET_KIN:g}"))
    write_dict(ldir / "0" / "U", "volVectorField", "U", FIELD_U)

    # blockMeshDict escalado por f (uniforme r/theta/z)
    refine_blockmesh.refine(
        str(SRC_FLUID / "system" / "blockMeshDict"),
        str(ldir / "system" / "blockMeshDict"), f, f, f)
    return ldir


# ---------------------------------------------------------------------------
def last_time_dir(ldir: Path) -> Path:
    times = []
    for d in ldir.iterdir():
        if d.is_dir():
            try:
                times.append((float(d.name), d))
            except ValueError:
                pass
    if not times:
        raise RuntimeError(f"nenhum diretorio de tempo em {ldir}")
    return max(times, key=lambda x: x[0])[1]


def parse_flow_dat(dat: Path) -> float:
    """Ultima linha de surfaceFieldValue.dat -> sum(phi) [m^3/s]."""
    if not dat.exists():
        return float("nan")
    last = None
    for ln in dat.read_text().splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        last = s
    if last is None:
        return float("nan")
    return float(last.split()[-1])


def n_iter_from_log(log: Path) -> int:
    txt = log.read_text()
    times = re.findall(r"^Time = (\d+)", txt, re.MULTILINE)
    return int(times[-1]) if times else -1


def run_level(f: int) -> dict:
    print(f"\n===== NIVEL f{f} =====")
    ldir = setup_level(f)

    docker(
        f"cd on-caso-1.2/_mesh_indep_fluid/f{f} && "
        "blockMesh > log.blockMesh 2>&1 && "
        "simpleFoam > log.simpleFoam 2>&1 ; tail -n 3 log.simpleFoam"
    )

    # malha
    cz = parse_cellzones(ldir / "constant" / "polyMesh" / "cellZones")
    n_cells = sum(len(v) for v in cz.values())

    # campos no ultimo tempo
    tdir = last_time_dir(ldir)
    p_all = parse_internal_field(tdir / "p")
    U_all = parse_vector_field(tdir / "U")

    sas_ids = cz["sas"]
    pp_ids = cz["peri_porous"]
    p_sas = sum(p_all[i] for i in sas_ids) / len(sas_ids)
    p_pp = sum(p_all[i] for i in pp_ids) / len(pp_ids)
    dp_lid_pa = (p_sas - p_pp) * RHO
    mag_sas = [(U_all[i][0] ** 2 + U_all[i][1] ** 2 + U_all[i][2] ** 2) ** 0.5
               for i in sas_ids]
    u_max_sas = max(mag_sas)
    u_mean_sas = sum(mag_sas) / len(mag_sas)
    uz_pp_mean = sum(U_all[i][2] for i in pp_ids) / len(pp_ids)

    # vazao de drenagem (sum phi no outlet); cross-check via Uz*A no lid
    q_outlet = parse_flow_dat(
        ldir / "postProcessing" / "outletFlow" / "0" / "surfaceFieldValue.dat")
    q_lid_xc = uz_pp_mean * A_OUTLET

    n_iter = n_iter_from_log(ldir / "log.simpleFoam")
    out = dict(
        level=f"f{f}", factor=f, n_cells=n_cells, n_iter=n_iter,
        q_outlet=q_outlet, q_lid_xcheck=q_lid_xc,
        u_max_sas=u_max_sas, u_mean_sas=u_mean_sas, dp_lid_pa=dp_lid_pa,
        p_sas_pa=p_sas * RHO, p_pp_pa=p_pp * RHO,
    )
    print(f"  nCells={n_cells}  iters={n_iter}  Q_outlet={q_outlet:.4e} m3/s  "
          f"|U|_max_SAS={u_max_sas:.4e} m/s  dp_lid={dp_lid_pa:.2f} Pa")
    return out


def main():
    factors = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4]
    ROOT.mkdir(parents=True, exist_ok=True)
    results_path = ROOT / "results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else []
    for f in factors:
        r = run_level(f)
        results = [x for x in results if x["level"] != r["level"]] + [r]
        results.sort(key=lambda x: x["factor"])
        results_path.write_text(json.dumps(results, indent=2))

    print("\n===== RESUMO =====")
    print(f"{'nivel':>6} {'nCells':>8} {'Q_outlet(m3/s)':>16} "
          f"{'|U|max_SAS(m/s)':>16} {'dp_lid(Pa)':>12}")
    for x in results:
        print(f"{x['level']:>6} {x['n_cells']:>8} {x['q_outlet']:>16.4e} "
              f"{x['u_max_sas']:>16.4e} {x['dp_lid_pa']:>12.2f}")
    print(f"\nresultados -> {results_path}")


if __name__ == "__main__":
    main()
