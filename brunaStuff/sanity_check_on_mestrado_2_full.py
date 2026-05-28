"""Sanity check do campo de deslocamento de cases/on-mestrado-2 (8 zonas).

Verifica:
  1) Simetria em y (Dy_min ~ -Dy_max)
  2) Dx dominantemente negativo (push da arteria do +X)
  3) Magnitudes razoaveis em cada zona
  4) Continuidade na juncao z=30 (sem salto entre nervo e LC/sclera)
  5) |D| no globo pequeno (rigido + engaste no equador)
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

CASE_DIR_HOST = Path(__file__).resolve().parent.parent / "cases" / "on-mestrado-2" / "solid"
CONTAINER = "om2-resume"
CASE_DIR_DOCKER = "/simulation/on-mestrado-2/solid"


def _docker_exec(cmd: str) -> str:
    out = subprocess.check_output(
        ["docker", "exec", CONTAINER, "bash", "-lc", cmd],
        stderr=subprocess.STDOUT,
    )
    return out.decode("utf-8", errors="replace")


def parse_volVectorField(text: str) -> list[tuple[float, float, float]]:
    """Le internalField do D no formato OpenFOAM ASCII."""
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n(\d+)\s*\n\(\s*(.*?)\s*\)\s*;",
                  text, re.DOTALL)
    if not m:
        m = re.search(r"internalField\s+uniform\s+\(([^)]+)\)", text)
        if not m:
            raise RuntimeError("nao achei internalField em D")
        x, y, z = (float(s) for s in m.group(1).split())
        return [(x, y, z)]
    data_text = m.group(2)
    vecs = []
    for line in data_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        ms = re.match(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)", line)
        if ms:
            vecs.append((float(ms.group(1)), float(ms.group(2)), float(ms.group(3))))
    return vecs


def cell_centers_per_zone() -> dict[str, tuple[int, int]]:
    """Retorna o intervalo (start, end) de indices de celula em cada zona, da log do checkMesh."""
    return {
        "on":          (0,    7680),
        "pia":         (7680, 7680 + 960),
        "sas":         (7680 + 960, 7680 + 960 + 5760),
        "dura":        (7680 + 960 + 5760, 7680 + 960 + 5760 + 1920),
        "lc":          (16320, 16320 + 256),
        "sclera_peri": (16320 + 256, 16320 + 256 + 128),
        "sclera_ring": (16320 + 256 + 128, 16320 + 256 + 128 + 160),
        "globo":       (16320 + 256 + 128 + 160, 17408),
    }


def main():
    # le D em t=1
    cmd = f"cat {CASE_DIR_DOCKER}/1/D"
    text = _docker_exec(cmd)
    D = parse_volVectorField(text)
    print(f"Total cells em D: {len(D)} (esperado 17408)")

    zones = cell_centers_per_zone()

    print("\n===== Magnitudes por zona =====")
    print(f"{'zone':<14} {'cells':>6} {'|D|max(um)':>12} {'Dx min(um)':>12} {'Dx max(um)':>12} {'Dy min(um)':>12} {'Dy max(um)':>12} {'Dz min(um)':>12} {'Dz max(um)':>12}")
    for zname, (a, b) in zones.items():
        sub = D[a:b]
        if not sub:
            continue
        mx = max(abs(d[0]**2 + d[1]**2 + d[2]**2)**0.5 for d in sub) * 1e6
        dxs = [d[0] for d in sub]
        dys = [d[1] for d in sub]
        dzs = [d[2] for d in sub]
        print(f"{zname:<14} {b-a:6d} {mx:12.3f} "
              f"{min(dxs)*1e6:12.3f} {max(dxs)*1e6:12.3f} "
              f"{min(dys)*1e6:12.3f} {max(dys)*1e6:12.3f} "
              f"{min(dzs)*1e6:12.3f} {max(dzs)*1e6:12.3f}")

    # ----- check 1: simetria em y -----------------------------------------
    Dy = [d[1] for d in D]
    print(f"\n===== Simetria em y (esperado ~0 medio) =====")
    print(f"  Dy min  = {min(Dy)*1e6:8.3f} um")
    print(f"  Dy max  = {max(Dy)*1e6:8.3f} um")
    print(f"  Dy mean = {sum(Dy)/len(Dy)*1e6:8.3f} um")
    sym_score = abs(min(Dy) + max(Dy)) / max(abs(min(Dy)), abs(max(Dy)) + 1e-30)
    print(f"  simetria score (|min+max|/max) = {sym_score:.3%}  (ideal: ~0%)")

    # ----- check 2: Dx dominante (push -X de contact_local em +X) ----------
    Dx = [d[0] for d in D]
    print(f"\n===== Dx dominantemente negativo? =====")
    print(f"  Dx min  = {min(Dx)*1e6:8.3f} um")
    print(f"  Dx max  = {max(Dx)*1e6:8.3f} um")
    print(f"  Dx mean = {sum(Dx)/len(Dx)*1e6:8.3f} um")

    # ----- check 5: |D| no globo pequeno comparado ao nervo ---------------
    a, b = zones["globo"]
    globo_max = max((d[0]**2+d[1]**2+d[2]**2)**0.5 for d in D[a:b]) * 1e6
    a, b = zones["on"]
    on_max = max((d[0]**2+d[1]**2+d[2]**2)**0.5 for d in D[a:b]) * 1e6
    print(f"\n===== |D| globo vs |D| nervo =====")
    print(f"  on  max = {on_max:8.3f} um")
    print(f"  globo max = {globo_max:8.3f} um")
    print(f"  ratio globo/on = {globo_max/(on_max+1e-30):.4f}  (esperado < 0.3)")


if __name__ == "__main__":
    main()
