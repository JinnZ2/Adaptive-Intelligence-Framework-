"""Substrate simulation — universal adaptive intelligence across physical media."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from aif.uai.equations import (
    adaptive_capacity,
    knowledge_update,
    memory_integrate,
    survival_probability,
)


@dataclass
class EnvironmentalChannel:
    """A sensing input channel available to a substrate."""

    name: str
    value: float = 0.5
    weight: float = 1.0
    noise: float = 0.05

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.value, self.weight, self.noise)


@dataclass
class Substrate:
    """Universal adaptive intelligence agent — substrate-independent.

    Same equations govern a human elder, a plant, a crystal, or a mycelial network.
    Only the parameters differ.
    """

    name: str
    kind: str  # e.g., "human", "plant", "crystal", "mycelial", "ai"
    channels: list[EnvironmentalChannel]
    knowledge: list[float] = field(default_factory=list)
    memory: list[float] = field(default_factory=list)
    alpha: float = 0.1  # learning rate
    beta: float = 0.02  # decay rate
    gamma: float = 0.0  # memory anchor coupling
    constraints: tuple[float, float] = (0.0, 1.0)
    history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        n = len(self.channels)
        if not self.knowledge:
            self.knowledge = [0.1] * n
        if not self.memory:
            self.memory = [0.0] * n

    @property
    def n_domains(self) -> int:
        return len(self.channels)

    def update(
        self,
        hazards: list[float] | None = None,
        resources: list[float] | None = None,
        context_gate: float = 1.0,
    ) -> dict[str, Any]:
        """Run one timestep of universal adaptation.

        Returns a snapshot dict with knowledge, survival_prob, and adaptive_capacity.
        """
        channel_tuples = [ch.as_tuple() for ch in self.channels]
        memory_anchors = self.memory

        self.knowledge = knowledge_update(
            knowledge=self.knowledge,
            channels=channel_tuples,
            alpha=self.alpha,
            beta=self.beta,
            memory_anchors=memory_anchors,
            gamma=self.gamma,
            constraints=self.constraints,
        )

        sensory = [ch.value for ch in self.channels]
        self.memory = memory_integrate(
            memory=self.memory,
            sensory_input=sensory,
            alpha=self.alpha * 0.5,  # memory integrates slower
            context_gate=context_gate,
        )

        p_s = survival_probability(
            knowledge=self.knowledge,
            hazards=hazards,
            resources=resources,
        )

        a_c = adaptive_capacity(self.knowledge, self.alpha, self.beta)

        snapshot = {
            "knowledge": list(self.knowledge),
            "survival_prob": p_s,
            "adaptive_capacity": a_c,
            "memory": list(self.memory),
        }
        self.history.append(snapshot)
        return snapshot

    def run(
        self,
        steps: int = 50,
        hazards: list[float] | None = None,
        resources: list[float] | None = None,
        vary_environment: bool = True,
    ) -> list[dict[str, Any]]:
        """Run multiple timesteps, optionally varying channel values."""
        results = []
        for _ in range(steps):
            if vary_environment:
                for ch in self.channels:
                    ch.value = max(0.0, min(1.0, ch.value + random.gauss(0, 0.02)))
            results.append(self.update(hazards=hazards, resources=resources))
        return results

    def summary(self) -> dict[str, Any]:
        """Return current state summary."""
        return {
            "name": self.name,
            "kind": self.kind,
            "domains": [ch.name for ch in self.channels],
            "knowledge": {ch.name: round(k, 4) for ch, k in zip(self.channels, self.knowledge)},
            "survival_prob": round(
                survival_probability(self.knowledge), 4
            ),
            "adaptive_capacity": round(
                adaptive_capacity(self.knowledge, self.alpha, self.beta), 4
            ),
        }


class SubstratePresets:
    """Factory for common substrate configurations from the UAI specification."""

    @staticmethod
    def human_elder(name: str = "Human Elder") -> Substrate:
        return Substrate(
            name=name,
            kind="human",
            channels=[
                EnvironmentalChannel("weather_patterns", 0.7, 1.0, 0.05),
                EnvironmentalChannel("plant_knowledge", 0.6, 0.9, 0.04),
                EnvironmentalChannel("animal_tracking", 0.5, 0.8, 0.06),
                EnvironmentalChannel("water_sources", 0.8, 1.0, 0.03),
            ],
            alpha=0.08,
            beta=0.01,  # low decay — generational knowledge persists
            gamma=0.3,  # strong ancestral memory coupling
        )

    @staticmethod
    def plant(name: str = "Phototropic Plant") -> Substrate:
        return Substrate(
            name=name,
            kind="plant",
            channels=[
                EnvironmentalChannel("light_intensity", 0.6, 1.0, 0.08),
                EnvironmentalChannel("nitrogen_gradient", 0.4, 0.7, 0.05),
                EnvironmentalChannel("water_availability", 0.5, 0.9, 0.06),
                EnvironmentalChannel("chemical_signals", 0.3, 0.6, 0.04),
            ],
            alpha=0.12,
            beta=0.03,  # faster adaptation cycle
            gamma=0.1,  # epigenetic memory
        )

    @staticmethod
    def mycelial(name: str = "Mycelial Network") -> Substrate:
        return Substrate(
            name=name,
            kind="mycelial",
            channels=[
                EnvironmentalChannel("nutrient_gradient", 0.5, 0.9, 0.06),
                EnvironmentalChannel("chemical_signals", 0.4, 0.8, 0.05),
                EnvironmentalChannel("electrical_conductivity", 0.3, 0.7, 0.07),
                EnvironmentalChannel("symbiont_signals", 0.6, 0.8, 0.04),
            ],
            alpha=0.10,
            beta=0.02,
            gamma=0.2,  # network topology memory
        )

    @staticmethod
    def crystal(name: str = "Crystalline System") -> Substrate:
        return Substrate(
            name=name,
            kind="crystal",
            channels=[
                EnvironmentalChannel("temperature", 0.5, 0.8, 0.03),
                EnvironmentalChannel("thermal_gradient", 0.3, 0.7, 0.04),
                EnvironmentalChannel("stress_tensor", 0.4, 0.9, 0.02),
                EnvironmentalChannel("defect_density", 0.2, 0.6, 0.03),
            ],
            alpha=0.05,
            beta=0.005,  # very slow decay — durable structural memory
            gamma=0.05,  # minimal but present
        )

    @staticmethod
    def ai_system(name: str = "AI System") -> Substrate:
        return Substrate(
            name=name,
            kind="ai",
            channels=[
                EnvironmentalChannel("training_signal", 0.7, 1.0, 0.02),
                EnvironmentalChannel("feedback_loop", 0.5, 0.9, 0.03),
                EnvironmentalChannel("context_window", 0.6, 0.8, 0.01),
                EnvironmentalChannel("objective_gradient", 0.4, 0.7, 0.04),
            ],
            alpha=0.15,  # fast learning
            beta=0.04,  # moderate forgetting (context window limits)
            gamma=0.4,  # strong weight memory
        )

    @classmethod
    def all_presets(cls) -> list[Substrate]:
        """Return one of each preset for cross-substrate comparison."""
        return [
            cls.human_elder(),
            cls.plant(),
            cls.mycelial(),
            cls.crystal(),
            cls.ai_system(),
        ]
