"""Tests for the Delta-X Consistency Test module."""

import unittest

from aif.delta_x import DeltaXEngine, ConsistencyResult
from aif.delta_x.engine import VerificationProbes


class TestDeltaXEngine(unittest.TestCase):
    def _build_ceo_test(self) -> DeltaXEngine:
        """Standard CEO merger test case from the spec."""
        engine = DeltaXEngine()
        engine.set_claim("CEO requires strategic vision", claimed_node="CEO")
        engine.add_decision("merger", {
            "financial": 8, "legal": 7, "comms": 6, "integration": 9,
        })
        engine.add_auxiliary("CFO", {"financial": 0.9, "legal": 0.2})
        engine.add_auxiliary("Legal", {"legal": 0.95})
        engine.add_auxiliary("Ops", {"integration": 0.85, "comms": 0.3})
        engine.add_auxiliary("Comms", {"comms": 0.9})
        return engine

    def test_ceo_scores_narrative(self):
        """CEO merger claim should score as narrative (NDS > 0.7)."""
        result = self._build_ceo_test().run()
        self.assertGreater(result.nds, 0.7)
        self.assertIn("narrative", result.interpretation)

    def test_high_rho_hidden(self):
        """Most work should be absorbed by auxiliaries."""
        result = self._build_ceo_test().run()
        self.assertGreater(result.rho_avg, 0.5)

    def test_no_auxiliaries_scores_operational(self):
        """With no auxiliaries, claimed node carries all work — NDS should be low."""
        engine = DeltaXEngine()
        engine.set_claim("Elder knows water sources", claimed_node="Elder")
        engine.add_decision("water_finding", {"terrain": 5, "weather": 4, "memory": 6})
        result = engine.run()
        self.assertLess(result.nds, 0.5)
        self.assertAlmostEqual(result.rho_avg, 0.0)

    def test_no_decisions_raises(self):
        """Should raise if no decisions provided."""
        engine = DeltaXEngine()
        engine.set_claim("test")
        with self.assertRaises(ValueError):
            engine.run()

    def test_reset(self):
        """Reset should clear all state."""
        engine = self._build_ceo_test()
        engine.reset()
        with self.assertRaises(ValueError):
            engine.run()

    def test_multiple_decisions(self):
        """Engine should handle multiple decision contexts."""
        engine = DeltaXEngine()
        engine.set_claim("Manager leads team", claimed_node="Manager")
        engine.add_decision("planning", {"strategy": 7, "execution": 8})
        engine.add_decision("review", {"analysis": 6, "reporting": 5})
        engine.add_auxiliary("Analyst", {"analysis": 0.8, "reporting": 0.7})
        engine.add_auxiliary("Engineer", {"execution": 0.9, "strategy": 0.2})
        result = engine.run()
        self.assertEqual(len(result.decisions), 2)
        self.assertGreater(result.nds, 0.0)


class TestConsistencyResult(unittest.TestCase):
    def test_interpretation_narrative(self):
        r = ConsistencyResult(claim="test", delta_x_claim=0.1, rho_avg=0.9, nds=0.95)
        self.assertIn("narrative", r.interpretation)

    def test_interpretation_operational(self):
        r = ConsistencyResult(claim="test", delta_x_claim=5.0, rho_avg=0.1, nds=0.1)
        self.assertIn("dynamics", r.interpretation)

    def test_interpretation_mixed(self):
        r = ConsistencyResult(claim="test", delta_x_claim=2.0, rho_avg=0.5, nds=0.5)
        self.assertIn("mixed", r.interpretation)


class TestVerificationProbes(unittest.TestCase):
    def test_generate_all(self):
        result = ConsistencyResult(
            claim="test claim",
            delta_x_claim=0.1,
            rho_avg=0.9,
            nds=0.95,
            decisions=[
                type("D", (), {"decision_name": "d1", "absorption_by_auxiliary": {"A": 5.0}})()
            ],
        )
        probes = VerificationProbes.generate_all(result, "CEO")
        self.assertGreater(len(probes), 3)
        self.assertTrue(any("CEO" in p for p in probes))


if __name__ == "__main__":
    unittest.main()
