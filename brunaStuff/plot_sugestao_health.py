#!/usr/bin/env python3
"""
Plot panorama de saude da simulacao FSI artéria-nervo (`cases/sugestao/`).

Combina, num unico PNG multi-painel:
  (a) P_contact(t) — max e media (lido de sugestao_p_contact_summary.csv)
  (b) area de contato A_c(t) (mm^2) (lido do mesmo CSV)
  (c) tortuosidade do nervo (lido de sugestao_nerve_tortuosity.csv)
  (d) |D|_max e |D|_arteria_meso vs t (lido do log do solver)
  (e) sanity check: P_contact_max(t) vs OMVS prescrita (P_lumen)

Os 4 primeiros paineis sao alimentados pelos CSVs gerados pelos scripts:
  - compute_nerve_tortuosity.py
  - extract_p_contact_from_sugestao.py

O painel (e) compara o P_contact extraido com a tabela OMVS de inlet
(fluid/constant/inlet_pressure.dat) — se P_contact eh fisicamente coerente,
sua amplitude deve ser uma fracao razoavel (10-80%) da pressao luminal,
modulada pelo gap geometrico/contato.

Uso:
    python3 plot_sugestao_health.py [--case CASE_DIR]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import numpy as np


def find_case_default() -> Path:
    candidates = [
        Path(__file__).resolve().parents[1] / "cases" / "sugestao",
        Path("/simulation/sugestao"),
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("cases/sugestao nao encontrado")


def read_csv(path: Path) -> tuple[list[str], list[list[float]]]:
    if not path.exists():
        return [], []
    rows: list[list[float]] = []
    with path.open() as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            try:
                rows.append([float(x) for x in row])
            except ValueError:
                pass
    return header, rows


def read_omvs_inlet(case: Path) -> np.ndarray | None:
    fpath = case / "fluid" / "constant" / "inlet_pressure.dat"
    if not fpath.exists():
        return None
    rows = []
    with fpath.open() as f:
        for line in f:
            ls = line.strip()
            if not ls or ls.startswith("#") or ls.startswith("//"):
                continue
            ls = ls.replace("(", " ").replace(")", " ")
            parts = ls.split()
            try:
                t = float(parts[0])
                p = float(parts[1])
                rows.append((t, p))
            except (ValueError, IndexError):
                continue
    return np.array(rows) if rows else None


def parse_log_dispnearcontact(log_path: Path) -> np.ndarray | None:
    """Le solid/log.solids4Foam e extrai dispNearContact watchpoint."""
    if not log_path.exists():
        return None
    times: list[float] = []
    dmag: list[float] = []
    cur_t = None
    pat_time = re.compile(r"^Time\s*=\s*([\d.eE+\-]+)")
    pat_disp = re.compile(
        r"dispNearContact.*?point[^\d-]*\(\s*([-\d.eE+]+)\s+"
        r"([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)"
    )
    for line in log_path.open(errors="ignore"):
        m = pat_time.match(line)
        if m:
            cur_t = float(m.group(1))
            continue
        m2 = pat_disp.search(line)
        if m2 and cur_t is not None:
            d = np.array([float(m2.group(i)) for i in (1, 2, 3)])
            times.append(cur_t)
            dmag.append(float(np.linalg.norm(d)))
            cur_t = None
    if not times:
        return None
    return np.column_stack([times, dmag])


def read_postproc_disp(case: Path) -> np.ndarray | None:
    """Le solid/postProcessing/0/solidPointDisplacement_dispNearContact.dat
    Format: # Time Dx Dy Dz magD
    Retorna (N, 2): [t, magD]."""
    fpath = case / "solid" / "postProcessing" / "0" / \
        "solidPointDisplacement_dispNearContact.dat"
    if not fpath.exists():
        return None
    rows = []
    for line in fpath.open():
        ls = line.strip()
        if not ls or ls.startswith("#"):
            continue
        parts = ls.split()
        if len(parts) >= 5:
            rows.append((float(parts[0]), float(parts[4])))
    return np.array(rows) if rows else None


def read_postproc_solid_forces(case: Path, patch: str) -> np.ndarray | None:
    """Le solid/postProcessing/0/solidForces<patch>.dat
    Format: # Time forceX forceY forceZ normalForce
    Retorna (N, 5): [t, Fx, Fy, Fz, Fn]."""
    fpath = case / "solid" / "postProcessing" / "0" / f"solidForces{patch}.dat"
    if not fpath.exists():
        return None
    rows = []
    for line in fpath.open():
        ls = line.strip()
        if not ls or ls.startswith("#"):
            continue
        parts = ls.split()
        if len(parts) >= 5:
            rows.append([float(x) for x in parts[:5]])
    return np.array(rows) if rows else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None)
    ap.add_argument("--out-png", default=None)
    args = ap.parse_args()

    case = Path(args.case) if args.case else find_case_default()
    here = Path(__file__).resolve().parent

    pc_csv = here / "sugestao_p_contact_summary.csv"
    tort_csv = here / "sugestao_nerve_tortuosity.csv"
    log = case / "solid" / "log.solids4Foam"

    pc_h, pc_rows = read_csv(pc_csv)
    tort_h, tort_rows = read_csv(tort_csv)
    omvs = read_omvs_inlet(case)
    disp = read_postproc_disp(case)
    if disp is None:
        disp = parse_log_dispnearcontact(log)
    f_ons = read_postproc_solid_forces(case, "ons_outer")

    print(f"[health] P_contact rows: {len(pc_rows)}")
    print(f"[health] tort rows: {len(tort_rows)}")
    print(f"[health] OMVS samples: {0 if omvs is None else len(omvs)}")
    print(f"[health] disp samples: {0 if disp is None else len(disp)}")
    print(f"[health] solidForces_ons samples: {0 if f_ons is None else len(f_ons)}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("ERROR: matplotlib nao disponivel.")
        sys.exit(1)

    fig, axes = plt.subplots(3, 2, figsize=(13, 9), sharex=False)

    # (a) P_contact(t)
    ax = axes[0, 0]
    if pc_rows:
        t = [r[0] for r in pc_rows]
        pmax = [r[1] for r in pc_rows]
        pmean = [r[2] for r in pc_rows]
        ax.plot(t, pmax, lw=1.4, label="P_max")
        ax.plot(t, pmean, lw=1.4, label="P_mean", alpha=0.7)
        ax.set_xlabel("t (s)")
        ax.set_ylabel("P_contact (Pa)")
        ax.legend()
        ax.grid(True, alpha=0.4)
        ax.set_title("(a) Pressao de contato arteria-ONS")
    else:
        ax.text(0.5, 0.5, "P_contact CSV missing", ha="center", va="center",
                transform=ax.transAxes)

    # (b) area de contato
    ax = axes[0, 1]
    if pc_rows:
        t = [r[0] for r in pc_rows]
        ac = [r[3] * 1e6 for r in pc_rows]   # m^2 -> mm^2
        a_total = pc_rows[0][4] * 1e6 if pc_rows else 0
        ax.plot(t, ac, lw=1.4, color="tab:orange")
        if a_total > 0:
            ax.axhline(a_total, ls="--", color="gray", alpha=0.5,
                       label=f"A_patch = {a_total:.1f} mm^2")
            ax.legend()
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Area de contato (mm^2)")
        ax.grid(True, alpha=0.4)
        ax.set_title("(b) Area dinamica de contato")
    else:
        ax.text(0.5, 0.5, "P_contact CSV missing", ha="center", va="center",
                transform=ax.transAxes)

    # (c) tortuosidade
    ax = axes[1, 0]
    if tort_rows:
        t = [r[0] for r in tort_rows]
        tort = [r[3] * 100 for r in tort_rows]
        ax.plot(t, tort, lw=1.4, color="tab:green")
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Tortuosidade (%)")
        ax.grid(True, alpha=0.4)
        ax.set_title("(c) Tortuosidade do nervo (arc/chord - 1)")
    else:
        ax.text(0.5, 0.5, "tortuosidade CSV missing", ha="center", va="center",
                transform=ax.transAxes)

    # (d) |D| watchpoint
    ax = axes[1, 1]
    if disp is not None:
        ax.plot(disp[:, 0], disp[:, 1] * 1e6, lw=1.4, color="tab:red")
        ax.set_xlabel("t (s)")
        ax.set_ylabel("|D| (μm)")
        ax.grid(True, alpha=0.4)
        ax.set_title("(d) Deslocamento na meso-parede arterial (P_contact)")
    else:
        ax.text(0.5, 0.5, "watchpoint nao encontrado no log",
                ha="center", va="center", transform=ax.transAxes)

    # (e) sanity check P_contact vs OMVS
    ax = axes[2, 0]
    if pc_rows and omvs is not None:
        t = np.array([r[0] for r in pc_rows])
        pmax = np.array([r[1] for r in pc_rows])
        ax.plot(t, pmax, label="P_contact_max", color="tab:blue")
        # Interpola OMVS no mesmo grid temporal
        p_omvs = np.interp(t, omvs[:, 0], omvs[:, 1])
        ax.plot(t, p_omvs, label="P_lumen (OMVS inlet)",
                color="tab:purple", alpha=0.7, ls="--")
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Pressao (Pa)")
        ax.legend()
        ax.grid(True, alpha=0.4)
        ax.set_title("(e) Sanity: P_contact vs P_lumen prescrita")
    else:
        ax.text(0.5, 0.5, "dados insuficientes", ha="center",
                va="center", transform=ax.transAxes)

    # (f) Forca normal integrada no patch ons_outer (forca de contato global)
    ax = axes[2, 1]
    if f_ons is not None:
        ax.plot(f_ons[:, 0], f_ons[:, 4], lw=1.0, color="tab:brown",
                label="F_n (ons_outer)")
        ax.plot(f_ons[:, 0],
                np.sqrt(f_ons[:, 1]**2 + f_ons[:, 2]**2 + f_ons[:, 3]**2),
                lw=1.0, ls="--", color="tab:olive", alpha=0.7,
                label="|F| (ons_outer)")
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Forca (N)")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.4)
        ax.set_title("(f) Forca de contato integrada no patch ons_outer")
    else:
        ax.text(0.5, 0.5, "dados insuficientes", ha="center",
                va="center", transform=ax.transAxes)

    fig.suptitle(f"Caso sugestao — saude geral  ({case.name})", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out_png = Path(args.out_png) if args.out_png else (
        here / "sugestao_health_panorama.png"
    )
    fig.savefig(out_png, dpi=120)
    print(f"[health] PNG salvo: {out_png}")


if __name__ == "__main__":
    main()
