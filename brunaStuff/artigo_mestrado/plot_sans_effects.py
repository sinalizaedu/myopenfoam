"""Plota os 4 efeitos da SANS comparando os 4 casos."""

from __future__ import annotations

import csv
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(f"matplotlib indisponivel: {exc}")

OUT = Path(__file__).resolve().parent / "sans_outputs"

CASES = [
    ("on-mestrado-1", "FEM-1 lumped (1g, 1333 Pa)",  "tab:gray",   ":"),
    ("on-mestrado-2", "FEM-2 anatomic (1g, 1333 Pa)", "tab:blue",   "-"),
    ("on-mestrado-3", "FEM-3 anatomic (SANS, 3800 Pa)", "tab:cyan",  "--"),
    ("on-fsi-2",      "FSI-2 (1g, 1333 Pa)",   "tab:red",    "-"),
    ("on-fsi-3",      "FSI-3 (SANS, 3800 Pa)", "tab:orange", "--"),
]


def read_csv(path: Path):
    with open(path) as f:
        return list(csv.DictReader(f))


def plot_dural_diameter():
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, label, color, ls in CASES:
        rows = read_csv(OUT / f"dural_diameter_{name}.csv")
        z = [float(r["z_mm"]) for r in rows]
        delta = [float(r["delta_um"]) for r in rows]
        ax.plot(z, delta, label=label, color=color, linestyle=ls, linewidth=1.7)
    ax.set_xlabel("z (mm) - canal optico (0) -> globo (30)")
    ax.set_ylabel(r"$\Delta r_{outer}$ (um) [dura deformada - dura inicial]")
    ax.set_title("(1) BALAO DURAL: deformacao radial da bainha vs P_CSF")
    ax.axhline(0, color="k", linewidth=0.5, alpha=0.4)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_dural_balloon.png", dpi=150)
    plt.close(fig)


def plot_kinking():
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, label, color, ls in CASES:
        rows = read_csv(OUT / f"nerve_kinking_{name}.csv")
        z = [float(r["z_mm"]) for r in rows]
        off = [float(r["offset_lateral_mm"]) * 1000 for r in rows]  # um
        ax.plot(z, off, label=label, color=color, linestyle=ls, linewidth=1.7)
    ax.set_xlabel("z (mm)")
    ax.set_ylabel("offset lateral do centroide do nervo (um)")
    ax.set_title("(3) KINKING: tortuosidade lateral do nervo optico")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_kinking.png", dpi=150)
    plt.close(fig)


def plot_summary_bars():
    """Grafico de barras com globe flattening e contact stress."""
    summary = {
        "on-mestrado-1": dict(globe=0.172, sigeq=2414.5,  sxx=-11000.3),
        "on-mestrado-2": dict(globe=0.010, sigeq=7543.3,  sxx=-18734.7),
        "on-mestrado-3": dict(globe=0.011, sigeq=7558.6,  sxx=-18733.6),
        "on-fsi-2":      dict(globe=4.077, sigeq=10144.3, sxx=-39911.6),
        "on-fsi-3":      dict(globe=11.692, sigeq=10166.1, sxx=-39834.9),
    }
    labels = ["mestrado-1\n(FEM lumped\n1g)", "mestrado-2\n(FEM anat.\n1g)",
              "mestrado-3\n(FEM anat.\nSANS)",
              "fsi-2\n(FSI 1g)", "fsi-3\n(FSI SANS)"]
    colors = ["tab:gray", "tab:blue", "tab:cyan", "tab:red", "tab:orange"]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    keys = list(summary.keys())

    # Globe flattening
    ax = axes[0]
    vals = [summary[k]["globe"] for k in keys]
    ax.bar(labels, vals, color=colors, edgecolor="k")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.3, f"{v:.2f}", ha="center", fontsize=10)
    ax.set_ylabel("Dz medio na anterior_globo (um)")
    ax.set_title("(2) ACHATAMENTO DO GLOBO\nDz da face anterior (z=30.8 mm)")
    ax.grid(True, alpha=0.3, axis="y")

    # sigma at contact_local
    ax = axes[1]
    vals = [-summary[k]["sxx"] for k in keys]  # plot positive (compressive)
    ax.bar(labels, vals, color=colors, edgecolor="k")
    for i, v in enumerate(vals):
        ax.text(i, v + 800, f"{v:.0f}", ha="center", fontsize=10)
    ax.set_ylabel(r"$|\sigma_{xx}|$ na cell sob contact_local (Pa)")
    ax.set_title("(4) BATALHA POR ESPACO no contact_local\ncompressao radial inward na dura")
    ax.grid(True, alpha=0.3, axis="y")

    fig.suptitle("Efeitos da microgravidade (SANS): comparacao FEM vs FSI",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig24_globe_and_contact.png", dpi=150)
    plt.close(fig)


def main():
    plot_dural_diameter()
    plot_kinking()
    plot_summary_bars()
    print(f"figs salvas em {OUT}/")
    for p in sorted(OUT.glob("*.png")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
