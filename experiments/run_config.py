#!/usr/bin/env python3
"""Run all Monte-Carlo repetitions for one row of campaign.csv."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hfe_sim.simulator import SimConfig, simulate  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--campaign", default=str(ROOT / "campaign.csv"))
p.add_argument("--index", type=int, required=True)
p.add_argument("--outdir", default=str(ROOT / "results" / "raw"))
p.add_argument("--runs", type=int, default=30)
p.add_argument("--seed-base", type=int, default=424242,
               help="Seed base used for common-random-number configurations.")
a = p.parse_args()

campaign = pd.read_csv(a.campaign)
row = campaign.iloc[a.index].to_dict()
base = {k: v for k, v in row.items() if k in SimConfig.__dataclass_fields__ and k != "seed"}
records = []

for run in range(a.runs):
    if row.get("seed_policy", "independent") == "common":
        seed = a.seed_base + run
    else:
        # Preserve the original main-campaign seed convention.
        seed = 100000 * a.index + run
    cfg = SimConfig(**base, seed=int(seed))
    result = simulate(cfg)
    result.update(row)
    result["seed"] = cfg.seed
    result["run"] = run
    records.append(result)

out = Path(a.outdir)
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(records).to_csv(out / f"config_{a.index:05d}.csv", index=False)
print(json.dumps({"index": a.index, "runs": a.runs, "rows": len(records), "seed_policy": row.get("seed_policy")}))
