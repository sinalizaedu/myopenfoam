#!/usr/bin/env python3
"""claude-wp1.1 -- verificacao linear K com varredura de theta_min (borda da calota).

Responde direto a *pergunta 1* do HANDOFF_WP1_octant_geometry.md: quanto a
borda livre da calota (theta < theta_min) esta distorcendo K perto do polo?

Roda WP1.1 (material linear, casca fina esferica) na malha de octante ja
validada (mesma do run_verification_octant.py), variando theta_min em
{1.0, 3.0, 5.0} graus, para humano e coelho. Se a variacao de K com
theta_min for pequena (~<0.1%), a borda livre nao e um artefato relevante
e o valor default de 3.0 usado no restante do projeto esta seguro. Se for
grande, a calota livre esta introduzindo erro sistematico que precisa ser
tratado (fechar a borda com uma condicao de restricao, ou reduzir theta_min).

Nao edita nenhum arquivo existente -- so importa write_mesh e extract do
wp1.1/scripts/ e escreve saida em cases/claude-wp1.1/output/.

Uso (dentro do container):
    cd /simulation/claude-wp1.1 && python3 scripts/verify_theta_min_sweep_claude.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE_ROOT = HERE.parent  # cases/claude-wp1.1/
CASES_DIR = CASE_ROOT.parent  # cases/
WP1_SCRIPTS = CASES_DIR / "wp1.1" / "scripts"
sys.path.insert(0, str(WP1_SCRIPTS))

from extract_K import K_analytic_mmHg_per_uL, extract  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402

MMHG_TO_MPA = 133.322e-6
CASES = {
    "human": {"R": 12.0, "t": 0.5},
    "rabbit": {"R": 7.6, "t": 0.33},
}
E_MPA = 3.0
NU = 0.47
DP_MMHG = 1.0
NE = 6  # malha de referencia do WP1.1 (288 elementos equivalentes)
THETA_MIN_SWEEP_DEG = [1.0, 3.0, 5.0]  # 3.0 e o default atual


@dataclass
class RunResult:
    case: str
    theta_min_deg: float
    ne: int
    K_analytic: float
    K_FEA: float
    error_pct: float
    n_elements_octant: int
    log_path: str


def ccx_bin() -> str:
    override = os.environ.get("CCX_BIN", "").strip()
    if override and Path(override).is_file():
        return override
    for name in ("ccx_preCICE", "ccx", "ccx_2.23", "ccx_2.21", "ccx_2.20"):
        p = shutil.which(name)
        if p:
            return p
    for p in ("/opt/calculix/bin/ccx_preCICE", "/opt/homebrew/bin/ccx_2.23"):
        if Path(p).is_file():
            return p
    raise RuntimeError("CalculiX (ccx) not found in PATH")


def write_deck(deck: Path, mesh_name: str, R_mm: float, t_mm: float,
                dP_mmHg: float, case_label: str) -> None:
    p_mpa = dP_mmHg * MMHG_TO_MPA
    K_an = K_analytic_mmHg_per_uL(R_mm, t_mm, E_MPA, NU)
    deck.write_text(
        f"""*HEADING
claude-wp1.1 theta_min sweep -- {case_label}
** R={R_mm} mm, t={t_mm} mm, octante (theta,phi), S8R, NLGEOM=NO
** K_analytic = {K_an:.6f} mmHg/uL, dP = {dP_mmHg} mmHg
*INCLUDE, INPUT={mesh_name}
*MATERIAL, NAME=SHELL_MAT
*ELASTIC
{E_MPA:.6f}, {NU:.6f}
*SHELL SECTION, ELSET=SHELL, MATERIAL=SHELL_MAT
{t_mm:.6f}
*STEP, NAME=PRESSURE, NLGEOM=NO, INC=10
*STATIC
1.0, 1.0, 1e-6, 1.0
*BOUNDARY
SYM_X, 1, 1, 0.0
SYM_Y, 2, 2, 0.0
SYM_Z, 3, 3, 0.0
*DSLOAD
INNER_SURF, P, {p_mpa:.12e}
*NODE FILE
U
*END STEP
"""
    )


def run_case(case: str, theta_min_deg: float, work_dir: Path) -> RunResult:
    geom = CASES[case]
    R, t = geom["R"], geom["t"]
    tag = f"{case}_tmin{int(theta_min_deg*10):02d}"  # ex: human_tmin30 = 3.0deg
    mesh = work_dir / f"{tag}_mesh.inp"
    deck = work_dir / f"{tag}.inp"
    write_mesh(
        mesh, R, t, NE, 2,
        label=f"{case} octant ne={NE} theta_min={theta_min_deg}",
        bc_mode="symmetry_octant", mesh_kind="spherical",
        theta_min_deg=theta_min_deg, reduced=True,
    )
    write_deck(deck, mesh.name, R, t, DP_MMHG, f"{case} tmin={theta_min_deg}deg")

    for ext in (".frd", ".sta", ".cvg", ".dat", ".12d"):
        p = work_dir / f"{tag}{ext}"
        if p.exists():
            p.unlink()

    log = work_dir / f"log_{tag}.txt"
    with open(log, "w") as fh:
        subprocess.run([ccx_bin(), "-i", tag], cwd=work_dir, check=True,
                        stdout=fh, stderr=subprocess.STDOUT,
                        env={**os.environ, "OMP_NUM_THREADS":
                              str(os.cpu_count() or 4)})
    frd = work_dir / f"{tag}.frd"
    res = extract(deck, frd, R, t, E_MPA, NU)
    return RunResult(
        case=case, theta_min_deg=theta_min_deg, ne=NE,
        K_analytic=res["K_analytic_mmHg_per_uL"],
        K_FEA=res["K_FEA_mmHg_per_uL"],
        error_pct=res["error_pct"],
        n_elements_octant=NE * NE,
        log_path=str(log),
    )


def main() -> int:
    out_dir = CASE_ROOT / "output"
    ccx_dir = out_dir / "ccx"
    out_dir.mkdir(parents=True, exist_ok=True)
    ccx_dir.mkdir(parents=True, exist_ok=True)
    print(f"CalculiX: {ccx_bin()}")
    print(f"Sweep: theta_min in {THETA_MIN_SWEEP_DEG} deg, ne={NE}, "
          f"{len(CASES)*len(THETA_MIN_SWEEP_DEG)} runs total")

    results: list[RunResult] = []
    for case in CASES:
        for tmin in THETA_MIN_SWEEP_DEG:
            print(f"  {case}, theta_min={tmin} deg ...")
            r = run_case(case, tmin, ccx_dir)
            results.append(r)
            print(f"    K_FEA = {r.K_FEA:.6f}  (erro {r.error_pct:+.3f}%)")

    # tabela por especie
    lines = ["# claude-wp1.1 -- varredura theta_min (borda da calota)\n",
             "Objetivo: quantificar o efeito da calota livre (theta<theta_min) em K.",
             f"Malha: octante ({NE}x{NE} elementos = {NE*NE} por octante, "
             f"{NE*NE*8} equivalentes na esfera completa), S8R, NLGEOM=NO, "
             f"linear elastico E={E_MPA} MPa, nu={NU}.\n"]
    for case in CASES:
        rows = [r for r in results if r.case == case]
        K_an = rows[0].K_analytic
        lines.append(f"## {case} (R={CASES[case]['R']} mm, t={CASES[case]['t']} mm)")
        lines.append(f"K_analitico = {K_an:.6f} mmHg/uL")
        lines.append("| theta_min (deg) | K_FEA | erro vs analitico (%) | delta K vs tmin=3deg (%) |")
        lines.append("|---:|---:|---:|---:|")
        K_ref = next(r.K_FEA for r in rows if r.theta_min_deg == 3.0)
        for r in rows:
            dK = 100.0 * (r.K_FEA - K_ref) / K_ref
            lines.append(f"| {r.theta_min_deg} | {r.K_FEA:.6f} | "
                          f"{r.error_pct:+.3f} | {dK:+.4f} |")
        lines.append("")

    lines.append("## Veredicto")
    lines.append("- Se |delta K| < 0.1% em toda a faixa: borda livre da calota "
                  "**nao e artefato relevante** e o default theta_min=3deg do "
                  "restante do projeto esta seguro.")
    lines.append("- Se |delta K| >= 0.1%: a borda esta introduzindo erro "
                  "sistematico -- ver Section 'Pergunta 1' do HANDOFF.")

    (out_dir / "RESULTS.md").write_text("\n".join(lines))
    (out_dir / "results.json").write_text(json.dumps(
        [{"case": r.case, "theta_min_deg": r.theta_min_deg, "K_FEA": r.K_FEA,
          "K_analytic": r.K_analytic, "error_pct": r.error_pct}
         for r in results], indent=2))
    print("\n" + "\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
