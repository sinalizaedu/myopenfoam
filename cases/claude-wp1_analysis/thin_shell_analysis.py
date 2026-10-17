#!/usr/bin/env python3
"""
Closed-form thin-shell equibiaxial inflation model for Ogden N=1 vs Yeoh-2,
using the WP1.2 fitted parameters, to explain analytically why the FEA shows
Ogden HARDENING (+1.3%) and Yeoh SOFTENING (-37.5%) in local dP/dV between
V=0 (post-prestress) and V=V_ref=10 uL.

Model: incompressible thin spherical membrane, isotropic equibiaxial stretch
lambda (lambda1 = lambda2 = lambda, lambda3 = lambda^-2 by incompressibility).
  R(lambda) = R0 * lambda        (radius grows with equatorial stretch)
  t(lambda) = t0 / lambda^2      (thickness shrinks, volume-preserving)
  sigma_eq(lambda) = equibiaxial Cauchy stress (material law)
  P(lambda) = 2 * t(lambda) * sigma_eq(lambda) / R(lambda)   (membrane equilibrium)
  V(lambda) = (4/3) pi R(lambda)^3

This isolates the MATERIAL contribution to K = dP/dV from geometric
thinning/growth, using exactly the fitted (mu1,alpha1) and (C10,C20).
Derivatives are computed by high-accuracy central finite differences
(no sympy available offline) -- more than adequate given the smoothness
of both strain-energy forms.
"""
from __future__ import annotations
import numpy as np
import json
from pathlib import Path
from scipy.optimize import brentq

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

# ---- fitted params (from WP1.2, Pallikaris target, octant ne=8) ----
MU1, ALPHA1 = 7.1586, 0.5000000711        # Ogden N=1 (D1 tied)
C10, C20 = 4.3639, 4.9950                  # Yeoh-2 (MPa)

R0_MM, T0_MM = 12.0, 0.5
P0_MMHG = 16.9
V_REF_UL = 10.0          # matches WP1.3 sweep default (10% of Vmax capped at 10uL)
MMHG_TO_MPA = 1.333223684e-4


def sigma_ogden(lam, mu1=MU1, alpha1=ALPHA1):
    return (2*mu1/alpha1) * (lam**alpha1 - lam**(-2*alpha1))


def sigma_yeoh(lam, c10=C10, c20=C20):
    I1 = 2*lam**2 + lam**-4
    dW_dI1 = c10 + 2*c20*(I1 - 3)
    return 2*(lam**2 - lam**-4) * dW_dI1


def make_model(sigma_fn):
    def R(lam):
        return R0_MM*lam

    def t(lam):
        return T0_MM/lam**2

    def P(lam):
        return 2*t(lam)*sigma_fn(lam)/R(lam)

    def V(lam):
        return (4.0/3.0)*np.pi*(R0_MM*lam)**3

    def d_dlam(f, lam, h=1e-7):
        return (f(lam+h) - f(lam-h))/(2*h)

    def K(lam):
        # dP/dV = (dP/dlam)/(dV/dlam)
        return d_dlam(P, lam)/d_dlam(V, lam)

    return dict(sigma=sigma_fn, P=P, V=V, K=K,
                dsigma=lambda l: d_dlam(sigma_fn, l))


ogden = make_model(sigma_ogden)
yeoh = make_model(sigma_yeoh)


def find_lambda_for_pressure(model, p_mpa, lo=1.0+1e-9, hi=3.0):
    f = lambda l: model['P'](l) - p_mpa
    return brentq(f, lo, hi, xtol=1e-14)


def find_lambda_for_dV(model, lam0, dV_target, hi=3.0):
    V0 = model['V'](lam0)
    f = lambda l: model['V'](l) - V0 - dV_target
    return brentq(f, lam0, hi, xtol=1e-14)


results = {}
for name, model in [('ogden', ogden), ('yeoh', yeoh)]:
    p0_mpa = P0_MMHG*MMHG_TO_MPA
    lam0 = find_lambda_for_pressure(model, p0_mpa)
    lam1 = find_lambda_for_dV(model, lam0, V_REF_UL)  # 1 uL = 1 mm^3

    K0 = model['K'](lam0)/MMHG_TO_MPA   # MPa/mm^3 -> mmHg/uL
    K1 = model['K'](lam1)/MMHG_TO_MPA
    rel_pct = 100.0*(K1-K0)/K0

    results[name] = dict(
        lambda0=lam0, lambda1=lam1,
        V0_mm3=model['V'](lam0), V1_mm3=model['V'](lam1),
        P0_check_mmHg=model['P'](lam0)/MMHG_TO_MPA,
        K0_mmHg_per_uL=K0, K1_mmHg_per_uL=K1,
        rel_change_pct=rel_pct,
        sigma0_MPa=model['sigma'](lam0), sigma1_MPa=model['sigma'](lam1),
        dsigma0=model['dsigma'](lam0), dsigma1=model['dsigma'](lam1),
    )
    print(f"\n=== {name.upper()} ===")
    print(f"  lambda0={lam0:.6f}  (P0 check = {model['P'](lam0)/MMHG_TO_MPA:.3f} mmHg)")
    print(f"  lambda1={lam1:.6f}  (dV={V_REF_UL} uL)")
    print(f"  K @ V=0    = {K0:.5f} mmHg/uL")
    print(f"  K @ V_ref  = {K1:.5f} mmHg/uL")
    print(f"  relative change = {rel_pct:+.2f}%   (FEA reference: {'+1.3%' if name=='ogden' else '-37.5%'})")

(OUT/"thin_shell_results.json").write_text(json.dumps(results, indent=2))
print("\nSaved:", OUT/"thin_shell_results.json")
