"""Mede 4 efeitos da microgravidade no nervo optico (SANS).

Compara on-mestrado-2/3 (FEM) e on-fsi-2/3 (FSI) e quantifica:

  1) BALAO DURAL : D_outer(z) - diametro externo da bainha ao longo do nervo.
                   Em SANS, espera-se aumento radial (ingurgitamento da SAS).

  2) ACHATAMENTO DO GLOBO : Dz na face anterior_globo (z=30.80 mm).
                   Em SANS, a tampa peripapilar e o polo posterior do globo
                   sao empurrados para frente pela coluna de LCR represada.

  3) KINKING / TORTUOSIDADE : centroide do nervo (zona on) em xy ao longo de z.
                   Em SANS, a combinacao de balao + impacto arterial deveria
                   deslocar lateralmente o eixo do nervo.

  4) BATALHA POR ESPACO : sigma_radial maxima na cell adjacente a contact_local.
                   Em SANS, o dura ja' inflado encontra a arteria com mais
                   intensidade -> aumento da concentracao de stress local.

Le D e sigma direto dos arquivos OpenFOAM via docker; usa xyz_C (cell centres)
para indexar por z. Gera tabelas e arquivos CSV em brunaStuff/sans_outputs/.
"""

from __future__ import annotations

import math
import re
import subprocess
from collections import defaultdict
from pathlib import Path

CONTAINER = "om2-resume"
OUT_DIR = Path(__file__).resolve().parent / "sans_outputs"
OUT_DIR.mkdir(exist_ok=True)


def _docker_cat(path: str) -> str:
    return subprocess.check_output(
        ["docker", "exec", CONTAINER, "bash", "-lc", f"cat {path}"],
        stderr=subprocess.STDOUT,
    ).decode("utf-8", errors="replace")


def _docker_run(cmd: str) -> str:
    return subprocess.check_output(
        ["docker", "exec", CONTAINER, "bash", "-lc", cmd],
        stderr=subprocess.STDOUT,
    ).decode("utf-8", errors="replace")


# --------------------- parsers OpenFOAM -----------------------

def _parse_field_data(text: str, kind: str):
    """Le internalField. kind in {'vector','scalar','symmTensor'}."""
    pattern = {
        "vector":      r"List<vector>",
        "scalar":      r"List<scalar>",
        "symmTensor":  r"List<symmTensor>",
    }[kind]
    m = re.search(rf"internalField\s+nonuniform\s+{pattern}\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        m = re.search(r"internalField\s+uniform\s+(.*?);", text, re.DOTALL)
        if m:
            v = m.group(1).strip()
            if kind == "scalar":
                return [float(v)]
            else:
                ms = re.match(r"\(([^)]+)\)", v)
                vals = [float(s) for s in ms.group(1).split()]
                return [tuple(vals)]
        raise RuntimeError(f"nao achei internalField {kind}")
    out = []
    for line in m.group(2).split("\n"):
        line = line.strip()
        if not line:
            continue
        if kind == "scalar":
            out.append(float(line))
        else:
            ms = re.match(r"\(\s*([^)]+)\s*\)", line)
            if ms:
                out.append(tuple(float(s) for s in ms.group(1).split()))
    return out


def parse_volVectorField(text):     return _parse_field_data(text, "vector")
def parse_volSymmTensorField(text): return _parse_field_data(text, "symmTensor")
def parse_volScalarField(text):     return _parse_field_data(text, "scalar")


# --------------------- cell-zone slicings -----------------------
ZONES_OM = {
    "on":          (0, 7680),
    "pia":         (7680, 8640),
    "sas":         (8640, 14400),
    "dura":        (14400, 16320),
    "lc":          (16320, 16576),
    "sclera_peri": (16576, 16704),
    "sclera_ring": (16704, 16864),
    "globo":       (16864, 17408),
}
ZONES_FSI = {
    "on":          (0, 7680),
    "pia":         (7680, 8640),
    "dura":        (8640, 10560),
    "lc":          (10560, 10816),
    "sclera_peri": (10816, 10944),
    "sclera_ring": (10944, 11104),
    "globo":       (11104, 11648),
}
# on-mestrado-1: 5 zonas. "pia" inclui pia+SAS+dura lumpadas; "sclera" inclui
# peri+ring lumpadas. Para a metrica do "balao dural" usamos a camada externa
# desta pia expandida (que estruturalmente *e'* a dura na -1).
ZONES_OM1 = {
    "on":     (0, 7680),
    "pia":    (7680, 16320),   # pia expandida = pia + SAS + dura
    "lc":     (16320, 16576),
    "sclera": (16576, 16864),  # sclera lumpada = peri + ring
    "globo":  (16864, 17408),
}


def get_cell_centres(case_dir_in_container: str):
    """Roda postProcess writeCellCentres e le Cx,Cy,Cz."""
    # writeCellCentres no OpenFOAM 2512 esta dentro do postProcess
    cmd = (f"cd {case_dir_in_container} && "
           f"postProcess -func writeCellCentres -time 0 2>&1 | tail -5")
    _docker_run(cmd)
    Cx = parse_volScalarField(_docker_cat(f"{case_dir_in_container}/0/Cx"))
    Cy = parse_volScalarField(_docker_cat(f"{case_dir_in_container}/0/Cy"))
    Cz = parse_volScalarField(_docker_cat(f"{case_dir_in_container}/0/Cz"))
    return Cx, Cy, Cz


# --------------------- 4 metricas -----------------------

def metric_dural_diameter_along_z(D, Cx, Cy, Cz, zones, dura_zone="dura"):
    """Para cada nivel z, mede o D_outer = max(r_deformado) entre celulas dura.
    r_deformado = sqrt((x+Dx)^2 + (y+Dy)^2)."""
    a, b = zones[dura_zone]
    bins = defaultdict(list)
    for i in range(a, b):
        x = Cx[i] + D[i][0]
        y = Cy[i] + D[i][1]
        z = Cz[i]
        # pega so' a layer mais externa (cells em r maior)
        r0 = (Cx[i]**2 + Cy[i]**2)**0.5
        # bin por z (1 mm)
        zbin = round(z * 1000)
        bins[zbin].append((r0, (x*x + y*y)**0.5))
    rows = []
    for zbin in sorted(bins.keys()):
        # so a celula com r0 maximo (camada mais externa da dura)
        r0_max = max(t[0] for t in bins[zbin])
        outer = [t[1] for t in bins[zbin] if abs(t[0] - r0_max) < 1e-6]
        if outer:
            rows.append((zbin / 1000.0, r0_max, sum(outer)/len(outer)))
    return rows


def metric_globe_flattening(D, Cx, Cy, Cz, zones):
    """Dz medio na zona globo - quanto o globo foi empurrado para +z."""
    a, b = zones["globo"]
    Dz = [D[i][2] for i in range(a, b)]
    z_max = max(Cz[i] for i in range(a, b))
    # somente cells na ponta anterior (z proximo de z_max)
    anterior_Dz = [D[i][2] for i in range(a, b) if abs(Cz[i] - z_max) < 0.05e-3]
    return {
        "Dz_globo_avg_um":         sum(Dz)/len(Dz)*1e6,
        "Dz_globo_max_um":         max(Dz)*1e6,
        "Dz_anterior_globo_um":    sum(anterior_Dz)/max(len(anterior_Dz),1)*1e6,
    }


def metric_nerve_kinking(D, Cx, Cy, Cz, zones):
    """Centroide do nervo (zona on) em x,y por slice z."""
    a, b = zones["on"]
    bins = defaultdict(list)
    for i in range(a, b):
        z = Cz[i]
        zbin = round(z * 1000)
        x = Cx[i] + D[i][0]
        y = Cy[i] + D[i][1]
        bins[zbin].append((x, y))
    rows = []
    for zbin in sorted(bins.keys()):
        xs = [p[0] for p in bins[zbin]]
        ys = [p[1] for p in bins[zbin]]
        x_c = sum(xs)/len(xs); y_c = sum(ys)/len(ys)
        # offset lateral medio em mm
        rows.append((zbin/1000.0, x_c*1000, y_c*1000, (x_c**2+y_c**2)**0.5*1000))
    return rows


def metric_contact_pressure(D, sigma, Cx, Cy, Cz, zones, dura_zone="dura",
                             contact_z_range=(0.0215, 0.0235)):
    """sigma compressivo maximo nas cells da dura proximas ao contact_local
    (z=22.5 mm, eixo +X). sigma_xx negativo = compressao radial inward."""
    a, b = zones[dura_zone]
    candidates = []
    for i in range(a, b):
        x = Cx[i]; y = Cy[i]; z = Cz[i]
        if not (contact_z_range[0] <= z <= contact_z_range[1]):
            continue
        # so' cells no setor +X (theta proximo a 0)
        if x <= 0:
            continue
        if abs(y) > 0.5e-3:
            continue
        # pega sigma_xx (radial em +X)
        s_xx = sigma[i][0]
        candidates.append((x, y, z, s_xx, sigma[i]))
    if not candidates:
        return {"sigma_xx_min_Pa": float("nan"), "sigma_xx_avg_Pa": float("nan"),
                "sigmaEq_max_Pa": float("nan"), "n_cells": 0}
    sxx_vals = [c[3] for c in candidates]
    seq_vals = []
    for c in candidates:
        xx, xy, xz, yy, yz, zz = c[4]
        d1, d2, d3 = xx-yy, yy-zz, zz-xx
        seq_vals.append((0.5*(d1*d1+d2*d2+d3*d3) + 3*(xy*xy+yz*yz+xz*xz))**0.5)
    return {
        "sigma_xx_min_Pa":  min(sxx_vals),
        "sigma_xx_avg_Pa":  sum(sxx_vals)/len(sxx_vals),
        "sigmaEq_max_Pa":   max(seq_vals),
        "n_cells":          len(candidates),
    }


# --------------------- main -----------------------

def run_for_case(name: str, fsi: bool, lumped: bool = False):
    base = f"/simulation/{name}/solid"
    print(f"\n{'='*60}\n  caso: {name}\n{'='*60}")
    Cx, Cy, Cz = get_cell_centres(base)
    D = parse_volVectorField(_docker_cat(f"{base}/1/D"))
    sigma = parse_volSymmTensorField(_docker_cat(f"{base}/1/sigma"))
    if fsi:
        zones = ZONES_FSI
        zlabel = "fsi(7)"
        dura_zone = "dura"
    elif lumped:
        zones = ZONES_OM1
        zlabel = "om1-lumped(5)"
        dura_zone = "pia"  # pia expandida = camada externa estruturalmente analoga a dura
    else:
        zones = ZONES_OM
        zlabel = "om(8)"
        dura_zone = "dura"
    print(f"  cells solido: {len(D)} (zones={zlabel})")

    # 1) Balao dural
    dia = metric_dural_diameter_along_z(D, Cx, Cy, Cz, zones, dura_zone=dura_zone)
    csv_path = OUT_DIR / f"dural_diameter_{name}.csv"
    with open(csv_path, "w") as f:
        f.write("z_mm,r_undeformed_mm,r_deformed_mm,delta_um\n")
        for z, r0, r1 in dia:
            f.write(f"{z:.3f},{r0*1000:.4f},{r1*1000:.4f},{(r1-r0)*1e6:.3f}\n")
    delta_max = max((r1 - r0) for _, r0, r1 in dia) * 1e6
    delta_avg = sum((r1 - r0) for _, r0, r1 in dia) / len(dia) * 1e6
    print(f"  [1] BALAO DURAL: delta r_outer max = {delta_max:.2f} um, "
          f"avg = {delta_avg:.2f} um  -> {csv_path.name}")

    # 2) Achatamento do globo
    glb = metric_globe_flattening(D, Cx, Cy, Cz, zones)
    print(f"  [2] GLOBO: Dz_anterior = {glb['Dz_anterior_globo_um']:.3f} um  "
          f"(esclera/globo empurrados em +z = achatamento)")

    # 3) Kinking lateral
    kink = metric_nerve_kinking(D, Cx, Cy, Cz, zones)
    csv_path = OUT_DIR / f"nerve_kinking_{name}.csv"
    with open(csv_path, "w") as f:
        f.write("z_mm,xc_mm,yc_mm,offset_lateral_mm\n")
        for z, xc, yc, r in kink:
            f.write(f"{z:.3f},{xc:.5f},{yc:.5f},{r:.5f}\n")
    off_max = max(r for _, _, _, r in kink)  # mm
    print(f"  [3] KINKING: offset lateral max do nervo = {off_max*1000:.2f} um  "
          f"-> {csv_path.name}")

    # 4) Pressao na batalha por espaco
    cp = metric_contact_pressure(D, sigma, Cx, Cy, Cz, zones, dura_zone=dura_zone)
    print(f"  [4] BATALHA NO CONTACT_LOCAL ({cp['n_cells']} cells dura em "
          f"z=21.5-23.5mm, +X):")
    print(f"        sigma_xx min (radial inward) = {cp['sigma_xx_min_Pa']:.1f} Pa")
    print(f"        sigma_xx avg                  = {cp['sigma_xx_avg_Pa']:.1f} Pa")
    print(f"        sigmaEq max (von Mises local) = {cp['sigmaEq_max_Pa']:.1f} Pa")

    return {
        "name": name,
        "balloon_max_um": delta_max,
        "balloon_avg_um": delta_avg,
        "globe_Dz_um":    glb['Dz_anterior_globo_um'],
        "kinking_max_um": off_max*1000,
        "contact_sigma_xx_min": cp['sigma_xx_min_Pa'],
        "contact_sigmaEq_max": cp['sigmaEq_max_Pa'],
    }


def main():
    # (name, fsi, lumped). lumped=True so para on-mestrado-1 (5 zonas).
    cases = [
        ("on-mestrado-1", False, True),
        ("on-mestrado-2", False, False),
        ("on-mestrado-3", False, False),
        ("on-fsi-2",      True,  False),
        ("on-fsi-3",      True,  False),
    ]
    rows = [run_for_case(n, f, lumped=lp) for n, f, lp in cases]

    print("\n" + "="*100)
    print("RESUMO COMPARATIVO - 4 efeitos da SANS:")
    print("="*100)
    fmt = "{:<16} {:>14} {:>14} {:>14} {:>14} {:>14} {:>14}"
    print(fmt.format("caso", "balao_max(um)", "balao_avg(um)",
                     "globo_Dz(um)", "kinking(um)",
                     "sxx_min(Pa)", "sigEq_max(Pa)"))
    print("-"*100)
    for r in rows:
        print(fmt.format(r["name"],
                         f"{r['balloon_max_um']:+.2f}",
                         f"{r['balloon_avg_um']:+.2f}",
                         f"{r['globe_Dz_um']:+.3f}",
                         f"{r['kinking_max_um']:.3f}",
                         f"{r['contact_sigma_xx_min']:+.1f}",
                         f"{r['contact_sigmaEq_max']:.1f}"))
    print("\nINTERPRETACAO:")
    print(" - balao_max  : diametro externo da bainha (delta r_outer) - SANS aumenta")
    print(" - globo_Dz   : Dz medio da face anterior do globo - SANS empurra")
    print(" - kinking    : offset lateral max do centroide do nervo - SANS aumenta")
    print(" - sxx_min    : sigma_xx mais compressivo na regiao do contact_local")
    print(" - sigEq_max  : von Mises max na regiao do contact_local")


if __name__ == "__main__":
    main()
