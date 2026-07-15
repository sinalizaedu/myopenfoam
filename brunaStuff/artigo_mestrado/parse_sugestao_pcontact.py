"""
Extrai P_contact da arteria_externa em cada timestep escrito do sugestao smoke.
"""
from __future__ import annotations
import re
from pathlib import Path

SOLID = Path("cases/sugestao/solid")


def parse(time_dir: Path):
    txt = time_dir / "D"
    if not txt.exists():
        return None
    text = txt.read_text()
    m = re.search(
        r"arteria_externa\s*\{[^}]*?traction\s+nonuniform List<vector>\s+(\d+)\s*\((.*?)\)\s*;",
        text,
        re.DOTALL,
    )
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
    print(f"{'time(s)':>8s}  {'n_act':>5s}  {'Tmax_Pa':>10s}  {'Tmean_act_Pa':>13s}")
    print("-" * 50)
    for t in times:
        r = parse(t)
        if r is None:
            continue
        n_total, n_nz, tmax, tmean = r
        print(f"{t.name:>8s}  {n_nz:>5d}  {tmax:>10.2f}  {tmean:>13.2f}")


if __name__ == "__main__":
    main()
