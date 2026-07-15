#!/usr/bin/env python3
"""
analyze_on-caso-3-sf_pcontact_sweep.py
======================================
Sweep analysis para on-caso-3-sf ("on-caso-3 Sem Forca frontal").

Diferenca para on-caso-3: NAO ha compressao/forca axial vinda da frente (sem Dz
prescrito, sem CLOAD EOM). A unica carga ativa e' a P_contact LATERAL da arteria
oftalmica, varrida 0 -> 18068 Pa. A pergunta e': a indentacao lateral SOZINHA
dispara a flambagem (kink) do nervo?

Como nao ha forca axial, a curva F-Dz nao e' o sinal relevante. Os indicadores
de flambagem aqui sao:
  (A) lam_final do Riks (.sta): se < 1.0, a estrutura NAO suportou a carga
      lateral total -> colapso/snap (flambagem). Se ~= 1.0, ficou estavel.
  (B) kink lateral max por camada (on, pia, sas, dura) vs P_contact: crescimento
      super-linear / salto = onset de bifurcacao lateral.
  (C) indentation local da dura no patch de contato (U_radial em z=22.5) vs P_c.
  (D) |U_lat| global max e amplificacao nervo/dura vs P_contact.

Saidas:
  brunaStuff/on-caso-3-sf_pcontact_sweep.png
  brunaStuff/on-caso-3-sf_pcontact_sweep_summary.txt
  brunaStuff/on-caso-3-sf_pcontact_sweep.json
"""
import re
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-3-sf/ccx")
OUT = Path("brunaStuff")
PREFIX = "on-caso-3-sf"

# (tag, Pc em Pa, rotulo curto, rotulo longo)
SWEEP = [
    ("Pc0",         0, "0 Pa",      "0 Pa     (sem arteria: referencia sem carga lateral)"),
    ("Pc4517",   4517, "4.5 kPa",   "4517 Pa  (0.5x, ~33 mmHg)"),
    ("Pc9034",   9034, "9.0 kPa",   "9034 Pa  (1.0x, ~67 mmHg, baseline)"),
    ("Pc13551", 13551, "13.6 kPa",  "13551 Pa (1.5x, ~100 mmHg)"),
    ("Pc18068", 18068, "18.1 kPa",  "18068 Pa (2.0x, ~135 mmHg, pico sistolico)"),
]
COLORS = plt.cm.plasma(np.linspace(0.05, 0.85, len(SWEEP)))


# ---------------------------------------------------------------------------
# 1) parse .dat (totais RF/U por incremento)
# ---------------------------------------------------------------------------
def parse_dat(path: Path):
    NUM = r"-?\d+(?:\.\d+)?(?:[Ee][+\-]?\d+)?"
    txt = path.read_text(errors="ignore")
    lines = txt.splitlines()
    rec = {}
    i = 0
    while i < len(lines):
        L = lines[i]
        m = re.match(
            r"\s*(total\s+force|displacements)\s+\([^)]*\)\s+for\s+set\s+(\S+)\s+and\s+time\s+([\d.E+\-]+)",
            L, re.IGNORECASE)
        if not m:
            i += 1
            continue
        kind, nset, t = m.group(1).lower(), m.group(2).upper(), float(m.group(3))
        rec.setdefault(t, {})
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if kind.startswith("total"):
            nums = re.findall(NUM, lines[j])
            floats = [float(x) for x in nums if "." in x or "e" in x.lower()]
            if len(floats) >= 3:
                rec[t][f"RF_{nset}"] = floats[:3]
            i = j + 1
        else:
            uxs, uys, uzs = [], [], []
            while j < len(lines) and lines[j].strip():
                parts = lines[j].split()
                if len(parts) >= 4:
                    try:
                        uxs.append(float(parts[1]))
                        uys.append(float(parts[2]))
                        uzs.append(float(parts[3]))
                    except ValueError:
                        pass
                j += 1
            if uxs:
                rec[t][f"U_{nset}"] = [
                    sum(uxs) / len(uxs),
                    sum(uys) / len(uys),
                    sum(uzs) / len(uzs),
                ]
            i = j
    times = sorted(rec.keys())
    F_lat_post, Dz_globo = [], []
    for t in times:
        d = rec[t]
        # reacao lateral total no engaste posterior (= P_contact resistida)
        fx = sum(d.get(f"RF_{n}", [0, 0, 0])[0]
                 for n in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"))
        fy = sum(d.get(f"RF_{n}", [0, 0, 0])[1]
                 for n in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"))
        F_lat_post.append(np.hypot(fx, fy))
        Dz_globo.append(d["U_ANTERIOR_GLOBO"][2] if "U_ANTERIOR_GLOBO" in d else np.nan)
    return np.array(times), np.array(F_lat_post), np.array(Dz_globo)


# ---------------------------------------------------------------------------
# 2) parser nativo de CalculiX .frd (ASCII)
# ---------------------------------------------------------------------------
def _parse_data_line(L: str, n_floats: int):
    if len(L) < 3 + 10 + 12:
        return None
    try:
        nid = int(L[3:13])
    except ValueError:
        return None
    vals = []
    for k in range(n_floats):
        s = L[13 + 12*k: 13 + 12*(k + 1)]
        if not s:
            return None
        try:
            vals.append(float(s))
        except ValueError:
            return None
    return nid, vals


def parse_frd_last_disp(path: Path):
    nodes = {}
    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    in_nodes = False
    for L in lines:
        s = L.strip()
        if not in_nodes:
            if s.startswith("2C ") or s == "2C":
                in_nodes = True
            continue
        if s.startswith("-3"):
            break
        if L.lstrip().startswith("-1"):
            r = _parse_data_line(L, 3)
            if r is not None:
                nid, xyz = r
                nodes[nid] = (xyz[0], xyz[1], xyz[2])

    disp_blocks = []
    in_disp = False
    cur = {}
    for L in lines:
        s = L.strip()
        if s.startswith("-4"):
            parts = s.split()
            varname = parts[1].strip() if len(parts) >= 2 else ""
            if varname == "DISP":
                in_disp = True
                cur = {}
            else:
                in_disp = False
            continue
        if not in_disp:
            continue
        if s.startswith("-3"):
            if cur:
                disp_blocks.append(cur)
            in_disp = False
            cur = {}
            continue
        if s.startswith("-5"):
            continue
        if L.lstrip().startswith("-1"):
            r = _parse_data_line(L, 3)
            if r is not None:
                nid, vs = r
                cur[nid] = (vs[0], vs[1], vs[2])

    last_disp = disp_blocks[-1] if disp_blocks else {}
    return nodes, last_disp


def parse_frd_kink(tag: str):
    frd = CASE / f"{PREFIX}_{tag}.frd"
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
        res[name] = float(np.sqrt(U[m, 0]**2 + U[m, 1]**2).max()) if m.sum() else 0.0
    res["Dz_max"] = float(np.abs(U[:, 2]).max())
    res["U_lat_global"] = float(np.sqrt(U[:, 0]**2 + U[:, 1]**2).max())

    # Indentation local: U_radial nos nos da dura externa (r~2.5) no patch
    # de contato (z=[20.9,24.1] mm, x>2.4 mm).
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
        res["U_r_contact_min"] = 0.0
        res["U_r_contact_mean"] = 0.0
        res["n_nodes_contact"] = 0
    return res


# ---------------------------------------------------------------------------
# 3) loop pelos runs
# ---------------------------------------------------------------------------
runs = []
for tag, pc, short, label in SWEEP:
    p_dat = CASE / f"{PREFIX}_{tag}.dat"
    p_sta = CASE / f"{PREFIX}_{tag}.sta"
    if not p_dat.exists():
        print(f" [SKIP] {tag}: {p_dat} nao existe")
        continue
    t, F_lat_post, Dz_globo = parse_dat(p_dat)
    kink = parse_frd_kink(tag) or {}
    lam_final = np.nan
    if p_sta.exists():
        for line in reversed(p_sta.read_text().splitlines()):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    lam_final = float(parts[4])
                    break
                except ValueError:
                    continue
    # buckling flag: Riks nao alcancou a carga lateral total (lam<~0.99)
    bifurcated = (not np.isnan(lam_final)) and (lam_final < 0.99)
    runs.append({
        "tag": tag, "pc": pc, "short": short, "label": label,
        "lam_final": lam_final, "bifurcated": bool(bifurcated),
        "F_lat_post_mN": float(F_lat_post[-1] * 1e3) if F_lat_post.size else 0.0,
        "kink": kink,
    })
    print(f"  {tag}: lam_final={lam_final:.3f} "
          f"{'[NAO suportou carga total -> flambagem?]' if bifurcated else '[estavel ate lam=1]'}, "
          f"kink_on={kink.get('on', 0)*1e3:.3f} mm, "
          f"kink_dura={kink.get('dura', 0)*1e3:.3f} mm, "
          f"U_r_contact={kink.get('U_r_contact_min', 0)*1e3:.4f} mm")

if not runs:
    print("Nenhum run encontrado em", CASE)
    raise SystemExit(1)

pcs = [r["pc"] for r in runs]


# ---------------------------------------------------------------------------
# 4) 4-panel plot
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15.5, 11.5))
fig.suptitle(
    "on-caso-3-sf - Sweep de P_contact LATERAL (arteria oftalmica), SEM forca frontal\n"
    "So indentacao lateral + Winkler k=200 kPa/m (baseline), sem perturbacao. Riks ARCMAX=1.0",
    fontsize=12)

# Painel A: lam_final do Riks vs P_contact (indicador de colapso/flambagem)
ax = axes[0, 0]
lams = [r["lam_final"] for r in runs]
cols = ["darkred" if r["bifurcated"] else "seagreen" for r in runs]
ax.bar([r["short"] for r in runs], lams, color=cols, alpha=0.85)
ax.axhline(1.0, ls="--", color="gray", lw=1.2, label="lam=1.0 (carga lateral total)")
for i, (r, lam) in enumerate(zip(runs, lams)):
    ax.text(i, lam, f"{lam:.2f}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("lam_final do Riks (.sta)")
ax.set_title("(A) Riks alcancou a carga lateral total?\n"
             "lam<1 (vermelho) = NAO suportou -> colapso/snap (flambagem)")
ax.set_ylim(0, max(1.1, max(lams) * 1.15 if lams else 1.1))
ax.legend(loc="lower right", fontsize=8)
ax.grid(alpha=0.3, axis="y")

# Painel B: kink lateral por camada vs P_contact
ax = axes[0, 1]
camadas = [("on",  "orange", "nervo (r=0.5)"),
           ("pia", "green",  "pia (r=1.55)"),
           ("sas", "cyan",   "SAS (r=2.0)"),
           ("dura", "red",   "dura (r=2.5)")]
for nm, c, lab in camadas:
    ys = [r["kink"].get(nm, 0) * 1e3 for r in runs]
    ax.plot(pcs, ys, "o-", lw=2, markersize=10, color=c, label=lab)
ax.set_xlabel("P_contact [Pa] - arteria oftalmica focal (LATERAL)")
ax.set_ylabel("|U_lat| max [mm] (kink lateral por camada)")
ax.set_title("(B) Kink lateral por camada vs P_contact\n"
             "salto / crescimento super-linear = onset de flambagem")
ax.legend(loc="best", fontsize=9)
ax.grid(alpha=0.3)

# Painel C: indentation local da dura no patch de contato
ax = axes[1, 0]
ur_min = [abs(r["kink"].get("U_r_contact_min", 0)) * 1e3 for r in runs]
ur_mean = [abs(r["kink"].get("U_r_contact_mean", 0)) * 1e3 for r in runs]
ax.plot(pcs, ur_min, "o-", lw=2, markersize=12, color="navy",
        label="|U_r|_max (pico de afundamento)")
ax.plot(pcs, ur_mean, "s--", lw=1.5, markersize=8, color="steelblue",
        label="|U_r|_medio (no patch contato)")
if len(pcs) >= 2:
    a, b = np.polyfit(pcs, ur_min, 1)
    pc_fit = np.linspace(0, max(pcs), 50)
    comp = (1 / (a * 1e3)) if a != 0 else float("inf")
    ax.plot(pc_fit, a * pc_fit + b, ":", color="gray", lw=1.5,
            label=f"linear: {a*1e3:.2f} um/kPa\n  -> rigidez focal ~ {comp:.2f} kPa/um")
ax.set_xlabel("P_contact [Pa] - arteria oftalmica focal (LATERAL)")
ax.set_ylabel("|U_r| dura no patch de contato [mm]")
ax.set_title("(C) Afundamento LOCAL da dura sob a arteria (z=22.5 mm, +X)\n"
             "linearidade = sem instabilidade; joelho = flambagem local")
ax.legend(loc="best", fontsize=8)
ax.grid(alpha=0.3)

# Painel D: |U_lat| global + amplificacao nervo/dura
ax = axes[1, 1]
ulat = [r["kink"].get("U_lat_global", 0) * 1e3 for r in runs]
ax.plot(pcs, ulat, "o-", lw=2, markersize=12, color="purple",
        label="|U_lat| global max")
ax.set_xlabel("P_contact [Pa] - arteria oftalmica focal (LATERAL)")
ax.set_ylabel("|U_lat| global max [mm]")
ax.set_title("(D) Deslocamento lateral global maximo vs P_contact")
ax2 = ax.twinx()
amp = []
for r in runs:
    kd = r["kink"].get("dura", 0)
    ko = r["kink"].get("on", 0)
    amp.append((ko / kd) if kd > 0 else 0.0)
ax2.plot(pcs, amp, "^--", lw=1.5, markersize=8, color="darkorange",
         label="razao kink nervo/dura")
ax2.set_ylabel("kink_nervo / kink_dura", color="darkorange")
ax2.tick_params(axis="y", labelcolor="darkorange")
lines1, labs1 = ax.get_legend_handles_labels()
lines2, labs2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labs1 + labs2, loc="best", fontsize=8)
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
out_png = OUT / f"{PREFIX}_pcontact_sweep.png"
plt.savefig(out_png, dpi=140, bbox_inches="tight")
print(f"\nGrafico salvo em: {out_png}")


# ---------------------------------------------------------------------------
# 5) tabela de resumo
# ---------------------------------------------------------------------------
lines = []
lines.append(
    f"{'tag':<8} {'Pc[Pa]':>7} {'lam':>6} {'flamb?':>7} "
    f"{'kink_on':>9} {'kink_pia':>10} {'kink_dura':>10} "
    f"{'Ur_min[mm]':>11} {'Ulat_g[mm]':>11}")
lines.append("-" * 92)
for r in runs:
    k = r["kink"]
    lines.append(
        f"{r['tag']:<8} {r['pc']:>7} {r['lam_final']:>6.2f} "
        f"{('SIM' if r['bifurcated'] else 'nao'):>7} "
        f"{k.get('on',0)*1e3:>9.3f} {k.get('pia',0)*1e3:>10.3f} "
        f"{k.get('dura',0)*1e3:>10.3f} "
        f"{k.get('U_r_contact_min',0)*1e3:>11.4f} "
        f"{k.get('U_lat_global',0)*1e3:>11.4f}")
table = "\n".join(lines)
print("\n" + table)
(OUT / f"{PREFIX}_pcontact_sweep_summary.txt").write_text(table + "\n")
print(f"\nTabela salva em: brunaStuff/{PREFIX}_pcontact_sweep_summary.txt")

runs_json = [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
              for k, v in r.items()} for r in runs]
(OUT / f"{PREFIX}_pcontact_sweep.json").write_text(json.dumps(runs_json, indent=2))
print(f"JSON dos dados em: brunaStuff/{PREFIX}_pcontact_sweep.json")
