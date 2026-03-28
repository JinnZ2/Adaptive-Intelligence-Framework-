"""Universal Adaptive Intelligence — substrate-independent intelligence modeling."""

from aif.uai.substrate import Substrate, EnvironmentalChannel, SubstratePresets
from aif.uai.equations import knowledge_update, survival_probability, memory_integrate

__all__ = [
    "Substrate",
    "EnvironmentalChannel",
    "SubstratePresets",
    "knowledge_update",
    "survival_probability",
    "memory_integrate",
]
