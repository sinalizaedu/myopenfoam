"""WP4.6 — paracentese × MOPP/dose."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for p in (str(WP4), str(WP0)):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_wp46_paracentese import simular_par  # noqa: E402


def test_sem_par_alinha_wp41_friedenwald():
    r = simular_par("sem_par", None, 0.0)
    assert r["IOP_pico_mmHg"] == pytest.approx(32.90, abs=0.05)
    assert r["T_abaixo_40_min"] == pytest.approx(10.98, abs=0.15)
    assert r["I_evt_OPP_40"] == pytest.approx(42.7, abs=1.0)


def test_profilatica_zera_dose_evt():
    r = simular_par("profilatica", -0.5, -0.5)
    assert r["IOP_pico_mmHg"] == pytest.approx(17.1, abs=0.1)
    assert r["T_abaixo_40_min"] == pytest.approx(0.0, abs=1e-6)
    assert r["I_evt_OPP_40"] == pytest.approx(0.0, abs=1e-6)


def test_json_oficial_existe():
    p = WP4 / "output_wp46" / "wp46_paracentese.json"
    if not p.is_file():
        pytest.skip("rode run_wp46_paracentese.py")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert len(data) == 4
