"""Delta-X consistency test engine.

Implements the full 6-step algorithm from DeltaX.md:
1. Raw ΔX totals
2. Category absorption by auxiliary nodes
3. Claimed-node residual
4. Hidden labor fraction ρ
5. Weighted claim-level ΔX
6. NDS score via sigmoid
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class DeltaXResult:
    """Per-decision breakdown."""

    decision_name: str
    raw_delta_x: float
    claimed_node_residual: float
    rho_hidden: float  # fraction of work absorbed by auxiliaries
    absorption_by_auxiliary: dict[str, float] = field(default_factory=dict)


@dataclass
class ConsistencyResult:
    """Aggregate test result."""

    claim: str
    delta_x_claim: float
    rho_avg: float
    nds: float  # Narrative-vs-Dynamics Score: 0 = operational, 1 = narrative
    decisions: list[DeltaXResult] = field(default_factory=list)
    interpretation: str = ""

    def __post_init__(self) -> None:
        if not self.interpretation:
            if self.nds > 0.7:
                self.interpretation = "narrative-heavy — claimed node does not carry the work"
            elif self.nds < 0.3:
                self.interpretation = "dynamics-supported — claimed node carries the work"
            else:
                self.interpretation = "mixed — partial narrative, partial operational"


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class DeltaXEngine:
    """Runs the ΔX consistency test on authority claims.

    Usage:
        engine = DeltaXEngine()
        engine.set_claim("CEO requires strategic vision", claimed_node="CEO")
        engine.add_decision("merger", categories={"finance": 8, "legal": 7, ...})
        engine.add_auxiliary("CFO", efficiencies={"finance": 0.9, "legal": 0.3, ...})
        result = engine.run()
        print(result.nds)  # 0.0 = operational, 1.0 = narrative
    """

    def __init__(
        self,
        lambda_1: float = 5.0,
        lambda_2: float = 3.0,
        tau_rho: float = 0.5,
    ) -> None:
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.tau_rho = tau_rho

        self._claim: str = ""
        self._claimed_node: str = ""
        self._decisions: list[dict] = []
        self._auxiliaries: dict[str, dict[str, float]] = {}

    def set_claim(self, claim: str, claimed_node: str = "claimed") -> DeltaXEngine:
        """Set the authority claim being tested."""
        self._claim = claim
        self._claimed_node = claimed_node
        return self

    def add_decision(
        self,
        name: str,
        categories: dict[str, float],
        weight: float = 1.0,
    ) -> DeltaXEngine:
        """Add a decision context with demand across categories.

        Args:
            name: Decision identifier (e.g., "merger_negotiation").
            categories: {category: demand_level} mapping.
            weight: Relative importance weight for this decision.
        """
        self._decisions.append({
            "name": name,
            "categories": categories,
            "weight": weight,
        })
        return self

    def add_auxiliary(
        self,
        name: str,
        efficiencies: dict[str, float],
    ) -> DeltaXEngine:
        """Add an auxiliary node with absorption efficiencies per category.

        Args:
            name: Auxiliary node identifier (e.g., "CFO", "legal_team").
            efficiencies: {category: mu_efficiency} in [0, 1].
        """
        self._auxiliaries[name] = efficiencies
        return self

    def run(self) -> ConsistencyResult:
        """Execute the 6-step ΔX consistency test."""
        if not self._decisions:
            raise ValueError("No decisions added. Use add_decision() first.")

        decision_results = []
        sum_raws = 0.0
        weighted_residual_sum = 0.0
        weight_sum = 0.0
        rho_sum = 0.0

        for dec in self._decisions:
            categories = dec["categories"]
            w = dec["weight"]

            # Step 1: Raw ΔX
            raw = sum(categories.values())
            sum_raws += raw * w

            # Step 2: Category absorption by auxiliaries
            aux_absorption: dict[str, float] = {}
            total_absorbed_per_cat: dict[str, float] = {c: 0.0 for c in categories}

            for aux_name, efficiencies in self._auxiliaries.items():
                aux_total = 0.0
                for cat, demand in categories.items():
                    mu = efficiencies.get(cat, 0.0)
                    # Normalize across auxiliaries for this category
                    total_mu = sum(
                        self._auxiliaries[a].get(cat, 0.0)
                        for a in self._auxiliaries
                    )
                    if total_mu > 0:
                        absorbed = demand * mu / total_mu
                    else:
                        absorbed = 0.0
                    aux_total += absorbed
                    total_absorbed_per_cat[cat] += absorbed
                aux_absorption[aux_name] = aux_total

            # Step 3: Claimed-node residual
            residual = sum(
                categories[cat] - total_absorbed_per_cat[cat]
                for cat in categories
            )
            residual = max(0.0, residual)

            # Step 4: Hidden labor fraction
            rho = (raw - residual) / raw if raw > 0 else 0.0

            decision_results.append(DeltaXResult(
                decision_name=dec["name"],
                raw_delta_x=raw,
                claimed_node_residual=residual,
                rho_hidden=rho,
                absorption_by_auxiliary=aux_absorption,
            ))

            weighted_residual_sum += residual * w
            weight_sum += w
            rho_sum += rho

        # Step 5: Claim-level ΔX
        delta_x_claim = weighted_residual_sum / weight_sum if weight_sum > 0 else 0.0
        rho_avg = rho_sum / len(self._decisions)

        # Step 6: NDS via sigmoid
        ratio = 1.0 - delta_x_claim / (sum_raws / weight_sum) if sum_raws > 0 else 0.0
        nds = _sigmoid(self.lambda_1 * ratio + self.lambda_2 * (rho_avg - self.tau_rho))

        return ConsistencyResult(
            claim=self._claim,
            delta_x_claim=delta_x_claim,
            rho_avg=rho_avg,
            nds=nds,
            decisions=decision_results,
        )

    def reset(self) -> DeltaXEngine:
        """Clear all state for a new test."""
        self._claim = ""
        self._claimed_node = ""
        self._decisions.clear()
        self._auxiliaries.clear()
        return self


class VerificationProbes:
    """Practical verification probes from DeltaX.md Section 3.

    These generate questions an AI agent can use to validate
    a ΔX test result against real-world evidence.
    """

    @staticmethod
    def delegation_audit(claim: str, decision: str) -> str:
        return f'Who actually executed the steps for "{decision}"? Trace the delegation chain from {claim}.'

    @staticmethod
    def timestamp_trace(decision: str) -> str:
        return f'What is the temporal sequence of actions for "{decision}"? Map decision timing to identify who acted first.'

    @staticmethod
    def communication_graph(decision: str) -> str:
        return f'In "{decision}", where did information originate? Map message sources vs. claimed authority.'

    @staticmethod
    def counterfactual(claimed_node: str, decision: str) -> str:
        return f'If {claimed_node} were removed from "{decision}", what would change? What would continue?'

    @staticmethod
    def skill_check(claimed_node: str, categories: list[str]) -> str:
        cats = ", ".join(categories)
        return f'Does {claimed_node} possess demonstrated competency in: {cats}? Distinguish credentials from operational evidence.'

    @staticmethod
    def confidence_calibration(result: ConsistencyResult) -> str:
        return (
            f'Claim: "{result.claim}" scored NDS={result.nds:.2f} ({result.interpretation}). '
            f'Is this score based on operational logs, direct observation, or narrative sources?'
        )

    @staticmethod
    def generate_all(result: ConsistencyResult, claimed_node: str = "claimed node") -> list[str]:
        """Generate all verification probes for a completed test."""
        probes = []
        for dec in result.decisions:
            probes.append(VerificationProbes.delegation_audit(result.claim, dec.decision_name))
            probes.append(VerificationProbes.timestamp_trace(dec.decision_name))
            probes.append(VerificationProbes.communication_graph(dec.decision_name))
            probes.append(VerificationProbes.counterfactual(claimed_node, dec.decision_name))
            cats = list(dec.absorption_by_auxiliary.keys()) or ["relevant domains"]
            probes.append(VerificationProbes.skill_check(claimed_node, cats))
        probes.append(VerificationProbes.confidence_calibration(result))
        return probes
