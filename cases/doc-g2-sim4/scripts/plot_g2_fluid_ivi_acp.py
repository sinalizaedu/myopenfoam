#!/usr/bin/env python3
"""G2-fluid meridional half with IVI + ACP tips (doc-g2-sim4)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "brunaStuff"))
from g2_needle import ACP_TIP_ORIGIN_M, IVI_TIP_ORIGIN_M, NEEDLE_R_LUMEN_M

CASE = Path(__file__).resolve().parents[1]
JSON = CASE.parent / "doc-g2-sim1/geometry/g2_fluid_half_m.json"
OUT = CASE / "figures" / "g2_fluid_ivi_acp.png"

IVI_XYZ = np.array(IVI_TIP_ORIGIN_M)
ACP_XYZ = np.array(ACP_TIP_ORIGIN_M)
R_M = NEEDLE_R_LUMEN_M


def draw_tip(ax, xyz, color, edge, label, ann_xy):
    mm = 1.0e3
    xy = xyz[:2] * mm
    r = R_M * mm
    theta = np.linspace(-0.5 * np.pi, 0.5 * np.pi, 80)
    ax.fill(
        xy[0] + r * np.cos(theta), xy[1] + r * np.sin(theta),
        facecolor=color, edgecolor=edge, alpha=0.55, lw=1.4, zorder=5, label=label,
    )
    ax.plot(xy[0], xy[1], "o", color=edge, ms=5, zorder=6)


def main() -> None:
    fluid = {k: np.asarray(v, dtype=float) for k, v in json.loads(JSON.read_text()).items()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.4, 8.2))
    mm = 1.0e3

    def fill(pts, color, label, alpha=0.40):
        p = np.asarray(pts) * mm
        ax.fill(p[:, 0], p[:, 1], color=color, alpha=alpha, label=label, linewidth=0)

    def stroke(pts, **kw):
        p = np.asarray(pts) * mm
        ax.plot(p[:, 0], p[:, 1], **kw)

    fill(fluid["band_vitreous_half"], "#5dade2", "Vitreous", 0.55)
    fill(fluid["band_ac_half"], "#a8dadc", "AC ∪ TM", 0.65)
    stroke(fluid["cornea_inside_right"], color="#1d3557", lw=0.9)
    stroke(fluid["lens_half"], color="#1e8449", lw=1.2)
    draw_tip(ax, IVI_XYZ, "#c0392b", "#7b241c", "ivi_tip (vitreous)", (2, 5))
    draw_tip(ax, ACP_XYZ, "#8e44ad", "#5b2c6f", "acp_tip (AC)", (2, -7))
    ax.axvline(0, color="0.35", ls="--", lw=0.9)
    ax.set_aspect("equal")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("G2 Sim4 — IVI + ACP tips on optical axis\nQ = Q_clinical/4 each")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-9.5, 9.0)
    fig.tight_layout()
    fig.savefig(OUT, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
