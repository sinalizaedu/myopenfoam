#!/usr/bin/env python3
"""
Sweep analysis para on-caso-2g: varia k_winkler (gordura orbital)
Lê N runs (cada um com sufixo _<tag>.dat e _<tag>.frd convertido em .vtu)
e produz:
  1) Curvas F-d sobrepostas (1 cor por k)
  2) Kink lateral max por camada vs k (linhas)
  3) F_max e P_cr aparente vs k (barra/scatter)
"""
import re
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-2g/ccx")
OUT = Path("brunaStuff")

# Sweep ordenado: (tag, k em Pa/m, rotulo)
SWEEP = [
    ("k020k",   20_000,   "20 kPa/m  (jovem muito macia, 0.1x)"),
    ("k100k",  100_000,   "100 kPa/m (jovem, 0.5x)"),
    ("k200k",  200_000,   "200 kPa/m (baseline)"),
    ("k1M",  1_000_000,   "1 MPa/m  (envelhecida, 5x)"),
    ("k5M",  5_000_000,   "5 MPa/m  (SANS-like, 25x)"),
]
COLORS = plt.cm.viridis(np.linspace(0.0, 0.9, len(SWEEP)))


# ---------------------------------------------------------------------------
# 1) parse on-caso-2_<tag>.dat para extrair F-d
# ---------------------------------------------------------------------------
def parse_dat(path: Path):
    """Extrai (Dz_globo, RF_total_engaste) por incremento.

    Formato CCX:
      ' total force (fx,fy,fz) for set POSTERIOR_DURA and time  0.1500000E+00'
      ''
      '       -1.073e-03  -7.806e-18   4.705e-02'   <- 3 valores na proxima nao-vazia
      ''
      ' displacements (vx,vy,vz) for set POSTERIOR_DURA and time ...'
      ''
      '      3182  0.000  0.000  0.000'             <- LISTA por no (4 cols)
      ...
    """
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
            # nums esperados: [fx, fy, fz] (3 floats)
            floats = [float(x) for x in nums if "." in x or "e" in x.lower()]
            if len(floats) >= 3:
                rec[t][f"RF_{nset}"] = floats[:3]
            i = j + 1
        else:
            # lista "node ux uy uz" (1 int + 3 floats)
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
    Dz = []; F_dura = []; F_pia = []; F_on = []; F_globo = []
    for t in times:
        d = rec[t]
        if "U_ANTERIOR_GLOBO" in d:
            Dz.append(d["U_ANTERIOR_GLOBO"][2])
        else:
            Dz.append(np.nan)
        F_dura.append(d.get("RF_POSTERIOR_DURA", [0,0,0])[2])
        F_pia.append( d.get("RF_POSTERIOR_PIA",  [0,0,0])[2])
        F_on.append(  d.get("RF_POSTERIOR_ON",   [0,0,0])[2])
        F_globo.append(d.get("RF_ANTERIOR_GLOBO", [0,0,0])[2])
    return (np.array(times), np.array(Dz),
            np.array(F_dura), np.array(F_pia),
            np.array(F_on), np.array(F_globo))


# ---------------------------------------------------------------------------
# 2) parse .vtu para extrair kink lateral max por camada
# ---------------------------------------------------------------------------
def parse_vtu_kink(tag: str):
    """Lê o ULTIMO incremento .vtu de tag e retorna kink max por camada radial."""
    try:
        import vtk
        from vtk.util.numpy_support import vtk_to_numpy
    except ImportError:
        return None
    vtus = sorted(CASE.glob(f"on-caso-2_{tag}.*.vtu"),
                  key=lambda p: int(p.stem.split('.')[-1]))
    if not vtus:
        return None
    rdr = vtk.vtkXMLUnstructuredGridReader()
    rdr.SetFileName(str(vtus[-1]))
    rdr.Update()
    g = rdr.GetOutput()
    P = vtk_to_numpy(g.GetPoints().GetData())
    U = vtk_to_numpy(g.GetPointData().GetArray("U"))
    r = np.sqrt(P[:, 0]**2 + P[:, 1]**2)
    res = {}
    for name, r_target, dr in [
        ("on",  0.5e-3, 0.1e-3),
        ("pia", 1.55e-3, 0.06e-3),
        ("sas", 2.0e-3, 0.06e-3),
        ("dura", 2.5e-3, 0.06e-3),
    ]:
        m = np.abs(r - r_target) < dr
        if m.sum() == 0:
            res[name] = 0.0
        else:
            U_lat = np.sqrt(U[m, 0]**2 + U[m, 1]**2)
            res[name] = float(U_lat.max())
    res["Dz_max"] = float(np.abs(U[:, 2]).max())
    res["U_lat_global"] = float(np.sqrt(U[:, 0]**2 + U[:, 1]**2).max())
    return res


# ---------------------------------------------------------------------------
# 3) loop pelos runs
# ---------------------------------------------------------------------------
runs = []
for tag, k, label in SWEEP:
    p_dat = CASE / f"on-caso-2_{tag}.dat"
    p_sta = CASE / f"on-caso-2_{tag}.sta"
    if not p_dat.exists():
        print(f" [SKIP] {tag}: {p_dat} nao existe")
        continue
    t, Dz, Fd, Fp, Fo, Fg = parse_dat(p_dat)
    F_eng = -(Fd + Fp + Fo)  # forca de reacao (compressiva)
    kink = parse_vtu_kink(tag) or {}
    # lambda final (do .sta)
    lam_final = np.nan
    if p_sta.exists():
        for line in reversed(p_sta.read_text().splitlines()):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    lam_final = float(parts[4])  # 5a coluna = lambda
                    break
                except ValueError:
                    continue
    # F_max no engaste
    F_max = float(np.nanmax(np.abs(F_eng)))
    Dz_at_Fmax = float(Dz[np.nanargmax(np.abs(F_eng))]) * 1e3
    runs.append({
        "tag": tag, "k": k, "label": label,
        "t": t, "Dz_mm": Dz * 1e3, "F_eng_mN": F_eng * 1e3,
        "F_dura_mN": -Fd * 1e3, "F_pia_mN": -Fp * 1e3, "F_on_mN": -Fo * 1e3,
        "F_max_mN": F_max * 1e3, "Dz_at_Fmax": Dz_at_Fmax,
        "lam_final": lam_final, "kink": kink,
    })
    print(f"  {tag}: {len(t)} pts, lam_final={lam_final:.3f}, F_max={F_max*1e3:.1f} mN, "
          f"kink_pia={kink.get('pia', 0)*1e3:.3f} mm")

if not runs:
    print("Nenhum run encontrado em", CASE)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# 4) Plot 3 paineis
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle("on-caso-2g - Sweep de rigidez da gordura orbital (Winkler k)\n"
             "Modelo SANS V14b: 8 zonas + SAS solido (E=3kPa, nu=0.05) + "
             "dura ortotropica + globo Dz=-1.5mm",
             fontsize=12)

# Painel A: F-d sobreposto
ax = axes[0, 0]
for i, run in enumerate(runs):
    ax.plot(run["Dz_mm"], np.abs(run["F_eng_mN"]),
            "o-", color=COLORS[i], label=run["label"], lw=2, markersize=4)
ax.set_xlabel("Dz globo [mm] (compressao axial)")
ax.set_ylabel("|F_z| total no engaste posterior [mN]")
ax.set_title("(A) Curva F-d - mais dura a gordura, maior a forca de pico")
ax.legend(loc="best", fontsize=8)
ax.grid(alpha=0.3)
ax.invert_xaxis()

# Painel B: F_max vs k
ax = axes[0, 1]
ks = [r["k"] for r in runs]
Fmaxs = [r["F_max_mN"] for r in runs]
ax.semilogx(ks, Fmaxs, "o-", lw=2, markersize=12, color="darkred")
for r, k_, fm in zip(runs, ks, Fmaxs):
    ax.annotate(r["tag"], (k_, fm), xytext=(5, -15),
                textcoords="offset points", fontsize=8)
ax.set_xlabel("Winkler k [Pa/m] - gordura orbital")
ax.set_ylabel("F_max no engaste [mN]")
ax.set_title("(B) Forca compressiva de pico vs rigidez da gordura")
ax.grid(alpha=0.3, which="both")

# Painel C: kink lateral por camada vs k
ax = axes[1, 0]
camadas = [("on", "orange", "nervo (r=0.5)"),
           ("pia", "green",  "pia (r=1.55)"),
           ("sas", "cyan",   "SAS (r=2.0)"),
           ("dura", "red",   "dura (r=2.5)")]
for nm, c, lab in camadas:
    ys = []
    for r in runs:
        ys.append(r["kink"].get(nm, 0) * 1e3)  # mm
    ax.semilogx(ks, ys, "o-", lw=2, markersize=10, color=c, label=lab)
ax.set_xlabel("Winkler k [Pa/m] - gordura orbital")
ax.set_ylabel("|U_lat| max [mm] (kink lateral por camada)")
ax.set_title("(C) Kink por camada radial - gordura mais dura, MENOS kink na dura")
ax.legend(loc="best", fontsize=9)
ax.grid(alpha=0.3, which="both")

# Painel D: razao kink_pia / kink_dura (efeito relativo)
ax = axes[1, 1]
ratio = []
for r in runs:
    kp = r["kink"].get("pia", 1e-9)
    kd = r["kink"].get("dura", 1e-9)
    ratio.append(kp / max(kd, 1e-9))
ax.semilogx(ks, ratio, "s-", lw=2, markersize=12, color="purple")
ax.set_xlabel("Winkler k [Pa/m] - gordura orbital")
ax.set_ylabel("kink_pia / kink_dura  (razao S-mode)")
ax.set_title("(D) Confinamento dural - razao alta = pia kinka mais que dura\n"
             "valores >> 1 indicam SANS classico (dura reta, nervo flamba dentro)")
ax.grid(alpha=0.3, which="both")
ax.axhline(1.0, color="k", lw=0.5, ls="--", label="paridade")
ax.legend(loc="best", fontsize=9)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_png = OUT / "on-caso-2g_sweep_winkler.png"
plt.savefig(out_png, dpi=140, bbox_inches="tight")
print(f"\nGrafico salvo em: {out_png}")

# ---------------------------------------------------------------------------
# 5) tabela de resumo
# ---------------------------------------------------------------------------
lines = []
lines.append(f"{'tag':<8} {'k[Pa/m]':>10} {'lam':>6} {'F_max[mN]':>10} "
             f"{'kink_on':>9} {'kink_pia':>10} {'kink_sas':>10} "
             f"{'kink_dura':>10} {'pia/dura':>10}")
lines.append("-" * 96)
for r in runs:
    k = r["kink"]
    lines.append(
        f"{r['tag']:<8} {r['k']:>10} {r['lam_final']:>6.2f} "
        f"{r['F_max_mN']:>10.1f} "
        f"{k.get('on',0)*1e3:>9.3f} {k.get('pia',0)*1e3:>10.3f} "
        f"{k.get('sas',0)*1e3:>10.3f} {k.get('dura',0)*1e3:>10.3f} "
        f"{k.get('pia',0)/max(k.get('dura',1e-9),1e-9):>10.2f}")
table = "\n".join(lines)
print("\n" + table)
(OUT / "on-caso-2g_sweep_summary.txt").write_text(table + "\n")
print(f"\nTabela salva em: brunaStuff/on-caso-2g_sweep_summary.txt")

# JSON pra reuso
runs_json = [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
              for k, v in r.items()} for r in runs]
(OUT / "on-caso-2g_sweep.json").write_text(json.dumps(runs_json, indent=2))
print(f"JSON dos dados em: brunaStuff/on-caso-2g_sweep.json")
