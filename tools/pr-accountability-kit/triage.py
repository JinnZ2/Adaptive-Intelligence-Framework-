#!/usr/bin/env python3
"""triage.py -- maintainer queue router. CC0. stdlib only. no network. no LLM.

Routes scarce maintainer ATTENTION. Does not judge code quality.
Every signal is deterministic and countable -- no model reads meaning,
so there is no coating layer and no accountability hole. Never auto-rejects;
rejection stays human. Three buckets:

  READY    complete attestation, scope coherent, cheap   -> review first
  INSPECT  coherent enough to read, flagged structurally  -> review, eyes open
  BOUNCE   attestation gap                                -> back to author

Input: a queue JSON file. One record per PR:
  {"id":"#412",
   "attestation": {...six fields...},   # or "attestation_text": "raw text"
   "files_touched": ["net.py","tests/test_net.py"],
   "test_files": ["tests/test_net.py"],
   "linked_issue": true, "signed": true}

Build the queue however you like (gh CLI dump, manual, a cron). The router
is decoupled from any platform on purpose.

Usage:
  python3 triage.py queue.json
  python3 triage.py --selftest
"""

import argparse
import json
import sys

import attest

WEIGHTS = {              # visible + tunable. not a verdict, an ordering.
    "completeness": 3.0,
    "scope_violation": -2.0,
    "edge_test_gap": -1.0,
    "provenance": 1.0,
    "size_divisor": 20.0,
}


def to_att(rec):
    if "attestation_text" in rec:
        return attest.parse(rec["attestation_text"])
    d = rec.get("attestation", {}) or {}
    return attest.Attestation(**{k: d.get(k, attest.Attestation().__dict__[k])
                                 for k in attest.FIELDS})


def measure(rec):
    att = to_att(rec)
    filled = sum(1 for k in attest.FIELDS
                 if (getattr(att, k) if k in attest.SCALAR else att.__dict__[k]))
    touched = set(rec.get("files_touched", []))
    oos = {t.strip().lower() for t in att.out_of_scope if t.strip()}
    viol = sum(1 for t in oos for f in touched if t in f.lower())
    edges = len(att.edge_cases_touched)
    edge_gap = edges if (edges and not rec.get("test_files")) else 0
    prov = int(bool(rec.get("linked_issue"))) + int(bool(rec.get("signed")))
    return {
        "completeness": round(filled / len(attest.FIELDS), 2),
        "scope_violations": viol,
        "edge_test_gap": edge_gap,
        "size": len(touched),
        "provenance": prov,
    }


def route(s):
    score = (s["completeness"] * WEIGHTS["completeness"]
             + s["scope_violations"] * WEIGHTS["scope_violation"]
             + (WEIGHTS["edge_test_gap"] if s["edge_test_gap"] else 0)
             + s["provenance"] * WEIGHTS["provenance"]
             - s["size"] / WEIGHTS["size_divisor"])
    if s["completeness"] < 1.0:
        bucket = "BOUNCE"
    elif s["scope_violations"] or s["edge_test_gap"]:
        bucket = "INSPECT"
    else:
        bucket = "READY"
    return bucket, round(score, 2)


def triage(queue):
    rows = []
    for rec in queue:
        s = measure(rec)
        bucket, score = route(s)
        rows.append({"id": rec.get("id", "?"), "bucket": bucket,
                     "score": score, "signals": s})
    order = {"READY": 0, "INSPECT": 1, "BOUNCE": 2}
    rows.sort(key=lambda r: (order[r["bucket"]], -r["score"]))
    return rows


def selftest():
    q = [
        {"id": "#412",
         "attestation": {"constraint_changed": "cap", "load_path_before": "x",
                         "load_path_after": "y", "edge_cases_touched": ["empty"],
                         "out_of_scope": ["auth"], "failure_mode": "deadlock"},
         "files_touched": ["net.py", "tests/test_net.py"],
         "test_files": ["tests/test_net.py"], "linked_issue": True, "signed": True},
        {"id": "#418",
         "attestation": {"constraint_changed": "refactor"},
         "files_touched": ["a.py", "b.py", "auth.py", "c.py", "d.py"],
         "test_files": []},
        {"id": "#420",
         "attestation": {"constraint_changed": "cache key", "load_path_before": "p",
                         "load_path_after": "q", "edge_cases_touched": ["collision"],
                         "out_of_scope": ["auth"], "failure_mode": "stale"},
         "files_touched": ["cache.py", "auth.py"], "test_files": [],
         "linked_issue": True},
    ]
    rows = triage(q)
    buckets = {r["id"]: r["bucket"] for r in rows}
    assert buckets["#412"] == "READY", rows
    assert buckets["#418"] == "BOUNCE", rows
    assert buckets["#420"] == "INSPECT", rows
    assert rows[0]["id"] == "#412", rows   # cheapest accountable first
    print("selftest: OK")
    print(json.dumps(rows, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("queue", nargs="?", help="queue JSON file")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest or not a.queue:
        return selftest()
    with open(a.queue, "r", encoding="utf-8") as f:
        queue = json.load(f)
    print(json.dumps(triage(queue), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
