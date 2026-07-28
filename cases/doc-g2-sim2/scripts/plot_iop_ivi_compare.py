#!/usr/bin/env python3
"""Overlay IOP vs time — Robin vs rigid wall (doc-g2-sim2 IVI)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

RHO = 995.0
PA_TO_MMHG = 0.0075006

PHASES = [
    ("baseline", 0, 5),
    ("ivi", 5, 11),
    ("recovery", 11, 20),
]

RUNS = (
    ("Robin", "results/robin_onaxis/iop_probe_p.txt", "#2980b9", "-"),
    ("Rigid", "results/rigid_onaxis/iop_probe_p.txt", "#c0392b", "--"),
)


def mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def read_probes(path: Path) -> tuple[list[float], list[float], list[float]]:
    ts, ac, vit = [], [], []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        ts.append(float(parts[0]))
        vals = [float(x) for x in parts[1:5]]
        ac.append(0.5 * (mmhg(vals[0]) + mmhg(vals[1])))
        vit.append(0.5 * (mmhg(vals[2]) + mmhg(vals[3])))
    return ts, ac, vit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    case = args.case

    series = []
    for label, rel, color, ls in RUNS:
        probe = case / rel
        if not probe.is_file():
            print(f"ERROR: missing {probe}", file=sys.stderr)
            sys.exit(1)
        ts, ac, vit = read_probes(probe)
        series.append((label, ts, ac, vit, color, ls))

    out = args.out or case / "figures" / "iop_ivi_robin_vs_rigid.png"
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.4), sharex=True)

    ymax_full = 0.0
    ymax_zoom = 0.0
    for _, ts, ac, vit, _, _ in series:
        ymax_full = max(ymax_full, max(ac), max(vit))
        ivi_ac = [y for t, y in zip(ts, ac) if 4.5 <= t <= 12]
        ivi_vit = [y for t, y in zip(ts, vit) if 4.5 <= t <= 12]
        if ivi_ac:
            ymax_zoom = max(ymax_zoom, max(ivi_ac), max(ivi_vit))
    ymax_full *= 1.08
    ymax_zoom = max(ymax_zoom * 1.15, 20.0)

    panels = (
        (axes[0, 0], 1, ymax_full, "AC — full scale"),
        (axes[0, 1], 2, ymax_full, "Vitreous — full scale"),
        (axes[1, 0], 1, ymax_zoom, "AC — Robin zoom (IVI window)"),
        (axes[1, 1], 2, ymax_zoom, "Vitreous — Robin zoom (IVI window)"),
    )

    for ax, idx, ymax, subtitle in panels:
        for name, t0, t1 in PHASES:
            ax.axvspan(t0, t1, color="#f4f6f7", alpha=0.9, zorder=0)
        for label, ts, ac, vit, color, ls in series:
            y = ac if idx == 1 else vit
            ax.plot(ts, y, label=label, lw=1.7, color=color, ls=ls)
        ax.set_ylabel(f"IOP [mmHg]")
        ax.set_title(subtitle, fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, ymax)
        if idx == 1 and ax is axes[0, 0]:
            ax.legend(frameon=False, loc="upper right")

    for ax in axes[1, :]:
        ax.set_xlabel("t [s]")
    for ax in axes[:, 0]:
        ax.set_xlim(min(series[0][1]), max(series[0][1]))

    fig.suptitle("G2 Sim2 — IVI: Robin vs rigid wall (on-axis tip)", y=0.98)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"Wrote {out}")
    for label, _, ac, vit, _, _ in series:
        print(f"  {label}: peak AC={max(ac):.1f}  peak vit={max(vit):.1f} mmHg")


if __name__ == "__main__":
    main()
