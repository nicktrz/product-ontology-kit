"""Shared helpers for the product ontology tools: load product/*.yaml, collect records, resolve code references.

No dependencies: uses PyYAML when it is installed, otherwise a small parser for the YAML subset
the ontology uses (block mappings and lists, [flow, lists], {flow: maps}, quoted strings, | and > blocks).
"""
import re
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:  # pragma: no cover
    _yaml = None

# ---------------------------------------------------------------- YAML subset parser

def _strip_comment(line):
    out, q = [], None
    for i, ch in enumerate(line):
        if q:
            if ch == q:
                q = None
        elif ch in "\"'" and (i == 0 or line[i - 1] in " \t[{,:"):
            q = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(s):
    s = s.strip()
    if not s:
        return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        body = s[1:-1]
        return body.replace("''", "'") if s[0] == "'" else body.encode().decode("unicode_escape") if "\\" in body else body
    if s in ("~", "null", "Null", "NULL"):
        return None
    if s in ("true", "True", "TRUE"):
        return True
    if s in ("false", "False", "FALSE"):
        return False
    if re.fullmatch(r"[-+]?\d+", s):
        return int(s)
    if re.fullmatch(r"[-+]?\d*\.\d+", s):
        return float(s)
    return s


class _Flow:
    def __init__(self, s):
        self.s, self.i = s, 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t\n":
            self.i += 1

    def value(self):
        self.ws()
        c = self.s[self.i] if self.i < len(self.s) else ""
        if c == "[":
            self.i += 1
            out = []
            while True:
                self.ws()
                if self.s[self.i] == "]":
                    self.i += 1
                    return out
                out.append(self.item())
                self.ws()
                if self.s[self.i] == ",":
                    self.i += 1
        if c == "{":
            self.i += 1
            out = {}
            while True:
                self.ws()
                if self.s[self.i] == "}":
                    self.i += 1
                    return out
                k = self.plain(stop=":,}")
                self.ws()
                v = None
                if self.s[self.i] == ":":
                    self.i += 1
                    v = self.value()
                out[_scalar(k)] = v
                self.ws()
                if self.s[self.i] == ",":
                    self.i += 1
        return self.item()

    def item(self):
        self.ws()
        c = self.s[self.i]
        if c in "[{":
            return self.value()
        if c in "\"'":
            j = self.i + 1
            while self.s[j] != c or (c == "'" and self.s[j:j + 2] == "''"):
                j += 2 if self.s[j:j + 2] == "''" else 1
            tok, self.i = self.s[self.i:j + 1], j + 1
            return _scalar(tok)
        return _scalar(self.plain(stop=",]}"))

    def plain(self, stop):
        self.ws()
        if self.s[self.i] in "\"'":
            q = self.s[self.i]
            j = self.s.index(q, self.i + 1)
            tok, self.i = self.s[self.i:j + 1], j + 1
            return tok
        j = self.i
        while j < len(self.s):
            ch = self.s[j]
            if ch in stop and (ch != ":" or j + 1 >= len(self.s) or self.s[j + 1] in " \t"):
                break
            j += 1
        tok, self.i = self.s[self.i:j].strip(), j
        return tok


def _inline(s):
    s = s.strip()
    if s[:1] in "[{":
        return _Flow(s).value()
    return _scalar(s)


def _balanced(s):
    depth, q = 0, None
    for ch in s:
        if q:
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
    return depth <= 0


_KEY = re.compile(r"""^("[^"]*"|'[^']*'|[^\s\-\[\]{}#&*!|>'"%@`][^:]*?|-[^\s][^:]*?)\s*:(?:\s+(.*))?$""")


def _lines(text):
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip() in ("---", "..."):
            continue
        s = _strip_comment(raw)
        if s.strip():
            out.append([len(s) - len(s.lstrip(" ")), s.strip(), n, raw])
    return out


def _parse(L, i, ind):
    if L[i][1].startswith("- ") or L[i][1] == "-":
        out = []
        while i < len(L) and L[i][0] == ind and (L[i][1].startswith("- ") or L[i][1] == "-"):
            rest = L[i][1][1:].strip()
            if not rest:
                v, i = _parse(L, i + 1, L[i + 1][0])
            elif _KEY.match(rest) and not rest.startswith(("[", "{", '"', "'")):
                L[i] = [ind + 2, rest, L[i][2], L[i][3]]
                v, i = _parse(L, i, ind + 2)
            else:
                v, i = _value(L, i, ind, rest)
            out.append(v)
        return out, i
    out = {}
    while i < len(L) and L[i][0] == ind and not L[i][1].startswith("- "):
        m = _KEY.match(L[i][1])
        if not m:
            raise ValueError(f"line {L[i][2]}: cannot parse `{L[i][3].strip()}`")
        key, rest = _scalar(m.group(1)), (m.group(2) or "").strip()
        if not rest:
            if i + 1 < len(L) and (L[i + 1][0] > ind or (L[i + 1][0] == ind and L[i + 1][1].startswith("- "))):
                v, i = _parse(L, i + 1, L[i + 1][0])
            else:
                v, i = None, i + 1
        else:
            v, i = _value(L, i, ind, rest)
        out[key] = v
    return out, i


def _value(L, i, ind, rest):
    if rest in ("|", ">", "|-", ">-", "|+", ">+"):
        j, parts = i + 1, []
        while j < len(L) and L[j][0] > ind:
            parts.append(L[j][3].strip())
            j += 1
        return ("\n" if rest[0] == "|" else " ").join(parts), j
    j = i + 1
    if rest[:1] in "[{":
        while not _balanced(rest) and j < len(L):
            rest += " " + L[j][1]
            j += 1
        try:
            return _inline(rest), j
        except IndexError:
            raise ValueError(f"line {L[i][2]}: unclosed [ or {{ in `{L[i][3].strip()}`") from None
    while j < len(L) and L[j][0] > ind and not (rest[:1] in "\"'"):
        rest += " " + L[j][1]
        j += 1
    if rest[:1] not in "\"'" and re.search(r":(\s|$)", rest):
        raise ValueError(f"line {L[i][2]}: `: ` inside a value; put the value in quotes")
    return _inline(rest), j


def load_yaml(path):
    text = Path(path).read_text(encoding="utf-8")
    if _yaml is not None:
        return _yaml.safe_load(text)
    L = _lines(text)
    return _parse(L, 0, L[0][0])[0] if L else None

# ---------------------------------------------------------------- records

ITEM = re.compile(r"^(\s*)- (\{\s*)?id:\s*['\"]?([\w.-]+)")


def record_lines(path):
    """id -> line number of `- id:` items in a YAML file (text scan, independent of the parser)."""
    out = {}
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        m = ITEM.match(line)
        if m:
            out.setdefault(m.group(3), n)
    return out


def walk_records(node, trail=()):
    """Yield (trail, record) for every mapping with an `id` key, at any depth."""
    if isinstance(node, dict):
        if "id" in node and isinstance(node["id"], (str, int)):
            yield trail, node
        for k, v in node.items():
            yield from walk_records(v, trail + (k,))
    elif isinstance(node, list):
        for v in node:
            yield from walk_records(v, trail)


def strings(node, key=None):
    """Yield (key, string) for every string scalar under node; key is the nearest mapping key."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v, key)
    elif isinstance(node, str):
        yield key, node


class Ontology:
    def __init__(self, product_dir):
        self.dir = Path(product_dir).resolve()
        self.root = self.dir.parent
        self.config = {}
        cfg = self.dir / "check_config.yaml"
        if cfg.exists():
            self.config = load_yaml(cfg) or {}
        self.files, self.records, self.where, self.errors, self.duplicates = {}, {}, {}, [], []
        self.path_roots = [r.rstrip("/") + "/" if r else "" for r in self.config.get("path_roots", [""])]
        for f in sorted(self.dir.glob("*.yaml")):
            if f.name == "check_config.yaml":
                continue
            try:
                data = load_yaml(f)
            except Exception as e:  # report and go on
                self.errors.append(f"{f.name}: YAML does not parse: {e}")
                continue
            self.files[f.name] = data
            lines = record_lines(f)
            for _, rec in walk_records(data):
                rid = str(rec["id"])
                if rid in self.records:
                    self.duplicates.append(f"{f.name}:{lines.get(rid, '?')}: id `{rid}` is also used in {self.where[rid][0]}; links to it are ambiguous")
                    continue
                self.records[rid] = rec
                self.where[rid] = (f.name, lines.get(rid, "?"))

    def loc(self, rid):
        f, n = self.where.get(rid, ("?", "?"))
        return f"{f}:{n}"

    def requirements(self):
        """Records listed under a top-level `requirements:` key (decisions.yaml by convention)."""
        out = {}
        for data in self.files.values():
            if isinstance(data, dict) and isinstance(data.get("requirements"), list):
                for r in data["requirements"]:
                    if isinstance(r, dict) and "id" in r:
                        out[str(r["id"])] = r
        return out

    def flows(self):
        """Records that create one thing from another: they have `from` and `to`."""
        return {rid: r for rid, r in self.records.items() if "from" in r and "to" in r}

    # ------------------------------------------------------------ code references

    PATH = re.compile(r"(?<![\w/.:-])((?:[\w.-]+/)+[\w.-]*?\.[A-Za-z0-9]{1,6})(?:#([\w.$]+))?(?::(\d+))?(?![\w/-]|\.[A-Za-z0-9])")
    BARE_PATH = re.compile(r"^(?:[\w.-]+/)+[\w.-]+/?$")

    def code_refs(self, value):
        """Path-like tokens in a string: (path, symbol or None)."""
        if "{" in value or "*" in value or "<" in value or "://" in value:
            value = re.sub(r"\S*[{*<]\S*|\S*://\S*", " ", value)
        refs = [(m.group(1), m.group(2)) for m in self.PATH.finditer(value)]
        v = value.strip()
        if not refs and self.BARE_PATH.match(v) and all(len(p) >= 2 for p in v.strip("/").split("/")):
            refs.append((v.rstrip("/"), None))
        return refs

    def find_path(self, path):
        """Path relative to the repository root, trying each of `path_roots` (for app-relative paths)."""
        for r in self.path_roots:
            if (self.root / (r + path)).exists():
                return r + path
        return None

    def resolve_dotted(self, dotted):
        """`pkg.module.func` -> (path, symbol) when pkg/module.<ext> exists under the repository root."""
        parts = dotted.split(".")
        exts = self.config.get("dotted_extensions", [".py", ".js", ".ts", ".java", ".kt", ".cs", ".go", ".rb", ".php"])
        for k in range(len(parts) - 1, 0, -1):
            base = "/".join(parts[:k])
            for root in self.path_roots:
                for ext in exts:
                    if (self.root / (root + base + ext)).is_file():
                        return root + base + ext, ".".join(parts[k:])
                if (self.root / (root + base) / "__init__.py").is_file():
                    return root + base + "/__init__.py", ".".join(parts[k:])
        return None, None

    def symbol_in(self, path, symbol):
        text = (self.root / path).read_text(encoding="utf-8", errors="replace")
        if path.endswith((".md", ".markdown")):  # a heading anchor
            slug = lambda h: re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")
            return any(slug(m.group(1)) == symbol.lower() for m in re.finditer(r"^#+\s+(.+)$", text, re.M))
        return all(re.search(r"(?<![\w$])" + re.escape(p) + r"(?![\w$])", text) for p in symbol.split(".") if p)

    def body_of(self, path, symbol):
        """Text of the function or class `symbol` in path; the whole file when it is not found."""
        text = (self.root / path).read_text(encoding="utf-8", errors="replace")
        name = symbol.split(".")[-1]
        lines = text.splitlines()
        head = re.compile(r"^(\s*)(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:def|function|func|class|const|let|var|public|private|protected|static|fun)\b[^\n]*?(?<![\w$])" + re.escape(name) + r"(?![\w$])")
        for i, l in enumerate(lines):
            m = head.match(l)
            if not m:
                continue
            ind, out = len(m.group(1)), [l]
            for l2 in lines[i + 1:]:
                s = l2.strip()
                if s and len(l2) - len(l2.lstrip()) <= ind:
                    if s[0] in ")}]":
                        out.append(l2)
                    break
                out.append(l2)
            return "\n".join(out)
        return text

    def body_with_callees(self, path, symbol, depth=2):
        """Body of `symbol` plus bodies of functions from the same file that it calls, `depth` levels deep."""
        text = (self.root / path).read_text(encoding="utf-8", errors="replace")
        seen, parts, todo = set(), [], [(symbol.split(".")[-1], 0)]
        while todo:
            name, level = todo.pop()
            if name in seen:
                continue
            seen.add(name)
            body = self.body_of(path, name)
            if body == text and level > 0:
                continue  # not defined in this file
            parts.append(body)
            if body == text or level >= depth:
                continue
            for callee in set(re.findall(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(", body)):
                todo.append((callee, level + 1))
        return "\n".join(parts)

    def code_of(self, rec):
        """(path, symbol or None) a record points to, for flows: `fn` and the like with their symbol."""
        out = []
        dotted_keys = set(self.config.get("dotted_keys", ["fn", "delegates_to", "calls", "method", "handler"]))
        for key, s in strings(rec):
            for p, sym in self.code_refs(s):
                p = self.find_path(p)
                if p and (self.root / p).is_file():
                    out.append((p, sym if key in dotted_keys else None))
            if key in dotted_keys and re.fullmatch(r"[\w]+(\.[\w]+)+", s):
                p, sym = self.resolve_dotted(s)
                if p:
                    out.append((p, sym))
        return list(dict.fromkeys(out))

    def code_files_of(self, rec):
        """Files a record points to: path tokens in its strings and resolvable dotted names under dotted keys."""
        files = []
        dotted_keys = set(self.config.get("dotted_keys", ["fn", "delegates_to", "calls", "method", "handler"]))
        for key, s in strings(rec):
            for p, _ in self.code_refs(s):
                p = self.find_path(p)
                if p and (self.root / p).is_file():
                    files.append(p)
            if key in dotted_keys and re.fullmatch(r"[\w]+(\.[\w]+)+", s):
                p, _ = self.resolve_dotted(s)
                if p:
                    files.append(p)
        return list(dict.fromkeys(files))
