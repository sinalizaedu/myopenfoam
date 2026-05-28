"""TESTE B da bateria 'compartimentalizacao FSI':
   Velocidade residual |U| no fluido (equilibrio estatico).

Hipotese H0 (Pascal puro + cul-de-sac quasi-fechado):
  Em equilibrio estatico ideal, |U| -> 0 em todo o anel SAS.
  Qualquer |U| > 0 e' (i) ruido numerico do solver iterativo
  (PIMPLE + IQN-ILS), ou (ii) circulacao parasita induzida pela
  carga assimetrica do contact_local que NAO seria absorvida
  perfeitamente pelo modo de inflacao isotropica do anel.

Diagnostico discriminante:
  (1) |U|_max e localizacao (x,y,z) / (r,theta,z).
  (2) Reynolds local Re = |U|_max * L_char / nu, com L_char = espessura
      do anel SAS (0.8 mm) e nu = 1e-6 m^2/s. Re << 1 confirma regime
      de Stokes (ainda mais: |U|<<Pa/(mu/L)*L = 1e6 m/s, valor trivial).
  (3) Decomposicao cilindrica (U_r, U_theta, U_z) por cell:
       - se H0 e' verdadeira: U_r, U_theta, U_z sao todos randomicos
         com media zero e variancia comparavel.
       - se houver compartimentalizacao com fuga axial: <U_z>(z) tem
         padrao (gradiente axial coerente, ex.: U_z positivo perto do
         inlet, negativo perto do cul-de-sac).
       - se houver circulacao de Stokes: <U_theta>(theta) ou (z) tem
         padrao senoidal com pico no setor da carga.
  (4) Razao Pe_max = U_max / (visc/L) (so' para escala; se Pe<<1, e'
      basicamente Stokes pure).

Compara on-fsi-2 e on-fsi-3 (esperado: |U| escala com P_inlet pois e' o
unico forcing externo que induz circulacao numerica).

OBS: roda LOCAL (sem docker), reusa os Cx,Cy,Cz ja' gerados em t=0
pelo Teste A.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from diag_fsi_compartmentalization_A import (
    parse_scalar_field, parse_vector_field, get_fluid_cell_centres,
    Z_CONTACT_M, RHO_LCR,
)

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
OUT_DIR = Path(__file__).resolve().parent / "sans_outputs"
OUT_DIR.mkdir(exist_ok=True)

# anel SAS (do blockMesh)
R_INNER_M = 0.00155       # 1.55 mm = pia exterior
R_OUTER_M = 0.00235       # 2.35 mm = dura interior
L_CHAR_M  = R_OUTER_M - R_INNER_M   # 0.8 mm = espessura radial do anel
NU_LCR    = 1.0e-6        # m^2/s (LCR newtoniano)
MU_LCR    = NU_LCR * RHO_LCR  # 1e-3 Pa.s

# pressao do inlet (Pa) para escala
P_INLET = {"on-fsi-2": 1333.0, "on-fsi-3": 3800.0}


def cylindrical_decompose(U: np.ndarray, cx: np.ndarray, cy: np.ndarray
                          ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Decompoe U=(Ux,Uy,Uz) em (Ur, Utheta, Uz) usando o centroid no plano xy.
    Convencao: U_r = +outward, U_theta = +counterclockwise."""
    r = np.hypot(cx, cy)
    er_x = cx / r;  er_y = cy / r
    et_x = -cy / r; et_y = cx / r
    Ur     = U[:, 0]*er_x + U[:, 1]*er_y
    Utheta = U[:, 0]*et_x + U[:, 1]*et_y
    Uz     = U[:, 2]
    return Ur, Utheta, Uz


def bin_axis_average(z: np.ndarray, v: np.ndarray, dz_mm: float = 1.0
                     ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Bins por z em mm; devolve (z_centro_mm, v_avg, v_std)."""
    z_mm = z * 1000.0
    bins = np.arange(np.floor(z_mm.min()), np.ceil(z_mm.max()) + dz_mm, dz_mm)
    centers = 0.5 * (bins[:-1] + bins[1:])
    avg = np.full(centers.size, np.nan)
    std = np.full(centers.size, np.nan)
    for i in range(centers.size):
        m = (z_mm >= bins[i]) & (z_mm < bins[i+1])
        if m.any():
            avg[i] = v[m].mean()
            std[i] = v[m].std()
    return centers, avg, std


def bin_theta_average(theta_deg: np.ndarray, v: np.ndarray, dth_deg: float = 15.0
                      ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    bins = np.arange(-180.0, 180.0 + dth_deg, dth_deg)
    centers = 0.5 * (bins[:-1] + bins[1:])
    avg = np.full(centers.size, np.nan)
    std = np.full(centers.size, np.nan)
    for i in range(centers.size):
        m = (theta_deg >= bins[i]) & (theta_deg < bins[i+1])
        if m.any():
            avg[i] = v[m].mean()
            std[i] = v[m].std()
    return centers, avg, std


def analyze_case(case_name: str) -> dict:
    case_dir = CASES_DIR / case_name / "fluid"
    U = parse_vector_field((case_dir / "1" / "U").read_text())
    cx, cy, cz = get_fluid_cell_centres(case_name)
    if not (U.shape[0] == cx.size == cy.size == cz.size):
        raise RuntimeError(f"{case_name}: tamanhos U vs Cxyz inconsistentes")

    Umag = np.linalg.norm(U, axis=1)
    Ur, Ut, Uz = cylindrical_decompose(U, cx, cy)

    # estatisticas globais
    Umag_max = float(Umag.max())
    Umag_avg = float(Umag.mean())
    Umag_p95 = float(np.percentile(Umag, 95))
    Umag_p99 = float(np.percentile(Umag, 99))

    imax = int(Umag.argmax())
    r_max = math.hypot(cx[imax], cy[imax])
    th_max = math.degrees(math.atan2(cy[imax], cx[imax]))

    # decomposicao: variancias relativas
    sig_r  = float(Ur.std())
    sig_th = float(Ut.std())
    sig_z  = float(Uz.std())
    mu_r   = float(Ur.mean())
    mu_th  = float(Ut.mean())
    mu_z   = float(Uz.mean())

    # Reynolds local baseado em |U|_max e espessura do anel
    Re_max = Umag_max * L_CHAR_M / NU_LCR
    Re_avg = Umag_avg * L_CHAR_M / NU_LCR

    # escala de Stokes: U esperado por viscosidade vs pressao do inlet
    # (Stokes 1D: dP/dx = mu * d2u/dy2; U_scale = P * L / mu para um conduto
    # de tamanho L sob gradiente P. Aqui nao ha gradiente real, mas serve como
    # referencia da MAXIMA U que aparece se houvesse Pa/mm em alguma direcao.)
    U_stokes_scale = P_INLET[case_name] * L_CHAR_M / MU_LCR  # ~ m/s
    ratio_U_over_Stokes = Umag_max / U_stokes_scale

    # quebra axial: <Uz>(z) -- procura padrao coerente fonte-sumidouro
    z_centers, Uz_avg, Uz_std = bin_axis_average(cz, Uz, dz_mm=1.0)
    z_centers_um, Umag_avg_z, Umag_std_z = bin_axis_average(cz, Umag, dz_mm=1.0)

    # quebra azimutal na slice da contact_local: <Ut>(theta) -- circulacao
    mask_contact_slice = np.abs(cz - Z_CONTACT_M) < 0.0015
    theta_all_deg = np.degrees(np.arctan2(cy, cx))
    th_centers, Ut_avg_th, Ut_std_th = bin_theta_average(
        theta_all_deg[mask_contact_slice], Ut[mask_contact_slice], dth_deg=15.0)
    _,           Ur_avg_th, Ur_std_th = bin_theta_average(
        theta_all_deg[mask_contact_slice], Ur[mask_contact_slice], dth_deg=15.0)

    # ratio sinal/ruido axial: amplitude de <Uz>(z) vs sigma_z global
    Uz_signal = float(np.nanmax(Uz_avg) - np.nanmin(Uz_avg))
    snr_axial = Uz_signal / sig_z if sig_z > 0 else float("inf")

    # ratio sinal/ruido azimutal (na slice da contact_local)
    if np.isfinite(Ut_avg_th).any():
        Ut_signal = float(np.nanmax(Ut_avg_th) - np.nanmin(Ut_avg_th))
        sig_th_slice = float(Ut[mask_contact_slice].std()) if mask_contact_slice.any() else sig_th
        snr_azimuthal = Ut_signal / sig_th_slice if sig_th_slice > 0 else float("inf")
    else:
        Ut_signal = float("nan"); snr_azimuthal = float("nan")

    return {
        "case": case_name,
        "n_cells": int(cx.size),
        "Umag_max": Umag_max, "Umag_avg": Umag_avg,
        "Umag_p95": Umag_p95, "Umag_p99": Umag_p99,
        "imax": imax,
        "max_loc_xyz_mm":   (cx[imax]*1e3, cy[imax]*1e3, cz[imax]*1e3),
        "max_loc_rthz":     (r_max*1e3, th_max, cz[imax]*1e3),
        "mu_r": mu_r, "mu_th": mu_th, "mu_z": mu_z,
        "sig_r": sig_r, "sig_th": sig_th, "sig_z": sig_z,
        "Re_max": Re_max, "Re_avg": Re_avg,
        "U_stokes_scale": U_stokes_scale,
        "ratio_U_over_Stokes": ratio_U_over_Stokes,
        "Uz_signal_axial": Uz_signal,
        "snr_axial": snr_axial,
        "Ut_signal_azimuthal": Ut_signal,
        "snr_azimuthal": snr_azimuthal,
        "_axis": (z_centers, Uz_avg, Uz_std, Umag_avg_z),
        "_theta": (th_centers, Ut_avg_th, Ut_std_th, Ur_avg_th),
        "_arrays": {"Umag": Umag, "Ur": Ur, "Ut": Ut, "Uz": Uz,
                    "cx": cx, "cy": cy, "cz": cz},
    }


def diagnose(res: dict) -> str:
    # criterios de veredito:
    #   Stokes classico: Re < 1   (inercia desprezivel vs viscosa)
    #   |U|/U_Stokes_scale << 1e-3 : forcing real desprezivel (so' ruido)
    #   SNR < 3 nos padroes coerentes : nao ha estrutura significativa
    crit_Re      = res["Re_max"] < 1.0
    crit_negligible = res["ratio_U_over_Stokes"] < 1e-3
    crit_noise   = res["snr_axial"] < 3 and res["snr_azimuthal"] < 3

    if crit_Re and crit_negligible and crit_noise:
        return ("EQUILIBRIO ESTATICO (|U| e' ruido numerico, "
                f"Re_max={res['Re_max']:.2f}<1, |U|/U_Stokes={res['ratio_U_over_Stokes']:.1e})")
    if crit_Re and crit_negligible:
        if res["snr_axial"] >= 3:
            return (f"FUGA AXIAL (SNR axial={res['snr_axial']:.2f}>3, "
                    f"mas |U|/U_Stokes={res['ratio_U_over_Stokes']:.1e} ainda desprezivel)")
        return (f"CIRCULACAO AZIMUTAL (SNR azim={res['snr_azimuthal']:.2f}>3, "
                f"mas |U|/U_Stokes={res['ratio_U_over_Stokes']:.1e} ainda desprezivel)")
    if not crit_Re:
        return f"REGIME COM INERCIA (Re_max={res['Re_max']:.2f}>=1)"
    return "PARCIALMENTE COMPARTMENTALIZADO"


def print_report(res: dict):
    print(f"\n{'='*72}\n  TESTE B - {res['case']}\n{'='*72}")
    print(f"  cells no fluido         : {res['n_cells']}")
    print(f"  --- magnitude |U|")
    print(f"  |U|_max   (m/s)         : {res['Umag_max']:.3e}")
    print(f"  |U|_p99   (m/s)         : {res['Umag_p99']:.3e}")
    print(f"  |U|_p95   (m/s)         : {res['Umag_p95']:.3e}")
    print(f"  |U|_avg   (m/s)         : {res['Umag_avg']:.3e}")
    print(f"  loc |U|_max (x,y,z) mm  : {tuple(round(v,3) for v in res['max_loc_xyz_mm'])}")
    print(f"  loc |U|_max (r,th,z)    : "
          f"({res['max_loc_rthz'][0]:.3f} mm, {res['max_loc_rthz'][1]:+.1f} deg, "
          f"{res['max_loc_rthz'][2]:.2f} mm)")
    print(f"  --- decomposicao cilindrica (media +- sigma, todas as cells)")
    print(f"  U_r     : {res['mu_r']:+.2e} +- {res['sig_r']:.2e} m/s")
    print(f"  U_theta : {res['mu_th']:+.2e} +- {res['sig_th']:.2e} m/s")
    print(f"  U_z     : {res['mu_z']:+.2e} +- {res['sig_z']:.2e} m/s")
    print(f"  --- escalas adimensionais")
    print(f"  Re_max = |U|max*L/nu    : {res['Re_max']:.3e}  (L=0.8mm, nu=1e-6)")
    print(f"  Re_avg = |U|avg*L/nu    : {res['Re_avg']:.3e}")
    print(f"  U_Stokes(P_inlet*L/mu)  : {res['U_stokes_scale']:.3e} m/s")
    print(f"  |U|max / U_Stokes       : {res['ratio_U_over_Stokes']:.3e}")
    print(f"  --- coerencia de padrao")
    print(f"  amp <Uz>(z)             : {res['Uz_signal_axial']:.3e} m/s "
          f"(SNR axial = {res['snr_axial']:.2f})")
    print(f"  amp <Ut>(theta)@slice   : {res['Ut_signal_azimuthal']:.3e} m/s "
          f"(SNR azim  = {res['snr_azimuthal']:.2f})")
    print(f"  >>> VEREDITO: {diagnose(res)}")


def plot_combined(results: list[dict], outpath: Path):
    n = len(results)
    fig, axes = plt.subplots(n, 3, figsize=(14, 4.0*n), squeeze=False)
    for irow, res in enumerate(results):
        a = res["_arrays"]
        zc, Uz_avg, Uz_std, Umag_avg_z = res["_axis"]
        thc, Ut_avg, Ut_std, Ur_avg = res["_theta"]

        # (a) histograma de |U| (log y para enfatizar cauda)
        ax = axes[irow, 0]
        ax.hist(a["Umag"], bins=80, color="#27ae60", edgecolor="white")
        ax.axvline(res["Umag_max"], color="red", ls="--", lw=1.0,
                   label=f"|U|_max={res['Umag_max']:.2e}")
        ax.axvline(res["Umag_avg"], color="black", ls=":", lw=1.0,
                   label=f"|U|_avg={res['Umag_avg']:.2e}")
        ax.set_xlabel("|U| [m/s]"); ax.set_ylabel("# cells (log)")
        ax.set_yscale("log")
        ax.set_title(f"{res['case']} - histograma |U|\n"
                     f"Re_max={res['Re_max']:.2e}  veredito: {diagnose(res).split(' (')[0]}")
        ax.legend(fontsize=8)

        # (b) padrao axial: <Uz>(z) e |U|_avg(z)
        ax = axes[irow, 1]
        ax.plot(zc, Uz_avg, marker="o", color="#2980b9", label="<Uz>(z)")
        ax.fill_between(zc, Uz_avg - Uz_std, Uz_avg + Uz_std,
                        alpha=0.2, color="#2980b9", label="+-1 sigma")
        ax.axhline(0, color="grey", lw=0.5)
        ax.axvline(0,                 color="green", ls=":", lw=1.0, label="inlet (z=0)")
        ax.axvline(Z_CONTACT_M*1e3,   color="red",   ls="--", lw=1.0,
                   label=f"contact (z={Z_CONTACT_M*1e3:.1f})")
        ax.axvline(30,                color="purple",ls=":", lw=1.0, label="cul-de-sac (z=30)")
        ax.set_xlabel("z [mm]"); ax.set_ylabel("Uz [m/s]")
        ax.set_title(f"{res['case']} - padrao axial <Uz>(z)\n"
                     f"SNR axial = {res['snr_axial']:.2f}")
        ax.legend(fontsize=7, loc="best")

        # (c) padrao azimutal: <Ut>(theta) e <Ur>(theta) na slice contact_local
        ax = axes[irow, 2]
        ax.plot(thc, Ut_avg, marker="o", color="#c0392b",
                label=f"<U_theta>(theta)  SNR={res['snr_azimuthal']:.2f}")
        ax.fill_between(thc, Ut_avg - Ut_std, Ut_avg + Ut_std,
                        alpha=0.2, color="#c0392b")
        ax.plot(thc, Ur_avg, marker="s", color="#16a085", label="<U_r>(theta)")
        ax.axvline(0, color="red", ls="--", lw=1.0,
                   label="theta=0 (lado +x, contact_local)")
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_xlabel("theta [deg]"); ax.set_ylabel("U [m/s]")
        ax.set_title(f"{res['case']} - slice z={Z_CONTACT_M*1e3:.1f}+-1.5 mm")
        ax.legend(fontsize=7, loc="best")

    fig.suptitle("Teste B - Velocidade residual no LCR (FSI)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"\n  figura: {outpath}")


def main():
    cases = ["on-fsi-2", "on-fsi-3"]
    results = [analyze_case(c) for c in cases]
    for r in results:
        print_report(r)

    csv_path = OUT_DIR / "diag_testB_fluid_U_residual.csv"
    with open(csv_path, "w") as f:
        f.write("case,n_cells,Umag_max,Umag_p99,Umag_p95,Umag_avg,"
                "Re_max,Re_avg,U_Stokes_scale,ratio_U_Stokes,"
                "mu_r,sig_r,mu_th,sig_th,mu_z,sig_z,"
                "amp_axial_Uz,snr_axial,amp_azim_Ut,snr_azim,verdict\n")
        for r in results:
            f.write(
                f"{r['case']},{r['n_cells']},"
                f"{r['Umag_max']:.6e},{r['Umag_p99']:.6e},"
                f"{r['Umag_p95']:.6e},{r['Umag_avg']:.6e},"
                f"{r['Re_max']:.6e},{r['Re_avg']:.6e},"
                f"{r['U_stokes_scale']:.6e},{r['ratio_U_over_Stokes']:.6e},"
                f"{r['mu_r']:+.6e},{r['sig_r']:.6e},"
                f"{r['mu_th']:+.6e},{r['sig_th']:.6e},"
                f"{r['mu_z']:+.6e},{r['sig_z']:.6e},"
                f"{r['Uz_signal_axial']:.6e},{r['snr_axial']:.4f},"
                f"{r['Ut_signal_azimuthal']:.6e},{r['snr_azimuthal']:.4f},"
                f"\"{diagnose(r)}\"\n")
    print(f"\n  CSV: {csv_path}")

    plot_combined(results, OUT_DIR / "diag_testB_fluid_U_residual.png")


if __name__ == "__main__":
    main()
