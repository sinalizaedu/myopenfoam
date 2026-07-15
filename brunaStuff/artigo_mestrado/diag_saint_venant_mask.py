"""Aplica mascara Saint-Venant (z em [5%L, 95%L]) ao campo do solido em
t=1.9 s (pico de strain no ciclo 3) e re-extrai metricas limpas.

Compara: dominio FULL vs INTERIOR (Saint-Venant) — diferenca quantifica o
quanto o engaste artificial nas caps esta inflando os picos."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CASE = Path("/tmp/_diag_export_v3")
OUT_PNG = Path(__file__).parent / "diag_saint_venant_mask.png"
OUT_TXT = Path(__file__).parent / "_diag_saint_venant_mask.txt"

SV_FRAC = 0.05  # 5% descartados em cada extremidade (Saint-Venant)


def _read_field(path: Path) -> np.ndarray:
    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(\s*([^)]+)\)",
        text,
    )
    if not m:
        raise ValueError(f"Could not parse {path}")
    n = int(m.group(1))
    body = m.group(2).strip()
    vals = np.fromstring(body, sep="\n", dtype=float)
    if vals.size != n:
        vals = np.fromstring(body.replace("\n", " "), sep=" ", dtype=float)
    assert vals.size == n
    return vals


def main() -> None:
    eps = _read_field(CASE / "epsilonEq")
    sig = _read_field(CASE / "sigmaEq")
    cx = _read_field(CASE / "Cx")
    cy = _read_field(CASE / "Cy")
    cz = _read_field(CASE / "Cz")

    n = eps.size
    z_min, z_max = cz.min(), cz.max()
    L = z_max - z_min
    z_lo = z_min + SV_FRAC * L
    z_hi = z_max - SV_FRAC * L

    is_interior = (cz >= z_lo) & (cz <= z_hi)
    n_int = int(is_interior.sum())
    n_caps = n - n_int

    def stats(values: np.ndarray) -> dict:
        return {
            "n": int(values.size),
            "max": float(values.max()),
            "p999": float(np.percentile(values, 99.9)),
            "p99": float(np.percentile(values, 99)),
            "p95": float(np.percentile(values, 95)),
            "p90": float(np.percentile(values, 90)),
            "p50": float(np.percentile(values, 50)),
            "mean": float(values.mean()),
            "std": float(values.std()),
        }

    eps_full = stats(eps)
    eps_int = stats(eps[is_interior])
    sig_full = stats(sig)
    sig_int = stats(sig[is_interior])

    lines: list[str] = []
    lines.append("=" * 72)
    lines.append(f"MASCARA SAINT-VENANT @ t=1.900 s (pico ciclo 3, regime)")
    lines.append("=" * 72)
    lines.append(f"  Total cells:           {n}")
    lines.append(f"  z_full = [{z_min*1e3:.2f}, {z_max*1e3:.2f}] mm  L = {L*1e3:.2f} mm")
    lines.append(f"  Saint-Venant fraction: {SV_FRAC*100:.0f}% em cada extremidade")
    lines.append(f"  z_interior = [{z_lo*1e3:.2f}, {z_hi*1e3:.2f}] mm")
    lines.append(f"  cells interior:        {n_int} ({n_int/n*100:.1f}%)")
    lines.append(f"  cells caps descartadas:{n_caps} ({n_caps/n*100:.1f}%)")
    lines.append("")
    lines.append("--- ε_vM von Mises strain ---")
    lines.append(f"  {'metric':<10} {'FULL':>14} {'INTERIOR (S-V)':>16} {'Δ':>9}")
    for key in ("max", "p999", "p99", "p95", "p90", "p50", "mean", "std"):
        v_full = eps_full[key] * 100
        v_int = eps_int[key] * 100
        delta = v_int - v_full
        lines.append(f"  {key:<10} {v_full:>13.3f}% {v_int:>15.3f}% {delta:>+8.3f}%")
    lines.append("")
    lines.append("--- σ_vM von Mises stress (kPa) ---")
    lines.append(f"  {'metric':<10} {'FULL':>14} {'INTERIOR (S-V)':>16} {'Δ':>9}")
    for key in ("max", "p999", "p99", "p95", "p90", "p50", "mean", "std"):
        v_full = sig_full[key] / 1000
        v_int = sig_int[key] / 1000
        delta = v_int - v_full
        lines.append(f"  {key:<10} {v_full:>12.2f}kPa {v_int:>13.2f}kPa {delta:>+6.2f}kPa")
    lines.append("")
    lines.append("--- Validacao Laplace (referencia teorica) ---")
    P_AVG_PA = 13333.0  # ~100 mmHg sistolico medio
    R_INT = 0.55e-3
    T_WALL = 0.20e-3
    E = 3e5
    NU = 0.49
    sigma_theta_th = P_AVG_PA * R_INT / T_WALL
    eps_theta_th = sigma_theta_th / E * (1 - NU**2)  # plane strain (efeito biaxial)
    eps_theta_th_uniaxial = sigma_theta_th / E
    lines.append(f"  σ_θθ (Laplace, parede fina, p=100 mmHg): {sigma_theta_th/1000:.2f} kPa")
    lines.append(f"  ε_θθ uniaxial (1D)                    : {eps_theta_th_uniaxial*100:.2f}%")
    lines.append(f"  ε_θθ plane strain (1-ν²)              : {eps_theta_th*100:.2f}%")
    lines.append("")
    lines.append("--- Veredicto ---")
    drop_eps = (eps_full["max"] - eps_int["max"]) / eps_full["max"] * 100
    drop_sig = (sig_full["max"] - sig_int["max"]) / sig_full["max"] * 100
    lines.append(f"  Pico ε reduz {drop_eps:+.1f}% ao mascarar caps")
    lines.append(f"  Pico σ reduz {drop_sig:+.1f}% ao mascarar caps")
    if abs(drop_eps) < 5 and abs(drop_sig) < 5:
        lines.append("  -> caps nao sao concentradoras de stress; pico vem do bulk (Laplace).")
    else:
        lines.append("  -> caps sao concentradoras; metricas mascaradas sao mais fisiologicas.")

    out_text = "\n".join(lines)
    print(out_text)
    OUT_TXT.write_text(out_text + "\n")

    # === Plot ===
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    ax = axes[0, 0]
    ax.scatter(cz * 1e3, eps * 100, s=2, alpha=0.4, color="C2", label="todas as cells")
    ax.scatter(cz[is_interior] * 1e3, eps[is_interior] * 100, s=2, alpha=0.6, color="C3", label="interior (S-V)")
    ax.axvline(z_lo * 1e3, color="k", ls="--", lw=0.7)
    ax.axvline(z_hi * 1e3, color="k", ls="--", lw=0.7)
    ax.axhline(eps_theta_th_uniaxial * 100, color="C0", ls=":", lw=0.8, label=f"Laplace 1D ({eps_theta_th_uniaxial*100:.1f}%)")
    ax.set_xlabel("z [mm]"); ax.set_ylabel("ε_vM [%]")
    ax.set_title("Distribuicao espacial de ε ao longo do eixo z")
    ax.legend(loc="lower right", fontsize=8); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.scatter(cz * 1e3, sig / 1000, s=2, alpha=0.4, color="C2")
    ax.scatter(cz[is_interior] * 1e3, sig[is_interior] / 1000, s=2, alpha=0.6, color="C3")
    ax.axvline(z_lo * 1e3, color="k", ls="--", lw=0.7)
    ax.axvline(z_hi * 1e3, color="k", ls="--", lw=0.7)
    ax.axhline(sigma_theta_th / 1000, color="C0", ls=":", lw=0.8, label=f"Laplace ({sigma_theta_th/1000:.1f} kPa)")
    ax.set_xlabel("z [mm]"); ax.set_ylabel("σ_vM [kPa]")
    ax.set_title("Distribuicao espacial de σ ao longo do eixo z")
    ax.legend(loc="lower right", fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1, 0]
    bins = np.linspace(eps.min() * 100, eps.max() * 100, 50)
    ax.hist(eps * 100, bins=bins, color="C2", alpha=0.5, label=f"FULL (n={n})")
    ax.hist(eps[is_interior] * 100, bins=bins, color="C3", alpha=0.7, label=f"INTERIOR (n={n_int})")
    ax.axvline(eps_theta_th_uniaxial * 100, color="C0", ls=":", lw=1.4, label="Laplace 1D")
    ax.set_xlabel("ε_vM [%]"); ax.set_ylabel("nº cells")
    ax.set_title("Histograma de ε_vM")
    ax.legend(loc="upper left", fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1, 1]
    bins = np.linspace(sig.min() / 1000, sig.max() / 1000, 50)
    ax.hist(sig / 1000, bins=bins, color="C2", alpha=0.5, label=f"FULL (n={n})")
    ax.hist(sig[is_interior] / 1000, bins=bins, color="C3", alpha=0.7, label=f"INTERIOR (n={n_int})")
    ax.axvline(sigma_theta_th / 1000, color="C0", ls=":", lw=1.4, label="Laplace")
    ax.set_xlabel("σ_vM [kPa]"); ax.set_ylabel("nº cells")
    ax.set_title("Histograma de σ_vM")
    ax.legend(loc="upper left", fontsize=8); ax.grid(alpha=0.3)

    fig.suptitle(
        f"Mascara Saint-Venant em z ∈ [{z_lo*1e3:.1f}, {z_hi*1e3:.1f}] mm @ t=1.900 s (ciclo 3)",
        fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_PNG, dpi=150)
    print(f"\nSaved plot: {OUT_PNG}")
    print(f"Saved txt:  {OUT_TXT}")


if __name__ == "__main__":
    main()
