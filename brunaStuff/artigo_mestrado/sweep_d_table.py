"""Sweep de Darcy d para o on-caso-1.2: compara compartimentalizacao
entre d=1e13 (minimo), d=1e15 (saudavel), d=1e17 (IIH/SANS).

Le os campos salvos em cases/on-caso-1.2/_sweep/d{1e13,1e15,1e17}/1/{p,U}
e gera uma tabela quantitativa com:
    - p_mean SAS bulk e peri_porous
    - |U|_max e mean SAS bulk e peri_porous
    - Vazao Q_drenagem aproximada (U_z * area_anular_outlet)
"""
from __future__ import annotations
import sys
sys.path.insert(0, 'brunaStuff')
from check_compartmentalization import parse_cellzones, parse_internal_field
from check_velocity import parse_vector_field
from pathlib import Path
import math

case = Path('cases/on-caso-1.2')
zones = parse_cellzones(case / 'fluid/constant/polyMesh/cellZones')

R_PIA_OUT = 1.55e-3
R_SCLERA_IN = 2.35e-3
A_OUTLET = math.pi * (R_SCLERA_IN ** 2 - R_PIA_OUT ** 2)


def stats_for_zone(p_all: list[float], U_all: list[tuple[float, float, float]],
                   ids: list[int]) -> dict:
    zp = [p_all[i] for i in ids]
    zU = [U_all[i] for i in ids]
    mags = [(u[0]**2 + u[1]**2 + u[2]**2) ** 0.5 for u in zU]
    uz = [u[2] for u in zU]
    return dict(
        p_mean=sum(zp)/len(zp),
        p_min=min(zp), p_max=max(zp),
        U_max=max(mags), U_mean=sum(mags)/len(mags),
        Uz_max=max(uz), Uz_mean=sum(uz)/len(uz),
    )


def report(d_label: str, sweep_dir: Path) -> dict:
    p_all = parse_internal_field(sweep_dir / "1/p")
    U_all = parse_vector_field(sweep_dir / "1/U")
    sas = stats_for_zone(p_all, U_all, zones["sas"])
    pp = stats_for_zone(p_all, U_all, zones["peri_porous"])
    Q_drainage = pp["Uz_mean"] * A_OUTLET
    return dict(d=d_label, sas=sas, pp=pp, Q=Q_drainage)


root = case / "_sweep"
results = [report(d, root / f"d{d}") for d in ["1e13", "1e15", "1e17"]]

hdr = (
    f"{'d (m^-2)':<10s} | "
    f"{'p_SAS (Pa)':>11s} {'p_pp (Pa)':>11s} {'Δp_lid (Pa)':>13s} | "
    f"{'|U|_SAS_max':>13s} {'|U|_pp_max':>13s} | "
    f"{'Q_drenage (m³/s)':>18s}"
)
print(hdr)
print("-" * len(hdr))
for r in results:
    sas, pp = r["sas"], r["pp"]
    print(
        f"d = {r['d']:<6s} | "
        f"{sas['p_mean']*1000:>11.1f} {pp['p_mean']*1000:>11.1f} "
        f"{(sas['p_mean']-pp['p_mean'])*1000:>13.1f} | "
        f"{sas['U_max']:>13.3e} {pp['U_max']:>13.3e} | "
        f"{r['Q']:>18.3e}"
    )

print()
print("Q_drenagem cerebral fisiologico estimado: ~3e-11 m^3/s")
print()
print("Compartmentalization assessment:")
Q_ref = results[1]['Q']  # d=1e15 healthy
for r in results:
    Q_norm = r['Q'] / max(Q_ref, 1e-30)
    label = ""
    if abs(math.log10(max(Q_norm, 1e-30))) < 0.3:
        label = "  <- baseline (saudavel ~ fisiologico)"
    elif Q_norm > 3:
        label = "  <- microdrenagem aberta (sem compartimentalizacao)"
    elif Q_norm < 0.3:
        label = "  <- COMPARTIMENTALIZADO (drenagem bloqueada, IIH/SANS-like)"
    print(f"  d={r['d']:<6s}: Q/Q_saudavel = {Q_norm:>8.3f} x{label}")
