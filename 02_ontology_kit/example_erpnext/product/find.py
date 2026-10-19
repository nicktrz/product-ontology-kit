#!/usr/bin/env python3
"""Print only the ontology records that match the given words or ids.

Usage: python3 product/find.py WORD [WORD ...]
A record is one list item (an `- id:` or `- {id: ...}` block) in a product/*.yaml file.
A record matches when it contains every given word (case-insensitive). At most 12 records are printed.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
ITEM = re.compile(r'^(\s*)- (\{\s*)?id:')

def nodes(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        m = ITEM.match(lines[i])
        if not m:
            i += 1
            continue
        indent = len(m.group(1))
        j = i + 1
        while j < len(lines):
            l = lines[j]
            if l.strip() and (len(l) - len(l.lstrip())) <= indent:
                break
            j += 1
        yield i + 1, "\n".join(lines[i:j]).rstrip()
        i = j

def main(words):
    if not words:
        print(__doc__); return
    words = [w.lower() for w in words]
    hits = []
    for f in sorted(HERE.glob("*.yaml")):
        for line, text in nodes(f):
            low = text.lower()
            if all(w in low for w in words):
                hits.append((f.name, line, text))
    for name, line, text in hits[:12]:
        print(f"## product/{name}:{line}\n{text}\n")
    if len(hits) > 12:
        print(f"... {len(hits) - 12} more records; add a word to narrow the search")
    if not hits:
        print("no records; try another word or search the code")

if __name__ == "__main__":
    main(sys.argv[1:])
