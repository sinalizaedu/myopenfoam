#!/usr/bin/env python3
"""
Sweep analysis para on-caso-2J (on-caso-2.2): varia k_winkler (gordura orbital)
na variante com tortuosidade em "J" embutida na malha.

Analogo a analyze_on-caso-2g_sweep.py, mas adaptado a geometria em "J":
  - a compressao axial e prescrita em -Y (DOF 2), nao -Z;
  - a malha esta curvada no plano XY (espessura/binormal em Z), logo a
    classificacao de camadas por raio sqrt(x^2+y^2) nao vale: as camadas
    (on/pia/sas/dura) sao identificadas pela CONECTIVIDADE dos *ELSET no
    on-caso-2.2_mesh.inp e casadas ao .vtu pelas coordenadas de referencia;
  - "excursao lateral" = deslocamento perpendicular ao eixo de compressao Y,
    i.e. sqrt(Ux^2 + Uz^2); o componente Z (binormal) e flambagem fora-do-plano.

Le N runs (sufixo _<tag>) e produz:
  1) Curvas F-d sobrepostas (1 cor por k)
  2) F_max no engaste vs k
  3) lambda_final de Riks vs k (indicador de estabilidade/snap-through)
  4) Excursao lateral max por camada vs k (kink)
"""
import re
import sys
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# reusa o parser de .frd ja existente (sem dependencia de vtk/ccx2paraview)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from frd_stress import parse_frd

CASE = Path("cases/on-caso-2.2/ccx")
PREFIX = "on-caso-2.2"
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

# Camadas radiais (no tubo reto original): nervo -> pia -> sas -> dura.
# Chaves minusculas para casar com frd_stress (_zone_key: ON_MAT -> on).
ZONES = ["on", "pia", "sas", "dura"]
AXIAL = 1  # indice do eixo de compressao (Y) no caso "J"


# ---------------------------------------------------------------------------
# 1) parse on-caso-2.2_<tag>.dat para extrair F-d (RF/U por NSET)
# ---------------------------------------------------------------------------
def parse_dat(path: Path):
    """Extrai (U_globo, RF_total) por incremento para cada NSET (TOTALS=ONLY)."""
    NUM = r"-?\d+(?:\.\d+)?(?:[Ee][+\-]?\d+)?"
    lines = path.read_text(errors="ignore").splitlines()
    rec = {}
    i = 0
    while i < len(lines):
        L = lines[i]
        m = re.match(
            r"\s*(total\s+force|displacements)\s+\([^)]*\)\s+for\s+set\s+(\S+)\s+"
            r"and\s+time\s+([\d.E+\-]+)", L, re.IGNORECASE)
        if not m:
            i += 1
            continue
        kind, nset, t = m.group(1).lower(), m.group(2).upper(), float(m.group(3))
        rec.setdefault(t, {})
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        # com TOTALS=ONLY tanto RF quanto U vem como 1 linha de 3 floats
        nums = re.findall(NUM, lines[j]) if j < len(lines) else []
        floats = [float(x) for x in nums if "." in x or "e" in x.lower()]
        key = "RF" if kind.startswith("total") else "U"
        if len(floats) >= 3:
            rec[t][f"{key}_{nset}"] = floats[:3]
        i = j + 1

    times = sorted(rec.keys())
    out = {"t": [], "U_globe": [], "F_mag": [],
           "F_dura": [], "F_pia": [], "F_on": []}
    for t in times:
        d = rec[t]
        out["t"].append(t)
        ug = d.get("U_ANTERIOR_GLOBO", [np.nan, np.nan, np.nan])
        out["U_globe"].append(abs(ug[AXIAL]))
        # reacao total no engaste posterior = soma vetorial dos 3 sets
        Rtot = np.zeros(3)
        for nm in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"):
            Rtot += np.array(d.get(f"RF_{nm}", [0, 0, 0]))
        out["F_mag"].append(float(np.linalg.norm(Rtot)))
        out["F_dura"].append(float(np.linalg.norm(d.get("RF_POSTERIOR_DURA", [0, 0, 0]))))
        out["F_pia"].append(float(np.linalg.norm(d.get("RF_POSTERIOR_PIA", [0, 0, 0]))))
        out["F_on"].append(float(np.linalg.norm(d.get("RF_POSTERIOR_ON", [0, 0, 0]))))
    return {k: np.array(v) for k, v in out.items()}


# ---------------------------------------------------------------------------
# 2) parse .frd (ultimo incremento) -> excursao lateral max por zona
# ---------------------------------------------------------------------------
def parse_frd_kink(tag: str):
    """Le on-caso-2.2_<tag>.frd e devolve, no ULTIMO passo de carga (max lam),
    a excursao lateral max (perp ao eixo de compressao Y: sqrt(Ux^2+Uz^2)) e o
    deslocamento fora-do-plano max (|Uz|, binormal) por zona anatomica.

    Usa frd_stress.parse_frd: no->zona vem do material do elemento (robusto, sem
    depender de vtk/ccx2paraview). lat aqui usa (Ux,Uz) -- diferente do ulat
    (Ux,Uy) do frd_stress, porque no caso J a compressao e' em -Y."""
    frd = CASE / f"{PREFIX}_{tag}.frd"
    if not frd.exists():
        return None
    _, n2zone, steps = parse_frd(frd)
    steps = [s for s in steps if s.get("disp")]
    if not steps:
        return None
    last = max(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0))
    disp = last["disp"]
    res = {z: {"lat": 0.0, "oop": 0.0} for z in ZONES}
    glat = 0.0
    gax = 0.0
    for nid, u in disp.items():
        lat = float(np.hypot(u[0], u[2]))   # perp a Y
        oop = abs(u[2])
        glat = max(glat, lat)
        gax = max(gax, abs(u[AXIAL]))
        for z in n2zone.get(nid, ()):
            if z in res:
                if lat > res[z]["lat"]:
                    res[z]["lat"] = lat
                if oop > res[z]["oop"]:
                    res[z]["oop"] = oop
    res["U_lat_global"] = glat
    res["U_globe_axial"] = gax
    res["lam"] = last["lam"]
    return res


def parse_lambda(sta_path: Path):
    if not sta_path.exists():
        return np.nan
    for line in reversed(sta_path.read_text().splitlines()):
        parts = line.split()
        if len(parts) >= 5:
            try:
                return float(parts[4])
            except ValueError:
                continue
    return np.nan


# ---------------------------------------------------------------------------
# 4) loop pelos runs
# ---------------------------------------------------------------------------
runs = []
for tag, k, label in SWEEP:
    p_dat = CASE / f"{PREFIX}_{tag}.dat"
    if not p_dat.exists():
        print(f" [SKIP] {tag}: {p_dat} nao existe")
        continue
    fd = parse_dat(p_dat)
    lam = parse_lambda(CASE / f"{PREFIX}_{tag}.sta")
    kink = parse_frd_kink(tag) or {}
    F_max = float(np.nanmax(fd["F_mag"])) if fd["F_mag"].size else np.nan
    runs.append({
        "tag": tag, "k": k, "label": label,
        "U_globe_mm": fd["U_globe"] * 1e3,
        "F_mag_mN": fd["F_mag"] * 1e3,
        "F_dura_mN": fd["F_dura"] * 1e3,
        "F_pia_mN": fd["F_pia"] * 1e3,
        "F_on_mN": fd["F_on"] * 1e3,
        "F_max_mN": F_max * 1e3, "lam_final": lam, "kink": kink,
    })
    kp = kink.get("pia", {}).get("lat", 0) * 1e3
    print(f"  {tag}: {fd['t'].size} pts, lam_final={lam:.3f}, "
          f"F_max={F_max*1e3:.1f} mN, kink_pia={kp:.3f} mm")

if not runs:
    print("Nenhum run encontrado em", CASE)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# 5) Plot 4 paineis
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle("on-caso-2J (on-caso-2.2) - Sweep de rigidez da gordura orbital (Winkler k)\n"
             "Variante em 'J' (tortuosidade embutida na malha) + SAS solido + "
             "dura ortotropica + globo Dy=-1.5mm",
             fontsize=12)

# Painel A: F-d sobreposto
ax = axes[0, 0]
for i, run in enumerate(runs):
    ax.plot(run["U_globe_mm"], run["F_mag_mN"],
            "o-", color=COLORS[i], label=run["label"], lw=2, markersize=4)
ax.set_xlabel("|U| globo [mm] (compressao axial imposta, -Y)")
ax.set_ylabel("|F| total no engaste posterior [mN]")
ax.set_title("(A) Curva F-d por rigidez da gordura (Winkler k)")
ax.legend(loc="best", fontsize=8)
ax.grid(alpha=0.3)

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
ax.set_title("(B) Reacao de pico no engaste vs rigidez da gordura\n"
             "(gordura mais rigida confina o J -> menor reacao lateral)")
ax.grid(alpha=0.3, which="both")

# Painel C: lambda final de Riks vs k (estabilidade)
ax = axes[1, 0]
lams = [r["lam_final"] for r in runs]
ax.semilogx(ks, lams, "D-", lw=2, markersize=12, color="navy")
for r, k_, lm in zip(runs, ks, lams):
    ax.annotate(f"{lm:.2f}", (k_, lm), xytext=(5, 6),
                textcoords="offset points", fontsize=8)
ax.axhline(1.0, color="k", lw=0.7, ls="--", label="lambda=1 (carga total atingida)")
ax.set_xlabel("Winkler k [Pa/m] - gordura orbital")
ax.set_ylabel("lambda final (Riks)")
ax.set_title("(C) Fator de carga de Riks vs rigidez da gordura")
ax.grid(alpha=0.3, which="both")
ax.legend(loc="best", fontsize=8)

# Painel D: excursao lateral max por camada vs k
ax = axes[1, 1]
camadas = [("on", "orange", "nervo"),
           ("pia", "green",  "pia"),
           ("sas", "cyan",   "SAS"),
           ("dura", "red",   "dura")]
has_kink = any(r["kink"] for r in runs)
if has_kink:
    for nm, c, lab in camadas:
        ys = [r["kink"].get(nm, {}).get("lat", 0) * 1e3 for r in runs]
        ax.semilogx(ks, ys, "o-", lw=2, markersize=10, color=c, label=lab)
    ax.set_ylabel("|U_lat| max [mm]  (perp a Y: sqrt(Ux^2+Uz^2))")
    ax.set_title("(D) Excursao lateral por camada - kink do nervo na geometria J")
    ax.legend(loc="best", fontsize=9)
else:
    ax.text(0.5, 0.5, "Sem .vtu disponivel\n(rode ccx2paraview no host)",
            ha="center", va="center", transform=ax.transAxes, fontsize=11)
    ax.set_title("(D) Excursao lateral por camada - indisponivel")
ax.set_xlabel("Winkler k [Pa/m] - gordura orbital")
ax.grid(alpha=0.3, which="both")

plt.tight_layout(rect=[0, 0, 1, 0.96])
figdir = OUT / "figs"
figdir.mkdir(exist_ok=True)
out_png = figdir / "on-caso-2J_sweep_winkler.png"
plt.savefig(out_png, dpi=140, bbox_inches="tight")
print(f"\nGrafico salvo em: {out_png}")

# ---------------------------------------------------------------------------
# 6) tabela de resumo
# ---------------------------------------------------------------------------
lines = []
lines.append(f"{'tag':<8} {'k[Pa/m]':>10} {'lam':>6} {'F_max[mN]':>10} "
             f"{'lat_on':>9} {'lat_pia':>9} {'lat_sas':>9} {'lat_dura':>9} "
             f"{'oop_dura':>9}")
lines.append("-" * 92)
for r in runs:
    k = r["kink"]
    def g(z, key):
        return k.get(z, {}).get(key, 0) * 1e3
    lines.append(
        f"{r['tag']:<8} {r['k']:>10} {r['lam_final']:>6.2f} "
        f"{r['F_max_mN']:>10.1f} "
        f"{g('on','lat'):>9.3f} {g('pia','lat'):>9.3f} "
        f"{g('sas','lat'):>9.3f} {g('dura','lat'):>9.3f} "
        f"{g('dura','oop'):>9.3f}")
table = "\n".join(lines)
print("\n" + table)
(OUT / "on-caso-2J_sweep_summary.txt").write_text(table + "\n")
print(f"\nTabela salva em: brunaStuff/on-caso-2J_sweep_summary.txt")

# JSON pra reuso
runs_json = [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
              for k, v in r.items()} for r in runs]
(OUT / "on-caso-2J_sweep.json").write_text(json.dumps(runs_json, indent=2))
print(f"JSON dos dados em: brunaStuff/on-caso-2J_sweep.json")

# ---------------------------------------------------------------------------
# 7) figura focada p/ o artigo (figs/on-caso-2j-winkler.png): eixo duplo
#    excursao lateral da pia (esq) e reacao de pico no engaste (dir) vs k_w
# ---------------------------------------------------------------------------
figdir = OUT / "figs"
figdir.mkdir(exist_ok=True)
ks = np.array([r["k"] for r in runs], dtype=float)
lat_pia = np.array([r["kink"].get("pia", {}).get("lat", np.nan) * 1e3 for r in runs])
Fmax = np.array([r["F_max_mN"] for r in runs])

fig2, axL = plt.subplots(figsize=(7.0, 4.6))
cL, cR = "#1f77b4", "#d62728"
l1 = axL.semilogx(ks, lat_pia, "o-", color=cL, lw=2, markersize=9,
                  label="Excursao lateral da pia")
axL.set_xlabel(r"Rigidez da gordura orbital  $k_w$  [Pa/m]")
axL.set_ylabel("Excursao lateral max da pia [mm]", color=cL)
axL.tick_params(axis="y", labelcolor=cL)
axL.grid(alpha=0.3, which="both")
axL.set_ylim(0, max(lat_pia) * 1.15)

axR = axL.twinx()
l2 = axR.semilogx(ks, Fmax, "s--", color=cR, lw=2, markersize=9,
                  label="Reacao de pico no engaste")
axR.set_ylabel("|F| de pico no engaste [mN]", color=cR)
axR.tick_params(axis="y", labelcolor=cR)

# anotacao do baseline (200 kPa/m)
if 200_000 in [int(k) for k in ks]:
    ib = [int(k) for k in ks].index(200_000)
    axL.annotate("baseline\n200 kPa/m", (ks[ib], lat_pia[ib]),
                 xytext=(8, 18), textcoords="offset points", fontsize=8,
                 color="k", ha="left",
                 arrowprops=dict(arrowstyle="->", color="gray", lw=0.8))

axL.set_title("Caso 2J - parametrizacao da gordura orbital (Winkler)\n"
              r"$\lambda=1{,}0$ (estavel) e modo $n=1$ em todo o intervalo",
              fontsize=10)
lines = l1 + l2
axL.legend(lines, [ln.get_label() for ln in lines], loc="upper center", fontsize=9)
fig2.tight_layout()
out_fig = figdir / "on-caso-2j-winkler.png"
fig2.savefig(out_fig, dpi=160, bbox_inches="tight")
print(f"Figura do artigo em: {out_fig}")
