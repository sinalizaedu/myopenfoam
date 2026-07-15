"""Compara compartimentalizacao entre d=1e15 e d=1e17."""
from __future__ import annotations
import sys
sys.path.insert(0, 'brunaStuff')
from check_compartmentalization import parse_cellzones, parse_internal_field, stats
from check_velocity import parse_vector_field
from pathlib import Path

case = Path('cases/on-caso-1.2')
zones = parse_cellzones(case / 'fluid/constant/polyMesh/cellZones')


def report(label: str, p_path: Path, U_path: Path) -> None:
    p_all = parse_internal_field(p_path)
    U_all = parse_vector_field(U_path)

    sas_ids = zones['sas']
    pp_ids = zones['peri_porous']
    sas_p = [p_all[i] for i in sas_ids]
    pp_p = [p_all[i] for i in pp_ids]

    sas_U = [U_all[i] for i in sas_ids]
    pp_U = [U_all[i] for i in pp_ids]
    sas_mag = [(u[0] ** 2 + u[1] ** 2 + u[2] ** 2) ** 0.5 for u in sas_U]
    pp_mag = [(u[0] ** 2 + u[1] ** 2 + u[2] ** 2) ** 0.5 for u in pp_U]

    sas_pm = sum(sas_p) / len(sas_p)
    pp_pm = sum(pp_p) / len(pp_p)
    p_max = max(p_all)
    p_min = min(p_all)

    print(f"\n=== {label} ===")
    print(f"  SAS bulk:    p mean = {sas_pm:>8.4f}  ({sas_pm * 1000:>7.1f} Pa)   "
          f"|U| max = {max(sas_mag):.4e}  mean = {sum(sas_mag)/len(sas_mag):.4e}")
    print(f"  peri_porous: p mean = {pp_pm:>8.4f}  ({pp_pm * 1000:>7.1f} Pa)   "
          f"|U| max = {max(pp_mag):.4e}  mean = {sum(pp_mag)/len(pp_mag):.4e}")
    print(f"  Delta p across lid:    {sas_pm - pp_pm:>8.4f}  ({(sas_pm - pp_pm) * 1000:.1f} Pa)")
    print(f"  Inlet  p:              {p_max:>8.4f}  ({p_max * 1000:.1f} Pa)")
    print(f"  Fraction dp dropped in lid: {(sas_pm - pp_pm) / p_max * 100:.1f}%")


root = case / "_compartmentalization-test"
report("d = 1e15  (SAUDAVEL)",
       root / "d1e15/1/p", root / "d1e15/1/U")
report("d = 1e17  (IIH/SANS-like)",
       root / "d1e17/1/p", root / "d1e17/1/U")

print("\n--- Comparison (Darcy efficiency check) ---")
p15 = parse_internal_field(root / "d1e15/1/p")
p17 = parse_internal_field(root / "d1e17/1/p")
sas15 = sum(p15[i] for i in zones["sas"]) / len(zones["sas"])
sas17 = sum(p17[i] for i in zones["sas"]) / len(zones["sas"])
print(f"  ICP_bulk @ d=1e15: {sas15 * 1000:>8.1f} Pa")
print(f"  ICP_bulk @ d=1e17: {sas17 * 1000:>8.1f} Pa")
print(f"  ICP_bulk increase: {(sas17 - sas15) * 1000:+.1f} Pa "
      f"({(sas17 - sas15) / sas15 * 100:+.1f}%)")

if abs(sas17 - sas15) / max(abs(sas15), 1e-9) > 0.05:
    print("\n  -> Darcy is now SENSITIVE to d! Compartmentalizacao Darcy-driven OK.")
else:
    print("\n  -> Darcy still NOT sensitive to d (ICP unchanged with d). PATCH FAILED?")
