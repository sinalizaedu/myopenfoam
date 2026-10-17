#!/usr/bin/env python3
"""
postprocess_frd.py
-----------------
Pos-processamento do .frd do CalculiX:
- Extrai deslocamentos (U) e tensoes (S) do ultimo step
- Verifica ordem de grandeza (deslocamentos em um a centenas de um)
- Calcula deslocamento maximo por regiao
- Salva resultados em JSON

Uso dentro do Docker:
    docker compose run --rm fsi bash -lc \
      'cd /simulation/<PASTA>/scripts && python3 postprocess_frd.py'

Referências:
    Formato .frd: CalculiX documentation, section "Results file format"
"""

import sys
import os
import json
import re
from pathlib import Path
from collections import defaultdict
import numpy as np

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("../output_test")
JOB_NAME = "eye_anat_test"
FRD_FILE = OUTPUT_DIR / f"{JOB_NAME}.frd"
MESH_INP = Path("../mesh/eye_anatomical.inp")
RESULTS_FILE = OUTPUT_DIR / "test_results.json"


# ---------------------------------------------------------------------------
# PARSER .frd (formato CalculiX)
# ---------------------------------------------------------------------------
def parse_frd(filepath):
    """Parse CalculiX .frd file.

    Returns
    -------
    nodes : dict {node_id: (x, y, z)}
    steps : list of {
        'step': int, 'time': float,
        'displacements': {node_id: (ux, uy, uz)},
        'stresses': {node_id: (sxx, syy, szz, sxy, sxz, syz)}
    }
    """
    if not filepath.exists():
        print(f"ERRO: {filepath} nao encontrado")
        sys.exit(1)

    nodes = {}
    steps = []
    current_step = None
    current_field = None  # 'DISP' or 'STRESS'
    current_data = {}

    with open(filepath) as f:
        for line in f:
            # Node coordinates block
            if line.startswith("    2C"):
                # Node definition: format is fixed-width
                # Cols: 1-3=" 2C", 4-13=node_id, 14-25=x, 26-37=y, 38-49=z
                try:
                    nid = int(line[3:13])
                    x = float(line[13:25])
                    y = float(line[25:37])
                    z = float(line[37:49])
                    nodes[nid] = (x, y, z)
                except (ValueError, IndexError):
                    pass

            # Step marker
            elif line.startswith("    1PSTEP"):
                if current_step is not None and current_field and current_data:
                    if current_field == "DISP":
                        current_step["displacements"] = current_data
                    elif current_field == "STRESS":
                        current_step["stresses"] = current_data
                    current_data = {}
                    current_field = None

            # New results block header
            elif line.startswith(" -4  DISP"):
                current_field = "DISP"
                current_data = {}

            elif line.startswith(" -4  STRESS"):
                current_field = "STRESS"
                current_data = {}

            # Step/time info
            elif line.startswith(" -5  STEP"):
                # Save previous step data
                if current_step is not None:
                    if current_field and current_data:
                        if current_field == "DISP":
                            current_step["displacements"] = current_data
                        elif current_field == "STRESS":
                            current_step["stresses"] = current_data
                        current_data = {}
                        current_field = None
                    steps.append(current_step)

                # Parse step number and time
                try:
                    parts = line.split()
                    step_num = int(float(parts[2]))
                except (IndexError, ValueError):
                    step_num = len(steps) + 1

                current_step = {
                    "step": step_num,
                    "time": 0.0,
                    "displacements": {},
                    "stresses": {},
                }

            elif line.startswith(" -5  TIME") and current_step:
                try:
                    parts = line.split()
                    current_step["time"] = float(parts[2])
                except (IndexError, ValueError):
                    pass

            # Data values
            elif line.startswith(" -1") and current_field:
                try:
                    nid = int(line[3:13])
                    vals = []
                    # Fixed-width fields of 12 chars each starting at col 13
                    pos = 13
                    while pos + 12 <= len(line):
                        val_str = line[pos:pos+12].strip()
                        if val_str:
                            vals.append(float(val_str))
                        pos += 12

                    if current_field == "DISP" and len(vals) >= 3:
                        current_data[nid] = (vals[0], vals[1], vals[2])
                    elif current_field == "STRESS" and len(vals) >= 6:
                        current_data[nid] = tuple(vals[:6])
                except (ValueError, IndexError):
                    pass

    # Save last step
    if current_step is not None:
        if current_field and current_data:
            if current_field == "DISP":
                current_step["displacements"] = current_data
            elif current_field == "STRESS":
                current_step["stresses"] = current_data
        steps.append(current_step)

    return nodes, steps


# ---------------------------------------------------------------------------
# PARSE MESH .inp to get node->zone mapping
# ---------------------------------------------------------------------------
def parse_elsets_and_nodes(mesh_inp):
    """Parse .inp to map nodes to tissue zones via ELSETs and elements."""
    if not mesh_inp.exists():
        print(f"AVISO: {mesh_inp} nao encontrado, sem mapeamento por zona")
        return {}

    elements = {}  # eid -> [node_ids]
    elsets = {}    # zone_name -> [eids]
    current_elset = None

    with open(mesh_inp) as f:
        mode = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("**"):
                continue

            if line.startswith("*ELEMENT"):
                mode = "element"
                continue
            elif line.startswith("*ELSET"):
                mode = "elset"
                match = re.search(r"ELSET=(\w+)", line, re.IGNORECASE)
                if match:
                    current_elset = match.group(1)
                    if current_elset not in elsets:
                        elsets[current_elset] = []
                continue
            elif line.startswith("*") and not line.startswith("**"):
                mode = None
                current_elset = None
                continue

            if mode == "element":
                parts = [int(x) for x in line.replace(",", " ").split()]
                if len(parts) >= 9:  # eid + 8 nodes for C3D8
                    elements[parts[0]] = parts[1:]

            elif mode == "elset" and current_elset:
                # Check if it references other ELSETs
                if any(c.isalpha() for c in line.replace(",", "").strip()):
                    # References to other elsets (e.g., "CORNEA, SCLERA, ...")
                    continue
                parts = [int(x) for x in line.replace(",", " ").split() if x]
                elsets[current_elset].extend(parts)

    # Map node -> zone
    node_zones = {}
    for zone_name in ["CORNEA", "SCLERA", "CHOROID", "RETINA"]:
        if zone_name in elsets:
            for eid in elsets[zone_name]:
                if eid in elements:
                    for nid in elements[eid]:
                        if nid not in node_zones:
                            node_zones[nid] = zone_name

    return node_zones


# ---------------------------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------------------------
def analyze_results(nodes, steps, node_zones):
    """Analyze displacement and stress results."""
    results = {}

    for i, step in enumerate(steps):
        step_key = f"step_{step['step']}"
        step_result = {
            "step": step["step"],
            "time": step["time"],
        }

        # Displacements
        if step["displacements"]:
            disp = step["displacements"]
            all_u = np.array(list(disp.values()))
            u_mag = np.sqrt(np.sum(all_u**2, axis=1))

            step_result["displacement"] = {
                "n_nodes": len(disp),
                "u_max_m": float(np.max(u_mag)),
                "u_max_um": float(np.max(u_mag) * 1e6),
                "u_mean_um": float(np.mean(u_mag) * 1e6),
                "ux_range_um": [float(all_u[:,0].min()*1e6), float(all_u[:,0].max()*1e6)],
                "uy_range_um": [float(all_u[:,1].min()*1e6), float(all_u[:,1].max()*1e6)],
                "uz_range_um": [float(all_u[:,2].min()*1e6), float(all_u[:,2].max()*1e6)],
            }

            # Per-zone analysis
            if node_zones:
                zone_stats = {}
                for zone_name in ["CORNEA", "SCLERA", "CHOROID", "RETINA"]:
                    zone_nids = [n for n in disp if node_zones.get(n) == zone_name]
                    if zone_nids:
                        zone_u = np.array([disp[n] for n in zone_nids])
                        zone_mag = np.sqrt(np.sum(zone_u**2, axis=1))
                        zone_stats[zone_name] = {
                            "n_nodes": len(zone_nids),
                            "u_max_um": float(np.max(zone_mag) * 1e6),
                            "u_mean_um": float(np.mean(zone_mag) * 1e6),
                        }
                step_result["displacement"]["per_zone"] = zone_stats

            # Sanity check: displacement order of magnitude
            u_max_um = step_result["displacement"]["u_max_um"]
            if u_max_um < 0.01:
                step_result["displacement"]["sanity"] = "AVISO: deslocamento muito pequeno (<0.01 um)"
            elif u_max_um > 1e6:
                step_result["displacement"]["sanity"] = "ERRO: deslocamento absurdo (>1 m)"
            elif u_max_um > 1e4:
                step_result["displacement"]["sanity"] = "AVISO: deslocamento grande (>10 mm)"
            else:
                step_result["displacement"]["sanity"] = "OK: ordem de grandeza razoavel"

        # Stresses
        if step["stresses"]:
            stress = step["stresses"]
            all_s = np.array(list(stress.values()))
            # Von Mises
            sxx, syy, szz = all_s[:,0], all_s[:,1], all_s[:,2]
            sxy, sxz, syz = all_s[:,3], all_s[:,4], all_s[:,5]
            vm = np.sqrt(0.5 * ((sxx-syy)**2 + (syy-szz)**2 + (szz-sxx)**2
                                + 6*(sxy**2 + sxz**2 + syz**2)))

            step_result["stress"] = {
                "n_nodes": len(stress),
                "von_mises_max_Pa": float(np.max(vm)),
                "von_mises_max_kPa": float(np.max(vm) / 1e3),
                "von_mises_mean_kPa": float(np.mean(vm) / 1e3),
            }

        results[step_key] = step_result

    return results


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("WP1.5 Pos-processamento do .frd")
    print("=" * 60)
    print()

    # Parse .frd
    print(f"Lendo {FRD_FILE}...")
    nodes, steps = parse_frd(FRD_FILE)
    print(f"  Nos: {len(nodes)}")
    print(f"  Steps: {len(steps)}")

    if not steps:
        print("ERRO: nenhum step encontrado no .frd")
        sys.exit(1)

    # Parse mesh for zone mapping
    print(f"\nLendo zonas de {MESH_INP}...")
    node_zones = parse_elsets_and_nodes(MESH_INP)
    print(f"  Nos mapeados a zonas: {len(node_zones)}")

    # Analyze
    print("\nAnalisando resultados...")
    results = analyze_results(nodes, steps, node_zones)

    # Print summary
    for step_key, step_data in results.items():
        print(f"\n--- {step_key} (time={step_data['time']:.4f}) ---")
        if "displacement" in step_data:
            d = step_data["displacement"]
            print(f"  Deslocamento max: {d['u_max_um']:.2f} um ({d['u_max_m']:.2e} m)")
            print(f"  Deslocamento medio: {d['u_mean_um']:.2f} um")
            print(f"  Sanity check: {d['sanity']}")
            if "per_zone" in d:
                for zone, zs in d["per_zone"].items():
                    print(f"    {zone}: max={zs['u_max_um']:.2f} um, mean={zs['u_mean_um']:.2f} um")
        if "stress" in step_data:
            s = step_data["stress"]
            print(f"  Von Mises max: {s['von_mises_max_kPa']:.2f} kPa")
            print(f"  Von Mises medio: {s['von_mises_mean_kPa']:.2f} kPa")

    # Save
    final = {
        "job": JOB_NAME,
        "frd_file": str(FRD_FILE),
        "n_nodes_frd": len(nodes),
        "n_steps": len(steps),
        "results": results,
        "geometry_source": "Lamminsalo et al. 2018 / Missel 2012 (coelho)",
        "material": "Ogden N=1 (Friedenwald WP1.2) — mesmo para todas as regioes",
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(final, f, indent=2)
    print(f"\nResultados salvos em: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
