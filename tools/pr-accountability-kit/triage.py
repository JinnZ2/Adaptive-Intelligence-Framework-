#!/usr/bin/env python3
"""triage.py -- maintainer queue router. CC0. stdlib only. no network.

Consumes a queue.json assembled by the maintainer (one record per PR,
each with an attestation dict from gate.py). Ranks by structural
accountability. No quality verdict. No LLM. All signals deterministic.

Buckets:
  READY    complete + no scope violation + edge cases tested  -> review first
  INSPECT  complete but flagged structurally                  -> review, eyes open
  BOUNCE   gap in attestation                                 -> back to author

Usage:
  python3 triage.py queue.json
  cat queue.json | python3 triage.py
  python3 triage.py --selftest
"""

import argparse
import json
import sys

import attest

# Weights are visible and tunable. They order attention, not a verdict.
# Fork freely. Public domain.
WEIGHTS = {
    "completeness":     3.0,   # fraction of attestation fields filled
    "scope_violation": -2.0,   # per file that violates out_of_scope
    "edge_test_gap":   -1.0,   # flat: edges claimed but no test in diff
    "provenance":       1.0,   # per provenance flag (linked_issue, signed)
    "size_per_file":   -0.05,  # larger diffs cost more review flux
}


def _att_from_dict(d):
    kwargs = {k: d.get(k, "") for k in attest.SCALAR}
    kwargs.update({k: list(d.get(k) or []) for k in attest.LIST})
    return attest.Attestation(**kwargs)


def scope_hits(att, files):
    """Files that violate an out_of_scope declaration. Substring match on path."""
    hits = []
    for token in att.out_of_scope:
        t = token.strip().lower()
        if not t:
            continue
        for f in files:
            if t in f.lower():
                hits.append({"declared_out_of_scope": token, "touched": f})
    return hits


def measure(pr):
    att    = _att_from_dict(pr.get("attestation", {}))
    files  = pr.get("files_touched", [])
    tests  = pr.get("test_files", [])
    miss   = att.missing()
    edges  = len(att.edge_cases_touched)
    hits   = scope_hits(att, files)
    return {
        "completeness":     round((len(attest.FIELDS) - len(miss)) / len(attest.FIELDS), 2),
        "missing":          miss,
        "scope_violations": len(hits),
        "scope_hits":       hits,
        "edge_test_gap":    edges if (edges and not tests) else 0,
        "size":             len(files),
        "provenance":       int(bool(pr.get("linked_issue"))) +
                            int(bool(pr.get("signed"))),
    }


def compute_score(m):
    return round(
        m["completeness"]     * WEIGHTS["completeness"]
      + m["scope_violations"] * WEIGHTS["scope_violation"]
      + (1 if m["edge_test_gap"] else 0) * WEIGHTS["edge_test_gap"]
      + m["provenance"]       * WEIGHTS["provenance"]
      + m["size"]             * WEIGHTS["size_per_file"],
        2,
    )


def route(m):
    if m["completeness"] < 1.0:
        return "BOUNCE"
    if m["scope_violations"] or m["edge_test_gap"]:
        return "INSPECT"
    return "READY"


def triage(prs):
    rows = []
    for pr in prs:
        m  = measure(pr)
        bk = route(m)
        sc = compute_score(m)
        rows.append({
            "id":      pr["id"],
            "bucket":  bk,
            "score":   sc,
            "signals": {k: m[k] for k in
                        ("completeness", "scope_violations", "edge_test_gap",
                         "size", "provenance")},
            "detail":  {k: m[k] for k in ("missing", "scope_hits")},
        })
    order = {"READY": 0, "INSPECT": 1, "BOUNCE": 2}
    return sorted(rows, key=lambda x: (order[x["bucket"]], -x["score"]))


_TEST_QUEUE = [
    {"id": "#412",
     "attestation": {
         "constraint_changed": "timeout cap",
         "load_path_before": "unbounded wait on slow peer",
         "load_path_after": "raises TimeoutError at cap",
         "edge_cases_touched": ["empty payload", "mid-read disconnect"],
         "out_of_scope": ["auth"],
         "failure_mode": "deadlock if cap == 0"},
     "files_touched": ["net.py", "tests/test_net.py"],
     "test_files":    ["tests/test_net.py"],
     "linked_issue": True, "signed": True},
    {"id": "#418",
     "attestation": {"constraint_changed": "refactor"},
     "files_touched": ["a.py", "b.py", "auth.py", "c.py", "d.py"],
     "test_files": []},
    {"id": "#420",
     "attestation": {
         "constraint_changed": "cache key",
         "load_path_before": "hash(user_id)",
         "load_path_after": "hash(user_id + shard)",
         "edge_cases_touched": ["collision"],
         "out_of_scope": ["auth"],
         "failure_mode": "stale read on shard migration"},
     "files_touched": ["cache.py", "auth.py"],
     "test_files": [], "linked_issue": True},
]


def selftest():
    result = triage(_TEST_QUEUE)
    buckets = {r["id"]: r["bucket"] for r in result}
    assert buckets["#412"] == "READY",   f"#412 → {buckets['#412']}"
    assert buckets["#418"] == "BOUNCE",  f"#418 → {buckets['#418']}"
    assert buckets["#420"] == "INSPECT", f"#420 → {buckets['#420']}"
    assert result[0]["id"] == "#412",    "READY should sort first"
    print("selftest: OK")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("queue", nargs="?", help="path to queue.json (default: stdin)")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        return selftest()
    if a.queue:
        with open(a.queue) as f:
            prs = json.load(f)
    else:
        prs = json.load(sys.stdin)
    print(json.dumps(triage(prs), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
