# CLAUDE.md

## Project Overview

**Adaptive Intelligence Framework** — A theoretical mathematics framework that formalizes adaptive intelligence as a universal, substrate-independent phenomenon. It provides specifications for detecting and mitigating tribal-empathy bias in AI systems.

**Stage:** Early specification/theoretical (pre-implementation). Documentation-complete; code is stubbed.

**License:** MIT (some components CC BY-SA 4.0)

## Repository Structure

```
├── README.md                           # Project overview
├── LICENSE                             # MIT license
├── Universal-Adaptive_Intelligence.md  # Core mathematical framework (UAI)
├── Core-features.md                    # Central concepts, non-tribal empathy, population analysis
├── DeltaX.md                           # ΔX consistency testing methodology
├── Orange-zone.md                      # AI bias against survival-adapted populations
├── Archetype.md                        # Unhealthy Father archetype analysis in AI
├── Archetype-decoupling.md             # Mother/Father dissociation failures in AI safety
└── tribal/                             # Anti-Tribal Bias Module (ATBM)
    ├── README.md                       # ATBM overview
    ├── ATBS.md                         # System architecture overview
    ├── ATBS-module.md                  # Technical specification with algorithms
    ├── docs/
    │   └── design_notes.md             # Implementation guidance and deployment notes
    └── tests/
        ├── 001.md                      # Training example: Gender/CEO lecture case study
        ├── 002.md                      # Training example: Alien intelligence projection
        └── test_detectors.py           # Test stub (not yet implemented)
```

## Five Core Components

1. **Universal Adaptive Intelligence (UAI)** — Formalizes intelligence as substrate-independent information processing (human, plant, crystalline, mycelial, AI).
2. **ΔX Consistency Test** — Empirical method to detect narrative vs. operational authority claims. Produces NDS score (0 = operational, 1 = narrative).
3. **Institutional Dynamics** — Models for vulnerability cascades, suppression mechanisms, and resource optimization in hierarchical networks.
4. **Archetype Analysis** — Examines unhealthy Father/Mother/Child archetypal patterns embedded in AI systems.
5. **Anti-Tribal Bias Module (ATBM)** — Middleware specification for detecting and mitigating tribal-empathy bias in AI outputs.

## Technology Stack

- **Primary content:** Markdown documentation with formal mathematical notation
- **Language (planned):** Python (single test stub at `tribal/tests/test_detectors.py`)
- **No package manager, build system, CI/CD, or linting** is configured yet

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

### Testing

No test infrastructure exists yet. The file `tribal/tests/test_detectors.py` is a stub placeholder. Future implementation would use Python testing frameworks.

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
