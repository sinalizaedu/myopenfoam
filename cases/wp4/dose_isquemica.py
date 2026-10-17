"""WP4.2 — dose isquêmica por evento único (𝓘), sobre o 4.1 e o solver 0D.

Construído sobre ``opp_perfusion.py`` (4.1) e ``cases/wp0/goldmann_iop_solver.py``
sem editar nenhum dos dois.

1. ``dose_isquemica(t, OPP_t, OPP_crit)`` — integral generalizada do déficit,
   aplicável a MOPP(t) ou OPP_diast(t).
2. ``dose_isquemica_da_cadeia(t, chain)`` — 𝓘 para as duas definições de
   perfusão a partir do dict de ``aplicar_cadeia`` (4.1).
3. ``curva_sensibilidade_opp_crit`` — 𝓘(OPP_crit) em faixa, nunca um número só.
4. ``derivar_P0_equilibrio`` / ``protocolo_com_P0_literatura`` — P0 ancorado
   nos quatro parâmetros de vazão da literatura (relatório WP0), não fixado
   à mão.
5. ``validacao_fechada_H6`` — 𝓘 numérico (solver 0D) vs fórmula fechada de H6
   para K constante (ThinShellPV), sem paracentese; ΔV líquido com refluxo instantâneo.

Âncoras de literatura para a faixa de OPP_crit (documentação, NÃO calibração):
Baltimore Eye Survey (DOPP<30, crônico), Barbados Eye Study (MOPP<42, crônico),
CRAO completa (12–15 min, limiar de TEMPO). Nenhuma medida no regime agudo
transitório pós-IVI.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for _p in (str(WP4), str(WP0)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from goldmann_iop_solver import Protocol, _reflux_mode, simulate  # noqa: E402


def delta_V_bolus_fechada(proto: Protocol) -> float:
    """Volume efetivo do bólus na forma fechada H6 (bólus + refluxo instantâneo WP0).

    Injeção completa em ``t_inj_dur_min``, refluxo instantâneo em seguida:
    ``ΔV = V_inj − ΔV_refluxo`` quando ``reflux_mode='instant'``.
    """
    dV = float(proto.V_inj_uL)
    mode = _reflux_mode(proto)
    if mode == "instant":
        dV -= float(proto.reflux_instant_dV_uL)
    elif mode == "poiseuille":
        raise ValueError(
            "delta_V_bolus_fechada: refluxo Poiseuille não entra na forma fechada H6 "
            "(use reflux_mode='instant' ou 'none')."
        )
    return dV
from opp_perfusion import aplicar_cadeia, opp_crit_efetivo  # noqa: E402

_trapz = getattr(np, "trapezoid", None) or np.trapz


def dose_isquemica(t_min: np.ndarray, OPP_t: np.ndarray, OPP_crit_mmHg: float) -> float:
    """𝓘 = ∫ max(0, OPP_crit − OPP(t)) dt  [mmHg·min]."""
    t = np.asarray(t_min, dtype=float)
    opp = np.asarray(OPP_t, dtype=float)
    if t.shape != opp.shape:
        raise ValueError("t_min e OPP_t precisam ter o mesmo formato")
    deficit = np.clip(OPP_crit_mmHg - opp, 0.0, None)
    return float(_trapz(deficit, t))


def dose_isquemica_da_cadeia(t_min: np.ndarray, chain: dict) -> dict:
    """𝓘 para MOPP e OPP_diast a partir do dict de ``aplicar_cadeia`` (4.1),
    no mesmo OPP_crit efetivo (já ajustado por phi_vasc)."""
    opp_crit_eff = chain["opp_crit_efetivo"]
    out = {
        "opp_crit_efetivo_mmHg": opp_crit_eff,
        "I_MOPP_mmHg_min": dose_isquemica(t_min, chain["mopp"], opp_crit_eff),
    }
    opp_diast = chain.get("opp_diast")
    out["I_OPP_diast_mmHg_min"] = (
        dose_isquemica(t_min, opp_diast, opp_crit_eff) if opp_diast is not None else None
    )
    return out


def curva_sensibilidade_opp_crit(
    t_min: np.ndarray,
    OPP_t: np.ndarray,
    opp_crit_range=(20, 25, 30, 35, 40, 45, 50, 55, 60),
) -> dict:
    """𝓘 como função de OPP_crit — nunca reportar 𝓘 sem esta curva ao lado
    (plano de tese, Seção 4.2/4.3)."""
    return {float(th): dose_isquemica(t_min, OPP_t, th) for th in opp_crit_range}


def derivar_P0_equilibrio(
    Pev_mmHg: float,
    Q_prod_uL_min: float,
    C_out_uL_min_mmHg: float,
    frac_uveoscleral: float,
) -> float:
    """P0 = Pev + Q_prod·(1 − frac_uv)/C_out — equilíbrio de Goldmann (dV/dt=0)."""
    return Pev_mmHg + Q_prod_uL_min * (1.0 - frac_uveoscleral) / C_out_uL_min_mmHg


# Mesmos parâmetros da tabela "Produção trabecular e uveoescleral" do
# relatório WP0: Goel et al. 2010 (humano); Kiel et al. 2011/2015 e
# Fourman & Garner 1989 (coelho anestesiado).
_PARAMS_LITERATURA = {
    "humano": dict(Q_prod_uL_min=2.4, C_out_uL_min_mmHg=0.28, Pev_mmHg=10.0, frac_uveoscleral=0.20),
    "coelho_anestesiado": dict(Q_prod_uL_min=3.06, C_out_uL_min_mmHg=0.26, Pev_mmHg=15.5, frac_uveoscleral=0.05),
}


def protocolo_com_P0_literatura(especie: str = "humano", **overrides) -> Protocol:
    """``Protocol`` cujo P0 é DERIVADO dos parâmetros de vazão de literatura.

    Motivo: ``Protocol()`` sem calibrar P0 com Q_prod da Tabela 3 deriva a IOP basal.
    Aqui P0 é o equilíbrio exato dos quatro parâmetros de fluxo. Refluxo fica
    ``none`` salvo override (o relatório WP0 usa ``instant`` via ``protocol_humano_relatorio``).

    ``overrides``: kwargs de fluxo (Q_prod_uL_min, C_out_uL_min_mmHg,
    Pev_mmHg, frac_uveoscleral) recalculam P0; demais kwargs (V_inj_uL,
    t_end_min, par_enabled, ...) passam direto para ``Protocol``.
    """
    if especie not in _PARAMS_LITERATURA:
        raise ValueError(f"especie desconhecida: {especie!r}. Use uma de {list(_PARAMS_LITERATURA)}")
    params = dict(_PARAMS_LITERATURA[especie])
    fluxo_keys = ("Q_prod_uL_min", "C_out_uL_min_mmHg", "Pev_mmHg", "frac_uveoscleral")
    outros_kwargs = {}
    for k, v in overrides.items():
        if k in fluxo_keys:
            params[k] = v
        else:
            outros_kwargs[k] = v
    P0 = derivar_P0_equilibrio(
        params["Pev_mmHg"], params["Q_prod_uL_min"],
        params["C_out_uL_min_mmHg"], params["frac_uveoscleral"],
    )
    return Protocol(
        P0_mmHg=P0,
        Pev_mmHg=params["Pev_mmHg"],
        Q_prod_uL_min=params["Q_prod_uL_min"],
        C_out_uL_min_mmHg=params["C_out_uL_min_mmHg"],
        frac_uveoscleral=params["frac_uveoscleral"],
        reflux_mode="none",
        **outros_kwargs,
    )


def validacao_fechada_H6(
    proto: Protocol,
    pv,
    OPP_crit_ref_mmHg: float,
    mopp_factor: float = 2.0 / 3.0,
    phi_vasc: float = 1.0,
) -> dict:
    """𝓘 numérico (solver 0D, via MOPP) vs fórmula fechada de H6:

        τ = 1/(C·K);  dP0 = K·ΔV;  dPth = f·MAP − P0 − OPP_crit_efetivo
        I_fechado = τ·(dP0 − dPth − dPth·ln(dP0/dPth))  se dP0 > dPth, senão 0

    Só válida para K CONSTANTE (ThinShellPV) e sem paracentese. A fórmula fechada
    usa ``delta_V_bolus_fechada(proto)`` (refluxo instantâneo WP0 como descontinuidade
    no fim da IVI). Requer dPth > 0 (MOPP basal acima do limiar). Residual esperado
    pequeno: bólus instantâneo versus rampa de injeção de 6 s.
    """
    if not hasattr(pv, "K_mmHg_per_uL"):
        raise ValueError(
            "validacao_fechada_H6 requer PV com K constante (ThinShellPV) — "
            "a fórmula fechada de H6 não vale para P(V) não-linear (ex.: FriedenwaldPV)."
        )
    if proto.par_enabled:
        raise ValueError(
            "validacao_fechada_H6 requer paracentese desligada — a fórmula de H6 "
            "não inclui Q_par."
        )
    K = pv.K_mmHg_per_uL
    C = proto.C_out_uL_min_mmHg
    dV = delta_V_bolus_fechada(proto)
    tau = 1.0 / (C * K)

    MAP = proto.DBP_mmHg + (proto.SBP_mmHg - proto.DBP_mmHg) / 3.0
    opp_crit_eff = opp_crit_efetivo(OPP_crit_ref_mmHg, phi_vasc)
    dP_th = mopp_factor * MAP - proto.P0_mmHg - opp_crit_eff
    dP_0 = K * dV

    if dP_th <= 0:
        raise ValueError(
            f"dP_th={dP_th:.2f} <= 0: a MOPP basal já está abaixo de "
            f"OPP_crit_efetivo ({opp_crit_eff:.1f} mmHg) mesmo sem injeção — "
            "a fórmula fechada de H6 não se aplica neste regime. Verifique se "
            "proto.P0_mmHg é de fato o equilíbrio da ODE (ver "
            "protocolo_com_P0_literatura()) e/ou reduza OPP_crit_ref_mmHg."
        )

    I_fechado = 0.0 if dP_0 <= dP_th else tau * (dP_0 - dP_th - dP_th * np.log(dP_0 / dP_th))

    t, _V, P = simulate(proto, pv)
    chain = aplicar_cadeia(
        t, P,
        pas=proto.SBP_mmHg, pad=proto.DBP_mmHg,
        opp_crit_ref=OPP_crit_ref_mmHg,
        fator_braquial=mopp_factor, phi_vasc=phi_vasc,
    )
    I_numerico = dose_isquemica(t, chain["mopp"], chain["opp_crit_efetivo"])

    erro_rel = (
        abs(I_numerico - I_fechado) / I_fechado
        if I_fechado > 0
        else abs(I_numerico - I_fechado)
    )
    return {
        "I_numerico_mmHg_min": I_numerico,
        "I_fechado_mmHg_min": I_fechado,
        "erro_relativo": erro_rel,
        "dP_0_mmHg": dP_0,
        "dP_th_mmHg": dP_th,
        "tau_min": tau,
        "K_mmHg_per_uL": K,
    }


if __name__ == "__main__":
    from goldmann_iop_solver import ThinShellPV

    proto = protocolo_com_P0_literatura("humano")
    print(f"P0 derivado (humano) = {proto.P0_mmHg:.2f} mmHg "
          f"(Protocol() default: {Protocol().P0_mmHg})")
    proto_c = protocolo_com_P0_literatura("coelho_anestesiado")
    print(f"P0 derivado (coelho anestesiado) = {proto_c.P0_mmHg:.2f} mmHg")

    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, _V, P = simulate(proto, pv)
    chain = aplicar_cadeia(t, P, pas=proto.SBP_mmHg, pad=proto.DBP_mmHg,
                           opp_crit_ref=50.0)
    d = dose_isquemica_da_cadeia(t, chain)
    print(f"\nI via MOPP      = {d['I_MOPP_mmHg_min']:.2f} mmHg.min")
    print(f"I via OPP_diast = {d['I_OPP_diast_mmHg_min']:.2f} mmHg.min")

    print("\nCurva de sensibilidade a OPP_crit (via MOPP):")
    for th, val in curva_sensibilidade_opp_crit(t, chain["mopp"]).items():
        print(f"  OPP_crit={th:5.1f}  I={val:8.2f} mmHg.min")

    v = validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)
    print(f"\nValidação H6: I_num={v['I_numerico_mmHg_min']:.3f} vs "
          f"I_fechado={v['I_fechado_mmHg_min']:.3f} "
          f"(erro {v['erro_relativo'] * 100:.2f}%)")
