#!/usr/bin/env python3
"""Diagnostico (NAO roda CalculiX -- so reprocessa .frd/.inp ja existentes):
tenta reextrair P(V) do coelho com p0_mmhg=26.7 em vez de 16.9, para ver se
isso e suficiente para corrigir o achado do WP1.5, ou se precisa mesmo de
um novo run de CCX com a rampa de pressao certa para a especie.
"""
import json
import sys
from pathlib import Path

WP12_SCRIPTS = Path("cases/wp1.2/scripts")
WP11_SCRIPTS = Path("cases/wp1.1/scripts")
sys.path.insert(0, str(WP12_SCRIPTS))
sys.path.insert(0, str(WP11_SCRIPTS))

from extract_pv_curve import extract_pv  # noqa: E402

WORK = Path("cases/claude-wp1.5/output_pilot_species_claude/ccx_runs")

P0_HUMANO = 16.9
P0_COELHO = 26.7


def keff(rows, p0):
    v = [r["dV_uL"] for r in rows if r["dV_uL"] > 0]
    p = [r["p_mmhg"] for r in rows if r["dV_uL"] > 0]
    if not v or v[0] <= 1e-9:
        return float("nan"), None, None
    return (p[0] - p0) / v[0], p[:3], v[:3]


for tag, p0_errado, p0_certo in [
    ("rabbit_ogden", P0_HUMANO, P0_COELHO),
    ("rabbit_yeoh", P0_HUMANO, P0_COELHO),
]:
    inp = WORK / f"{tag}.inp"
    frd = WORK / f"{tag}.frd"
    print(f"=== {tag} ===")
    meta = json.loads(inp.with_suffix(".meta.json").read_text())
    p_steps = [s["p_mmhg"] for s in meta.get("steps", [])]
    print(f"  pressoes na rampa (ja gravada no .inp): {p_steps[:3]} ... {p_steps[-3:]}")
    closest = min(p_steps, key=lambda p: abs(p - p0_certo))
    print(f"  passo mais proximo do P0 correto ({p0_certo}): {closest:.3f} mmHg "
          f"(delta={abs(closest-p0_certo):.3f})")

    rows_errado = extract_pv(inp, frd, R_mm=7.6, p0_mmhg=p0_errado)
    k_errado, p3, v3 = keff(rows_errado, p0_errado)
    print(f"  K_eff com p0={p0_errado} (como no script original): {k_errado:.4f} mmHg/uL")

    rows_certo = extract_pv(inp, frd, R_mm=7.6, p0_mmhg=p0_certo)
    k_certo, p3b, v3b = keff(rows_certo, p0_certo)
    print(f"  K_eff so trocando p0_mmhg->{p0_certo} no extract_pv "
          f"(SEM re-rodar CCX): {k_certo:.4f} mmHg/uL")
    print(f"    (nenhum passo da rampa cai perto de {p0_certo} mmHg -- "
          f"volume de referencia cai de volta no primeiro passo calculado, "
          f"~{p3b[0] if p3b else float('nan'):.2f} mmHg -- NAO e o volume "
          f"fisico do coelho em 26.7 mmHg, que nunca foi calculado)")
    print()

print("CONCLUSAO: reprocessar os .frd existentes so troca a REFERENCIA de "
      "volume (dV=0), mas a malha do coelho foi assumida SEM TENSAO logo no "
      "primeiro passo da rampa (~16.9 mmHg) e a rampa de pressao aplicada "
      "(16.9->50) nunca passa por 26.7->59.8 mmHg (a janela fisiologicamente "
      "correta). Nao da para corrigir sem rodar o CCX de novo com a rampa "
      "certa para o coelho.")
