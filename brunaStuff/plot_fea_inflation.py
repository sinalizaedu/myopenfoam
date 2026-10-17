#!/usr/bin/env python3
"""Overlay V(P) and Goldmann P(t) for fea-simplf vs fea-sim.

Also writes compare_sphere_vs_b2.txt (sphere-only is valid if B2 died).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

P0 = 15.0
DV = 50.0
# Thin-shell isotropic sclera bounds from the plan (same repo moduli).
THIN_SPHERE_DIOP = 17.0   # mmHg at 50 µL, R=8.67 mm, V~2.73 mL
THIN_B2_DIOP = 19.0       # mmHg at 50 µL, B2 equatorial
R_IN_SCLERA = 8.67e-3     # m
E_SCLERA = 2.54e6         # Pa
NU = 0.47
T_SCLERA = 0.33e-3        # m
MMHG = 133.322


def load_csv(path: Path):
    rows = list(csv.DictReader(path.open()))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def load_json(path: Path | None):
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text())


def rigidity_k(infl: dict) -> float | None:
    """K = dP/dV [mmHg/µL] on the living branch just above 15 mmHg."""
    living = infl["p_mmhg"] >= P0 - 0.2
    dv = infl["dV_full_uL"][living]
    p = infl["p_mmhg"][living]
    if len(dv) < 2:
        return None
    order = np.argsort(dv)
    dv, p = dv[order], p[order]
    # first interval with ΔV > 1 µL
    for i in range(len(dv) - 1):
        if dv[i + 1] - dv[i] > 1.0:
            return float((p[i + 1] - p[i]) / (dv[i + 1] - dv[i]))
    return float((p[-1] - p[0]) / (dv[-1] - dv[0] + 1e-15))


def thin_shell_p(dv_uL: np.ndarray, diop_at_50: float) -> np.ndarray:
    return P0 + diop_at_50 * (dv_uL / DV)


def write_compare(out: Path, args) -> None:
    sph_j = load_json(
        args.sphere_json
        or (args.sphere_infl.with_suffix(".json") if args.sphere_infl else None)
    )
    b2_j = load_json(
        args.b2_json or (args.b2_infl.with_suffix(".json") if args.b2_infl else None)
    )
    sph_g = load_json(
        args.sphere_gold.with_suffix(".json")
        if args.sphere_gold and args.sphere_gold.exists()
        else None
    )
    b2_g = load_json(
        args.b2_gold.with_suffix(".json")
        if args.b2_gold and args.b2_gold.exists()
        else None
    )
    status_path = args.out_dir / "status.txt"
    status = status_path.read_text().strip() if status_path.exists() else "unknown"

    v_sphere_analytic = (4.0 / 3.0) * math.pi * R_IN_SCLERA**3 * 1e9  # µL
    v0_sph = sph_j.get("v0_full_uL")
    rel = None
    if v0_sph:
        rel = 100.0 * (v0_sph - v_sphere_analytic) / v_sphere_analytic

    lines = []
    w = lines.append
    w("fea-sim vs fea-simplf — corneoscleral inflation + Goldmann")
    w("IOP0 = 15 mmHg. 50 mmHg is a solver ceiling, not a clinical target.")
    w("Units SI in CalculiX (m, Pa). Volumes below are full-eye (wedge ×4).")
    w("")
    w("=== sphere (fea-simplf) ===")
    w(f"  undeformed V0            = {v0_sph} µL")
    w(f"  analytic 1/4·4/3π R_in^3 = {v_sphere_analytic:.3f} µL  (R_in = 8.67 mm sclera)")
    w(f"  relative difference      = {rel:.2f} %" if rel is not None else "  relative difference = n/a")
    w("  (mixed cornea R_in=8.16 mm + 5° polar holes → a few % below the pure-sclera sphere is expected)")
    w(f"  *DSLOAD outward          = {sph_j.get('outward_ok')}  {sph_j.get('outward_msg')}")
    w(f"  V(15 mmHg)               = {sph_j.get('v_at_15_uL')} µL")
    w(f"  covers +50 µL            = {sph_j.get('covers_50uL')}  (dV_max = {sph_j.get('dV_max_uL')} µL)")
    w(f"  P(50 µL) no outflow      = {sph_j.get('P_at_50uL_mmHg')} mmHg")
    w(f"  ΔIOP(50 µL) no outflow   = {sph_j.get('dIOP_50uL_mmHg')} mmHg")
    w(f"  thin-shell analytic      = {THIN_SPHERE_DIOP} mmHg  (plan bound, same radii)")
    if args.sphere_infl and args.sphere_infl.exists():
        sph = load_csv(args.sphere_infl)
        k = rigidity_k(sph)
        w(f"  K = dP/dV at 15 mmHg     = {k:.4f} mmHg/µL" if k else "  K = n/a")
        living = sph["p_mmhg"] >= P0 - 0.2
        if living.any():
            w(f"  Uy cornea apex @ max P   = {sph['uy_apex'][living][-1]:.4e} m")
            w(f"  Uy posterior     @ max P = {sph['uy_post'][living][-1]:.4e} m")
    if sph_g:
        w(f"  Goldmann P_peak          = {sph_g.get('P_peak_mmHg')} mmHg at t={sph_g.get('t_peak_s')} s")
        w(f"  Goldmann ΔIOP peak       = {sph_g.get('dIOP_peak_mmHg')} mmHg  (TM trims ~4 % of 50 µL)")
        w(f"  Goldmann P(40 min)       = {sph_g.get('P_inf_mmHg')} mmHg  (must → 15)")
        w(f"  Goldmann τ_lin           = {sph_g.get('tau_lin_min')} min  (rabbit C=0.48; not human 15–60 min)")
        w(f"  t back to 16 mmHg        = {sph_g.get('t_back_to_16mmHg_min')} min")
    w("")
    w("=== B2 anatomical (fea-sim) ===")
    w(f"  Allrun status            = {status}")
    if not b2_j:
        w("  NO CONVERGED B2 NUMBER. Do not invent ΔIOP from a crashed .sta.")
        w(f"  thin-shell B2 equatorial = {THIN_B2_DIOP} mmHg at 50 µL (plan bound)")
        w("  Study fallback (plan step 4): sphere FEA + thin-shell 17/19 mmHg.")
        w("  free-iris (fea-sim.inp) diverged in Step 1 increment 1:")
        w("    iter 1: Δu = 2.47 mm; iter 3: Δu = 2.46 m, residual ~1e15 (iris E=4 kPa).")
        if status == "frozen_failed":
            w("  frozen-iris (fea-sim_frozen.inp): also diverged.")
            w("    *ERROR: increment size smaller than minimum (cut back to 7.6e-7 < 1e-6).")
            w("    Soft retina (E=20 kPa) + axis C3D6 still kill NR with iris clamped.")
            w("    Anisotropy skipped (requires a converged isotropic B2 run).")
        else:
            w("  frozen-iris result: not available in this file yet.")
    else:
        w(f"  undeformed V0            = {b2_j.get('v0_full_uL')} µL")
        w("  B2 vitreous ellipsoid     ≈ 2020 µL (geometry spec; not the sphere 2730 µL)")
        w(f"  *DSLOAD outward          = {b2_j.get('outward_ok')}  {b2_j.get('outward_msg')}")
        w(f"  V(15 mmHg)               = {b2_j.get('v_at_15_uL')} µL")
        w(f"  covers +50 µL            = {b2_j.get('covers_50uL')}  (dV_max = {b2_j.get('dV_max_uL')} µL)")
        w(f"  P(50 µL) no outflow      = {b2_j.get('P_at_50uL_mmHg')} mmHg")
        w(f"  ΔIOP(50 µL) no outflow   = {b2_j.get('dIOP_50uL_mmHg')} mmHg")
        w(f"  thin-shell B2 equatorial = {THIN_B2_DIOP} mmHg")
        if args.b2_infl and args.b2_infl.exists():
            b2 = load_csv(args.b2_infl)
            k = rigidity_k(b2)
            w(f"  K = dP/dV at 15 mmHg     = {k:.4f} mmHg/µL" if k else "  K = n/a")
            living = b2["p_mmhg"] >= P0 - 0.2
            if living.any():
                w(f"  Uy cornea apex @ max P   = {b2['uy_apex'][living][-1]:.4e} m")
                w(f"  Uy posterior     @ max P = {b2['uy_post'][living][-1]:.4e} m")
        if status == "frozen_iris":
            w("  iris BC                 = FROZEN (Ux=Uy=Uz=0 on fsi_iris)")
            w("  free-iris ΔIOP          = not available (free deck diverged in Step 1)")
            w("  |ΔIOP_free − ΔIOP_frozen|/ΔIOP_frozen cannot be formed — free run does not exist.")
        elif status == "free_iris":
            w("  iris BC                 = FREE (pressure on fsi_iris)")
        if b2_g:
            w(f"  Goldmann P_peak          = {b2_g.get('P_peak_mmHg')} mmHg at t={b2_g.get('t_peak_s')} s")
            w(f"  Goldmann ΔIOP peak       = {b2_g.get('dIOP_peak_mmHg')} mmHg")
            w(f"  Goldmann P(40 min)       = {b2_g.get('P_inf_mmHg')} mmHg  (must → 15)")
            w(f"  Goldmann τ_lin           = {b2_g.get('tau_lin_min')} min")
        if sph_j.get("dIOP_50uL_mmHg") and b2_j.get("dIOP_50uL_mmHg"):
            w("")
            w("  Do not expect ΔIOP@50 µL within 20–30 % (V0 sphere 2.73 mL vs B2 ~2.02 mL).")
            w("  Compare K = dP/dV and ΔIOP at the same ΔV/V.")
    w("")
    w("=== limits (do not overclaim) ===")
    w("  Living CAD treated as stress-free (no inverse prestress).")
    w("  Choroidal blood missing → FEA peak is an upper bound on the scleral share.")
    w("  NH ≈ linear at ~0.7 % hoop strain. Rabbit 50 µL ≠ human IVI 40–60 mmHg.")
    w("  Goldmann τ is rabbit C=0.48 µL/min/mmHg, not human C≈0.28 plus creep.")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sphere-infl", type=Path)
    ap.add_argument("--b2-infl", type=Path)
    ap.add_argument("--sphere-gold", type=Path)
    ap.add_argument("--b2-gold", type=Path)
    ap.add_argument("--sphere-json", type=Path)
    ap.add_argument("--b2-json", type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for path, lab, col in (
        (args.sphere_infl, "sphere (fea-simplf)", "C0"),
        (args.b2_infl, "B2 (fea-sim)", "C1"),
    ):
        if path is None or not path.exists():
            continue
        d = load_csv(path)
        living = d["p_mmhg"] >= P0 - 0.2
        ax.plot(d["dV_full_uL"][living], d["p_mmhg"][living], lw=2, color=col, label=lab)
    dv_line = np.linspace(0.0, 80.0, 50)
    ax.plot(
        dv_line,
        thin_shell_p(dv_line, THIN_SPHERE_DIOP),
        color="C0",
        ls="--",
        lw=1.0,
        label=f"thin-shell sphere ({THIN_SPHERE_DIOP:.0f} mmHg / 50 µL)",
    )
    ax.plot(
        dv_line,
        thin_shell_p(dv_line, THIN_B2_DIOP),
        color="C1",
        ls="--",
        lw=1.0,
        label=f"thin-shell B2 eq. ({THIN_B2_DIOP:.0f} mmHg / 50 µL)",
    )
    ax.axhline(P0, color="0.4", ls="--", lw=0.8, label="IOP0 = 15 mmHg")
    ax.axvline(50.0, color="0.4", ls=":", lw=0.8, label="50 µL")
    ax.set_xlabel("extra cavity volume  ΔV  [µL]  (full eye)")
    ax.set_ylabel("IOP  [mmHg]")
    ax.set_title("Corneoscleral inflation  (living branch, P ≥ 15 mmHg)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.out_dir / "iop_vs_volume.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for path, lab, col in (
        (args.sphere_gold, "sphere Goldmann", "C0"),
        (args.b2_gold, "B2 Goldmann", "C1"),
    ):
        if path is None or not path.exists():
            continue
        d = load_csv(path)
        ax.plot(d["t_min"], d["P_mmHg"], lw=2, color=col, label=lab)
    ax.axhline(P0, color="0.4", ls="--", lw=0.8, label="P∞ = 15 mmHg")
    ax.set_xlabel("time  [min]   (rabbit TM drain, τ ≈ 5.5 min — not human 15–60 min)")
    ax.set_ylabel("IOP  [mmHg]")
    ax.set_title("Goldmann restoration after 50 µL / 6 s IVI")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(args.out_dir / "iop_vs_time_goldmann.png", dpi=140)
    plt.close(fig)
    print(f"wrote {args.out_dir / 'iop_vs_volume.png'}")
    print(f"wrote {args.out_dir / 'iop_vs_time_goldmann.png'}")

    write_compare(args.out_dir / "compare_sphere_vs_b2.txt", args)


if __name__ == "__main__":
    main()
