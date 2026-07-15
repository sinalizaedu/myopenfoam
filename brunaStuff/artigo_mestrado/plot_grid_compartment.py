#!/usr/bin/env python3
"""Figuras finais da grade de compartimentalizacao do on-caso-1.2 (FSI Caso 3).

Le:
  cases/on-caso-1.2/_grid_calib/calib_results.json  (fluido-so: Q(P,d))
  cases/on-caso-1.2/_grid/grid_fsi_results.json     (FSI: distensao dura/pia)

Gera:
  brunaStuff/on-caso-1.2_compartment_grid.png
  brunaStuff/on-caso-1.2_compartment_grid_summary.txt
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CALIB = REPO / "cases" / "on-caso-1.2" / "_grid_calib" / "calib_results.json"
FSI = REPO / "cases" / "on-caso-1.2" / "_grid" / "grid_fsi_results.json"

# Volume do SAS (anel r=1.55..2.35 mm, L=30 mm) p/ tempo de residencia V/Q
R_PIA, R_DURA, L_SAS = 1.55e-3, 2.35e-3, 0.030
V_SAS = math.pi * (R_DURA ** 2 - R_PIA ** 2) * L_SAS


def main():
    calib = json.loads(CALIB.read_text()) if CALIB.exists() else []
    fsi = json.loads(FSI.read_text()) if FSI.exists() else []

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))

    # ---- Painel A: Q vs PIC, curvas por d (compartimentalizacao) ----
    ax = axes[0]
    ds = sorted({r["d"] for r in calib})
    colors = {1e15: "#27ae60", 1e16: "#f39c12", 1e17: "#e67e22", 1e19: "#c0392b"}
    for d in ds:
        pts = sorted([r for r in calib if r["d"] == d], key=lambda z: z["p_target_pa"])
        if not pts:
            continue
        P = [r["p_target_pa"] for r in pts]
        Q = [r["q_outlet"] for r in pts]
        ax.semilogy(P, Q, "-o", color=colors.get(d, "#555"),
                    label=f"d = {d:g} m⁻²")
    ax.set_xlabel("PIC no SAS (Pa)")
    ax.set_ylabel("Q de drenagem (m³/s)")
    ax.set_title("A) Compartimentalização: vazão vs PIC\n(mesma PIC, Q despenca com d → estase)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()

    # eixo secundario: tempo de residencia V/Q (dias)
    def q2days(q):
        return V_SAS / q / 86400.0 if q and q > 0 else float("nan")
    ax2 = ax.twinx()
    ax2.set_yscale("log")
    lo, hi = ax.get_ylim()
    ax2.set_ylim(q2days(lo), q2days(hi))
    ax2.set_ylabel("tempo de residência V/Q (dias)")

    # ---- Painel B: distensao dura/pia vs PIC (FSI Neo-Hookean, d=1e15) ----
    ax = axes[1]
    nh = [r for r in fsi if r.get("mat") == "neohooke" and r.get("status") == "OK"]
    curve = sorted([r for r in nh if r["d"] == 1e15], key=lambda z: z["p_target_pa"])
    if curve:
        P = [r["p_target_pa"] for r in curve]
        dura = [r.get("dura_ur_max_um", float("nan")) for r in curve]
        pia = [abs(r.get("pia_ur_max_um", float("nan"))) for r in curve]
        ax.plot(P, dura, "-o", color="#c0392b", label="Dura (distensão bainha)")
        ax.plot(P, pia, "-s", color="#2980b9", label="Pia (compressão nervo)")
    # checagem de independencia de d em 3900
    chk = [r for r in nh if r["p_target_pa"] == 3900.0]
    if len(chk) >= 2:
        for r in chk:
            if r["d"] != 1e15:
                ax.plot([3900], [r.get("dura_ur_max_um", float("nan"))], "x",
                        color="#7f8c8d", ms=11,
                        label=f"Dura @ d={r['d']:g} (check indep. de d)")
    ax.set_xlabel("PIC no SAS (Pa)")
    ax.set_ylabel("|u_r| máx (µm)")
    ax.set_title("B) Resposta estrutural vs PIC (FSI Neo-Hookean)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.suptitle("on-caso-1.2 (FSI Caso 3) — Compartimentalização do LCR (modelo de Davson: PIC = R·Q)",
                 fontsize=13)
    fig.tight_layout()
    out = HERE / "on-caso-1.2_compartment_grid.png"
    fig.savefig(out, dpi=130)
    print(f"figura -> {out}")

    # ---- resumo txt ----
    lines = ["=== on-caso-1.2 (FSI Caso 3) - grade de compartimentalizacao ===", ""]
    lines.append(f"V_SAS = {V_SAS:.3e} m^3")
    lines.append("")
    lines.append("FASE 1 (fluido-so): Q de drenagem por (PIC, d)")
    lines.append(f"{'PIC(Pa)':>8} {'d(m^-2)':>10} {'p_SAS(Pa)':>10} {'Q(m3/s)':>13} {'tau_resid(dias)':>16}")
    for r in sorted(calib, key=lambda z: (z["p_target_pa"], z["d"])):
        td = q2days(r["q_outlet"])
        lines.append(f"{r['p_target_pa']:>8.0f} {r['d']:>10.0g} {r['p_sas_pa']:>10.1f} "
                     f"{r['q_outlet']:>13.4e} {td:>16.1f}")
    lines.append("")
    lines.append("FASE 2 (FSI): distensao radial maxima (corpo do nervo)")
    lines.append(f"{'tag':>22} {'PIC':>6} {'mat':>9} {'dura(um)':>9} {'pia(um)':>9}")
    for r in sorted(fsi, key=lambda z: (z["p_target_pa"], z["mat"], z["d"])):
        lines.append(f"{r['tag']:>22} {r['p_target_pa']:>6.0f} {r['mat']:>9} "
                     f"{r.get('dura_ur_max_um', float('nan')):>9.2f} "
                     f"{r.get('pia_ur_max_um', float('nan')):>9.2f}")
    txt = HERE / "on-caso-1.2_compartment_grid_summary.txt"
    txt.write_text("\n".join(lines) + "\n")
    print(f"resumo -> {txt}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
