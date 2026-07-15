#!/usr/bin/env python3
"""Comparacao B: resposta estrutural FSI vs solido hidrostatico (Casos 1/2).

Malha: on-caso-1.2 (mesma do FSI acoplado), convertida via foam_polymesh_to_ccx_inp
(_mesh_indep_solid/f1). Material: elastico LINEAR (nu=0.45), igual ao grid FSI linear.

Solido (Casos 1/2):
  - PIC = P Pa somente em FSI_DURA_SURF (face interna da dura, interface dura<->SAS);
  - caps da esclera a 1333 Pa (desacoplamento seletivo, igual ao FSI);
  - SEM carga em FSI_PIA (o SAS solido transmitiria pressao a pia; aqui a cavidade
    nao esta discretizada — e' o substituto simplificado dos Casos 1 e 2).

FSI: valores de cases/on-caso-1.2/_grid/grid_fsi_results.json (mat=linear, d=1e15).

Saida:
  cases/on-caso-1.2/_compare_b/solid_results.json
  brunaStuff/compare_b_fsi_vs_solid_summary.txt
  brunaStuff/figs/compare_b_fsi_vs_solid.png

Uso:
  python3 brunaStuff/compare_b_fsi_vs_solid.py
  python3 brunaStuff/compare_b_fsi_vs_solid.py --no-run   # so extrai/plota
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from frd_stress import parse_frd  # noqa: E402
CASE = REPO / "cases" / "on-caso-1.2"
MESH_SRC = CASE / "_mesh_indep_solid" / "f1" / "ccx"
OUT = CASE / "_compare_b"
GRID_JSON = CASE / "_grid" / "grid_fsi_results.json"
PICS = [1333.0, 2000.0, 3000.0, 3800.0]
P_SCLERA = 1333.0
K_WINKLER = 2.0e5

MAIN_TMPL = """\
** on-caso-1.2 -- solido PIC-only (Casos 1/2), malha identica ao FSI
*INCLUDE, INPUT=all_mesh.inp
*INCLUDE, INPUT=winkler.inp

*MATERIAL, NAME=ON_MAT
*ELASTIC
30000.0, 0.45
*DENSITY
1000.0
*MATERIAL, NAME=PIA_MAT
*ELASTIC
3.0e6, 0.45
*DENSITY
1100.0
*MATERIAL, NAME=DURA_MAT
*ELASTIC
3.0e6, 0.45
*DENSITY
1100.0
*MATERIAL, NAME=LC_MAT
*ELASTIC
0.4e6, 0.45
*DENSITY
1100.0
*MATERIAL, NAME=SCLERA_PERI_MAT
*ELASTIC
5.0e6, 0.45
*DENSITY
1400.0
*MATERIAL, NAME=SCLERA_RING_MAT
*ELASTIC
5.0e6, 0.45
*DENSITY
1400.0
*MATERIAL, NAME=GLOBO_MAT
*ELASTIC
5.0e6, 0.45
*DENSITY
1400.0

*SOLID SECTION, ELSET=ON,          MATERIAL=ON_MAT
*SOLID SECTION, ELSET=PIA,         MATERIAL=PIA_MAT
*SOLID SECTION, ELSET=DURA,        MATERIAL=DURA_MAT
*SOLID SECTION, ELSET=LC,          MATERIAL=LC_MAT
*SOLID SECTION, ELSET=SCLERA_PERI, MATERIAL=SCLERA_PERI_MAT
*SOLID SECTION, ELSET=SCLERA_RING, MATERIAL=SCLERA_RING_MAT
*SOLID SECTION, ELSET=GLOBO,       MATERIAL=GLOBO_MAT

*BOUNDARY
POSTERIOR_ON,   1, 3, 0.0
POSTERIOR_PIA,  1, 3, 0.0
POSTERIOR_DURA, 1, 3, 0.0
GLOBO_OUTER,    1, 3, 0.0

*STEP
*STATIC
*DLOAD
FSI_DURA_SURF, P, {pic:.1f}
FSI_SCLERA_PERI_SURF, P, {p_sclera:.1f}
FSI_SCLERA_RING_SURF, P, {p_sclera:.1f}
*NODE FILE
U
*NODE PRINT, NSET=FSI_DURA, U
*NODE PRINT, NSET=FSI_PIA, U
*END STEP
"""


def sh(cmd: str, check=True):
    print(f"  $ {cmd}", flush=True)
    return subprocess.run(cmd, shell=True, cwd=str(REPO), check=check)


def docker_ccx(tag: str):
    inner = (
        f"set -e; cd on-caso-1.2/_compare_b/{tag} && "
        "rm -f main.frd main.dat main.cvg main.sta && "
        "ccx_preCICE -i main > log.ccx 2>&1; tail -n 8 log.ccx"
    )
    sh(f'docker compose run --rm fsi bash -lc {json.dumps(inner)}', check=False)


def load_coords(msh: Path) -> dict[int, tuple[float, float, float]]:
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


def last_disp_block(dat: Path, setname: str) -> dict[int, tuple[float, float, float]]:
    lines = dat.read_text().splitlines()
    idxs = [i for i, l in enumerate(lines) if "displacements" in l and setname in l]
    if not idxs:
        return {}
    data: dict[int, tuple[float, float, float]] = {}
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


def radial_ur_max_frd(frd: Path, msh: Path, zone: str, z_max: float = 29.5) -> float | None:
    """Max Ur radial (µm) nos nos da zona, corpo do nervo z < z_max."""
    coords = load_coords(msh)
    _, n2zone, steps = parse_frd(frd)
    if not steps:
        return None
    disp = steps[-1]["disp"]
    urs = []
    for nid, (ux, uy, uz) in disp.items():
        zones = n2zone.get(nid, set())
        if zone not in zones or nid not in coords:
            continue
        x, y, z = coords[nid]
        if z >= z_max:
            continue
        r = math.hypot(x, y)
        if r > 0:
            urs.append((x * ux + y * uy) / r)
    return max(urs, key=abs) * 1e6 if urs else None


def radial_ur_max(dat: Path, msh: Path, setname: str, z_max: float = 29.5) -> float | None:
    """Max |Ur| no corpo do nervo (exclui ponta z>=29.5 mm)."""
    coords = load_coords(msh)
    disp = last_disp_block(dat, setname)
    urs = []
    for n, (ux, uy, uz) in disp.items():
        if n not in coords:
            continue
        x, y, z = coords[n]
        if z >= z_max:
            continue
        r = math.hypot(x, y)
        if r > 0:
            urs.append((x * ux + y * uy) / r)
    return max(urs, key=abs) * 1e6 if urs else None


def prepare(pic: float) -> Path:
    tag = f"P{int(pic)}_solid"
    pdir = OUT / tag
    pdir.mkdir(parents=True, exist_ok=True)
    for f in ("all_mesh.inp", "winkler.inp"):
        shutil.copy(MESH_SRC / f, pdir / f)
    (pdir / "main.inp").write_text(
        MAIN_TMPL.format(pic=pic, p_sclera=P_SCLERA))
    return pdir


def extract_solid(pdir: Path) -> dict:
    frd, msh = pdir / "main.frd", pdir / "all_mesh.inp"
    if not frd.exists():
        return {"status": "NO_FRD"}
    return {
        "status": "OK",
        "dura_ur_max_um": radial_ur_max_frd(frd, msh, "dura"),
        "pia_ur_max_um": radial_ur_max_frd(frd, msh, "pia"),
    }


def run_solid(pic: float) -> dict:
    tag = f"P{int(pic)}_solid"
    pdir = prepare(pic)
    docker_ccx(tag)
    out = {"pic_pa": pic, "model": "solid_pic_dura", **extract_solid(pdir)}
    return out


def load_fsi() -> dict[float, dict]:
    rows = json.loads(GRID_JSON.read_text())
    out = {}
    for r in rows:
        if r.get("mat") != "linear" or r.get("status") != "OK":
            continue
        if abs(r["d"] - 1e15) / 1e15 > 1e-6:
            continue
        p = float(r["p_target_pa"])
        if any(abs(p - x) < 1.0 for x in PICS):
            out[p] = r
    return out


def plot(rows: list[dict], path: Path):
    pics = sorted({r["pic_pa"] for r in rows})
    x = np.array(pics)

    def series(key, model):
        return [next(r[key] for r in rows if r["pic_pa"] == p and r["model"] == model)
                for p in pics]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(x, series("dura_ur_max_um", "fsi"), "o-", label="FSI (linear)", color="#1f77b4")
    ax1.plot(x, series("dura_ur_max_um", "solid_pic_dura"), "s--",
             label="Solido PIC na dura", color="#ff7f0e")
    ax1.set_xlabel("PIC (Pa)")
    ax1.set_ylabel(r"$\Delta r_{\mathrm{dura}}$ (µm)")
    ax1.set_title("Distensao radial da dura")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(x, series("pia_ur_max_um", "fsi"), "o-", label="FSI (linear)", color="#1f77b4")
    ax2.plot(x, series("pia_ur_max_um", "solid_pic_dura"), "s--",
             label="Solido PIC na dura", color="#ff7f0e")
    ax2.set_xlabel("PIC (Pa)")
    ax2.set_ylabel(r"$\Delta r_{\mathrm{pia}}$ (µm)")
    ax2.set_title("Compressao radial da pia")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    fig.suptitle("Comparacao B: FSI vs solido hidrostatico (Casos 1/2)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    print(f"Figura -> {path}")


def write_summary(rows: list[dict], path: Path):
    lines = [
        "=" * 78,
        "Comparacao B — FSI (linear, d=1e15) vs solido PIC na dura (Casos 1/2)",
        "Malha on-caso-1.2 identica; material linear nu=0.45",
        "=" * 78,
        f"{'PIC(Pa)':>8}  {'dura_FSI':>10} {'dura_sol':>10} {'Δ%':>8}  "
        f"{'pia_FSI':>10} {'pia_sol':>10} {'Δ%':>8}",
        "-" * 78,
    ]
    for p in sorted({r["pic_pa"] for r in rows}):
        fsi = next(r for r in rows if r["pic_pa"] == p and r["model"] == "fsi")
        sol = next((r for r in rows if r["pic_pa"] == p and r["model"] == "solid_pic_dura"), None)
        if not sol or sol.get("dura_ur_max_um") is None:
            lines.append(f"{p:8.0f}  FSI ok; solido ausente ou falhou")
            continue
        dd = sol["dura_ur_max_um"] - fsi["dura_ur_max_um"]
        dp = sol["pia_ur_max_um"] - fsi["pia_ur_max_um"]
        pd = 100 * dd / fsi["dura_ur_max_um"] if fsi["dura_ur_max_um"] else float("nan")
        pp = 100 * dp / fsi["pia_ur_max_um"] if fsi["pia_ur_max_um"] else float("nan")
        lines.append(
            f"{p:8.0f}  {fsi['dura_ur_max_um']:10.2f} {sol['dura_ur_max_um']:10.2f} {pd:7.1f}%  "
            f"{fsi['pia_ur_max_um']:10.2f} {sol['pia_ur_max_um']:10.2f} {pp:7.1f}%"
        )
    path.write_text("\n".join(lines) + "\n")
    print(path.read_text())


def main():
    if not MESH_SRC.exists():
        sys.exit(f"Malha nao encontrada: {MESH_SRC}\n"
                 "Rode: python3 brunaStuff/mesh_independence_solid_caso_1_2.py 1")

    run = "--no-run" not in sys.argv
    fsi = load_fsi()
    rows: list[dict] = []

    for p in PICS:
        if p not in fsi:
            print(f"AVISO: FSI linear P={p} ausente em grid_fsi_results.json")
            continue
        rows.append({
            "pic_pa": p,
            "model": "fsi",
            "dura_ur_max_um": fsi[p]["dura_ur_max_um"],
            "pia_ur_max_um": fsi[p]["pia_ur_max_um"],
        })
        if run:
            sol = run_solid(p)
            rows.append({
                "pic_pa": p,
                "model": "solid_pic_dura",
                "dura_ur_max_um": sol.get("dura_ur_max_um"),
                "pia_ur_max_um": sol.get("pia_ur_max_um"),
                "status": sol.get("status"),
            })
        else:
            tag = OUT / f"P{int(p)}_solid"
            if (tag / "main.frd").exists():
                rows.append({"pic_pa": p, "model": "solid_pic_dura", **extract_solid(tag)})

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "solid_results.json"
    out_json.write_text(json.dumps(rows, indent=2))
    summary = HERE / "compare_b_fsi_vs_solid_summary.txt"
    write_summary(rows, summary)
    plot(rows, HERE / "figs" / "compare_b_fsi_vs_solid.png")
    print(f"\nJSON -> {out_json}")


if __name__ == "__main__":
    main()
