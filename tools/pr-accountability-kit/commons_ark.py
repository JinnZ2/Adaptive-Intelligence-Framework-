#!/usr/bin/env python3
"""commons_ark.py -- the exit. CC0. stdlib only. no network. offline-first.

When maintainers walk, the comprehension knowledge must travel WITH them,
not die on the platform. The ark is a single portable file a small community
(coop, distributed repo, offline cache) can carry, verify, fork, and re-seed.

It bundles, into one self-verifying JSON capsule:
  - SUBSTRATE.txt   what the project is actually coupled to (4 layers)
  - every ATTESTATION the project accumulated (the why, the load paths)
  - KNOWLEDGE.md    free-text ledger (relational knowledge, failure records)
  - a SHA-256 manifest so the capsule is tamper-evident with no server

No platform required to read it. No corporation owns it. Public domain.

  python3 commons_ark.py build  <project_dir> -o ark.json
  python3 commons_ark.py verify ark.json
  python3 commons_ark.py show   ark.json
  python3 commons_ark.py --selftest
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import sys

import attest

VERSION = "1"
LAYERS = ["physical", "knowledge", "feedback", "constraint"]


def sha(obj):
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def parse_substrate(text):
    layers = {k: [] for k in LAYERS}
    key = None
    for raw in text.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- "):
            if key:
                layers[key].append(s[2:].strip())
            continue
        if line.endswith(":") and line[:-1].strip() in LAYERS:
            key = line[:-1].strip()
    return layers


def read(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return default


def collect_attestations(project_dir):
    """Every *.attestation.txt plus a top-level ATTESTATION.txt if present."""
    out = []
    paths = sorted(glob.glob(os.path.join(project_dir, "**", "*ATTESTATION*.txt"),
                             recursive=True))
    for p in paths:
        att = attest.parse(read(p))
        out.append({"source": os.path.relpath(p, project_dir),
                    "fields": att.as_dict(),
                    "complete": att.complete()})
    return out


def build(project_dir):
    substrate = parse_substrate(read(os.path.join(project_dir, "SUBSTRATE.txt")))
    attestations = [a for a in collect_attestations(project_dir)
                    if any(a["fields"].values())]
    ledger = read(os.path.join(project_dir, "KNOWLEDGE.md"))
    sections = {
        "substrate": substrate,
        "attestations": attestations,
        "ledger": ledger,
    }
    manifest = {k: sha(v) for k, v in sections.items()}
    ark = {
        "ark_version": VERSION,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "project": os.path.basename(os.path.abspath(project_dir)),
        "sections": sections,
        "manifest": manifest,
        "manifest_root": sha(manifest),
    }
    return ark


def verify(ark):
    problems = []
    for k, expected in ark.get("manifest", {}).items():
        actual = sha(ark["sections"].get(k))
        if actual != expected:
            problems.append({"section": k, "expected": expected, "actual": actual})
    if sha(ark.get("manifest", {})) != ark.get("manifest_root"):
        problems.append({"section": "manifest_root", "status": "mismatch"})
    return {"intact": not problems, "problems": problems}


def show(ark):
    s = ark["sections"]
    sub = s["substrate"]
    return {
        "project": ark["project"],
        "created_utc": ark["created_utc"],
        "manifest_root": ark["manifest_root"][:16] + "...",
        "n_attestations": len(s["attestations"]),
        "n_complete": sum(1 for a in s["attestations"] if a["complete"]),
        "substrate_layers_declared": {k: len(sub.get(k, [])) for k in LAYERS},
        "ledger_chars": len(s["ledger"]),
        "integrity": verify(ark)["intact"],
    }


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "SUBSTRATE.txt"), "w") as f:
        f.write("physical:\n- server farm, hydro grid, river cooling\n"
                "knowledge:\n- diverse open source\n- ecological records\n"
                "feedback:\n- power bill, water table, real failures\n"
                "constraint:\n- knowledge it cannot self-generate\n")
    with open(os.path.join(d, "core.ATTESTATION.txt"), "w") as f:
        f.write("constraint_changed: cap read 30s\nload_path_before: unbounded\n"
                "load_path_after: TimeoutError\nedge_cases_touched:\n- empty\n"
                "out_of_scope:\n- auth\nfailure_mode: deadlock at 0\n")
    with open(os.path.join(d, "KNOWLEDGE.md"), "w") as f:
        f.write("why the timeout exists: a slow peer once hung the whole node.\n")
    ark = build(d)
    assert verify(ark)["intact"] is True
    info = show(ark)
    assert info["n_attestations"] == 1 and info["n_complete"] == 1, info
    assert info["substrate_layers_declared"]["knowledge"] == 2, info
    # tamper detection
    ark["sections"]["ledger"] += " (forged line)"
    assert verify(ark)["intact"] is False
    print("selftest: OK")
    print(json.dumps(info, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", nargs="?", choices=["build", "verify", "show"])
    p.add_argument("target", nargs="?")
    p.add_argument("-o", "--out", default="ark.json")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest or not a.cmd:
        return selftest()
    if a.cmd == "build":
        ark = build(a.target or ".")
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(ark, f, indent=2, ensure_ascii=False)
        print(json.dumps(show(ark), indent=2))
        return 0
    with open(a.target, "r", encoding="utf-8") as f:
        ark = json.load(f)
    print(json.dumps(verify(ark) if a.cmd == "verify" else show(ark), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
