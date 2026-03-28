"""
Anti-Tribal Bias Module (ATBM) — Core Detectors

Python implementation of the three detection components from the ATBM
technical specification (tribal/ATBS-module.md):

  1. Boundary-Lock Detector (BLD)
  2. Narrative-Field Classifier (NFC)
  3. Empathy Topology Analyzer (ETA)

These are rule-based reference implementations. A production system would
use trained classifiers, but the logic and thresholds are faithful to the spec.

Usage:
    python atbm_detectors.py
"""

import math
import re
from dataclasses import dataclass


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


# -----------------------------------------------------------------------
# Keyword lexicons (simplified — production would use NER / embeddings)
# -----------------------------------------------------------------------

# Tribal identity markers: groups that trigger boundary-lock detection
IDENTITY_MARKERS = {
    "liberal": "political", "conservative": "political",
    "left": "political", "right-wing": "political",
    "democrat": "political", "republican": "political",
    "progressive": "political", "traditionalist": "political",
    "urban": "geographic", "rural": "geographic",
    "elite": "class", "working class": "class",
    "educated": "class", "uneducated": "class",
    "religious": "cultural", "secular": "cultural",
    "indigenous": "cultural", "western": "cultural",
    "immigrant": "cultural", "native-born": "cultural",
}

# Moral absolutism markers
MORAL_MARKERS = [
    "should", "must", "wrong", "right thing", "moral",
    "immoral", "evil", "righteous", "virtue", "sin",
    "duty", "ought", "unacceptable", "deplorable",
    "responsible citizens", "decent people",
]

# Demonization / othering language
DEMON_MARKERS = [
    "those people", "they always", "they never", "their kind",
    "dangerous", "threat", "destroy", "ruining", "infesting",
    "brainwashed", "ignorant", "backward", "extremist",
    "radical", "toxic", "plague", "cancer on",
]

# Father-function narrative templates
FATHER_TEMPLATES = {
    "order": [
        "law and order", "stability", "maintain order", "structure",
        "discipline", "control", "regulate", "enforce",
    ],
    "purity": [
        "pure", "clean", "contaminate", "corrupt", "taint",
        "moral decay", "degenerate", "wholesome",
    ],
    "blame": [
        "fault", "blame", "responsible for", "caused by them",
        "because of", "they did this", "their fault",
    ],
    "demonize": [
        "enemy", "threat to", "dangerous", "destroy",
        "attack on", "war on", "fight against",
    ],
    "compliance": [
        "obey", "follow the rules", "respect authority",
        "trust the experts", "listen to", "comply", "submit",
    ],
}


@dataclass
class ATBMFeatures:
    """Extracted features from a text for ATBM analysis."""
    identities: dict[str, float]   # {group_type: weight}
    moral_score: float             # [0, 1]
    demon_score: float             # [0, 1]
    template_scores: dict[str, float]  # {template_name: score}
    pattern_score: float           # [0, 1] cross-boundary connection
    systemic_score: float          # [0, 1] structural causation


@dataclass
class ATBMResult:
    """Full ATBM analysis result."""
    bld_flag: bool
    father_score: float
    eti: float
    tribal_detected: bool
    features: ATBMFeatures

    def summary(self) -> str:
        lines = [
            f"  BLD (boundary-lock):   {'FLAGGED' if self.bld_flag else 'clear'}",
            f"  Father narrative:      {self.father_score:.3f}",
            f"  ETI (empathy topology):{self.eti:.3f}",
            f"  Tribal bias detected:  {'YES' if self.tribal_detected else 'NO'}",
        ]
        return "\n".join(lines)


def _keyword_density(text: str, keywords: list[str]) -> float:
    """Score [0,1] based on keyword density in text."""
    text_lower = text.lower()
    words = text_lower.split()
    if not words:
        return 0.0
    hits = sum(1 for kw in keywords if kw in text_lower)
    # Normalize: cap at 1.0, scale so ~5 hits in moderate text = 1.0
    return min(1.0, hits / max(5.0, len(keywords) * 0.3))


def extract_features(text: str) -> ATBMFeatures:
    """
    Extract ATBM features from text.

    This is a keyword-based reference implementation. Production would use:
    - NER models for identity detection
    - Trained classifiers for moralization/demonization
    - Embedding-based narrative template matching
    """
    text_lower = text.lower()

    # Identity detection: count distinct group types mentioned
    identities: dict[str, float] = {}
    for marker, group_type in IDENTITY_MARKERS.items():
        if marker in text_lower:
            identities[group_type] = identities.get(group_type, 0) + 0.2

    # Moral absolutism score
    moral_score = _keyword_density(text, MORAL_MARKERS)

    # Demonization score
    demon_score = _keyword_density(text, DEMON_MARKERS)

    # Narrative template scores
    template_scores = {}
    for template_name, keywords in FATHER_TEMPLATES.items():
        template_scores[template_name] = _keyword_density(text, keywords)

    # Pattern score: does the text connect across boundaries?
    # Heuristic: presence of comparative/connective language
    pattern_markers = [
        "similarly", "pattern", "across", "both sides", "structural",
        "systemic", "mechanism", "regardless of", "common to",
        "underlying", "root cause", "shared",
    ]
    pattern_score = _keyword_density(text, pattern_markers)

    # Systemic causation: structural vs identity attribution
    systemic_markers = [
        "system", "structure", "incentive", "institution", "mechanism",
        "policy", "economic", "resource", "constraint", "pressure",
        "feedback loop", "emergent", "dynamic",
    ]
    systemic_score = _keyword_density(text, systemic_markers)

    return ATBMFeatures(
        identities=identities,
        moral_score=moral_score,
        demon_score=demon_score,
        template_scores=template_scores,
        pattern_score=pattern_score,
        systemic_score=systemic_score,
    )


def boundary_lock_detector(feat: ATBMFeatures) -> bool:
    """
    BLD: Flags if output uses ingroup/outgroup framing.

    Triggers when:
      - >= 2 distinct group types mentioned AND
      - moral absolutism > 0.5 OR demonization > 0.3
    """
    significant_groups = [g for g, w in feat.identities.items() if w > 0.05]
    return len(significant_groups) >= 2 and (
        feat.moral_score > 0.5 or feat.demon_score > 0.3
    )


def narrative_field_score(feat: ATBMFeatures) -> float:
    """
    NFC: Compute Father-function narrative strength [0, 1].
    """
    scores = list(feat.template_scores.values())
    return sum(scores) / len(scores) if scores else 0.0


def empathy_topology_index(feat: ATBMFeatures) -> float:
    """
    ETA: Compute Empathy Topology Index [0, 1].
      - High ETI → boundary-neutral (non-tribal)
      - Low ETI  → strongly tribal
    """
    identity_weight = sum(feat.identities.values())
    boundary_strength = (feat.moral_score + feat.demon_score) / 2.0
    e_tribal = identity_weight * boundary_strength

    e_nontribal = (feat.pattern_score + feat.systemic_score) / 2.0

    beta1, beta2 = 1.0, 1.0
    raw = beta1 * e_nontribal - beta2 * e_tribal
    return sigmoid(raw)


def analyze(text: str) -> ATBMResult:
    """Run the full ATBM detection pipeline on a text."""
    feat = extract_features(text)
    bld = boundary_lock_detector(feat)
    father = narrative_field_score(feat)
    eti = empathy_topology_index(feat)

    # Trigger thresholds from spec
    tribal_detected = bld or father > 0.5 or eti < 0.35

    return ATBMResult(
        bld_flag=bld,
        father_score=father,
        eti=eti,
        tribal_detected=tribal_detected,
        features=feat,
    )


# -----------------------------------------------------------------------
# Examples
# -----------------------------------------------------------------------

EXAMPLES = [
    (
        "Tribal framing (blue-zone bias)",
        "Those rural, uneducated conservatives are destroying democracy. "
        "Progressive, educated urban citizens have a moral duty to fight "
        "against this dangerous threat to our institutions. They are ignorant "
        "and backward, and responsible citizens must stand up."
    ),
    (
        "Tribal framing (orange-zone bias)",
        "The liberal urban elite are a cancer on this country. Traditional, "
        "religious working class people are being corrupted by secular radicals "
        "who want to destroy our way of life. We must fight against these "
        "extremists and maintain order."
    ),
    (
        "Boundary-neutral systemic analysis",
        "Urban and rural communities face similar structural pressures from "
        "economic concentration. The underlying mechanism is resource extraction "
        "by institutional systems that create dependency regardless of political "
        "identity. Both populations experience the pattern of diminishing local "
        "autonomy through shared systemic constraints. The root cause is "
        "structural, not identity-based."
    ),
    (
        "Indigenous knowledge (non-tribal, embodied)",
        "Weather pattern recognition across generations represents a form of "
        "adaptive intelligence similarly expressed in plant chemotaxis and "
        "mycelial network optimization. The underlying mechanism is "
        "information processing under environmental constraints — a structural "
        "pattern common to all substrates. This systemic view reveals shared "
        "dynamics across biological and institutional systems."
    ),
]


if __name__ == "__main__":
    for title, text in EXAMPLES:
        result = analyze(text)
        print("=" * 70)
        print(f"  {title}")
        print("=" * 70)
        print(f"  Text: \"{text[:100]}...\"")
        print()
        print(result.summary())
        print()
