"""Compara on-mestrado-2 (SAS solido) vs on-fsi-2 (SAS = LCR fluido).

Para cada zona solida em comum, reporta:
  - |D| max (deslocamento maximo, em micrometros)
  - sigmaEq max (von Mises, em Pa)
  - sigma_xx medio (proxy de sigma_radial ao longo do eixo +X)
  - sigma_zz medio (proxy de sigma axial)

Tambem extrai do fluid (apenas on-fsi-2):
  - p_kinematic medio (deve ser ~1.333 m^2/s^2 = 1333 Pa para LCR rho=1000)

Hipotese a verificar:
  No SAS solido (om2): pressao isotropica do LCR e' SUBSTITUIDA por um
  solido elastico mole (E=100kPa, nu=0.30) que transmite stress por
  Poisson ratio. A pressao radial nas paredes da pia/dura e' so da ordem
  de p_axial * nu/(1-nu) ~ 1333 * 0.43 = 571 Pa (subestimacao).
  
  No SAS fluido (fsi-2): a pressao do LCR e' isotropica, todas as paredes
  do cul-de-sac (pia outer, dura inner, tampa peripapilar) recebem 1333 Pa
  por igual.
  
  Esperado: sigma_radial(pia,fsi2) / sigma_radial(pia,om2) ~ 2.33
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

CONTAINER = "om2-resume"

# cellZones (start, end) por caso. Derivadas das blockMeshDict-em-ordem-de-bloco
# (cells contiguas dentro de cada zona, mesmo zona repete em multiplos blocos).
ZONES_OM2 = {
    "on":          (0,     7680),
    "pia":         (7680,  8640),
    "sas":         (8640,  14400),
    "dura":        (14400, 16320),
    "lc":          (16320, 16576),
    "sclera_peri": (16576, 16704),
    "sclera_ring": (16704, 16864),
    "globo":       (16864, 17408),
}

ZONES_FSI2 = {
    "on":          (0,     7680),
    "pia":         (7680,  8640),
    "dura":        (8640,  10560),
    "lc":          (10560, 10816),
    "sclera_peri": (10816, 10944),
    "sclera_ring": (10944, 11104),
    "globo":       (11104, 11648),
}


def _docker_cat(path: str) -> str:
    return subprocess.check_output(
        ["docker", "exec", CONTAINER, "bash", "-lc", f"cat {path}"],
        stderr=subprocess.STDOUT,
    ).decode("utf-8", errors="replace")


def parse_volVectorField(text: str) -> list[tuple[float, float, float]]:
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        m = re.search(r"internalField\s+uniform\s+\(([^)]+)\)", text)
        if not m:
            raise RuntimeError("nao achei internalField vector")
        x, y, z = (float(s) for s in m.group(1).split())
        return [(x, y, z)]
    out = []
    for line in m.group(2).split("\n"):
        line = line.strip()
        if not line:
            continue
        ms = re.match(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)", line)
        if ms:
            out.append((float(ms.group(1)), float(ms.group(2)), float(ms.group(3))))
    return out


def parse_volSymmTensorField(text: str):
    """Le sigma como (xx xy xz yy yz zz)."""
    m = re.search(r"internalField\s+nonuniform\s+List<symmTensor>\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        raise RuntimeError("nao achei internalField symmTensor em sigma")
    out = []
    for line in m.group(2).split("\n"):
        line = line.strip()
        if not line:
            continue
        ms = re.match(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*\)", line)
        if ms:
            out.append(tuple(float(g) for g in ms.groups()))
    return out


def parse_volScalarField(text: str) -> list[float]:
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        m = re.search(r"internalField\s+uniform\s+(\S+)\s*;", text)
        if not m:
            raise RuntimeError("nao achei internalField scalar")
        return [float(m.group(1))]
    return [float(s.strip()) for s in m.group(2).split("\n") if s.strip()]


def stats_per_zone(D, sigma, zones, label):
    print(f"\n===== {label} =====")
    print(f"{'zone':<14} {'cells':>6} {'|D|max(um)':>12} "
          f"{'sigmaEq(Pa)':>12} {'sigma_xx(Pa)':>14} {'sigma_yy(Pa)':>14} {'sigma_zz(Pa)':>14}")
    for zname, (a, b) in zones.items():
        if a >= len(D):
            continue
        sub_D = D[a:b]
        sub_S = sigma[a:b]
        if not sub_D:
            continue
        # |D| max
        d_mag = [(d[0]**2 + d[1]**2 + d[2]**2)**0.5 for d in sub_D]
        d_max = max(d_mag) * 1e6
        # sigmaEq max (von Mises) por celula
        seq = []
        sxx_avg = 0.0; syy_avg = 0.0; szz_avg = 0.0
        for s in sub_S:
            xx, xy, xz, yy, yz, zz = s
            sxx_avg += xx; syy_avg += yy; szz_avg += zz
            d1 = xx - yy; d2 = yy - zz; d3 = zz - xx
            mises = (0.5*(d1*d1 + d2*d2 + d3*d3) + 3*(xy*xy + yz*yz + xz*xz))**0.5
            seq.append(mises)
        n = len(sub_S)
        print(f"{zname:<14} {b-a:6d} {d_max:12.3f} {max(seq):12.2f} "
              f"{sxx_avg/n:14.2f} {syy_avg/n:14.2f} {szz_avg/n:14.2f}")


def stress_at_axis_pX(D, sigma, zones, zname, axis_tol=2e-4):
    """Media de sigma_xx,sigma_yy,sigma_zz nas cells da zona ao longo do eixo +X
    (y ~ 0). Como nao temos cellCentres aqui, reportamos apenas a media de toda
    a zona como proxy de sigma_radial (acima de symetria circunferencial)."""
    a, b = zones[zname]
    sub_S = sigma[a:b]
    if not sub_S:
        return None
    n = len(sub_S)
    xx = sum(s[0] for s in sub_S) / n
    yy = sum(s[3] for s in sub_S) / n
    zz = sum(s[5] for s in sub_S) / n
    return xx, yy, zz


def main():
    print("=== Lendo on-mestrado-2/solid/1 ===")
    D_om2 = parse_volVectorField(_docker_cat("/simulation/on-mestrado-2/solid/1/D"))
    S_om2 = parse_volSymmTensorField(_docker_cat("/simulation/on-mestrado-2/solid/1/sigma"))
    print(f"  cells D = {len(D_om2)}, sigma = {len(S_om2)}")

    print("\n=== Lendo on-fsi-2/solid/1 ===")
    D_fsi = parse_volVectorField(_docker_cat("/simulation/on-fsi-2/solid/1/D"))
    S_fsi = parse_volSymmTensorField(_docker_cat("/simulation/on-fsi-2/solid/1/sigma"))
    print(f"  cells D = {len(D_fsi)}, sigma = {len(S_fsi)}")

    stats_per_zone(D_om2, S_om2, ZONES_OM2, "on-mestrado-2 (SAS solido)")
    stats_per_zone(D_fsi, S_fsi, ZONES_FSI2, "on-fsi-2 (SAS fluido)")

    # ----- comparacao quantitativa: pressao isotropica vs Poisson -----
    print("\n===== COMPARACAO QUANTITATIVA: SIGMA RADIAL =====")
    print("Hipotese: sigma_radial(fsi2) / sigma_radial(om2) ~ 2.33 na pia/dura")
    print("        (om2: pressao isotropica reduzida por nu/(1-nu) ~0.43)")
    print(f"{'zone':<14} {'om2 sxx':>10} {'fsi sxx':>10} {'razao xx':>9} "
          f"{'om2 syy':>10} {'fsi syy':>10}  {'om2 szz':>10} {'fsi szz':>10}")
    for zname in ("pia", "dura", "sclera_peri", "sclera_ring"):
        om = stress_at_axis_pX(D_om2, S_om2, ZONES_OM2, zname)
        fs = stress_at_axis_pX(D_fsi, S_fsi, ZONES_FSI2, zname)
        if om is None or fs is None:
            continue
        ratio_xx = fs[0] / om[0] if abs(om[0]) > 1e-3 else float("nan")
        print(f"{zname:<14} {om[0]:10.2f} {fs[0]:10.2f} {ratio_xx:9.2f}  "
              f"{om[1]:10.2f} {fs[1]:10.2f}  {om[2]:10.2f} {fs[2]:10.2f}")

    # ----- pressao no fluido (fsi-2) ---------------------------------
    print("\n===== PRESSAO NO FLUIDO (on-fsi-2) =====")
    p = parse_volScalarField(_docker_cat("/simulation/on-fsi-2/fluid/1/p"))
    print(f"  cells = {len(p)}")
    print(f"  p_kinematic min  = {min(p):.4f} m^2/s^2  (esperado ~1.333)")
    print(f"  p_kinematic max  = {max(p):.4f} m^2/s^2")
    print(f"  p_kinematic mean = {sum(p)/len(p):.4f} m^2/s^2")
    print(f"  ==> Pressao real (rho=1000): {sum(p)/len(p)*1000:.1f} Pa  (esperado ~1333)")

    # ----- velocidade no fluido --------------------------------------
    U = parse_volVectorField(_docker_cat("/simulation/on-fsi-2/fluid/1/U"))
    Umag = [(u[0]**2 + u[1]**2 + u[2]**2)**0.5 for u in U]
    print(f"\n  |U| max = {max(Umag)*1000:.4f} mm/s  (esperado <1, fluido quase estatico)")
    print(f"  |U| avg = {sum(Umag)/len(Umag)*1000:.4f} mm/s")

    # ----- watchpoint preCICE ---------------------------------------
    print("\n===== WATCHPOINT (tampa peripapilar +X axis em z=30 mm) =====")
    wp = _docker_cat("/simulation/on-fsi-2/solid/precice-Solid-watchpoint-tampaPeripapilar.log")
    lines = [l for l in wp.split("\n") if l.strip() and not l.startswith("  Time")]
    if lines:
        last = lines[-1].split()
        print(f"  posicao: ({float(last[1])*1e3:.3f}, {float(last[2])*1e3:.3f}, {float(last[3])*1e3:.3f}) mm")
        print(f"  D = ({float(last[4])*1e6:.2f}, {float(last[5])*1e6:.2f}, {float(last[6])*1e6:.2f}) um")
        print(f"  Force = ({float(last[7])*1e3:.4f}, {float(last[8])*1e3:.4f}, {float(last[9])*1e3:.4f}) mN")

    # ----- preCICE iter count -----------------------------------------
    print("\n===== preCICE FSI ITERATIONS =====")
    it = _docker_cat("/simulation/on-fsi-2/solid/precice-Solid-iterations.log")
    print(it.strip())


if __name__ == "__main__":
    main()
