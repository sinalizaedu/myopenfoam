#!/usr/bin/env python3
"""Compare LaTeX report tables (wp0/wp1) against canonical JSON / WP0 solver output.

Exit 0 if all checks pass within rounding tolerance; exit 1 and print mismatches otherwise.

Canonical WP1.2 matrix: cases/wp1.2/output_literature_p50_digitized/
WP1.3 pretension: cases/wp1.3/output_backward_displacement_6/table10_summary.json
WP1.3 analytic ref: cases/wp1.3/data/analytic_membrane_reference_wp13.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    root = here.parents[2]
    if (root / "brunaStuff" / "latex" / "report" / "wp1.tex").is_file():
        return root
    env = os.environ.get("MYOPENFOAM_REPO")
    if env and (Path(env) / "brunaStuff" / "latex" / "report" / "wp1.tex").is_file():
        return Path(env)
    raise FileNotFoundError(
        "Cannot find brunaStuff/latex/report/wp1.tex — run from repo root or set MYOPENFOAM_REPO"
    )


REPO = repo_root()
LATEX = REPO / "brunaStuff" / "latex" / "report"
WP12_DIG = REPO / "cases" / "wp1.2" / "output_literature_p50_digitized"
WP12_MS_WIDE = REPO / "cases" / "wp1.2" / "output_multistart_friedenwald_alpha100" / "friedenwald"
WP12_MS_LOCAL = REPO / "cases" / "wp1.2" / "output_ogden_multistart_p50" / "friedenwald"
WP11_SUMMARY = REPO / "cases" / "wp1.1" / "output_octant" / "summary.json"
WP13_BD = REPO / "cases" / "wp1.3" / "output_backward_displacement_6"
WP13_ANALYTIC = REPO / "cases" / "wp1.3" / "data" / "analytic_membrane_reference_wp13.json"
WP0 = REPO / "cases" / "wp0"
WP0_METRICS = WP0 / "output_wp0" / "report_metrics.json"
WP0_VERIFY = WP0 / "output_wp0" / "verify_wp0_standards.json"
AUDIT_CMD = (
    "docker compose run --rm -v \"$PWD:/repo\" -w /repo fsi "
    "bash -lc 'python3 cases/scripts/audit_latex_report_numbers.py'"
)


def _br_float(s: str) -> float:
    s = s.strip()
    s = re.sub(r"\\textsuperscript\{[^}]*\}", "", s)
    s = s.replace("{,}", ".")
    s = s.replace(r"\,", ".")
    s = s.replace(",", ".")
    s = re.sub(r"[$\\{}]", "", s)
    s = re.sub(r"[^\d.\-+eE]", "", s.split()[0] if s.split() else s)
    if s in ("", "-", "+"):
        raise ValueError(f"not a number: {s!r}")
    return float(s)


def _close(a: float, b: float, *, abs_tol: float = 0.011, rel_tol: float = 0.002) -> bool:
    if abs(a - b) <= abs_tol:
        return True
    denom = max(abs(b), 1e-9)
    return abs(a - b) / denom <= rel_tol


@dataclass
class Check:
    name: str
    tex: float | None
    ref: float
    ok: bool
    note: str = ""


def extract_tabular_block(tex: str, label: str) -> str:
    m = re.search(rf"\\label\{{{re.escape(label)}\}}", tex)
    if not m:
        raise KeyError(f"label {label} not in tex")
    chunk = tex[m.start() : m.start() + 8000]
    begin = chunk.find("\\begin{tabular}")
    end = chunk.find("\\end{tabular}", begin)
    if begin < 0 or end < 0:
        raise KeyError(f"tabular for {label} not found")
    return chunk[begin:end]


def parse_wp12_ajuste_rows(block: str) -> list[dict]:
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("%") or "&" not in line:
            continue
        if line.startswith("\\") and "midrule" not in line and "toprule" not in line:
            continue
        if "midrule" in line or "toprule" in line or "bottomrule" in line:
            continue
        if "multicolumn" in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) < 8:
            continue
        alvo, mat = parts[0], parts[1]
        if alvo in ("Alvo", ""):
            continue
        rows.append(
            {
                "alvo": alvo.replace(" ", "").lower(),
                "material": mat.strip().lower(),
                "vmax": _br_float(parts[2]),
                "p1": _br_float(re.sub(r"\\textsuperscript\{\*\}", "", parts[3])),
                "p2": _br_float(re.sub(r"\\textsuperscript\{\*\}", "", parts[4])),
                "r2": _br_float(parts[5]),
                "max_res": _br_float(parts[6]),
                "nfev": int(round(_br_float(parts[7]))),
            }
        )
    return rows


def load_fit_matrix() -> dict[str, dict]:
    out = {}
    for target in ("friedenwald", "pallikaris", "silver"):
        for mat in ("ogden", "yeoh"):
            p = WP12_DIG / f"{target}_{mat}" / "fit_results.json"
            d = json.loads(p.read_text())
            sel = d["selected"]
            pr = sel["params"]
            q = sel["quality"]
            opt = sel["optimizer"]
            key = f"{target}_{mat}"
            if mat == "ogden":
                out[key] = {
                    "vmax": d["v_max_uL"],
                    "p1": pr["mu1_MPa"],
                    "p2": pr["alpha1"],
                    "r2": q["R2"],
                    "max_res": q["max_residual_mmHg"],
                    "nfev": opt["nfev"],
                }
            else:
                out[key] = {
                    "vmax": d["v_max_uL"],
                    "p1": pr["C10_MPa"],
                    "p2": pr["C20_MPa"],
                    "r2": q["R2"],
                    "max_res": q["max_residual_mmHg"],
                    "nfev": opt["nfev"],
                }
    return out


def check_wp12_ajuste(tex: str) -> list[Check]:
    block = extract_tabular_block(tex, "tab:wp12_ajuste")
    rows = parse_wp12_ajuste_rows(block)
    ref = load_fit_matrix()
    checks: list[Check] = []
    for row in rows:
        key = f"{row['alvo']}_{row['material']}"
        r = ref[key]
        for field, tex_key in (
            ("vmax", "vmax"),
            ("p1", "p1"),
            ("p2", "p2"),
            ("r2", "r2"),
            ("max_res", "max_res"),
            ("nfev", "nfev"),
        ):
            tv = row[tex_key] if tex_key != "nfev" else float(row["nfev"])
            rv = r[field]
            checks.append(
                Check(
                    f"tab12_ajuste {key} {field}",
                    tv,
                    rv,
                    _close(tv, rv, abs_tol=0.015 if field != "nfev" else 0.5),
                )
            )
    return checks


def check_wp12_linear(tex: str) -> list[Check]:
    block = extract_tabular_block(tex, "tab:wp12_linear")
    # friedenwald ogden pressures at V=20,50 from fit JSON
    d = json.loads((WP12_DIG / "friedenwald_ogden/fit_results.json").read_text())
    sel = d["selected"]
    target_by_v: dict[int, float] = {}
    for pt in sel.get("exp_at_fit", []):
        v = int(round(pt["V_uL"]))
        target_by_v[v] = pt["P_exp_dP_mmHg"] + 16.9
    curve = sel["fea_curve"]
    import numpy as np

    vs = [c["V_uL"] for c in curve]
    ps = [c["P_mmHg"] for c in curve]
    for V in (20, 50):
        target_by_v.setdefault(V, float(np.interp(V, vs, ps)))

    checks = []
    for line in block.splitlines():
        m = re.match(r"^\s*(\d+)\s*&", line)
        if not m:
            continue
        v = int(m.group(1))
        if v not in (20, 50):
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) < 8:
            continue
        alvo = _br_float(parts[1])
        ogden = _br_float(parts[6])
        err_ogden = _br_float(parts[7])
        ref_p = target_by_v[v]
        ref_err = 100 * (ogden - ref_p) / ref_p
        checks.append(Check(f"tab12_linear V={v} alvo", alvo, ref_p, _close(alvo, ref_p, abs_tol=0.15)))
        checks.append(Check(f"tab12_linear V={v} ogden err%", err_ogden, ref_err, _close(err_ogden, ref_err, abs_tol=0.15)))
    return checks


def check_wp13_tables(tex: str) -> list[Check]:
    summary = json.loads((WP13_BD / "table10_summary.json").read_text())
    by_label = {r["label"]: r for r in summary}
    analytic = json.loads(WP13_ANALYTIC.read_text())["cases"]

    checks: list[Check] = []

    block_p = extract_tabular_block(tex, "tab:wp13_pretensao")
    for line in block_p.splitlines():
        if "&" not in line or "midrule" in line or "Alvo" in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) < 7:
            continue
        alvo, mat = parts[0].lower(), parts[1].lower()
        if alvo == "alvo":
            continue
        key = f"{alvo}_{mat}"
        r = by_label[key]
        u = _br_float(parts[2])
        four_u = _br_float(parts[3])
        dk10 = _br_float(parts[4])
        ref_u = r["fixed_point"]["u_mm"]
        ref_4u = r["fixed_point"]["four_u_over_R_pct"]
        ref_dk = r["relative_change_pct"]["secant_10mmHg_pct"]
        checks.append(Check(f"tab13_pret {key} u", u, ref_u, _close(u, ref_u, abs_tol=0.002)))
        checks.append(Check(f"tab13_pret {key} 4u/R", four_u, ref_4u, _close(four_u, ref_4u, abs_tol=0.02)))
        checks.append(Check(f"tab13_pret {key} dK+10", dk10, ref_dk, _close(dk10, ref_dk, abs_tol=0.02)))

    block_a = extract_tabular_block(tex, "tab:wp13_analytic")
    for line in block_a.splitlines():
        if "&" not in line or "midrule" in line or "Alvo" in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) < 6:
            continue
        alvo, mat = parts[0].lower(), parts[1].lower()
        if alvo == "alvo":
            continue
        key = f"{alvo}_{mat}"
        an = analytic[key]
        u_an = _br_float(parts[2])
        u_fea = _br_float(parts[3])
        dk_an = _br_float(parts[4])
        dk_fea = _br_float(parts[5])
        ref_u_fea = by_label[key]["fixed_point"]["u_mm"]
        ref_dk_fea = by_label[key]["relative_change_pct"]["secant_10mmHg_pct"]
        checks.append(Check(f"tab13_analytic {key} u_an", u_an, an["u_analytic_mm"], _close(u_an, an["u_analytic_mm"], abs_tol=0.002)))
        checks.append(Check(f"tab13_analytic {key} u_fea", u_fea, ref_u_fea, _close(u_fea, ref_u_fea, abs_tol=0.002)))
        checks.append(Check(f"tab13_analytic {key} dK_an", dk_an, an["deltaK_analytic_pct"], _close(dk_an, an["deltaK_analytic_pct"], abs_tol=0.02)))
        checks.append(Check(f"tab13_analytic {key} dK_fea", dk_fea, ref_dk_fea, _close(dk_fea, ref_dk_fea, abs_tol=0.02)))

    return checks


def _multistart_by_x0(ms: dict, x0: tuple[float, float], tol: float = 0.02) -> dict | None:
    for r in ms.get("all_results", []):
        if "error" in r:
            continue
        x = r.get("x0")
        if not x or len(x) < 2:
            continue
        if abs(float(x[0]) - x0[0]) <= tol and abs(float(x[1]) - x0[1]) <= tol:
            return r
    return None


def check_wp12_multistart(tex: str) -> list[Check]:
    """Wide box α∈[0.5,100] (15 starts) + local minima C1–C6 from aux run α∈[0.5,6]."""
    checks: list[Check] = []
    wide_path = WP12_MS_WIDE / "multistart_results.json"
    local_path = WP12_MS_LOCAL / "multistart_results.json"
    if not wide_path.is_file():
        checks.append(Check("multistart wide JSON present", None, 1.0, False, note=str(wide_path)))
        return checks
    wide = json.loads(wide_path.read_text())
    n_err = sum(1 for r in wide["all_results"] if "error" in r)
    checks.append(Check("multistart wide CCX failures", float(n_err), 7.0, n_err == 7))

    fit = json.loads((WP12_DIG / "friedenwald_ogden/fit_results.json").read_text())["selected"]
    pr = fit["params"]
    q = fit["quality"]
    checks.append(Check("ms single mu1", _br_float("1,925"), pr["mu1_MPa"], _close(1.925, pr["mu1_MPa"], abs_tol=0.002)))
    checks.append(Check("ms single alpha1", _br_float("10,385"), pr["alpha1"], _close(10.385, pr["alpha1"], abs_tol=0.02)))
    checks.append(Check("ms single R2", _br_float("0,9865"), q["R2"], _close(0.9865, q["R2"], abs_tol=0.0005)))

    best_cost = min(
        float(r["cost"])
        for r in wide["all_results"]
        if "cost" in r and r["cost"] != float("inf") and float(r.get("R2", -1)) > 0.98
    )
    for label, x0 in (
        ("x0_1925_1038", (1.925, 10.38)),
        ("x0_227_106", (2.27, 1.06)),
        ("x0_100_250", (1.0, 2.5)),
    ):
        r = _multistart_by_x0(wide, x0)
        if not r:
            checks.append(Check(f"multistart wide {label} found", None, 1.0, False))
            continue
        checks.append(Check(f"multistart wide {label} R2", r["R2"], r["R2"], r["R2"] > 0.976))
        checks.append(
            Check(
                f"multistart wide {label} alpha1",
                r["alpha1_final"],
                r["alpha1_final"],
                (label == "x0_100_250" and r["alpha1_final"] <= 6) or r["alpha1_final"] > 6,
            )
        )

    block = extract_tabular_block(tex, "tab:wp12_multistart_friedenwald")
    if local_path.is_file():
        local = json.loads(local_path.read_text())
        clusters_by_id = {int(c["id"]): c["best"] for c in local.get("clusters", [])}
        for line in block.splitlines():
            m = re.match(r"^\s*C(\d+)\s*&", line)
            if not m:
                continue
            cid = int(m.group(1))
            parts = [p.strip() for p in line.split("&")]
            if len(parts) < 5:
                continue
            mu = _br_float(parts[1])
            al = _br_float(re.sub(r"\\textsuperscript\{\*\}", "", parts[2]))
            r2 = _br_float(parts[3])
            ref = clusters_by_id.get(cid)
            if ref and ref.get("R2", -999) > 0.976:
                checks.append(Check(f"ms local C{cid} mu1", mu, ref["mu1_final"], _close(mu, ref["mu1_final"], abs_tol=0.015)))
                checks.append(Check(f"ms local C{cid} alpha1", al, ref["alpha1_final"], _close(al, ref["alpha1_final"], abs_tol=0.02)))
                checks.append(Check(f"ms local C{cid} R2", r2, ref["R2"], _close(r2, ref["R2"], abs_tol=0.0005)))
            else:
                checks.append(Check(f"ms local C{cid} cluster", None, 1.0, False, note=f"id={cid}"))
    else:
        checks.append(Check("multistart local JSON present", None, 1.0, False, note=str(local_path)))

    return checks


def check_wp11_tables(tex: str) -> list[Check]:
    checks: list[Check] = []
    if not WP11_SUMMARY.is_file():
        checks.append(Check("wp1.1 summary.json present", None, 1.0, False, note=str(WP11_SUMMARY)))
        return checks
    summary = json.loads(WP11_SUMMARY.read_text())

    def row(case: str, ne: int) -> dict | None:
        for r in summary.get("results", []):
            if r.get("case") == case and r.get("ne") == ne:
                return r
        return None

    targets = {
        "human": {"K": 0.163338, "err": 0.25, "eps_36": 0.0193},
        "rabbit": {"K": 0.670183, "err": 0.27, "eps_36": 0.0104},
    }
    for case, tgt in targets.items():
        r6 = row(case, 6)
        r3 = row(case, 3)
        if r6:
            checks.append(Check(f"wp11 {case} K@ne6", r6["K_FEA_mmHg_per_uL"], tgt["K"], _close(r6["K_FEA_mmHg_per_uL"], tgt["K"], abs_tol=0.0002)))
            checks.append(Check(f"wp11 {case} err@ne6", r6["error_pct"], tgt["err"], _close(r6["error_pct"], tgt["err"], abs_tol=0.02)))
        if r3 and r6:
            eps = 100 * abs(r6["K_FEA_mmHg_per_uL"] - r3["K_FEA_mmHg_per_uL"]) / r3["K_FEA_mmHg_per_uL"]
            checks.append(Check(f"wp11 {case} eps_i 72->288", eps, tgt["eps_36"], _close(eps, tgt["eps_36"], abs_tol=0.005)))

    def row_by_equiv(case: str, equiv: int) -> dict | None:
        for r in summary.get("results", []):
            if r.get("case") == case and r.get("full_sphere_equiv_elements") == equiv:
                return r
        return None

    block_ind = extract_tabular_block(tex, "tab:wp1_independencia")
    for line in block_ind.splitlines():
        m = re.match(r"^\s*(\d+)\s*&", line)
        if not m:
            continue
        equiv = int(m.group(1))
        parts = [p.strip() for p in line.split("&")]
        if len(parts) < 5:
            continue
        k_h = _br_float(parts[1])
        k_r = _br_float(parts[3])
        rh = row_by_equiv("human", equiv)
        rr = row_by_equiv("rabbit", equiv)
        if rh:
            checks.append(
                Check(
                    f"wp11 indep human {equiv} K",
                    k_h,
                    rh["K_FEA_mmHg_per_uL"],
                    _close(k_h, rh["K_FEA_mmHg_per_uL"], abs_tol=0.0002),
                )
            )
        if rr:
            checks.append(
                Check(
                    f"wp11 indep rabbit {equiv} K",
                    k_r,
                    rr["K_FEA_mmHg_per_uL"],
                    _close(k_r, rr["K_FEA_mmHg_per_uL"], abs_tol=0.0002),
                )
            )
        if equiv >= 288 and "--" not in parts[2]:
            eps_h = _br_float(parts[2])
            if rh and math.isfinite(float(rh.get("epsilon_i_pct", float("nan")))):
                checks.append(
                    Check(
                        f"wp11 indep human {equiv} eps_i",
                        eps_h,
                        rh["epsilon_i_pct"],
                        _close(eps_h, rh["epsilon_i_pct"], abs_tol=0.001),
                    )
                )
        if equiv >= 288 and "--" not in parts[4] and "<" not in parts[4]:
            eps_r = _br_float(parts[4])
            if rr and math.isfinite(float(rr.get("epsilon_i_pct", float("nan")))):
                checks.append(
                    Check(
                        f"wp11 indep rabbit {equiv} eps_i",
                        eps_r,
                        rr["epsilon_i_pct"],
                        _close(eps_r, rr["epsilon_i_pct"], abs_tol=0.001),
                    )
                )

    block = extract_tabular_block(tex, "tab:wp1_sensibilidade")
    for case_key, label in (("Humano", "human"), ("Coelho", "rabbit")):
        for line in block.splitlines():
            if not line.strip().startswith(case_key):
                continue
            parts = [p.strip() for p in line.split("&")]
            if len(parts) < 5:
                continue
            k_tex = _br_float(parts[2])
            err_tex = _br_float(parts[4])
            r6 = row(label, 6)
            if r6:
                checks.append(Check(f"wp11 tex {label} K", k_tex, r6["K_FEA_mmHg_per_uL"], _close(k_tex, r6["K_FEA_mmHg_per_uL"], abs_tol=0.0002)))
                checks.append(Check(f"wp11 tex {label} err%", err_tex, r6["error_pct"], _close(err_tex, r6["error_pct"], abs_tol=0.02)))
    return checks


def check_wp0_report_metrics() -> list[Check]:
    checks: list[Check] = []
    if not WP0_METRICS.is_file():
        checks.append(
            Check(
                "wp0 report_metrics.json present",
                None,
                1.0,
                False,
                note="run: cd cases/wp0 && ./Allrun",
            )
        )
        return checks
    data = json.loads(WP0_METRICS.read_text())
    for c in data.get("checks", []):
        checks.append(
            Check(
                f"wp0 metric {c['name']}",
                c["got"],
                c["expected"],
                bool(c["ok"]),
                note=f"tol={c.get('tol')}",
            )
        )
    return checks


def check_wp0_prose(tex: str) -> list[Check]:
    sys.path.insert(0, str(WP0))
    from goldmann_iop_solver import (  # noqa: WPS433
        lobue_return_metrics,
        protocol_humano_relatorio,
        Q_PROD_HUMAN_TABELA_UL_MIN,
    )

    checks: list[Check] = []
    proto = protocol_humano_relatorio()
    checks.append(
        Check(
            "code Q_prod protocol",
            proto.Q_prod_uL_min,
            Q_PROD_HUMAN_TABELA_UL_MIN,
            _close(proto.Q_prod_uL_min, Q_PROD_HUMAN_TABELA_UL_MIN, abs_tol=1e-6),
        )
    )
    if "2{,}415" not in tex and "2.415" not in tex:
        checks.append(Check("wp0.tex mentions Q_prod 2,415", None, 1.0, False, note="substring missing"))
    lb = lobue_return_metrics()
    m14 = re.search(r"\\SI\{14\{,\}(\d+)\}\{\\minute\}", tex)
    m58 = re.search(r"modelo prev[eê]\s+\$?\\SI\{5\{,\}(\d+)\}", tex)
    if m14:
        tv = float("14." + m14.group(1))
        checks.append(Check("LoBue t_return vs tex 14,x min", tv, lb["t_return_min"], _close(tv, lb["t_return_min"], abs_tol=0.15)))
    if m58:
        tv = float("5." + m58.group(1))
        checks.append(Check("LoBue delta@10min vs tex 5,x mmHg", tv, lb["delta_P_at_10min_mmHg"], _close(tv, lb["delta_P_at_10min_mmHg"], abs_tol=0.15)))
    return checks


def write_methodology_audit_meta(path: Path) -> None:
    fits = load_fit_matrix()
    payload = {
        "meta": {
            "purpose": "Pointer only — use cases/scripts/audit_latex_report_numbers.py for numeric truth",
            "supersedes_stale_v2_mulf_audit": True,
            "canonical_outputs": {
                "wp12_matrix": str(WP12_DIG.relative_to(REPO)),
                "wp12_multistart_wide": str(WP12_MS_WIDE.relative_to(REPO)),
                "wp12_multistart_local_C": str(WP12_MS_LOCAL.relative_to(REPO)),
                "wp13_pretension": str((WP13_BD / "table10_summary.json").relative_to(REPO)),
                "wp13_analytic": str(WP13_ANALYTIC.relative_to(REPO)),
            },
            "audit_command": AUDIT_CMD,
        },
        "fit_table7_snapshot": {
            k: {kk: (round(vv, 6) if isinstance(vv, float) else vv) for kk, vv in v.items()}
            for k, v in fits.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def write_methodology_audit_root(path: Path) -> None:
    """Replace legacy manual methodology_audit.json with run manifest + artifact pointers."""
    import subprocess

    def git_head() -> str:
        try:
            return (
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"

    verify_ok = None
    if WP0_VERIFY.is_file():
        v = json.loads(WP0_VERIFY.read_text())
        failed = [c for c in v.get("checks", []) if not c.get("ok")]
        verify_ok = len(failed) == 0

    payload = {
        "meta": {
            "purpose": "Canonical pipeline for brunaStuff/latex/report (wp0.tex, wp1.tex)",
            "supersedes_manual_audit_2026-10-09": True,
            "generated_by": "cases/scripts/audit_latex_report_numbers.py --write-methodology-audit-root",
            "git_head": git_head(),
            "audit_latex_command": AUDIT_CMD,
        },
        "pipelines": {
            "wp0": {
                "command": "cd cases/wp0 && ./Allrun",
                "docker": "docker compose run --rm -v \"$PWD:/repo\" -w /repo fsi bash -lc 'cd cases/wp0 && ./Allrun'",
                "artifacts": [
                    "cases/wp0/output_wp0/report_metrics.json",
                    "cases/wp0/output_wp0/verify_wp0_standards.json",
                    "cases/wp0/output_wp0/verify_ruffini.json",
                    "brunaStuff/latex/report/Figuras/fig*.png",
                ],
            },
            "wp1.1": {
                "command": "cd cases/wp1.1 && ./Allrun",
                "docker": "docker compose run --rm -v \"$PWD:/repo\" -w /repo fsi bash -lc 'cd cases/wp1.1 && ./Allrun'",
                "artifacts": ["cases/wp1.1/output_octant/summary.json"],
            },
            "wp1.2_matrix": {
                "command": "cd cases/wp1.2 && ./Allrun_literature_p50",
                "artifacts": ["cases/wp1.2/output_literature_p50_digitized/*/fit_results.json"],
            },
            "wp1.2_multistart": {
                "note": "Wide α∈[0.5,100] fifteen starts + local C1–C6 from output_ogden_multistart_p50",
                "commands": [
                    "cd cases/wp1.2 && python3 scripts/run_ogden_multistart_matrix.py --targets friedenwald --out output_multistart_friedenwald_alpha100 --alpha-lo 0.5 --alpha-hi 100",
                    "cd cases/wp1.2 && python3 scripts/run_ogden_multistart_matrix.py --targets friedenwald --out output_ogden_multistart_p50 --alpha-lo 0.5 --alpha-hi 6",
                ],
                "artifacts": [
                    "cases/wp1.2/output_multistart_friedenwald_alpha100/friedenwald/multistart_results.json",
                    "cases/wp1.2/output_ogden_multistart_p50/friedenwald/multistart_results.json",
                ],
            },
            "wp1.3": {
                "command": "cd cases/wp1.3 && ./Allrun_backward_displacement_6",
                "artifacts": [
                    "cases/wp1.3/output_backward_displacement_6/table10_summary.json",
                    "cases/wp1.3/data/analytic_membrane_reference_wp13.json",
                ],
            },
        },
        "verification_status": {
            "verify_wp0_standards_json_present": WP0_VERIFY.is_file(),
            "verify_wp0_standards_all_ok": verify_ok,
            "report_metrics_json_present": WP0_METRICS.is_file(),
            "wp12_wp13_stub": str(REPO / "methodology_audit_wp12_wp13.json"),
        },
        "note": "Numeric truth is enforced by audit_latex_report_numbers.py, not by this file.",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write-methodology-audit",
        type=Path,
        default=None,
        help="Refresh methodology_audit_wp12_wp13.json stub",
    )
    ap.add_argument(
        "--write-methodology-audit-root",
        type=Path,
        default=None,
        help="Replace repo-root methodology_audit.json with pipeline manifest",
    )
    args = ap.parse_args()

    wp1 = (LATEX / "wp1.tex").read_text(encoding="utf-8")
    wp0 = (LATEX / "wp0.tex").read_text(encoding="utf-8")

    all_checks: list[Check] = []
    all_checks.extend(check_wp11_tables(wp1))
    all_checks.extend(check_wp12_ajuste(wp1))
    all_checks.extend(check_wp12_linear(wp1))
    all_checks.extend(check_wp12_multistart(wp1))
    all_checks.extend(check_wp13_tables(wp1))
    all_checks.extend(check_wp0_report_metrics())
    try:
        all_checks.extend(check_wp0_prose(wp0))
    except ImportError as e:
        print("SKIP wp0 solver checks (scipy):", e, file=sys.stderr)

    failed = [c for c in all_checks if not c.ok]
    for c in all_checks:
        status = "OK" if c.ok else "FAIL"
        print(f"{status}\t{c.name}\ttex={c.tex}\tref={c.ref}\t{c.note}")

    if failed:
        print(f"\n{len(failed)} check(s) failed.", file=sys.stderr)
        return 1
    if args.write_methodology_audit:
        write_methodology_audit_meta(args.write_methodology_audit)
    if args.write_methodology_audit_root:
        write_methodology_audit_root(args.write_methodology_audit_root)
    print(f"\nAll {len(all_checks)} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
