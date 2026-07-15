#!/usr/bin/env python3
"""
analyze_on-caso-4.py
====================
Analise da Fase B do on-caso-4 (runs ACOPLADOS: inchaco SANS + contato arterial
ancorado). Conta a historia central do caso:

    inchaco da bainha (P_CSF up) -> AREA de contato up + FORCA de contato up
                                 -> insulto ao nervo up

Le, por estagio de SANS:
  - brunaStuff/on-caso-4_stage_table.json : Dr_dura (inchaco), A_contact, P_contact,
    forca (vindos da Fase A / measure_on-caso-4_swelling.py);
  - cases/on-caso-4/ccx/on-caso-4_<tag>.frd : campos do run acoplado, de onde
    extraimos a RESPOSTA DO NERVO:
      * kink lateral por camada (on/pia/sas/dura);
      * offset lateral do centroide neural (tortuosidade);
      * sigma de von Mises maxima na vizinhanca do contato.

Saidas:
  brunaStuff/on-caso-4_summary.png
  brunaStuff/on-caso-4_summary.txt
  brunaStuff/on-caso-4_results.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-4/ccx")
OUT = Path("brunaStuff")
PREFIX = "on-caso-4"
STAGE_JSON = OUT / "on-caso-4_stage_table.json"
# Sufixo opcional dos .frd/saidas, p/ analisar runs em outra malha sem sobrescrever
# os da malha base. Ex.: ANALYZE_SUFFIX=_meshmed -> le on-caso-4_<tag>_meshmed.frd
# e escreve on-caso-4_summary_meshmed.{png,txt}.
SUFFIX = os.environ.get("ANALYZE_SUFFIX", "")

R_DURA = 2.5e-3
Z_ART = 22.5e-3


# ---------------------------------------------------------------------------
# Parser .frd: nos + ultimo DISP + ultimo STRESS
# ---------------------------------------------------------------------------
def _parse_data_line(L: str, n_floats: int):
    if len(L) < 3 + 10 + 12:
        return None
    try:
        nid = int(L[3:13])
    except ValueError:
        return None
    vals = []
    for k in range(n_floats):
        s = L[13 + 12 * k: 13 + 12 * (k + 1)]
        if not s:
            return None
        try:
            vals.append(float(s))
        except ValueError:
            return None
    return nid, vals


def parse_frd(path: Path):
    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    nodes = {}
    in_nodes = False
    for L in lines:
        s = L.strip()
        if not in_nodes:
            if s.startswith("2C ") or s == "2C":
                in_nodes = True
            continue
        if s.startswith("-3"):
            break
        if L.lstrip().startswith("-1"):
            r = _parse_data_line(L, 3)
            if r is not None:
                nodes[r[0]] = tuple(r[1])

    def last_block(varname: str, n_floats: int):
        blocks = []
        cur = {}
        active = False
        for L in lines:
            s = L.strip()
            if s.startswith("-4"):
                parts = s.split()
                vn = parts[1].strip() if len(parts) >= 2 else ""
                if vn == varname:
                    active = True
                    cur = {}
                else:
                    active = False
                continue
            if not active:
                continue
            if s.startswith("-3"):
                if cur:
                    blocks.append(cur)
                active = False
                cur = {}
                continue
            if s.startswith("-5"):
                continue
            if L.lstrip().startswith("-1"):
                r = _parse_data_line(L, n_floats)
                if r is not None:
                    cur[r[0]] = r[1]
        return blocks[-1] if blocks else {}

    disp = last_block("DISP", 3)
    stress = last_block("STRESS", 6)
    return nodes, disp, stress


def von_mises(s6):
    sxx, syy, szz, sxy, syz, szx = s6
    return np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                   + 3.0 * (sxy ** 2 + syz ** 2 + szx ** 2))


# ---------------------------------------------------------------------------
# Resposta do nervo por run
# ---------------------------------------------------------------------------
def analyze_run(tag: str):
    frd = CASE / f"{PREFIX}_{tag}{SUFFIX}.frd"
    if not frd.exists():
        return None
    nodes, disp, stress = parse_frd(frd)
    if not nodes or not disp:
        return None

    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.zeros_like(P)
    for i, n in enumerate(nids):
        if n in disp:
            U[i] = disp[n]
    r0 = np.hypot(P[:, 0], P[:, 1])

    res = {}
    # kink lateral por camada
    for name, r_t, dr in [("on", 0.5e-3, 0.10e-3), ("pia", 1.55e-3, 0.06e-3),
                          ("sas", 2.0e-3, 0.06e-3), ("dura", 2.5e-3, 0.06e-3)]:
        m = np.abs(r0 - r_t) < dr
        res[f"kink_{name}"] = (float(np.hypot(U[m, 0], U[m, 1]).max())
                               if m.sum() else 0.0)
    res["U_lat_global"] = float(np.hypot(U[:, 0], U[:, 1]).max())

    # offset lateral do centroide neural (nervo: r0 < 1.0 mm), max sobre z
    m_on = r0 < 1.0e-3
    offset_max = 0.0
    if m_on.sum():
        zr = np.round(P[m_on, 2] * 1e3).astype(int)  # bins de 1 mm
        xc = P[m_on, 0] + U[m_on, 0]
        yc = P[m_on, 1] + U[m_on, 1]
        for zb in np.unique(zr):
            sel = zr == zb
            off = np.hypot(xc[sel].mean(), yc[sel].mean())
            offset_max = max(offset_max, off)
    res["offset_neural_max"] = float(offset_max)

    # sigma von Mises maxima na vizinhanca do contato (dura + nervo, +X, z~22.5)
    vm_contact = 0.0
    if stress:
        m_zone = ((np.abs(P[:, 2] - Z_ART) < 3.0e-3) & (P[:, 0] > 0)
                  & (np.abs(np.degrees(np.arctan2(P[:, 1], P[:, 0]))) < 40))
        for i, n in enumerate(nids):
            if m_zone[i] and n in stress:
                vm = von_mises(stress[n])
                if vm > vm_contact:
                    vm_contact = vm
    res["vm_contact_max"] = float(vm_contact)
    return res


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    if not STAGE_JSON.exists():
        print(f"ERRO: {STAGE_JSON} nao existe. Rode a Fase A primeiro:")
        print("  bash brunaStuff/sweep_on-caso-4.sh phaseA")
        raise SystemExit(1)
    meta = json.loads(STAGE_JSON.read_text())
    stages = meta["stages"]

    runs = []
    for s in stages:
        tag = s["tag"]
        resp = analyze_run(tag)
        if resp is None:
            print(f"  [SKIP] {tag}: {CASE/(PREFIX+'_'+tag+SUFFIX+'.frd')} nao existe "
                  f"(rode a Fase B: bash brunaStuff/sweep_on-caso-4.sh phaseB)")
            continue
        row = dict(s)
        row.update(resp)
        runs.append(row)
        print(f"  {tag:<12} P_CSF={s['P_CSF']:>5} A={s['A_contact_mm2']:.3f} mm2 "
              f"F={s['force_mN']:.3f} mN | kink_on={resp['kink_on']*1e3:.3f} mm "
              f"offset={resp['offset_neural_max']*1e3:.3f} mm "
              f"vM_contato={resp['vm_contact_max']*1e-3:.2f} kPa")

    if not runs:
        print("\nNenhum run acoplado (Fase B) encontrado. Rode:")
        print("  bash brunaStuff/sweep_on-caso-4.sh phaseB")
        raise SystemExit(1)

    tags = [r["tag"] for r in runs]
    pcsf = [r["P_CSF"] for r in runs]
    dr = [r["dr_sector_um"] for r in runs]
    A = [r["A_contact_mm2"] for r in runs]
    pc = [r["P_CONTACT"] for r in runs]
    F = [r["force_mN"] for r in runs]

    # ----- figura -----
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    mesh_note = (" [malha independente: theta,z 2x ~27.6k hex]" if SUFFIX == "_meshmed"
                 else (f" [{SUFFIX}]" if SUFFIX else " [malha base 1x]"))
    fig.suptitle(
        "on-caso-4 - inchaco SANS dirige AREA e FORCA de contato arterial" + mesh_note + "\n"
        "cadeia: P_CSF up -> bainha distende -> area+forca de contato up -> insulto no nervo up",
        fontsize=12.5)

    # (A) inchaco (Dr_dura) e area vs estagio
    ax = axes[0, 0]
    ax.plot(tags, dr, "o-", color="teal", lw=2, markersize=10, label="Dr_dura [um]")
    ax.set_ylabel("Dr_dura (inchaco) [um]", color="teal")
    ax.tick_params(axis="y", labelcolor="teal")
    ax2 = ax.twinx()
    ax2.plot(tags, A, "s--", color="indianred", lw=2, markersize=9, label="A_contato [mm2]")
    ax2.set_ylabel("area de contato [mm^2]", color="indianred")
    ax2.tick_params(axis="y", labelcolor="indianred")
    ax.set_title("(A) inchaco da bainha e area de contato")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(alpha=0.3)

    # (B) P_contact e forca vs estagio
    ax = axes[0, 1]
    ax.plot(tags, pc, "o-", color="navy", lw=2, markersize=10, label="P_contact [Pa]")
    ax.set_ylabel("P_contact [Pa]", color="navy")
    ax.tick_params(axis="y", labelcolor="navy")
    ax2 = ax.twinx()
    ax2.plot(tags, F, "^--", color="darkorange", lw=2, markersize=9, label="forca [mN]")
    ax2.set_ylabel("forca de contato [mN]", color="darkorange")
    ax2.tick_params(axis="y", labelcolor="darkorange")
    ax.set_title("(B) pressao e forca de contato da arteria")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(alpha=0.3)

    # (C) kink lateral por camada vs P_CSF
    ax = axes[1, 0]
    for nm, c, lab in [("kink_on", "orange", "nervo (r=0.5)"),
                       ("kink_pia", "green", "pia (r=1.55)"),
                       ("kink_sas", "cyan", "SAS (r=2.0)"),
                       ("kink_dura", "red", "dura (r=2.5)")]:
        ys = [r[nm] * 1e3 for r in runs]
        ax.plot(pcsf, ys, "o-", lw=2, markersize=9, color=c, label=lab)
    ax.set_xlabel("P_CSF [Pa] (inchaco)")
    ax.set_ylabel("|U_lat| max por camada [mm]")
    ax.set_title("(C) kink lateral do nervo vs inchaco")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # (D) von Mises no contato + offset neural vs estagio
    ax = axes[1, 1]
    vm = [r["vm_contact_max"] * 1e-3 for r in runs]
    ax.plot(tags, vm, "o-", color="purple", lw=2, markersize=10,
            label="sigma_vM max no contato [kPa]")
    ax.set_ylabel("sigma_vM max no contato [kPa]", color="purple")
    ax.tick_params(axis="y", labelcolor="purple")
    ax2 = ax.twinx()
    off = [r["offset_neural_max"] * 1e3 for r in runs]
    ax2.plot(tags, off, "^--", color="brown", lw=2, markersize=9,
             label="offset centroide neural [mm]")
    ax2.set_ylabel("offset lateral do nervo [mm]", color="brown")
    ax2.tick_params(axis="y", labelcolor="brown")
    ax.set_title("(D) insulto ao nervo: tensao no contato e tortuosidade")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_png = OUT / f"on-caso-4_summary{SUFFIX}.png"
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    print(f"\nGrafico salvo em: {out_png}")

    # ----- summary txt -----
    lines = [
        "on-caso-4 - inchaco SANS dirigindo area+forca de contato (resultados)",
        "=" * 92,
        f"{'tag':<12}{'P_CSF':>7}{'Dr_um':>8}{'A_mm2':>8}{'Pc_Pa':>9}{'F_mN':>8}"
        f"{'kink_on':>9}{'kink_dura':>10}{'offset':>9}{'vM_kPa':>9}",
        "-" * 92,
    ]
    for r in runs:
        lines.append(
            f"{r['tag']:<12}{r['P_CSF']:>7}{r['dr_sector_um']:>8.2f}"
            f"{r['A_contact_mm2']:>8.3f}{r['P_CONTACT']:>9.0f}{r['force_mN']:>8.3f}"
            f"{r['kink_on']*1e3:>9.3f}{r['kink_dura']*1e3:>10.3f}"
            f"{r['offset_neural_max']*1e3:>9.3f}{r['vm_contact_max']*1e-3:>9.2f}")
    txt = "\n".join(lines)
    (OUT / f"on-caso-4_summary{SUFFIX}.txt").write_text(txt + "\n")
    print("\n" + txt)
    print(f"\nResumo: brunaStuff/on-caso-4_summary{SUFFIX}.txt")

    (OUT / f"on-caso-4_results{SUFFIX}.json").write_text(json.dumps(runs, indent=2))
    print(f"JSON: brunaStuff/on-caso-4_results{SUFFIX}.json")


if __name__ == "__main__":
    main()
