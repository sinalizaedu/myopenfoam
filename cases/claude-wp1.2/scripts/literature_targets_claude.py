#!/usr/bin/env python3
"""WP1.2 (Claude, independente) — 4 alvos P(V) da literatura para calibracao.

Terceiro braco independente (Sonnet), em paralelo a cases/wp1.2/ (Composer/Cursor).
Nao edita nada la -- so importa ExpPoint de fit_hyperelastic.py (ja validado).

Diferenca deliberada em relacao a cases/wp1.2/scripts/literature_targets.py:
  - "friedenwald" aqui usa o coeficiente RECALIBRADO do WP0 da usuaria
    (Kf=0.00581 /uL, contra o pico clinico de Knecht et al. 2009), e NAO o
    coeficiente classico historico (Kf=0.0215 /uL, olho enucleado) que o
    modulo do Composer usa sob o mesmo nome. Ver PRETENSION_MECHANISM_
    INVESTIGATION.md e figs/06_pv_all_sources_combined.png em
    cases/claude-wp1_analysis/ para a justificativa: o alvo classico (0.0215)
    prediz ~85 mmHg em V=50uL (implausivel); o recalibrado do WP0 prediz
    33.0 mmHg, alinhado com a media dos picos clinicos reais (35.3 mmHg).
  - "pallikaris", "silver" e "agra" usam os mesmos coeficientes/dados que o
    Composer ja usa (fonte cruzada: cases/wp1.2/scripts/literature_targets.py,
    lido mas nao editado), reimplementados aqui para manter este braco
    numericamente autocontido e auditavel de forma independente.

Convencao: todas as curvas retornam ExpPoint(V_uL, P_mmHg) com P_mmHg = DeltaP
acima de P0 (mesma convencao "delta_P_above_P0" usada por fit_pallikaris.py
e run_e3_e1b.py), para poderem ser passadas direto a fit_ogden1()/fit_yeoh2().
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
WP12 = HERE.parent.parent / "wp1.2"
sys.path.insert(0, str(WP12 / "scripts"))

from fit_hyperelastic import ExpPoint  # noqa: E402  (reuso, somente leitura)
from fit_pallikaris import (  # noqa: E402
    V_MAX_PALLIKARIS_DIGIT,
    pallikaris_digitized_points,
)

PALLIKARIS_TARGET_MODE = "synthetic"  # overridden by run_literature_matrix_claude --pallikaris-mode

# ---------------------------------------------------------------------------
# Constantes compartilhadas
# ---------------------------------------------------------------------------
P0_MMHG = 16.9  # basal do WP0 (equilibrio 0D: P_ev + Q_prod(1-f_uv)/C_out)

# Pallikaris et al. (2005) -- forma exponencial (Friedenwald log-linear
# rearranjado). Kf igual ao usado por cases/wp1.2/fit_pallikaris.py, mas
# ATENCAO: aqui a curva e RE-ANCORADA no basal do proprio WP0 (P0_MMHG=16.9),
# nao no basal do artigo (P0_paper=10 mmHg). Ver pallikaris_pressure() abaixo
# -- usar P0_MMHG diretamente como prefator (P0_MMHG * 10**(Kf*V), como o
# fit_pallikaris.py do Composer faz) mistura o slope calibrado contra um
# basal de 10 mmHg com um basal fisiologico diferente (16.9), o que infla
# a curva inteira por um fator ~1.7x (72 mmHg em V=50uL em vez dos ~44-50
# mmHg que o grafico digitalizado do artigo realmente mostra -- ver
# cases/claude-wp1_analysis/pv_literature/). Achado reportado a usuaria em
# 2026-09-23; o mesmo bug existe em cases/wp1.2/scripts/fit_pallikaris.py
# (nao editado aqui, so usado como leitura por outros modulos deste caso).
KF_PALLIKARIS = 0.0126
P0_PALLIKARIS_PAPER = 10.0  # basal real do artigo (Fig. 2), nao confundir com P0_MMHG

# Friedenwald RECALIBRADO do WP0 (contra Knecht et al. 2009, IVI 50uL) --
# ALVO ADOTADO pela usuaria no WP0, distinto do classico 0.0215.
KF_FRIEDENWALD_WP0 = 0.00581

# Silver & Geyer (2000) -- coeficientes exatos do artigo (olho medio,
# V_ref=6200uL): dV(P) = -49.8 + 30.2*ln(P) + 0.242*P  [uL, P em mmHg]
def dV_silver(p: float) -> float:
    return -49.8 + 30.2 * np.log(p) + 0.242 * p


def v_inj_silver(p: float, p0: float = P0_MMHG) -> float:
    return dV_silver(p) - dV_silver(p0)


def p_from_v_silver(v_target: float, p0: float = P0_MMHG, p_hi: float = 400.0) -> float:
    if abs(v_target) < 1e-12:
        return p0
    f = lambda p: v_inj_silver(p, p0) - v_target
    return float(brentq(f, p0, p_hi))


# Agra et al. (2023) -- Tabela 2, bancada hidraulica (nao e olho; usado como
# alvo de calibracao mecanica pura, sem componente de fisiologia ocular).
V_AGRA = np.array([20.0, 30.0, 40.0, 50.0], dtype=float)
P_AGRA = np.array([32.3, 36.5, 43.5, 50.7], dtype=float)


def pallikaris_pressure(v_uL: float, p0: float = P0_MMHG, kf: float = KF_PALLIKARIS) -> float:
    """P(V) do Pallikaris, RE-ANCORADA no basal p0 (default P0_MMHG=16.9).

    Usa o INCREMENTO que a curva do artigo preve a partir do seu proprio
    basal (P0_PALLIKARIS_PAPER=10 mmHg) e soma esse incremento em cima de
    p0. Em V=50uL isso da ~49.6 mmHg (bate com o grafico digitalizado, que
    mostra ~44 mmHg em V=49uL) -- MUITO diferente dos 72 mmHg que a formula
    ingenua p0*10**(kf*V) da quando p0=16.9 (essa forma so faz sentido com
    p0=P0_PALLIKARIS_PAPER=10, o basal que o artigo realmente usou).
    """
    delta = P0_PALLIKARIS_PAPER * (10.0 ** (kf * v_uL)) - P0_PALLIKARIS_PAPER
    return p0 + delta


def friedenwald_wp0_pressure(v_uL: float, p0: float = P0_MMHG, kf: float = KF_FRIEDENWALD_WP0) -> float:
    return p0 * (10.0 ** (kf * v_uL))


TARGETS = ("pallikaris", "silver", "agra", "friedenwald")

# ---------------------------------------------------------------------------
# IMPORTANTE: P_final=50 mmHg e o TETO da rampa de pressao na FEA (ver
# run_literature_matrix_claude.py). Isso significa que a FEA nunca aplica
# mais que 50 mmHg absolutos -- entao nenhum ponto-alvo pode pedir um volume
# que, na curva original, so e alcancado acima de 50 mmHg (a FEA nunca
# "chegaria la" e o residuo do ajuste ficaria artificialmente grande/invalido).
#
# Ao inverter cada curva em P=50 mmHg (ver bloco __main__ para os numeros):
#   pallikaris (re-ancorada, ver acima): P=50mmHg em V=50.4 uL -> cabe justo
#   silver & geyer:                       P=50mmHg em V=40.8 uL -> EXTRAPOLA
#   friedenwald recalibrado WP0:          P=50mmHg em V=81.1 uL -> folga ampla
#   agra (tabela, V=50 -> P=50.7):        ultimo ponto (50.7) fica ACIMA do teto
#
# (correcao de 2026-09-23: pallikaris usava v_max=35 aqui por causa do bug de
# baseline described acima -- P0=16.9 aplicado direto no prefator inflava a
# curva e fazia ela "precisar" de 72mmHg em V=50uL. Re-ancorada corretamente,
# ela cabe quase exatamente no teto de 50mmHg em V=50uL, entao volta a usar
# o volume clinico padrao inteiro, igual ao friedenwald.)
#
# Para silver e agra o problema e outro (a curva deles, mesmo correta, pede
# mais que 50mmHg antes de V=50uL) -- por isso o alvo e truncado com margem
# de seguranca abaixo do ponto onde a propria curva ja pediria mais que
# 50 mmHg. Friedenwald e pallikaris (agora corrigida) sao os unicos que
# cobrem o volume clinico padrao inteiro (0-50 uL) dentro do novo teto.
V_MAX_SAFE = {
    "pallikaris": V_MAX_PALLIKARIS_DIGIT if PALLIKARIS_TARGET_MODE == "digitized" else 50.0,
    "silver": 38.0,       # margem sob 40.8 uL
    "friedenwald": 50.0,  # alvo adotado no WP0; P(50uL)=33.0 mmHg, folgado
    "agra": 40.0,         # so pontos com P<=50 mmHg (V=50/P=50.7 descartado)
}


def _write_csv(path: Path, rows: list[ExpPoint], eye_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_mmHg", "eye_id"])
        for row in rows:
            w.writerow([f"{row.V_uL:.4f}", f"{row.P_mmHg:.4f}", eye_id])


def generate_target(
    target: str,
    path: Path,
    *,
    v_max: float | None = None,
    n_pts: int = 9,
    p0: float = P0_MMHG,
) -> list[ExpPoint]:
    """Constroi a curva-alvo (CSV + lista de ExpPoint, DeltaP acima de P0).

    v_max=None usa o teto seguro em V_MAX_SAFE (ver comentario acima sobre
    por que isso difere por alvo quando P_final=50 mmHg).
    """
    target = target.lower().strip()
    if v_max is None:
        v_max = V_MAX_SAFE.get(target, 50.0)
    rows: list[ExpPoint] = []

    if target == "pallikaris":
        if PALLIKARIS_TARGET_MODE == "digitized":
            rows = pallikaris_digitized_points(
                v_max=min(v_max, V_MAX_PALLIKARIS_DIGIT),
            )
            eye_id = "pallikaris_digitized"
        else:
            vs = np.linspace(0.0, v_max, n_pts)
            for v in vs:
                p_abs = pallikaris_pressure(float(v), p0, KF_PALLIKARIS)
                rows.append(ExpPoint(V_uL=float(v), P_mmHg=float(p_abs - p0)))
            eye_id = "pallikaris_synthetic"

    elif target == "friedenwald":
        vs = np.linspace(0.0, v_max, n_pts)
        for v in vs:
            p_abs = friedenwald_wp0_pressure(float(v), p0, KF_FRIEDENWALD_WP0)
            rows.append(ExpPoint(V_uL=float(v), P_mmHg=float(p_abs - p0)))
        eye_id = "friedenwald_wp0_recalibrated"

    elif target == "silver":
        vs = np.linspace(0.0, v_max, n_pts)
        for v in vs:
            p_abs = p_from_v_silver(float(v), p0)
            rows.append(ExpPoint(V_uL=float(v), P_mmHg=float(p_abs - p0)))
        eye_id = "silver_geyer_2000"

    elif target == "agra":
        for v, p_abs in zip(V_AGRA, P_AGRA):
            if v <= v_max + 1e-9:
                rows.append(ExpPoint(V_uL=float(v), P_mmHg=float(p_abs - p0)))
        eye_id = "agra_2023_bench"

    else:
        raise ValueError(f"Unknown target {target!r}; use pallikaris|silver|agra|friedenwald")

    _write_csv(path, rows, eye_id)
    return rows


if __name__ == "__main__":
    # Sanity check rapido: imprime P(V=50uL) para os 4 alvos.
    out = Path("/tmp/_claude_target_check")
    for t in TARGETS:
        rows = generate_target(t, out / f"{t}.csv")
        v_last = rows[-1].V_uL
        p_last_abs = rows[-1].P_mmHg + P0_MMHG
        print(f"{t:12s}: V={v_last:5.1f} uL -> P={p_last_abs:6.2f} mmHg (abs)")
