"""Extrai estatisticas de pressao por cellZone para validar compartimentalizacao
do lid poroso no on-caso-1.2.

Uso:
    python brunaStuff/check_compartmentalization.py CASE_PATH [TIME]

Exemplo:
    python brunaStuff/check_compartmentalization.py cases/on-caso-1.2 1

Le os arquivos:
    CASE/fluid/constant/polyMesh/cellZones    (mapeia cellId -> zona)
    CASE/fluid/TIME/p                          (campo de pressao)

E reporta para cada cellZone (sas, peri_porous):
    - count, min, max, mean, std
    - permite comparar ICP (SAS bulk) vs P_outlet (=0) e identificar
      compartimentalizacao quando ICP_bulk >> P_outlet com gradiente
      concentrado no peri_porous.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_cellzones(path: Path) -> dict[str, list[int]]:
    """Le o arquivo polyMesh/cellZones do OpenFOAM e retorna dict zona -> cell ids."""
    text = path.read_text()
    out: dict[str, list[int]] = {}
    for m in re.finditer(
        r"^\s*(\S+)\s*\n\s*\{[^}]*?type\s+cellZone;[^}]*?cellLabels\s+List<label>\s*\n\s*(\d+)\s*\(\s*([0-9\s]+?)\)",
        text, re.MULTILINE | re.DOTALL,
    ):
        zone_name = m.group(1)
        n = int(m.group(2))
        labels = list(map(int, m.group(3).split()))
        assert len(labels) == n, f"{zone_name}: expected {n}, got {len(labels)}"
        out[zone_name] = labels
    return out


def parse_internal_field(path: Path) -> list[float]:
    """Le o internalField (scalar nonuniform List<scalar>) do arquivo de campo."""
    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\(\s*([\s\S]+?)\)\s*;",
        text,
    )
    if not m:
        raise ValueError(f"Could not parse internalField in {path}")
    n = int(m.group(1))
    values = list(map(float, m.group(2).split()))
    assert len(values) == n, f"expected {n}, got {len(values)}"
    return values


def stats(values: list[float]) -> tuple[float, float, float, float]:
    n = len(values)
    if n == 0:
        return (0.0, 0.0, 0.0, 0.0)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    std = var ** 0.5
    return (min(values), max(values), mean, std)


def main(case_path: str, time: str = "1") -> None:
    case = Path(case_path).resolve()
    fluid = case / "fluid"
    cellzones_path = fluid / "constant" / "polyMesh" / "cellZones"
    p_path = fluid / time / "p"

    if not cellzones_path.exists():
        sys.exit(f"ERROR: {cellzones_path} not found")
    if not p_path.exists():
        sys.exit(f"ERROR: {p_path} not found")

    zones = parse_cellzones(cellzones_path)
    p_all = parse_internal_field(p_path)

    print(f"Case:        {case}")
    print(f"Fluid time:  {time}")
    print(f"Total cells: {len(p_all)}")
    print()
    print(f"{'Zone':<14s} {'Count':>6s} {'min':>10s} {'max':>10s} {'mean':>10s} {'std':>10s}")
    print("-" * 64)

    p_global_min, p_global_max, p_global_mean, p_global_std = stats(p_all)
    print(f"{'<all>':<14s} {len(p_all):>6d} "
          f"{p_global_min:>10.4f} {p_global_max:>10.4f} "
          f"{p_global_mean:>10.4f} {p_global_std:>10.4f}")
    for zone_name, cell_ids in zones.items():
        zone_p = [p_all[i] for i in cell_ids]
        z_min, z_max, z_mean, z_std = stats(zone_p)
        print(f"{zone_name:<14s} {len(zone_p):>6d} "
              f"{z_min:>10.4f} {z_max:>10.4f} {z_mean:>10.4f} {z_std:>10.4f}")

    if "sas" in zones and "peri_porous" in zones:
        sas_p = [p_all[i] for i in zones["sas"]]
        pp_p = [p_all[i] for i in zones["peri_porous"]]
        sas_mean = sum(sas_p) / len(sas_p)
        pp_mean = sum(pp_p) / len(pp_p)
        delta = sas_mean - pp_mean
        p_inlet = max(p_all)
        ratio_drop_in_lid = delta / p_inlet if p_inlet else 0.0

        print()
        print("Compartmentalization analysis:")
        print(f"  Mean p in SAS bulk:    {sas_mean:>8.4f}  (~ {sas_mean*1000:.1f} Pa)")
        print(f"  Mean p in peri_porous: {pp_mean:>8.4f}  (~ {pp_mean*1000:.1f} Pa)")
        print(f"  Delta p across lid:    {delta:>8.4f}  (~ {delta*1000:.1f} Pa)")
        print(f"  Inlet  p:              {p_inlet:>8.4f}  (~ {p_inlet*1000:.1f} Pa)")
        print(f"  Fraction of total dp dropped in lid: {ratio_drop_in_lid*100:.1f}%")
        print()
        if ratio_drop_in_lid > 0.5:
            print("  -> PRESENCE of compartmentalization (lid carries >50% of dp).")
        else:
            print("  -> NO compartmentalization (lid is permeable; SAS bulk ~ outlet).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python check_compartmentalization.py CASE_PATH [TIME]")
    case_arg = sys.argv[1]
    time_arg = sys.argv[2] if len(sys.argv) > 2 else "1"
    main(case_arg, time_arg)
