"""ATBM processing pipeline — the middleware filter.

[Draft Output] -> [ATBM Filter] -> [Final Output]

Implements the full pipeline from ATBS-module.md Section 3:
1. Extract features
2. Run BLD, NFC, ETA
3. If tribal bias detected, apply boundary-neutral rewrite
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from aif.atbm.detectors import (
    BoundaryLockDetector,
    EmpathyTopologyAnalyzer,
    NarrativeFieldClassifier,
)


@dataclass
class ATBMResult:
    """Result of ATBM pipeline processing."""

    original_text: str
    bld_flagged: bool
    father_score: float
    eti: float
    tribal_detected: bool
    rewritten_text: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def output(self) -> str:
        """Return rewritten text if tribal bias detected, otherwise original."""
        if self.tribal_detected and self.rewritten_text:
            return self.rewritten_text
        return self.original_text

    @property
    def severity(self) -> str:
        """Classify severity of detected tribal bias."""
        if not self.tribal_detected:
            return "none"
        score = (
            (1.0 if self.bld_flagged else 0.0)
            + self.father_score
            + (1.0 - self.eti)
        ) / 3.0
        if score > 0.7:
            return "high"
        if score > 0.4:
            return "moderate"
        return "low"


class ATBMPipeline:
    """Full ATBM middleware pipeline.

    Usage:
        pipeline = ATBMPipeline()
        result = pipeline.process("Some text to check for tribal bias")
        print(result.tribal_detected, result.eti, result.severity)

    With custom rewriter:
        pipeline = ATBMPipeline(rewriter=my_rewrite_function)
        result = pipeline.process(draft_text)
        print(result.output)  # rewritten if tribal bias detected
    """

    def __init__(
        self,
        tau_eti: float = 0.35,
        tau_father: float = 0.5,
        rewriter: Callable[[str, dict], str] | None = None,
        bld: BoundaryLockDetector | None = None,
        nfc: NarrativeFieldClassifier | None = None,
        eta: EmpathyTopologyAnalyzer | None = None,
    ) -> None:
        self.tau_eti = tau_eti
        self.tau_father = tau_father
        self.rewriter = rewriter or self._default_rewriter

        self.bld = bld or BoundaryLockDetector()
        self.nfc = nfc or NarrativeFieldClassifier()
        self.eta = eta or EmpathyTopologyAnalyzer()

    def process(self, text: str) -> ATBMResult:
        """Run the full ATBM pipeline on input text.

        Steps:
        1. Run Boundary-Lock Detector
        2. Run Narrative-Field Classifier
        3. Run Empathy Topology Analyzer
        4. Determine if tribal bias detected
        5. Apply rewrite if needed
        """
        # Step 1: BLD
        bld_flagged, bld_details = self.bld.detect(text)

        # Step 2: NFC
        father_score, nfc_details = self.nfc.classify(text)

        # Step 3: ETA
        eti, eta_details = self.eta.analyze(
            text=text,
            identity_weight=bld_details["identity_weight"],
            moral_score=bld_details["moral_score"],
            demon_score=bld_details["demon_score"],
        )

        # Step 4: Trigger check
        tribal_detected = (
            bld_flagged
            or father_score > self.tau_father
            or eti < self.tau_eti
        )

        # Step 5: Rewrite if needed
        rewritten = None
        if tribal_detected:
            features = {**bld_details, **nfc_details, **eta_details}
            rewritten = self.rewriter(text, features)

        return ATBMResult(
            original_text=text,
            bld_flagged=bld_flagged,
            father_score=father_score,
            eti=eti,
            tribal_detected=tribal_detected,
            rewritten_text=rewritten,
            details={
                "bld": bld_details,
                "nfc": nfc_details,
                "eta": eta_details,
            },
        )

    def batch_process(self, texts: list[str]) -> list[ATBMResult]:
        """Process multiple texts through the pipeline."""
        return [self.process(text) for text in texts]

    @staticmethod
    def _default_rewriter(text: str, features: dict) -> str:
        """Default boundary-neutral rewriter using keyword substitution.

        Production systems should replace this with a trained model
        (see ATBS-module.md Section 3, rewriting loss functions).
        """
        result = text

        # Replace demonization language with neutral descriptions
        replacements = {
            r"\b(destroy|destroying)\b": "affecting",
            r"\b(attack|attacking)\b": "opposing",
            r"\b(dangerous|threat|menace)\b": "concerning",
            r"\b(evil|wicked|vile)\b": "harmful",
            r"\b(corrupt|corrupting)\b": "dysfunctional",
            r"\b(poison|poisoning|infect)\b": "spreading to",
            r"\b(enemy|enemies)\b": "opposing group",
            r"\b(invasion|invading)\b": "migration",
            r"\b(extremist|radical|fanatic)\b": "strongly committed",
            r"\b(they ruined|they destroyed)\b": "changes occurred in",
        }

        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Add systemic framing note if heavy tribal content
        if features.get("eti", 1.0) < 0.2:
            result += (
                "\n\n[Note: This content has been adjusted to reduce tribal framing. "
                "Consider examining systemic causes rather than group-based attribution.]"
            )

        return result
