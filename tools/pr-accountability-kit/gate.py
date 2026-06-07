#!/usr/bin/env python3
"""gate.py -- contributor / CI gate. CC0. stdlib only. no network.

Runs on the PR author (or in CI). Re-imposes the proof-of-comprehension
buffer that hand-writing code used to force and that agents removed.

  - parses ATTESTATION.txt
  - checks all six fields are filled
  - checks declared out_of_scope was not actually touched by the diff
  - emits one JSON block a maintainer reads in a single glance

Exit 0 = ready to enter review queue. Exit 1 = routed back to author.
Cost lands on the source, not the maintainer's attention.

Usage:
  python3 gate.py                         # uses ATTESTATION.txt, git diff vs main
  python3 gate.py --file path.txt --base main
  python3 gate.py --selftest              # offline self-check, no git, no net
"""

import argparse
import json
import subprocess
import sys

import attest


def diff_files(base):
    """Files changed vs base branch. Empty list if git unavailable."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", base + "...HEAD"],
            capture_output=True, text=True, timeout=15,
        )
        files = [f for f in out.stdout.split() if f]
        if not files:  # fall back to staged + working changes
            out = subprocess.run(
                ["git", "diff", "--name-only", base],
                capture_output=True, text=True, timeout=15,
            )
            files = [f for f in out.stdout.split() if f]
        return files
    except Exception:
        return []


def scope_violations(att, files):
    """out_of_scope tokens that appear in a touched path. descriptor only."""
    hits = []
    for token in att.out_of_scope:
        t = token.strip().lower()
        if not t:
            continue
        for f in files:
            if t in f.lower():
                hits.append({"declared_out_of_scope": token, "touched": f})
    return hits


def evaluate(att, files):
    miss = att.missing()
    viol = scope_violations(att, files)
    ready = (not miss) and (not viol)
    return {
        "ready": ready,
        "missing_fields": miss,           # gap = comprehension not demonstrated
        "scope_violations": viol,         # touched what it said it wouldn't
        "files_touched": files,
        "n_files": len(files),
        "attestation": att.as_dict(),
    }


def selftest():
    good = attest.parse(
        "constraint_changed: cap read at 30s\n"
        "load_path_before: unbounded wait\n"
        "load_path_after: raises TimeoutError\n"
        "edge_cases_touched:\n- empty payload\n- mid-read disconnect\n"
        "out_of_scope:\n- auth\n- retry\n"
        "failure_mode: deadlock if cap==0\n"
    )
    r1 = evaluate(good, ["net.py", "tests/test_net.py"])
    assert r1["ready"] is True, r1
    r2 = evaluate(good, ["net.py", "auth.py"])        # touched out-of-scope
    assert r2["ready"] is False and r2["scope_violations"], r2
    bad = attest.parse("constraint_changed: refactor\n")
    r3 = evaluate(bad, ["a.py"])
    assert r3["ready"] is False and r3["missing_fields"], r3
    print("selftest: OK")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default="ATTESTATION.txt")
    p.add_argument("--base", default="main")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        return selftest()
    try:
        att = attest.from_file(a.file)
    except FileNotFoundError:
        print(json.dumps({"ready": False,
                          "error": "no ATTESTATION.txt -- copy the template"},
                         indent=2))
        return 1
    result = evaluate(att, diff_files(a.base))
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
