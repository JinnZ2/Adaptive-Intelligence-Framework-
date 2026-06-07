# pr-accountability-kit

CC0. stdlib only. no deps. no network. no LLM. phone-buildable.
A drop-in for open-source maintainers drowning in AI-generated PRs.

## the problem, as flux

```
flux_in   = PRs            [agents collapsed the cost of producing one to ~0]
flux_proc = human review   [fixed at comprehension speed -- cannot scale]
buffer    = "you had to understand code to write it"   <- agents deleted this

flux_in >> flux_proc  ->  queue grows unbounded
  queue^ -> latency^ -> real contributors leave -> reviewers fewer
         -> throughput v -> queue^   (self-reinforcing collapse)
```

The expensive case is not obvious garbage (rejects at a glance).
It is plausible-wrong: forces full mental simulation per diff.

## the fix: re-impose the deleted buffer at the GATE, not the queue

Route the review cost back to the source. Demand proof-of-comprehension,
not proof-of-work. If the author can name what they changed, review is
worth it. If they cannot, the PR never costs the maintainer's attention.

```
author -> ATTESTATION.txt (6 structural fields) -> gate.py
   |
   gate: complete? scope coherent vs diff?
   |-- no  -> BOUNCE  (back to author, queue untouched)
   |-- yes -> enters queue
                 |
                 triage.py ranks scarce attention, deterministic only:
                   READY    complete + coherent + cheap   -> review first
                   INSPECT  coherent, flagged structurally -> review, eyes open
                   BOUNCE   gap                            -> back to author
```

## why no AI in the path

```
AI-reviews-AI (CodeRabbit / Sashiko style) raises the review ceiling
  -> invites more flux (Jevons), and the same statistical substrate that
     writes plausible-wrong is blindest to plausible-wrong when judging.
     it relocates the trust problem into the ranker. coating layer.

this kit measures only countable things:
  attestation completeness, declared-scope vs actual-diff, edge/test gap,
  provenance flags, diff size. no field reads meaning. rejection stays human,
  so accountability stays with a person.
```

## files

```
attest.py         shared parser + Attestation model
gate.py           contributor / CI gate     -> JSON + exit code
triage.py         maintainer queue router   -> ranked buckets
ATTESTATION.txt   template the author copies and fills
attestation.yml   example GitHub Actions hook
```

## use it

```
# contributor (or CI), in the PR branch:
cp ATTESTATION.txt then fill all six fields
python3 gate.py                 # exit 0 = ready, 1 = back to you

# maintainer, on a queue you assembled (gh dump / manual / cron):
python3 triage.py queue.json    # ranked READY / INSPECT / BOUNCE

# verify offline, no repo needed:
python3 gate.py --selftest
python3 triage.py --selftest
```

## queue.json shape (one record per PR)

```json
[{"id":"#412",
  "attestation":{"constraint_changed":"...","load_path_before":"...",
    "load_path_after":"...","edge_cases_touched":["..."],
    "out_of_scope":["..."],"failure_mode":"..."},
  "files_touched":["net.py","tests/test_net.py"],
  "test_files":["tests/test_net.py"],
  "linked_issue":true,"signed":true}]
```

triage weights are visible and tunable in `WEIGHTS` – they order
attention, they are not a verdict. Fork freely. Public domain.
