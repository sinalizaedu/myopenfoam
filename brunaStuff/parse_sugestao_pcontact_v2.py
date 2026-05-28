"""
Extrai P_contact da arteria_externa em cada timestep escrito do sugestao.
Versao v2 com gordura 3D: shadowPatch agora eh fat_inner_arteria.
Tambem extrai a interface fat_inner_nerve <-> ons_outer.
"""
from __future__ import annotations
import re
from pathlib import Path

SOLID = Path("cases/sugestao/solid")


def parse_traction_on_patch(time_dir: Path, patch_name: str):
    """Extrai traction da arteria_externa (D file) ou outras BCs solidContact."""
    d_file = time_dir / "D"
    if not d_file.exists():
        return None
    text = d_file.read_text()
    pat = re.compile(
        rf"{patch_name}\s*\{{[^}}]*?traction\s+nonuniform List<vector>\s+(\d+)\s*\((.*?)\)\s*;",
        re.DOTALL,
    )
    m = pat.search(text)
    if not m:
        return None
    n_total = int(m.group(1))
    body = m.group(2)
    vals = re.findall(
        r"\(([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\)",
        body,
    )
    if not vals:
        return None
    mags = [(float(a) ** 2 + float(b) ** 2 + float(c) ** 2) ** 0.5 for a, b, c in vals]
    nz = [v for v in mags if v > 1e-3]
    return n_total, len(nz), max(mags), (sum(nz) / len(nz) if nz else 0.0)


def main() -> None:
    times = sorted(
        [p for p in SOLID.iterdir() if p.is_dir() and re.match(r"0\.\d", p.name)],
        key=lambda p: float(p.name),
    )

    print("=" * 80)
    print("INTERFACE 1: arteria_externa <-> fat_inner_arteria  (P_contact da arteria)")
    print("=" * 80)
    print(f"{'time(s)':>8s}  {'n_act':>6s}  {'Tmax_Pa':>10s}  {'Tmean_act_Pa':>13s}")
    print("-" * 50)
    for t in times:
        r = parse_traction_on_patch(t, "arteria_externa")
        if r is None:
            continue
        n_total, n_nz, tmax, tmean = r
        print(f"{t.name:>8s}  {n_nz:>3d}/{n_total:<3d}  {tmax:>10.2f}  {tmean:>13.2f}")

    print()
    print("=" * 80)
    print("INTERFACE 2: fat_inner_nerve <-> ons_outer  (P transmitida ao nervo)")
    print("=" * 80)
    print(f"{'time(s)':>8s}  {'n_act':>6s}  {'Tmax_Pa':>10s}  {'Tmean_act_Pa':>13s}")
    print("-" * 50)
    for t in times:
        r = parse_traction_on_patch(t, "fat_inner_nerve")
        if r is None:
            continue
        n_total, n_nz, tmax, tmean = r
        print(f"{t.name:>8s}  {n_nz:>3d}/{n_total:<3d}  {tmax:>10.2f}  {tmean:>13.2f}")


if __name__ == "__main__":
    main()
