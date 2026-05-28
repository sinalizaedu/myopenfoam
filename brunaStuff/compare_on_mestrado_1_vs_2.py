"""Comparacao quantitativa on-mestrado-1 vs on-mestrado-2.

Metricas:
  - geometria: numero de zonas, celulas, patches
  - estatisticas de campos: sigmaEq, epsilonEq, |D|
  - perfis axiais (centro do nervo e na pia/bainha)
  - histograma comparativo de sigmaEq
  - mapa axial do pico de sigmaEq

Output: brunaStuff/compare_on_mestrado_1_vs_2.png + tabela texto.
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def parse_points(path):
    text = path.read_text()
    out = []
    for m in re.finditer(r"\(([-0-9.eE+ ]+)\)", text):
        parts = m.group(1).split()
        if len(parts) == 3:
            out.append([float(x) for x in parts])
    return np.array(out)


def parse_faces(path):
    text = path.read_text()
    out = []
    for m in re.finditer(r"(\d+)\(([^)]*)\)", text):
        n = int(m.group(1))
        pts = [int(p) for p in m.group(2).split()]
        if len(pts) == n:
            out.append(pts)
    return out


def parse_owner(path):
    text = path.read_text()
    # try List<label> form
    m = re.search(r"List<label>\s*\d+\s*\(([^)]+)\)", text)
    if m:
        return np.fromstring(m.group(1), sep=" ", dtype=int)
    # try labelList form: "<n>\n(\n...\n)\n"
    m = re.search(r"\n\s*(\d+)\s*\n\(\s*([^)]+)\)", text)
    if m:
        return np.fromstring(m.group(2), sep=" ", dtype=int)
    return None


def parse_boundary(path):
    text = path.read_text()
    patches = {}
    for m in re.finditer(
        r"(\w+)[\s\n]*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", text
    ):
        patches[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return patches


def parse_cellZones(path):
    if not path.exists():
        return {}
    text = path.read_text()
    zones = {}
    pattern = re.compile(
        r"(\w+)\s*\{\s*type\s+cellZone;\s*cellLabels\s+List<label>\s*\d+\s*\(([^)]+)\)\s*;",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        name = m.group(1)
        if name in ("FoamFile", "meta"):
            continue
        zones[name] = np.fromstring(m.group(2), sep=" ", dtype=int)
    return zones


def parse_volScalar(path):
    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s*\d+\s*\(([^)]+)\)", text
    )
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+([0-9.eE+-]+);", text)
        if m2:
            return None
        raise RuntimeError(f"cannot parse {path}")
    return np.fromstring(m.group(1), sep=" ")


def parse_volVector(path):
    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s*\d+\s*\(([\s\S]+?)\)\s*;",
        text,
    )
    if not m:
        return None
    block = m.group(1)
    triples = re.findall(r"\(([-0-9.eE+ ]+)\)", block)
    arr = np.zeros((len(triples), 3))
    for i, t in enumerate(triples):
        arr[i] = [float(x) for x in t.split()]
    return arr


def cell_centers(points, faces, owner, n_cells):
    centers = np.zeros((n_cells, 3))
    counts = np.zeros(n_cells)
    for f_idx, pts in enumerate(faces):
        if f_idx >= len(owner):
            break
        cc = points[pts].mean(axis=0)
        c = owner[f_idx]
        centers[c] += cc
        counts[c] += 1
    centers /= counts[:, None]
    return centers


def load_case(case_dir):
    poly = case_dir / "constant" / "polyMesh"
    time_dir = case_dir / "1"
    points = parse_points(poly / "points")
    faces = parse_faces(poly / "faces")
    owner = parse_owner(poly / "owner")
    patches = parse_boundary(poly / "boundary")
    zones = parse_cellZones(poly / "cellZones")
    sigmaEq = parse_volScalar(time_dir / "sigmaEq")
    epsilonEq = parse_volScalar(time_dir / "epsilonEq")
    D = parse_volVector(time_dir / "D")
    n_cells = len(sigmaEq)
    centers = cell_centers(points, faces, owner, n_cells)
    print(f"  {case_dir.name}: {n_cells} cells, {len(patches)} patches, {len(zones)} zones")
    return {
        "name": case_dir.parent.name,
        "centers": centers,
        "sigmaEq": sigmaEq,
        "epsilonEq": epsilonEq,
        "D": D,
        "zones": zones,
        "patches": patches,
        "n_cells": n_cells,
    }


def axial_profile(centers, field, n_bins=28, z_min=0, z_max=0.0303, r_max=None, r_min=None):
    z = centers[:, 2]
    r = np.hypot(centers[:, 0], centers[:, 1])
    mask = (z >= z_min) & (z <= z_max)
    if r_max is not None:
        mask &= r <= r_max
    if r_min is not None:
        mask &= r > r_min
    z_sel = z[mask]
    f_sel = field[mask]
    bins = np.linspace(z_min, z_max, n_bins + 1)
    centers_b = 0.5 * (bins[:-1] + bins[1:])
    means = np.array(
        [
            f_sel[(z_sel >= bins[i]) & (z_sel < bins[i + 1])].mean()
            if ((z_sel >= bins[i]) & (z_sel < bins[i + 1])).any()
            else np.nan
            for i in range(n_bins)
        ]
    )
    return centers_b, means


def main():
    case1 = ROOT / "cases" / "on-mestrado-1" / "solid"
    case2 = ROOT / "cases" / "on-mestrado-2" / "solid"

    print("Loading cases...")
    c1 = load_case(case1)
    c2 = load_case(case2)

    print("\n=== METRICAS ===")
    for c in (c1, c2):
        sig = c["sigmaEq"]
        eps = c["epsilonEq"]
        dmag = np.linalg.norm(c["D"], axis=1) if c["D"] is not None else None
        print(f"\n{c['name']}:")
        print(f"  cells:           {c['n_cells']}")
        print(f"  cellZones:       {list(c['zones'].keys())}")
        print(f"  patches:         {list(c['patches'].keys())}")
        print(
            f"  sigmaEq:         max={sig.max():9.1f} Pa  mean={sig.mean():8.1f} Pa  "
            f"P95={np.percentile(sig, 95):8.1f} Pa  P99={np.percentile(sig, 99):8.1f} Pa"
        )
        print(
            f"  epsilonEq:       max={eps.max():.4e}  mean={eps.mean():.4e}  "
            f"P95={np.percentile(eps, 95):.4e}  P99={np.percentile(eps, 99):.4e}"
        )
        if dmag is not None:
            print(
                f"  |D|:             max={dmag.max() * 1e6:7.2f} um  "
                f"mean={dmag.mean() * 1e6:7.2f} um"
            )

    # Per-zone stats: -1 has (on, pia, lc, sclera); -2 has (on, pia, sas, dura, lc, sclera_peri, sclera_ring, globo).
    # Mapping to compare like-with-like:
    #   ON:           c1.on              vs  c2.on
    #   "bainha":     c1.pia (lumped)    vs  c2.[pia ∪ sas ∪ dura]
    #   LC:           c1.lc              vs  c2.lc
    #   "casca/globo":c1.sclera (lumped) vs  c2.[sclera_peri ∪ sclera_ring ∪ globo]
    def zone_stats(c, names):
        idx_list = []
        for n in names:
            if n in c["zones"]:
                idx_list.append(c["zones"][n])
        if not idx_list:
            return None
        idx = np.concatenate(idx_list)
        sig = c["sigmaEq"][idx]
        eps = c["epsilonEq"][idx]
        dmag = (
            np.linalg.norm(c["D"][idx], axis=1)
            if c["D"] is not None
            else None
        )
        return {
            "n": len(idx),
            "sig_max": sig.max(),
            "sig_mean": sig.mean(),
            "sig_p99": np.percentile(sig, 99),
            "eps_max": eps.max(),
            "eps_mean": eps.mean(),
            "d_max_um": dmag.max() * 1e6 if dmag is not None else None,
            "d_mean_um": dmag.mean() * 1e6 if dmag is not None else None,
        }

    print("\n=== POR REGIAO ANATOMICA (mapping like-with-like) ===")
    region_map = [
        ("Nervo (on)",       ["on"],                                   ["on"]),
        ("Bainha (pia*)",    ["pia"],                                  ["pia", "sas", "dura"]),
        ("LC",               ["lc"],                                   ["lc"]),
        ("Casca/globo",      ["sclera"],                               ["sclera_peri", "sclera_ring", "globo"]),
    ]
    zone_rows = []
    for label, names1, names2 in region_map:
        s1 = zone_stats(c1, names1)
        s2 = zone_stats(c2, names2)
        if s1 and s2:
            print(f"\n {label}: -1 zones={names1}, -2 zones={names2}")
            print(f"   sigmaEq max  : -1={s1['sig_max']:9.1f} Pa   -2={s2['sig_max']:9.1f} Pa   ratio(2/1)={s2['sig_max']/max(s1['sig_max'],1e-9):.2f}")
            print(f"   sigmaEq mean : -1={s1['sig_mean']:9.1f} Pa   -2={s2['sig_mean']:9.1f} Pa   ratio(2/1)={s2['sig_mean']/max(s1['sig_mean'],1e-9):.2f}")
            print(f"   epsEq P99    : -1={np.percentile(c1['epsilonEq'][np.concatenate([c1['zones'][n] for n in names1 if n in c1['zones']])], 99):.3e}   -2={np.percentile(c2['epsilonEq'][np.concatenate([c2['zones'][n] for n in names2 if n in c2['zones']])], 99):.3e}")
            print(f"   |D| max (um) : -1={s1['d_max_um']:7.2f}     -2={s2['d_max_um']:7.2f}     ratio(2/1)={s2['d_max_um']/max(s1['d_max_um'],1e-9):.2f}")
            zone_rows.append((label, s1, s2))

    fig, axes = plt.subplots(3, 2, figsize=(16, 13))

    ax = axes[0, 0]
    bins = np.linspace(0, max(c1["sigmaEq"].max(), c2["sigmaEq"].max()), 80)
    ax.hist(c1["sigmaEq"], bins=bins, alpha=0.55, label=f'{c1["name"]} (n={c1["n_cells"]})', color="C0", edgecolor="black", linewidth=0.2)
    ax.hist(c2["sigmaEq"], bins=bins, alpha=0.55, label=f'{c2["name"]} (n={c2["n_cells"]})', color="C1", edgecolor="black", linewidth=0.2)
    ax.set_yscale("log")
    ax.set_xlabel("sigmaEq (Pa)")
    ax.set_ylabel("celulas (log)")
    ax.set_title("Distribuicao de sigmaEq (von Mises)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    bins = np.linspace(0, max(c1["epsilonEq"].max(), c2["epsilonEq"].max()), 80)
    ax.hist(c1["epsilonEq"], bins=bins, alpha=0.55, label=c1["name"], color="C0", edgecolor="black", linewidth=0.2)
    ax.hist(c2["epsilonEq"], bins=bins, alpha=0.55, label=c2["name"], color="C1", edgecolor="black", linewidth=0.2)
    ax.set_yscale("log")
    ax.set_xlabel("epsilonEq")
    ax.set_ylabel("celulas (log)")
    ax.set_title("Distribuicao de epsilonEq")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    for c, color in ((c1, "C0"), (c2, "C1")):
        zb, mp = axial_profile(c["centers"], c["sigmaEq"], r_max=1.50e-3, z_min=0, z_max=0.030)
        ok = np.isfinite(mp)
        ax.plot(zb[ok] * 1000, mp[ok], color=color, label=f'{c["name"]} (ON r<1.5)', linewidth=2, marker="o", markersize=3)
    ax.set_xlabel("z (mm)")
    ax.set_ylabel("sigmaEq medio na ON (Pa)")
    ax.set_title("Perfil axial: sigmaEq no nervo (r < 1.5 mm)")
    ax.axvline(22.5, color="red", linestyle=":", alpha=0.6, label="contact_local")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    for c, color in ((c1, "C0"), (c2, "C1")):
        zb, mp = axial_profile(c["centers"], c["sigmaEq"], r_max=2.50e-3, r_min=1.50e-3, z_min=0, z_max=0.030)
        ok = np.isfinite(mp)
        ax.plot(zb[ok] * 1000, mp[ok], color=color, label=f'{c["name"]} (bainha r=1.5-2.5)', linewidth=2, marker="o", markersize=3)
    ax.set_xlabel("z (mm)")
    ax.set_ylabel("sigmaEq medio na bainha (Pa)")
    ax.set_title("Perfil axial: sigmaEq na bainha (r = 1.5-2.5 mm)")
    ax.axvline(22.5, color="red", linestyle=":", alpha=0.6, label="contact_local")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[2, 0]
    for c, color in ((c1, "C0"), (c2, "C1")):
        if c["D"] is not None:
            dmag = np.linalg.norm(c["D"], axis=1)
            zb, mp = axial_profile(c["centers"], dmag, r_max=2.50e-3, z_min=0, z_max=0.030)
            ok = np.isfinite(mp)
            ax.plot(zb[ok] * 1000, mp[ok] * 1e6, color=color, label=f'{c["name"]}', linewidth=2, marker="o", markersize=3)
    ax.set_xlabel("z (mm)")
    ax.set_ylabel("|D| medio (um)")
    ax.set_title("Perfil axial: deslocamento total")
    ax.axvline(22.5, color="red", linestyle=":", alpha=0.6, label="contact_local")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[2, 1]
    if zone_rows:
        labels = [r[0] for r in zone_rows]
        vals1_sig = [r[1]["sig_p99"] for r in zone_rows]
        vals2_sig = [r[2]["sig_p99"] for r in zone_rows]
        vals1_d = [r[1]["d_max_um"] for r in zone_rows]
        vals2_d = [r[2]["d_max_um"] for r in zone_rows]
        x = np.arange(len(labels))
        w = 0.2
        ax.bar(x - 1.5 * w, vals1_sig, w, label="-1 sigmaEq P99 (Pa)", color="C0", alpha=0.85)
        ax.bar(x - 0.5 * w, vals2_sig, w, label="-2 sigmaEq P99 (Pa)", color="C1", alpha=0.85)
        ax.set_ylabel("sigmaEq P99 (Pa)", color="black")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
        ax2 = ax.twinx()
        ax2.bar(x + 0.5 * w, vals1_d, w, label="-1 |D|max (um)", color="C0", alpha=0.45, hatch="//")
        ax2.bar(x + 1.5 * w, vals2_d, w, label="-2 |D|max (um)", color="C1", alpha=0.45, hatch="//")
        ax2.set_ylabel("|D| max (um)")
        lns1, lbs1 = ax.get_legend_handles_labels()
        lns2, lbs2 = ax2.get_legend_handles_labels()
        ax.legend(lns1 + lns2, lbs1 + lbs2, fontsize=7, loc="upper left")
        ax.set_title("Comparacao por regiao anatomica (mapping lumped)")
        ax.grid(True, alpha=0.3, axis="y")
    else:
        ax.axis("off")
        ax.text(0.5, 0.5, "no zone data parsed", ha="center", va="center")

    fig.suptitle("on-mestrado-1 (pia lumped) vs on-mestrado-2 (anatomico)", fontsize=12, weight="bold")
    fig.tight_layout()
    out = ROOT / "brunaStuff" / "compare_on_mestrado_1_vs_2.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
