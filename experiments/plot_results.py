#!/usr/bin/env python3
"""Generate the paper figures and supplementary diagnostic plots."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "figures"
out.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "results" / "summary" / "summary.csv")

# RQ1 refined threshold curves.
for tau in [6, 12]:
    r = df[(df.experiment == "RQ1_threshold") & (df.N == 50) & (df.tau == tau)]
    if len(r):
        fig, ax = plt.subplots(figsize=(5.2, 3.3))
        for H, g in r.groupby("H"):
            g = g.sort_values("p_attack")
            ax.errorbar(g.p_attack, g.sat_fraction_mean, yerr=g.sat_fraction_ci95, marker="o", label=f"H={int(H)}")
        ax.set_xlabel(r"Attack success probability $p_A$")
        ax.set_ylabel("Fraction of saturated epochs")
        ax.set_ylim(-0.03, 1.03)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out / f"rq1_threshold_tau{tau}.pdf")
        plt.close(fig)

# Offered-load diagnostic.
r = df[(df.experiment == "RQ1_threshold") & (df.N == 50)].sort_values("offered_load_ratio")
if len(r):
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    for tau, g in r.groupby("tau"):
        ax.scatter(g.offered_load_ratio, g.sat_fraction_mean, label=fr"$\tau={int(tau)}$")
    ax.axvline(1.0, linestyle="--")
    ax.set_xlabel(r"Offered-load indicator $\rho_A=Bp_A\tau/H$")
    ax.set_ylabel("Fraction of saturated epochs")
    ax.set_ylim(-0.03, 1.03)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "rq1_offered_load.pdf")
    plt.close(fig)

# RQ2 attacker-strategy comparison (representative paper configuration).
r = df[(df.experiment == "RQ2_strategies") & (df.N == 50) & (df.H == 2) & (df.B == 1) & (df.tau == 12) & (df.profile == "critical-unit")]
if len(r):
    r = r.sort_values("mission_loss_mean")
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.bar(r.strategy, r.mission_loss_mean, yerr=r.mission_loss_ci95)
    ax.set_ylabel("Cumulative mission loss")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(out / "rq2_strategy_comparison.pdf")
    plt.close(fig)

# RQ3 mission-loss amplification.
r = df[(df.experiment == "RQ3_dependencies") & (df.N == 50) & (df.H == 2) & (df.B == 1)]
if len(r):
    r = r.sort_values("amplification_mean")
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.bar(r.profile, r.amplification_mean, yerr=r.amplification_ci95)
    ax.axhline(1, linestyle="--")
    ax.set_ylabel(r"Amplification factor $\mathcal{A}$")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(out / "rq3_amplification.pdf")
    plt.close(fig)

# RQ4 capacity/safe-mode sensitivity from the main campaign.
r = df[(df.experiment == "RQ4_architecture") & (df.N == 100) & (df.B == 2) & (df.tau == 8) & (df.p_attack == 0.9) & (df.profile == "coordination") & (df.priority == "criticality")]
if len(r):
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    for sm, g in r.groupby("safe_mode"):
        g = g.sort_values("H")
        ax.errorbar(g.H, g.mission_loss_mean, yerr=g.mission_loss_ci95, marker="o", label=f"safe mode={sm}")
    ax.set_xlabel("Human fallback capacity H")
    ax.set_ylabel("Cumulative mission loss")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "rq4_capacity_resilience.pdf")
    plt.close(fig)

# RQ4 paired prioritization gain.
paired_file = ROOT / "results" / "summary" / "rq4_priority_paired_runs.csv"
if paired_file.exists():
    paired = pd.read_csv(paired_file)
    metric = "mission_loss_delta_fifo_minus_criticality"
    if len(paired) and metric in paired:
        grp = paired.groupby(["N", "H", "tau", "p_attack"])[metric].agg(["mean", "std", "count"]).reset_index()
        grp["ci95"] = 1.96 * grp["std"].fillna(0) / (grp["count"] ** 0.5)
        for H in sorted(grp.H.unique()):
            x = grp[(grp.H == H) & (grp.N == 50)]
            fig, ax = plt.subplots(figsize=(5.2, 3.3))
            for tau, g in x.groupby("tau"):
                g = g.sort_values("p_attack")
                ax.errorbar(g.p_attack, g["mean"], yerr=g.ci95, marker="o", label=fr"$\tau={int(tau)}$")
            ax.axhline(0, linestyle="--")
            ax.set_xlabel(r"Attack success probability $p_A$")
            ax.set_ylabel("Mission-loss reduction\n(FIFO $-$ criticality priority)")
            ax.legend(fontsize=8)
            fig.tight_layout()
            fig.savefig(out / f"rq4_priority_gain_H{int(H)}.pdf")
            plt.close(fig)

print(f"Figures written to {out}")
