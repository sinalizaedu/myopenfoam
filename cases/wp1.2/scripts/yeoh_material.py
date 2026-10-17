#!/usr/bin/env python3
"""Validated Yeoh-2 material from E3 (shared by E5/E6)."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_FIT = Path(__file__).resolve().parents[1] / "output_exploration" / "e3_yeoh" / "fit_results.json"
FALLBACK_FIT = Path(__file__).resolve().parents[2] / "wp1_octant" / "output" / "wp1.2-yeoh" / "fit_results.json"

P0_MMHG = 16.9
P_FINAL_MMHG = 50.0
N_LOAD_STEPS = 16


def load_yeoh_params(fit_path: Path | None = None) -> dict:
    for p in (fit_path, DEFAULT_FIT, FALLBACK_FIT):
        if p and p.is_file():
            data = json.loads(p.read_text())
            sel = data.get("fit") or data.get("selected")
            return dict(sel["params"])
    raise FileNotFoundError("No Yeoh fit_results.json (run E3 first)")


def p_targets(p_final: float = P_FINAL_MMHG, n_steps: int = N_LOAD_STEPS) -> list[float]:
    return [P0_MMHG + (p_final - P0_MMHG) * i / n_steps for i in range(1, n_steps + 1)]
