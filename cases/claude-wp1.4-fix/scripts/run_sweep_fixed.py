#!/usr/bin/env python3
"""WP1.4 corrigido — varredura LHS de 300 casos, sem constantes inventadas.

Diferencas em relacao a cases/wp1.4/sweep_full/scripts/run_sweep.py:

  1. Usa case_model_fixed: R = AL/2, sem deslocamentos por ACD/cristalino.
  2. NAO aplica o fator 1,085 de vitrectomia aos dV.
  3. PERSISTE a curva P-V de cada caso (o original descartava `pv_curve` ao salvar,
     e com isso a grandeza da H1 — dIOP para 50 uL fixos — nao ficava disponivel).
  4. Reporta dIOP em 50 uL por interpolacao da curva P-V (grandeza da H1).
  5. Reporta K basal de duas formas (primeiro incremento e ajuste linear nos tres
     primeiros pontos), para mostrar que K nao depende do tamanho do passo.
  6. n_bands desacoplado de ne.

Uso no Docker:
    docker compose run --rm fsi bash -lc \
      'pip install numpy --break-system-packages && \
       cd /simulation/claude-wp1.4-fix/scripts && python3 run_sweep_fixed.py --resume'
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = ROOT.parent
WP12 = CASES / "wp1.2" / "scripts"
SWEEPFULL = CASES / "wp1.4" / "sweep_full" / "scripts"

sys.path.insert(0, str(WP12))
sys.path.insert(0, str(HERE))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402

from case_model_fixed import P0_MMHG, p_targets, resolve_case  # noqa: E402
from gen_mesh_bands import write_mesh_banded  # noqa: E402

# write_deck_vt do Composer e reaproveitado sem alteracao (esta correto).
sys.path.append(str(SWEEPFULL))
from write_deck_vt import write_deck_variable_t  # noqa: E402

NE_DEFAULT = 8
N_BANDS_DEFAULT = None  # None = uma faixa por anel de elementos (ver gen_mesh_bands)
V_TARGET_UL = 50.0  # volume clinico da IVI padrao (plano de tese, WP0)


def _pv_arrays(pv_rows: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    rows = sorted(pv_rows, key=lambda r: r["p_mmhg"])
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    v = v - v[0]  # dV medido a partir do estado basal
    return p, v


def _k_basal_first(p: np.ndarray, v: np.ndarray) -> float | None:
    if len(p) < 2 or v[1] <= 0:
        return None
    return float((p[1] - p[0]) / (v[1] - v[0]))


def _k_basal_fit(p: np.ndarray, v: np.ndarray, n: int = 3) -> float | None:
    """Inclinacao dP/dV pelos n primeiros pontos (robustez ao tamanho do passo)."""
    m = min(n + 1, len(p))
    if m < 3 or v[m - 1] <= 0:
        return None
    slope = np.polyfit(v[:m], p[:m], 1)[0]
    return float(slope)


def _dp_at_volume(p: np.ndarray, v: np.ndarray, v_target: float) -> tuple[float | None, bool]:
    """dIOP acima do basal para v_target uL. Retorna (valor, dentro_da_faixa)."""
    if v[-1] < v_target:
        return None, False  # exigiria extrapolar acima do teto de 50 mmHg
    return float(np.interp(v_target, v, p) - p[0]), True


def run_one_case(row: dict, work: Path, ne: int, n_bands: int, p_final: float) -> dict:
    cid = row["case_id"]
    resolved = resolve_case(row, n_bands=n_bands)
    t0 = time.time()
    try:
        mesh_path = work / f"{cid}_mesh.inp"
        mesh_meta = write_mesh_banded(
            mesh_path,
            resolved["R_mm"],
            resolved["t_equatorial_mm"],
            resolved["t_posterior_mm"],
            ne,
            2,
            cid,
            theta_min_deg=resolved["theta_min_deg"],
            reduced=True,
            n_bands=n_bands,
        )
        mu1 = resolved["mu1_MPa"]
        params = {
            "mu1_MPa": mu1,
            "alpha1": resolved["alpha1"],
            "D1": d1_from_ogden_mu1(mu1),
            "d1_tied_mu1": True,
        }
        deck_path = work / f"{cid}.inp"
        write_deck_variable_t(
            deck_path,
            mesh_path.name,
            mesh_meta["band_thickness_mm"],
            "ogden1",
            params,
            p_targets(p_final, p0=P0_MMHG),
            label=f"wp1.4 corrigido {cid}",
            p0_mmhg=P0_MMHG,
        )
        frd = run_ccx(deck_path, clean=False)  # manter .frd para reanalise
        pv_rows = extract_pv(deck_path, frd, resolved["R_mm"], p0_mmhg=P0_MMHG)

        p, v = _pv_arrays(pv_rows)
        dp50, in_range = _dp_at_volume(p, v, V_TARGET_UL)
        k_first = _k_basal_first(p, v)
        k_fit = _k_basal_fit(p, v)

        return {
            **{k: row.get(k) for k in row},
            **resolved,
            "status": "OK",
            "V_max_uL": round(float(v[-1]), 3),
            "P_max_mmHg": round(float(p[-1]), 3),
            "K_basal_first_mmHg_per_uL": round(k_first, 6) if k_first else None,
            "K_basal_fit3_mmHg_per_uL": round(k_fit, 6) if k_fit else None,
            "dIOP_at_50uL_mmHg": round(dp50, 3) if dp50 is not None else None,
            "dIOP_at_50uL_in_range": in_range,
            "n_bands_effective": mesh_meta["n_bands_effective"],
            "ne": ne,
            "elapsed_s": round(time.time() - t0, 1),
            "pv_curve": [
                {"p_mmhg": round(float(pi), 4), "dV_uL": round(float(vi), 4)}
                for pi, vi in zip(p, v)
            ],
        }
    except Exception as exc:
        return {
            **row,
            **resolved,
            "status": f"FAIL: {type(exc).__name__}: {exc}",
            "elapsed_s": round(time.time() - t0, 1),
        }


def load_existing(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    return {r["case_id"]: r for r in json.loads(path.read_text()) if r.get("status") == "OK"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--samples",
        type=Path,
        default=CASES / "wp1.4" / "sweep_full" / "sweep_samples.csv",
        help="mesmo desenho LHS do sweep_full, para comparacao direta",
    )
    ap.add_argument("--out", type=Path, default=ROOT / "output_sweep_fixed")
    ap.add_argument("--ne", type=int, default=NE_DEFAULT)
    ap.add_argument("--n-bands", type=int, default=N_BANDS_DEFAULT,
                    help="None (padrao) = uma faixa por anel, espessura por media de area")
    ap.add_argument("--p-final", type=float, default=50.0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    args = ap.parse_args()

    with open(args.samples, newline="") as fh:
        samples = list(csv.DictReader(fh))
    end = args.end if args.end is not None else len(samples)
    samples = samples[args.start : end]

    work = args.out / "ccx_runs"
    work.mkdir(parents=True, exist_ok=True)
    results_path = args.out / "sweep_results_fixed.json"

    existing = load_existing(results_path) if args.resume else {}
    if existing:
        print(f"Resume: {len(existing)} casos OK ignorados")

    results = list(existing.values())
    n_new = n_fail = 0
    for i, row in enumerate(samples):
        cid = row["case_id"]
        if cid in existing:
            continue
        print(f"[{args.start + i + 1}/{args.start + len(samples)}] {cid}")
        res = run_one_case(row, work, args.ne, args.n_bands, args.p_final)
        results.append(res)
        n_new += 1
        if res["status"] == "OK":
            dp = res["dIOP_at_50uL_mmHg"]
            print(
                f"  OK  K={res['K_basal_first_mmHg_per_uL']}  "
                f"V_max={res['V_max_uL']:.1f} uL  "
                f"dIOP@50uL={dp if dp is not None else 'fora da faixa'}  "
                f"({res['elapsed_s']:.0f}s)"
            )
        else:
            n_fail += 1
            print(f"  {res['status']}")
        if n_new % 10 == 0:
            results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    n_ok = sum(1 for r in results if r.get("status") == "OK")
    print(f"\nFim: {n_ok}/{len(results)} OK, {n_fail} falhas novas")
    print(f"Resultados: {results_path}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
