#!/usr/bin/env python3
"""Write product/INDEX.md: one line per YAML file with the ids of its records and their line numbers.

Usage: python3 product/index.py      (run after every change of product/*.yaml; check.py reports a stale index)
An agent reads INDEX.md first and then fetches single records with `python3 product/find.py <id or word>`.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ontology import record_lines  # noqa: E402


def build():
    out = ["# Ontology index", "",
           "One line per file: record ids with line numbers. Get a record with `python3 product/find.py <id or word>`.", ""]
    for f in sorted(HERE.glob("*.yaml")):
        if f.name == "check_config.yaml":
            continue
        ids = record_lines(f)
        if ids:
            out.append(f"- `{f.name}`: " + ", ".join(f"{i}:{n}" for i, n in ids.items()))
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    (HERE / "INDEX.md").write_text(build(), encoding="utf-8")
    print(f"wrote {HERE / 'INDEX.md'}")
