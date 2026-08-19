# Experiment definitions

This document records how the complete campaign maps to the paper's research questions.

## RQ1 — When does fallback exhaustion emerge?

`RQ1_core` provides a coarse factorial sweep over fleet size `N`, human capacity `H`, attack budget `B`, and request persistence `tau`. `RQ1_threshold` then resolves the transition more finely by sweeping attack success probability `p_attack` for `B=1`, multiple capacities, persistence values, and fleet sizes.

The threshold sweep also computes `offered_load_ratio = B * p_attack * tau / H`. It is a first-order explanatory indicator; genuine degradations, finite-source effects, stochastic overlap, and the simulator's service semantics prevent it from being a closed-form saturation threshold.

## RQ2 — Does attacker strategy matter?

`RQ2_strategies` compares four target-selection policies: random, criticality-first, fallback-first, and capacity-aware. The primary outcome is cumulative mission loss; saturation is also reported to distinguish maximizing supervisory overload from maximizing mission impact.

## RQ3 — Do fleet dependencies amplify the attack?

`RQ3_dependencies` evaluates independent, coordination, coverage, and critical-unit mission profiles. The simulator reports an amplification factor defined as total fleet mission loss divided by direct loss attributable to currently attacked vessels.

## RQ4 — Which architectural choices improve resilience?

`RQ4_architecture` varies fallback capacity, persistence, attack success, allocation policy, and a minimal autonomous safe mode. `RQ4_priority` focuses on the allocation question near the exhaustion boundary and uses common random numbers to pair FIFO and criticality-aware policies exactly.

## Default run length and repetitions

Each simulation lasts 120 discrete epochs. Unless changed on the command line, each parameter configuration is repeated 30 times.
