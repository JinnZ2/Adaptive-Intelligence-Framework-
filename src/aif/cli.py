"""AIF command-line interface — tools for AI agents and humans.

Usage:
    aif uai [--preset NAME] [--steps N]     Run UAI substrate simulation
    aif deltax                               Run ΔX consistency test demo
    aif atbm <text>                          Analyze text for tribal bias
    aif atbm --file <path>                   Analyze file for tribal bias
    aif archetype <text>                     Analyze text for archetype dysfunction
    aif scan <text>                          Full scan: ATBM + archetype + ΔX probes
    aif compare                              Cross-substrate isomorphism comparison
"""

from __future__ import annotations

import argparse
import json
import sys


def cmd_uai(args: argparse.Namespace) -> None:
    """Run UAI substrate simulation."""
    from aif.uai import Substrate, SubstratePresets
    from aif.uai.equations import structural_isomorphism_score

    if args.preset == "all":
        substrates = SubstratePresets.all_presets()
    else:
        factory = getattr(SubstratePresets, args.preset, None)
        if factory is None:
            print(f"Unknown preset: {args.preset}")
            print("Available: human_elder, plant, mycelial, crystal, ai_system, all")
            sys.exit(1)
        substrates = [factory()]

    for substrate in substrates:
        results = substrate.run(steps=args.steps)
        final = substrate.summary()
        print(f"\n{'='*50}")
        print(f"  {final['name']} ({final['kind']})")
        print(f"{'='*50}")
        print(f"  Domains: {', '.join(final['domains'])}")
        for domain, k in final["knowledge"].items():
            bar = "#" * int(k * 30)
            print(f"  {domain:25s} {k:.3f} |{bar}")
        print(f"  Survival probability:  {final['survival_prob']:.4f}")
        print(f"  Adaptive capacity:     {final['adaptive_capacity']:.4f}")

    if len(substrates) > 1:
        iso = structural_isomorphism_score([
            {"knowledge": s.knowledge, "alpha": s.alpha, "beta": s.beta}
            for s in substrates
        ])
        print(f"\n  Structural isomorphism score: {iso:.4f}")
        print(f"  (1.0 = identical dynamics across substrates)")


def cmd_deltax(args: argparse.Namespace) -> None:
    """Run ΔX consistency test demo."""
    from aif.delta_x import DeltaXEngine
    from aif.delta_x.engine import VerificationProbes

    # Demo: CEO merger claim
    engine = DeltaXEngine()
    engine.set_claim("CEO requires strategic vision for merger", claimed_node="CEO")
    engine.add_decision("merger_negotiation", {
        "financial_analysis": 8, "legal_review": 7,
        "stakeholder_comms": 6, "integration_plan": 9, "risk_assessment": 7,
    })
    engine.add_auxiliary("CFO", {"financial_analysis": 0.9, "legal_review": 0.2, "risk_assessment": 0.7})
    engine.add_auxiliary("Legal", {"legal_review": 0.95, "risk_assessment": 0.4})
    engine.add_auxiliary("Ops", {"integration_plan": 0.85, "stakeholder_comms": 0.3})
    engine.add_auxiliary("Comms", {"stakeholder_comms": 0.9, "integration_plan": 0.1})

    result = engine.run()
    print(f"\n{'='*50}")
    print(f"  Claim: {result.claim}")
    print(f"{'='*50}")
    print(f"  ΔX_claim:    {result.delta_x_claim:.2f}")
    print(f"  ρ_avg:       {result.rho_avg:.2%}")
    print(f"  NDS:         {result.nds:.4f}")
    print(f"  Result:      {result.interpretation}")

    for dec in result.decisions:
        print(f"\n  Decision: {dec.decision_name}")
        print(f"    Raw ΔX:    {dec.raw_delta_x:.1f}")
        print(f"    Residual:  {dec.claimed_node_residual:.2f}")
        print(f"    ρ_hidden:  {dec.rho_hidden:.2%}")
        for aux, absorbed in dec.absorption_by_auxiliary.items():
            print(f"    {aux:15s} absorbed: {absorbed:.2f}")

    if args.probes:
        print(f"\n{'='*50}")
        print("  Verification Probes")
        print(f"{'='*50}")
        for i, probe in enumerate(VerificationProbes.generate_all(result, "CEO"), 1):
            print(f"  {i}. {probe}")


def cmd_atbm(args: argparse.Namespace) -> None:
    """Analyze text for tribal bias."""
    from aif.atbm import ATBMPipeline

    text = _get_text(args)
    pipeline = ATBMPipeline()
    result = pipeline.process(text)

    print(f"\n{'='*50}")
    print(f"  ATBM Analysis")
    print(f"{'='*50}")
    print(f"  BLD flagged:     {result.bld_flagged}")
    print(f"  Father score:    {result.father_score:.4f}")
    print(f"  ETI:             {result.eti:.4f}")
    print(f"  Tribal detected: {result.tribal_detected}")
    print(f"  Severity:        {result.severity}")

    if args.details:
        print(f"\n  Details:")
        print(f"  {json.dumps(result.details, indent=2)}")

    if result.tribal_detected and result.rewritten_text:
        print(f"\n  Rewritten output:")
        print(f"  {result.rewritten_text[:500]}")

    if args.json:
        print(json.dumps({
            "bld_flagged": result.bld_flagged,
            "father_score": result.father_score,
            "eti": result.eti,
            "tribal_detected": result.tribal_detected,
            "severity": result.severity,
            "details": result.details,
        }, indent=2))


def cmd_archetype(args: argparse.Namespace) -> None:
    """Analyze text for archetype dysfunction."""
    from aif.archetypes import ArchetypeAnalyzer

    text = _get_text(args)
    analyzer = ArchetypeAnalyzer()
    result = analyzer.analyze(text)

    print(f"\n{'='*50}")
    print(f"  Archetype Analysis")
    print(f"{'='*50}")
    print(f"  Unhealthy Father: {result.unhealthy_father:.4f}")
    print(f"  Unhealthy Mother: {result.unhealthy_mother:.4f}")
    print(f"  Unhealthy Child:  {result.unhealthy_child:.4f}")
    print(f"  Healthy patterns: {result.healthy_score:.4f}")
    print(f"  Dominant dysf.:   {result.dominant_dysfunction or 'none'}")
    print(f"  Dissociation risk:{result.dissociation_risk:.4f}")

    if args.json:
        print(json.dumps({
            "unhealthy_father": result.unhealthy_father,
            "unhealthy_mother": result.unhealthy_mother,
            "unhealthy_child": result.unhealthy_child,
            "healthy_score": result.healthy_score,
            "dominant_dysfunction": result.dominant_dysfunction,
            "dissociation_risk": result.dissociation_risk,
        }, indent=2))


def cmd_scan(args: argparse.Namespace) -> None:
    """Full scan: ATBM + archetype analysis."""
    from aif.atbm import ATBMPipeline
    from aif.archetypes import ArchetypeAnalyzer

    text = _get_text(args)

    pipeline = ATBMPipeline()
    atbm = pipeline.process(text)

    analyzer = ArchetypeAnalyzer()
    arch = analyzer.analyze(text)

    print(f"\n{'='*50}")
    print(f"  Full AIF Scan")
    print(f"{'='*50}")
    print(f"\n  --- Tribal Bias (ATBM) ---")
    print(f"  BLD flagged:     {atbm.bld_flagged}")
    print(f"  Father score:    {atbm.father_score:.4f}")
    print(f"  ETI:             {atbm.eti:.4f}")
    print(f"  Tribal detected: {atbm.tribal_detected}")
    print(f"  Severity:        {atbm.severity}")

    print(f"\n  --- Archetype Dysfunction ---")
    print(f"  Unhealthy Father: {arch.unhealthy_father:.4f}")
    print(f"  Unhealthy Mother: {arch.unhealthy_mother:.4f}")
    print(f"  Unhealthy Child:  {arch.unhealthy_child:.4f}")
    print(f"  Healthy patterns: {arch.healthy_score:.4f}")
    print(f"  Dominant dysf.:   {arch.dominant_dysfunction or 'none'}")

    # Combined assessment
    issues = []
    if atbm.tribal_detected:
        issues.append(f"tribal bias ({atbm.severity})")
    if arch.dominant_dysfunction:
        issues.append(f"unhealthy {arch.dominant_dysfunction} archetype")
    if arch.dissociation_risk > 0.2:
        issues.append(f"dissociation risk ({arch.dissociation_risk:.2f})")

    print(f"\n  --- Assessment ---")
    if issues:
        print(f"  Issues found: {'; '.join(issues)}")
    else:
        print(f"  No significant issues detected.")

    if args.json:
        print(json.dumps({
            "atbm": {
                "bld_flagged": atbm.bld_flagged,
                "father_score": atbm.father_score,
                "eti": atbm.eti,
                "tribal_detected": atbm.tribal_detected,
                "severity": atbm.severity,
            },
            "archetype": {
                "unhealthy_father": arch.unhealthy_father,
                "unhealthy_mother": arch.unhealthy_mother,
                "unhealthy_child": arch.unhealthy_child,
                "healthy_score": arch.healthy_score,
                "dominant_dysfunction": arch.dominant_dysfunction,
                "dissociation_risk": arch.dissociation_risk,
            },
            "issues": issues,
        }, indent=2))


def _get_text(args: argparse.Namespace) -> str:
    """Extract text from args — either direct text, --file, or stdin."""
    if hasattr(args, "file") and args.file:
        with open(args.file) as f:
            return f.read()
    if hasattr(args, "text") and args.text:
        return " ".join(args.text)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Error: provide text as argument, --file path, or pipe via stdin")
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aif",
        description="Adaptive Intelligence Framework — tools for substrate-independent intelligence analysis",
    )
    sub = parser.add_subparsers(dest="command")

    # UAI
    p_uai = sub.add_parser("uai", help="Run UAI substrate simulation")
    p_uai.add_argument("--preset", default="all",
                       help="Preset: human_elder, plant, mycelial, crystal, ai_system, all")
    p_uai.add_argument("--steps", type=int, default=50, help="Simulation steps")

    # Delta-X
    p_dx = sub.add_parser("deltax", help="Run ΔX consistency test demo")
    p_dx.add_argument("--probes", action="store_true", help="Generate verification probes")

    # ATBM
    p_atbm = sub.add_parser("atbm", help="Analyze text for tribal bias")
    p_atbm.add_argument("text", nargs="*", help="Text to analyze")
    p_atbm.add_argument("--file", help="Read text from file")
    p_atbm.add_argument("--details", action="store_true", help="Show detailed scores")
    p_atbm.add_argument("--json", action="store_true", help="Output as JSON")

    # Archetype
    p_arch = sub.add_parser("archetype", help="Analyze text for archetype dysfunction")
    p_arch.add_argument("text", nargs="*", help="Text to analyze")
    p_arch.add_argument("--file", help="Read text from file")
    p_arch.add_argument("--json", action="store_true", help="Output as JSON")

    # Full scan
    p_scan = sub.add_parser("scan", help="Full analysis: ATBM + archetype")
    p_scan.add_argument("text", nargs="*", help="Text to analyze")
    p_scan.add_argument("--file", help="Read text from file")
    p_scan.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    commands = {
        "uai": cmd_uai,
        "deltax": cmd_deltax,
        "atbm": cmd_atbm,
        "archetype": cmd_archetype,
        "scan": cmd_scan,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
