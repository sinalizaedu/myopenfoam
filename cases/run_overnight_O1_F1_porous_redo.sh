#!/bin/bash
# Redo O1+F1 after vitreous_zone porous fix (ymin -1.5 mm → -3.60 mm).
# After each mesh experiment, archives fluid/ → runs/<MESH>/ with <MESH>.foam
# so ParaView can open O1 and F1 independently (no overwrite).
#
# Run inside Docker:
#   docker compose run --rm --user ubuntu fsi bash -lc \
#     '/simulation/run_overnight_O1_F1_porous_redo.sh'
set -euo pipefail

NP="${NP:-4}"
MASTER_LOG="/simulation/run_overnight_O1_F1_porous_redo.log"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

save_calib() {
    local case_dir="$1" mesh="$2"
    mkdir -p "${case_dir}/calibration"
    if [ -f "${case_dir}/calibration/baseline_iop.yaml" ]; then
        cp -f "${case_dir}/calibration/baseline_iop.yaml" \
            "${case_dir}/calibration/baseline_${mesh}.yaml"
        cp -f "${case_dir}/calibration/baseline_iop.yaml" \
            "${case_dir}/calibration/baseline_${mesh}_porousRedo.yaml"
        log "saved ${case_dir}/calibration/baseline_${mesh}.yaml (+ _porousRedo)"
    fi
}

archive_run() {
    local case_dir="$1" mesh="$2"
    log "===== ARCHIVE ${case_dir} → runs/${mesh}/ ====="
    (
        cd "$case_dir"
        chmod +x scripts/archive_mesh_run.sh
        ./scripts/archive_mesh_run.sh "$mesh"
    )
}

calibrate_case() {
    local case_dir="$1" mesh="$2"
    log "===== CALIBRATE ${case_dir} MESH=${mesh} (IOP_AC≈15, new vitreous porous) ====="
    (
        cd "$case_dir"
        mkdir -p mesh_independence
        python3 scripts/calibrate_d_tm.py --mesh "$mesh" \
            2>&1 | tee "mesh_independence/calibrate_${mesh}_porousRedo.log"
    )
    save_calib "$case_dir" "$mesh"
}

sim4_experiment() {
    local mesh="$1"
    log "===== sim4 IVI+ACP experiment MESH=${mesh} np=${NP} ====="
    (
        cd /simulation/doc-g2-sim4
        chmod +x scripts/run_experiment_1h.sh
        ./scripts/run_experiment_1h.sh "$mesh" "$NP" \
            2>&1 | tee "mesh_independence/run_${mesh}_experiment_1h_porousRedo.log"
    )
    archive_run /simulation/doc-g2-sim4 "$mesh"
}

sim5_pipeline() {
    local mesh="$1"
    calibrate_case /simulation/T1: Volume vs Patch/doc-g2-sim5 "$mesh"
    log "===== sim5 Model C experiment MESH=${mesh} np=${NP} ====="
    (
        cd /simulation/T1: Volume vs Patch/doc-g2-sim5
        chmod +x scripts/run_experiment_1h.sh
        ./scripts/run_experiment_1h.sh "$mesh" "$NP" \
            2>&1 | tee "mesh_independence/run_${mesh}_experiment_1h_porousRedo.log"
    )
    archive_run /simulation/T1: Volume vs Patch/doc-g2-sim5 "$mesh"
}

log "=== POROUS-REDO BATCH START np=${NP} ==="
log "vitreous_zone box ymin = -3.60 mm (full vitreous to hyaloid / AC boundary)"
log "results archived under runs/<MESH>/<MESH>.foam after each experiment"

# --- O1 ---
calibrate_case /simulation/doc-g2-sim4 O1
sim4_experiment O1
sim5_pipeline O1

# --- F1 ---
calibrate_case /simulation/doc-g2-sim4 F1
sim4_experiment F1
sim5_pipeline F1

log "=== POROUS-REDO BATCH COMPLETE ==="
