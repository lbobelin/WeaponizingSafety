#!/bin/bash
#SBATCH --job-name=hfe
#SBATCH --output=logs/hfe_%A_%a.out
#SBATCH --error=logs/hfe_%A_%a.err
#SBATCH --time=00:15:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p logs results/raw
# Configure the Python environment for the target cluster, e.g.:
# module load python/3.11
# source .venv/bin/activate
RUNS=${RUNS:-30}
python experiments/run_config.py --campaign campaign.csv --index "${SLURM_ARRAY_TASK_ID}" --runs "$RUNS"
