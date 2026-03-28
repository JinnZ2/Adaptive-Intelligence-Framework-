"""Tests for the Universal Adaptive Intelligence module."""

import unittest

from aif.uai import Substrate, EnvironmentalChannel, SubstratePresets
from aif.uai.equations import (
    knowledge_update,
    survival_probability,
    memory_integrate,
    adaptive_capacity,
    structural_isomorphism_score,
)


class TestKnowledgeUpdate(unittest.TestCase):
    def test_basic_learning(self):
        """Knowledge should increase with positive input."""
        k = [0.1, 0.1]
        channels = [(0.8, 1.0, 0.0), (0.6, 0.8, 0.0)]
        result = knowledge_update(k, channels, alpha=0.1, beta=0.0)
        self.assertTrue(all(r >= k_i for r, k_i in zip(result, k)))

    def test_decay_reduces_knowledge(self):
        """With no input, decay should reduce knowledge."""
        k = [0.5, 0.5]
        channels = [(0.0, 0.0, 0.0)]
        result = knowledge_update(k, channels, alpha=0.0, beta=0.1)
        self.assertTrue(all(r <= k_i for r, k_i in zip(result, k)))

    def test_bounded_by_constraints(self):
        """Knowledge should stay within constraint bounds."""
        k = [0.99]
        channels = [(1.0, 5.0, 0.0)]
        result = knowledge_update(k, channels, alpha=0.5, beta=0.0, constraints=(0.0, 1.0))
        self.assertLessEqual(result[0], 1.0)

        k = [0.01]
        channels = [(0.0, 0.0, 0.0)]
        result = knowledge_update(k, channels, alpha=0.0, beta=0.5, constraints=(0.0, 1.0))
        self.assertGreaterEqual(result[0], 0.0)


class TestSurvivalProbability(unittest.TestCase):
    def test_high_knowledge_high_survival(self):
        """High knowledge across all domains = high survival."""
        p = survival_probability([0.9, 0.9, 0.9])
        self.assertGreater(p, 0.9)

    def test_low_knowledge_low_survival(self):
        """Low knowledge = low survival probability."""
        p = survival_probability([0.1, 0.1, 0.1])
        self.assertLess(p, 0.9)

    def test_returns_bounded(self):
        """Survival probability always in [0, 1]."""
        p = survival_probability([0.0, 0.0, 0.0], hazards=[1.0, 1.0, 1.0])
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)


class TestMemoryIntegrate(unittest.TestCase):
    def test_memory_converges(self):
        """Memory should move toward sensory input over time."""
        mem = [0.0, 0.0]
        sensory = [1.0, 1.0]
        for _ in range(100):
            mem = memory_integrate(mem, sensory, alpha=0.1)
        self.assertAlmostEqual(mem[0], 1.0, places=1)

    def test_context_gate_zero(self):
        """Zero context gate should prevent integration."""
        mem = [0.5, 0.5]
        sensory = [1.0, 1.0]
        result = memory_integrate(mem, sensory, alpha=0.5, context_gate=0.0)
        for m, r in zip(mem, result):
            self.assertAlmostEqual(r, m * 0.5, places=5)


class TestAdaptiveCapacity(unittest.TestCase):
    def test_high_knowledge_high_capacity(self):
        ac = adaptive_capacity([0.9, 0.9], learning_rate=0.1, decay_rate=0.01)
        self.assertGreater(ac, 0.5)

    def test_zero_learning_zero_capacity(self):
        ac = adaptive_capacity([0.9, 0.9], learning_rate=0.0, decay_rate=0.01)
        self.assertAlmostEqual(ac, 0.0)


class TestSubstrate(unittest.TestCase):
    def test_substrate_runs(self):
        """Substrate simulation should complete without error."""
        s = SubstratePresets.human_elder()
        results = s.run(steps=10, vary_environment=False)
        self.assertEqual(len(results), 10)
        self.assertIn("knowledge", results[-1])
        self.assertIn("survival_prob", results[-1])

    def test_all_presets_run(self):
        """All substrate presets should work."""
        for s in SubstratePresets.all_presets():
            results = s.run(steps=5, vary_environment=False)
            self.assertEqual(len(results), 5)
            summary = s.summary()
            self.assertIn("kind", summary)

    def test_structural_isomorphism(self):
        """All substrates should show structural isomorphism."""
        substrates = SubstratePresets.all_presets()
        for s in substrates:
            s.run(steps=20, vary_environment=False)
        score = structural_isomorphism_score([
            {"knowledge": s.knowledge, "alpha": s.alpha, "beta": s.beta}
            for s in substrates
        ])
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
