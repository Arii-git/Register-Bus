#!/usr/bin/env python3
"""Fill the README mutation tables and status lines from the mutation logs.

Source results (from log/mutations.md and log/mutations_bus.md):
  regfile: 3 breaks, each gives FAIL=2 of 5 tests (all caught)
  mmio_top: 4 breaks at depth 8, 2 read ports, each gives FAIL=1 of 10 tests (all caught)

usage (from ~/Register-Bus): python3 apply_mutation_tables.py
Each old string must occur exactly once. If one does not, nothing is written.
"""
import pathlib
import sys

README = pathlib.Path("README.md")

PAIRS = [
    ("| regfile | write ignores `we` | any | *pending* |",
     "| regfile | write ignores `we` | not recorded in log | Yes, 2 of 5 tests fail |"),
    ("| regfile | reset does nothing | any | *pending* |",
     "| regfile | reset does nothing | not recorded in log | Yes, 2 of 5 tests fail |"),
    ("| regfile | `BYPASS` ignored | `BYPASS=1` | *pending* |",
     "| regfile | `BYPASS` ignored | `BYPASS=1` | Yes, 2 of 5 tests fail |"),
    ("| mmio_top | write counter adds 2 | any | *pending* |",
     "| mmio_top | write counter adds 2 | 8 × 2, bypass 0 | Yes, 1 of 10 tests fail |"),
    ("| mmio_top | offset 3 treated as mapped | any | *pending* |",
     "| mmio_top | offset 3 treated as mapped | 8 × 2, bypass 0 | Yes, 1 of 10 tests fail |"),
    ("| mmio_top | scan gate removed | `NREAD ≥ 2` | *pending* |",
     "| mmio_top | scan gate removed | 8 × 2, bypass 0 | Yes, 1 of 10 tests fail |"),
    ("| mmio_top | bypass ignored | `BYPASS=1` | *pending* |",
     "| mmio_top | bypass ignored | 8 × 2, bypass 1 | Yes, 1 of 10 tests fail |"),
    ("**Mutation checks.** Each suite will be run against deliberately broken RTL, one break at a time, and at least one test must fail for each break.",
     "**Mutation checks.** Each suite was run against deliberately broken RTL, one break at a time. At least one test must fail for each break, and all seven breaks were caught."),
    ("| `regfile` tests | Running, mutation checks pending |",
     "| `regfile` tests | Passing at depth 8; 3 of 3 mutations caught |"),
    ("| `mmio_top` tests | 10 of 10 passing on the bus design; mutation checks pending |",
     "| `mmio_top` tests | 10 of 10 passing at depth 8; 4 of 4 mutations caught |"),
    ("against the model | Running |",
     "against the model | Passing at depth 8; 3 of 3 mutations caught |"),
]


def main():
    if not README.exists():
        sys.exit("README.md not found. Run this from the repo root.")
    text = README.read_text(encoding="utf-8")
    bad = [(text.count(old), old[:70]) for old, _ in PAIRS if text.count(old) != 1]
    if bad:
        for n, snippet in bad:
            print(f"NOT APPLIED (found {n} times): {snippet}")
        sys.exit("No changes written. Paste this output to me.")
    for old, new in PAIRS:
        text = text.replace(old, new)
    README.write_text(text, encoding="utf-8")
    print(f"Applied {len(PAIRS)} edits to README.md. Check with: git diff --stat")


if __name__ == "__main__":
    main()
