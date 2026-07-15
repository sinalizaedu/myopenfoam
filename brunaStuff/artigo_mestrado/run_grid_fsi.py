#!/usr/bin/env python3
"""Fase 2 (FSI ACOPLADO) da grade de compartimentalizacao do on-caso-1.2.

Para cada ponto (P_alvo, d, material) monta um caso FSI independente em
cases/on-caso-1.2/_grid/<label>/, parametrizando:
  - fvOptions          : coeficiente de Darcy d no lid poroso
  - 0/p                : PIC em RAMPA de 0 -> P_alvo (modo pressao-prescrita,
                         mais estavel; o Q fisico vem da Fase 1 / fluido-so)
  - transportProperties: nu = 1.1e-6 (mu = 1.1e-3 Pa.s, Sadeghi Namaghi 2026)
  - solid/main.inp     : material LINEAR (*ELASTIC) ou NEO-HOOKEAN
                         (*HYPERELASTIC, NEO HOOKE) -- mesmas E/nu por zona
  - precice-config.xml : max-time = n_windows ; controlDict endTime idem

Roda solids4Foam (fluido) + ccx_preCICE (solido) em paralelo via preCICE no
container, e extrai a distensao radial MAXIMA da dura e da pia (corpo do nervo,
nao a ponta engastada).

Uso:
    python3 brunaStuff/run_grid_fsi.py P1333_d1e15 linear
    python3 brunaStuff/run_grid_fsi.py P3900_d1e19 neohooke
    python3 brunaStuff/run_grid_fsi.py --all          # os 4 (2 pts x 2 mats)
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CASE = REPO / "cases" / "on-caso-1.2"
SRC = CASE
GRID = CASE / "_grid"
RHO = 1000.0
NU = 1.1e-6  # mu = 1.1e-3 Pa.s (Namaghi)

# Pontos: label -> (P_alvo[Pa], d[m^-2], n_windows_linear, n_windows_neohooke)
# Curva de distensao em d=1e15 (4 pressoes) + 3900/d1e19 p/ checar independencia
# de d. Janelas crescem com a pressao (rampa gentil p/ convergencia do NH).
POINTS = {
    "P1333_d1e15": (1333.0, 1e15, 4, 6),
    "P1333_d1e17": (1333.0, 1e17, 4, 6),
    "P1333_d1e19": (1333.0, 1e19, 4, 6),
    "P2000_d1e15": (2000.0, 1e15, 4, 7),
    "P2000_d1e17": (2000.0, 1e17, 4, 7),
    "P2000_d1e19": (2000.0, 1e19, 4, 7),
    "P3000_d1e15": (3000.0, 1e15, 5, 8),
    "P3000_d1e17": (3000.0, 1e17, 5, 8),
    "P3000_d1e19": (3000.0, 1e19, 5, 8),
    "P3800_d1e15": (3800.0, 1e15, 5, 10),
    "P3800_d1e17": (3800.0, 1e17, 5, 10),
    "P3800_d1e19": (3800.0, 1e19, 5, 10),
    # legado (independencia de d ja verificada): 3900
    "P3900_d1e15": (3900.0, 1e15, 5, 10),
    "P3900_d1e19": (3900.0, 1e19, 5, 10),
}
MATS = ("linear", "neohooke")

# Zonas anatomicas (name, E[Pa], nu, rho)
# LINEAR: tabela documentada do Caso 1 (artigo, Tab. mat-linear), nu=0.45
#         (nu=0.45 evita travamento volumetrico em C3D8 linear).
ZONES_LINEAR = [
    ("ON_MAT", 30000.0, 0.45, 1000.0),
    ("PIA_MAT", 3.0e6, 0.45, 1100.0),
    ("DURA_MAT", 3.0e6, 0.45, 1100.0),
    ("LC_MAT", 0.4e6, 0.45, 1100.0),
    ("SCLERA_PERI_MAT", 5.0e6, 0.45, 1400.0),
    ("SCLERA_RING_MAT", 5.0e6, 0.45, 1400.0),
    ("GLOBO_MAT", 5.0e6, 0.45, 1400.0),
]
# NEO-HOOKE: alinhado aos casos on-caso-2/on-caso-3 (NEO HOOKE compressivel,
#   nu=0.49 quase-incompressivel; C10=E/[4(1+nu)], D1=6(1-2nu)/E). E por zona
#   identico aos casos 2/3 (LC=0.3 MPa, esclera/globo=3 MPa). Dura mantida
#   Neo-Hookean ISOTROPICA (nao a ortotropica Holzapfel dos casos 2/3) para
#   nao bloquear a distensao radial, que e' a QoI deste caso de FSI.
ZONES_NH = [
    ("ON_MAT", 30000.0, 0.49, 1000.0),
    ("PIA_MAT", 3.0e6, 0.49, 1100.0),
    ("DURA_MAT", 3.0e6, 0.49, 1100.0),
    ("LC_MAT", 0.3e6, 0.49, 1100.0),
    ("SCLERA_PERI_MAT", 3.0e6, 0.49, 1400.0),
    ("SCLERA_RING_MAT", 3.0e6, 0.49, 1400.0),
    ("GLOBO_MAT", 3.0e6, 0.49, 1400.0),
]


def sh(cmd: str, check=True, **kw):
    print(f"  $ {cmd}", flush=True)
    return subprocess.run(cmd, shell=True, cwd=str(REPO), check=check, **kw)


# ---------------------------------------------------------------------------
# Material section (gera *ELASTIC ou *HYPERELASTIC, NEO HOOKE por zona)
# ---------------------------------------------------------------------------
def material_blocks(mat: str) -> str:
    zones = ZONES_LINEAR if mat == "linear" else ZONES_NH
    out = []
    for name, E, nu, rho in zones:
        out.append(f"*MATERIAL, NAME={name}")
        out.append(f"** E={E:.6g} Pa, nu={nu}")
        if mat == "linear":
            out.append("*ELASTIC")
            out.append(f"{E:.6g}, {nu}")
        else:  # neohooke (casos 2/3): C10 = E/(4(1+nu)) ; D1 = 6(1-2nu)/E
            c10 = E / (4.0 * (1.0 + nu))
            d1 = 6.0 * (1.0 - 2.0 * nu) / E
            out.append("*HYPERELASTIC, NEO HOOKE")
            out.append(f"{c10:.6g}, {d1:.6g}")
        out.append("*DENSITY")
        out.append(f"{rho}")
        out.append("")
    return "\n".join(out)


def patch_main_inp(text: str, mat: str) -> str:
    """Substitui o bloco de materiais (entre o 1o *MATERIAL e *SOLID SECTION)."""
    lines = text.splitlines()
    i0 = next(i for i, l in enumerate(lines) if l.strip().startswith("*MATERIAL"))
    i1 = next(i for i, l in enumerate(lines) if l.strip().startswith("*SOLID SECTION"))
    new = lines[:i0] + material_blocks(mat).splitlines() + ["", lines[i1].rstrip()] + \
        ["" ] + lines[i1 + 1:]
    return "\n".join(new) + "\n"


def patch_step_time(text: str, nwin: int) -> str:
    """Ajusta *STATIC para tempo total = nwin (janelas de 1.0 s)."""
    # linha apos *STATIC: "1.0, 6.0" -> "1.0, <nwin>.0"
    return re.sub(r"(?m)^\s*1\.0\s*,\s*[\d.]+\s*$", f"1.0, {float(nwin)}", text)


# ---------------------------------------------------------------------------
def p_ramp_table(p_target_pa: float, nwin: int) -> str:
    """Tabela de p_kin (m^2/s^2) em rampa 0 -> alvo ao longo de nwin janelas."""
    p_kin = p_target_pa / RHO
    rows = "\n".join(f"            ({t}   {p_kin * t / nwin:.6g})" for t in range(nwin + 1))
    return rows


FIELD_P_TMPL = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}}
dimensions      [ 0 2 -2 0 0 0 0 ];
internalField   uniform 0.0;
boundaryField
{{
    inlet
    {{
        type            uniformFixedValue;
        uniformValue    table
        (
{rows}
        );
    }}
    outlet_peri      {{ type fixedValue; value uniform 0.0; }}
    fsi_pia          {{ type zeroGradient; }}
    fsi_dura         {{ type zeroGradient; }}
    lid_wall_inner   {{ type zeroGradient; }}
    lid_wall_outer   {{ type zeroGradient; }}
}}
"""


def prepare(label: str, mat: str) -> Path:
    p_pa, d, nlin, nnh = POINTS[label]
    nwin = nlin if mat == "linear" else nnh
    pdir = GRID / f"{label}_{mat}"
    print(f"\n=== PREPARE {label}_{mat}: P={p_pa:.0f} Pa, d={d:g}, mat={mat}, "
          f"nwin={nwin} ===")
    sh(f"rm -rf {pdir}")
    (pdir / "fluid" / "0").mkdir(parents=True, exist_ok=True)
    (pdir / "fluid" / "constant").mkdir(parents=True, exist_ok=True)
    (pdir / "fluid" / "system").mkdir(parents=True, exist_ok=True)
    (pdir / "solid").mkdir(parents=True, exist_ok=True)

    # ---- fluid/0 (so os campos de entrada) ----
    for f in ("U", "pointDisplacement"):
        shutil.copy(SRC / "fluid" / "0" / f, pdir / "fluid" / "0" / f)
    shutil.copytree(SRC / "fluid" / "0" / "uniform", pdir / "fluid" / "0" / "uniform")
    (pdir / "fluid" / "0" / "p").write_text(
        FIELD_P_TMPL.format(rows=p_ramp_table(p_pa, nwin)))

    # ---- fluid/constant (inclui polyMesh) ----
    for f in ("dynamicMeshDict", "fluidProperties", "g", "physicsProperties",
              "thermodynamicProperties", "turbulenceProperties"):
        shutil.copy(SRC / "fluid" / "constant" / f, pdir / "fluid" / "constant" / f)
    shutil.copytree(SRC / "fluid" / "constant" / "polyMesh",
                    pdir / "fluid" / "constant" / "polyMesh")
    # transportProperties com nu de Namaghi
    (pdir / "fluid" / "constant" / "transportProperties").write_text(
        "FoamFile\n{\n    version 2.0; format ascii; class dictionary;\n"
        "    object transportProperties;\n}\n"
        f"nu  nu  [0 2 -1 0 0 0 0] {NU:g};\n"
        f"rho rho [1 -3 0 0 0 0 0] {RHO:g};\n"
        f"mu  mu  [1 -1 -1 0 0 0 0] {NU*RHO:g};\n"
        "transportModel  Newtonian;\n")

    # ---- fluid/system ----
    for f in ("blockMeshDict", "fvSchemes", "fvSolution", "preciceDict"):
        shutil.copy(SRC / "fluid" / "system" / f, pdir / "fluid" / "system" / f)
    # controlDict: endTime = nwin
    cd = (SRC / "fluid" / "system" / "controlDict").read_text()
    cd = re.sub(r"(?m)^endTime\s+[\d.]+\s*;", f"endTime         {float(nwin)};", cd)
    (pdir / "fluid" / "system" / "controlDict").write_text(cd)
    # fvOptions: coeficiente d
    fo = (SRC / "fluid" / "system" / "fvOptions").read_text()
    fo = re.sub(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\([^)]*\)",
                f"d   d [0 -2 0 0 0 0 0] ({d:g} {d:g} {d:g})", fo)
    (pdir / "fluid" / "system" / "fvOptions").write_text(fo)

    # ---- solid ----
    for f in ("all.msh", "all.nam", "winkler.inp", "config.yml"):
        shutil.copy(SRC / "solid" / f, pdir / "solid" / f)
    mi = (SRC / "solid" / "main.inp").read_text()
    mi = patch_main_inp(mi, mat)
    mi = patch_step_time(mi, nwin)
    (pdir / "solid" / "main.inp").write_text(mi)

    # ---- precice-config.xml: max-time = nwin ----
    pc = (SRC / "precice-config.xml").read_text()
    pc = re.sub(r'<max-time value="[\d.]+"\s*/>',
                f'<max-time value="{float(nwin)}" />', pc)
    (pdir / "precice-config.xml").write_text(pc)
    return pdir


# ---------------------------------------------------------------------------
RUN_INNER = (
    "set -e; cd on-caso-1.2/_grid/{tag}; "
    "rm -rf precice-run precice-Fluid-* precice-Solid-* 2>/dev/null || true; "
    "( cd fluid && rm -rf [1-9]* processor* log.* && solids4Foam > log.solids4Foam 2>&1 ) & PF=$!; "
    "( cd solid && rm -f main.frd main.dat main.cvg main.sta && "
    "ccx_preCICE -i main -precice-participant Solid > log.ccx 2>&1 ) & PS=$!; "
    "RF=0; RS=0; wait $PF || RF=$?; wait $PS || RS=$?; "
    "echo \"RC_FLUID=$RF RC_SOLID=$RS\"; "
    "tail -n 2 solid/log.ccx; tail -n 2 fluid/log.solids4Foam"
)


def run(label: str, mat: str):
    tag = f"{label}_{mat}"
    print(f"\n=== RUN {tag} (acoplado preCICE) ===", flush=True)
    inner = RUN_INNER.format(tag=tag)
    sh(f'docker compose run --rm fsi bash -lc {json.dumps(inner)}', check=False)


# ---------------------------------------------------------------------------
# Extracao da distensao radial maxima (corpo do nervo, nao a ponta z=30)
# ---------------------------------------------------------------------------
def load_coords(msh: Path) -> dict:
    coords, mode = {}, None
    for line in msh.read_text().splitlines():
        s = line.strip()
        if s.startswith("*"):
            mode = "node" if s.upper().startswith("*NODE") else None
            continue
        if mode == "node" and s and not s.startswith("**"):
            p = [x.strip() for x in s.split(",")]
            if len(p) >= 4:
                try:
                    coords[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
                except ValueError:
                    pass
    return coords


def last_disp_block(dat: Path, setname: str) -> dict:
    lines = dat.read_text().splitlines()
    idxs = [i for i, l in enumerate(lines) if "displacements" in l and setname in l]
    if not idxs:
        return {}
    data = {}
    for l in lines[idxs[-1] + 1:]:
        ss = l.split()
        if len(ss) >= 4:
            try:
                data[int(ss[0])] = (float(ss[1]), float(ss[2]), float(ss[3]))
            except ValueError:
                break
        elif not l.strip() and data:
            break
    return data


def extract(label: str, mat: str) -> dict:
    tag = f"{label}_{mat}"
    pdir = GRID / tag
    coords = load_coords(pdir / "solid" / "all.msh")
    dat = pdir / "solid" / "main.dat"
    res = {"tag": tag, "p_target_pa": POINTS[label][0], "d": POINTS[label][1], "mat": mat}
    if not dat.exists():
        res["status"] = "NO_DAT (rodada falhou?)"
        return res
    for setname, key in (("NFSI_DURA", "dura"), ("NFSI_PIA", "pia")):
        d = last_disp_block(dat, setname)
        urs = []
        for n, (ux, uy, uz) in d.items():
            if n not in coords:
                continue
            x, y, z = coords[n]
            r = math.hypot(x, y)
            if r > 0:
                urs.append((x * ux + y * uy) / r)
        if urs:
            res[f"{key}_ur_max_um"] = max(urs, key=abs) * 1e6
    res["status"] = "OK"
    return res


# ---------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    GRID.mkdir(parents=True, exist_ok=True)
    if "--all" in args:
        jobs = [(lab, m) for lab in POINTS for m in MATS]
    elif len(args) >= 2:
        jobs = [(args[0], args[1])]
    else:
        print(__doc__)
        return
    results = []
    for label, mat in jobs:
        prepare(label, mat)
        run(label, mat)
        r = extract(label, mat)
        results.append(r)
        print(f"  -> {r}", flush=True)
    out = GRID / "grid_fsi_results.json"
    prev = json.loads(out.read_text()) if out.exists() else []
    prev = [x for x in prev if x["tag"] not in {r["tag"] for r in results}] + results
    out.write_text(json.dumps(prev, indent=2))
    print("\n===== RESUMO FSI =====")
    print(f"{'tag':>22} {'P(Pa)':>7} {'mat':>9} {'dura_ur(um)':>12} {'pia_ur(um)':>12} {'status':>10}")
    for x in sorted(prev, key=lambda z: (z['p_target_pa'], z['mat'])):
        print(f"{x['tag']:>22} {x['p_target_pa']:>7.0f} {x['mat']:>9} "
              f"{x.get('dura_ur_max_um', float('nan')):>12.3f} "
              f"{x.get('pia_ur_max_um', float('nan')):>12.3f} {x.get('status',''):>10}")
    print(f"\nresultados -> {out}")


if __name__ == "__main__":
    main()
