#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python experiments/generate_campaign.py
N=$(($(wc -l < campaign.csv)-1))
echo "Submitting $N parameter configurations"
sbatch --array=0-$((N-1))%100 slurm_array.sh
