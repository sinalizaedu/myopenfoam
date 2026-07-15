"""
Plot da evolucao temporal do contato com gordura 3D em sugestao.
3 paineis:
  (a) P_max nas 2 interfaces (arteria<->fat, fat<->ONS)
  (b) Numero de faces ativas em cada interface
  (c) P_lumen, P_contact_arteria, P_contact_ons sobreposto na mesma escala
"""
from __future__ import annotations
import re
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

SOLID = Path("cases/sugestao/solid")


def parse_traction(time_dir: Path, patch: str):
    f = time_dir / "D"
    if not f.exists():
        return None
    text = f.read_text()
    pat = re.compile(
        rf"{patch}\s*\{{[^}}]*?traction\s+nonuniform List<vector>\s+(\d+)\s*\((.*?)\)\s*;",
        re.DOTALL,
    )
    m = pat.search(text)
    if not m:
        return None
    body = m.group(2)
    vals = re.findall(
        r"\(([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\)",
        body,
    )
    if not vals:
        return None
    mags = np.array([float(a) ** 2 + float(b) ** 2 + float(c) ** 2 for a, b, c in vals]) ** 0.5
    nz = mags[mags > 1e-3]
    return dict(
        n_active=len(nz),
        tmax=mags.max(),
        tmean_act=float(nz.mean()) if len(nz) > 0 else 0.0,
    )


def main() -> None:
    times = sorted(
        [p for p in SOLID.iterdir() if p.is_dir() and re.match(r"0\.\d", p.name)],
        key=lambda p: float(p.name),
    )

    rows = []
    for t in times:
        r1 = parse_traction(t, "arteria_externa")
        r2 = parse_traction(t, "fat_inner_nerve")
        if r1 is None or r2 is None:
            continue
        rows.append(
            (
                float(t.name),
                r1["n_active"],
                r1["tmax"],
                r1["tmean_act"],
                r2["n_active"],
                r2["tmax"],
                r2["tmean_act"],
            )
        )
    arr = np.array(rows)
    t = arr[:, 0]

    fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)

    ax = axes[0]
    ax.plot(t * 1e3, arr[:, 2], "o-", color="tab:blue", lw=2, label="P_max @ arteria↔fat")
    ax.plot(t * 1e3, arr[:, 5], "s-", color="tab:red", lw=2, label="P_max @ fat↔ONS")
    ax.plot(t * 1e3, arr[:, 3], "o--", color="tab:blue", lw=1, alpha=0.6, label="P_mean_act @ art↔fat")
    ax.plot(t * 1e3, arr[:, 6], "s--", color="tab:red", lw=1, alpha=0.6, label="P_mean_act @ fat↔ONS")
    ax.set_ylabel("P_contact [Pa]")
    ax.legend(loc="best", fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_title("(a) Pressão de contato — P_max e P_mean_active nas duas interfaces")

    ax = axes[1]
    ax.plot(t * 1e3, arr[:, 1], "o-", color="tab:blue", lw=2, label="n_active @ arteria↔fat (de 5088)")
    ax.plot(t * 1e3, arr[:, 4], "s-", color="tab:red", lw=2, label="n_active @ fat↔ONS (de 515)")
    ax.set_ylabel("# faces em contato")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_title("(b) Número de faces ativas no contato (= área de contato discretizada)")

    ax = axes[2]
    P_lumen_kpa = 16.0 * 0.5 * (1 - np.cos(np.pi * np.minimum(t, 0.05) / 0.05))
    P_lumen_kpa[t > 0.05] = 16.0 * (
        0.55 + 0.45 * np.sin(2 * np.pi * (t[t > 0.05] - 0.05) / 0.870)
    )
    ax.plot(t * 1e3, P_lumen_kpa * 1e3, "k-", lw=2, label="P_lumen (Hann ramp + OMVS)")
    ax.plot(t * 1e3, arr[:, 2], "o-", color="tab:blue", lw=1.5, label="P_contact arteria↔fat")
    ax.plot(t * 1e3, arr[:, 5], "s-", color="tab:red", lw=1.5, label="P_contact fat↔ONS")
    ax.set_xlabel("Tempo [ms]")
    ax.set_ylabel("Pressão [Pa]")
    ax.set_yscale("log")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, which="both")
    ax.set_title("(c) P_lumen vs P_contact (escala log) — ratio ~30:1 (esperado)")

    fig.suptitle(
        "sugestao — Gordura orbital 3D resolve perda de contato no peak sistólico",
        fontsize=12,
        weight="bold",
    )
    fig.tight_layout()
    out = Path("brunaStuff/sugestao_fat3d_contact.png")
    fig.savefig(out, dpi=120, bbox_inches="tight")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
