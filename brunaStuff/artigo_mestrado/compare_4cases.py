"""Compara 4 casos: on-mestrado-2, on-mestrado-3, on-fsi-2, on-fsi-3.

  on-mestrado-2 : SAS solido, P_CSF=1333 Pa (1g normotenso)
  on-mestrado-3 : SAS solido, P_CSF=2667 Pa (microgravidade SANS)
  on-fsi-2      : SAS fluido, P_CSF=1333 Pa (1g normotenso)
  on-fsi-3      : SAS fluido, P_CSF=2667 Pa (microgravidade SANS)

Hipotese: como o problema e linear elastico, dobrar P_CSF deveria aumentar
linearmente a contribuicao de P_CSF no campo de deslocamento. Mas
contact_local (9034 Pa) NAO mudou, entao o |D| total nao dobra exatamente.
A componente AXIAL (Dz) na tampa peripapilar deveria escalar quase
exatamente com P_CSF.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

CONTAINER = "om2-resume"


def _docker_cat(path: str) -> str:
    return subprocess.check_output(
        ["docker", "exec", CONTAINER, "bash", "-lc", f"cat {path}"],
        stderr=subprocess.STDOUT,
    ).decode("utf-8", errors="replace")


def parse_volVectorField(text: str):
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
    m = re.search(r"internalField\s+nonuniform\s+List<symmTensor>\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        raise RuntimeError("nao achei internalField symmTensor")
    out = []
    for line in m.group(2).split("\n"):
        line = line.strip()
        if not line:
            continue
        ms = re.match(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*\)", line)
        if ms:
            out.append(tuple(float(g) for g in ms.groups()))
    return out


def parse_volScalarField(text: str):
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        m = re.search(r"internalField\s+uniform\s+(\S+)\s*;", text)
        if not m:
            raise RuntimeError("nao achei internalField scalar")
        return [float(m.group(1))]
    return [float(s.strip()) for s in m.group(2).split("\n") if s.strip()]


# --------------------- cell-zone slicings -----------------------
ZONES_OM = {
    "on":          (0, 7680),
    "pia":         (7680, 8640),
    "sas":         (8640, 14400),
    "dura":        (14400, 16320),
    "lc":          (16320, 16576),
    "sclera_peri": (16576, 16704),
    "sclera_ring": (16704, 16864),
    "globo":       (16864, 17408),
}

ZONES_FSI = {
    "on":          (0, 7680),
    "pia":         (7680, 8640),
    "dura":        (8640, 10560),
    "lc":          (10560, 10816),
    "sclera_peri": (10816, 10944),
    "sclera_ring": (10944, 11104),
    "globo":       (11104, 11648),
}


def load_case(name: str, fsi: bool):
    base = f"/simulation/{name}"
    D = parse_volVectorField(_docker_cat(f"{base}/solid/1/D"))
    S = parse_volSymmTensorField(_docker_cat(f"{base}/solid/1/sigma"))
    p = None
    if fsi:
        p = parse_volScalarField(_docker_cat(f"{base}/fluid/1/p"))
    return D, S, p


def stats_per_zone(D, S, zones):
    out = {}
    for z, (a, b) in zones.items():
        sub_D = D[a:b]
        sub_S = S[a:b]
        if not sub_D:
            continue
        d_mag_max = max((d[0]**2 + d[1]**2 + d[2]**2)**0.5 for d in sub_D)
        Dz_max = max(abs(d[2]) for d in sub_D)
        seq_max = 0.0
        for s in sub_S:
            xx, xy, xz, yy, yz, zz = s
            d1, d2, d3 = xx-yy, yy-zz, zz-xx
            mises = (0.5*(d1*d1+d2*d2+d3*d3) + 3*(xy*xy+yz*yz+xz*xz))**0.5
            if mises > seq_max:
                seq_max = mises
        out[z] = {
            "Dmax_um": d_mag_max * 1e6,
            "Dz_max_um": Dz_max * 1e6,
            "seq_max_Pa": seq_max,
        }
    return out


def main():
    print("Carregando 4 casos...")
    D_om2, S_om2, _ = load_case("on-mestrado-2", fsi=False)
    D_om3, S_om3, _ = load_case("on-mestrado-3", fsi=False)
    D_f2, S_f2, p_f2 = load_case("on-fsi-2", fsi=True)
    D_f3, S_f3, p_f3 = load_case("on-fsi-3", fsi=True)

    s_om2 = stats_per_zone(D_om2, S_om2, ZONES_OM)
    s_om3 = stats_per_zone(D_om3, S_om3, ZONES_OM)
    s_f2  = stats_per_zone(D_f2,  S_f2,  ZONES_FSI)
    s_f3  = stats_per_zone(D_f3,  S_f3,  ZONES_FSI)

    # --- pressao no fluido (sanity) ---
    print("\n===== PRESSAO MEDIA DO FLUIDO (LCR) =====")
    print(f"  on-fsi-2: p_avg = {sum(p_f2)/len(p_f2)*1000:7.1f} Pa  (esperado 1333)")
    print(f"  on-fsi-3: p_avg = {sum(p_f3)/len(p_f3)*1000:7.1f} Pa  (esperado 2667)")

    # --- |D|max por zona ---
    print("\n===== |D| MAX POR ZONA (em micrometros) =====")
    print(f"{'zone':<14} {'om-2':>9} {'om-3':>9} {'om3/om2':>8}  "
          f"{'fsi-2':>9} {'fsi-3':>9} {'fsi3/fsi2':>10}")
    for z in ZONES_FSI:  # nao inclui sas (so existe em om)
        a = s_om2[z]["Dmax_um"]; b = s_om3[z]["Dmax_um"]
        c = s_f2[z]["Dmax_um"];  d = s_f3[z]["Dmax_um"]
        ra = b/a if a>1e-9 else float("nan")
        rb = d/c if c>1e-9 else float("nan")
        print(f"{z:<14} {a:9.3f} {b:9.3f} {ra:8.3f}  "
              f"{c:9.3f} {d:9.3f} {rb:10.3f}")

    # --- Dz max (axial) por zona ---
    print("\n===== |Dz| MAX POR ZONA (axial, em um) - escalar diretamente com P_CSF =====")
    print(f"{'zone':<14} {'om-2':>9} {'om-3':>9} {'om3/om2':>8}  "
          f"{'fsi-2':>9} {'fsi-3':>9} {'fsi3/fsi2':>10}")
    for z in ZONES_FSI:
        a = s_om2[z]["Dz_max_um"]; b = s_om3[z]["Dz_max_um"]
        c = s_f2[z]["Dz_max_um"];  d = s_f3[z]["Dz_max_um"]
        ra = b/a if a>1e-9 else float("nan")
        rb = d/c if c>1e-9 else float("nan")
        print(f"{z:<14} {a:9.3f} {b:9.3f} {ra:8.3f}  "
              f"{c:9.3f} {d:9.3f} {rb:10.3f}")

    # --- sigmaEq max por zona ---
    print("\n===== sigmaEq MAX (von Mises, em Pa) =====")
    print(f"{'zone':<14} {'om-2':>10} {'om-3':>10} {'om3/om2':>8}  "
          f"{'fsi-2':>10} {'fsi-3':>10} {'fsi3/fsi2':>10}")
    for z in ZONES_FSI:
        a = s_om2[z]["seq_max_Pa"]; b = s_om3[z]["seq_max_Pa"]
        c = s_f2[z]["seq_max_Pa"];  d = s_f3[z]["seq_max_Pa"]
        ra = b/a if a>1e-3 else float("nan")
        rb = d/c if c>1e-3 else float("nan")
        print(f"{z:<14} {a:10.2f} {b:10.2f} {ra:8.3f}  "
              f"{c:10.2f} {d:10.2f} {rb:10.3f}")

    # --- watchpoint FSI ---
    print("\n===== WATCHPOINT TAMPA PERIPAPILAR (FSI; (1.91, -0.19, 30) mm) =====")
    for case in ("on-fsi-2", "on-fsi-3"):
        try:
            wp = _docker_cat(f"/simulation/{case}/solid/precice-Solid-watchpoint-tampaPeripapilar.log")
            lines = [l for l in wp.split("\n") if l.strip() and not l.startswith("  Time")]
            if lines:
                last = lines[-1].split()
                print(f"  {case}: D=({float(last[4])*1e6:7.3f}, "
                      f"{float(last[5])*1e6:7.3f}, {float(last[6])*1e6:7.3f}) um  "
                      f"F_z={float(last[9])*1e6:8.2f} uN")
        except Exception as e:
            print(f"  {case}: WARN {e}")


if __name__ == "__main__":
    main()
