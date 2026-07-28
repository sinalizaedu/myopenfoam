#!/usr/bin/env python3
"""IOP vs time for doc-g2-sim2 (IVI + Robin)."""
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


def mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def resolve_probe(case: Path, wall: str, probe: Path | None = None) -> Path:
    if probe is not None:
        if not probe.is_file():
            raise SystemExit(f"ERROR: missing {probe}")
        return probe
    archived = case / "results" / f"{wall}_onaxis" / "iop_probe_p.txt"
    if archived.is_file():
        return archived
    live = case / "fluid/postProcessing/iop_probe/0/p"
    if live.is_file():
        return live
    raise SystemExit(f"ERROR: no IOP probe under {archived} or {live}")


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
    ap.add_argument("--wall", choices=("robin", "rigid"), default="robin")
    ap.add_argument("--case", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--probe",
        type=Path,
        default=None,
        help="IOP probe file (default: results/<wall>_onaxis/iop_probe_p.txt, else fluid/postProcessing)",
    )
    args = ap.parse_args()
    case = args.case
    wall = args.wall
    probe = resolve_probe(case, wall, args.probe)

    ts, ac, vit = read_probes(probe)
    out = args.out or case / "figures" / f"iop_ivi_{wall}_onaxis.png"
    wall_label = "Robin" if wall == "robin" else "Rigid wall"

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = {"baseline": "#ecf0f1", "ivi": "#fadbd8", "recovery": "#eafaf1"}
    ymax = max(max(ac), max(vit)) * 1.05
    for name, t0, t1 in PHASES:
        ax.axvspan(t0, t1, color=colors.get(name, "#f0f0f0"), alpha=0.7, zorder=0)
        ax.text(0.5 * (t0 + t1), ymax, name, ha="center", va="bottom", fontsize=7, color="0.35")

    ax.plot(ts, ac, label="AC", lw=1.8)
    ax.plot(ts, vit, label="Vitreous", lw=1.8)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("IOP [mmHg]")
    ax.set_title(f"G2 Sim2 — IVI + {wall_label} (on-axis tip)")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(min(ts), max(ts))
    ax.set_ylim(0, ymax)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"Wrote {out}  peak AC={max(ac):.2f}  peak vit={max(vit):.2f}")


if __name__ == "__main__":
    main()
