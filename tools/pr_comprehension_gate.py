# pr_comprehension_gate.py  — CC0, stdlib only, phone-buildable
# Runs on the CONTRIBUTOR. Emits a structured attestation the
# maintainer reads spatially in one glance — no file-by-file sim.
# Structural descriptors only. No quality verdict, no moral valence.

from dataclasses import dataclass, asdict
import json, subprocess

@dataclass
class Attestation:
    constraint_changed: str   # what physical/logical invariant moves
    load_path_before: str     # where flow went before
    load_path_after: str      # where flow goes now
    edge_cases_touched: list  # cases whose behavior CHANGES
    out_of_scope: list        # what this deliberately does NOT touch
    failure_mode: str         # how it breaks if assumptions wrong

def diff_scope():             # claimed vs actual — descriptor only
    files = subprocess.run(["git","diff","--name-only","main"],
                           capture_output=True,text=True).stdout.split()
    return {"files_touched": files, "n": len(files)}

def gate(a: Attestation):
    blanks = [k for k,v in asdict(a).items() if not v]
    return {
        "ready": not blanks,
        "missing": blanks,            # empty field = comprehension gap
        "scope": diff_scope(),
        "attestation": asdict(a),
    }

# maintainer reads ONE json block:
#   missing==[]  → contributor can articulate the change → review worth it
#   missing!=[]  → routed back to source, never costs the queue
if __name__ == "__main__":
    print(json.dumps(gate(Attestation(
        constraint_changed="", load_path_before="", load_path_after="",
        edge_cases_touched=[], out_of_scope=[], failure_mode="",
    )), indent=2))
