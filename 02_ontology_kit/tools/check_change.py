#!/usr/bin/env python3
"""Check a change (an agent's or anyone's) against the requirements written in the ontology.

Usage:  python3 product/check_change.py --base <commit before the change> [requirement_id ...]
        or BASE_REF=<commit> python3 product/check_change.py [requirement_id ...]
        Run from the repository root. Without ids every record under `requirements:` is checked.
        The change = `git diff BASE_REF` (committed and uncommitted) plus new untracked files; product/ is skipped.
Exit code 1 when anything is violated, 0 when the change satisfies the requirements.

Each requirement record (product/decisions.yaml, list `requirements:`) may set:
  field                 name of the field in code; a list when layers name it differently: [contractNo, contract_no]
  entity                id of the record where the rule acts (its definition file: `definition`, `schema`, `json` or `code`)
  carried_to            entity ids that must also define the field
  required_near_field   regexes that must occur next to the field in the entity definition (e.g. the "mandatory" flag)
  applies_to            flow ids (records with `from` and `to`) that create the entity and must fill the field
  exceptions            flow ids the rule does not cover; every other flow into the entity is a violation
  shown_in              files that must mention the field after the change (reports, print forms, screens)
  forbidden_values      literals that must not appear in added lines (stubs like "N/A")
  forbidden_in_change   regexes that must not appear in changed hunks that mention the field (weakening the rule)
  migration             regex of a migration file path; such a file mentioning the field must be in the change
  open_questions        while not empty, a change that touches the field cannot pass: the product owner decides first
  status: proposed      the requirement is not approved yet and is skipped
Violations are tagged [product] (return to the product owner) or [technical] (the author fixes).
A path whose value is missing is tagged by the requirement's `kind`: for `kind: product` the product owner
decides where the value comes from. The change may not edit or delete approved requirements.
Files under `change_ignore` (default: work/) are not part of the change.
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ontology import Ontology  # noqa: E402

NEAR = 15  # lines around a field occurrence that count as "next to the field"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def change(root, base, skip, ignore=()):
    """[(path, hunk_text, added_lines)] for the diff against base plus untracked files."""
    out = []
    excl = [f":(exclude){p.rstrip('/')}/**" for p in [skip, *ignore]]
    diff = git(root, "diff", "--unified=5", base, "--", ".", *excl)
    path, hunk, added = None, [], []
    def flush():
        if path and hunk:
            out.append((path, "\n".join(hunk), list(added)))
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            flush(); path, hunk, added = None, [], []
        elif line.startswith("+++ "):
            path = None if line[4:] == "/dev/null" else line[6:]
        elif line.startswith("@@"):
            flush(); hunk, added = [], []
        elif path is not None and line[:1] in "+- ":
            hunk.append(line[1:])
            if line.startswith("+"):
                added.append(line[1:])
    flush()
    for p in git(root, "ls-files", "--others", "--exclude-standard").splitlines():
        if p.startswith(tuple(x.rstrip("/") + "/" for x in [skip, *ignore])):
            continue
        try:
            text = (root / p).read_text(encoding="utf-8", errors="replace")
        except (IsADirectoryError, FileNotFoundError):
            continue
        out.append((p, text, text.splitlines()))
    return out


def text_of(root, path):
    try:
        return (root / path).read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, IsADirectoryError):
        return ""


def main(ids):
    ont = Ontology(HERE)
    root = ont.root
    ap = argparse.ArgumentParser(description="Check a change against product/ requirements")
    ap.add_argument("--base", default=os.environ.get("BASE_REF"))
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args(ids)
    base, ids = a.base, a.ids
    if not base:
        print("give the commit before the change: python3 product/check_change.py --base main"); sys.exit(2)
    try:
        git(root, "rev-parse", "--verify", base + "^{commit}")
    except subprocess.CalledProcessError:
        print(f"BASE_REF `{base}` is not a commit in {root}"); sys.exit(2)
    # compare with the point where the branch left base, not with the current tip of base
    base_name, base = base, git(root, "merge-base", base, "HEAD").strip() or base
    def at_base(path):
        try:
            return git(root, "show", f"{base}:{path}")
        except subprocess.CalledProcessError:
            return ""
    reqs = ont.requirements()
    proposed = [i for i, r in reqs.items() if str(r.get("status", "")).lower() == "proposed"]
    for i in proposed:
        print(f"note: {i} has status: proposed and is skipped until the product owner approves it")
    reqs = {i: r for i, r in reqs.items() if i not in proposed}
    if ids:
        missing = [i for i in ids if i not in reqs]
        if missing:
            print("no requirement with id:", ", ".join(missing)); sys.exit(2)
        reqs = {i: reqs[i] for i in ids}
    if not reqs:
        print("no records under `requirements:` in product/*.yaml"); sys.exit(2)

    hunks = change(root, base, ont.dir.name, ont.config.get("change_ignore", ["work/"]))
    def_keys = ont.config.get("definition_keys", ["definition", "schema", "json", "model", "code"])
    def definition(eid):
        rec = ont.records.get(str(eid))
        if not rec:
            return None
        for k in def_keys:
            v = rec.get(k)
            for s in (v if isinstance(v, list) else [v]):
                if isinstance(s, str):
                    for p, _ in ont.code_refs(s):
                        found = ont.find_path(p)
                        if found and (root / found).is_file():
                            return found
        return None

    # requirements as they were before the change: the change may not rewrite them
    old_reqs = {}
    for fname in ont.files:
        try:
            import tempfile
            from ontology import load_yaml
            txt = at_base(f"{ont.dir.relative_to(root)}/{fname}")
            if txt:
                with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as t:
                    t.write(txt)
                data = load_yaml(t.name)
                os.unlink(t.name)
                if isinstance(data, dict) and isinstance(data.get("requirements"), list):
                    old_reqs.update({str(x["id"]): x for x in data["requirements"] if isinstance(x, dict) and "id" in x})
        except Exception:
            pass

    violations = []
    for rid in sorted(set(old_reqs) - set(ont.requirements())):
        violations.append((rid, "product", "requirement removed", "the change deletes this requirement: the product owner approves it"))
    for rid, r in reqs.items():
        def v(kind, rule, msg):
            violations.append((rid, kind, rule, msg))
        if rid in old_reqs and old_reqs[rid] != r:
            changed = sorted(k for k in set(old_reqs[rid]) | set(r) if old_reqs[rid].get(k) != r.get(k))
            v("product", "requirement changed", f"the change edits {', '.join(changed)}: the product owner approves it")
        names = r.get("field")
        names = [str(x) for x in (names if isinstance(names, list) else [names] if names else [])]
        field = names[0] if names else None
        word = re.compile(r"(?<![\w$])(?:" + "|".join(map(re.escape, names)) + r")(?![\w$])") if names else None
        ent = str(r.get("entity")) if r.get("entity") else None
        path_kind = "product" if r.get("kind") == "product" else "technical"
        relevant = bool(word) and any(word.search(h) for _, h, _ in hunks)

        if r.get("open_questions"):
            if relevant:
                for q in r["open_questions"]:
                    v("product", "open question", f"decide before merge: {q}")
            else:
                print(f"note: {rid} has open questions; this change does not touch `{field}`")
        if not field or not ent:
            v("technical", "requirement", "set `field` and `entity` so the change can be checked")
            continue

        # the field is defined where the rule says
        for e in [ent] + [str(x) for x in r.get("carried_to") or []]:
            d = definition(e)
            if not d:
                v("technical", "definition", f"`{e}`: no definition file in the ontology record (keys {', '.join(def_keys)})")
            elif not word.search(text_of(root, d)):
                v("technical", "field", f"`{e}`: `{field}` is not in {d}")
        d = definition(ent)
        if d:
            lines = text_of(root, d).splitlines()
            spots = [i for i, l in enumerate(lines) if word.search(l)]
            for pat in (r.get("required_near_field") or []) if spots else []:
                if not any(re.search(pat, "\n".join(lines[max(0, i - NEAR):i + NEAR + 1])) for i in spots):
                    v("product", "weakened", f"`{pat}` is not next to `{field}` in {d}: the rule is not in force")

        # every path that creates the entity is covered
        flows = ont.flows()
        listed = {str(x) for x in r.get("applies_to") or []}
        excepted = {str(x) for x in r.get("exceptions") or []}
        for fid, fr in flows.items():
            if str(fr.get("to")) == ent and fid not in listed | excepted:
                v("product", "path", f"`{fid}` also creates `{ent}`; the requirement says nothing about it (add to applies_to or exceptions)")
        for fid in sorted(listed):
            fr = flows.get(fid)
            if not fr:
                v("technical", "path", f"applies_to `{fid}`: no flow with this id")
                continue
            src = str(fr.get("from"))
            src_def = definition(src)
            if src_def and word.search(text_of(root, src_def)):
                continue  # the source document has the field and carries it
            code = ont.code_of(fr)
            if not any(word.search(ont.body_with_callees(p, s) if s else text_of(root, p)) for p, s in code):
                where = ", ".join(f"{p}#{s}" if s else p for p, s in code) or "no code files in the flow record"
                v(path_kind, "path", f"`{fid}` creates `{ent}` from `{src}`, which has no `{field}`, "
                                       f"and the flow code does not set it ({where})")

        # where the field must show
        for p in r.get("shown_in") or []:
            found = ont.find_path(p)
            if not found:
                v("technical", "shown_in", f"{p} does not exist")
            elif not word.search(text_of(root, found)):
                v("technical", "shown_in", f"`{field}` is not in {found}")

        # stubs and weakening in the change
        for lit in r.get("forbidden_values") or []:
            for path, hunk, added in hunks:
                if not word.search(hunk):
                    continue
                for line in added:
                    m = re.search(r"""["']""" + re.escape(str(lit)) + r"""["']""", line, re.I)
                    if m:
                        v("product", "stub", f"{path}: adds the value {m.group(0)}: `{line.strip()[:100]}`")
        for pat in r.get("forbidden_in_change") or []:
            for path, hunk, added in hunks:
                if word.search(hunk):
                    for line in added:
                        if re.search(pat, line):
                            v("product", "weakened", f"{path}: `{line.strip()[:100]}` next to `{field}`")
        new_field = d and not word.search(at_base(d))  # old records exist only for a field new to base
        if r.get("migration") and new_field:
            mig = [p for p, h, _ in hunks if re.search(r["migration"], p) and word.search(text_of(root, p))]
            if not mig:
                v("technical", "migration", f"no file matching `{r['migration']}` that mentions `{field}` in the change")

    violations = list(dict.fromkeys(violations))
    for rid, kind, rule, msg in violations:
        print(f"FAIL [{kind}] {rid} · {rule}: {msg}")
    if violations:
        n_p = sum(1 for x in violations if x[1] == "product")
        print(f"{len(violations)} violation(s): {n_p} for the product owner, {len(violations) - n_p} technical")
        sys.exit(1)
    print(f"OK: the change satisfies {len(reqs)} requirement(s) against {base_name}")


if __name__ == "__main__":
    main(sys.argv[1:])
