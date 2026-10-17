"""WP4.1 — protocolo de referência alinhado ao WP0."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for p in (str(WP4), str(WP0)):
    if p not in sys.path:
        sys.path.insert(0, p)

from goldmann_iop_solver import _reflux_mode, protocol_humano_relatorio  # noqa: E402
from run_wp41 import protocolo_referencia  # noqa: E402


def test_protocolo_referencia_refluxo_instantaneo_wp0():
    """WP4.1/4.2 numérico: mesmo protocolo humano do WP0 (refluxo ligado, sem paracentese)."""
    proto = protocolo_referencia()
    ref = protocol_humano_relatorio(
        par_enabled=False,
        t_end_min=40.0,
        SBP_mmHg=proto.SBP_mmHg,
        DBP_mmHg=proto.DBP_mmHg,
    )
    assert _reflux_mode(proto) == "instant"
    assert proto.reflux_instant_dV_uL == pytest.approx(1.19)
    assert not proto.par_enabled
    assert proto.V_inj_uL == 50.0
    assert proto.reflux_mode == ref.reflux_mode
    assert proto.reflux_instant_dV_uL == ref.reflux_instant_dV_uL
    assert proto.Q_prod_uL_min == ref.Q_prod_uL_min
