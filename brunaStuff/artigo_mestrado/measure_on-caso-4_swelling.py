#!/usr/bin/env python3
"""
measure_on-caso-4_swelling.py
=============================
Fase A do on-caso-4: a partir dos runs INCHACO-ONLY (P_CONTACT=0, so P_CSF), medir
quanto e onde a bainha (dura) distende e converter isso, por estagio de SANS, na
AREA do patch de contato e na FORCA (P_contact) da arteria oftalmica.

Por que esta etapa existe
-------------------------
No caso 4 a P_contact nao e' mais "chutada": ela e' ANCORADA na distensao real da
bainha. A cadeia fisica e':
   P_CSF elevado -> bainha distende (Dr_dura) -> a arteria (obstaculo fixo em +X,
   z~22.5 mm) sofre MAIOR interferencia -> AREA e FORCA de contato crescem.

Modelo de contato (Hertz-like, encenado/prescrito)
--------------------------------------------------
A arteria e' tratada como um indentador efetivo de raio R_eff encostado na bainha
em (+X, z=22.5 mm). A "aproximacao" (interferencia) por estagio e':
    delta = max(0, Dr_dura - gap0)
onde Dr_dura e' a distensao radial media da dura no setor da arteria (medida do
.frd do run inchaco-only) e gap0 e' a folga inicial arteria-bainha em 1g.

Hertz (indentador esferico/cilindrico): raio de contato a = sqrt(R_eff * delta),
logo a AREA cresce com o inchaco:
    A_contact = pi * a^2 = pi * R_eff * delta        (linear em delta)
A FORCA usa P_contact = k_art * delta (pressao media ~ interferencia), com k_art
calibrado para que o estagio baseline (1g) reproduza P_contact ~ 9034 Pa:
    k_art = P0_baseline / delta(S0)
Assim:
    P_contact(estagio) = P0_baseline * delta(estagio)/delta(S0)
    Forca(estagio)     = P_contact * A ~ delta^2   (superlinear, assinatura Hertz)

Saidas
------
  brunaStuff/on-caso-4_stage_table.json   <- (tag, P_CSF, CONTACT_BOX, P_CONTACT, ...)
                                             consumido por sweep_on-caso-4.sh (Fase B)
  brunaStuff/on-caso-4_swelling.png        <- verificacao do inchaco
  brunaStuff/on-caso-4_swelling_summary.txt
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CASE = Path("cases/on-caso-4/ccx")
OUT = Path("brunaStuff")
PREFIX = "on-caso-4"

# Estagios de SANS (tag_faseA, tag_faseB, P_CSF [Pa], rotulo).
#   tag_faseA  : OUT_TAG do run inchaco-only (lido aqui).
#   tag_faseB  : OUT_TAG do run acoplado (chave da stage_table.json).
STAGES = [
    ("swell_S0", "S0_baseline", 1333, "baseline 1g (~10 mmHg)"),
    ("swell_S1", "S1_mild",     2400, "SANS leve (~18 mmHg)"),
    ("swell_S2", "S2_upper",    3800, "SANS upper (~28 mmHg)"),
    ("swell_S3", "S3_severe",   5500, "severo/compartim. (~41 mmHg)"),
]

# Geometria da bainha / arteria
R_DURA = 2.5e-3      # raio externo nominal da dura [m]
Z_ART = 22.5e-3      # posicao axial da arteria [m]
SECTOR_DEG = 30.0    # meia-abertura angular do setor +X usado p/ medir Dr_dura
DZ_SECTOR = 3.0e-3   # meia-altura axial em torno de Z_ART p/ medir Dr_dura

# Parametros do contato (fenomenologicos, anotados)
GAP0 = 0.0           # folga inicial arteria-bainha em 1g [m] (0 = encostada)
P0_BASELINE = 9034.0 # P_contact alvo no estagio baseline [Pa] (~67 mmHg sistole-diastole)
# Teto FISIOLOGICO da pressao de contato: a arteria oftalmica nao pode pressionar
# acima da sua pressao luminal (~pico sistolico ~135 mmHg = 18068 Pa). Alem disso,
# pressoes focais acima disso esmagam o SAS mole e fazem o solver divergir. Logo
# P_contact satura no sistolico e a FORCA cresce sobretudo pela AREA (engajamento
# progressivo da arteria contra a bainha inchada) -- consistente com a fisiologia.
P_SYS_MAX = 18068.0  # Pa (~135 mmHg, pico sistolico)

# Malha da dura_outer: 24 celulas tangenciais (dtheta=15 deg) x 10 axiais (dz=3 mm).
# Area nominal de UMA face externa da dura:
N_THETA_CELLS = 24
DZ_CELL = 3.0e-3
FACE_AREA = R_DURA * (2.0 * math.pi / N_THETA_CELLS) * DZ_CELL  # ~1.963e-6 m^2

# box do topoSetDict (margens p/ capturar centros de celula)
X_MAX_BOX = 2.60e-3
MARG = 0.06e-3

# -----------------------------------------------------------------------------
# ESCALONAMENTO DA AREA DE CONTATO (engajamento progressivo)
# -----------------------------------------------------------------------------
# Por que NAO usamos Hertz sub-celula: a distensao Dr_dura e' da ordem de poucos
# micrometros, mas as faces da dura_outer sao grossas (~1.96 mm^2, dtheta=15 deg,
# dz=3 mm). Um contato Hertziano de raio sqrt(R_eff*delta) ~ dezenas de um fica
# MUITO menor que uma face -> a area carved nao mudaria entre estagios.
#
# Modelo adotado (encenado, prescrito): conforme a bainha incha, a arteria
# (obstaculo curvo fixo) ENGAJA progressivamente mais faces ao redor de +X,
# z=22.5 mm. O grau de engajamento e' indexado pela razao de interferencia
# ratio = delta/delta(baseline). Cada nivel amplia o box (e a area carved) em
# passos resolviveis pela malha. NB: a area absoluta e' grosseira (malha coarse);
# o que importa e' o ACOPLAMENTO MONOTONICO inchaco -> area -> forca.
#
# A AREA cresce APENAS axialmente (faixa estreita +/-7.5 deg, alongada em z). NB:
# ampliar angularmente (incluir +/-22.5 deg) remove molas Winkler de uma banda
# larga da dura e mal-condiciona a rigidez tangente -> Newton diverge ja' no 1o
# incremento (testado: S2/S3 com colunas +/-22.5 deg nao convergem). O crescimento
# axial mantem o patch no mesmo "tipo" que converge em S0/S1, so mais comprido.
#
# nivel: (theta_half[graus], z_half[m], n_faces_esperado, rotulo)
#   nivel 0: theta=+/-7.5  z=22.5         -> 2 faces  (1 col x 1 axial)
#   nivel 1: theta=+/-7.5  z=19.5..25.5   -> 6 faces  (1 col x 3 axial)
#   nivel 2: theta=+/-7.5  z=16.5..28.5   -> 10 faces (1 col x 5 axial)
#   nivel 3: theta=+/-7.5  z=13.5..28.5   -> 12 faces (1 col x 6 axial)
LEVELS = [
    (11.0,  1.6e-3,  2, "1 col x 1 axial"),
    (11.0,  4.6e-3,  6, "1 col x 3 axial"),
    (11.0,  7.6e-3, 10, "1 col x 5 axial"),
    (11.0, 10.6e-3, 12, "1 col x 6 axial"),
]
# limiares de ratio (delta/delta0) para subir de nivel
RATIO_THRESH = [1.5, 2.5, 3.5]


def ratio_to_level(ratio: float) -> int:
    lvl = 0
    for t in RATIO_THRESH:
        if ratio >= t:
            lvl += 1
    return min(lvl, len(LEVELS) - 1)


# ---------------------------------------------------------------------------
# Parser nativo de CalculiX .frd (ASCII) -- igual ao do analyzer do 3-sf
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
        s = L[13 + 12 * k: 13 + 12 * (k + 1)]
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


# ---------------------------------------------------------------------------
# Medida do inchaco
# ---------------------------------------------------------------------------
def measure_swelling(tag: str):
    """Retorna dict com Dr_dura no setor da arteria, perfis e diagnosticos."""
    frd = CASE / f"{PREFIX}_{tag}.frd"
    if not frd.exists():
        # tenta o nome sem tag (run unico)
        alt = CASE / f"{PREFIX}.frd"
        if alt.exists():
            frd = alt
        else:
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

    r0 = np.hypot(P[:, 0], P[:, 1])
    theta = np.degrees(np.arctan2(P[:, 1], P[:, 0]))
    # nos da casca externa da dura
    m_dura = np.abs(r0 - R_DURA) < 0.06e-3
    # deslocamento radial (outward positivo)
    rhat_x = np.where(r0 > 1e-12, P[:, 0] / np.maximum(r0, 1e-12), 1.0)
    rhat_y = np.where(r0 > 1e-12, P[:, 1] / np.maximum(r0, 1e-12), 0.0)
    U_r = U[:, 0] * rhat_x + U[:, 1] * rhat_y

    # setor da arteria (+X, |theta|<SECTOR_DEG, z proximo de Z_ART)
    m_sector = (m_dura
                & (np.abs(theta) < SECTOR_DEG)
                & (np.abs(P[:, 2] - Z_ART) < DZ_SECTOR))
    dr_sector = float(U_r[m_sector].mean()) if m_sector.sum() else 0.0

    # perfil Dr_dura(z) no setor +X (todas as alturas)
    m_xpos = m_dura & (np.abs(theta) < SECTOR_DEG)
    zs = P[m_xpos, 2]
    urs = U_r[m_xpos]
    order = np.argsort(zs)
    z_prof = zs[order]
    ur_prof = urs[order]

    # uniformidade angular: Dr medio na altura Z_ART, por theta
    m_zring = m_dura & (np.abs(P[:, 2] - Z_ART) < DZ_SECTOR)
    dr_global_mean = float(U_r[m_dura].mean()) if m_dura.sum() else 0.0
    dr_global_max = float(U_r[m_dura].max()) if m_dura.sum() else 0.0

    return {
        "tag": tag,
        "dr_sector_m": dr_sector,
        "dr_global_mean_m": dr_global_mean,
        "dr_global_max_m": dr_global_max,
        "z_prof": z_prof,
        "ur_prof": ur_prof,
        "n_sector_nodes": int(m_sector.sum()),
        "n_ring_nodes": int(m_zring.sum()),
    }


def level_to_box(theta_half_deg: float, z_half: float) -> str:
    """Constroi o box do topoSetDict_contact que captura os CENTROS das celulas
    da dura ate theta_half (graus) e z_half (m) em torno de (+X, Z_ART)."""
    th = math.radians(theta_half_deg)
    x_min = R_DURA * math.cos(th) - MARG
    y_half = R_DURA * math.sin(th) + MARG
    z_lo = Z_ART - z_half - MARG
    z_hi = Z_ART + z_half + MARG
    return (f"({x_min:.4e} {-y_half:.4e} {z_lo:.4e}) "
            f"({X_MAX_BOX:.4e} {y_half:.4e} {z_hi:.4e})")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    runs = []
    for a_tag, b_tag, pcsf, label in STAGES:
        m = measure_swelling(a_tag)
        if m is None:
            print(f"  [SKIP] {a_tag}: {CASE/(PREFIX+'_'+a_tag+'.frd')} nao existe "
                  f"(rode a Fase A: bash brunaStuff/sweep_on-caso-4.sh phaseA)")
            continue
        m["tag"] = b_tag          # chave para a Fase B
        m["a_tag"] = a_tag
        m["P_CSF"] = pcsf
        m["label"] = label
        runs.append(m)
        print(f"  {a_tag}: P_CSF={pcsf:>5} Pa | Dr_setor={m['dr_sector_m']*1e6:7.2f} um "
              f"| Dr_global_mean={m['dr_global_mean_m']*1e6:7.2f} um "
              f"| nos_setor={m['n_sector_nodes']}")

    if not runs:
        print("\nNenhum run de Fase A encontrado. Rode primeiro:")
        print("  bash brunaStuff/sweep_on-caso-4.sh phaseA")
        raise SystemExit(1)

    # calibra k_art pelo estagio baseline (primeiro run disponivel)
    base = runs[0]
    delta0 = max(1e-12, base["dr_sector_m"] - GAP0)
    k_art = P0_BASELINE / delta0
    print(f"\n  Calibracao: delta(baseline)={delta0*1e6:.2f} um -> "
          f"k_art = {k_art:.3e} Pa/m (P0={P0_BASELINE:.0f} Pa)")

    # monta tabela de estagios
    table = []
    for m in runs:
        delta = max(0.0, m["dr_sector_m"] - GAP0)
        ratio = delta / delta0
        lvl = ratio_to_level(ratio)
        theta_half_deg, z_half, n_faces, lvl_label = LEVELS[lvl]
        A = n_faces * FACE_AREA          # area nominal carved [m^2]
        A_mm2 = A * 1e6
        p_contact = min(k_art * delta, P_SYS_MAX)   # satura no sistolico
        box = level_to_box(theta_half_deg, z_half)
        F = p_contact * A                # forca total = pressao * area
        entry = {
            "tag": m["tag"],
            "label": m["label"],
            "P_CSF": m["P_CSF"],
            "dr_sector_um": round(m["dr_sector_m"] * 1e6, 4),
            "delta_um": round(delta * 1e6, 4),
            "ratio": round(ratio, 3),
            "level": lvl,
            "level_label": lvl_label,
            "n_faces": n_faces,
            "A_contact_mm2": round(A_mm2, 4),
            "P_CONTACT": round(p_contact, 1),
            "force_mN": round(F * 1e3, 4),
            "CONTACT_BOX": box,
        }
        table.append(entry)
        print(f"  {m['tag']:<12} delta={entry['delta_um']:7.2f} um  ratio={ratio:4.2f}  "
              f"nivel {lvl} ({lvl_label})  A={entry['A_contact_mm2']:6.3f} mm2  "
              f"P_contact={entry['P_CONTACT']:8.1f} Pa  F={entry['force_mN']:.3f} mN")

    meta = {
        "params": {
            "gap0_m": GAP0, "P0_baseline_Pa": P0_BASELINE,
            "P_sys_max_Pa": P_SYS_MAX,
            "k_art_Pa_per_m": k_art, "face_area_m2": FACE_AREA,
            "R_dura_m": R_DURA, "z_art_m": Z_ART,
            "ratio_thresholds": RATIO_THRESH,
        },
        "stages": table,
    }
    out_json = OUT / "on-caso-4_stage_table.json"
    out_json.write_text(json.dumps(meta, indent=2))
    print(f"\nTabela de estagios salva em: {out_json}")
    print("  -> consumida por: bash brunaStuff/sweep_on-caso-4.sh phaseB")

    # ----- plot de verificacao -----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("on-caso-4 Fase A - inchaco da bainha (so P_CSF, sem arteria)\n"
                 "verificacao da distensao Dr_dura e mapeamento p/ area+forca de contato",
                 fontsize=12)
    colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(runs)))

    # (A) perfil Dr_dura(z) no setor +X (media por bin de z p/ curva limpa)
    ax = axes[0, 0]
    for m, c in zip(runs, colors):
        zb = np.round(m["z_prof"] * 1e3).astype(int)
        zs_u = np.unique(zb)
        ur_u = np.array([m["ur_prof"][zb == z].mean() * 1e6 for z in zs_u])
        ax.plot(ur_u, zs_u, "o-", color=c, lw=1.6, markersize=4,
                label=f"{m['tag']} (P_CSF={m['P_CSF']})")
    ax.axhline(Z_ART * 1e3, ls="--", color="gray", lw=1, label="z arteria=22.5 mm")
    ax.set_xlabel("Dr_dura (distensao radial outward) [um]")
    ax.set_ylabel("z [mm]")
    ax.set_title("(A) perfil de inchaco da bainha ao longo do eixo (setor +X)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    pcsfs = [m["P_CSF"] for m in runs]
    # (B) Dr_dura no setor da arteria vs P_CSF
    ax = axes[0, 1]
    drs = [m["dr_sector_m"] * 1e6 for m in runs]
    ax.plot(pcsfs, drs, "o-", color="teal", lw=2, markersize=10)
    for x, y in zip(pcsfs, drs):
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8)
    ax.set_xlabel("P_CSF [Pa]")
    ax.set_ylabel("Dr_dura no setor da arteria [um]")
    ax.set_title("(B) inchaco vs P_CSF (motor do SANS)")
    ax.grid(alpha=0.3)

    # (C) area de contato vs estagio
    ax = axes[1, 0]
    tags = [e["tag"] for e in table]
    As = [e["A_contact_mm2"] for e in table]
    ax.bar(tags, As, color="indianred", alpha=0.85)
    for i, a in enumerate(As):
        ax.text(i, a, f"{a:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("area de contato A [mm^2]")
    ax.set_title("(C) AREA cresce com o inchaco (engajamento progressivo de faces)")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(alpha=0.3, axis="y")

    # (D) P_contact e forca vs estagio
    ax = axes[1, 1]
    pcs = [e["P_CONTACT"] for e in table]
    ax.plot(tags, pcs, "s-", color="navy", lw=2, markersize=9, label="P_contact [Pa]")
    ax.set_ylabel("P_contact [Pa]", color="navy")
    ax.tick_params(axis="y", labelcolor="navy")
    ax2 = ax.twinx()
    Fs = [e["force_mN"] for e in table]
    ax2.plot(tags, Fs, "^--", color="darkorange", lw=2, markersize=9, label="forca [mN]")
    ax2.set_ylabel("forca de contato [mN]", color="darkorange")
    ax2.tick_params(axis="y", labelcolor="darkorange")
    ax.set_title("(D) FORCA cresce com o inchaco (F = P_contact*A ~ delta^2)")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_png = OUT / "on-caso-4_swelling.png"
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    print(f"Grafico de verificacao: {out_png}")

    # ----- summary txt -----
    lines = [
        "on-caso-4 Fase A - inchaco da bainha e mapeamento p/ contato arterial",
        "=" * 84,
        f"params: gap0={GAP0*1e6:.1f} um, P0_baseline={P0_BASELINE:.0f} Pa, "
        f"k_art={k_art:.3e} Pa/m, face_area={FACE_AREA*1e6:.3f} mm2, "
        f"ratio_thresh={RATIO_THRESH}",
        "",
        f"{'tag':<12}{'P_CSF':>7}{'Dr_um':>8}{'ratio':>7}{'nivel':>7}"
        f"{'faces':>7}{'A_mm2':>9}{'P_contact':>11}{'F_mN':>9}",
        "-" * 84,
    ]
    for e in table:
        lines.append(f"{e['tag']:<12}{e['P_CSF']:>7}{e['dr_sector_um']:>8.2f}"
                     f"{e['ratio']:>7.2f}{e['level']:>7}{e['n_faces']:>7}"
                     f"{e['A_contact_mm2']:>9.3f}{e['P_CONTACT']:>11.1f}"
                     f"{e['force_mN']:>9.3f}")
    lines.append("")
    lines.append("CONTACT_BOX por estagio (p/ topoSetDict_contact, em metros):")
    for e in table:
        lines.append(f"  {e['tag']:<12} {e['CONTACT_BOX']}")
    txt = "\n".join(lines)
    (OUT / "on-caso-4_swelling_summary.txt").write_text(txt + "\n")
    print("\n" + txt)
    print(f"\nResumo: brunaStuff/on-caso-4_swelling_summary.txt")


if __name__ == "__main__":
    main()
