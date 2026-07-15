#!/usr/bin/env python3
"""
analyze_mesh_independence_on-caso-4.py
======================================
Estudo de independencia de malha do on-caso-4 (estagio representativo S2_upper,
cargas FISICAS identicas em todas as malhas). Le os .frd gerados em malhas de
resolucao crescente:

    cases/on-caso-4/ccx/on-caso-4_mesh{1,2,3}.frd   (1x, 2x, 3x as contagens de celula)

Para cada malha mede as MESMAS metricas do analyze_on-caso-4.py (kink por camada,
offset neural, sigma_vM no contato, |U| max) e quantifica a variacao relativa
entre malhas sucessivas. Uma metrica e' "independente da malha" quando a variacao
entre a malha intermediaria e a mais fina cai abaixo de ~2-3%.

Saidas:
  brunaStuff/on-caso-4_mesh_independence.png
  brunaStuff/on-caso-4_mesh_independence.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-4/ccx")
OUT = Path("brunaStuff")
PREFIX = "on-caso-4"
# (tag do .frd, rotulo curto). Ordenados depois por n_nos.
MESH_TAGS = [
    ("mesh1",   "1x base"),
    ("meshmed", "theta,z 2x"),
    ("mesh2",   "2x uniforme"),
]
Z_ART = 22.5e-3


# ---------------------------------------------------------------------------
# Parser .frd (identico ao analyze_on-caso-4.py)
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


def parse_frd(path: Path):
    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    nodes = {}
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
                nodes[r[0]] = tuple(r[1])

    def last_block(varname: str, n_floats: int):
        blocks = []
        cur = {}
        active = False
        for L in lines:
            s = L.strip()
            if s.startswith("-4"):
                parts = s.split()
                vn = parts[1].strip() if len(parts) >= 2 else ""
                if vn == varname:
                    active = True
                    cur = {}
                else:
                    active = False
                continue
            if not active:
                continue
            if s.startswith("-3"):
                if cur:
                    blocks.append(cur)
                active = False
                cur = {}
                continue
            if s.startswith("-5"):
                continue
            if L.lstrip().startswith("-1"):
                r = _parse_data_line(L, n_floats)
                if r is not None:
                    cur[r[0]] = r[1]
        return blocks[-1] if blocks else {}

    disp = last_block("DISP", 3)
    stress = last_block("STRESS", 6)
    return nodes, disp, stress


def von_mises(s6):
    sxx, syy, szz, sxy, syz, szx = s6
    return np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                   + 3.0 * (sxy ** 2 + syz ** 2 + szx ** 2))


def analyze_run(frd: Path):
    if not frd.exists():
        return None
    nodes, disp, stress = parse_frd(frd)
    if not nodes or not disp:
        return None

    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.zeros_like(P)
    for i, n in enumerate(nids):
        if n in disp:
            U[i] = disp[n]
    r0 = np.hypot(P[:, 0], P[:, 1])

    res = {"n_nodes": len(nids)}
    for name, r_t, dr in [("on", 0.5e-3, 0.10e-3), ("pia", 1.55e-3, 0.06e-3),
                          ("sas", 2.0e-3, 0.06e-3), ("dura", 2.5e-3, 0.06e-3)]:
        m = np.abs(r0 - r_t) < dr
        res[f"kink_{name}"] = (float(np.hypot(U[m, 0], U[m, 1]).max())
                               if m.sum() else 0.0)
    res["U_lat_global"] = float(np.hypot(U[:, 0], U[:, 1]).max())

    m_on = r0 < 1.0e-3
    offset_max = 0.0
    if m_on.sum():
        zr = np.round(P[m_on, 2] * 1e3).astype(int)
        xc = P[m_on, 0] + U[m_on, 0]
        yc = P[m_on, 1] + U[m_on, 1]
        for zb in np.unique(zr):
            sel = zr == zb
            off = np.hypot(xc[sel].mean(), yc[sel].mean())
            offset_max = max(offset_max, off)
    res["offset_neural_max"] = float(offset_max)

    vm_contact = 0.0
    if stress:
        m_zone = ((np.abs(P[:, 2] - Z_ART) < 3.0e-3) & (P[:, 0] > 0)
                  & (np.abs(np.degrees(np.arctan2(P[:, 1], P[:, 0]))) < 40))
        for i, n in enumerate(nids):
            if m_zone[i] and n in stress:
                vm = von_mises(stress[n])
                if vm > vm_contact:
                    vm_contact = vm
    res["vm_contact_max"] = float(vm_contact)
    return res


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
# metricas reportadas (chave, rotulo, fator de escala, unidade)
METRICS = [
    ("kink_on",           "kink nervo (r=0.5)",   1e3, "mm"),
    ("kink_dura",         "kink dura (r=2.5)",    1e3, "mm"),
    ("offset_neural_max", "offset centroide",     1e3, "mm"),
    ("U_lat_global",      "|U_lat| max global",   1e3, "mm"),
    ("vm_contact_max",    "sigma_vM contato",     1e-3, "kPa"),
]


def main():
    runs = []
    for tag, label in MESH_TAGS:
        frd = CASE / f"{PREFIX}_{tag}.frd"
        resp = analyze_run(frd)
        if resp is None:
            print(f"  [SKIP] {tag}: {frd} ausente ou sem campos")
            continue
        resp["tag"] = tag
        resp["label"] = label
        runs.append(resp)
        print(f"  {tag:<8} ({label:<11}): {resp['n_nodes']:>7} nos | "
              f"kink_on={resp['kink_on']*1e3:.4f} mm "
              f"kink_dura={resp['kink_dura']*1e3:.4f} mm "
              f"offset={resp['offset_neural_max']*1e3:.4f} mm "
              f"vM={resp['vm_contact_max']*1e-3:.2f} kPa")

    if len(runs) < 2:
        print("\nMenos de 2 malhas disponiveis - rode o estudo primeiro:")
        print("  bash brunaStuff/mesh_independence_on-caso-4.sh \"1 2 3\"")
        raise SystemExit(1)

    runs.sort(key=lambda r: r["n_nodes"])
    nodes = [r["n_nodes"] for r in runs]
    finest = runs[-1]

    # ----- tabela txt -----
    L = ["on-caso-4 - independencia de malha (estagio S0_baseline; cargas fisicas fixas)",
         "=" * 88,
         "Malhas: base (1x) -> intermediaria (theta,z 2x; radial 1x) -> fina (2x uniforme).",
         "Patch de contato (box em metros) e pressoes (Pa) IDENTICOS -> so a discretizacao muda.",
         "",
         f"{'metrica':<24}" + "".join(f"{r['label']:>13}" for r in runs)
         + f"{'var.%(int->fim)':>16}",
         f"{'n_nos':<24}" + "".join(f"{r['n_nodes']:>13}" for r in runs) + f"{'':>16}",
         "-" * 88]

    diffs = {}
    for key, lab, sc, unit in METRICS:
        vals = [r[key] * sc for r in runs]
        # variacao relativa entre a malha intermediaria e a mais fina
        ref = finest[key] * sc
        if len(runs) >= 3 and abs(ref) > 1e-12:
            rel = abs(runs[-2][key] * sc - ref) / abs(ref) * 100.0
        elif abs(ref) > 1e-12:
            rel = abs(runs[0][key] * sc - ref) / abs(ref) * 100.0
        else:
            rel = 0.0
        diffs[key] = rel
        L.append(f"{lab + ' ['+unit+']':<24}"
                 + "".join(f"{v:>13.4f}" for v in vals)
                 + f"{rel:>15.2f}%")

    L += ["-" * 88,
          "Criterio: metrica considerada independente da malha quando var.% (malha",
          "intermediaria -> mais fina) < ~2-3%. Variacoes maiores indicam que vale",
          "refinar mais ou que a metrica e' local (pico pontual sensivel ao no)."]
    txt = "\n".join(L)
    (OUT / "on-caso-4_mesh_independence.txt").write_text(txt + "\n")
    print("\n" + txt)

    # ----- figura -----
    ncols = len(METRICS)
    fig, axes = plt.subplots(1, ncols, figsize=(4.2 * ncols, 4.2))
    fig.suptitle("on-caso-4 - independencia de malha (S0_baseline; cargas fisicas fixas)\n"
                 "metricas vs numero de nos (base 1x -> theta,z 2x -> 2x uniforme)",
                 fontsize=12)
    for ax, (key, lab, sc, unit) in zip(axes, METRICS):
        ys = [r[key] * sc for r in runs]
        ax.plot(nodes, ys, "o-", lw=2, markersize=9, color="navy")
        for x, y in zip(nodes, ys):
            ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=8)
        ax.axhline(ys[-1], color="red", ls=":", lw=1.2, alpha=0.7,
                   label=f"mais fina ({ys[-1]:.3f})")
        ax.set_title(f"{lab}\n(var. int->fim: {diffs[key]:.1f}%)", fontsize=10)
        ax.set_xlabel("numero de nos")
        ax.set_ylabel(f"[{unit}]")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    out_png = OUT / "on-caso-4_mesh_independence.png"
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    print(f"\nGrafico: {out_png}")
    print(f"Tabela:  brunaStuff/on-caso-4_mesh_independence.txt")


if __name__ == "__main__":
    main()
