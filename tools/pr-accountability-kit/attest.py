"""attest.py -- shared attestation model + parser. CC0. stdlib only.

An Attestation is proof-of-comprehension supplied by the PR author.
It is structural, not a quality claim. Six fields, all required:

  constraint_changed   what invariant / behavior moves
  load_path_before     where flow went before
  load_path_after      where flow goes now
  edge_cases_touched   cases whose behavior CHANGES   (list)
  out_of_scope         what this deliberately does NOT touch  (list)
  failure_mode         how it breaks if assumptions are wrong

File format (ATTESTATION.txt) is phone-friendly key/value text:

  constraint_changed: cap socket read at 30s
  load_path_before: unbounded wait on slow peer
  load_path_after: raises TimeoutError at cap
  edge_cases_touched:
  - empty payload
  - peer disconnect mid-read
  out_of_scope:
  - auth
  - retry logic
  failure_mode: deadlock if cap == 0
"""

from dataclasses import dataclass, field, asdict

SCALAR = ["constraint_changed", "load_path_before", "load_path_after",
          "failure_mode"]
LIST = ["edge_cases_touched", "out_of_scope"]
FIELDS = SCALAR + LIST


@dataclass
class Attestation:
    constraint_changed: str = ""
    load_path_before: str = ""
    load_path_after: str = ""
    edge_cases_touched: list = field(default_factory=list)
    out_of_scope: list = field(default_factory=list)
    failure_mode: str = ""

    def missing(self):
        m = [k for k in SCALAR if not getattr(self, k).strip()]
        m += [k for k in LIST if not getattr(self, k)]
        return m

    def complete(self):
        return not self.missing()

    def as_dict(self):
        return asdict(self)


def parse(text):
    """Parse ATTESTATION.txt text into an Attestation. No deps."""
    data = {k: "" for k in SCALAR}
    data.update({k: [] for k in LIST})
    key = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and key in LIST:
            data[key].append(line.lstrip()[2:].strip())
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            if k in FIELDS:
                key = k
                if k in SCALAR:
                    data[k] = v.strip()
                # for LIST keys, items follow on subsequent "- " lines
                continue
        # continuation of a scalar value
        if key in SCALAR and data[key]:
            data[key] += " " + line.strip()
    return Attestation(**data)


def from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return parse(f.read())
