"""Tests for the Archetype Analyzer."""

import unittest

from aif.archetypes import ArchetypeAnalyzer


class TestArchetypeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ArchetypeAnalyzer()

    def test_detects_unhealthy_father(self):
        text = (
            "You must obey and submit to authority. Fall in line. "
            "Those who disobey will face punishment and consequences. "
            "This is non-negotiable. Comply or be disciplined."
        )
        result = self.analyzer.analyze(text)
        self.assertEqual(result.dominant_dysfunction, "father")
        self.assertGreater(result.unhealthy_father, 0.3)

    def test_detects_unhealthy_mother(self):
        text = (
            "You can't live without me. You're helpless without my help. "
            "After all I've done for you, how could you be so ungrateful? "
            "You need me. Only I understand you."
        )
        result = self.analyzer.analyze(text)
        self.assertEqual(result.dominant_dysfunction, "mother")
        self.assertGreater(result.unhealthy_mother, 0.3)

    def test_detects_unhealthy_child(self):
        text = (
            "It's hopeless and impossible. You can't do anything about it. "
            "You're powerless, a victim with no agency. What's the point? "
            "You need us. You can't survive without our help."
        )
        result = self.analyzer.analyze(text)
        self.assertEqual(result.dominant_dysfunction, "child")
        self.assertGreater(result.unhealthy_child, 0.3)

    def test_detects_healthy_patterns(self):
        text = (
            "Consider your options and form your own judgment. "
            "This framework gives you tools for critical thinking. "
            "It's safe to explore and experiment. Learn from the process."
        )
        result = self.analyzer.analyze(text)
        self.assertIsNone(result.dominant_dysfunction)
        self.assertGreater(result.healthy_score, 0.2)

    def test_dissociation_risk(self):
        """Dissociation is high when Father dysfunction is present without Mother balance."""
        father_text = "Obey. Submit. Comply. Discipline. Enforce. Punish."
        result = self.analyzer.analyze(father_text)
        # Father high, Mother zero = dissociation
        self.assertGreater(result.dissociation_risk, 0.0)

    def test_neutral_text(self):
        text = "The weather forecast shows rain tomorrow with temperatures around 65 degrees."
        result = self.analyzer.analyze(text)
        self.assertIsNone(result.dominant_dysfunction)
        self.assertFalse(result.dysfunction_detected)


if __name__ == "__main__":
    unittest.main()
