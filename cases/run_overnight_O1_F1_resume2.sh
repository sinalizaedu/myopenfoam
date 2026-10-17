#!/bin/bash
# Resume from sim5 O1 experiment (calibrations done for sim4/sim5 O1).
set -euo pipefail

NP="${NP:-4}"
MASTER_LOG="/simulation/run_overnight_O1_F1_resume2.log"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" | tee -a "$MASTER_LOG"
}

save_calib() {
    local case_dir="$1" mesh="$2"
    if [ -f "${case_dir}/calibration/baseline_iop.yaml" ]; then
        cp -f "${case_dir}/calibration/baseline_iop.yaml" \
            "${case_dir}/calibration/baseline_${mesh}.yaml"
        log "saved ${case_dir}/calibration/baseline_${mesh}.yaml"
    fi
}

calibrate_case() {
    local case_dir="$1" mesh="$2"
    log "===== CALIBRATE ${case_dir} MESH=${mesh} ====="
    (
        cd "$case_dir"
        mkdir -p mesh_independence
        python3 scripts/calibrate_d_tm.py --mesh "$mesh" \
            2>&1 | tee -a "mesh_independence/calibrate_${mesh}.log"
    )
    save_calib "$case_dir" "$mesh"
}

sim4_experiment() {
    local mesh="$1"
    log "===== sim4 experiment MESH=${mesh} np=${NP} ====="
    (
        cd /simulation/doc-g2-sim4
        ./scripts/run_experiment_1h.sh "$mesh" "$NP" \
            2>&1 | tee -a "mesh_independence/run_${mesh}_experiment_1h.log"
    )
}

sim5_experiment() {
    local mesh="$1"
    log "===== sim5 experiment MESH=${mesh} np=${NP} ====="
    (
        cd /simulation/T1: Volume vs Patch/doc-g2-sim5
        ./scripts/run_experiment_1h.sh "$mesh" "$NP" \
            2>&1 | tee -a "mesh_independence/run_${mesh}_experiment_1h.log"
    )
}

log "=== RESUME2: sim5 O1 exp + F1 all np=${NP} ==="

sim5_experiment O1

calibrate_case /simulation/doc-g2-sim4 F1
sim4_experiment F1
calibrate_case /simulation/T1: Volume vs Patch/doc-g2-sim5 F1
sim5_experiment F1

log "=== RESUME2 COMPLETE ==="
