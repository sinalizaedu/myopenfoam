#!/usr/bin/env python3
"""IOP vs time — ACP-only (sim3) or IVI+ACP (sim4/sim5/doc-run-*)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

RHO = 995.0
PA_TO_MMHG = 0.0075006

PHASES_SIM3 = [
    ("baseline", 0, 5), ("wait", 5, 15), ("acp", 15, 22), ("recovery_acp", 22, 30),
]
PHASES_SIM4 = [
    ("baseline", 0, 5), ("ivi", 5, 12), ("gap", 12, 15),
    ("acp", 15, 22), ("recovery", 22, 30),
]

IVI_T0, IVI_T1 = 5.0, 12.0
ACP_T0, ACP_T1 = 15.0, 22.0


def uses_ivi_acp_protocol(case_name: str) -> bool:
    return case_name in ("doc-g2-sim4", "doc-g2-sim5") or case_name.startswith(
        "doc-run-"
    )


def mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


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
        "--protocol",
        choices=("acp", "ivi_acp", "auto"),
        default="auto",
        help="Override protocol detection from case directory name",
    )
    ap.add_argument(
        "--probe",
        type=Path,
        default=None,
        help="IOP probe file (default: results/iop_probe_p.txt, else fluid/postProcessing)",
    )
    args = ap.parse_args()
    case = args.case
    protocol = args.protocol
    if protocol == "auto":
        protocol = "ivi_acp" if uses_ivi_acp_protocol(case.name) else "acp"

    phases_raw = PHASES_SIM4 if protocol == "ivi_acp" else PHASES_SIM3
    phases = [{"name": n, "t0": a, "t1": b} for n, a, b in phases_raw]

    probe = resolve_probe(case, args.probe)
    ts, ac, vit = read_probes(probe)
    if protocol == "ivi_acp":
        out = args.out or case / "figures" / "iop_ivi_acp_onaxis.png"
    else:
        out = args.out or case / "figures" / "iop_acp_onaxis.png"

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = {
        "baseline": "#ecf0f1",
        "wait": "#ecf0f1",
        "gap": "#ecf0f1",
        "ivi": "#fadbd8",
        "acp": "#e8daef",
        "recovery_acp": "#eafaf1",
        "recovery": "#eafaf1",
    }
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
    if protocol == "ivi_acp":
        label = "volumetric" if "volume" in case.name else "patch"
        title = f"{case.name} — IVI+ACP ({label}) + volume-matched wall flux"
    else:
        title = f"{case.name} — ACP + volume-matched wall flux"
    ax.set_title(title)
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(min(ts), max(ts))
    ax.set_ylim(0, ymax)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)

    acp_pairs = [(t, a, v) for t, a, v in zip(ts, ac, vit) if ACP_T0 <= t <= ACP_T1]
    if not acp_pairs:
        raise SystemExit(f"ERROR: no probe samples in ACP phase {ACP_T0}–{ACP_T1} s")
    min_ac = min(acp_pairs, key=lambda r: r[1])
    min_vit = min(acp_pairs, key=lambda r: r[2])

    if protocol == "ivi_acp":
        ivi_pairs = [(t, a, v) for t, a, v in zip(ts, ac, vit) if IVI_T0 <= t <= IVI_T1]
        if not ivi_pairs:
            raise SystemExit(f"ERROR: no probe samples in IVI phase {IVI_T0}–{IVI_T1} s")
        peak_ac = max(ivi_pairs, key=lambda r: r[1])
        peak_vit = max(ivi_pairs, key=lambda r: r[2])
        print(
            f"Wrote {out}  peak IVI AC={peak_ac[1]:.2f} vit={peak_vit[2]:.2f} @ {peak_ac[0]:.1f}s"
            f"  min ACP AC={min_ac[1]:.2f} vit={min_vit[2]:.2f} @ {min_ac[0]:.1f}s"
        )
    else:
        print(
            f"Wrote {out}  min ACP AC={min_ac[1]:.2f} vit={min_vit[2]:.2f} @ {min_ac[0]:.1f}s"
        )


if __name__ == "__main__":
    main()
