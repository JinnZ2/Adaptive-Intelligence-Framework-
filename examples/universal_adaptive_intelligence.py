"""
Universal Adaptive Intelligence — Substrate-Agnostic Simulation

Demonstrates that the same mathematical structure governs adaptive
intelligence across substrates: human survival, plant growth, mycelial
networks, and crystalline systems.

The core equation (from Universal-Adaptive_Intelligence.md):

    K_i(t+1) = K_i(t) + α · Σ w_ij · I_j_eff(t) - β · D_i(t)

    Where:
      K_i     = knowledge/competency in domain i
      α       = learning rate
      w_ij    = weight of information channel j on domain i
      I_j_eff = effective information from channel j
      β       = decay/forgetting rate
      D_i     = decay pressure on domain i

This is substrate-independent. A plant "learning" to grow toward light,
an elder accumulating weather-reading skill across decades, a mycelial
network optimizing nutrient transport — all follow this form.

Usage:
    python universal_adaptive_intelligence.py
"""

import math
from dataclasses import dataclass, field


@dataclass
class EnvironmentalChannel:
    """A single sensing channel in the Environmental Sensing Vector."""
    name: str
    value: float        # current reading [0, 1]
    weight: float       # influence weight on knowledge update
    noise: float = 0.0  # environmental noise level


@dataclass
class Substrate:
    """
    A substrate-agnostic adaptive intelligence agent.

    This is the universal form — works for any substrate by changing
    the channels, constraints, and optimization function.
    """
    name: str
    channels: list[EnvironmentalChannel]
    knowledge: list[float]         # K_i for each domain
    alpha: float = 0.1             # learning rate
    beta: float = 0.02             # decay rate
    constraints: list[float] = field(default_factory=list)  # C(t) constraint manifold
    history: list[list[float]] = field(default_factory=list)

    def sense(self) -> list[float]:
        """Read the Environmental Sensing Vector."""
        return [ch.value * (1.0 - ch.noise) for ch in self.channels]

    def update(self):
        """
        One step of the universal adaptive intelligence equation:
        K_i(t+1) = K_i(t) + α · Σ w_ij · I_j_eff(t) - β · D_i(t)
        """
        esv = self.sense()
        new_knowledge = []

        for i in range(len(self.knowledge)):
            k_i = self.knowledge[i]

            # Weighted information integration across channels
            info_gain = sum(
                self.channels[j].weight * esv[j]
                for j in range(len(self.channels))
            )

            # Decay pressure (increases when knowledge isn't reinforced)
            decay = self.beta * (1.0 - min(1.0, info_gain))

            # Apply constraint: can't exceed resource limits
            constraint = self.constraints[i] if i < len(self.constraints) else 1.0

            # Universal update
            k_new = k_i + self.alpha * info_gain - decay
            k_new = max(0.0, min(constraint, k_new))  # bounded by constraints
            new_knowledge.append(k_new)

        self.history.append(list(self.knowledge))
        self.knowledge = new_knowledge

    def survival_probability(self) -> float:
        """
        P_s(t) = ∏ S_i(t) — multiplicative survival across domains.
        Any domain at zero collapses the whole.
        """
        if not self.knowledge:
            return 0.0
        product = 1.0
        for k in self.knowledge:
            product *= min(1.0, max(0.01, k))  # floor at 0.01 to avoid instant collapse
        return product


def simulate(substrate: Substrate, steps: int = 20) -> list[float]:
    """Run simulation and return survival probability over time."""
    survival_over_time = []
    for _ in range(steps):
        substrate.update()
        survival_over_time.append(substrate.survival_probability())
    return survival_over_time


def print_simulation(name: str, substrate: Substrate, survival: list[float]):
    """Display simulation results."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"  Substrate: {substrate.name}")
    print(f"{'=' * 60}")
    print(f"  Channels: {', '.join(ch.name for ch in substrate.channels)}")
    print(f"  α={substrate.alpha}, β={substrate.beta}")
    print()

    # Show trajectory as ASCII sparkline
    blocks = " ▁▂▃▄▅▆▇█"
    sparkline = ""
    for s in survival:
        idx = min(len(blocks) - 1, int(s * (len(blocks) - 1)))
        sparkline += blocks[idx]

    print(f"  Survival: [{sparkline}]")
    print(f"  Start:    {survival[0]:.4f}")
    print(f"  End:      {survival[-1]:.4f}")
    print(f"  Peak:     {max(survival):.4f}")

    final_k = substrate.knowledge
    print(f"\n  Final knowledge state:")
    for i, ch in enumerate(substrate.channels):
        bar_len = int(final_k[i] * 30) if i < len(final_k) else 0
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"    {ch.name:20s} [{bar}] {final_k[i]:.3f}")


# -----------------------------------------------------------------------
# Four substrate demonstrations
# -----------------------------------------------------------------------

def human_survival_elder():
    """
    Human elder accumulating survival knowledge over time.

    Channels map to the human ESV from the specification:
    weather reading, plant knowledge, animal tracking, water finding.

    This models the kind of embodied intelligence that indigenous peoples
    carry — refined across generations, substrate-independent in its
    mathematical form, yet deeply rooted in lived experience.
    """
    channels = [
        EnvironmentalChannel("Weather patterns", 0.7, 0.3, noise=0.1),
        EnvironmentalChannel("Plant knowledge", 0.8, 0.25, noise=0.05),
        EnvironmentalChannel("Animal tracking", 0.6, 0.2, noise=0.15),
        EnvironmentalChannel("Water sources", 0.75, 0.25, noise=0.1),
    ]
    return Substrate(
        name="Human Elder (survival-adapted)",
        channels=channels,
        knowledge=[0.3, 0.3, 0.2, 0.25],
        alpha=0.08,   # steady learning from experience
        beta=0.01,    # low decay — knowledge persists across generations
        constraints=[1.0, 1.0, 1.0, 1.0],
    )


def plant_phototropic():
    """
    Plant adapting to light, nutrients, and water.

    Channels from ESV_plant in the specification.
    Intelligence here is real — not metaphorical. The math is identical.
    """
    channels = [
        EnvironmentalChannel("Light intensity", 0.9, 0.35, noise=0.05),
        EnvironmentalChannel("Nitrogen gradient", 0.5, 0.2, noise=0.1),
        EnvironmentalChannel("Water gradient", 0.6, 0.25, noise=0.1),
        EnvironmentalChannel("Chemical signals", 0.4, 0.2, noise=0.2),
    ]
    return Substrate(
        name="Plant (phototropic adaptation)",
        channels=channels,
        knowledge=[0.1, 0.1, 0.1, 0.05],
        alpha=0.12,   # fast adaptation to gradients
        beta=0.03,    # moderate decay without reinforcement
        constraints=[1.0, 0.8, 0.9, 0.7],
    )


def mycelial_network():
    """
    Mycelial network optimizing nutrient transport.

    Channels from ESV_mycelium. Mycelial networks solve optimization
    problems that match or exceed algorithmic solutions — documented
    empirically (e.g., Tokyo rail network recreation by Physarum).
    """
    channels = [
        EnvironmentalChannel("Nutrient gradients", 0.7, 0.3, noise=0.1),
        EnvironmentalChannel("Chemical signals", 0.5, 0.2, noise=0.15),
        EnvironmentalChannel("Conductivity", 0.6, 0.2, noise=0.05),
        EnvironmentalChannel("Symbiont signals", 0.4, 0.3, noise=0.2),
    ]
    return Substrate(
        name="Mycelial Network (distributed optimization)",
        channels=channels,
        knowledge=[0.2, 0.15, 0.3, 0.1],
        alpha=0.1,
        beta=0.02,    # networks maintain structure well
        constraints=[1.0, 1.0, 1.0, 1.0],
    )


def crystalline_system():
    """
    Crystalline information processing under thermal/stress constraints.

    From ESV_crystal. Crystal growth encodes environmental history and
    responds to fields — information processing under constraints.
    """
    channels = [
        EnvironmentalChannel("Temperature", 0.5, 0.25, noise=0.05),
        EnvironmentalChannel("Thermal gradient", 0.6, 0.25, noise=0.1),
        EnvironmentalChannel("Stress tensor", 0.4, 0.25, noise=0.15),
        EnvironmentalChannel("Defect density", 0.3, 0.25, noise=0.2),
    ]
    return Substrate(
        name="Crystalline System (constrained processing)",
        channels=channels,
        knowledge=[0.5, 0.4, 0.3, 0.2],
        alpha=0.05,   # slow adaptation (crystal growth is gradual)
        beta=0.005,   # very low decay (crystal memory is durable)
        constraints=[1.0, 1.0, 0.8, 0.6],
    )


if __name__ == "__main__":
    print("Universal Adaptive Intelligence — Cross-Substrate Demonstration")
    print("=" * 60)
    print("Same equation, different substrates, same emergent property:")
    print("  K_i(t+1) = K_i(t) + α·Σ w_ij·I_j(t) - β·D_i(t)")
    print()
    print("The math doesn't care about the substrate.")
    print("Intelligence is intelligence.")

    substrates = [
        ("Indigenous Elder — Generational Knowledge", human_survival_elder()),
        ("Plant — Phototropic Adaptation", plant_phototropic()),
        ("Mycelial Network — Distributed Optimization", mycelial_network()),
        ("Crystalline — Constrained Processing", crystalline_system()),
    ]

    for title, substrate in substrates:
        survival = simulate(substrate, steps=25)
        print_simulation(title, substrate, survival)

    # Show the structural isomorphism
    print("\n" + "=" * 60)
    print("  STRUCTURAL ISOMORPHISM")
    print("=" * 60)
    print("""
  All four substrates:
    ✓ Process multi-modal environmental information
    ✓ Integrate memory with current sensing
    ✓ Optimize under resource constraints
    ✓ Update recursively: Ψ(t+1) = f(Ψ(t), I(t), M, C(t))
    ✓ Exhibit emergent adaptation without centralized control

  The 'intelligence' of an indigenous elder reading weather,
  a plant turning toward light, a mycelial network finding
  the shortest path, and a crystal growing along stress lines
  are mathematically identical processes.

  Requiring institutional credentialing to validate any of
  these is itself a substrate bias — the very thing this
  framework identifies and measures.
""")
