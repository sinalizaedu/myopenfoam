#!/usr/bin/env python3
"""Analise do Caso 3F com rampa Dz = -1.0 mm (em vez de -1.5 mm).

Le os runs gerados por sweep_on-caso-3_dz1.sh:
  - sweep oficial em cases/_mi/on-caso-3__radpia2dura3/ccx (Pc 0..18068)
  - independencia de malha em Pc9034: radpia2dura3 / radpia3dura4 / radpia4dura5

Produz:
  brunaStuff/caso_3f_dz1_summary.txt   (3 blocos: sweep, mesh-indep, gap SAS)
  brunaStuff/caso_3f_dz1.json
"""
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# reaproveita as funcoes de parsing do analisador de producao
src = (HERE / "analyze_on-caso-3_pcontact_sweep.py").read_text()
cut = src.index("# 3) loop pelos runs")
ns: dict = {}
exec(compile(src[:cut], "pcontact_funcs", "exec"), ns)  # noqa: S102
parse_dat = ns["parse_dat"]
parse_frd_last_disp = ns["parse_frd_last_disp"]

SWEEP = [("Pc0", 0), ("Pc4517", 4517), ("Pc9034", 9034),
         ("Pc13551", 13551), ("Pc18068", 18068)]


def kink_metrics(tag, case_dir):
    frd = case_dir / f"on-caso-3_{tag}.frd"
    if not frd.exists():
        return None
    nodes, disp = parse_frd_last_disp(frd)
    if not nodes or not disp:
        return None
    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.zeros_like(P)
    for i, n in enumerate(nids):
        if n in disp:
            U[i] = disp[n]
    r0 = np.sqrt(P[:, 0]**2 + P[:, 1]**2)
    res = {}
    for name, rt, dr in [("on", 0.5e-3, 0.10e-3), ("pia", 1.55e-3, 0.06e-3),
                         ("sas", 2.0e-3, 0.06e-3), ("dura", 2.5e-3, 0.06e-3)]:
        m = np.abs(r0 - rt) < dr
        res[name] = float(np.sqrt(U[m, 0]**2 + U[m, 1]**2).max()) if m.sum() else 0.0
    res["Dz_max"] = float(np.abs(U[:, 2]).max())
    # indentacao radial local no patch de contato (dura externa, +X, z~22.5)
    md = (np.abs(r0 - 2.5e-3) < 0.06e-3) & (P[:, 2] > 20.9e-3) & (P[:, 2] < 24.1e-3) & (P[:, 0] > 2.4e-3)
    if md.sum():
        rx = P[md, 0] / r0[md]
        ry = P[md, 1] / r0[md]
        Ur = U[md, 0] * rx + U[md, 1] * ry
        res["U_r_contact_min"] = float(Ur.min())
    else:
        res["U_r_contact_min"] = 0.0
    # folga radial dura_inner (r~2.35) <-> pia_outer (r~1.55) no patch
    mz = (P[:, 2] > 20.9e-3) & (P[:, 2] < 24.1e-3)
    mdura = (np.abs(r0 - 2.35e-3) < 0.05e-3) & mz & (P[:, 0] > 2.0e-3)
    if mdura.sum() == 0:
        mdura = (r0 > 2.20e-3) & (r0 < 2.45e-3) & mz & (P[:, 0] > 2.0e-3)
    mpia = (np.abs(r0 - 1.55e-3) < 0.06e-3) & mz & (P[:, 0] > 1.0e-3)
    Px = P[:, 0] + U[:, 0]
    Py = P[:, 1] + U[:, 1]
    rdef = np.sqrt(Px**2 + Py**2)
    gap0 = (r0[mdura].min() - r0[mpia].max()) * 1e3
    gapd = (rdef[mdura].min() - rdef[mpia].max()) * 1e3
    res["gap0_mm"] = float(gap0)
    res["gap_def_mm"] = float(gapd)
    res["gap_reduc_pct"] = float((1 - gapd / gap0) * 100)
    return res


def lam_final(case_dir, tag):
    p = case_dir / f"on-caso-3_{tag}.sta"
    if not p.exists():
        return float("nan")
    for line in reversed(p.read_text().splitlines()):
        parts = line.split()
        if len(parts) >= 5:
            try:
                return float(parts[4])
            except ValueError:
                continue
    return float("nan")


def fmax_dz(case_dir, tag):
    p = case_dir / f"on-caso-3_{tag}.dat"
    if not p.exists():
        return float("nan"), float("nan")
    t, Dz, Fd, Fp, Fo, Fg = parse_dat(p)
    F_eng = -(Fd + Fp + Fo)
    if not F_eng.size:
        return float("nan"), float("nan")
    Fmax = float(np.nanmax(np.abs(F_eng))) * 1e3
    dz_at = float(Dz[np.nanargmax(np.abs(F_eng))]) * 1e3
    return Fmax, dz_at


# ---------- 1) sweep oficial radpia2dura3 ----------
OFF = REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx"
sweep = []
for tag, pc in SWEEP:
    k = kink_metrics(tag, OFF) or {}
    lam = lam_final(OFF, tag)
    Fmax, dz = fmax_dz(OFF, tag)
    sweep.append(dict(tag=tag, pc=pc, lam=lam, Fmax_mN=Fmax, dz_at_Fmax_mm=dz, **k))

# ---------- 2) mesh-indep em Pc9034 ----------
MESHES = [("radpia2dura3", REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx"),
          ("radpia3dura4", REPO / "cases/_mi/on-caso-3__radpia3dura4/ccx"),
          ("radpia4dura5", REPO / "cases/_mi/on-caso-3__radpia4dura5/ccx")]
mi = []
for mesh, cdir in MESHES:
    k = kink_metrics("Pc9034", cdir) or {}
    lam = lam_final(cdir, "Pc9034")
    Fmax, dz = fmax_dz(cdir, "Pc9034")
    mi.append(dict(mesh=mesh, lam=lam, Fmax_mN=Fmax, **k))

# ---------- 3) escreve tabelas ----------
L = []
L.append("CASO 3F  --  rampa Dz = -1.0 mm  (PIC 1333 Pa, Winkler 200 kPa/m)")
L.append("")
L.append("=== (1) Sweep oficial P_contact na malha radial radpia2dura3 ===")
L.append(f"{'tag':<8} {'Pc[Pa]':>7} {'lam':>5} {'Fmax[mN]':>9} {'Dz@Fmax':>8} "
         f"{'kink_on':>8} {'kink_pia':>9} {'kink_dura':>10} {'Ur_min':>8} "
         f"{'gap0':>6} {'gap_def':>8} {'gap_red%':>8}")
L.append("-" * 110)
for r in sweep:
    L.append(f"{r['tag']:<8} {r['pc']:>7} {r['lam']:>5.2f} {r['Fmax_mN']:>9.1f} "
             f"{r['dz_at_Fmax_mm']:>8.3f} {r.get('on',0)*1e3:>8.3f} "
             f"{r.get('pia',0)*1e3:>9.3f} {r.get('dura',0)*1e3:>10.3f} "
             f"{r.get('U_r_contact_min',0)*1e3:>8.3f} {r.get('gap0_mm',0):>6.3f} "
             f"{r.get('gap_def_mm',0):>8.3f} {r.get('gap_reduc_pct',0):>8.1f}")
L.append("")
L.append("=== (2) Independencia de malha em Pc9034 (kink_dura e Ur convergem) ===")
L.append(f"{'mesh':<14} {'lam':>5} {'Fmax[mN]':>9} {'kink_dura[mm]':>13} "
         f"{'Ur_min[mm]':>11} {'gap_red%':>8}")
L.append("-" * 70)
for r in mi:
    L.append(f"{r['mesh']:<14} {r['lam']:>5.2f} {r['Fmax_mN']:>9.1f} "
             f"{r.get('dura',0)*1e3:>13.3f} {r.get('U_r_contact_min',0)*1e3:>11.3f} "
             f"{r.get('gap_reduc_pct',0):>8.1f}")
table = "\n".join(L)
print(table)
(HERE / "caso_3f_dz1_summary.txt").write_text(table + "\n")
(HERE / "caso_3f_dz1.json").write_text(json.dumps(dict(sweep=sweep, mesh_indep=mi), indent=2))
print("\nSalvo: brunaStuff/caso_3f_dz1_summary.txt (+ .json)")
