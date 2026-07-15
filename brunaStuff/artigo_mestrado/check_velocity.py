"""Like check_compartmentalization.py mas extrai U (vector field) por cellZone."""
from __future__ import annotations
import re
import sys
from pathlib import Path


def parse_cellzones(path: Path) -> dict[str, list[int]]:
    text = path.read_text()
    out: dict[str, list[int]] = {}
    for m in re.finditer(
        r"^\s*(\S+)\s*\n\s*\{[^}]*?type\s+cellZone;[^}]*?cellLabels\s+List<label>\s*\n\s*(\d+)\s*\(\s*([0-9\s]+?)\)",
        text, re.MULTILINE | re.DOTALL,
    ):
        out[m.group(1)] = list(map(int, m.group(3).split()))
    return out


def parse_vector_field(path: Path) -> list[tuple[float, float, float]]:
    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s*\n\s*(\d+)\s*\(\s*([\s\S]+?)\)\s*;",
        text,
    )
    if not m:
        raise ValueError(f"Could not parse internalField in {path}")
    n = int(m.group(1))
    body = m.group(2)
    triples = re.findall(r"\(([-+0-9.eE\s]+)\)", body)
    out = []
    for t in triples:
        parts = t.split()
        out.append((float(parts[0]), float(parts[1]), float(parts[2])))
    assert len(out) == n, f"expected {n}, got {len(out)}"
    return out


def main(case_path: str, time: str = "1") -> None:
    case = Path(case_path).resolve()
    fluid = case / "fluid"
    cellzones = parse_cellzones(fluid / "constant" / "polyMesh" / "cellZones")
    U = parse_vector_field(fluid / time / "U")

    print(f"Case: {case}")
    print(f"Time: {time}")
    print(f"{'Zone':<14s} {'Count':>6s} {'|U|_max':>12s} {'|U|_mean':>12s} {'Uz_max':>12s}")
    print("-" * 64)
    for zone_name, ids in cellzones.items():
        zone_U = [U[i] for i in ids]
        mags = [(u[0]**2 + u[1]**2 + u[2]**2) ** 0.5 for u in zone_U]
        uz = [u[2] for u in zone_U]
        print(f"{zone_name:<14s} {len(ids):>6d} "
              f"{max(mags):>12.4e} {sum(mags)/len(mags):>12.4e} "
              f"{max(uz):>12.4e}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "1")
