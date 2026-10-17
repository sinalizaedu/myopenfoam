#!/usr/bin/env python3
"""WP1.4 — Runner da varredura paramétrica completa.

Lê o CSV de amostras LHS (gerado por generate_lhs_samples.py) e roda
cada caso no CalculiX usando o pipeline existente (ogden_forward_run).

Uso:
    python3 run_sweep_claude.py
    python3 run_sweep_claude.py --samples sweep_samples.csv --resume
    python3 run_sweep_claude.py --samples sweep_samples.csv --start 100 --end 200

O --resume pula casos que já têm resultado em sweep_results.json.
O --start/--end permite rodar em lotes (útil em cluster/HPC).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Ajustar caminhos conforme a estrutura do repo
CLAUDE_WP14 = HERE.parent  # cases/claude-wp1.4-sweep/
CASES = CLAUDE_WP14.parent  # cases/
WP12 = CASES / "wp1.2"
WP11 = CASES / "wp1.1"

sys.path.insert(0, str(WP12 / "scripts"))
sys.path.insert(0, str(WP11 / "scripts"))
sys.path.insert(0, str(CASES / "claude-wp1.4" / "scripts"))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

P0_MMHG = 16.9
P_FINAL_DEFAULT = 50.0
N_STEPS = 16
NE_DEFAULT = 8


def p_targets(p_final: float, n_steps: int, p0: float = P0_MMHG) -> list[float]:
    return [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]


def phenomenological_corrections(
    row: dict, v_max: float, k_eff: float | None
) -> tuple[float, float | None, dict]:
    """Fatores fora da malha FE (ACD, cristalino, vitrectomia) — escala V e K.

    Não substituem geometria real (WP1.5); dão sinal treinável ao emulador enquanto
    a casca esférica não inclui câmara anterior / vítreo.
    """
    acd_nom = 3.25
    acd = float(row.get("ACD_mm", acd_nom))
    vol_factor = 1.0 + 0.025 * (acd - acd_nom)

    lens = row.get("lens_status", "phakic")
    lens_vol = {"phakic": 1.0, "pseudophakic": 0.97, "aphakic": 1.05}
    vol_factor *= lens_vol.get(lens, 1.0)

    vit = row.get("vitrectomy") in (True, "True", "true", "sim", "Sim")
    v_mult = 1.04 if vit else 1.0
    k_mult = 0.88 if vit else 1.0

    v_corr = v_max * vol_factor * v_mult
    k_corr = None
    if k_eff is not None and k_eff > 0:
        k_corr = k_eff * k_mult / max(vol_factor, 1e-6)

    meta = {
        "V_max_raw_uL": round(v_max, 2),
        "K_eff_raw_mmHg_per_uL": round(k_eff, 6) if k_eff else None,
        "correction_vol_factor": round(vol_factor, 4),
        "correction_vitrectomy": vit,
    }
    return v_corr, k_corr, meta


def run_one_case(row: dict, work: Path, ne: int, p_final: float) -> dict:
    """Roda um caso forward Ogden e retorna o resultado."""
    cid = row["case_id"]
    R = float(row["R_mm"])
    t = float(row["t_mm"])
    mu1 = float(row["mu1_MPa"])
    alpha1 = float(row["alpha1"])

    tag = cid
    t0 = time.time()

    try:
        # Gerar malha
        mesh_path = work / f"{tag}_mesh.inp"
        write_mesh(
            mesh_path, R, t, ne, 2, tag,
            bc_mode="symmetry_octant", mesh_kind="spherical",
            theta_min_deg=3.0, reduced=True,
        )

        # Parâmetros de material
        d1 = d1_from_ogden_mu1(mu1)
        params = {
            "mu1_MPa": mu1,
            "alpha1": alpha1,
            "D1": d1,
            "d1_tied_mu1": True,
        }

        # Deck CalculiX
        deck_path = work / f"{tag}.inp"
        write_deck(
            deck_path, mesh_path.name, t, "ogden1", params,
            p_targets(p_final, N_STEPS),
            label=f"ogden {tag}", bc_mode="symmetry_octant", p0_mmhg=P0_MMHG,
        )

        # Rodar
        frd = run_ccx(deck_path, clean=True)
        pv_rows = extract_pv(deck_path, frd, R, p0_mmhg=P0_MMHG)

        v_max = max(r["dV_uL"] for r in pv_rows)
        p_max = max(r["p_mmhg"] for r in pv_rows)

        # K_eff (rigidez inicial, entre os dois primeiros pontos)
        if len(pv_rows) >= 2:
            dv = pv_rows[1]["dV_uL"] - pv_rows[0]["dV_uL"]
            dp = pv_rows[1]["p_mmhg"] - pv_rows[0]["p_mmhg"]
            k_eff = dp / dv if dv > 0 else None
        else:
            k_eff = None

        v_corr, k_corr, corr_meta = phenomenological_corrections(row, v_max, k_eff)
        elapsed = time.time() - t0
        return {
            **row,
            "status": "OK",
            "V_max_uL": round(v_corr, 2),
            "P_max_mmHg": round(p_max, 2),
            "K_eff_mmHg_per_uL": round(k_corr, 6) if k_corr else None,
            **corr_meta,
            "elapsed_s": round(elapsed, 1),
            "pv_curve": pv_rows,
        }
    except Exception as exc:
        elapsed = time.time() - t0
        return {
            **row,
            "status": f"FAIL: {exc}",
            "elapsed_s": round(elapsed, 1),
        }


def load_existing(results_path: Path) -> dict[str, dict]:
    """Carrega resultados existentes para --resume."""
    if not results_path.exists():
        return {}
    data = json.loads(results_path.read_text())
    return {r["case_id"]: r for r in data if r.get("status") == "OK"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", type=Path, default=HERE / "sweep_samples.csv")
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_sweep_claude")
    ap.add_argument("--ne", type=int, default=NE_DEFAULT)
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--resume", action="store_true", help="Pula casos já convergidos")
    ap.add_argument("--start", type=int, default=0, help="Índice inicial (para lotes)")
    ap.add_argument("--end", type=int, default=None, help="Índice final (para lotes)")
    args = ap.parse_args()

    # Ler amostras
    with open(args.samples, newline="") as fh:
        samples = list(csv.DictReader(fh))

    # Filtrar intervalo
    end = args.end if args.end is not None else len(samples)
    samples = samples[args.start:end]

    # Resume
    results_path = args.out / "sweep_results.json"
    existing = load_existing(results_path) if args.resume else {}
    if existing:
        print(f"Resume: {len(existing)} casos já feitos, pulando...")

    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    work.mkdir(parents=True, exist_ok=True)

    results = list(existing.values())
    n_new = 0
    n_fail = 0

    for i, row in enumerate(samples):
        cid = row["case_id"]
        if cid in existing:
            continue

        idx = args.start + i + 1
        total = args.start + len(samples)
        print(f"[{idx}/{total}] {cid}  R={row['R_mm']} t={row['t_mm']} "
              f"mu1={row['mu1_MPa']} alpha1={row['alpha1']}")

        result = run_one_case(row, work, args.ne, args.p_final)
        results.append(result)
        n_new += 1

        if result["status"] == "OK":
            print(f"  -> OK  V_max={result['V_max_uL']:.1f} µL  "
                  f"K_eff={result.get('K_eff_mmHg_per_uL', '?')}  "
                  f"({result['elapsed_s']:.0f}s)")
        else:
            n_fail += 1
            print(f"  -> {result['status']}  ({result['elapsed_s']:.0f}s)")

        # Salvar incremental a cada 10 casos
        if n_new % 10 == 0:
            _save(results_path, results)

    _save(results_path, results)
    n_ok = sum(1 for r in results if r.get("status") == "OK")
    print(f"\nDone: {n_ok}/{len(results)} OK, {n_fail} FAIL")
    print(f"Resultados: {results_path}")
    return 0 if n_fail == 0 else 1


def _save(path: Path, results: list[dict]) -> None:
    """Salva resultados (sem pv_curve no JSON principal, para não ficar gigante)."""
    slim = []
    for r in results:
        entry = {k: v for k, v in r.items() if k != "pv_curve"}
        slim.append(entry)
    path.write_text(json.dumps(slim, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
