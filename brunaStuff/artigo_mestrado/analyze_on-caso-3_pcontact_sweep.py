#!/usr/bin/env python3
"""
Sweep analysis para on-caso-3: varia P_contact (arteria oftalmica focal) 
em 0 -> 18068 Pa, com Winkler fixo em 2 MPa/m (SANS).

Le N runs (cada um com sufixo _<tag>.dat e .frd opcionalmente convertido para .vtu)
e produz on-caso-3_pcontact_sweep.png com 4 paineis:
  (A) Curvas F-Dz sobrepostas (1 cor por P_contact)
  (B) F_max no engaste vs P_contact (impacto na carga de pico aparente)
  (C) Kink lateral max por camada (on, pia, sas, dura) vs P_contact
  (D) Indentation local da dura no ponto de contato (U_radial em z=22.5) vs P_contact

Tabela de resumo em on-caso-3_pcontact_sweep_summary.txt.
JSON dos dados em on-caso-3_pcontact_sweep.json.
"""
import re
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-3/ccx")
OUT = Path("brunaStuff")

# (tag, Pc em Pa, rotulo curto, rotulo longo)
SWEEP = [
    ("Pc0",         0, "0 Pa",      "0 Pa     (sem arteria)"),
    ("Pc4517",   4517, "4.5 kPa",   "4517 Pa  (0.5x, ~33 mmHg)"),
    ("Pc9034",   9034, "9.0 kPa",   "9034 Pa  (1.0x, ~67 mmHg, baseline)"),
    ("Pc13551", 13551, "13.6 kPa",  "13551 Pa (1.5x, ~100 mmHg)"),
    ("Pc18068", 18068, "18.1 kPa",  "18068 Pa (2.0x, ~135 mmHg, pico sistolico)"),
]
COLORS = plt.cm.plasma(np.linspace(0.05, 0.85, len(SWEEP)))


# ---------------------------------------------------------------------------
# 1) parse on-caso-3_<tag>.dat (formato identico ao on-caso-2g)
# ---------------------------------------------------------------------------
def parse_dat(path: Path):
    """Extrai por incremento: tempo, Dz_globo, RF_z de cada NSET monitorado."""
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
    Dz, F_dura, F_pia, F_on, F_globo = [], [], [], [], []
    for t in times:
        d = rec[t]
        Dz.append(d["U_ANTERIOR_GLOBO"][2] if "U_ANTERIOR_GLOBO" in d else np.nan)
        F_dura.append(d.get("RF_POSTERIOR_DURA", [0, 0, 0])[2])
        F_pia.append( d.get("RF_POSTERIOR_PIA",  [0, 0, 0])[2])
        F_on.append(  d.get("RF_POSTERIOR_ON",   [0, 0, 0])[2])
        F_globo.append(d.get("RF_ANTERIOR_GLOBO", [0, 0, 0])[2])
    return (np.array(times), np.array(Dz),
            np.array(F_dura), np.array(F_pia),
            np.array(F_on), np.array(F_globo))


# ---------------------------------------------------------------------------
# 2) parser nativo de CalculiX .frd (ASCII) -- evita dependencia de vtk/vtu
# ---------------------------------------------------------------------------
def _parse_data_line(L: str, n_floats: int):
    """Le uma linha CCX fixed-width '-1' (formato I3,I10,N*E12.5).
    Necessario porque sinais negativos colam ao node_id ou ao expoente
    (ex.: ' -1         5-2.50000E-04 ...') -> split() falharia.
    Retorna (node_id, [v1, v2, ..., vN]) ou None se invalido.
    """
    if len(L) < 3 + 10 + 12:
        return None
    try:
        nid = int(L[3:13])
    except ValueError:
        return None
    vals = []
    for k in range(n_floats):
        s = L[13 + 12*k : 13 + 12*(k + 1)]
        if not s:
            return None
        try:
            vals.append(float(s))
        except ValueError:
            return None
    return nid, vals


def parse_frd_last_disp(path: Path):
    """Le o .frd e retorna (nodes_dict, last_disp_dict).

    nodes_dict:     {node_id: (x, y, z)}
    last_disp_dict: {node_id: (ux, uy, uz)} no ULTIMO bloco DISP encontrado.

    Formato CCX .frd ASCII fixed-width (I3,I10,N*E12.5):
      - bloco '2C ... N_NODES' seguido de linhas '-1 NID X Y Z' ate '-3'
      - varios blocos '100C ...' (1 por incremento salvo) com varios '-4 VAR ...'
        sub-blocos, cada um com linhas '-1 NID V1 V2 V3 [|V|]' ate '-3'
    """
    nodes = {}
    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    # phase 1: nodes (2C)
    in_nodes = False
    for L in lines:
        s = L.strip()
        if not in_nodes:
            if s.startswith("2C ") or s == "2C":
                in_nodes = True
            continue
        if s.startswith("-3"):
            in_nodes = False
            break
        if L.lstrip().startswith("-1"):
            r = _parse_data_line(L, 3)
            if r is not None:
                nid, xyz = r
                nodes[nid] = (xyz[0], xyz[1], xyz[2])

    # phase 2: blocos DISP (acumula em disp_blocks, pega o ultimo).
    # DISP tem 4 componentes (D1, D2, D3, ALL=magnitude) -> 4 floats por linha.
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
            continue  # cabecalho de componente
        if L.lstrip().startswith("-1"):
            # DISP data: 3 floats por linha (D1=UX, D2=UY, D3=UZ).
            # O header -4 declara 4 componentes mas o 4o (ALL=magnitude) e'
            # derivado, nao escrito em disco.
            r = _parse_data_line(L, 3)
            if r is not None:
                nid, vs = r
                cur[nid] = (vs[0], vs[1], vs[2])

    # Quando o Riks DIVERGE catastroficamente, o CCX as vezes grava um ULTIMO
    # bloco DISP com deslocamentos absurdos (>1 m, NaN-like). Filtramos esse
    # caso pegando o ultimo bloco com |U|_max < 100 mm (sanity check).
    MAX_REASONABLE_U = 0.1  # 100 mm
    last_disp = {}
    for blk in reversed(disp_blocks):
        u_max = max((max(abs(v) for v in uvw) for uvw in blk.values()),
                    default=0.0)
        if u_max < MAX_REASONABLE_U:
            last_disp = blk
            break
    return nodes, last_disp


def parse_frd_kink(tag: str):
    """Le o ULTIMO incremento do .frd e retorna kink lateral por camada
    + indent radial local no patch de contato."""
    frd = CASE / f"on-caso-3_{tag}.frd"
    if not frd.exists():
        return None
    nodes, disp = parse_frd_last_disp(frd)
    if not nodes or not disp:
        return None
    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    # U pode nao ter todos os nos (ALL_NODES vs subset); preencher com 0
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
        if m.sum() == 0:
            res[name] = 0.0
        else:
            U_lat = np.sqrt(U[m, 0]**2 + U[m, 1]**2)
            res[name] = float(U_lat.max())
    res["Dz_max"] = float(np.abs(U[:, 2]).max())
    res["U_lat_global"] = float(np.sqrt(U[:, 0]**2 + U[:, 1]**2).max())

    # Indentation local: U_radial nos nos da dura externa (r~2.5) no patch
    # de contato. Os 6 nos do patch estao em z={21, 24} mm e theta={-15, 0, +15} deg
    # (cantos das 2 faces). Usa-se janela [20.9, 24.1] com tolerancia em z e
    # x > 2.4 mm (cos(15)*2.5 = 2.415) p/ pegar todos os 6.
    mask_dura = np.abs(r0 - 2.5e-3) < 0.06e-3
    mask_z    = (P[:, 2] > 20.9e-3) & (P[:, 2] < 24.1e-3)
    mask_x    = P[:, 0] > 2.4e-3
    m_local = mask_dura & mask_z & mask_x
    if m_local.sum() > 0:
        rhat_x = P[m_local, 0] / r0[m_local]
        rhat_y = P[m_local, 1] / r0[m_local]
        U_r = U[m_local, 0] * rhat_x + U[m_local, 1] * rhat_y
        res["U_r_contact_min"]  = float(U_r.min())
        res["U_r_contact_mean"] = float(U_r.mean())
        res["n_nodes_contact"]  = int(m_local.sum())
    else:
        res["U_r_contact_min"]  = 0.0
        res["U_r_contact_mean"] = 0.0
        res["n_nodes_contact"]  = 0
    return res


# ---------------------------------------------------------------------------
# 3) loop pelos runs
# ---------------------------------------------------------------------------
runs = []
for tag, pc, short, label in SWEEP:
    p_dat = CASE / f"on-caso-3_{tag}.dat"
    p_sta = CASE / f"on-caso-3_{tag}.sta"
    if not p_dat.exists():
        print(f" [SKIP] {tag}: {p_dat} nao existe")
        continue
    t, Dz, Fd, Fp, Fo, Fg = parse_dat(p_dat)
    # forca compressiva total nas BC posteriores
    F_eng = -(Fd + Fp + Fo)
    kink = parse_frd_kink(tag) or {}
    # lambda final (do .sta)
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
    F_max = float(np.nanmax(np.abs(F_eng))) if F_eng.size else 0.0
    Dz_at_Fmax = (float(Dz[np.nanargmax(np.abs(F_eng))]) * 1e3
                  if F_eng.size else 0.0)
    runs.append({
        "tag": tag, "pc": pc, "short": short, "label": label,
        "t": t, "Dz_mm": Dz * 1e3, "F_eng_mN": F_eng * 1e3,
        "F_dura_mN": -Fd * 1e3, "F_pia_mN": -Fp * 1e3, "F_on_mN": -Fo * 1e3,
        "F_max_mN": F_max * 1e3, "Dz_at_Fmax_mm": Dz_at_Fmax,
        "lam_final": lam_final, "kink": kink,
    })
    print(f"  {tag}: {len(t)} pts, lam_final={lam_final:.3f}, "
          f"F_max={F_max*1e3:.1f} mN, "
          f"kink_pia={kink.get('pia', 0)*1e3:.3f} mm, "
          f"U_r_contact={kink.get('U_r_contact_min', 0)*1e3:.4f} mm")

if not runs:
    print("Nenhum run encontrado em", CASE)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# 4) 4-panel plot
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15.5, 11.5))
fig.suptitle(
    "on-caso-3 - Sweep de P_contact (arteria oftalmica focal)\n"
    "Caso 2 (V14b) + P_contact apenas: Winkler k=200 kPa/m baseline + "
    "SAS solido + Dz=-1.5 mm Riks",
    fontsize=11)

# Painel A: F-Dz sobreposto
ax = axes[0, 0]
for i, run in enumerate(runs):
    ax.plot(np.abs(run["Dz_mm"]), np.abs(run["F_eng_mN"]),
            "o-", color=COLORS[i], label=run["label"], lw=2, markersize=4)
ax.set_xlabel("|Dz| globo [mm] (compressao axial)")
ax.set_ylabel("|F_z| total no engaste posterior [mN]")
ax.set_title("(A) Curva F-Dz - P_contact desloca a resposta axial")
ax.legend(loc="best", fontsize=8)
ax.grid(alpha=0.3)

# Painel B: F_max vs P_contact
ax = axes[0, 1]
pcs = [r["pc"] for r in runs]
Fmaxs = [r["F_max_mN"] for r in runs]
ax.plot(pcs, Fmaxs, "o-", lw=2, markersize=12, color="darkred")
for r, pc_, fm in zip(runs, pcs, Fmaxs):
    ax.annotate(r["short"], (pc_, fm), xytext=(6, -12),
                textcoords="offset points", fontsize=8)
ax.set_xlabel("P_contact [Pa] - arteria oftalmica focal")
ax.set_ylabel("F_max no engaste [mN]")
ax.set_title("(B) Forca axial de pico vs pressao focal externa")
ax.grid(alpha=0.3)

# Painel C: kink lateral por camada vs P_contact
ax = axes[1, 0]
camadas = [("on",  "orange", "nervo (r=0.5)"),
           ("pia", "green",  "pia (r=1.55)"),
           ("sas", "cyan",   "SAS (r=2.0)"),
           ("dura", "red",   "dura (r=2.5)")]
for nm, c, lab in camadas:
    ys = [r["kink"].get(nm, 0) * 1e3 for r in runs]
    ax.plot(pcs, ys, "o-", lw=2, markersize=10, color=c, label=lab)
ax.set_xlabel("P_contact [Pa] - arteria oftalmica focal")
ax.set_ylabel("|U_lat| max [mm] (kink lateral por camada)")
ax.set_title("(C) Kink global por camada - dura amplifica MUITO (5.6x), pia/nervo pouco")
ax.legend(loc="best", fontsize=9)
ax.grid(alpha=0.3)

# Painel D: indentation local da dura no ponto de contato
ax = axes[1, 1]
ur_min = [r["kink"].get("U_r_contact_min", 0) * 1e3 for r in runs]
ur_mean = [r["kink"].get("U_r_contact_mean", 0) * 1e3 for r in runs]
ax.plot(pcs, np.abs(ur_min), "o-", lw=2, markersize=12, color="navy",
        label="|U_r|_max (pico de afundamento)")
ax.plot(pcs, np.abs(ur_mean), "s--", lw=1.5, markersize=8, color="steelblue",
        label="|U_r|_medio (no patch contato)")
# Ajuste linear para extrair compliance focal da membrana dura
if len(pcs) >= 2:
    coef = np.polyfit(pcs, np.abs(ur_min), 1)  # [a, b] em mm/Pa, mm
    a, b = coef
    pc_fit = np.linspace(0, max(pcs), 50)
    ax.plot(pc_fit, a*pc_fit + b, ":", color="gray", lw=1.5,
            label=f"linear: {a*1e3:.2f} um/kPa\n  -> compliance focal "
                  f"membrana ~ {1/(a*1e3):.2f} kPa/um")
ax.set_xlabel("P_contact [Pa] - arteria oftalmica focal")
ax.set_ylabel("|U_r| dura no patch de contato [mm]")
ax.set_title("(D) Afundamento LOCAL da dura sob a arteria (z=22.5 mm, +X)\n"
             "(contact_local sem Winkler -> resposta = membrane stiffness)",
             fontsize=10)
ax.legend(loc="best", fontsize=8)
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_png = OUT / "on-caso-3_pcontact_sweep.png"
plt.savefig(out_png, dpi=140, bbox_inches="tight")
print(f"\nGrafico salvo em: {out_png}")


# ---------------------------------------------------------------------------
# 5) tabela de resumo
# ---------------------------------------------------------------------------
lines = []
lines.append(
    f"{'tag':<8} {'Pc[Pa]':>7} {'lam':>6} {'F_max[mN]':>10} {'Dz@Fmax[mm]':>12} "
    f"{'kink_on':>9} {'kink_pia':>10} {'kink_dura':>10} "
    f"{'Ur_min[mm]':>11}")
lines.append("-" * 96)
for r in runs:
    k = r["kink"]
    lines.append(
        f"{r['tag']:<8} {r['pc']:>7} {r['lam_final']:>6.2f} "
        f"{r['F_max_mN']:>10.2f} {r['Dz_at_Fmax_mm']:>12.3f} "
        f"{k.get('on',0)*1e3:>9.3f} {k.get('pia',0)*1e3:>10.3f} "
        f"{k.get('dura',0)*1e3:>10.3f} "
        f"{k.get('U_r_contact_min',0)*1e3:>11.4f}")
table = "\n".join(lines)
print("\n" + table)
(OUT / "on-caso-3_pcontact_sweep_summary.txt").write_text(table + "\n")
print(f"\nTabela salva em: brunaStuff/on-caso-3_pcontact_sweep_summary.txt")

# JSON pra reuso
runs_json = [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
              for k, v in r.items()} for r in runs]
(OUT / "on-caso-3_pcontact_sweep.json").write_text(json.dumps(runs_json, indent=2))
print(f"JSON dos dados em: brunaStuff/on-caso-3_pcontact_sweep.json")
