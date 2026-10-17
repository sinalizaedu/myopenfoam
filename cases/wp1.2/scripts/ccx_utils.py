"""CalculiX helpers shared by wp1.2 inverse FEA fitting."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

MMHG_TO_MPA = 133.322e-6  # N/mm² when lengths are mm

# WP1.1 / nearly incompressible shell: K0 ≈ E/[3(1−2ν)] → D1 = 2/K0 ≈ 0.12 MPa⁻¹ at ν≈0.47.
YEOH_D1_MPA = 0.12
OGDEN_D1_SCALE = 0.12  # D1 = OGDEN_D1_SCALE * (1.0204 / μ1)


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
    raise RuntimeError("CalculiX (ccx / ccx_preCICE) not found in PATH")


def mmhg_to_mpa(p_mmhg: float) -> float:
    return float(p_mmhg) * MMHG_TO_MPA


def run_ccx(deck: Path, clean: bool = True) -> Path:
    """Run CalculiX on ``deck`` (.inp). Returns path to .frd."""
    ccx = ccx_bin()
    work = deck.parent
    stem = deck.stem
    if clean:
        for ext in (".frd", ".sta", ".cvg", ".dat", ".12d"):
            p = work / f"{stem}{ext}"
            if p.exists():
                p.unlink()
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", str(os.cpu_count() or 4))
    log = work / f"log_{stem}.txt"
    with open(log, "w") as fh:
        subprocess.run(
            [ccx, "-i", stem],
            cwd=work,
            check=True,
            stdout=fh,
            stderr=subprocess.STDOUT,
            env=env,
        )
    frd = work / f"{stem}.frd"
    if not frd.is_file():
        raise RuntimeError(f"Missing {frd}; see {log}")
    return frd


def d1_from_nu_mpa(nu: float = 0.47, E_mpa: float = 3.0) -> float:
    """Nearly-incompressible bulk compliance D1 [1/MPa] from (E, nu)."""
    k_mpa = E_mpa / (3.0 * (1.0 - 2.0 * nu))
    return 2.0 / k_mpa


def d1_from_ogden_mu1(mu1_mpa: float) -> float:
    """Bulk compliance D1 [1/MPa] tied to μ₁ (ν≈0.47, WP1.1 convention)."""
    return OGDEN_D1_SCALE * (1.0204 / float(mu1_mpa))


def bulk_compliance_mpa(model: str, nu: float = 0.47, E_mpa: float = 3.0) -> float:
    """Bulk compliance D1 [1/MPa] for *HYPERELASTIC cards."""
    if model.startswith("ogden"):
        return 1.0e-6
    return YEOH_D1_MPA


def ccx_diagnostics() -> dict:
    """Record CalculiX binary version and dynamic linker deps (convergence audit)."""
    ccx = ccx_bin()
    info: dict = {"ccx_bin": ccx}
    try:
        ver = subprocess.run(
            [ccx, "-v"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        info["ccx_v_stdout"] = ver.stdout.strip()
        info["ccx_v_stderr"] = ver.stderr.strip()
        info["ccx_v_returncode"] = ver.returncode
    except Exception as exc:
        info["ccx_v_error"] = str(exc)
    try:
        ldd = subprocess.run(
            ["ldd", ccx],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        info["ldd_stdout"] = ldd.stdout.strip()
        info["ldd_returncode"] = ldd.returncode
    except Exception as exc:
        info["ldd_error"] = str(exc)
    return info
