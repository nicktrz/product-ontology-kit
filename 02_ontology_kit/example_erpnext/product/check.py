#!/usr/bin/env python3
"""Check the product ontology against the code. Exit code 1 on any error, 0 when everything resolves.

Usage: python3 product/check.py            (run from the repository root; product/ sits in the root)

What it checks, for any system:
  - every YAML file parses; every `id` is unique across product/*.yaml;
  - references between records: values under reference keys (entities, from, to, leads_to, affects,
    applies_to, ...) are ids of existing records;
  - code references: every path-like token (`dir/file.ext`, `dir/file.ext#Symbol`, `dir/file.ext:42`)
    points to an existing file, the symbol occurs in it, the line exists;
    dotted names under `fn`, `delegates_to`, `calls`, `method`, `handler` resolve to a file and a symbol;
  - requirements (records with `rule`) have the fields an agent and a check need;
  - INDEX.md matches the records (rebuild with index.py);
  - size: each YAML file stays under `max_lines` (300 by default);
  - no secrets: keys, tokens, passwords, private keys.
System-specific checks (fields exist in a schema, translations exist, settings match) go into
`check_local.py` next to this file: it defines `def check(ont, error, warn)` and is called at the end.

Settings live in optional product/check_config.yaml, see the kit's template for the keys.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ontology import Ontology, strings  # noqa: E402

REF_KEYS = ["entities", "entity", "from", "to", "leads_to", "opens_from", "depends_on", "affects",
            "applies_to", "carried_to", "value_from", "screen", "screens", "events", "copy", "links", "tables"]
SECRET = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"\bsk-[A-Za-z0-9_-]{20,}", "API key (sk-...)"),
    (r"\bgh[pousr]_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"\bxox[abprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"(?i)(?:\b|_)(password|passwd|secret|api_?key|token)\s*[:=]\s*['\"]?[^\s'\"]{8,}", "credential value"),
    (r"\b[a-z][\w+.-]*://[^\s:/@]+:[^\s@/]+@", "password in a URL"),
    (r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.", "JWT"),
]


def main():
    ont = Ontology(HERE)
    cfg = ont.config
    errors, warnings = list(ont.errors), list(ont.duplicates)
    error, warn = errors.append, warnings.append
    if not ont.files:
        print(f"no product/*.yaml next to {HERE}"); sys.exit(1)

    # ---- references between records
    ref_keys = set(cfg.get("ref_keys", REF_KEYS)) | set(cfg.get("extra_ref_keys", []))
    external = set(map(str, cfg.get("external_ids", [])))
    links = 0
    for rid, rec in ont.records.items():
        for key in ref_keys & set(rec):
            vals = rec[key]
            if isinstance(vals, dict):
                vals = list(vals.values())
            if not isinstance(vals, list):
                vals = [vals]
            flat = []
            for v in vals:
                flat += v if isinstance(v, list) else [v]
            for v in flat:
                if v is None or not isinstance(v, (str, int)):
                    continue
                v = str(v)
                links += 1
                if v not in ont.records and v not in external:
                    error(f"{ont.loc(rid)}: `{key}` -> `{v}`: no record with this id "
                          f"(if it lives outside the ontology, list it in external_ids in check_config.yaml)")

    # ---- code references
    ignore = tuple(cfg.get("ignore_paths", []))
    dotted_keys = set(cfg.get("dotted_keys", ["fn", "delegates_to", "calls", "method", "handler"]))
    refs = 0
    for fname, data in ont.files.items():
        lines = (HERE / fname).read_text(encoding="utf-8").splitlines()
        def where(token):
            for n, l in enumerate(lines, 1):
                if token in l:
                    return f"{fname}:{n}"
            return fname
        no_path = set(cfg.get("no_path_keys", ["forbidden_values", "forbidden_in_change", "required_near_field", "migration"]))
        for key, s in strings(data):
            if key in no_path:
                continue
            if key in dotted_keys and re.fullmatch(r"[A-Za-z_][\w]*(\.[\w]+)+", s.strip()):
                refs += 1
                p, sym = ont.resolve_dotted(s.strip())
                if not p:
                    error(f"{where(s.strip())}: `{s}` does not resolve to a file under {ont.root.name}/")
                elif sym and not ont.symbol_in(p, sym):
                    error(f"{where(s.strip())}: `{sym}` not found in {p}")
                continue
            for path, sym in ont.code_refs(s):
                if path.startswith(ignore) or path.startswith("product/"):
                    continue
                refs += 1
                m = re.search(re.escape(path) + r":(\d+)", s)
                found = ont.find_path(path)
                target = ont.root / found if found else None
                if not found:
                    error(f"{where(path)}: `{path}` does not exist")
                elif sym and target.is_file() and not ont.symbol_in(found, sym):
                    error(f"{where(path + '#' + sym)}: `{sym}` not found in {found}")
                elif m and target.is_file() and int(m.group(1)) > len(target.read_text(encoding="utf-8", errors="replace").splitlines()):
                    error(f"{where(path + ':' + m.group(1))}: {found} has no line {m.group(1)}")

    # ---- requirements
    flows = ont.flows()
    reqs = {i: r for i, r in ont.requirements().items() if str(r.get("status", "")).lower() != "proposed"}
    for rid, r in reqs.items():
        if r.get("kind") not in ("product", "technical"):
            error(f"{ont.loc(rid)}: requirement needs `kind: product` or `kind: technical`")
        if "exceptions" not in r:
            error(f"{ont.loc(rid)}: requirement needs `exceptions` (an empty list when there are none)")
        if not r.get("applies_to"):
            warn(f"{ont.loc(rid)}: requirement has no `applies_to`: the check cannot see where it acts")
        ent = r.get("entity")
        if ent and flows:
            into = sorted(f for f, fr in flows.items() if str(fr.get("to")) == str(ent))
            listed = set(map(str, r.get("applies_to") or [])) | set(map(str, r.get("exceptions") or []))
            missing = [f for f in into if f not in listed]
            if missing:
                error(f"{ont.loc(rid)}: `{ent}` is also created by {', '.join(missing)}: add each to applies_to or exceptions")
        if r.get("open_questions"):
            warn(f"{ont.loc(rid)}: {len(r['open_questions'])} open question(s): an agent stops on them")

    # ---- size and secrets
    max_lines = int(cfg.get("max_lines", 300))
    exempt = set(cfg.get("size_exempt", ["fields.yaml"]))
    for f in sorted(HERE.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        n = len(text.splitlines())
        if n > max_lines and f.name not in exempt:
            error(f"{f.name}: {n} lines, limit {max_lines}: move details to the code and keep a reference")
        for pat, what in SECRET:
            for m in re.finditer(pat, text):
                line = text[:m.start()].count("\n") + 1
                error(f"{f.name}:{line}: looks like a secret ({what}); keep secrets out of the ontology")

    # ---- index is up to date
    idx = HERE / "INDEX.md"
    if (HERE / "index.py").exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("index", HERE / "index.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        if not idx.exists() or idx.read_text(encoding="utf-8") != mod.build():
            error("INDEX.md is missing or stale: run `python3 product/index.py`")

    # ---- system-specific checks
    local = HERE / "check_local.py"
    if local.exists():
        ns = {"__file__": str(local), "__name__": "check_local"}
        exec(compile(local.read_text(encoding="utf-8"), str(local), "exec"), ns)
        ns["check"](ont, error, warn)

    for w in warnings:
        print("note:", w)
    for e in errors:
        print("FAIL", e)
    if errors:
        print(f"{len(errors)} error(s)")
        sys.exit(1)
    print(f"OK: {len(ont.records)} records in {len(ont.files)} files, {links} links between records, "
          f"{refs} code references, {len(reqs)} requirement(s)")


if __name__ == "__main__":
    main()
