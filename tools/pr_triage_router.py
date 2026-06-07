# pr_triage_router.py — CC0, stdlib only, phone-buildable
# Consumes the Attestation json emitted by pr_comprehension_gate.py.
# Ranks a queue by STRUCTURAL accountability. No quality verdict.
# No LLM. Every signal deterministic + countable. Routes attention only.

from dataclasses import dataclass, field, asdict
import json

ATTEST_FIELDS = ["constraint_changed","load_path_before","load_path_after",
                 "edge_cases_touched","out_of_scope","failure_mode"]

@dataclass
class PR:
    id: str
    attestation: dict          # from the gate
    files_touched: list        # actual diff
    test_files: list           # subset of diff that are tests
    linked_issue: bool = False
    signed: bool = False

@dataclass
class Signals:                  # raw, transparent — maintainer can sort any column
    completeness: float = 0.0   # frac of attestation fields filled
    scope_violations: int = 0   # out_of_scope items actually touched
    edge_test_gap: int = 0      # edge cases claimed but no test in diff
    size: int = 0               # files touched (smaller = cheaper review)
    provenance: int = 0         # linked_issue + signed (0..2)

def measure(pr: PR) -> Signals:
    a = pr.attestation
    filled = sum(1 for k in ATTEST_FIELDS if a.get(k))
    touched = set(pr.files_touched)
    oos = set(a.get("out_of_scope", []))
    edges_claimed = len(a.get("edge_cases_touched", []))
    return Signals(
        completeness   = round(filled / len(ATTEST_FIELDS), 2),
        scope_violations = len(oos & touched),
        edge_test_gap  = edges_claimed if (edges_claimed and not pr.test_files) else 0,
        size           = len(touched),
        provenance     = int(pr.linked_issue) + int(pr.signed),
    )

def route(s: Signals) -> dict:
    # transparent composite. high = review first (cheap, accountable).
    # NOT a verdict — just attention ordering. weights visible, tunable.
    score = ( s.completeness * 3
            - s.scope_violations * 2
            - (1 if s.edge_test_gap else 0)
            + s.provenance
            - (s.size / 20) )            # large diffs cost more review flux
    if s.completeness < 1.0:
        bucket = "BOUNCE"                # gap → route back to source (human sends)
    elif s.scope_violations or s.edge_test_gap:
        bucket = "INSPECT"               # coherent enough to read, flagged structurally
    else:
        bucket = "READY"                 # cheap, accountable → top of queue
    return {"bucket": bucket, "score": round(score, 2)}

def triage(prs: list) -> list:
    rows = []
    for pr in prs:
        s = measure(pr)
        r = route(s)
        rows.append({"id": pr.id, **r, "signals": asdict(s)})
    order = {"READY": 0, "INSPECT": 1, "BOUNCE": 2}
    return sorted(rows, key=lambda x: (order[x["bucket"]], -x["score"]))

if __name__ == "__main__":
    q = [
        PR("#412", {"constraint_changed":"timeout cap","load_path_before":"x",
            "load_path_after":"y","edge_cases_touched":["empty input"],
            "out_of_scope":["auth"],"failure_mode":"deadlock if 0"},
           files_touched=["net.py","tests/test_net.py"], test_files=["tests/test_net.py"],
           linked_issue=True, signed=True),
        PR("#418", {"constraint_changed":"refactor"},   # gap → bounces, never costs queue
           files_touched=["a.py","b.py","auth.py","c.py","d.py"], test_files=[]),
        PR("#420", {"constraint_changed":"cache key","load_path_before":"p",
            "load_path_after":"q","edge_cases_touched":["collision"],
            "out_of_scope":["auth"],"failure_mode":"stale read"},
           files_touched=["cache.py","auth.py"], test_files=[],   # touched out-of-scope + no test
           linked_issue=True),
    ]
    print(json.dumps(triage(q), indent=2))
