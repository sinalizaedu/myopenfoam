"""TESTE A da bateria 'compartimentalizacao FSI':
   Uniformidade do campo p no fluido (Pascal direto).

Mede em on-fsi-2 e on-fsi-3 (t = 1 s, regime estatico convergido):

  - p_min, p_max, p_avg, sigma_p (no internalField do anel SAS-fluido)
  - span absoluto    : Delta p = p_max - p_min          [Pa]
  - span relativo    : Delta p / p_avg                  [-]
  - desvio do inlet  : (p_avg - p_inlet) / p_inlet      [-]
  - localizacao do extremo: argmax/argmin no espaco (x,y,z) e tambem em
    coordenadas anulares (r,theta,z) -- importante para checar se o pico
    de p coincide com o setor +x da carga contact_local (z=22.5 mm).

Interpretacao do criterio:

  Pascal puro      <=> (p_max - p_min)/p_avg << 1%   E   p_avg ~ p_inlet
  Pascal + offset  <=> p_avg > p_inlet (compartimento elevado mas uniforme)
                       => so' aparece em cul-de-sac TOTALMENTE fechado
                       (nao e' o nosso caso: temos inlet aberto em z=0)
  Direcional       <=> pico de p alinhado com setor +x da contact_local
                       (z ~ 22.5 mm, theta ~ 0)

Tambem gera uma figura com 3 paineis:
  (a) histograma de p (escala fina)
  (b) scatter (z, p) -- distribuicao axial
  (c) scatter (theta, p) na slice z ~ 22.5 mm -- direcionalidade

OBS: este script roda LOCALMENTE (sem docker), pois so' le os arquivos
ASCII do OpenFOAM.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
OUT_DIR = Path(__file__).resolve().parent / "sans_outputs"
OUT_DIR.mkdir(exist_ok=True)

# pressao do inlet do fluido (em unidades cinematicas p/rho), do fluid/0/p
P_INLET_KIN = {
    "on-fsi-2": 1.333,     # 1333 Pa / 1000 kg/m3
    "on-fsi-3": 3.800,     # 3800 Pa / 1000 kg/m3
}
RHO_LCR = 1000.0  # kg/m3 (incompressivel newtoniano, transportProperties)

# centro axial da contact_local arterial (do D file: z = 22.5 mm)
Z_CONTACT_M = 0.0225
DZ_HALF_M = 0.001  # +- 1 mm em torno do contact_local
SECTOR_HALF_DEG = 30.0  # +- 30 graus em torno de theta=0 (lado +x)


def parse_scalar_field(text: str) -> np.ndarray:
    """Le internalField nonuniform List<scalar> N (...). Devolve np.array(N).
    Aceita tambem internalField uniform <valor> (devolve array de 1 elemento)."""
    m = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
        text, re.DOTALL,
    )
    if m:
        n = int(m.group(1))
        body = m.group(2)
        vals = np.fromstring(body, sep="\n", dtype=np.float64)
        if vals.size != n:
            raise RuntimeError(f"esperava {n} valores, achei {vals.size}")
        return vals
    m = re.search(r"internalField\s+uniform\s+([-\deE.+]+)\s*;", text)
    if m:
        return np.array([float(m.group(1))], dtype=np.float64)
    raise RuntimeError("nao achei internalField scalar")


def parse_vector_field(text: str) -> np.ndarray:
    """Le internalField nonuniform List<vector>. Devolve np.array shape (N,3)."""
    m = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s*\n\s*(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
        text, re.DOTALL,
    )
    if not m:
        m = re.search(r"internalField\s+uniform\s+\(\s*([-\deE.+\s]+)\s*\)\s*;", text)
        if m:
            v = np.fromstring(m.group(1), sep=" ", dtype=np.float64)
            return v.reshape(1, 3)
        raise RuntimeError("nao achei internalField vector")
    n = int(m.group(1))
    body = m.group(2)
    # cada linha: (vx vy vz)
    rows = []
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            continue
        ms = re.match(r"\(\s*([^)]+)\s*\)", line)
        if ms:
            rows.append([float(s) for s in ms.group(1).split()])
    arr = np.array(rows, dtype=np.float64)
    if arr.shape != (n, 3):
        raise RuntimeError(f"esperava ({n},3), achei {arr.shape}")
    return arr


# -------- cell centres do fluido (lemos de constant/polyMesh via meshio? nao.
# usamos os arquivos 0/Cx,Cy,Cz se existirem, senao calculamos via writeCellCentres).
# Como este script roda LOCAL (sem docker), vamos derivar (x,y,z) das celulas do
# fluido reconstruindo a topologia anular ANALITICAMENTE a partir do blockMesh:
#   anel SAS r in [1.55, 2.35] mm, z in [0, 30] mm, 5760 hexaedros
#   (24 theta) x (8 radial) x (30 axial) = 5760
# Verifiquei: 24*8*30 = 5760, bate.
# A ordenacao de cells no OpenFOAM para um blockMesh-anel construido com cilindrico
# (i, j, k) costuma ser k-major: k(axial) varre primeiro, depois j(radial), depois
# i(theta). Vou inferir da consistencia geometrica.
# Se o blockMesh for retangular com 1 bloco e nx*ny*nz cells, a ordenacao e
# k-major (i+nx*j+nx*ny*k). Aqui o anel e' segmentado em multiplos blocos
# theta (talvez 4 ou 6 blocos), o que torna o reverse-engineering arriscado.
# Solucao robusta: leio cell-centres do solido sas (zonas com 5760 cells, mesma
# resolucao do fluido) - nao, espera, o solido FSI nao tem zona SAS.
# Outra solucao: regenero analiticamente os centroids do anel via blockMesh-style
# (24,8,30) e identifico a permutacao por bijecao geometrica.
# Mais simples: vou rodar postProcess writeCellCentres via DOCKER do user.

import subprocess


def find_running_fsi_container() -> str | None:
    """Procura container interativo do servico 'fsi'."""
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--filter", "ancestor=fsi-openfoam:latest",
             "--format", "{{.Names}}"],
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return None
    if not out:
        return None
    # primeiro container ativo
    return out.split("\n")[0]


def get_fluid_cell_centres(case_name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Roda postProcess writeCellCentres no container Docker (servico fsi)
    e le os arquivos Cx, Cy, Cz do tempo 0 do fluido."""
    case_path_local = CASES_DIR / case_name / "fluid"
    cx_path = case_path_local / "0" / "Cx"

    if not cx_path.exists():
        cont = find_running_fsi_container()
        if cont is None:
            # tenta criar um container efemero do servico fsi
            cmd = (f"cd /simulation/{case_name}/fluid && "
                   f"postProcess -func writeCellCentres -time 0 -case . 2>&1 | tail -3")
            print(f"[{case_name}] sem container ativo; usando docker compose run --rm fsi ...")
            subprocess.check_call(
                ["docker", "compose", "run", "--rm", "fsi", "bash", "-lc", cmd],
                cwd=str(ROOT),
            )
        else:
            cmd = (f"cd /simulation/{case_name}/fluid && "
                   f"postProcess -func writeCellCentres -time 0 -case . 2>&1 | tail -3")
            print(f"[{case_name}] reusando container '{cont}' ...")
            subprocess.check_call(
                ["docker", "exec", cont, "bash", "-lc", cmd],
            )

    cx = parse_scalar_field((case_path_local / "0" / "Cx").read_text())
    cy = parse_scalar_field((case_path_local / "0" / "Cy").read_text())
    cz = parse_scalar_field((case_path_local / "0" / "Cz").read_text())
    return cx, cy, cz


# -------------------------- core analise -----------------------------


def analyze_case(case_name: str) -> dict:
    """Le p e U no fluido em t=1, e cell-centres em t=0; calcula uniformidade."""
    case_dir = CASES_DIR / case_name / "fluid"
    p_kin = parse_scalar_field((case_dir / "1" / "p").read_text())   # m^2/s^2
    U     = parse_vector_field((case_dir / "1" / "U").read_text())   # m/s
    cx, cy, cz = get_fluid_cell_centres(case_name)

    # consistencia
    if not (len(p_kin) == U.shape[0] == cx.size == cy.size == cz.size):
        raise RuntimeError(
            f"{case_name}: tamanhos inconsistentes "
            f"p={len(p_kin)} U={U.shape[0]} Cxyz={cx.size}")

    p_Pa = p_kin * RHO_LCR  # converte para Pa absolutos
    p_inlet_Pa = P_INLET_KIN[case_name] * RHO_LCR

    p_min, p_max = float(p_Pa.min()), float(p_Pa.max())
    p_avg = float(p_Pa.mean())
    p_std = float(p_Pa.std())
    span_abs = p_max - p_min
    span_rel = span_abs / p_avg if abs(p_avg) > 0 else float("inf")
    deviation_from_inlet = (p_avg - p_inlet_Pa) / p_inlet_Pa

    # localiza extremos
    imax = int(p_Pa.argmax()); imin = int(p_Pa.argmin())
    r_max = math.hypot(cx[imax], cy[imax])
    th_max = math.degrees(math.atan2(cy[imax], cx[imax]))
    r_min = math.hypot(cx[imin], cy[imin])
    th_min = math.degrees(math.atan2(cy[imin], cx[imin]))

    # zona perto do contact_local: z em [Z-DZ, Z+DZ], theta em [-SECTOR, +SECTOR]
    r_all = np.hypot(cx, cy)
    th_all = np.degrees(np.arctan2(cy, cx))
    mask_z = np.abs(cz - Z_CONTACT_M) < DZ_HALF_M
    mask_th = np.abs(th_all) < SECTOR_HALF_DEG
    mask_focus = mask_z & mask_th

    p_focus = p_Pa[mask_focus]
    n_focus = int(mask_focus.sum())
    p_focus_avg = float(p_focus.mean()) if n_focus else float("nan")
    p_focus_max = float(p_focus.max()) if n_focus else float("nan")
    p_focus_amp = p_focus_max - p_avg  # quanto o setor da carga sobe acima da media

    # |U| residual
    Umag = np.linalg.norm(U, axis=1)
    Umag_max = float(Umag.max())
    Umag_avg = float(Umag.mean())

    return {
        "case": case_name,
        "n_cells": int(cx.size),
        "p_inlet_Pa": p_inlet_Pa,
        "p_min_Pa": p_min,
        "p_max_Pa": p_max,
        "p_avg_Pa": p_avg,
        "p_std_Pa": p_std,
        "span_abs_Pa": span_abs,
        "span_rel_pct": span_rel * 100.0,
        "deviation_from_inlet_pct": deviation_from_inlet * 100.0,
        "imax": imax,
        "max_loc_xyz_mm": (float(cx[imax]*1e3), float(cy[imax]*1e3), float(cz[imax]*1e3)),
        "max_loc_rthz_mm_deg_mm": (r_max*1e3, th_max, float(cz[imax]*1e3)),
        "imin": imin,
        "min_loc_xyz_mm": (float(cx[imin]*1e3), float(cy[imin]*1e3), float(cz[imin]*1e3)),
        "min_loc_rthz_mm_deg_mm": (r_min*1e3, th_min, float(cz[imin]*1e3)),
        "focus_n_cells": n_focus,
        "focus_p_avg_Pa": p_focus_avg,
        "focus_p_max_Pa": p_focus_max,
        "focus_amp_above_global_avg_Pa": p_focus_amp,
        "Umag_max_m_s": Umag_max,
        "Umag_avg_m_s": Umag_avg,
        "_arrays": {
            "p_Pa": p_Pa,
            "cx": cx, "cy": cy, "cz": cz,
            "r_all": r_all, "th_all": th_all,
            "mask_z": mask_z,
            "Umag": Umag,
        },
    }


def print_report(res: dict):
    print(f"\n{'='*72}\n  TESTE A - {res['case']}\n{'='*72}")
    print(f"  cells no fluido         : {res['n_cells']}")
    print(f"  p_inlet (Pa)            : {res['p_inlet_Pa']:.3f}")
    print(f"  p_avg   (Pa)            : {res['p_avg_Pa']:.3f}")
    print(f"  p_std   (Pa)            : {res['p_std_Pa']:.3e}")
    print(f"  p_min,p_max (Pa)        : {res['p_min_Pa']:.3f} ... {res['p_max_Pa']:.3f}")
    print(f"  span abs (p_max-p_min)  : {res['span_abs_Pa']:.3e} Pa")
    print(f"  span relativo           : {res['span_rel_pct']:.3e} %")
    print(f"  desvio do inlet         : {res['deviation_from_inlet_pct']:+.3e} %")
    print(f"  loc max (x,y,z) mm      : {res['max_loc_xyz_mm']}")
    print(f"  loc max (r,th,z) mm,deg : ({res['max_loc_rthz_mm_deg_mm'][0]:.3f}, "
          f"{res['max_loc_rthz_mm_deg_mm'][1]:+.1f}, {res['max_loc_rthz_mm_deg_mm'][2]:.3f})")
    print(f"  loc min (x,y,z) mm      : {res['min_loc_xyz_mm']}")
    print(f"  loc min (r,th,z) mm,deg : ({res['min_loc_rthz_mm_deg_mm'][0]:.3f}, "
          f"{res['min_loc_rthz_mm_deg_mm'][1]:+.1f}, {res['min_loc_rthz_mm_deg_mm'][2]:.3f})")
    print(f"  --- foco no setor da contact_local (z={Z_CONTACT_M*1e3:.1f} +- "
          f"{DZ_HALF_M*1e3:.1f} mm, theta=0 +- {SECTOR_HALF_DEG:.0f} deg)")
    print(f"  focus n_cells           : {res['focus_n_cells']}")
    print(f"  focus p_avg (Pa)        : {res['focus_p_avg_Pa']:.3f}")
    print(f"  focus p_max (Pa)        : {res['focus_p_max_Pa']:.3f}")
    print(f"  focus amp acima global  : {res['focus_amp_above_global_avg_Pa']:+.3e} Pa")
    print(f"  --- velocidade residual")
    print(f"  |U|_max (m/s)           : {res['Umag_max_m_s']:.3e}")
    print(f"  |U|_avg (m/s)           : {res['Umag_avg_m_s']:.3e}")

    # diagnostico Pascal
    if res['span_rel_pct'] < 1.0 and abs(res['deviation_from_inlet_pct']) < 1.0:
        verdict = "PASCAL PURO (compartimento isotropico, p ~ p_inlet)"
    elif res['span_rel_pct'] < 1.0:
        verdict = "PASCAL UNIFORME (p uniforme mas desviado do inlet)"
    elif res['focus_amp_above_global_avg_Pa'] > 0.05 * res['p_avg_Pa']:
        verdict = "DIRECIONAL (pico de p alinhado com setor da contact_local)"
    else:
        verdict = "PARCIALMENTE COMPARTMENTALIZADO (gradientes nao desprezíveis)"
    print(f"  >>> VEREDITO: {verdict}")


def plot_combined(results: list[dict], outpath: Path):
    fig, axes = plt.subplots(len(results), 3,
                              figsize=(14, 4.0 * len(results)),
                              squeeze=False)
    for irow, res in enumerate(results):
        a = res["_arrays"]
        ax_hist = axes[irow, 0]
        ax_z    = axes[irow, 1]
        ax_th   = axes[irow, 2]

        # (a) histograma de p
        ax_hist.hist(a["p_Pa"], bins=80, color="#3a78bf", edgecolor="white")
        ax_hist.axvline(res["p_inlet_Pa"], color="red", ls="--", lw=1.2,
                        label=f"p_inlet={res['p_inlet_Pa']:.1f} Pa")
        ax_hist.axvline(res["p_avg_Pa"], color="black", ls=":", lw=1.2,
                        label=f"p_avg={res['p_avg_Pa']:.4f} Pa")
        ax_hist.set_xlabel("p [Pa]"); ax_hist.set_ylabel("# cells")
        ax_hist.set_title(f"{res['case']} - histograma de p\n"
                          f"span={res['span_abs_Pa']:.2e} Pa  ({res['span_rel_pct']:.2e}%)")
        ax_hist.legend(fontsize=8)

        # (b) scatter (z, p)
        ax_z.scatter(a["cz"]*1e3, a["p_Pa"], s=4, alpha=0.4, color="#2b6cb0")
        ax_z.axvline(Z_CONTACT_M*1e3, color="red", ls="--", lw=1.0,
                     label=f"z=contact_local={Z_CONTACT_M*1e3:.1f} mm")
        ax_z.set_xlabel("z [mm]"); ax_z.set_ylabel("p [Pa]")
        ax_z.set_title(f"{res['case']} - p ao longo de z (todas as cells)")
        ax_z.legend(fontsize=8)

        # (c) scatter (theta, p) na slice z~contact_local
        mask_z = a["mask_z"]
        th_z = a["th_all"][mask_z]; p_z = a["p_Pa"][mask_z]
        ax_th.scatter(th_z, p_z, s=8, alpha=0.6, color="#c0392b")
        ax_th.axvline(0, color="red", ls="--", lw=1.0,
                       label="theta=0 (lado +x = contact_local)")
        ax_th.set_xlabel("theta [deg]"); ax_th.set_ylabel("p [Pa]")
        ax_th.set_title(f"{res['case']} - p(theta) na slice z=22.5+-1 mm "
                        f"(n={int(mask_z.sum())})")
        ax_th.legend(fontsize=8)

    fig.suptitle("Teste A - Uniformidade do campo p no LCR (FSI)",
                  fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"\n  figura: {outpath}")


def main():
    cases = ["on-fsi-2", "on-fsi-3"]
    results = [analyze_case(c) for c in cases]
    for r in results:
        print_report(r)

    # CSV resumo
    csv_path = OUT_DIR / "diag_testA_fluid_p_uniformity.csv"
    with open(csv_path, "w") as f:
        f.write("case,n_cells,p_inlet_Pa,p_avg_Pa,p_std_Pa,p_min_Pa,p_max_Pa,"
                "span_abs_Pa,span_rel_pct,dev_inlet_pct,"
                "focus_n,focus_p_avg_Pa,focus_p_max_Pa,focus_amp_Pa,"
                "Umag_max_m_s,Umag_avg_m_s\n")
        for r in results:
            f.write(f"{r['case']},{r['n_cells']},"
                    f"{r['p_inlet_Pa']:.4f},{r['p_avg_Pa']:.6f},{r['p_std_Pa']:.6e},"
                    f"{r['p_min_Pa']:.6f},{r['p_max_Pa']:.6f},"
                    f"{r['span_abs_Pa']:.6e},{r['span_rel_pct']:.6e},"
                    f"{r['deviation_from_inlet_pct']:+.6e},"
                    f"{r['focus_n_cells']},{r['focus_p_avg_Pa']:.6f},"
                    f"{r['focus_p_max_Pa']:.6f},{r['focus_amp_above_global_avg_Pa']:+.6e},"
                    f"{r['Umag_max_m_s']:.6e},{r['Umag_avg_m_s']:.6e}\n")
    print(f"\n  CSV: {csv_path}")

    fig_path = OUT_DIR / "diag_testA_fluid_p_uniformity.png"
    plot_combined(results, fig_path)


if __name__ == "__main__":
    main()
