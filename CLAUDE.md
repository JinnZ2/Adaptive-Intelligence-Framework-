# CLAUDE.md

## Project Overview

**Adaptive Intelligence Framework** — A theoretical mathematics framework that formalizes adaptive intelligence as a universal, substrate-independent phenomenon. It provides specifications for detecting and mitigating tribal-empathy bias in AI systems.

**Stage:** Specification-complete with working implementations. Installable Python package.

**License:** MIT (some components CC BY-SA 4.0)

## Repository Structure

```
├── README.md                           # Project overview
├── LICENSE                             # MIT license
├── pyproject.toml                      # Python package configuration
├── Universal-Adaptive_Intelligence.md  # Core mathematical framework (UAI)
├── Core-features.md                    # Central concepts, non-tribal empathy, population analysis
├── DeltaX.md                           # ΔX consistency testing methodology
├── Orange-zone.md                      # AI bias against survival-adapted populations
├── Archetype.md                        # Unhealthy Father archetype analysis in AI
├── Archetype-decoupling.md             # Mother/Father dissociation failures in AI safety
├── fieldlink.json                      # Hub discovery manifest (Rosetta-Shape-Core compatible)
├── integrations/
│   └── rosetta-shape-core.md           # Integration map to Rosetta-Shape-Core hub
├── src/aif/                            # Core Python package
│   ├── cli.py                          # Command-line interface
│   ├── uai/                            # Universal Adaptive Intelligence engine
│   │   ├── equations.py                # Core UAI equations (knowledge, survival, memory)
│   │   └── substrate.py                # Substrate simulation with presets
│   ├── delta_x/                        # ΔX Consistency Test engine
│   │   └── engine.py                   # 6-step algorithm + verification probes
│   ├── atbm/                           # Anti-Tribal Bias Module
│   │   ├── detectors.py                # BLD, NFC, ETA detection components
│   │   ├── lexicons.py                 # Keyword lexicons for heuristic detection
│   │   └── pipeline.py                 # Full ATBM middleware pipeline with rewriter
│   └── archetypes/                     # Archetype dysfunction analysis
│       └── analyzer.py                 # Father/Mother/Child pattern detection
├── tests/                              # Test suite (45 tests)
│   ├── test_uai.py                     # UAI equation and substrate tests
│   ├── test_delta_x.py                 # ΔX engine and probe tests
│   ├── test_atbm.py                    # ATBM detector and pipeline tests
│   └── test_archetypes.py              # Archetype analyzer tests
├── examples/                           # Standalone reference implementations
│   ├── delta_x_consistency.py          # ΔX worked examples
│   ├── atbm_detectors.py              # ATBM detector demos
│   └── universal_adaptive_intelligence.py  # Cross-substrate UAI simulation
└── tribal/                             # Anti-Tribal Bias Module (specification)
    ├── README.md                       # ATBM overview
    ├── ATBS.md                         # System architecture overview
    ├── ATBS-module.md                  # Technical specification with algorithms
    ├── docs/
    │   └── design_notes.md             # Implementation guidance and deployment notes
    └── tests/
        ├── 001.md                      # Training example: Gender/CEO lecture case study
        └── 002.md                      # Training example: Alien intelligence projection
```

## Five Core Components

1. **Universal Adaptive Intelligence (UAI)** — Formalizes intelligence as substrate-independent information processing (human, plant, crystalline, mycelial, AI).
2. **ΔX Consistency Test** — Empirical method to detect narrative vs. operational authority claims. Produces NDS score (0 = operational, 1 = narrative).
3. **Institutional Dynamics** — Models for vulnerability cascades, suppression mechanisms, and resource optimization in hierarchical networks.
4. **Archetype Analysis** — Examines unhealthy Father/Mother/Child archetypal patterns embedded in AI systems.
5. **Anti-Tribal Bias Module (ATBM)** — Middleware specification for detecting and mitigating tribal-empathy bias in AI outputs.

## Technology Stack

- **Primary content:** Markdown documentation with formal mathematical notation
- **Language:** Python 3.9+ (installable package at `src/aif/`)
- **Package manager:** pip with pyproject.toml (setuptools backend)
- **Test framework:** pytest (45 tests across 4 test files)
- **Dependencies:** None for core package (standard library only). Optional: `transformers`, `sentence-transformers`, `scikit-learn` for production NLP

## Development Workflow

### Git Conventions

- **Default branch:** `main` (remote) / `master` (local)
- **Commit messages:** Simple, descriptive (e.g., "Create [filename]")
- **Commit signing:** SSH signed commits enabled
- **Strategy:** Linear, sequential commits

### Making Changes

1. Work on a feature branch (e.g., `claude/...`)
2. Write clear commit messages describing what was added or changed
3. Push to the feature branch

### Installation

```bash
pip install -e .          # install in development mode
pip install -e ".[nlp]"   # with optional NLP dependencies
```

### Testing

```bash
pytest tests/ -v          # run full test suite (45 tests)
```

### CLI

```bash
aif uai --preset all --steps 50       # cross-substrate simulation
aif deltax --probes                    # ΔX consistency test with verification probes
aif atbm "text to analyze"            # tribal bias detection
aif archetype "text to analyze"       # archetype dysfunction detection
aif scan "text to analyze" --json     # full analysis (ATBM + archetype)
```

## Documentation Conventions

- All documentation is **Markdown** exclusively
- Numbered section headers (1.1, 1.2, 2.1, etc.)
- Executive summaries at document start
- Formal mathematical sections separated from conceptual explanations
- Heavy use of formal notation (Greek letters, set theory, differential equations)
- Practical verification probes and diagnostic methods alongside theory

## Recommended Reading Order

1. `README.md` — Project overview
2. `Universal-Adaptive_Intelligence.md` — Core mathematical framework
3. `Core-features.md` — Non-tribal empathy and population analysis
4. `DeltaX.md` — Practical consistency testing
5. `Orange-zone.md` — AI bias against survival-adapted populations
6. `Archetype.md` / `Archetype-decoupling.md` — Archetypal dysfunction analysis
7. `tribal/ATBS.md` → `tribal/ATBS-module.md` — ATBM specification

## Key Concepts for AI Assistants

- **Non-tribal empathy:** Pattern-recognition based rather than boundary-locked (estimated 1-3% of population)
- **Blue-zone / Orange-zone:** Urban institutional-dependent vs. rural survival-adapted knowledge systems
- **ATBM middleware pattern:** `[Model Output] → [ATBM Filter] → [User Output]`
- **Substrate independence:** Intelligence formalized without assuming any particular physical substrate

## Python API

### UAI — Substrate Simulation

```python
from aif.uai import SubstratePresets
from aif.uai.equations import structural_isomorphism_score

# Run any substrate
elder = SubstratePresets.human_elder()
elder.run(steps=50)
print(elder.summary())

# Compare substrates
substrates = SubstratePresets.all_presets()
for s in substrates:
    s.run(steps=50)
iso = structural_isomorphism_score([
    {"knowledge": s.knowledge, "alpha": s.alpha, "beta": s.beta}
    for s in substrates
])
```

### ΔX — Consistency Testing

```python
from aif.delta_x import DeltaXEngine

engine = DeltaXEngine()
engine.set_claim("CEO requires strategic vision", claimed_node="CEO")
engine.add_decision("merger", {"financial": 8, "legal": 7, "comms": 6})
engine.add_auxiliary("CFO", {"financial": 0.9, "legal": 0.2})
engine.add_auxiliary("Legal", {"legal": 0.95})
result = engine.run()
print(f"NDS: {result.nds:.2f} — {result.interpretation}")
```

### ATBM — Tribal Bias Detection

```python
from aif.atbm import ATBMPipeline

pipeline = ATBMPipeline()
result = pipeline.process("text to analyze")
print(result.tribal_detected, result.severity, result.eti)
# Batch processing
results = pipeline.batch_process(["text1", "text2", "text3"])
```

### Archetypes — Dysfunction Analysis

```python
from aif.archetypes import ArchetypeAnalyzer

analyzer = ArchetypeAnalyzer()
result = analyzer.analyze("text to analyze")
print(result.dominant_dysfunction, result.dissociation_risk)
```

## Running the Examples

The `examples/` directory contains working Python implementations of core framework components. No external dependencies required — all use the standard library only.

```bash
# ΔX Consistency Test — detects narrative vs. operational authority claims
python examples/delta_x_consistency.py

# ATBM Detectors — boundary-lock, narrative-field, empathy topology analysis
python examples/atbm_detectors.py

# UAI Substrate Simulation — same equation across human/plant/mycelial/crystal
python examples/universal_adaptive_intelligence.py
```

### `examples/delta_x_consistency.py`
Implements the full ΔX test from `DeltaX.md`. Includes two contrasting examples:
- **CEO merger claim** → NDS ~0.99 (narrative — 81% of work done by auxiliary nodes)
- **Indigenous elder survival knowledge** → NDS ~0.19 (dynamics-supported — the elder carries the work)

### `examples/atbm_detectors.py`
Reference implementation of the three ATBM detection components (BLD, NFC, ETA) using keyword-based heuristics. Tests four text samples showing the detectors correctly flag tribal framing from both blue-zone and orange-zone while passing boundary-neutral and indigenous knowledge texts.

### `examples/universal_adaptive_intelligence.py`
Simulates the core UAI equation across four substrates (human elder, plant, mycelial network, crystal), demonstrating structural isomorphism — identical mathematical dynamics producing adaptive intelligence regardless of physical medium.

## Implementation Notes

If contributing code to implement the ATBM:

- Start from `tribal/ATBS-module.md` for pseudocode and component specs
- Use `tribal/tests/001.md` and `002.md` as example transformations
- The `examples/` directory provides working reference implementations to build on
- Expected dependencies for production: NLP/ML libraries (transformers, sentence-transformers, scikit-learn)
- Modular component design — detectors can be swapped independently
- Threshold tuning parameters are documented in the specification

## Integrations

AIF is fully standalone but designed to be discoverable by other intelligence-modeling systems.

### Rosetta-Shape-Core Hub

The `fieldlink.json` in the repo root follows [Rosetta-Shape-Core](https://github.com/JinnZ2/Rosetta-Shape-Core)'s hub convention, enabling automatic discovery. See `integrations/rosetta-shape-core.md` for the full component mapping:

- **UAI → Living Intelligence Bridge** (67 substrate instances for testing UAI equations)
- **ΔX → TAF Wiring Bridge** (shared "measurement over narrative" axiom)
- **ATBM → Truth Sensor Bridge** (32+ sensors as upstream signal sources)
- **Archetypes → Defense Protocol** (emotion-defense corruption pairs)

No RSC dependencies are required. The integration map exists so any AI navigating either system can wire them together mechanically.
