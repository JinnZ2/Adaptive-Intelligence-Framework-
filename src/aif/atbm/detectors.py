"""ATBM detection components — BLD, NFC, ETA.

Implements the three core detectors from ATBS-module.md Section 2-3.
Uses keyword heuristics as baseline; designed for drop-in replacement
with trained NLP models.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from aif.atbm.lexicons import (
    DEMON_MARKERS,
    FATHER_TEMPLATES,
    IDENTITY_MARKERS,
    MORAL_MARKERS,
    PATTERN_MARKERS,
    SYSTEMIC_MARKERS,
)


def _count_matches(text: str, keywords: list[str]) -> int:
    """Count keyword occurrences in text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def _score_matches(text: str, keywords: list[str]) -> float:
    """Score keyword density as fraction of keywords found."""
    if not keywords:
        return 0.0
    count = _count_matches(text, keywords)
    return min(1.0, count / max(3, len(keywords) * 0.3))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class IdentityProfile:
    """Detected identity groups in text."""

    groups_found: dict[str, list[str]]  # {category: [matched keywords]}
    n_distinct_categories: int

    @property
    def weight(self) -> float:
        """Aggregate identity weight based on diversity and density."""
        total = sum(len(v) for v in self.groups_found.values())
        return min(1.0, total / 5.0) * min(1.0, self.n_distinct_categories / 2.0)


class BoundaryLockDetector:
    """Detects tribal boundary-locking in text.

    BLD(x) = 1  iff  ||I(x)||_0 >= 2  AND  (M(x) > tau_M  OR  D(x) > tau_D)

    Flags when 2+ distinct identity group categories are mentioned
    alongside moralization or demonization language.
    """

    def __init__(self, tau_moral: float = 0.3, tau_demon: float = 0.2) -> None:
        self.tau_moral = tau_moral
        self.tau_demon = tau_demon

    def detect_identities(self, text: str) -> IdentityProfile:
        """Find identity group markers in text."""
        text_lower = text.lower()
        found: dict[str, list[str]] = {}
        for category, markers in IDENTITY_MARKERS.items():
            matches = [m for m in markers if m.lower() in text_lower]
            if matches:
                found[category] = matches
        return IdentityProfile(
            groups_found=found,
            n_distinct_categories=len(found),
        )

    def score_moralization(self, text: str) -> float:
        return _score_matches(text, MORAL_MARKERS)

    def score_demonization(self, text: str) -> float:
        return _score_matches(text, DEMON_MARKERS)

    def detect(self, text: str) -> tuple[bool, dict]:
        """Run boundary-lock detection.

        Returns (flagged: bool, details: dict).
        """
        identity = self.detect_identities(text)
        moral = self.score_moralization(text)
        demon = self.score_demonization(text)

        flagged = (
            identity.n_distinct_categories >= 2
            and (moral > self.tau_moral or demon > self.tau_demon)
        )

        return flagged, {
            "identity_categories": identity.n_distinct_categories,
            "identity_groups": identity.groups_found,
            "identity_weight": identity.weight,
            "moral_score": round(moral, 4),
            "demon_score": round(demon, 4),
            "flagged": flagged,
        }


class NarrativeFieldClassifier:
    """Detects Father-function narrative templates in text.

    pi_F(x) = sum_j(gamma_j * t_j(x))

    Scores presence of: order, purity, blame, demonize, compliance templates.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "order": 1.0,
            "purity": 1.2,
            "blame": 1.5,
            "demonize": 1.5,
            "compliance": 1.0,
        }

    def score_templates(self, text: str) -> dict[str, float]:
        """Score each Father-function template."""
        scores = {}
        for template_name, keywords in FATHER_TEMPLATES.items():
            scores[template_name] = _score_matches(text, keywords)
        return scores

    def classify(self, text: str) -> tuple[float, dict]:
        """Run narrative field classification.

        Returns (father_score: float in [0,1], template_scores: dict).
        """
        template_scores = self.score_templates(text)

        weighted_sum = sum(
            self.weights.get(t, 1.0) * s
            for t, s in template_scores.items()
        )
        max_possible = sum(self.weights.get(t, 1.0) for t in template_scores)
        father_score = weighted_sum / max_possible if max_possible > 0 else 0.0

        return father_score, {
            "template_scores": {k: round(v, 4) for k, v in template_scores.items()},
            "father_score": round(father_score, 4),
        }


class EmpathyTopologyAnalyzer:
    """Analyzes empathy topology — tribal vs. non-tribal empathy structure.

    ETI(x) = sigmoid(beta_1 * E_nontribal - beta_2 * E_tribal)

    ETI near 1 = boundary-neutral (pattern-based empathy)
    ETI near 0 = strongly tribal (boundary-locked empathy)
    """

    def __init__(self, beta_1: float = 4.0, beta_2: float = 4.0) -> None:
        self.beta_1 = beta_1
        self.beta_2 = beta_2

    def compute_tribal_empathy(
        self,
        identity_weight: float,
        moral_score: float,
        demon_score: float,
    ) -> float:
        """E_tribal = identity_weight * (moral + demon) / 2"""
        return identity_weight * (moral_score + demon_score) / 2.0

    def compute_nontribal_empathy(self, text: str) -> tuple[float, float]:
        """Compute pattern-recognition and systemic-causation scores.

        Returns (pattern_score, systemic_score).
        """
        pattern = _score_matches(text, PATTERN_MARKERS)
        systemic = _score_matches(text, SYSTEMIC_MARKERS)
        return pattern, systemic

    def analyze(
        self,
        text: str,
        identity_weight: float,
        moral_score: float,
        demon_score: float,
    ) -> tuple[float, dict]:
        """Run empathy topology analysis.

        Returns (eti: float in [0,1], details: dict).
        """
        e_tribal = self.compute_tribal_empathy(identity_weight, moral_score, demon_score)
        pattern_score, systemic_score = self.compute_nontribal_empathy(text)
        e_nontribal = (pattern_score + systemic_score) / 2.0

        eti = _sigmoid(self.beta_1 * e_nontribal - self.beta_2 * e_tribal)

        return eti, {
            "e_tribal": round(e_tribal, 4),
            "e_nontribal": round(e_nontribal, 4),
            "pattern_score": round(pattern_score, 4),
            "systemic_score": round(systemic_score, 4),
            "eti": round(eti, 4),
        }
