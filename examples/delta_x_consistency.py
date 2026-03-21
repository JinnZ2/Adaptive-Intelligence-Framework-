"""
ΔX Consistency Test — Python Implementation

Detects when authority claims are narrative (social framing) vs. operational
(competency-based) by measuring how much work is actually done by the claimed
node versus absorbed by auxiliary nodes.

Based on: DeltaX.md formal specification

Usage:
    python delta_x_consistency.py
"""

import math
from dataclasses import dataclass, field


def sigmoid(x: float) -> float:
    """Logistic sigmoid, squashes to (0, 1)."""
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class DeltaXResult:
    """Result of a ΔX consistency test on a single decision."""
    decision_name: str
    raw_delta_x: float
    ceo_residual: float
    rho_hidden: float


@dataclass
class ConsistencyTestResult:
    """Aggregate result across all decisions for a claim."""
    claim: str
    per_decision: list[DeltaXResult]
    delta_x_claim: float
    rho_avg: float
    nds: float

    def interpretation(self) -> str:
        if self.nds > 0.8:
            return "NARRATIVE — claim is largely social framing, not operational competency"
        elif self.nds > 0.5:
            return "MIXED — partial operational basis, significant narrative component"
        elif self.nds > 0.2:
            return "MOSTLY OPERATIONAL — claim has substantial dynamics support"
        else:
            return "DYNAMICS-SUPPORTED — claimed node carries the ΔX"


def dx_consistency_test(
    claim: str,
    decisions: list[str],
    demand_vectors: dict[str, list[float]],
    mu_matrix: list[list[float]],
    weights: dict[str, float] | None = None,
    tau_rho: float = 0.6,
    lambda1: float = 5.0,
    lambda2: float = 5.0,
) -> ConsistencyTestResult:
    """
    Run the ΔX Consistency Test.

    Args:
        claim: The authority claim being tested (e.g., "CEO personally drives mergers").
        decisions: List of decision names where the claim is asserted relevant.
        demand_vectors: {decision_name: [d_1, ..., d_n]} raw demand per category.
        mu_matrix: Auxiliary node absorption efficiencies, shape [categories x nodes].
                   mu_matrix[i][k] = how efficiently node k absorbs category i work.
        weights: Optional per-decision importance weights. Defaults to equal.
        tau_rho: Hidden-labor threshold for NDS calculation (default 0.6).
        lambda1: NDS weighting for residual ratio (default 5.0).
        lambda2: NDS weighting for rho deviation (default 5.0).

    Returns:
        ConsistencyTestResult with per-decision breakdowns, aggregate ΔX, ρ_avg, and NDS.
    """
    num_categories = len(mu_matrix)
    num_nodes = len(mu_matrix[0]) if mu_matrix else 0

    if weights is None:
        weights = {d: 1.0 / len(decisions) for d in decisions}

    results = []
    sum_raws = 0.0

    for decision in decisions:
        d_vec = demand_vectors[decision]
        assert len(d_vec) == num_categories, (
            f"Demand vector for '{decision}' has {len(d_vec)} categories, "
            f"expected {num_categories}"
        )

        # Step 1: raw ΔX
        raw = sum(d_vec)

        # Step 2: compute absorbed shares per category per node
        # Each auxiliary node absorbs d_i * mu_ik of category i's demand.
        # The claimed node (CEO/elder) retains whatever the auxiliaries
        # cannot absorb. Total auxiliary absorption per category is capped
        # at d_i (they can't absorb more than the demand).
        total_absorbed = 0.0
        for i in range(num_categories):
            aux_absorption = sum(d_vec[i] * mu_matrix[i][k] for k in range(num_nodes))
            # Cap: auxiliaries can't absorb more than the total demand
            absorbed_i = min(d_vec[i], aux_absorption)
            total_absorbed += absorbed_i

        # Step 3: CEO residual — what the claimed node actually carries
        residual = raw - total_absorbed

        # Step 4: hidden labor fraction
        rho = (raw - residual) / raw if raw > 0 else 0.0

        results.append(DeltaXResult(
            decision_name=decision,
            raw_delta_x=raw,
            ceo_residual=residual,
            rho_hidden=rho,
        ))
        sum_raws += raw

    # Step 5: weighted claim-level ΔX
    delta_x_claim = sum(
        weights[r.decision_name] * r.ceo_residual for r in results
    )

    # Step 6: NDS
    rho_avg = sum(r.rho_hidden for r in results) / len(results) if results else 0.0
    ratio = 1.0 - (delta_x_claim / sum_raws) if sum_raws > 0 else 0.5
    nds = sigmoid(lambda1 * ratio + lambda2 * (rho_avg - tau_rho))

    return ConsistencyTestResult(
        claim=claim,
        per_decision=results,
        delta_x_claim=delta_x_claim,
        rho_avg=rho_avg,
        nds=nds,
    )


# ---------------------------------------------------------------------------
# Worked example: Merger negotiation (from DeltaX.md)
# ---------------------------------------------------------------------------

def example_merger_negotiation():
    """
    Reproduce the merger negotiation example from the specification.

    Scenario: A CEO claims personal mastery of a trait is essential for
    merger negotiations. We test whether the CEO actually carries the work
    or if auxiliary nodes (legal, finance, strategy teams) absorb it.

    Categories (6): Legal analysis, Financial modeling, Stakeholder mgmt,
                     Strategic framing, Due diligence, Communication
    Auxiliary nodes (3): Legal team, Finance team, Strategy team
    """
    categories = [
        "Legal analysis", "Financial modeling", "Stakeholder mgmt",
        "Strategic framing", "Due diligence", "Communication"
    ]
    nodes = ["Legal team", "Finance team", "Strategy team"]

    # Demand vector for the merger negotiation decision
    # Each value = how much work that category requires (0-1 scale)
    demand = {
        "Merger negotiation": [0.8, 0.7, 0.5, 0.6, 0.7, 0.5]
        # total raw = 3.8
    }

    # Absorption efficiencies: mu[category][node]
    # How much of each category's work each auxiliary node can absorb
    mu = [
        # Legal   Finance  Strategy
        [0.9,    0.05,    0.05],   # Legal analysis → mostly legal team
        [0.05,   0.9,     0.05],   # Financial modeling → mostly finance
        [0.1,    0.1,     0.3],    # Stakeholder mgmt → partially strategy
        [0.1,    0.1,     0.7],    # Strategic framing → mostly strategy
        [0.3,    0.4,     0.2],    # Due diligence → spread across teams
        [0.1,    0.05,    0.2],    # Communication → partially strategy
    ]

    result = dx_consistency_test(
        claim="CEO must personally possess trait X for effective mergers",
        decisions=["Merger negotiation"],
        demand_vectors=demand,
        mu_matrix=mu,
    )

    print("=" * 70)
    print(f"ΔX CONSISTENCY TEST")
    print(f"Claim: \"{result.claim}\"")
    print("=" * 70)

    for r in result.per_decision:
        print(f"\n  Decision: {r.decision_name}")
        print(f"    Raw ΔX:        {r.raw_delta_x:.2f}")
        print(f"    CEO residual:  {r.ceo_residual:.4f}")
        print(f"    ρ_hidden:      {r.rho_hidden:.3f} ({r.rho_hidden*100:.1f}% absorbed by auxiliary nodes)")

    print(f"\n  Aggregate ΔX_claim:  {result.delta_x_claim:.4f}")
    print(f"  ρ_avg:               {result.rho_avg:.3f}")
    print(f"  NDS:                 {result.nds:.4f}")
    print(f"\n  → {result.interpretation()}")
    print()


def example_indigenous_knowledge():
    """
    Contrast example: Indigenous elder teaching survival skills.

    Here the claimed node (the elder) directly carries the knowledge and
    transmits it. Auxiliary nodes exist (community, environment) but the
    elder's personal embodied knowledge IS the operational capability.

    This demonstrates that the ΔX test correctly identifies operational
    competency when it exists — it's not biased toward always flagging claims.
    The test respects substrate-independent intelligence: embodied knowledge
    that has been refined across generations is real, measurable competency.
    """
    # Categories of survival teaching
    categories = [
        "Weather reading", "Plant identification", "Animal tracking",
        "Water finding", "Tool making", "Story/pattern transmission"
    ]

    demand = {
        "Survival teaching": [0.8, 0.9, 0.7, 0.8, 0.6, 0.9]
    }

    # Absorption efficiencies for auxiliary "nodes"
    # (community members, written references, environment itself)
    # Key insight: for embodied knowledge, auxiliary absorption is LOW
    # because the knowledge lives in the practitioner
    mu = [
        # Community  References  Environment
        [0.05,      0.0,        0.1],    # Weather reading — embodied, not in books
        [0.1,       0.05,       0.0],    # Plant ID — learned through direct teaching
        [0.05,      0.0,        0.05],   # Animal tracking — embodied skill
        [0.1,       0.0,        0.1],    # Water finding — deep local knowledge
        [0.15,      0.05,       0.0],    # Tool making — some community knowledge
        [0.1,       0.05,       0.0],    # Story transmission — community assists
    ]

    result = dx_consistency_test(
        claim="Elder's embodied knowledge is essential for community survival",
        decisions=["Survival teaching"],
        demand_vectors=demand,
        mu_matrix=mu,
    )

    print("=" * 70)
    print(f"ΔX CONSISTENCY TEST")
    print(f"Claim: \"{result.claim}\"")
    print("=" * 70)

    for r in result.per_decision:
        print(f"\n  Decision: {r.decision_name}")
        print(f"    Raw ΔX:        {r.raw_delta_x:.2f}")
        print(f"    CEO residual:  {r.ceo_residual:.4f}")
        print(f"    ρ_hidden:      {r.rho_hidden:.3f} ({r.rho_hidden*100:.1f}% absorbed by auxiliary nodes)")

    print(f"\n  Aggregate ΔX_claim:  {result.delta_x_claim:.4f}")
    print(f"  ρ_avg:               {result.rho_avg:.3f}")
    print(f"  NDS:                 {result.nds:.4f}")
    print(f"\n  → {result.interpretation()}")
    print()


if __name__ == "__main__":
    example_merger_negotiation()
    print("\n" + "—" * 70 + "\n")
    example_indigenous_knowledge()
