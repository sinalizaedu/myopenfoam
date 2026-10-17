#!/usr/bin/env python3
"""
Compressible thin-shell (plane-stress) equibiaxial inflation model, extending
thin_shell_analysis.py to include the ACTUAL bulk compliance D1 used by each
material deck (from ccx_utils.bulk_compliance_mpa):

    Ogden N=1  ->  D1 = 1.0e-6 1/MPa   (k = 2/D1 ~ 2.0e6 MPa, CCX-Ogden-stability
                                          workaround -> numerically near-locked)
    Yeoh-2     ->  D1 = d1_from_nu_mpa(nu=0.47, E=3.0) = 0.12 1/MPa
                                          (k = E/(3(1-2*0.47)) = 16.7 MPa)

This is a ~140,000x difference in assumed bulk modulus between the two decks.
It is NOT a property of "Ogden the material" vs "Yeoh the material" -- it is a
documented numerical workaround (comment in ccx_utils.py: "CalculiX Ogden is
unstable with the Yeoh-style D1 (~0.1); it expects near-zero D1") -- but it has
a physical side-effect: Ogden's deck is solved essentially incompressible,
while Yeoh's deck allows real volumetric strain with bulk modulus only ~2x its
own shear-type modulus (k/mu ~ 16.7/8.7 ~ 1.9). Under internal pressure with a
free (zero-traction) inner/outer shell surface, that volumetric compliance
feeds directly into the thickness change and hence into the membrane P-V
response. This script tests whether that alone, holding the deviatoric law
otherwise as fitted, reproduces the sign/magnitude split the FEA shows.

Method: principal-stretch hyperelasticity, sigma_i = (lambda_i/J) dW/dlambda_i
(exact, general form -- no incompressibility constraint assumed). Plane-stress
condition sigma_3 = 0 (free through-thickness surface) is solved for lambda_3
at each equatorial stretch lambda = lambda_1 = lambda_2.
"""
from __future__ import annotations
import numpy as np
import json
from pathlib import Path
from scipy.optimize import brentq

OUT = Path(__file__).resolve().parent

MU1, ALPHA1 = 7.1586, 0.5000000711
C10, C20 = 4.3639, 4.9950
D1_OGDEN = 1.0e-6
D1_YEOH = 2.0 / (3.0 / (3.0 * (1.0 - 2.0 * 0.47)))   # d1_from_nu_mpa(0.47, 3.0) = 0.12

R0_MM, T0_MM = 12.0, 0.5
P0_MMHG = 16.9
V_REF_UL = 10.0
MMHG_TO_MPA = 1.333223684e-4


def W_ogden(l1, l2, l3, mu1=MU1, alpha1=ALPHA1, D1=D1_OGDEN):
    J = l1 * l2 * l3
    Jm13 = J ** (-1.0 / 3.0)
    lb1, lb2, lb3 = Jm13 * l1, Jm13 * l2, Jm13 * l3
    Wdev = (2 * mu1 / alpha1 ** 2) * (lb1 ** alpha1 + lb2 ** alpha1 + lb3 ** alpha1 - 3)
    Wvol = (1.0 / D1) * (J - 1) ** 2
    return Wdev + Wvol


def W_yeoh(l1, l2, l3, c10=C10, c20=C20, D1=D1_YEOH):
    J = l1 * l2 * l3
    Jm23 = J ** (-2.0 / 3.0)
    I1b = Jm23 * (l1 ** 2 + l2 ** 2 + l3 ** 2)
    Wdev = c10 * (I1b - 3) + c20 * (I1b - 3) ** 2
    Wvol = (1.0 / D1) * (J - 1) ** 2
    return Wdev + Wvol


def principal_cauchy(W_fn, l1, l2, l3, h=1e-7):
    J = l1 * l2 * l3
    dWdl1 = (W_fn(l1 + h, l2, l3) - W_fn(l1 - h, l2, l3)) / (2 * h)
    dWdl2 = (W_fn(l1, l2 + h, l3) - W_fn(l1, l2 - h, l3)) / (2 * h)
    dWdl3 = (W_fn(l1, l2, l3 + h) - W_fn(l1, l2, l3 - h)) / (2 * h)
    return (l1 / J) * dWdl1, (l2 / J) * dWdl2, (l3 / J) * dWdl3


def solve_lambda3(W_fn, lam_eq, lo=0.2, hi=3.0):
    f = lambda l3: principal_cauchy(W_fn, lam_eq, lam_eq, l3)[2]
    return brentq(f, lo, hi, xtol=1e-13)


def make_model(W_fn):
    def sigma_eq(lam):
        l3 = solve_lambda3(W_fn, lam)
        s1, s2, s3 = principal_cauchy(W_fn, lam, lam, l3)
        return s1, l3

    def t_of(lam):
        return T0_MM * solve_lambda3(W_fn, lam)

    def R_of(lam):
        return R0_MM * lam

    def P_of(lam):
        s, _ = sigma_eq(lam)
        return 2 * t_of(lam) * s / R_of(lam)

    def V_of(lam):
        return (4.0 / 3.0) * np.pi * R_of(lam) ** 3

    def d_dlam(f, lam, h=1e-6):
        return (f(lam + h) - f(lam - h)) / (2 * h)

    def K_of(lam):
        return d_dlam(P_of, lam) / d_dlam(V_of, lam)

    return dict(sigma_eq=sigma_eq, t=t_of, R=R_of, P=P_of, V=V_of, K=K_of)


ogden = make_model(W_ogden)
yeoh = make_model(W_yeoh)


def find_lambda_for_pressure(model, p_mpa, lo=1.0 + 1e-9, hi=1.1):
    f = lambda l: model['P'](l) - p_mpa
    return brentq(f, lo, hi, xtol=1e-14)


def find_lambda_for_dV(model, lam0, dV_target, hi=1.1):
    V0 = model['V'](lam0)
    f = lambda l: model['V'](l) - V0 - dV_target
    return brentq(f, lam0, hi, xtol=1e-14)


results = {}
curves = {}
for name, model in [('ogden', ogden), ('yeoh', yeoh)]:
    p0_mpa = P0_MMHG * MMHG_TO_MPA
    lam0 = find_lambda_for_pressure(model, p0_mpa)
    lam1 = find_lambda_for_dV(model, lam0, V_REF_UL)

    K0 = model['K'](lam0) / MMHG_TO_MPA
    K1 = model['K'](lam1) / MMHG_TO_MPA
    rel_pct = 100.0 * (K1 - K0) / K0
    _, l3_0 = model['sigma_eq'](lam0)
    _, l3_1 = model['sigma_eq'](lam1)
    J0 = lam0 * lam0 * l3_0
    J1 = lam1 * lam1 * l3_1

    results[name] = dict(
        lambda0=lam0, lambda1=lam1, lambda3_0=l3_0, lambda3_1=l3_1,
        J0=J0, J1=J1,
        V0_mm3=model['V'](lam0), V1_mm3=model['V'](lam1),
        P0_check_mmHg=model['P'](lam0) / MMHG_TO_MPA,
        K0_mmHg_per_uL=K0, K1_mmHg_per_uL=K1,
        rel_change_pct=rel_pct,
    )
    print(f"\n=== {name.upper()} (compressible, D1={'1e-6' if name=='ogden' else '0.12'}) ===")
    print(f"  lambda0={lam0:.6f}  lambda3_0={l3_0:.6f}  J0={J0:.6f}")
    print(f"  lambda1={lam1:.6f}  lambda3_1={l3_1:.6f}  J1={J1:.6f}")
    print(f"  K@V=0={K0:.5f}  K@Vref={K1:.5f}  rel change={rel_pct:+.2f}%   (FEA: {'+1.3%' if name=='ogden' else '-37.5%'})")

    # dense curve for plotting
    lam_max = find_lambda_for_pressure(model, 80.0 * MMHG_TO_MPA)
    lams = np.linspace(1.0001, lam_max, 60)
    Ps, Vs, Ks, l3s = [], [], [], []
    for l in lams:
        Ps.append(model['P'](l) / MMHG_TO_MPA)
        Vs.append(model['V'](l))
        Ks.append(model['K'](l) / MMHG_TO_MPA)
        _, l3v = model['sigma_eq'](l)
        l3s.append(l3v)
    curves[name] = dict(lam=lams.tolist(), P_mmHg=Ps, V_mm3=Vs, K_mmHg_per_uL=Ks, lam3=l3s)

(OUT / "thin_shell_compressible_results.json").write_text(json.dumps(results, indent=2))
(OUT / "thin_shell_compressible_curves.json").write_text(json.dumps(curves, indent=2))
print("\nSaved results + curves.")
