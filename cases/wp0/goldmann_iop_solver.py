"""
goldmann_iop_solver.py
=======================

WP0 - nucleo 0D do plano de tese: IOP apos injecao intravitrea (IVI).

Resolve o balanço de volume do olho

    dV/dt = Q_prod + Q_ivi(t) - Q_TM(P) - Q_uv - Q_reflux(t, P) - Q_par(t, P)

onde P = P(V) vem de uma curva de rigidez ocular (casca fina linear ou
Friedenwald exponencial, trocavel por uma spline de FEA/dado experimental
mais tarde sem mudar o resto do codigo).

Termos incluidos (todos ligáveis/desligaveis por parametro):
  - Q_prod       producao de humor aquoso (constante)
  - Q_ivi(t)     injecao intravitrea, rampa de duracao finita
  - Q_TM(P)      escoamento trabecular, C_out*(P - P_ev)
  - Q_uv         escoamento uveoescleral (aprox. constante)
  - Q_reflux(t,P) refluxo pelo trajeto escleral da agulha (Poiseuille),
                  ativo por uma janela apos a injecao
  - Q_par(t,P)   paracentese (Poiseuille), ativo numa janela escolhida

Pos-processamento:
  - IOP(t) = P(V(t))
  - pressao de perfusao ocular MOPP(t) = (2/3)*MAP - IOP(t)
  - "dose isquemica" I = integral de max(0, OPP_crit - MOPP(t)) dt
  - tempo acima de limiares de IOP

Instalacao (uma vez so):
    pip install numpy scipy matplotlib

Uso rapido (relatorio wp0.tex):
    cd cases/wp0 && ./Allrun
    # ou: python3 wp0_report.py

O demo legado ``python3 goldmann_iop_solver.py`` delega ao pipeline do relatorio.
``reflux_mode="poiseuille"`` e ``par_mode="duration"`` estao depreciados.

Uso programatico: importe as classes e funcoes deste arquivo no seu
proprio script/notebook. Ver `simulate()`, `Protocol`, `ThinShellPV`,
`FriedenwaldPV`, `perfusion_metrics()`, `ischemic_dose_curve()`,
`volume_para_alvo()` e `K_de_biometria()`.

Autor: WP0, plano de tese "Biomecanica do pico pressorico agudo pos-IVI".
"""

from __future__ import annotations

import dataclasses
import warnings
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from scipy.integrate import solve_ivp

MMHG_TO_PA = 133.322

# Tabela 3 (wp0.tex): P0 arredondado; Q_prod calibrado para dV/dt=0 em V=0 nesse P0
# (humano ~2,415 uL/min vs 2,4 citado; coelho ~3,0653 vs 3,06 citado).
P0_HUMAN_REPORT_MMHG = 16.9
P0_RABBIT_REPORT_MMHG = 26.7
PEV_HUMAN_REPORT_MMHG = 10.0
PEV_RABBIT_REPORT_MMHG = 15.5
C_OUT_HUMAN_REPORT = 0.28
C_OUT_RABBIT_REPORT = 0.26
FRAC_UV_HUMAN_REPORT = 0.20
FRAC_UV_RABBIT_REPORT = 0.05

def _equilibrium_q(P0: float, Pev: float, C: float, f: float) -> float:
    return float(C * (P0 - Pev) / (1.0 - f))


# Calibrados para P0 da Tabela 3: Q = C_out(P0-P_ev)/(1-f_uv) → humano 2,415000.
Q_PROD_HUMAN_TABELA_UL_MIN = 2.415
Q_PROD_RABBIT_TABELA_UL_MIN = 3.065263
Q_PROD_HUMAN_TABLE_ROUNDED_UL_MIN = 2.4  # Tabela 3 (texto); ver desvio em verify_wp0_standards
Q_PROD_RABBIT_TABLE_ROUNDED_UL_MIN = 3.06

# numpy >=2.0 renomeou trapz -> trapezoid; mantem compatibilidade com ambas as versoes
_trapz = getattr(np, "trapezoid", None) or np.trapz


# ---------------------------------------------------------------------------
# 1. Relacoes de rigidez ocular P(V)  --  trocaveis, mesma interface
# ---------------------------------------------------------------------------

class ThinShellPV:
    """
    P(V) linear a partir da formula de casca fina esferica:

        K = dP/dV = t*E / (2*pi*R^4*(1-nu))      [Pa/m3]

    Uso: verificacao rapida, ou quando so se tem E, t, R (sem dado de
    inflacao). Subestima a rigidez real por nao ter recrutamento de
    fibras (ver H2 do plano de tese) -- prefira FriedenwaldPV quando
    houver K medido ou K_f da literatura.
    """

    def __init__(self, R_m: float, t_m: float, E_Pa: float, nu: float = 0.47,
                 P0_mmHg: float = 15.0, V0_uL: float = 0.0):
        self.K_Pa_per_m3 = t_m * E_Pa / (2 * np.pi * R_m**4 * (1 - nu))
        self.K_mmHg_per_uL = self.K_Pa_per_m3 * 1e-9 / MMHG_TO_PA
        self.P0 = P0_mmHg
        self.V0 = V0_uL

    def P(self, V_uL: float) -> float:
        """Pressao (mmHg) dado o volume (uL, relativo à mesma origem de V0)."""
        return self.P0 + self.K_mmHg_per_uL * (V_uL - self.V0)

    def dPdV(self, V_uL: float) -> float:
        return self.K_mmHg_per_uL

    def V_of_P(self, P_mmHg: float) -> float:
        return self.V0 + (P_mmHg - self.P0) / self.K_mmHg_per_uL


class FriedenwaldPV:
    """
    P(V) exponencial (lei de Friedenwald, 1937):

        log10(P) = log10(P0) + Kf*(V - V0)

    Kf tipico em humano: 0.0126-0.0221 uL^-1 (faixa da literatura).
    Reproduz o enrijecimento nao linear por recrutamento de fibras que
    o modelo linear (ThinShellPV) nao tem -- ver H2 do plano de tese.
    """

    def __init__(self, Kf_per_uL: float, P0_mmHg: float = 15.0, V0_uL: float = 0.0):
        self.Kf = Kf_per_uL
        self.P0 = P0_mmHg
        self.V0 = V0_uL

    def P(self, V_uL: float) -> float:
        return self.P0 * 10 ** (self.Kf * (V_uL - self.V0))

    def dPdV(self, V_uL: float) -> float:
        return self.P(V_uL) * self.Kf * np.log(10)

    def V_of_P(self, P_mmHg: float) -> float:
        return self.V0 + np.log10(P_mmHg / self.P0) / self.Kf


# ---------------------------------------------------------------------------
# 2. Parametros do protocolo
# ---------------------------------------------------------------------------

@dataclass
class Protocol:
    # --- pressao e producao basais -----------------------------------
    P0_mmHg: float = P0_HUMAN_REPORT_MMHG  # IOP basal (Tabela 3; equilibrio exato ~16,86 com Q=2,4)
    Pev_mmHg: float = 10.0         # pressao episcleral (sink do TM)
    Patm_mmHg: float = 0.0         # referencia atmosferica (IOP e "acima de")
    Q_prod_uL_min: float = Q_PROD_HUMAN_TABELA_UL_MIN  # calibrado: equilibrio em P0 (Tabela 3)

    # --- escoamento -----------------------------------------------------
    C_out_uL_min_mmHg: float = 0.28   # facilidade trabecular (humano ~0.28; coelho, ver nota abaixo)

    # Fracao do escoamento total que e uveoescleral (pressao-independente).
    # ATENCAO -- fortemente dependente de especie, nao use um unico valor
    # para todas:
    #   humano  : ~15-25% (Goel et al. 2010; faixa ampla relatada, 4-60%
    #             conforme metodo; 20% e um valor de meio de faixa razoavel)
    #   coelho  : ~3-8%  (Toris/Pederson; revisao de Uveoscleral outflow --
    #             musculo ciliar pouco desenvolvido faz essa via ser quase
    #             irrelevante nesta especie, MUITO diferente do humano)
    #   suino   : NAO CONFIRMADO -- nao assuma igual ao coelho. Meça no WP2.
    # Usar o valor humano (0.20) num cenario de coelho foi um erro real
    # cometido numa versao anterior deste arquivo (dava C_out=0.48 em vez
    # do C_out~0.55-0.60 correto) -- ver WP2 do plano de tese.
    frac_uveoscleral: float = 0.20

    # Hook para WP7 (facilidade dependente da pressao). Se None, C_out e constante.
    # Assinatura: C_of_P(P_mmHg) -> uL/min/mmHg
    C_of_P: Optional[Callable[[float], float]] = None

    # --- injecao intravitrea --------------------------------------------
    V_inj_uL: float = 50.0
    t_inj_start_min: float = 0.0
    t_inj_dur_min: float = 0.1        # 6 s = 0.1 min

    # --- refluxo ----------------------------------------------------------
    # "instant": perda discreta de volume no fim da injecao (relatorio WP0).
    # "poiseuille": legado — vazao continua numa janela pos-injecao.
    reflux_mode: str = "instant"  # none | instant | poiseuille (depreciado)
    reflux_enabled: bool = False  # legado: forca poiseuille com DeprecationWarning
    reflux_instant_dV_uL: float = 1.19
    R_reflux_Pa_s_per_m3: float = 6.216e11
    t_reflux_dur_min: float = 0.5

    # --- paracentese (Poiseuille) -----------------------------------------
    par_enabled: bool = False
    par_mode: str = "volume"  # volume (relatorio) | duration (depreciado)
    par_volume_uL: float = 50.0
    t_par_start_min: float = 2.0
    t_par_dur_min: float = 0.2
    R_par_Pa_s_per_m3: float = 6.216e11

    # --- hemodinamica para perfusao ---------------------------------------
    SBP_mmHg: float = 120.0
    DBP_mmHg: float = 70.0

    # --- janela de simulacao -----------------------------------------------
    t_end_min: float = 40.0


# ---------------------------------------------------------------------------
# 3. Termos de vazao
# ---------------------------------------------------------------------------

def Q_ivi(t: float, proto: Protocol) -> float:
    """Injecao em rampa constante durante [t_inj_start, t_inj_start+t_inj_dur]. uL/min."""
    t0, t1 = proto.t_inj_start_min, proto.t_inj_start_min + proto.t_inj_dur_min
    if t0 <= t <= t1 and t1 > t0:
        return proto.V_inj_uL / (t1 - t0)
    return 0.0


def Q_TM(P_mmHg: float, proto: Protocol) -> float:
    """Escoamento trabecular. Usa C_of_P (WP7) se fornecido, senao C_out constante."""
    C = proto.C_of_P(P_mmHg) if proto.C_of_P is not None else proto.C_out_uL_min_mmHg
    return C * (P_mmHg - proto.Pev_mmHg)


def Q_uveoscleral(proto: Protocol) -> float:
    """Fracao pressao-independente do escoamento total, calibrada no equilibrio basal."""
    Q_total_basal = proto.Q_prod_uL_min
    return proto.frac_uveoscleral * Q_total_basal


def _poiseuille_uL_per_min(P_mmHg: float, Patm_mmHg: float, R_Pa_s_per_m3: float) -> float:
    """Converte (P-Patm) em vazao uL/min atraves de uma resistencia hidraulica em Pa.s/m3."""
    dP_Pa = (P_mmHg - Patm_mmHg) * MMHG_TO_PA
    Q_m3_s = dP_Pa / R_Pa_s_per_m3
    return Q_m3_s * 1e9 * 60.0   # m3/s -> uL/min


def _reflux_mode(proto: Protocol) -> str:
    if proto.reflux_enabled:
        if proto.reflux_mode in ("none", "instant"):
            return "poiseuille"
    mode = proto.reflux_mode or "none"
    return mode if mode != "none" else "none"


def _warn_legacy_protocol_once(proto: Protocol) -> None:
    """Avisos de depreciacao (uma vez por combinacao relevante)."""
    if getattr(proto, "_legacy_warned", False):
        return
    if proto.reflux_enabled:
        warnings.warn(
            "Protocol.reflux_enabled esta depreciado; use reflux_mode='poiseuille'.",
            DeprecationWarning,
            stacklevel=3,
        )
    if proto.reflux_mode == "poiseuille":
        warnings.warn(
            "reflux_mode='poiseuille' esta depreciado; o relatorio usa reflux_mode='instant'.",
            DeprecationWarning,
            stacklevel=3,
        )
    if proto.par_enabled and proto.par_mode == "duration":
        warnings.warn(
            "par_mode='duration' esta depreciado; use par_mode='volume'.",
            DeprecationWarning,
            stacklevel=3,
        )
    object.__setattr__(proto, "_legacy_warned", True)


def Q_reflux(t: float, P_mmHg: float, proto: Protocol) -> float:
    if _reflux_mode(proto) != "poiseuille":
        return 0.0
    t0 = proto.t_inj_start_min
    t1 = t0 + proto.t_inj_dur_min + proto.t_reflux_dur_min
    if t0 <= t <= t1:
        return _poiseuille_uL_per_min(P_mmHg, proto.Patm_mmHg, proto.R_reflux_Pa_s_per_m3)
    return 0.0


def Q_paracentese(t: float, P_mmHg: float, proto: Protocol) -> float:
    if not proto.par_enabled or proto.par_mode == "volume":
        return 0.0
    t0 = proto.t_par_start_min
    t1 = t0 + proto.t_par_dur_min
    if t0 <= t <= t1:
        return _poiseuille_uL_per_min(P_mmHg, proto.Patm_mmHg, proto.R_par_Pa_s_per_m3)
    return 0.0


def needle_hydraulic_resistance(a_mm: float, L_mm: float, mu_mPa_s: float) -> float:
    """Poiseuille resistance [Pa·s/m³] for circular channel (radius a_mm)."""
    a = a_mm * 1e-3
    L = L_mm * 1e-3
    mu = mu_mPa_s * 1e-3
    return float(8.0 * mu * L / (np.pi * a**4))


def equilibrium_q_prod(
    P0_mmHg: float,
    Pev_mmHg: float,
    C_out: float,
    frac_uv: float,
) -> float:
    """Q_prod que fecha o equilibrio em P0 com C_out e frac_uv constantes."""
    return float(C_out * (P0_mmHg - Pev_mmHg) / (1.0 - frac_uv))


def protocol_humano_relatorio(**kwargs) -> Protocol:
    """Protocolo humano alinhado ao wp0.tex (Tabela 3 + refluxo instantaneo + par por volume)."""
    base = dict(
        P0_mmHg=P0_HUMAN_REPORT_MMHG,
        Pev_mmHg=10.0,
        Q_prod_uL_min=Q_PROD_HUMAN_TABELA_UL_MIN,
        C_out_uL_min_mmHg=0.28,
        frac_uveoscleral=0.20,
        V_inj_uL=50.0,
        t_inj_dur_min=0.1,
        t_end_min=40.0,
        reflux_mode="instant",
        reflux_instant_dV_uL=1.19,
        par_mode="volume",
        par_volume_uL=50.0,
        R_par_Pa_s_per_m3=needle_hydraulic_resistance(0.0795, 13.0, 0.75),
    )
    base.update(kwargs)
    return Protocol(**base)


def protocol_coelho_relatorio(**kwargs) -> Protocol:
    base = dict(
        P0_mmHg=26.7,
        Pev_mmHg=15.5,
        Q_prod_uL_min=Q_PROD_RABBIT_TABELA_UL_MIN,
        C_out_uL_min_mmHg=0.26,
        frac_uveoscleral=0.05,
        V_inj_uL=50.0,
        t_inj_dur_min=0.1,
        t_end_min=40.0,
        reflux_mode="instant",
        reflux_instant_dV_uL=1.19,
        par_mode="volume",
    )
    base.update(kwargs)
    return Protocol(**base)


def simulate_with_instant_reflux(
    proto: Protocol,
    pv,
    reflux_dV_uL: float | None = None,
    n_points: int = 4000,
):
    """Integrate ODE; perda discreta de volume no fim da IVI (descontinuidade, nao Poiseuille)."""
    dV = proto.reflux_instant_dV_uL if reflux_dV_uL is None else float(reflux_dV_uL)
    p2 = dataclasses.replace(
        proto,
        reflux_mode="instant",
        reflux_enabled=False,
        reflux_instant_dV_uL=dV,
    )
    return simulate(p2, pv, n_points=n_points)


def _integrate_segment(t0: float, t1: float, v0: float, pv, proto: Protocol, n_seg: int):
    t_eval = np.linspace(t0, t1, n_seg)
    sol = solve_ivp(
        _rhs,
        (t0, t1),
        [v0],
        t_eval=t_eval,
        args=(pv, proto),
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
        max_step=(t1 - t0) / 10 if t1 > t0 else None,
    )
    if not sol.success:
        raise RuntimeError(f"Integracao falhou [{t0},{t1}]: {sol.message}")
    return sol.t, sol.y[0]


def simulate_paracentesis_by_volume(
    proto: Protocol,
    pv,
    *,
    volume_uL: float | None = None,
    t_start_min: float | None = None,
    R_par: float | None = None,
    t_end_min: float | None = None,
    t_begin_min: float | None = None,
    dt_min: float = 0.002,
):
    """Paracentese ate retirar ``volume_uL`` (regra de volume, nao janela fixa)."""
    vol = float(volume_uL if volume_uL is not None else proto.par_volume_uL)
    t0 = float(t_start_min if t_start_min is not None else proto.t_par_start_min)
    r_par = float(R_par if R_par is not None else proto.R_par_Pa_s_per_m3)
    t_end = float(t_end_min if t_end_min is not None else proto.t_end_min)
    t_begin = float(t_begin_min if t_begin_min is not None else min(0.0, t0))

    t_all: list[float] = []
    v_all: list[float] = []
    v_curr = 0.0
    removed = 0.0
    t_curr = t_begin

    # Phase 1: before paracentesis
    if t0 > t_curr + 1e-12:
        ts, vs = _integrate_segment(t_curr, t0, v_curr, pv, proto, max(40, int(400 * (t0 - t_curr))))
        if t_all:
            t_all.extend(ts[1:])
            v_all.extend(vs[1:])
        else:
            t_all.extend(ts)
            v_all.extend(vs)
        v_curr = float(vs[-1])
        t_curr = t0

    # Phase 2: paracentesis until volume target
    while removed < vol - 1e-9 and t_curr < t_end:
        p = pv.P(v_curr)
        q = _poiseuille_uL_per_min(p, proto.Patm_mmHg, r_par)
        if q <= 1e-12:
            break
        step = min(dt_min, (vol - removed) / q)
        step = min(step, t_end - t_curr)
        v_curr -= q * step
        removed += q * step
        t_curr += step
        t_all.append(t_curr)
        v_all.append(v_curr)

    # Phase 3: remainder
    if t_curr < t_end - 1e-12:
        ts, vs = _integrate_segment(t_curr, t_end, v_curr, pv, proto, max(40, int(400 * (t_end - t_curr))))
        t_all.extend(ts[1:])
        v_all.extend(vs[1:])

    t_arr = np.array(t_all)
    v_arr = np.array(v_all)
    p_arr = np.array([pv.P(x) for x in v_arr])
    meta = {"par_duration_min": t_curr - t0, "volume_removed_uL": removed}
    return t_arr, v_arr, p_arr, meta


@dataclass
class Wp0Timeline:
    """Cenario WP0 alinhado ao relatorio (refluxo instantaneo + par por volume)."""

    t_begin_min: float = 0.0
    t_end_min: float = 40.0
    par_start_min: float | None = None
    par_volume_uL: float = 50.0
    instant_reflux_uL: float = 1.19
    dt_min: float = 2.0e-4  # ~12 ms


def _rhs_timeline(
    t: float,
    y: np.ndarray,
    pv,
    proto: Protocol,
    timeline: Wp0Timeline,
    r_par: float,
) -> list[float]:
    """Estado y = [V, volume_par_removido]; refluxo instantaneo e aplicado entre segmentos."""
    v = float(y[0])
    m_par = float(y[1])
    p = pv.P(v)
    par_on = (
        timeline.par_start_min is not None
        and t >= timeline.par_start_min - 1e-12
        and m_par < timeline.par_volume_uL - 1e-12
    )
    q_par = _poiseuille_uL_per_min(p, proto.Patm_mmHg, r_par) if par_on else 0.0
    dV = (
        proto.Q_prod_uL_min
        + Q_ivi(t, proto)
        - Q_TM(p, proto)
        - Q_uveoscleral(proto)
        - q_par
    )
    return [dV, q_par]


def _make_par_volume_event(volume_uL: float):
    def par_volume_event(_t: float, y: np.ndarray, *_args) -> float:
        return float(y[1]) - volume_uL

    par_volume_event.terminal = True
    par_volume_event.direction = 1
    return par_volume_event


def lobue_return_metrics(
    *,
    p0_mmHg: float = P0_HUMAN_REPORT_MMHG,
    tolerance_mmHg: float = 4.0,
    rtol: float = 1e-8,
    atol: float = 1e-10,
) -> dict:
    """LoBue (wp0.tex §4.3): retorno ao basal, delta-P @ 10 min, excesso pos-pico."""
    proto = protocol_humano_relatorio()
    pv = FriedenwaldPV(Kf_per_uL=0.00581, P0_mmHg=p0_mmHg, V0_uL=0.0)
    tl = Wp0Timeline(t_begin_min=0.0, t_end_min=60.0, par_start_min=None, instant_reflux_uL=1.19)
    t, _, p, meta = simulate_wp0_timeline(proto, pv, tl, rtol=rtol, atol=atol)
    i_peak = int(np.argmax(p))
    p_peak = float(p[i_peak])
    t_peak = float(t[i_peak])
    excess_peak = p_peak - p0_mmHg
    after_peak = (t > t_peak) & (np.abs(p - p0_mmHg) < tolerance_mmHg)
    idx = np.where(after_peak)[0]
    t_return_min = float(t[int(idx[0])]) if idx.size else float("nan")

    def excess_at(t_min: float) -> float:
        return float(np.interp(t_min, t, p) - p0_mmHg)

    return {
        "P0_ref_mmHg": p0_mmHg,
        "P_peak_mmHg": p_peak,
        "t_peak_min": t_peak,
        "t_return_min": t_return_min,
        "delta_P_at_10min_mmHg": excess_at(10.0),
        "delta_P_at_600s_mmHg": excess_at(10.0),
        "excess_above_P0_at_10min_mmHg": excess_at(10.0),
        "excess_above_P0_at_30min_mmHg": excess_at(30.0),
        "excess_above_P0_at_50min_mmHg": excess_at(50.0),
        "drop_from_peak_at_10min_mmHg": float(np.interp(10.0, t, p) - p_peak),
        "drop_from_peak_at_30min_mmHg": float(np.interp(30.0, t, p) - p_peak),
        "drop_from_peak_at_50min_mmHg": float(np.interp(50.0, t, p) - p_peak),
        "fraction_excess_dissipated_at_10min": (
            float(-(np.interp(10.0, t, p) - p_peak) / excess_peak) if excess_peak > 0 else float("nan")
        ),
        "fraction_excess_dissipated_at_50min": (
            float(-(np.interp(50.0, t, p) - p_peak) / excess_peak) if excess_peak > 0 else float("nan")
        ),
        "t_origin": "t=0 injection start",
        "reflux_on": True,
        "dynamic_peak_meta_mmHg": float(meta["P_peak_mmHg"]),
    }


def simulate_wp0_timeline(
    proto: Protocol,
    pv,
    timeline: Wp0Timeline,
    *,
    r_par: float | None = None,
    rtol: float = 1e-8,
    atol: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Paracentese por volume + refluxo instantaneo como descontinuidade no fim da IVI."""
    _warn_legacy_protocol_once(proto)
    r_par_use = float(r_par if r_par is not None else proto.R_par_Pa_s_per_m3)
    t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min
    reflux_dV = (
        timeline.instant_reflux_uL
        if _reflux_mode(proto) == "instant"
        else 0.0
    )

    meta: dict = {
        "par_duration_min": float("nan"),
        "par_volume_removed_uL": 0.0,
        "reflux_applied_uL": 0.0,
        "P_peak_mmHg": float("nan"),
        "t_peak_min": float("nan"),
    }

    v_curr, m_curr = 0.0, 0.0
    t_all: list[float] = []
    v_all: list[float] = []

    bp = {
        timeline.t_begin_min,
        timeline.t_end_min,
        proto.t_inj_start_min,
        t_inj_end,
    }
    if timeline.par_start_min is not None:
        bp.add(timeline.par_start_min)
    seg_ends = sorted(x for x in bp if timeline.t_begin_min - 1e-15 <= x <= timeline.t_end_min + 1e-15)
    if seg_ends[0] != timeline.t_begin_min:
        seg_ends = [timeline.t_begin_min] + seg_ends
    if seg_ends[-1] != timeline.t_end_min:
        seg_ends.append(timeline.t_end_min)

    for i in range(len(seg_ends) - 1):
        ta, tb = seg_ends[i], seg_ends[i + 1]
        if tb <= ta + 1e-15:
            continue
        apply_reflux_here = abs(tb - t_inj_end) < 1e-12 and ta < t_inj_end - 1e-15
        par_event_segment = (
            timeline.par_start_min is not None
            and np.isnan(meta["par_duration_min"])
            and m_curr < timeline.par_volume_uL - 1e-12
            and tb > timeline.par_start_min - 1e-12
        )
        n_seg = max(80, int(1500 * (tb - ta)))
        t_eval = np.linspace(ta, tb, n_seg)
        events = (
            _make_par_volume_event(timeline.par_volume_uL) if par_event_segment else None
        )
        sol = solve_ivp(
            _rhs_timeline,
            (ta, tb),
            [v_curr, m_curr],
            t_eval=t_eval,
            args=(pv, proto, timeline, r_par_use),
            method="RK45",
            rtol=rtol,
            atol=atol,
            max_step=(tb - ta) / 8 if tb > ta else None,
            events=events,
        )
        if not sol.success:
            raise RuntimeError(f"simulate_wp0_timeline falhou [{ta},{tb}]: {sol.message}")

        def _append_sol(sol_obj, first_seg: bool) -> None:
            if first_seg:
                t_all.extend(sol_obj.t.tolist())
                v_all.extend(sol_obj.y[0].tolist())
            else:
                t_all.extend(sol_obj.t[1:].tolist())
                v_all.extend(sol_obj.y[0][1:].tolist())

        event_hit = events is not None and sol.t_events and len(sol.t_events[0]) > 0
        if event_hit and timeline.par_start_min is not None:
            t_done = float(sol.t_events[0][0])
            meta["par_duration_min"] = t_done - timeline.par_start_min
            v_curr = float(sol.y_events[0][0][0])
            m_curr = float(timeline.par_volume_uL)
            _append_sol(sol, i == 0)
            if t_done < tb - 1e-12:
                n2 = max(40, int(800 * (tb - t_done)))
                t_eval2 = np.linspace(t_done, tb, n2)
                sol2 = solve_ivp(
                    _rhs_timeline,
                    (t_done, tb),
                    [v_curr, m_curr],
                    t_eval=t_eval2,
                    args=(pv, proto, timeline, r_par_use),
                    method="RK45",
                    rtol=rtol,
                    atol=atol,
                    max_step=(tb - t_done) / 8,
                )
                if not sol2.success:
                    raise RuntimeError(f"simulate_wp0_timeline pos-par [{t_done},{tb}]: {sol2.message}")
                _append_sol(sol2, False)
                v_curr = float(sol2.y[0, -1])
                m_curr = float(sol2.y[1, -1])
            if apply_reflux_here and reflux_dV > 0:
                v_curr -= reflux_dV
                meta["reflux_applied_uL"] = reflux_dV
                t_all.append(t_inj_end + 1e-10)
                v_all.append(v_curr)
            continue

        _append_sol(sol, i == 0)
        v_curr = float(sol.y[0, -1])
        m_curr = float(sol.y[1, -1])

        if apply_reflux_here and reflux_dV > 0:
            v_curr -= reflux_dV
            meta["reflux_applied_uL"] = reflux_dV
            t_all.append(t_inj_end + 1e-10)
            v_all.append(v_curr)

    meta["par_volume_removed_uL"] = float(min(m_curr, timeline.par_volume_uL))

    t_arr = np.array(t_all)
    v_arr = np.array(v_all)
    p_arr = np.array([pv.P(x) for x in v_arr])
    i_peak = int(np.argmax(p_arr))
    meta["P_peak_mmHg"] = float(p_arr[i_peak])
    meta["t_peak_min"] = float(t_arr[i_peak])
    return t_arr, v_arr, p_arr, meta


# ---------------------------------------------------------------------------
# 4. ODE e integracao por segmentos
# ---------------------------------------------------------------------------

def _rhs(t: float, y: np.ndarray, pv, proto: Protocol) -> list:
    V = y[0]
    P = pv.P(V)
    dVdt = (
        proto.Q_prod_uL_min
        + Q_ivi(t, proto)
        - Q_TM(P, proto)
        - Q_uveoscleral(proto)
        - Q_reflux(t, P, proto)
        - Q_paracentese(t, P, proto)
    )
    return [dVdt]


def simulate(proto: Protocol, pv, n_points: int = 4000):
    """
    Integra a ODE por segmentos (separados nos pontos onde algum termo
    liga/desliga), para evitar que o integrador tropece em descontinuidades.
    Refluxo ``instant`` aplica salto de volume no fim da injecao (t = 6 s).
    Retorna t (min), V (uL, relativo a V0=0 no t=0) e P=IOP (mmHg).
    """
    _warn_legacy_protocol_once(proto)
    mode = _reflux_mode(proto)
    t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min
    reflux_dV = proto.reflux_instant_dV_uL if mode == "instant" else 0.0

    breakpoints = {0.0, proto.t_end_min}
    breakpoints.add(proto.t_inj_start_min)
    breakpoints.add(t_inj_end)
    if mode == "poiseuille":
        breakpoints.add(t_inj_end + proto.t_reflux_dur_min)
    if proto.par_enabled and proto.par_mode == "duration":
        breakpoints.add(proto.t_par_start_min)
        breakpoints.add(proto.t_par_start_min + proto.t_par_dur_min)
    bp = sorted(b for b in breakpoints if 0.0 <= b <= proto.t_end_min)

    t_all, V_all = [], []
    V_curr = 0.0
    for i in range(len(bp) - 1):
        t0, t1 = bp[i], bp[i + 1]
        if t1 <= t0:
            continue
        n_seg = max(20, int(n_points * (t1 - t0) / proto.t_end_min))
        t_eval = np.linspace(t0, t1, n_seg)
        sol = solve_ivp(
            _rhs,
            (t0, t1),
            [V_curr],
            t_eval=t_eval,
            args=(pv, proto),
            method="RK45",
            rtol=1e-8,
            atol=1e-10,
            max_step=(t1 - t0) / 10 if t1 > t0 else None,
        )
        if not sol.success:
            raise RuntimeError(f"Integracao falhou no segmento [{t0},{t1}]: {sol.message}")
        if i > 0:
            t_all.extend(sol.t[1:])
            V_all.extend(sol.y[0][1:])
        else:
            t_all.extend(sol.t)
            V_all.extend(sol.y[0])
        V_curr = float(sol.y[0][-1])
        if reflux_dV > 0 and abs(t1 - t_inj_end) < 1e-12:
            V_curr -= reflux_dV
            t_all.append(t_inj_end + 1e-10)
            V_all.append(V_curr)

    t_arr = np.array(t_all)
    V_arr = np.array(V_all)
    P_arr = np.array([pv.P(v) for v in V_arr])
    return t_arr, V_arr, P_arr


# ---------------------------------------------------------------------------
# 5. Perfusao e dose isquemica  (eixo (d) do plano de tese)
# ---------------------------------------------------------------------------

def perfusion_metrics(t_min: np.ndarray, IOP_mmHg: np.ndarray, proto: Protocol,
                       OPP_crit_mmHg: float = 50.0,
                       mopp_factor: float = 2.0 / 3.0):
    """
    MAP = DBP + (SBP-DBP)/3
    MOPP(t) = mopp_factor * MAP - IOP(t)      (convencao usual: 2/3)

    Retorna dict com MOPP(t), dose isquemica I (mmHg.min) acima do
    deficit em relacao a OPP_crit, e tempos acima de limiares de IOP.

    AVISO: OPP_crit e mopp_factor sao parametros incertos da literatura.
    Sempre reporte I(OPP_crit) como funcao, nao como numero fixo -- ver
    plano de tese, WP4.2.
    """
    MAP = proto.DBP_mmHg + (proto.SBP_mmHg - proto.DBP_mmHg) / 3.0
    MOPP = mopp_factor * MAP - IOP_mmHg

    deficit = np.clip(OPP_crit_mmHg - MOPP, 0.0, None)
    I_mmHg_min = _trapz(deficit, t_min)

    def time_above(th):
        mask = IOP_mmHg > th
        if not mask.any():
            return 0.0
        return _trapz(mask.astype(float), t_min)

    return {
        "MAP_mmHg": MAP,
        "MOPP": MOPP,
        "MOPP_min_mmHg": float(MOPP.min()),
        "I_mmHg_min": float(I_mmHg_min),
        "T_above_30_min": time_above(30.0),
        "T_above_40_min": time_above(40.0),
        "T_above_50_min": time_above(50.0),
        "IOP_peak_mmHg": float(IOP_mmHg.max()),
        "t_peak_min": float(t_min[np.argmax(IOP_mmHg)]),
    }


def ischemic_dose_curve(t_min: np.ndarray, IOP_mmHg: np.ndarray, proto: Protocol,
                         OPP_crit_range=(30, 40, 50, 60)):
    """Dose isquemica como funcao do limiar assumido -- use isto no relatorio, nao um numero so."""
    out = {}
    for th in OPP_crit_range:
        m = perfusion_metrics(t_min, IOP_mmHg, proto, OPP_crit_mmHg=th)
        out[th] = m["I_mmHg_min"]
    return out


# ---------------------------------------------------------------------------
# 6. Regra de bolso: volume de paracentese para atingir uma IOP-alvo
# ---------------------------------------------------------------------------

def volume_para_alvo(pv, P_atual_mmHg: float, P_alvo_mmHg: float) -> float:
    """
    Delta V (uL, positivo = retirar) para levar a IOP de P_atual a P_alvo,
    usando a MESMA curva P(V) da simulacao (nao um K generico -- ver o
    erro de inconsistencia interna corrigido no plano de tese, WP5.3).
    """
    V_atual = pv.V_of_P(P_atual_mmHg)
    V_alvo = pv.V_of_P(P_alvo_mmHg)
    return V_atual - V_alvo


# ---------------------------------------------------------------------------
# 7. Estimador rapido de K a partir de biometria (nomograma, WP1.4/WP6)
# ---------------------------------------------------------------------------

def K_de_biometria(comprimento_axial_mm: float, espessura_esclera_mm: float,
                    E_Pa: float = 3.0e6, nu: float = 0.47) -> float:
    """
    K (mmHg/uL) a partir da formula de casca fina, usando o comprimento
    axial como proxy do raio equatorial (R ~ AL/2, aproximacao grosseira
    para uma esfera -- o olho real e oblato/prolato, ver limitacoes do
    plano). Uso: gerar a hipotese H1 antes de qualquer FEA ou dado.
    """
    R_m = (comprimento_axial_mm / 2.0) * 1e-3
    t_m = espessura_esclera_mm * 1e-3
    K_Pa_m3 = t_m * E_Pa / (2 * np.pi * R_m**4 * (1 - nu))
    return K_Pa_m3 * 1e-9 / MMHG_TO_PA


# ---------------------------------------------------------------------------
# 8. Exemplo de uso / cenarios
# ---------------------------------------------------------------------------

def _print_summary(nome: str, t, V, P, proto: Protocol):
    m = perfusion_metrics(t, P, proto, OPP_crit_mmHg=50.0)
    print(f"\n--- {nome} ---")
    print(f"  IOP basal            : {proto.P0_mmHg:.1f} mmHg")
    print(f"  IOP pico             : {m['IOP_peak_mmHg']:.1f} mmHg  em t={m['t_peak_min']:.2f} min")
    print(f"  tempo acima de 30 mmHg: {m['T_above_30_min']:.2f} min")
    print(f"  tempo acima de 40 mmHg: {m['T_above_40_min']:.2f} min")
    print(f"  tempo acima de 50 mmHg: {m['T_above_50_min']:.2f} min")
    print(f"  MOPP minima          : {m['MOPP_min_mmHg']:.1f} mmHg")
    print(f"  dose isquemica (OPPcrit=50): {m['I_mmHg_min']:.1f} mmHg.min")
    curva = ischemic_dose_curve(t, P, proto)
    print(f"  dose isquemica vs limiar: " +
          ", ".join(f"OPPcrit={k}->{v:.1f}" for k, v in curva.items()))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    print(
        "goldmann_iop_solver: defaults alinhados ao relatorio (instant + volume, Q_prod=2,4).\n"
        "Executando verify + wp0_report (mesmo fluxo que ./Allrun)..."
    )
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    from verify_wp0_standards import main as verify_main
    from wp0_report import main as report_main

    code = verify_main()
    if code != 0:
        raise SystemExit(code)
    raise SystemExit(report_main())
