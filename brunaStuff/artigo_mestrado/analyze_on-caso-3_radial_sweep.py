#!/usr/bin/env python3
"""
Reaproveita o analisador do sweep 3S apontando o CASE para o scratch da malha
RADIAL (radpia2dura3). Mesmas metricas (lam, F_max, kink por camada, Ur_min),
mesma extracao — so muda o diretorio dos .dat/.frd/.sta. Gera uma tabela de
resumo paralela em brunaStuff/on-caso-3_radial_sweep_summary.txt e um JSON.

A unica coisa diferente da producao e' a MALHA (refino radial das laminas);
carga, materiais, BCs, Riks vem do mesmo deck. Por isso a area do patch e' a
mesma e P=p_c gera a mesma forca arterial.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# carrega o modulo de analise (nome tem hifens -> importlib por caminho)
spec = importlib.util.spec_from_file_location(
    "pcontact_sweep", HERE / "analyze_on-caso-3_pcontact_sweep.py")
A = importlib.util.module_from_spec(spec)
# evita re-executar o pipeline de plot/escrita do modulo no import:
# o modulo roda tudo em nivel de top-level, entao em vez de import normal
# vamos so' reutilizar suas FUNCOES recompilando o arquivo num namespace
# truncado ate antes do "loop pelos runs".
src = (HERE / "analyze_on-caso-3_pcontact_sweep.py").read_text()
cut = src.index("# 3) loop pelos runs")
ns: dict = {}
exec(compile(src[:cut], "pcontact_sweep_funcs", "exec"), ns)  # noqa: S102

parse_dat = ns["parse_dat"]
parse_frd_last_disp = ns["parse_frd_last_disp"]

CASE = REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx"
SWEEP = ns["SWEEP"]


def parse_frd_kink_dir(tag: str, case_dir: Path):
    """Versao de parse_frd_kink com diretorio configuravel."""
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
    for name, r_target, dr in [
        ("on",  0.5e-3, 0.10e-3),
        ("pia", 1.55e-3, 0.06e-3),
        ("sas", 2.0e-3, 0.06e-3),
        ("dura", 2.5e-3, 0.06e-3),
    ]:
        m = np.abs(r0 - r_target) < dr
        res[name] = (float(np.sqrt(U[m, 0]**2 + U[m, 1]**2).max())
                     if m.sum() else 0.0)
    res["Dz_max"] = float(np.abs(U[:, 2]).max())
    res["U_lat_global"] = float(np.sqrt(U[:, 0]**2 + U[:, 1]**2).max())
    mask_dura = np.abs(r0 - 2.5e-3) < 0.06e-3
    mask_z = (P[:, 2] > 20.9e-3) & (P[:, 2] < 24.1e-3)
    mask_x = P[:, 0] > 2.4e-3
    m_local = mask_dura & mask_z & mask_x
    if m_local.sum() > 0:
        rhat_x = P[m_local, 0] / r0[m_local]
        rhat_y = P[m_local, 1] / r0[m_local]
        U_r = U[m_local, 0] * rhat_x + U[m_local, 1] * rhat_y
        res["U_r_contact_min"] = float(U_r.min())
        res["U_r_contact_mean"] = float(U_r.mean())
        res["n_nodes_contact"] = int(m_local.sum())
    else:
        res["U_r_contact_min"] = res["U_r_contact_mean"] = 0.0
        res["n_nodes_contact"] = 0
    return res


runs = []
for tag, pc, short, label in SWEEP:
    p_dat = CASE / f"on-caso-3_{tag}.dat"
    p_sta = CASE / f"on-caso-3_{tag}.sta"
    if not p_dat.exists():
        print(f" [SKIP] {tag}: {p_dat} nao existe")
        continue
    t, Dz, Fd, Fp, Fo, Fg = parse_dat(p_dat)
    F_eng = -(Fd + Fp + Fo)
    kink = parse_frd_kink_dir(tag, CASE) or {}
    lam_final = float("nan")
    if p_sta.exists():
        for line in reversed(p_sta.read_text().splitlines()):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    lam_final = float(parts[4]); break
                except ValueError:
                    continue
    F_max = float(np.nanmax(np.abs(F_eng))) if F_eng.size else 0.0
    Dz_at_Fmax = (float(Dz[np.nanargmax(np.abs(F_eng))]) * 1e3
                  if F_eng.size else 0.0)
    runs.append(dict(tag=tag, pc=pc, lam_final=lam_final, F_max_mN=F_max*1e3,
                     Dz_at_Fmax_mm=Dz_at_Fmax, kink=kink))
    print(f"  {tag}: lam={lam_final:.3f} F_max={F_max*1e3:.1f} mN "
          f"kink_on={kink.get('on',0)*1e3:.3f} kink_dura={kink.get('dura',0)*1e3:.3f} "
          f"Ur_min={kink.get('U_r_contact_min',0)*1e3:.4f}")

if not runs:
    raise SystemExit("nenhum run radial encontrado em " + str(CASE))

lines = [f"{'tag':<8} {'Pc[Pa]':>7} {'lam':>6} {'F_max[mN]':>10} "
         f"{'Dz@Fmax[mm]':>12} {'kink_on':>9} {'kink_pia':>10} "
         f"{'kink_dura':>10} {'Ur_min[mm]':>11}",
         "-" * 96]
for r in runs:
    k = r["kink"]
    lines.append(f"{r['tag']:<8} {r['pc']:>7} {r['lam_final']:>6.2f} "
                 f"{r['F_max_mN']:>10.2f} {r['Dz_at_Fmax_mm']:>12.3f} "
                 f"{k.get('on',0)*1e3:>9.3f} {k.get('pia',0)*1e3:>10.3f} "
                 f"{k.get('dura',0)*1e3:>10.3f} "
                 f"{k.get('U_r_contact_min',0)*1e3:>11.4f}")
table = "\n".join(lines)
print("\nMALHA RADIAL radpia2dura3 (so a malha muda vs producao):\n" + table)
(HERE / "on-caso-3_radial_sweep_summary.txt").write_text(table + "\n")
(HERE / "on-caso-3_radial_sweep.json").write_text(json.dumps(runs, indent=2))
print("\nSalvo: brunaStuff/on-caso-3_radial_sweep_summary.txt (+ .json)")
