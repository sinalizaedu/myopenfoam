#!/usr/bin/env python3
"""
run_anatomical_test.py
---------------------
Monta o .inp completo (malha + material + BCs + step) e executa ccx.
Fase 1: material unico (Ogden esclera) para todas as regioes.

Uso dentro do Docker:
    docker compose run --rm fsi bash -lc \
      'cd /simulation/<PASTA>/scripts && python3 run_anatomical_test.py'

Prerequisito: converter a malha antes (convert_gmsh_to_ccx.py)

Material:
    Ogden N=1 (ajuste Friedenwald, WP1.2):
    mu1 = 2.2708 MPa, alpha1 = 1.0562, D1 = 0.2247

Pressao:
    P0 = 15 mmHg = 1999.83 Pa (IOP basal)
    P_final = 50 mmHg = 6666.1 Pa (pico pos-IVI)
    Fonte: plano de tese, Ensaios A e B do WP2

Simetria:
    SYMMETRY_0 (plano z=0): DOF 3 = 0
    SYMMETRY_90 (plano x=0): DOF 1 = 0

Referências:
    Geometria: Lamminsalo et al. 2018 / Missel 2012 (coelho)
    Material: ajuste Friedenwald WP1.2
    Pressao: plano de tese, WP2
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
MESH_INP = Path("../mesh/eye_anatomical.inp")
OUTPUT_DIR = Path("../output_test")
JOB_NAME = "eye_anat_test"

# Material: Ogden N=1 — Friedenwald fit (WP1.2)
# Fonte: resultado do WP1.2 (ajuste curva pressao-volume de Friedenwald)
MU1 = 2.2708e6       # Pa (CalculiX usa Pa quando malha em metros)
ALPHA1 = 1.0562
D1 = 0.2247e-6        # 1/Pa

# Pressao interna
# Fonte: plano de tese, WP2 — "Equilibrar a 15 mmHg" / "injetar 50 uL em 6 s"
MMHG_TO_PA = 133.322
P_BASAL = 15.0 * MMHG_TO_PA    # 1999.83 Pa
P_FINAL = 50.0 * MMHG_TO_PA    # 6666.1 Pa
N_STEPS = 16


# ---------------------------------------------------------------------------
# GERAR .inp COMPLETO
# ---------------------------------------------------------------------------
def generate_full_inp(mesh_inp, output_dir, job_name):
    """Gera o .inp completo combinando malha + material + BCs + step."""

    if not mesh_inp.exists():
        print(f"ERRO: malha .inp nao encontrada: {mesh_inp}")
        print("Execute convert_gmsh_to_ccx.py primeiro.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    inp_path = output_dir / f"{job_name}.inp"

    with open(inp_path, "w") as f:
        f.write("** ============================================================\n")
        f.write("** WP1.5 Fase 1: Teste de pipeline anatomico\n")
        f.write("** Material unico (Ogden esclera) para todas as regioes\n")
        f.write("** Geometria: Lamminsalo et al. 2018 / Missel 2012 (coelho)\n")
        f.write("** ============================================================\n")
        f.write("**\n")

        # Include mesh
        f.write(f"*INCLUDE, INPUT={mesh_inp}\n")
        f.write("**\n")

        # ---- MATERIAL ----
        # Ogden N=1, ajuste Friedenwald WP1.2
        # Nota: todas as regioes recebem o mesmo material (Fase 1 = teste de pipeline)
        f.write("** MATERIAL: Ogden N=1 (Friedenwald fit, WP1.2)\n")
        f.write("** mu1 = 2.2708 MPa, alpha1 = 1.0562, D1 = 0.2247 1/MPa\n")
        f.write("** (em Pa: mu1 = 2.2708e6, D1 = 0.2247e-6)\n")
        f.write("*MATERIAL, NAME=SCLERA_OGDEN\n")
        f.write("*HYPERELASTIC, OGDEN, N=1\n")
        f.write(f"{MU1:.6e}, {ALPHA1:.6f}, {D1:.6e}\n")
        f.write("**\n")

        # Assign material to all zones (same material for Phase 1)
        for zone in ["CORNEA", "SCLERA", "CHOROID", "RETINA"]:
            f.write(f"*SOLID SECTION, ELSET={zone}, MATERIAL=SCLERA_OGDEN\n")
        f.write("**\n")

        # ---- BOUNDARY CONDITIONS ----
        # Nota: a calote de 90 graus e aberta no "equador" (sem iris/lente
        # solidos que fechariam a estrutura). Os dois planos de simetria por
        # si so NAO removem o modo de corpo rigido de translacao ao longo do
        # eixo y (linha de intersecao dos planos x=0 e z=0, onde ficam os nos
        # NAXIS/NPOSTERIOR_POLE). Mesma convencao do caso de referencia
        # cases/fea-sim/ccx/fea-sim.inp (AXIS + POSTERIOR_POLE).
        f.write("** SIMETRIA\n")
        f.write("** SYMMETRY_0: plano z=0, restringir uz (DOF 3)\n")
        f.write("*BOUNDARY\n")
        f.write("NSYMMETRY_0, 3, 3, 0.0\n")
        f.write("**\n")
        f.write("** SYMMETRY_90: plano x=0, restringir ux (DOF 1)\n")
        f.write("*BOUNDARY\n")
        f.write("NSYMMETRY_90, 1, 1, 0.0\n")
        f.write("**\n")
        f.write("** AXIS: reforco nos nos do eixo (intersecao dos planos)\n")
        f.write("*BOUNDARY\n")
        f.write("NAXIS, 1, 1, 0.0\n")
        f.write("NAXIS, 3, 3, 0.0\n")
        f.write("**\n")
        f.write("** POSTERIOR_POLE: remove o modo de corpo rigido ao longo do eixo y (DOF 2)\n")
        f.write("*BOUNDARY\n")
        f.write("NPOSTERIOR_POLE, 2, 2, 0.0\n")
        f.write("**\n")

        # ---- STEP: Pressao interna ----
        f.write("** CARREGAMENTO: pressao interna de 15 a 50 mmHg\n")
        f.write(f"** P_basal = {P_BASAL:.2f} Pa (15 mmHg)\n")
        f.write(f"** P_final = {P_FINAL:.2f} Pa (50 mmHg)\n")
        f.write("**\n")

        # Step 1: apply basal pressure (equilibrium)
        f.write("*STEP, NLGEOM\n")
        f.write("*STATIC\n")
        f.write(f"0.0625, 1.0, 1e-8, 0.1\n")
        f.write("**\n")
        f.write("*DLOAD\n")
        f.write(f"SINNER, P, {P_BASAL:.4f}\n")
        f.write("**\n")
        f.write("*NODE FILE\n")
        f.write("U\n")
        f.write("*EL FILE\n")
        f.write("S, E\n")
        f.write("*END STEP\n")
        f.write("**\n")

        # Step 2: ramp to peak pressure
        f.write("*STEP, NLGEOM\n")
        f.write("*STATIC\n")
        f.write(f"0.0625, 1.0, 1e-8, 0.1\n")
        f.write("**\n")
        f.write("*DLOAD\n")
        f.write(f"SINNER, P, {P_FINAL:.4f}\n")
        f.write("**\n")
        f.write("*NODE FILE\n")
        f.write("U\n")
        f.write("*EL FILE\n")
        f.write("S, E\n")
        f.write("*END STEP\n")

    print(f"Arquivo .inp completo gerado: {inp_path}")
    return inp_path


# ---------------------------------------------------------------------------
# LOCALIZAR BINARIO ccx (mesma logica de wp1.2/scripts/ccx_utils.py)
# ---------------------------------------------------------------------------
import shutil


def ccx_bin():
    """Localiza o binario do CalculiX no container.

    No container 'fsi' deste projeto o binario se chama ccx_preCICE
    (nao 'ccx'). Mesma logica usada em wp1.2/scripts/ccx_utils.py.
    """
    override = os.environ.get("CCX_BIN", "").strip()
    if override:
        return override

    for name in ("ccx_preCICE", "ccx", "ccx_2.23", "ccx_2.21", "ccx_2.20"):
        found = shutil.which(name)
        if found:
            return found

    for p in ("/opt/calculix/bin/ccx_preCICE", "/opt/homebrew/bin/ccx_2.23"):
        if Path(p).exists():
            return p

    raise RuntimeError("CalculiX (ccx / ccx_preCICE) nao encontrado no PATH")


# ---------------------------------------------------------------------------
# EXECUTAR ccx
# ---------------------------------------------------------------------------
def run_ccx(inp_path):
    """Executa CalculiX e captura a saida."""
    job = inp_path.stem
    work_dir = inp_path.parent

    try:
        ccx = ccx_bin()
    except RuntimeError as e:
        print(f"  ERRO: {e}")
        return False

    print(f"\nExecutando ccx: {job}")
    print(f"  Binario: {ccx}")
    print(f"  Diretorio: {work_dir}")

    try:
        result = subprocess.run(
            [ccx, "-i", job],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=600,
        )
        # Save log
        log_path = work_dir / f"{job}.log"
        with open(log_path, "w") as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(result.stderr)

        print(f"  Return code: {result.returncode}")
        print(f"  Log salvo em: {log_path}")

        if result.returncode != 0:
            print(f"  ERRO: ccx falhou!")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False

        # Check for convergence
        if "*ERROR" in result.stdout or "*ERROR" in result.stderr:
            print("  ERRO: ccx reportou erro(s)")
            return False

        # Check for .frd output
        frd_path = work_dir / f"{job}.frd"
        if frd_path.exists():
            print(f"  Resultado .frd: {frd_path} ({frd_path.stat().st_size} bytes)")
        else:
            print(f"  AVISO: {frd_path} nao foi gerado")
            return False

        return True

    except FileNotFoundError:
        print("  ERRO: ccx nao encontrado no PATH")
        print("  Verifique se esta rodando dentro do Docker: docker compose run --rm fsi ...")
        return False
    except subprocess.TimeoutExpired:
        print("  ERRO: ccx excedeu timeout de 600s")
        return False


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("WP1.5 Fase 1: Teste de Pipeline Anatomico")
    print("=" * 60)
    print()
    print(f"Material: Ogden N=1 (Friedenwald WP1.2)")
    print(f"  mu1 = {MU1/1e6:.4f} MPa, alpha1 = {ALPHA1:.4f}, D1 = {D1*1e6:.4f} 1/MPa")
    print(f"Pressao: {P_BASAL:.1f} Pa (15 mmHg) -> {P_FINAL:.1f} Pa (50 mmHg)")
    print()

    # Generate .inp
    inp_path = generate_full_inp(MESH_INP, OUTPUT_DIR, JOB_NAME)

    # Run ccx
    success = run_ccx(inp_path)

    # Save metadata
    meta = {
        "job_name": JOB_NAME,
        "mesh_inp": str(MESH_INP),
        "material": {
            "type": "Ogden N=1",
            "source": "Friedenwald fit WP1.2",
            "mu1_MPa": MU1 / 1e6,
            "alpha1": ALPHA1,
            "D1_invMPa": D1 * 1e6,
            "note": "Mesmo material para todas as regioes (Fase 1 = teste pipeline)"
        },
        "pressure": {
            "P_basal_Pa": P_BASAL,
            "P_basal_mmHg": 15.0,
            "P_final_Pa": P_FINAL,
            "P_final_mmHg": 50.0,
            "source": "Plano de tese, WP2"
        },
        "symmetry": {
            "SYMMETRY_0": "plano z=0, DOF 3 = 0",
            "SYMMETRY_90": "plano x=0, DOF 1 = 0",
            "AXIS": "reforco nos nos do eixo, DOF 1 = 0 e DOF 3 = 0",
            "POSTERIOR_POLE": "remove modo de corpo rigido (translacao eixo y), DOF 2 = 0 (mesma convencao de cases/fea-sim/ccx/fea-sim.inp)"
        },
        "ccx_converged": success,
        "geometry_source": "Lamminsalo et al. 2018 / Missel 2012 (coelho)"
    }
    meta_path = OUTPUT_DIR / f"{JOB_NAME}_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nMetadados salvos em: {meta_path}")

    if success:
        print("\n*** Pipeline OK — prosseguir com postprocess_frd.py ***")
    else:
        print("\n*** Pipeline FALHOU — verificar o .log ***")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
