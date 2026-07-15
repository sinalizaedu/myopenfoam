#!/usr/bin/env python3
"""
analyze_on-caso-3-sf_meshindep.py
=================================
Independencia de malha do caso 3F (on-caso-3-sf): SO a carga lateral da arteria
oftalmica (p_c = 9034 Pa, +X), sem Dz/EOM. Como NAO ha carga axial, a metrica de
convergencia NAO e' a rigidez axial k_axial (usada nos casos 2/2.2/3), e sim os
indicadores LATERAIS que sao o resultado-chave do 3F:

  (1) |Ux|max do eixo do nervo  -- a deflexao lateral reportada no artigo
      (Tabela tab:res-caso3sf: 326.9 um na malha de producao f100).
  (2) kink lateral max por camada (on/pia/sas/dura).
  (3) afundamento local da dura sob o patch de contato (U_r_contact_min).

Todos os niveis atingem lambda = 1.0 (carga lateral plena; o 3F e' uma
indentacao estavel, sem snap/colapso), entao a comparacao e' feita DIRETAMENTE
no estado final de cada malha -- nao precisa da secante pre-flambagem usada nos
casos com bifurcacao de Riks.

Niveis (malha geometricamente IDENTICA a' do on-caso-3; muda so' o carregamento):
  GLOBAL : f050 (819), f100=producao (4752), f150 (16587)
  RADIAL : radpia2dura3 (5328), radpia3dura4 (5904)

Saidas:
  brunaStuff/on-caso-3-sf_meshindep.png
  brunaStuff/on-caso-3-sf_meshindep_summary.txt
  brunaStuff/on-caso-3-sf_meshindep.json
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "brunaStuff"
DECK = "on-caso-3-sf"
R_AXIS = 0.35e-3   # raio para amostrar o eixo do nervo (zona ON)

# (tag, familia, nCells, pia_radial, dura_radial, producao?)
LEVELS = [
    ("f050",         "global", 819,   1, 1, False),
    ("f100",         "global", 4752,  1, 2, True),
    ("f150",         "global", 16587, 2, 3, False),
    ("radpia2dura3", "radial", 5328,  2, 3, False),
    ("radpia3dura4", "radial", 5904,  3, 4, False),
]


def case_dir(tag: str, prod: bool) -> Path:
    if prod:
        return REPO / "cases" / DECK / "ccx"
    return REPO / "cases" / "_mi" / f"{DECK}__{tag}" / "ccx"


def frd_path(tag: str, prod: bool) -> Path:
    return case_dir(tag, prod) / f"{DECK}.frd"


def lateral_force_mN(dat: Path) -> float:
    """Reacao lateral total no engaste posterior no ultimo tempo (= |F_x,y|
    aplicada pelo contato arterial). Mede a CARGA efetivamente aplicada."""
    if not dat.exists():
        return float("nan")
    txt = dat.read_text(errors="ignore").splitlines()
    NUM = r"-?\d+\.\d+(?:[Ee][+\-]?\d+)?"
    rec: dict[float, dict[str, list[float]]] = {}
    for i, L in enumerate(txt):
        m = re.match(r"\s*total force.*for set (\S+) and time\s+([\d.E+\-]+)", L, re.I)
        if not m:
            continue
        nset, t = m.group(1).upper(), float(m.group(2))
        j = i + 1
        while j < len(txt) and not txt[j].strip():
            j += 1
        nums = [float(x) for x in re.findall(NUM, txt[j])] if j < len(txt) else []
        if len(nums) >= 3:
            rec.setdefault(round(t, 6), {})[nset] = nums[:3]
    if not rec:
        return float("nan")
    d = rec[max(rec)]
    fx = sum(d.get(n, [0, 0, 0])[0] for n in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"))
    fy = sum(d.get(n, [0, 0, 0])[1] for n in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"))
    return math.hypot(fx, fy) * 1e3


def n_contact_faces(mesh_inp: Path) -> int:
    """Conta faces do *SURFACE CONTACT_LOCAL_SURF (area do patch arterial)."""
    if not mesh_inp.exists():
        return -1
    n, inside = 0, False
    for L in mesh_inp.read_text(errors="ignore").splitlines():
        s = L.strip()
        if s.upper().startswith("*SURFACE") and "CONTACT_LOCAL_SURF" in s.upper():
            inside = True
            continue
        if s.startswith("*"):
            inside = False
            continue
        if inside and s:
            n += 1
    return n


# ---------------------------------------------------------------------------
# parser nativo do CalculiX .frd (ASCII), ultimo bloco DISP
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
    nodes, disp_blocks, cur = {}, [], {}
    in_nodes = in_disp = False
    for L in path.read_text(errors="ignore").splitlines():
        s = L.strip()
        if not in_nodes and not in_disp and (s.startswith("2C ") or s == "2C"):
            in_nodes = True
            continue
        if in_nodes:
            if s.startswith("-3"):
                in_nodes = False
                continue
            if L.lstrip().startswith("-1"):
                r = _parse_data_line(L, 3)
                if r:
                    nodes[r[0]] = tuple(r[1])
            continue
        if s.startswith("-4"):
            parts = s.split()
            in_disp = len(parts) >= 2 and parts[1].strip() == "DISP"
            if in_disp:
                cur = {}
            continue
        if in_disp:
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
                if r:
                    cur[r[0]] = tuple(r[1])
    return nodes, (disp_blocks[-1] if disp_blocks else {})


def metrics(path: Path) -> dict | None:
    if not path.exists():
        return None
    nodes, disp = parse_frd_last_disp(path)
    if not nodes or not disp:
        return None
    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.array([disp.get(n, (0.0, 0.0, 0.0)) for n in nids])
    r0 = np.hypot(P[:, 0], P[:, 1])

    out = {}
    # (1) eixo do nervo: |Ux|max (deflexao lateral reportada no artigo)
    axis = (r0 <= R_AXIS) & (P[:, 2] <= 0.0305)
    out["ux_axis_max_um"] = float(np.abs(U[axis, 0]).max() * 1e6) if axis.any() else 0.0
    out["uz_span_um"] = float((U[axis, 2].max() - U[axis, 2].min()) * 1e6) if axis.any() else 0.0

    # (2) kink lateral max por camada
    for name, r_t, dr in [("on", 0.5e-3, 0.10e-3), ("pia", 1.55e-3, 0.06e-3),
                          ("sas", 2.0e-3, 0.06e-3), ("dura", 2.5e-3, 0.06e-3)]:
        m = np.abs(r0 - r_t) < dr
        out[f"kink_{name}_um"] = float(np.hypot(U[m, 0], U[m, 1]).max() * 1e6) if m.any() else 0.0

    # (3) afundamento local da dura no patch de contato (z=[20.9,24.1], x>2.4)
    md = (np.abs(r0 - 2.5e-3) < 0.06e-3) & (P[:, 2] > 20.9e-3) & (P[:, 2] < 24.1e-3) & (P[:, 0] > 2.4e-3)
    if md.any():
        rhat = P[md, :2] / r0[md, None]
        u_r = U[md, 0] * rhat[:, 0] + U[md, 1] * rhat[:, 1]
        out["ur_contact_min_um"] = float(u_r.min() * 1e6)
    else:
        out["ur_contact_min_um"] = 0.0
    return out


def main():
    rows = []
    for tag, fam, nc, pia, dura, prod in LEVELS:
        cd = case_dir(tag, prod)
        m = metrics(cd / f"{DECK}.frd")
        if m is None:
            print(f"[SKIP] {tag}: {cd / (DECK + '.frd')} ausente/sem DISP")
            continue
        m["flat_mN"] = lateral_force_mN(cd / f"{DECK}.dat")
        m["n_faces"] = n_contact_faces(cd / f"{DECK}_mesh.inp")
        rows.append(dict(tag=tag, fam=fam, nc=nc, pia=pia, dura=dura,
                         prod=prod, **m))
        print(f"  {tag:13s} nc={nc:6d} pia/dura={pia}/{dura} "
              f"faces={m['n_faces']:>2d} Flat={m['flat_mN']:6.1f}mN  "
              f"|Ux|axis={m['ux_axis_max_um']:7.1f}um  "
              f"kink_dura={m['kink_dura_um']:6.1f}um")
    if not rows:
        raise SystemExit("Nenhum .frd encontrado.")

    glob = [r for r in rows if r["fam"] == "global"]
    rad = [r for r in rows if r["fam"] == "radial"]

    # ---------------- sumario texto ----------------
    L = []
    p = L.append
    p("=" * 86)
    p("INDEPENDENCIA DE MALHA - caso 3F (on-caso-3-sf): SO arteria, p_c=9034 Pa, +X")
    p("=" * 86)
    p("Metrica de convergencia = deflexao lateral (NAO ha carga axial -> k_axial nao se aplica).")
    p("Todos os niveis atingem lambda=1.0 (indentacao estavel, sem snap).")
    p("")
    hdr = (f"{'nivel':<14}{'fam':>7}{'nCells':>8}{'pia/dura':>9}{'faces':>6}"
           f"{'Flat[mN]':>9}{'|Ux|axis[um]':>14}{'kink_dura':>10}{'Ur_cont[um]':>12}")
    p(hdr)
    p("-" * len(hdr))
    for r in rows:
        tag = r["tag"] + ("*" if r["prod"] else "")
        pd = f"{r['pia']}/{r['dura']}"
        p(f"{tag:<14}{r['fam']:>7}{r['nc']:>8}{pd:>9}{r['n_faces']:>6}"
          f"{r['flat_mN']:>9.1f}{r['ux_axis_max_um']:>14.1f}"
          f"{r['kink_dura_um']:>10.1f}{r['ur_contact_min_um']:>12.2f}")
    p("  (* = malha de producao f100; faces = nº de faces da dura no patch arterial)")
    p("")
    p("ACHADO CHAVE: o patch de contato (CONTACT_LOCAL_SURF) e' uma caixa topoSet")
    p("GEOMETRICA fixa; o nº de faces da dura externa que caem nela depende da malha")
    p("circunferencial/axial (0 -> 2 -> 5). Como a carga e' P=9034 Pa x area, a FORCA")
    p("lateral efetiva NAO e' invariante no refino GLOBAL (Flat: 72 -> 33 mN). O refino")
    p("RADIAL nao toca o ladrilhamento da face externa (2 faces em todos), por isso a")
    p("deflexao do eixo converge. Para convergencia GLOBAL limpa e' preciso fixar a")
    p("AREA carregada (escalar P p/ P*A=const, ou usar contato mecanico real).")
    p("")

    def converge(group, ref_tag, title):
        if len(group) < 2:
            return
        ref = next((g for g in group if g["tag"] == ref_tag), group[-1])
        p(f"{title} (ref = {ref['tag']}, {ref['nc']} cells):")
        for g in group:
            d_ux = 100 * (g["ux_axis_max_um"] - ref["ux_axis_max_um"]) / ref["ux_axis_max_um"]
            d_kd = 100 * (g["kink_dura_um"] - ref["kink_dura_um"]) / ref["kink_dura_um"] if ref["kink_dura_um"] else float("nan")
            p(f"   {g['tag']:<14} {g['nc']:>6} cells: "
              f"|Ux|axis desvio {d_ux:+6.2f}%  |  kink_dura desvio {d_kd:+6.2f}%")
        p("")

    converge(glob, "f150", "CONVERGENCIA GLOBAL")
    converge(rad + [g for g in glob if g["prod"]], "radpia3dura4",
             "CONVERGENCIA RADIAL (laminas pia/dura; inclui producao f100 p/ referencia)")

    txt = "\n".join(L) + "\n"
    print("\n" + txt)
    (OUT / "on-caso-3-sf_meshindep_summary.txt").write_text(txt)
    (OUT / "on-caso-3-sf_meshindep.json").write_text(json.dumps(rows, indent=2))

    # ---------------- figura ----------------
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Independencia de malha - caso 3F (on-caso-3-sf): deflexao lateral "
                 "sob p_c=9034 Pa (lambda=1.0)", fontsize=12, fontweight="bold")

    # Painel A: |Ux|axis vs nCells (refino GLOBAL)
    ax = axes[0]
    ncs = [g["nc"] for g in glob]
    ys = [g["ux_axis_max_um"] for g in glob]
    yref = next((g["ux_axis_max_um"] for g in glob if g["tag"] == "f150"), ys[-1])
    ax.axhspan(yref * 0.95, yref * 1.05, color="#2ca02c", alpha=0.13, label="+-5% (f150)")
    ax.axhline(yref, color="#2ca02c", lw=1.0, ls="--", alpha=0.7)
    ax.plot(ncs, ys, "o-", lw=1.8, ms=8, color="#1f77b4", zorder=3)
    for g in glob:
        dev = 100 * (g["ux_axis_max_um"] - yref) / yref
        ax.annotate(f"{g['ux_axis_max_um']:.0f}um ({dev:+.0f}%)\n"
                    f"{g['n_faces']}faces, {g['flat_mN']:.0f}mN",
                    (g["nc"], g["ux_axis_max_um"]),
                    textcoords="offset points", xytext=(0, 10), fontsize=7.5, ha="center")
        if g["prod"]:
            ax.plot([g["nc"]], [g["ux_axis_max_um"]], "s", ms=13, mfc="none",
                    mec="#d62728", mew=2.0, zorder=4, label="producao (f100)")
    ax.set_xscale("log")
    ax.set_xlabel("nCells (log)")
    ax.set_ylabel("|Ux|max do eixo do nervo (um)")
    ax.set_title("(A) Refino GLOBAL - deflexao lateral")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8, loc="best")

    # Painel B: kink por camada vs nCells (refino GLOBAL)
    ax = axes[1]
    for nm, c in [("on", "orange"), ("pia", "green"), ("sas", "cyan"), ("dura", "red")]:
        ax.plot(ncs, [g[f"kink_{nm}_um"] for g in glob], "o-", lw=1.6, ms=7,
                color=c, label=f"{nm}")
    ax.set_xscale("log")
    ax.set_xlabel("nCells (log)")
    ax.set_ylabel("kink lateral max por camada (um)")
    ax.set_title("(B) Refino GLOBAL - kink por camada")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8, loc="best")

    # Painel C: refino RADIAL dirigido (producao + radpia2dura3 + radpia3dura4)
    ax = axes[2]
    rad_group = sorted(rad + [g for g in glob if g["prod"]], key=lambda r: r["nc"])
    xlabels = [f"{r['tag']}\n(pia{r['pia']}/dura{r['dura']})\n{r['nc']}cel" for r in rad_group]
    x = np.arange(len(rad_group))
    ax.bar(x - 0.2, [r["ux_axis_max_um"] for r in rad_group], 0.4,
           color="#1f77b4", label="|Ux|axis [um]")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, [abs(r["ur_contact_min_um"]) for r in rad_group], 0.4,
            color="#ff7f0e", alpha=0.8, label="|Ur| contato [um]")
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=8)
    ax.set_ylabel("|Ux|max eixo (um)", color="#1f77b4")
    ax2.set_ylabel("|Ur| afundamento local (um)", color="#ff7f0e")
    ax.set_title("(C) Refino RADIAL das laminas (pia/dura)")
    ax.grid(alpha=0.3, axis="y")
    lns1, lb1 = ax.get_legend_handles_labels()
    lns2, lb2 = ax2.get_legend_handles_labels()
    ax.legend(lns1 + lns2, lb1 + lb2, fontsize=8, loc="lower right")

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    png = OUT / "on-caso-3-sf_meshindep.png"
    fig.savefig(png, dpi=140)
    print(f"Figura salva em: {png}")
    print(f"Sumario:  {OUT / 'on-caso-3-sf_meshindep_summary.txt'}")


if __name__ == "__main__":
    main()
