"""Core UAI equations — universal across all substrates.

K_i(t+1) = K_i(t) + alpha * sum(w_ij * I_j_eff(t)) - beta * D_i(t)
P_s(t)   = prod_i [1 - phi_i * (1 - K_i(t)) * H_i(t) / R_i(t)]
M(t+1)   = (1 - alpha) * M(t) + alpha * ESV(t) * g(context)
"""

from __future__ import annotations

import math
import random
from typing import Sequence


def knowledge_update(
    knowledge: list[float],
    channels: Sequence[tuple[float, float, float]],
    alpha: float,
    beta: float,
    decay_pressures: list[float] | None = None,
    memory_anchors: list[float] | None = None,
    gamma: float = 0.0,
    constraints: tuple[float, float] = (0.0, 1.0),
) -> list[float]:
    """Apply universal knowledge update equation.

    K_i(t+1) = K_i(t) + alpha * sum_j(w_ij * I_j_eff) - beta * D_i(t)

    Args:
        knowledge: Current knowledge vector K(t).
        channels: Sequence of (value, weight, noise) tuples per channel.
        alpha: Learning rate.
        beta: Decay/forgetting rate.
        decay_pressures: Per-domain decay pressures D_i(t). Defaults to uniform.
        memory_anchors: Per-channel ancestral memory anchors A_j.
        gamma: Memory anchor coupling strength.
        constraints: (min, max) bounds on knowledge values.

    Returns:
        Updated knowledge vector K(t+1).
    """
    n_domains = len(knowledge)
    if decay_pressures is None:
        decay_pressures = [1.0] * n_domains
    if memory_anchors is None:
        memory_anchors = [0.0] * len(channels)

    updated = []
    for i in range(n_domains):
        # Effective information with noise and memory anchoring
        info_sum = 0.0
        for j, (value, weight, noise) in enumerate(channels):
            noise_sample = random.gauss(0, noise) if noise > 0 else 0.0
            i_eff = value + noise_sample + gamma * memory_anchors[j]
            info_sum += weight * i_eff

        k_new = knowledge[i] + alpha * info_sum - beta * decay_pressures[i]
        k_new = max(constraints[0], min(constraints[1], k_new))
        updated.append(k_new)

    return updated


def survival_probability(
    knowledge: list[float],
    hazards: list[float] | None = None,
    resources: list[float] | None = None,
    phi: list[float] | None = None,
) -> float:
    """Compute recursive survival probability.

    P_s(t) = prod_i [1 - phi_i * (1 - K_i(t)) * H_i(t) / R_i(t)]

    Args:
        knowledge: Knowledge vector K(t).
        hazards: Per-domain hazard levels H_i(t). Defaults to 0.5.
        resources: Per-domain resource levels R_i(t). Defaults to 1.0.
        phi: Per-domain vulnerability weights. Defaults to 0.3.

    Returns:
        Survival probability in [0, 1].
    """
    n = len(knowledge)
    if hazards is None:
        hazards = [0.5] * n
    if resources is None:
        resources = [1.0] * n
    if phi is None:
        phi = [0.3] * n

    p_s = 1.0
    for i in range(n):
        r_i = max(resources[i], 0.01)  # prevent division by zero
        factor = 1.0 - phi[i] * (1.0 - knowledge[i]) * hazards[i] / r_i
        factor = max(0.01, min(1.0, factor))
        p_s *= factor

    return p_s


def memory_integrate(
    memory: list[float],
    sensory_input: list[float],
    alpha: float,
    context_gate: float = 1.0,
) -> list[float]:
    """Universal memory integration.

    M(t+1) = (1 - alpha) * M(t) + alpha * ESV(t) * g(context)

    Args:
        memory: Current memory state M(t).
        sensory_input: Environmental sensing vector ESV(t).
        alpha: Integration rate.
        context_gate: Context gating function g(context) in [0, 1].

    Returns:
        Updated memory state M(t+1).
    """
    return [
        (1 - alpha) * m + alpha * s * context_gate
        for m, s in zip(memory, sensory_input)
    ]


def adaptive_capacity(
    knowledge: list[float],
    learning_rate: float,
    decay_rate: float,
) -> float:
    """Compute aggregate adaptive capacity A(t).

    A(t) = mean(K) * (alpha / (alpha + beta))

    Higher when knowledge is high and learning outpaces decay.
    """
    if not knowledge:
        return 0.0
    mean_k = sum(knowledge) / len(knowledge)
    rate_ratio = learning_rate / (learning_rate + decay_rate) if (learning_rate + decay_rate) > 0 else 0.0
    return mean_k * rate_ratio


def structural_isomorphism_score(substrates: list[dict]) -> float:
    """Measure how structurally isomorphic a set of substrates are.

    Compares the survival probability trajectories across substrates.
    Returns a score in [0, 1] where 1 = identical dynamics.

    Args:
        substrates: List of dicts with keys 'knowledge', 'alpha', 'beta'.

    Returns:
        Isomorphism score.
    """
    if len(substrates) < 2:
        return 1.0

    # Compute adaptive capacity for each
    capacities = [
        adaptive_capacity(s["knowledge"], s["alpha"], s["beta"])
        for s in substrates
    ]

    # Variance of capacities — lower = more isomorphic
    mean_c = sum(capacities) / len(capacities)
    variance = sum((c - mean_c) ** 2 for c in capacities) / len(capacities)

    # Convert to similarity score
    return math.exp(-10 * variance)
