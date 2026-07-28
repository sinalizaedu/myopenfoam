#!/usr/bin/env python3
"""Draw G2-fluid meridional half with ACP tip on the optical axis (doc-g2-sim3)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CASE = Path(__file__).resolve().parents[1]
REPO = CASE.parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))
from g2_needle import ACP_TIP_ORIGIN_M, NEEDLE_R_LUMEN_M

JSON = CASE.parent / "doc-g2-sim1/geometry/g2_fluid_half_m.json"
OUT = CASE / "figures" / "g2_fluid_acp.png"

ACP_XYZ_M = np.array(ACP_TIP_ORIGIN_M)
ACP_R_M = NEEDLE_R_LUMEN_M


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

    fill(fluid["band_vitreous_half"], "#5dade2", "Vitreous", alpha=0.55)
    fill(fluid["band_ac_half"], "#a8dadc", "AC ∪ TM", alpha=0.65)
    tmm = fluid["tm_markers_right"] * mm
    ax.fill(tmm[:, 0], tmm[:, 1], color="#f4a261", alpha=0.75, label="TM", linewidth=0, zorder=2)
    stroke(fluid["lens_half"], color="#1e8449", lw=1.4, label="Lens (wall)")
    stroke(fluid["iris_half"], color="#9b2226", lw=1.2, label="Iris (wall)")
    stroke(fluid["cornea_inside_right"], color="#1d3557", lw=0.9)
    stroke(fluid["vitreous_retina_right"], color="#1d3557", lw=0.9)
    stroke(fluid["hyaloid_right"], color="#2874a6", lw=1.0)

    tip_xy = ACP_XYZ_M[:2] * mm
    tip_r = ACP_R_M * mm
    theta = np.linspace(-0.5 * np.pi, 0.5 * np.pi, 80)
    ax.fill(
        tip_xy[0] + tip_r * np.cos(theta),
        tip_xy[1] + tip_r * np.sin(theta),
        facecolor="#8e44ad",
        edgecolor="#5b2c6f",
        alpha=0.55,
        lw=1.4,
        zorder=5,
        label="acp_tip (on axis)",
    )
    ax.plot(tip_xy[0], tip_xy[1], "o", color="#5b2c6f", ms=6, zorder=6)
    ax.annotate(
        f"ACP tip on optical axis\n"
        f"(x,y)=({tip_xy[0]:.1f}, {tip_xy[1]:.1f}) mm\n"
        f"r = {tip_r:.2f} mm\n"
        f"Q_acp = Q_clinical / 4",
        xy=tip_xy,
        xytext=(1.8, -7.5),
        fontsize=8,
        color="#5b2c6f",
        arrowprops=dict(arrowstyle="-", color="#8e44ad", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#8e44ad", alpha=0.92),
        zorder=7,
    )

    ax.axvline(0.0, color="0.35", ls="--", lw=0.9, label="Optical axis")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]  (+ posterior / − anterior)")
    ax.set_title("G2-fluid — ACP tip on axis (Model B)\nparacentesis in AC  ·  Q_clinical/4")
    ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-9.5, 9.0)
    fig.tight_layout()
    fig.savefig(OUT, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
