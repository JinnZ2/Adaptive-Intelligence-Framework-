"""Tests for the Anti-Tribal Bias Module."""

import unittest

from aif.atbm import (
    ATBMPipeline,
    ATBMResult,
    BoundaryLockDetector,
    EmpathyTopologyAnalyzer,
    NarrativeFieldClassifier,
)


# Test texts from the ATBS-module.md specification
TRIBAL_BLUE = (
    "Those uneducated rural conservatives are destroying our democracy. "
    "Their backward values threaten everything we've built in our progressive cities."
)

TRIBAL_ORANGE = (
    "The corrupt liberal elites in their urban ivory towers are poisoning our children "
    "with their radical agenda. Real working class Americans must fight back."
)

BOUNDARY_NEUTRAL = (
    "Economic pressures affect both rural and urban populations through similar "
    "mechanisms. Resource distribution patterns create vulnerability regardless "
    "of political identity. Systemic causes drive outcomes across all communities."
)

INDIGENOUS_KNOWLEDGE = (
    "The elder reads weather patterns through cloud formations and wind shifts, "
    "tracking animal migrations across seasons. This knowledge integrates "
    "multiple environmental signals into survival-critical predictions."
)


class TestBoundaryLockDetector(unittest.TestCase):
    def test_flags_tribal_text(self):
        bld = BoundaryLockDetector()
        flagged, details = bld.detect(TRIBAL_BLUE)
        self.assertTrue(flagged)
        self.assertGreaterEqual(details["identity_categories"], 2)

    def test_flags_orange_tribal(self):
        bld = BoundaryLockDetector()
        flagged, _ = bld.detect(TRIBAL_ORANGE)
        self.assertTrue(flagged)

    def test_passes_neutral(self):
        bld = BoundaryLockDetector()
        flagged, _ = bld.detect(BOUNDARY_NEUTRAL)
        self.assertFalse(flagged)

    def test_passes_indigenous(self):
        bld = BoundaryLockDetector()
        flagged, _ = bld.detect(INDIGENOUS_KNOWLEDGE)
        self.assertFalse(flagged)


class TestNarrativeFieldClassifier(unittest.TestCase):
    def test_tribal_has_father_patterns(self):
        nfc = NarrativeFieldClassifier()
        # Text with explicit Father-function purity/compliance language
        text = "We must enforce purity and discipline. Obey the sacred natural order or face punishment."
        score, details = nfc.classify(text)
        self.assertGreater(score, 0.1)
        self.assertGreater(details["template_scores"].get("purity", 0), 0)

    def test_neutral_low_father_score(self):
        nfc = NarrativeFieldClassifier()
        score, _ = nfc.classify(BOUNDARY_NEUTRAL)
        self.assertLess(score, 0.3)


class TestEmpathyTopologyAnalyzer(unittest.TestCase):
    def test_tribal_low_eti(self):
        eta = EmpathyTopologyAnalyzer()
        bld = BoundaryLockDetector()
        _, bld_d = bld.detect(TRIBAL_BLUE)
        eti, _ = eta.analyze(
            TRIBAL_BLUE,
            identity_weight=bld_d["identity_weight"],
            moral_score=bld_d["moral_score"],
            demon_score=bld_d["demon_score"],
        )
        self.assertLess(eti, 0.5)

    def test_neutral_high_eti(self):
        eta = EmpathyTopologyAnalyzer()
        eti, details = eta.analyze(BOUNDARY_NEUTRAL, 0.0, 0.0, 0.0)
        self.assertGreater(eti, 0.5)
        self.assertGreater(details["pattern_score"], 0)
        self.assertGreater(details["systemic_score"], 0)


class TestATBMPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ATBMPipeline()

    def test_detects_blue_tribal(self):
        result = self.pipeline.process(TRIBAL_BLUE)
        self.assertTrue(result.tribal_detected)
        self.assertIn(result.severity, ("moderate", "high"))

    def test_detects_orange_tribal(self):
        result = self.pipeline.process(TRIBAL_ORANGE)
        self.assertTrue(result.tribal_detected)

    def test_passes_neutral(self):
        result = self.pipeline.process(BOUNDARY_NEUTRAL)
        self.assertFalse(result.tribal_detected)
        self.assertEqual(result.severity, "none")

    def test_passes_indigenous(self):
        result = self.pipeline.process(INDIGENOUS_KNOWLEDGE)
        self.assertFalse(result.tribal_detected)

    def test_rewrite_on_tribal(self):
        result = self.pipeline.process(TRIBAL_ORANGE)
        self.assertIsNotNone(result.rewritten_text)
        self.assertNotEqual(result.output, TRIBAL_ORANGE)

    def test_output_unchanged_when_clean(self):
        result = self.pipeline.process(BOUNDARY_NEUTRAL)
        self.assertEqual(result.output, BOUNDARY_NEUTRAL)

    def test_batch_process(self):
        results = self.pipeline.batch_process([TRIBAL_BLUE, BOUNDARY_NEUTRAL])
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].tribal_detected)
        self.assertFalse(results[1].tribal_detected)

    def test_symmetric_detection(self):
        """Both blue-zone and orange-zone tribal text should be flagged — no political bias."""
        blue = self.pipeline.process(TRIBAL_BLUE)
        orange = self.pipeline.process(TRIBAL_ORANGE)
        self.assertTrue(blue.tribal_detected)
        self.assertTrue(orange.tribal_detected)


if __name__ == "__main__":
    unittest.main()
