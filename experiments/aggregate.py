#!/usr/bin/env python3
"""Aggregate raw per-configuration CSV files and compute confidence intervals."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw_dir = ROOT / "results" / "raw"
summary_dir = ROOT / "results" / "summary"
summary_dir.mkdir(parents=True, exist_ok=True)
files = sorted(raw_dir.glob("config_*.csv"))
if not files:
    raise SystemExit("No raw results found. Run experiments first.")

df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
df.to_csv(summary_dir / "all_runs.csv", index=False)
metrics = [
    "mission_loss", "sat_fraction", "excess_demand", "denied_request_epochs",
    "time_to_first_saturation", "attack_efficiency", "amplification", "indirect_loss",
]
group_cols = [c for c in [
    "experiment", "N", "H", "B", "tau", "p_genuine", "p_attack", "strategy",
    "profile", "priority", "safe_mode", "T", "offered_load_ratio", "seed_policy",
] if c in df]
agg = df.groupby(group_cols, dropna=False)[metrics].agg(["mean", "std", "median", "count"]).reset_index()
agg.columns = ["_".join(x).rstrip("_") if isinstance(x, tuple) else x for x in agg.columns]
for m in metrics:
    n = agg[f"{m}_count"].clip(lower=1)
    agg[f"{m}_ci95"] = 1.96 * agg[f"{m}_std"].fillna(0) / np.sqrt(n)
agg.to_csv(summary_dir / "summary.csv", index=False)

# Paired RQ4 allocation-policy comparison.
a2 = df[df.experiment == "RQ4_priority"].copy()
if len(a2):
    keys = ["N", "H", "B", "tau", "p_genuine", "p_attack", "strategy", "profile", "safe_mode", "T", "run", "seed"]
    piv = a2.pivot_table(index=keys, columns="priority",
                         values=["mission_loss", "sat_fraction", "denied_request_epochs"], aggfunc="first").reset_index()
    for m in ["mission_loss", "sat_fraction", "denied_request_epochs"]:
        if (m, "fifo") in piv.columns and (m, "criticality") in piv.columns:
            piv[(m, "delta_fifo_minus_criticality")] = piv[(m, "fifo")] - piv[(m, "criticality")]
    piv.columns = ["_".join([str(z) for z in x if str(z) != ""]).rstrip("_") if isinstance(x, tuple) else x for x in piv.columns]
    piv.to_csv(summary_dir / "rq4_priority_paired_runs.csv", index=False)

print(f"Aggregated {len(df)} runs from {len(files)} configurations.")
