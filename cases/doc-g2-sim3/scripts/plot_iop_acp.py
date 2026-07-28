#!/usr/bin/env python3
"""IOP vs time for doc-g2-sim3 (ACP) or doc-g2-sim4 (IVI+ACP)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

RHO = 995.0
PA_TO_MMHG = 0.0075006

# Default phase shading (overridden from case name)
PHASES_SIM3 = [
    ("baseline", 0, 5), ("wait", 5, 15), ("acp", 15, 21), ("recovery_acp", 21, 30),
]
PHASES_SIM4 = [
    ("baseline", 0, 5), ("ivi", 5, 11), ("gap", 11, 15),
    ("acp", 15, 21), ("recovery", 21, 30),
]


def mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def window_extrema(
    ts: list[float], ac: list[float], vit: list[float], t0: float, t1: float, mode: str
) -> tuple[float, float, float]:
    """Min or max of AC in [t0, t1]; returns (t_at_extreme, ac, vit)."""
    pairs = [(t, a, v) for t, a, v in zip(ts, ac, vit) if t0 <= t <= t1]
    if not pairs:
        raise ValueError(f"no samples in [{t0}, {t1}]")
    pick = max if mode == "max" else min
    return pick(pairs, key=lambda x: x[1])


def resolve_probe(case: Path, probe: Path | None = None) -> Path:
    if probe is not None:
        if not probe.is_file():
            raise SystemExit(f"ERROR: missing {probe}")
        return probe
    archived = case / "results" / "iop_probe_p.txt"
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
    ap.add_argument("--case", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--probe",
        type=Path,
        default=None,
        help="IOP probe file (default: results/iop_probe_p.txt, else fluid/postProcessing)",
    )
    args = ap.parse_args()
    case = args.case
    phases_raw = PHASES_SIM4 if case.name == "doc-g2-sim4" else PHASES_SIM3
    phases = [{"name": n, "t0": a, "t1": b} for n, a, b in phases_raw]

    probe = resolve_probe(case, args.probe)
    ts, ac, vit = read_probes(probe)
    if case.name == "doc-g2-sim4":
        out = args.out or case / "figures" / "iop_ivi_acp_onaxis.png"
    else:
        out = args.out or case / "figures" / "iop_acp_onaxis.png"

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = {"baseline": "#ecf0f1", "wait": "#ecf0f1", "gap": "#ecf0f1",
              "ivi": "#fadbd8", "acp": "#e8daef", "recovery_acp": "#eafaf1", "recovery": "#eafaf1"}
    ymax = max(max(ac), max(vit)) * 1.08
    for ph in phases:
        t0, t1 = ph["t0"], ph["t1"]
        c = colors.get(ph["name"], "#f0f0f0")
        ax.axvspan(t0, t1, color=c, alpha=0.7, zorder=0)
        ax.text(0.5 * (t0 + t1), ymax * 0.98, ph["name"], ha="center", va="top", fontsize=7, color="0.35")

    ax.plot(ts, ac, label="AC", lw=1.8)
    ax.plot(ts, vit, label="Vitreous", lw=1.8)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("IOP [mmHg]")
    title = "G2 Sim3 — ACP + Robin" if case.name == "doc-g2-sim3" else "G2 Sim4 — IVI + ACP + Robin"
    ax.set_title(title)
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(min(ts), max(ts))
    ax.set_ylim(0, ymax)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    if case.name == "doc-g2-sim4":
        t_i, ac_i, vit_i = window_extrema(ts, ac, vit, 5, 11, "max")
        t_a, ac_a, vit_a = window_extrema(ts, ac, vit, 15, 21, "min")
        print(
            f"Wrote {out}  peak IVI AC={ac_i:.2f} vit={vit_i:.2f} @ {t_i:.1f}s"
            f"  min ACP AC={ac_a:.2f} vit={vit_a:.2f} @ {t_a:.1f}s"
        )
    else:
        t_a, ac_a, vit_a = window_extrema(ts, ac, vit, 15, 21, "min")
        print(f"Wrote {out}  min ACP AC={ac_a:.2f} vit={vit_a:.2f} @ {t_a:.1f}s")


if __name__ == "__main__":
    main()
