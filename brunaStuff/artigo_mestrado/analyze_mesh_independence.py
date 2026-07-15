#!/usr/bin/env python3
"""
analyze_mesh_independence.py
============================
Estudo de independencia de malha para on-caso-2, on-caso-2.2 e on-caso-3.

Para cada caso, varios niveis de refino (fator global no blockMeshDict) foram
rodados em cases/_mi/<caso>__f<NNN>/ccx (o nivel f100 = baseline e' o caso de
producao em cases/<caso>/ccx).

DUAS familias de indicadores sao reportadas:

  (1) GLOBAL "mole" -- rigidez axial PRE-flambagem k_axial (do .dat). Robusta
      mesmo quando o run diverge cedo, mas e' uma grandeza global pouco
      sensivel a resolucao local.

  (2) LOCAL/MODAL (do .frd, apenas on-caso-2) -- pico de tensao de von Mises e
      o "kink" lateral por camada (pia, dura) com a razao kink_pia/kink_dura,
      assinatura do modo S confinado. Estes sao os RESULTADOS-CHAVE do estudo;
      a convergencia em k_axial NAO garante a convergencia destes.

Os runs atingem load factors (lambda) diferentes (o fino diverge cedo). Por
isso ha duas leituras dos indicadores locais:
  - SECANTE pre-flambagem ancorada na origem, avaliada num deslocamento comum
    pequeno Dz_c=0.1 mm (interpolacao linear 0 -> primeiro incremento). E' a
    comparacao JUSTA entre malhas que nao compartilham lambda (mesma logica do
    k_axial secante).
  - CARGA PLENA (lambda=1.0, Dz=1.5 mm), so' para as malhas que a alcancaram,
    expondo o modo de flambagem TOTALMENTE DESENVOLVIDO (razao pia/dura).

Saidas:
  brunaStuff/mesh_independence_summary.txt
  brunaStuff/mesh_independence.png
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frd_stress import analyze_frd, parse_frd  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "brunaStuff"
PNG = OUT_DIR / "mesh_independence.png"
SUMMARY = OUT_DIR / "mesh_independence_summary.txt"

DZ_NOMINAL = 1.5e-3   # m, amplitude do Dz/Dy prescrito (DZRAMP, time 0->1)
DZ_LIN = 0.2e-3       # m, janela do ajuste linear (|Dz| <= DZ_LIN)
DZ_COMMON = 0.1e-3    # m, ponto de cross-check / secante comum

# nCells por fator (do log.blockMesh). f200 = refino global fator 2 (38016).
# radNN = refino RADIAL dirigido das laminas pia/dura (atualizado dinamicamente
# pela contagem de hexes lida do proprio .frd, ver ncells_from_frd()).
NCELLS = {"f050": 819, "f100": 4752, "f150": 16587, "f200": 38016}

CASES = {
    "on-caso-2":   {"deck": "on-caso-2",   "label": "Caso 2 (saudavel)"},
    "on-caso-2.2": {"deck": "on-caso-2.2", "label": "Caso 2.2 (tortuosidade J)"},
    "on-caso-3":   {"deck": "on-caso-3",   "label": "Caso 3 (SANS arteria)"},
}
LEVELS = ["f050", "f100", "f150", "f200"]

# Niveis com indicadores LOCAIS/MODAIS (von Mises + kink), por caso. Inclui o
# refino radial dirigido (rad*) das laminas, quando presente.
LOCAL_LEVELS = {
    "on-caso-2":   ["f050", "f100", "f150", "f200",
                    "radpia2dura3", "radpia3dura4"],
    "on-caso-2.2": ["f050", "f100", "f150",
                    "radpia2dura3", "radpia3dura4"],
}


def parse_dat(path: Path):
    """Retorna totals[nset]=list[(t,fx,fy,fz)] e disp[nset]=list[(t,ux,uy,uz)]."""
    totals: dict[str, list] = {}
    disp: dict[str, list] = {}
    if not path.exists():
        return totals, disp
    text = path.read_text()
    pat_force = re.compile(
        r"total\s+force.*?for\s+set\s+(\w+)\s+and\s+time\s+([\-+\d\.E]+)"
        r"\s+([\-+\d\.E]+)\s+([\-+\d\.E]+)\s+([\-+\d\.E]+)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pat_force.finditer(text):
        nset, t, fx, fy, fz = m.groups()
        totals.setdefault(nset.upper(), []).append(
            (float(t), float(fx), float(fy), float(fz)))
    pat_disp = re.compile(
        r"displacements.*?for\s+set\s+(\w+)\s+and\s+time\s+([\-+\d\.E]+)\n([^*]*?)(?=\n\s*\n|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pat_disp.finditer(text):
        nset, t, body = m.groups()
        comps = [[], [], []]
        for line in body.splitlines():
            p = line.split()
            if len(p) >= 4:
                try:
                    for i in range(3):
                        comps[i].append(float(p[1 + i]))
                except ValueError:
                    pass
        if comps[0]:
            disp.setdefault(nset.upper(), []).append(
                (float(t), float(np.mean(comps[0])),
                 float(np.mean(comps[1])), float(np.mean(comps[2]))))
    return totals, disp


def loaded_axis(totals) -> int:
    """Detecta o eixo carregado (1=x,2=y,3=z) pela maior |F| no ANTERIOR_GLOBO."""
    rows = totals.get("ANTERIOR_GLOBO", [])
    if not rows:
        return 3
    arr = np.array(rows)  # t,fx,fy,fz
    mags = [np.abs(arr[:, 1]).max(), np.abs(arr[:, 2]).max(), np.abs(arr[:, 3]).max()]
    return int(np.argmax(mags)) + 1  # 1,2,3


def compute_level(dat: Path):
    totals, _ = parse_dat(dat)
    if "ANTERIOR_GLOBO" not in totals or not totals["ANTERIOR_GLOBO"]:
        return None
    axis = loaded_axis(totals)
    arr = np.array(totals["ANTERIOR_GLOBO"])  # t,fx,fy,fz
    # remove duplicatas de tempo (cutbacks reescrevem o mesmo lambda)
    by_t = {}
    for row in arr:
        by_t[round(float(row[0]), 9)] = row
    arr = np.array(sorted(by_t.values(), key=lambda r: r[0]))
    t = arr[:, 0]
    F = np.abs(arr[:, axis])             # |F| no eixo carregado
    Dz = DZ_NOMINAL * t                  # deslocamento imposto (m), DZRAMP linear
    lam_max = float(t.max())

    # inclui a origem (carga 0 -> forca 0)
    Dz = np.concatenate([[0.0], Dz])
    F = np.concatenate([[0.0], F])

    F_common = float(np.interp(DZ_COMMON, Dz, F)) if Dz.max() >= DZ_COMMON else float("nan")
    k = abs(F_common) / DZ_COMMON if np.isfinite(F_common) else float("nan")

    return dict(axis=axis, k_axial=k, F_common=F_common,
                lam_max=lam_max, Dz=Dz, F=F, npts=len(Dz) - 1)


# --------------------------------------------------------------------------
# Indicadores LOCAIS/MODAIS (do .frd)
# --------------------------------------------------------------------------

def ncells_from_frd(path: Path) -> int:
    """Conta hexaedros estruturais (nos mapeados a zonas) do proprio .frd."""
    _, n2zone, _ = parse_frd(path)
    # n2zone e' por no; precisamos do n de elementos -> reusa o parser completo
    # (parse_frd ja' descartou molas). Recontagem barata via 3C header seria
    # ambigua (inclui molas); aqui aproximamos por contagem de elementos hex.
    # parse_frd nao retorna elementos; reabrimos so' o cabecalho 3C estrutural.
    nhex = 0
    in_elems = False
    pend_mat = None
    # materiais estruturais = 1..8 (ON..GLOBO); molas sao 9+.
    for raw in path.read_text().splitlines():
        s = raw
        st = s.strip()
        if re.match(r"\s*3C\b", s):
            in_elems = True
            continue
        if in_elems:
            if st.startswith("-3"):
                break
            if s[1:3] == "-1":
                mat = int(s[23:28]) if len(s) >= 28 else 0
                if 1 <= mat <= 8:
                    nhex += 1
    return nhex


def frd_secant(steps, dz_c_m=DZ_COMMON):
    """Secante pre-flambagem ancorada na origem, avaliada em Dz_c.

    Retorna dict com vm_global, vm_pia, vm_dura (Pa) e kink_pia, kink_dura (m)
    interpolados linearmente entre a origem e os incrementos disponiveis.
    """
    if not steps:
        return None
    dz = np.array([0.0] + [s["dz_mm"] * 1e-3 for s in steps])
    if dz.max() < dz_c_m:
        return None

    def interp(getter):
        y = np.array([0.0] + [getter(s) for s in steps])
        return float(np.interp(dz_c_m, dz, y))

    vm_g = interp(lambda s: s["vm_global_max"])
    vm_p = interp(lambda s: s["vm_zone_max"].get("pia", np.nan))
    vm_d = interp(lambda s: s["vm_zone_max"].get("dura", np.nan))
    kp = interp(lambda s: s["ulat_zone_max"].get("pia", np.nan))
    kd = interp(lambda s: s["ulat_zone_max"].get("dura", np.nan))
    return dict(vm_global=vm_g, vm_pia=vm_p, vm_dura=vm_d,
                kink_pia=kp, kink_dura=kd,
                ratio=(kp / kd if kd else float("nan")))


def frd_fullload(steps, lam_min=0.99):
    """Indicadores no maior lambda atingido (modo plenamente desenvolvido).

    Retorna None se nenhum passo atingiu lambda>=lam_min (carga ~plena).
    """
    if not steps:
        return None
    last = max(steps, key=lambda s: s["lam"])
    kp = last["ulat_zone_max"].get("pia", float("nan"))
    kd = last["ulat_zone_max"].get("dura", float("nan"))
    vz = last["vm_zone_max"]
    return dict(lam=last["lam"], full=last["lam"] >= lam_min,
                vm_global=last["vm_global_max"],
                vm_pia=vz.get("pia", float("nan")),
                vm_dura=vz.get("dura", float("nan")),
                vm_sclera_ring=vz.get("sclera_ring", float("nan")),
                kink_pia=kp, kink_dura=kd,
                ratio=(kp / kd if kd else float("nan")))


def dat_path(case: str, deck: str, level: str) -> Path:
    if level == "f100":
        return REPO / "cases" / case / "ccx" / f"{deck}.dat"
    return REPO / "cases" / "_mi" / f"{case}__{level}" / "ccx" / f"{deck}.dat"


def frd_path(case: str, deck: str, level: str) -> Path:
    if level == "f100":
        return REPO / "cases" / case / "ccx" / f"{deck}.frd"
    return REPO / "cases" / "_mi" / f"{case}__{level}" / "ccx" / f"{deck}.frd"


def main():
    lines = []
    p = lines.append
    p("=" * 78)
    p("ESTUDO DE INDEPENDENCIA DE MALHA - on-caso-2, on-caso-2.2, on-caso-3")
    p("=" * 78)
    p("(1) GLOBAL: k_axial = rigidez axial SECANTE pre-flambagem = |F(Dz_c)|/Dz_c,")
    p(f"    com Dz_c={DZ_COMMON*1e3:.2f} mm (ancorada na origem). Robusta mas 'mole'.")
    p("(2) LOCAL/MODAL (on-caso-2, do .frd): pico de von Mises e kink lateral por")
    p("    camada (pia/dura) + razao pia/dura. Lidos como SECANTE pre-flambagem")
    p(f"    em Dz_c={DZ_COMMON*1e3:.2f} mm e, quando lambda=1 e' atingido, em CARGA PLENA.")
    p(f"Dz nominal = {DZ_NOMINAL*1e3:.2f} mm.\n")

    results = {c: {} for c in CASES}

    # ---- (1) k_axial por caso (global) ----
    for case, cfg in CASES.items():
        deck = cfg["deck"]
        p("-" * 78)
        p(f"{case}  --  {cfg['label']}   [GLOBAL: k_axial]")
        p("-" * 78)
        p(f"{'nivel':6s} {'nCells':>8s} {'eixo':>5s} {'k_axial[N/m]':>14s} "
          f"{'F@0.1mm[mN]':>13s} {'lam_max':>8s}")
        ncs, ks = [], []
        axis_letter = {1: "x", 2: "y", 3: "z"}
        for lvl in LEVELS:
            dp = dat_path(case, deck, lvl)
            r = compute_level(dp)
            if r is None:
                continue
            nc = NCELLS.get(lvl, float("nan"))
            results[case][lvl] = (nc, r)
            ncs.append(nc); ks.append(r["k_axial"])
            p(f"{lvl:6s} {nc:8d} {axis_letter[r['axis']]:>5s} "
              f"{r['k_axial']:14.2f} {r['F_common']*1e3:13.3f} {r['lam_max']:8.3f}")
        if len(ks) >= 2:
            k_ref = ks[-1]
            p(f"   convergencia de k_axial (ref = malha mais fina, {ncs[-1]} cells):")
            for nc, k in zip(ncs, ks):
                p(f"      {nc:8d} cells: k={k:9.2f} N/m  (desvio {100*(k-k_ref)/k_ref:+6.2f}%)")
        p("")

    # ---- (2) von Mises + kink (local/modal) ----
    local2 = local_modal_section(p, "on-caso-2", "on-caso-2", note=NOTE_CASO2)
    p("")
    local22 = local_modal_section(p, "on-caso-2.2", "on-caso-2.2", note=NOTE_CASO22)
    p("")

    txt = "\n".join(lines) + "\n"
    print(txt)
    SUMMARY.write_text(txt)
    print(f"Sumario salvo em {SUMMARY}")

    _plot(results, local2)
    _plot_caso22(local22)


def build_local(case: str, deck: str):
    """Computa indicadores locais/modais (secante + carga plena) por nivel."""
    local = {}          # level -> dict(nc, secant, full)
    for lvl in LOCAL_LEVELS.get(case, []):
        fp = frd_path(case, deck, lvl)
        if not fp.exists():
            continue
        steps = analyze_frd(fp)
        if not steps:
            continue
        local[lvl] = dict(nc=ncells_from_frd(fp),
                          secant=frd_secant(steps),
                          full=frd_fullload(steps))
    return local


def local_modal_section(p, case: str, deck: str, note):
    """Imprime a secao local/modal (secante + carga plena) e retorna o dict."""
    levels = LOCAL_LEVELS.get(case, [])
    local = build_local(case, deck)
    p("=" * 78)
    p(f"{case}  --  INDICADORES LOCAIS/MODAIS (von Mises de pico + kink por camada)")
    p("=" * 78)
    p("SECANTE pre-flambagem (Dz_c=0.10 mm, ancorada na origem):")
    p(f"{'nivel':14s} {'nCells':>8s} {'vm_glob[kPa]':>13s} {'vm_pia[kPa]':>12s} "
      f"{'vm_dura[kPa]':>13s} {'kink_pia[um]':>13s} {'kink_dura[um]':>14s} {'pia/dura':>9s}")
    for lvl in levels:
        if lvl not in local or not local[lvl]["secant"]:
            continue
        nc = local[lvl]["nc"]
        sec = local[lvl]["secant"]
        p(f"{lvl:14s} {nc:8d} {sec['vm_global']/1e3:13.2f} {sec['vm_pia']/1e3:12.2f} "
          f"{sec['vm_dura']/1e3:13.2f} {sec['kink_pia']*1e6:13.2f} "
          f"{sec['kink_dura']*1e6:14.2f} {sec['ratio']:9.2f}")
    sec_levels = [lv for lv in levels if lv in local and local[lv]["secant"]]
    if len(sec_levels) >= 2:
        ref = local[sec_levels[-1]]["secant"]
        p(f"   convergencia (ref = {sec_levels[-1]}, {local[sec_levels[-1]]['nc']} cells):")
        for lv in sec_levels:
            s = local[lv]["secant"]
            dvm = 100 * (s["vm_global"] - ref["vm_global"]) / ref["vm_global"]
            dkp = 100 * (s["kink_pia"] - ref["kink_pia"]) / ref["kink_pia"]
            p(f"      {lv:14s} {local[lv]['nc']:8d} cells: "
              f"vm_glob desvio {dvm:+6.2f}% | kink_pia desvio {dkp:+6.2f}%")
    p("")
    p("CARGA PLENA (lambda=1.0, Dz=1.5 mm; modo de flambagem desenvolvido):")
    p("  von Mises de PICO por zona estrutural (kPa); vm_glob inclui a juncao")
    p("  sclera_ring/globo (concentracao na fixacao dura-esclera).")
    p(f"{'nivel':14s} {'nCells':>8s} {'lam':>6s} {'vm_pia':>8s} {'vm_dura':>8s} "
      f"{'vm_scl':>8s} {'vm_glob':>8s} {'kink[mm]':>9s} {'status':>9s}")
    full_levels = [lv for lv in levels
                   if lv in local and local[lv]["full"] and local[lv]["full"]["full"]]
    for lvl in levels:
        if lvl not in local or not local[lvl]["full"]:
            continue
        f = local[lvl]["full"]
        status = "PLENA" if f["full"] else f"lam={f['lam']:.2f}"
        p(f"{lvl:14s} {local[lvl]['nc']:8d} {f['lam']:6.3f} "
          f"{f['vm_pia']/1e3:8.1f} {f['vm_dura']/1e3:8.1f} "
          f"{f['vm_sclera_ring']/1e3:8.1f} {f['vm_global']/1e3:8.1f} "
          f"{f['kink_pia']*1e3:9.3f} {status:>9s}")
    if len(full_levels) >= 2:
        ref = local[full_levels[-1]]["full"]
        p(f"   convergencia von Mises pico (ref = {full_levels[-1]}, "
          f"{local[full_levels[-1]]['nc']} cells):")
        for key, name in [("vm_pia", "pia"), ("vm_dura", "dura"),
                          ("vm_global", "global")]:
            rv = ref[key]
            devs = "  ".join(
                f"{lv}:{100*(local[lv]['full'][key]-rv)/rv:+.1f}%"
                for lv in full_levels)
            p(f"      {name:7s} (ref={rv/1e3:.1f} kPa): {devs}")
    for ln in note:
        p(ln)
    return local


NOTE_CASO2 = [
    "   NOTA: a razao pia/dura em CARGA PLENA NAO converge de forma robusta neste",
    "   setup (sem imperfeicao explicita, a flambagem e' semeada pela assimetria da",
    "   propria malha). As malhas radialmente bem resolvidas (radpia2dura3/3dura4)",
    "   dao razao O(1) (~0.8-1.2): pia e dura dobram de forma comparavel. A razao",
    "   ~3.9 da malha de producao (pia1/dura2) e' artefato da resolucao radial grossa.",
    "   Ja' o PICO de von Mises converge: malhas radiais -> ~198 kPa; producao +11%.",
    "   Conclusao: indicadores PRE-flambagem (secante) estao convergidos; o MODO de",
    "   flambagem so' e' quantitativamente confiavel com imperfeicao fisica explicita.",
]

NOTE_CASO22 = [
    "   NOTA: o Caso 2.2 tem IMPERFEICAO GEOMETRICA EXPLICITA (tortuosidade em J),",
    "   logo a flambagem tem gatilho DETERMINISTICO: o kink lateral (~1.5 mm) e'",
    "   dominado pela flexao GLOBAL do nervo em J -> pia e dura andam juntas",
    "   (razao ~1.00 em todas as malhas; metrica nao informativa do modo local).",
    "   A grandeza local relevante e' o PICO de von Mises, que CONVERGE com refino",
    "   RADIAL: os dois niveis radiais (pia2/dura3 e pia3/dura4) concordam em ~0.6%",
    "   (pia ~172, dura ~183, juncao sclera/globo ~238 kPa). A malha de PRODUCAO",
    "   (pia1/dura2) SUBESTIMA o pico: pia -53% (80 vs 172!), dura -5%, global -27%.",
    "   => 1 celula radial na pia e' insuficiente p/ a tensao de flexao da lamina.",
    "   Correcao barata: pia>=2 / dura>=3 celulas radiais (radpia2dura3 = 5328 cels,",
    "   so' +12% vs producao) ja' entrega o pico convergido.",
]


def _plot(results, local):
    """Figura multi-painel: linha 1 = k_axial (3 casos, global);
    linha 2 = on-caso-2 local/modal (von Mises secante, kink secante, modo pleno)."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    # ---------- linha 1: k_axial (global) ----------
    for ax, (case, cfg) in zip(axes[0], CASES.items()):
        rc = results[case]
        ncs = [rc[lv][0] for lv in LEVELS if lv in rc]
        ks = [rc[lv][1]["k_axial"] for lv in LEVELS if lv in rc]
        if not ncs:
            ax.set_visible(False)
            continue
        k_ref = ks[-1]
        ax.axhspan(k_ref * 0.99, k_ref * 1.01, color="#2ca02c", alpha=0.15,
                   label="+-1% (mais fina)")
        ax.axhline(k_ref, color="#2ca02c", lw=1.0, ls="--", alpha=0.7)
        ax.plot(ncs, ks, "o-", lw=1.8, ms=7, color="#1f77b4", zorder=3)
        if "f100" in rc:
            nc0, r0 = rc["f100"]
            ax.plot([nc0], [r0["k_axial"]], "s", ms=11, mfc="none",
                    mec="#d62728", mew=2.0, zorder=4, label="baseline (producao)")
        for nc, k in zip(ncs, ks):
            dev = 100 * (k - k_ref) / k_ref
            ax.annotate(f"{k:.1f}\n({dev:+.1f}%)", (nc, k),
                        textcoords="offset points", xytext=(0, 9),
                        fontsize=8, ha="center")
        ax.set_xscale("log")
        ax.set_xlabel("nCells (log)")
        ax.set_ylabel("k_axial secante (N/m)")
        ax.set_title(f"{cfg['label']} - k_axial (global)")
        ax.grid(alpha=0.3, which="both")
        lo, hi = min(ks), max(ks)
        pad = max((hi - lo) * 0.6, k_ref * 0.02)
        ax.set_ylim(lo - pad, hi + pad)
        ax.legend(fontsize=7, loc="lower right")

    # ---------- linha 2: on-caso-2 local/modal ----------
    sec_lv = [lv for lv in LOCAL_LEVELS if lv in local and local[lv]["secant"]]
    ncs_s = [local[lv]["nc"] for lv in sec_lv]

    def _panel(ax, ys, ylabel, title, ref_band=True, unit=""):
        if not sec_lv:
            ax.set_visible(False)
            return
        ax.plot(ncs_s, ys, "o-", lw=1.8, ms=7, color="#9467bd", zorder=3)
        yref = ys[-1]
        if ref_band and yref:
            ax.axhspan(yref * 0.95, yref * 1.05, color="#2ca02c", alpha=0.12,
                       label="+-5% (mais fina)")
            ax.axhline(yref, color="#2ca02c", lw=1.0, ls="--", alpha=0.7)
        if "f100" in local:
            i = sec_lv.index("f100") if "f100" in sec_lv else None
            if i is not None:
                ax.plot([ncs_s[i]], [ys[i]], "s", ms=11, mfc="none",
                        mec="#d62728", mew=2.0, zorder=4, label="baseline (producao)")
        for nc, y in zip(ncs_s, ys):
            dev = 100 * (y - yref) / yref if yref else float("nan")
            ax.annotate(f"{y:.2f}{unit}\n({dev:+.1f}%)", (nc, y),
                        textcoords="offset points", xytext=(0, 9),
                        fontsize=7.5, ha="center")
        ax.set_xscale("log")
        ax.set_xlabel("nCells (log)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=7, loc="lower right")

    if sec_lv:
        _panel(axes[1][0], [local[lv]["secant"]["vm_global"] / 1e3 for lv in sec_lv],
               "von Mises de pico (kPa)",
               "Caso 2 - von Mises pico (secante 0.1 mm)")
        _panel(axes[1][1], [local[lv]["secant"]["kink_pia"] * 1e6 for lv in sec_lv],
               "kink pia (um)",
               "Caso 2 - kink lateral da pia (secante 0.1 mm)")

    # painel 3: modo pleno (razao pia/dura em carga plena)
    full_lv = [lv for lv in LOCAL_LEVELS
               if lv in local and local[lv]["full"] and local[lv]["full"]["full"]]
    axm = axes[1][2]
    if full_lv:
        ncs_f = [local[lv]["nc"] for lv in full_lv]
        ratios = [local[lv]["full"]["ratio"] for lv in full_lv]
        axm.plot(ncs_f, ratios, "o-", lw=1.8, ms=7, color="#ff7f0e", zorder=3)
        axm.axhline(1.0, color="grey", ls=":", lw=1.0, alpha=0.7)
        axm.text(min(ncs_f), 1.02, "razao=1 (modo NAO confinado)", fontsize=7,
                 color="grey")
        for nc, r in zip(ncs_f, ratios):
            axm.annotate(f"{r:.2f}", (nc, r), textcoords="offset points",
                         xytext=(0, 9), fontsize=8, ha="center")
        axm.set_xscale("log")
        axm.set_xlabel("nCells (log)")
        axm.set_ylabel("kink_pia / kink_dura (carga plena)")
        axm.set_title("Caso 2 - modo S confinado (carga plena)")
        axm.grid(alpha=0.3, which="both")
    else:
        axm.set_visible(False)

    fig.suptitle("Independencia de malha - global (k_axial) vs local/modal "
                 "(von Mises de pico, kink por camada)",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(PNG, dpi=140)
    print(f"Plot salvo em {PNG}")


PNG22 = OUT_DIR / "mesh_independence_caso2.2.png"


def _plot_caso22(local):
    """Figura do Caso 2.2 (imperfeicao J explicita): von Mises secante, kink
    secante e von Mises em CARGA PLENA. A razao pia/dura nao e' plotada porque,
    com a dobra global em J, vale ~1 em todas as malhas (metrica dominada pelo
    movimento de corpo rigido da secao)."""
    levels = LOCAL_LEVELS["on-caso-2.2"]
    sec_lv = [lv for lv in levels if lv in local and local[lv]["secant"]]
    full_lv = [lv for lv in levels
               if lv in local and local[lv]["full"] and local[lv]["full"]["full"]]
    if not sec_lv:
        print("Caso 2.2: sem dados locais para plotar")
        return

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    ncs_s = [local[lv]["nc"] for lv in sec_lv]

    def _panel(ax, xs, ys, ylabel, title, lv_list, unit="", band=0.05):
        ax.plot(xs, ys, "o-", lw=1.8, ms=7, color="#9467bd", zorder=3)
        yref = ys[-1]
        if yref:
            ax.axhspan(yref * (1 - band), yref * (1 + band), color="#2ca02c",
                       alpha=0.12, label=f"+-{band*100:.0f}% (mais fina)")
            ax.axhline(yref, color="#2ca02c", lw=1.0, ls="--", alpha=0.7)
        if "f100" in lv_list:
            i = lv_list.index("f100")
            ax.plot([xs[i]], [ys[i]], "s", ms=11, mfc="none", mec="#d62728",
                    mew=2.0, zorder=4, label="baseline (producao)")
        for x, y in zip(xs, ys):
            dev = 100 * (y - yref) / yref if yref else float("nan")
            ax.annotate(f"{y:.1f}{unit}\n({dev:+.1f}%)", (x, y),
                        textcoords="offset points", xytext=(0, 9),
                        fontsize=7.5, ha="center")
        ax.set_xscale("log")
        ax.set_xlabel("nCells (log)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=7, loc="lower right")

    _panel(axes[0], ncs_s,
           [local[lv]["secant"]["vm_global"] / 1e3 for lv in sec_lv],
           "von Mises de pico (kPa)",
           "Caso 2.2 - von Mises pico (secante 0.1 mm)", sec_lv)
    _panel(axes[1], ncs_s,
           [local[lv]["secant"]["kink_pia"] * 1e6 for lv in sec_lv],
           "kink pia (um)",
           "Caso 2.2 - kink lateral da pia (secante 0.1 mm)", sec_lv)
    if full_lv:
        ncs_f = [local[lv]["nc"] for lv in full_lv]
        ax = axes[2]
        series = [("vm_pia", "pia", "#1f77b4"),
                  ("vm_dura", "dura", "#d62728"),
                  ("vm_global", "global (juncao scl/globo)", "#7f7f7f")]
        for key, lab, col in series:
            ys = [local[lv]["full"][key] / 1e3 for lv in full_lv]
            ax.plot(ncs_f, ys, "o-", lw=1.8, ms=6, color=col, label=lab, zorder=3)
            for x, y in zip(ncs_f, ys):
                ax.annotate(f"{y:.0f}", (x, y), textcoords="offset points",
                            xytext=(0, 7), fontsize=7, ha="center", color=col)
        if "f100" in full_lv:
            i = full_lv.index("f100")
            for key, _, _ in series:
                ax.plot([ncs_f[i]], [local["f100"]["full"][key] / 1e3], "s",
                        ms=10, mfc="none", mec="k", mew=1.5, zorder=4)
        ax.set_xscale("log")
        ax.set_xlabel("nCells (log)")
        ax.set_ylabel("von Mises de pico por zona (kPa)")
        ax.set_title("Caso 2.2 - von Mises pico por zona (CARGA PLENA)")
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=7, loc="lower right",
                  title="quadrado=producao (subestima)")
    else:
        axes[2].set_visible(False)

    fig.suptitle("Independencia de malha - Caso 2.2 (imperfeicao J explicita): "
                 "pico de von Mises converge com refino RADIAL (producao subestima)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(PNG22, dpi=140)
    print(f"Plot Caso 2.2 salvo em {PNG22}")


if __name__ == "__main__":
    main()
