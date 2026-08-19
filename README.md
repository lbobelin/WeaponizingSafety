# Human Fallback Exhaustion — Experimental Artifact

Anonymous research artifact accompanying a paper on **human fallback exhaustion attacks in autonomous maritime fleets**. The repository contains the complete simulator and all experiment definitions used for RQ1–RQ4, including the refined threshold and paired prioritization analyses.

No platform-specific exploit is implemented. The artifact evaluates the fleet-level consequence of successfully induced fallback requests under a discrete-time Monte-Carlo model.

## Repository layout

```text
.
├── hfe_sim/                 # discrete-time fleet simulator
├── experiments/             # campaign generation, execution, aggregation, plotting
├── campaign.csv             # generated complete parameter matrix
├── results/raw/             # one CSV per configuration (generated)
├── results/summary/         # aggregate and paired statistics (generated)
├── figures/                 # PDF figures (generated)
├── run_local.sh             # complete local workflow
├── submit_slurm.sh          # submit full SLURM array
├── slurm_array.sh           # one array task = one parameter configuration
└── postprocess_slurm.sh     # aggregate and plot after SLURM completion
```

## Requirements

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduce the complete campaign

Generate the unified experiment matrix:

```bash
python experiments/generate_campaign.py
```

The matrix contains **742 configurations**. With the default 30 repetitions, the full campaign comprises **22,260 Monte-Carlo runs**.

For a quick smoke test:

```bash
python experiments/run_config.py --index 0 --runs 3
```

For the complete local workflow:

```bash
./run_local.sh 30
```

This generates raw CSV files, aggregate statistics, paired-policy comparisons, and all figures.

## SLURM execution

Edit only the environment setup lines in `slurm_array.sh` if the cluster requires modules or a virtual environment. Then run:

```bash
./submit_slurm.sh
```

Each array task executes all repetitions for one parameter configuration. After the array has completed:

```bash
./postprocess_slurm.sh
```

The maximum array concurrency is set to 100 in `submit_slurm.sh` and can be adjusted to the local cluster policy.

## Experiment map

| Experiment | Purpose | Main parameters |
|---|---|---|
| `RQ1_core` | Coarse exhaustion characterization | `N`, `H`, `B`, `tau` |
| `RQ1_threshold` | Refined exhaustion transition | `p_attack`, `H`, `tau`, `N` |
| `RQ2_strategies` | Compare attacker targeting strategies | random, criticality-first, fallback-first, capacity-aware |
| `RQ3_dependencies` | Measure mission-level amplification | independent, coordination, coverage, critical-unit profiles |
| `RQ4_architecture` | Test architectural resilience | capacity, persistence, safe mode, allocation policy |
| `RQ4_priority` | Paired FIFO vs criticality-aware allocation | `p_attack`, `H`, `tau` |

The refined RQ1 sweep also reports the first-order offered-load indicator

\[
\rho_A = \frac{B p_A \tau}{H},
\]

which is used as an explanatory load metric rather than a hard analytical threshold.

## Output files

`results/summary/summary.csv` contains mean, standard deviation, median, count, and 95% confidence interval for the principal metrics. `results/summary/rq4_priority_paired_runs.csv` contains run-by-run paired differences between FIFO and criticality-aware allocation.

The figure generator produces, among others:

- `rq1_threshold_tau6.pdf` and `rq1_threshold_tau12.pdf` — saturation transition;
- `rq1_offered_load.pdf` — offered-load diagnostic;
- `rq2_strategy_comparison.pdf` — attacker strategy comparison;
- `rq3_amplification.pdf` — mission-loss amplification;
- `rq4_capacity_resilience.pdf` — capacity/safe-mode sensitivity;
- `rq4_priority_gain_H5.pdf` — paired prioritization gain used in the paper.

## Metrics

The simulator reports cumulative mission loss, saturation fraction, excess fallback demand, denied-request epochs, time to first saturation, attack efficiency, indirect loss, and mission-loss amplification. The amplification factor is computed as total fleet mission loss divided by loss directly attributable to currently attacked vessels; it is reported only when at least one induced-fallback action succeeds.

## Reproducibility and seeds

The original core campaign uses independent deterministic seeds derived from the configuration index. The refined threshold and prioritization experiments use common random numbers (`seed_base + run`) to reduce comparison noise; the FIFO/criticality comparison is therefore exactly paired by seed. Both policies see the same stochastic realization for a given run.

## Modeling scope

Human fallback is represented by a fixed capacity `H`. The simulator intentionally does **not** model cognitive workload, fatigue, individual operator skill, or a specific remote-operation-center interface. Loss values are normalized synthetic quantities and should not be interpreted as calibrated monetary or safety-risk estimates.

## Anonymous-review note

The artifact intentionally contains no author names, affiliations, institutional paths, account identifiers, acknowledgements, or repository URLs. If hosted for double-blind review, use an anonymous repository/account or the conference's anonymous artifact-hosting mechanism; repository ownership itself is outside the contents of this archive.
