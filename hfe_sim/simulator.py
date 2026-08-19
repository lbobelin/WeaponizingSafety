from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class SimConfig:
    N:int=20; H:int=3; B:int=1; T:int=120
    tau:int=6; p_genuine:float=0.002; p_attack:float=0.9
    strategy:str='capacity_aware'; profile:str='none'
    priority:str='fifo'; safe_mode:bool=False
    seed:int=0


def _criticalities(N, profile, rng):
    c=np.ones(N)
    if profile=='critical-unit':
        k=max(1,N//10); idx=rng.choice(N,k,replace=False); c[idx]=4.0
    else:
        c=rng.uniform(0.8,1.2,N)
    return c


def _durations(N, tau, rng):
    # heterogeneity makes fallback-first distinct while preserving requested mean scale
    lo=max(1,int(round(0.6*tau))); hi=max(lo+1,int(round(1.4*tau))+1)
    return rng.integers(lo,hi,size=N)


def _mission_loss(active, served, criticality, profile, safe_mode):
    # served fallback retains partial mission capability; unserved fallback loses more.
    unserved=active & (~served)
    served_loss=0.20*criticality[served].sum()
    unserved_factor=0.55 if safe_mode else 1.0
    direct=served_loss + unserved_factor*criticality[unserved].sum()
    unavailable = float(unserved.sum()) + 0.2*float(served.sum())
    N=len(active)
    interaction=0.0
    if profile=='coordination':
        frac=unavailable/max(N,1)
        interaction=0.8*N*(frac**1.5)
    elif profile=='coverage':
        frac=unavailable/max(N,1)
        interaction=1.2*N*(frac**2)
    elif profile=='critical-unit':
        interaction=0.35*criticality[unserved & (criticality>=3.0)].sum()
    return direct+interaction, direct, interaction


def _choose_targets(cfg, active, criticality, durations, remaining, rng):
    candidates=np.where(~active)[0]
    if cfg.B<=0 or len(candidates)==0 or cfg.strategy=='none': return np.array([],dtype=int)
    k=min(cfg.B,len(candidates))
    if cfg.strategy=='random': return rng.choice(candidates,k,replace=False)
    if cfg.strategy=='criticality_first':
        score=criticality[candidates]
    elif cfg.strategy=='fallback_first':
        score=durations[candidates].astype(float)
    elif cfg.strategy=='capacity_aware':
        # Favor persistent requests when capacity is not yet saturated; once near/over
        # capacity, favor mission-critical vessels. This is intentionally one-step/heuristic.
        occupied=int(active.sum())
        pressure=max(0.0,(occupied-cfg.H+1)/max(cfg.H,1))
        score=(1.0+pressure)*criticality[candidates] + (durations[candidates]/max(cfg.tau,1))
        if cfg.profile in ('coordination','coverage'):
            score += 0.25*criticality[candidates]
    else:
        raise ValueError(f'Unknown strategy {cfg.strategy}')
    order=np.argsort(score)[::-1]
    return candidates[order[:k]]


def simulate(cfg:SimConfig):
    rng=np.random.default_rng(cfg.seed)
    crit=_criticalities(cfg.N,cfg.profile,rng)
    durations=_durations(cfg.N,cfg.tau,rng)
    remaining=np.zeros(cfg.N,dtype=int)
    attacked_current=np.zeros(cfg.N,dtype=bool)
    total_loss=total_direct=total_interaction=0.0
    excess_sum=denied_epochs=0
    sat_epochs=0; first_sat=-1; attack_successes=attack_attempts=0
    direct_attacked_loss=0.0; indirect_loss=0.0

    for t in range(cfg.T):
        # decrement old requests at start of epoch
        remaining=np.maximum(remaining-1,0)
        attacked_current &= remaining>0
        active=remaining>0

        # genuine degradations among currently nominal vessels
        cand=np.where(~active)[0]
        if len(cand):
            gen=cand[rng.random(len(cand)) < cfg.p_genuine]
            remaining[gen]=durations[gen]
        active=remaining>0

        # adversarial induced fallback
        targets=_choose_targets(cfg,active,crit,durations,remaining,rng)
        attack_attempts += len(targets)
        if len(targets):
            succ=targets[rng.random(len(targets)) < cfg.p_attack]
            remaining[succ]=durations[succ]
            attacked_current[succ]=True
            attack_successes += len(succ)
        active=remaining>0
        R=int(active.sum())

        # allocate human fallback capacity
        served=np.zeros(cfg.N,dtype=bool)
        active_idx=np.where(active)[0]
        if len(active_idx)<=cfg.H:
            served[active_idx]=True
        elif cfg.H>0:
            if cfg.priority=='criticality':
                order=active_idx[np.argsort(crit[active_idx])[::-1]]
            else: # deterministic FIFO proxy: longest elapsed/remaining persistence first
                order=active_idx[np.argsort(remaining[active_idx])[::-1]]
            served[order[:cfg.H]]=True

        excess=max(0,R-cfg.H)
        excess_sum += excess
        if excess>0:
            sat_epochs += 1
            denied_epochs += excess
            if first_sat<0: first_sat=t

        loss,direct,interaction=_mission_loss(active,served,crit,cfg.profile,cfg.safe_mode)
        total_loss += loss; total_direct += direct; total_interaction += interaction
        # decomposition used only as descriptive metric
        attacked_loss=0.20*crit[served & attacked_current].sum() + (0.55 if cfg.safe_mode else 1.0)*crit[(~served)&active&attacked_current].sum()
        direct_attacked_loss += attacked_loss
        indirect_loss += max(0.0,loss-attacked_loss)

    return {
        'mission_loss':total_loss,
        'direct_loss':total_direct,
        'interaction_loss':total_interaction,
        'sat_fraction':sat_epochs/cfg.T,
        'excess_demand':excess_sum,
        'denied_request_epochs':denied_epochs,
        'time_to_first_saturation': first_sat if first_sat>=0 else np.nan,
        'attack_attempts':attack_attempts,
        'attack_successes':attack_successes,
        'attack_efficiency': total_loss/max(attack_successes,1),
        'direct_attacked_loss':direct_attacked_loss,
        'indirect_loss':indirect_loss,
        'amplification': total_loss/max(direct_attacked_loss,1e-9) if attack_successes else np.nan,
    }
