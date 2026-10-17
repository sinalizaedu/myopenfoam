#!/bin/bash
# Overnight batch: O1 + F1 calibrated baseline (IOP_AC≈15) + sim4 IVI/ACP + sim5 Model C.
# Run inside Docker:
#   docker compose run --rm --user ubuntu fsi bash -lc \
#     '/simulation/run_overnight_O1_F1_batch.sh' 2>&1 | tee cases/run_overnight_O1_F1.log
set -euo pipefail

NP="${NP:-4}"
MASTER_LOG="/simulation/run_overnight_O1_F1.log"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

save_calib() {
    local case_dir="$1" mesh="$2"
    mkdir -p "${case_dir}/calibration"
    if [ -f "${case_dir}/calibration/baseline_iop.yaml" ]; then
        cp -f "${case_dir}/calibration/baseline_iop.yaml" \
            "${case_dir}/calibration/baseline_${mesh}.yaml"
        log "saved ${case_dir}/calibration/baseline_${mesh}.yaml"
    fi
}

calibrate_case() {
    local case_dir="$1" mesh="$2"
    log "===== CALIBRATE ${case_dir} MESH=${mesh} (IOP_AC≈15) ====="
    (
        cd "$case_dir"
        mkdir -p mesh_independence
        python3 scripts/calibrate_d_tm.py --mesh "$mesh" \
            2>&1 | tee "mesh_independence/calibrate_${mesh}.log"
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
            2>&1 | tee "mesh_independence/run_${mesh}_experiment_1h.log"
    )
}

sim5_pipeline() {
    local mesh="$1"
    calibrate_case /simulation/T1: Volume vs Patch/doc-g2-sim5 "$mesh"
    log "===== sim5 Model C experiment MESH=${mesh} np=${NP} ====="
    (
        cd /simulation/T1: Volume vs Patch/doc-g2-sim5
        chmod +x scripts/run_experiment_1h.sh
        ./scripts/run_experiment_1h.sh "$mesh" "$NP" \
            2>&1 | tee "mesh_independence/run_${mesh}_experiment_1h.log"
    )
}

log "=== OVERNIGHT BATCH START np=${NP} ==="

# --- O1 ---
calibrate_case /simulation/doc-g2-sim4 O1
sim4_experiment O1
sim5_pipeline O1

# --- F1 ---
calibrate_case /simulation/doc-g2-sim4 F1
sim4_experiment F1
sim5_pipeline F1

log "=== OVERNIGHT BATCH COMPLETE ==="
