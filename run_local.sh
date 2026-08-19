#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
RUNS=${1:-30}
python "$ROOT/experiments/generate_campaign.py"
N=$(($(wc -l < "$ROOT/campaign.csv")-1))
mkdir -p "$ROOT/results/raw"
for ((i=0;i<N;i++)); do
  python "$ROOT/experiments/run_config.py" --campaign "$ROOT/campaign.csv" --index "$i" --runs "$RUNS"
done
python "$ROOT/experiments/aggregate.py"
python "$ROOT/experiments/plot_results.py"
