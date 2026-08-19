#!/usr/bin/env python3
"""Generate the complete experiment matrix used by the paper."""
from __future__ import annotations
import itertools
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "campaign.csv"
rows: list[dict] = []


def add(experiment: str, seed_policy: str = "independent", **grid):
    keys = list(grid)
    vals = [v if isinstance(v, (list, tuple)) else [v] for v in grid.values()]
    for comb in itertools.product(*vals):
        d = dict(zip(keys, comb))
        d["experiment"] = experiment
        d["seed_policy"] = seed_policy
        rows.append(d)


# Common defaults used by the main campaign.
common = dict(T=120, p_genuine=0.002, p_attack=0.9, priority="fifo", safe_mode=False)

# RQ1 (coarse characterization): fleet size, capacity, attack budget, persistence.
add(
    "RQ1_core",
    N=[10, 20, 50, 100], H=[1, 3, 5], B=[0, 1, 2], tau=[2, 6, 12],
    strategy="fallback_first", profile="none", **common,
)

# RQ2: attacker strategy comparison.
add(
    "RQ2_strategies",
    N=[20, 50, 100], H=[2, 5], B=[1, 2], tau=[6, 12],
    strategy=["random", "criticality_first", "fallback_first", "capacity_aware"],
    profile="critical-unit", **common,
)

# RQ3: mission-dependency amplification.
add(
    "RQ3_dependencies",
    N=[20, 50, 100], H=[2, 5], B=[1, 2], tau=8,
    strategy="capacity_aware",
    profile=["none", "coordination", "coverage", "critical-unit"], **common,
)

# RQ4: architectural resilience levers under stressed conditions.
add(
    "RQ4_architecture",
    N=[50, 100], H=[1, 3, 5], B=2, tau=[4, 8, 12],
    strategy="capacity_aware", profile="coordination",
    p_genuine=0.002, p_attack=[0.6, 0.9],
    priority=["fifo", "criticality"], safe_mode=[False, True], T=120,
)

# RQ1 refined threshold sweep. Common random numbers reduce noise across the
# attack-probability curve and make capacity/persistence comparisons cleaner.
p_grid = [0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 0.90]
add(
    "RQ1_threshold", seed_policy="common",
    N=[20, 50, 100], H=[1, 3, 5], B=1, tau=[6, 12],
    p_genuine=0.002, p_attack=p_grid,
    strategy="fallback_first", profile="none", priority="fifo",
    safe_mode=False, T=120,
)

# RQ4 refined prioritization experiment. FIFO and criticality-aware policies
# use paired random seeds for direct policy comparison.
add(
    "RQ4_priority", seed_policy="common",
    N=[50, 100], H=[2, 5], B=1, tau=[6, 12],
    p_genuine=0.002, p_attack=[0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.75],
    strategy="capacity_aware", profile="critical-unit",
    priority=["fifo", "criticality"], safe_mode=False, T=120,
)

df = pd.DataFrame(rows)
# Strategy is irrelevant in the no-attack rows; canonicalize before de-duplication.
df.loc[df.B == 0, "strategy"] = "none"
df = df.drop_duplicates().reset_index(drop=True)
df["offered_load_ratio"] = (df.B * df.p_attack * df.tau / df.H).astype(float)
df.to_csv(OUT, index_label="config_id")
print(f"Wrote {len(df)} configurations to {OUT}")
print(df.groupby("experiment").size().to_string())
