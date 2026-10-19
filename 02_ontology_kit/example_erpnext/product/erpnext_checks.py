#!/usr/bin/env python3
"""ERPNext-specific checks of the product ontology in product/ (called from check_local.py).

Run from anywhere: python3 product/check.py
Exit code 0 when every reference resolves, 1 otherwise. Uses only the standard library
(PyYAML is used when installed; otherwise a small parser for the YAML subset used here).
"""

import ast
import glob
import json
import os
import re
import sys
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
YAML_FILES = ["domain", "screens", "features", "copy", "analytics", "code_map", "decisions"]
MAX_YAML_LINES = 300
MAX_README_LINES = 120

errors: list[str] = []
notes: list[str] = []


def err(where: str, msg: str) -> None:
	errors.append(f"{where}: {msg}")


# ---------------------------------------------------------------- YAML subset parser


def _strip_comment(line: str) -> str:
	quote = None
	for i, ch in enumerate(line):
		if quote:
			if ch == "\\" and quote == '"':
				continue
			if ch == quote:
				quote = None
		elif ch in "\"'":
			quote = ch
		elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
			return line[:i].rstrip()
	return line.rstrip()


def _scalar(text: str):
	t = text.strip()
	if t in ("null", "~", ""):
		return None
	if t == "true":
		return True
	if t == "false":
		return False
	if re.fullmatch(r"-?\d+", t):
		return int(t)
	if re.fullmatch(r"-?\d+\.\d+", t):
		return float(t)
	return t


class _Flow:
	def __init__(self, s: str):
		self.s, self.i = s, 0

	def ws(self):
		while self.i < len(self.s) and self.s[self.i] in " \t":
			self.i += 1

	def value(self, stops: str):
		self.ws()
		ch = self.s[self.i] if self.i < len(self.s) else ""
		if ch == "[":
			self.i += 1
			out = []
			while True:
				self.ws()
				if self.s[self.i] == "]":
					self.i += 1
					return out
				out.append(self.value(",]"))
				self.ws()
				if self.s[self.i] == ",":
					self.i += 1
		if ch == "{":
			self.i += 1
			out = {}
			while True:
				self.ws()
				if self.s[self.i] == "}":
					self.i += 1
					return out
				key = self.key()
				out[key] = self.value(",}")
				self.ws()
				if self.s[self.i] == ",":
					self.i += 1
		if ch in "\"'":
			return self.quoted()
		start = self.i
		while self.i < len(self.s) and self.s[self.i] not in stops:
			self.i += 1
		return _scalar(self.s[start : self.i])

	def key(self) -> str:
		self.ws()
		if self.s[self.i] in "\"'":
			k = self.quoted()
		else:
			start = self.i
			while not (self.s[self.i] == ":" and self.s[self.i + 1 : self.i + 2] in (" ", "")):
				self.i += 1
			k = self.s[start : self.i].strip()
		self.ws()
		assert self.s[self.i] == ":", f"expected ':' in {self.s!r}"
		self.i += 1
		return k

	def quoted(self) -> str:
		q = self.s[self.i]
		self.i += 1
		out = []
		while self.s[self.i] != q:
			if q == '"' and self.s[self.i] == "\\":
				self.i += 1
			out.append(self.s[self.i])
			self.i += 1
		self.i += 1
		return "".join(out)


def _split_key(content: str):
	"""Return (key, rest) if the line is `key: ...` / `key:`, else None."""
	if content[:1] in "[{\"'":
		if content[:1] in "\"'":
			f = _Flow(content)
			k = f.quoted()
			rest = content[f.i :].lstrip()
			if rest.startswith(":"):
				return k, rest[1:].strip()
		return None
	m = re.match(r"^([^:#\[\]{}]+?):(?:\s+(.*))?$", content)
	if not m:
		return None
	return m.group(1).strip(), (m.group(2) or "").strip()


def _inline(rest: str):
	if rest[:1] in "[{":
		return _Flow(rest).value("")
	if rest[:1] in "\"'":
		return _Flow(rest).quoted()
	return _scalar(rest)


def mini_yaml(text: str):
	lines = []
	for raw in text.splitlines():
		s = _strip_comment(raw)
		if s.strip():
			lines.append((len(s) - len(s.lstrip(" ")), s.strip()))

	def block(i, indent):
		if lines[i][1].startswith("- ") or lines[i][1] == "-":
			return seq(i, indent)
		return mapping(i, indent)

	def mapping(i, indent):
		out = {}
		while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("- "):
			kv = _split_key(lines[i][1])
			if kv is None:
				raise ValueError(f"cannot parse line: {lines[i][1]!r}")
			key, rest = kv
			i += 1
			if rest:
				out[key] = _inline(rest)
			elif i < len(lines) and (
				lines[i][0] > indent or (lines[i][0] == indent and lines[i][1].startswith("- "))
			):
				out[key], i = block(i, lines[i][0])
			else:
				out[key] = None
		return out, i

	def seq(i, indent):
		out = []
		while i < len(lines) and lines[i][0] == indent and (lines[i][1].startswith("- ") or lines[i][1] == "-"):
			item = lines[i][1][2:].strip()
			if not item:
				i += 1
				val, i = block(i, lines[i][0])
			elif _split_key(item) is not None:
				lines[i] = (indent + 2, item)
				val, i = mapping(i, indent + 2)
			else:
				val, i = _inline(item), i + 1
			out.append(val)
		return out, i

	if not lines:
		return {}
	value, _ = block(0, lines[0][0])
	return value


def load_yaml(path: str):
	text = open(path, encoding="utf-8").read()
	try:
		import yaml  # type: ignore

		return yaml.safe_load(text)
	except ImportError:
		return mini_yaml(text)


# ---------------------------------------------------------------- code index


def rel(path: str) -> str:
	return os.path.join(ROOT, path)


def exists(path: str) -> bool:
	return os.path.exists(rel(path))


@lru_cache(maxsize=None)
def read(path: str) -> str:
	return open(rel(path), encoding="utf-8").read()


@lru_cache(maxsize=None)
def parse_py(path: str) -> ast.Module:
	return ast.parse(read(path), filename=path)


@lru_cache(maxsize=None)
def doctype_index() -> dict:
	index = {}
	for p in glob.glob(rel("erpnext/**/doctype/*/*.json"), recursive=True):
		folder = os.path.basename(os.path.dirname(p))
		if os.path.basename(p) != folder + ".json":
			continue
		try:
			d = json.load(open(p, encoding="utf-8"))
		except ValueError:
			continue
		if isinstance(d, dict) and d.get("doctype") == "DocType":
			index[d["name"]] = os.path.relpath(p, ROOT)
	return index


@lru_cache(maxsize=None)
def doctype_json(name: str) -> dict:
	return json.loads(read(doctype_index()[name]))


def fields_of(name: str) -> dict:
	return {f["fieldname"]: f for f in doctype_json(name).get("fields", [])}


def select_options(f: dict) -> list:
	return [o for o in (f.get("options") or "").split("\n") if o]


def top_level(tree: ast.Module, name: str):
	for node in tree.body:
		if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and node.name == name:
			return node
		if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
			return node
		if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == name:
			return node
	return None


def member(cls: ast.ClassDef, name: str):
	for node in cls.body:
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
			return node
		if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
			return node
	return None


def resolve_symbol(path: str, symbol: str):
	"""path.py + 'Name' or 'Class.method' -> AST node or None. Other files: text search."""
	if not path.endswith(".py"):
		return symbol in read(path) or None
	parts = symbol.split(".")
	node = top_level(parse_py(path), parts[0])
	for part in parts[1:]:
		node = member(node, part) if isinstance(node, ast.ClassDef) else None
	return node


def module_file(dotted: str):
	"""erpnext.a.b -> erpnext/a/b.py or erpnext/a/b/__init__.py"""
	base = dotted.replace(".", "/")
	for cand in (base + ".py", base + "/__init__.py"):
		if exists(cand):
			return cand
	return None


def resolve_dotted(dotted: str):
	"""Return (file, node) for erpnext.x.y.func, (file, None) for a module, None if unresolved."""
	mod = module_file(dotted)
	if mod:
		return mod, None
	head, _, func = dotted.rpartition(".")
	mod = module_file(head)
	if mod:
		node = top_level(parse_py(mod), func)
		if node is not None:
			return mod, node
	return None


def is_whitelisted(node) -> bool:
	return any("whitelist" in ast.unparse(d) for d in getattr(node, "decorator_list", []))


def calls_in(node) -> set:
	names = set()
	for c in ast.walk(node):
		if isinstance(c, ast.Call):
			f = c.func
			names.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None))
	return names


# ---------------------------------------------------------------- conversions


def _const(node):
	return node.value if isinstance(node, ast.Constant) else None


def _mapping_dict(fn, node):
	"""get_mapped_doc's table map: a dict literal or a local variable assigned in the function."""
	if isinstance(node, ast.Dict):
		return node
	if isinstance(node, ast.Name):
		found = None
		for n in ast.walk(fn):
			if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == node.id for t in n.targets):
				if isinstance(n.value, ast.Dict):
					found = n.value
		return found
	return None


def _imports(tree: ast.Module, fn) -> dict:
	out = {}
	for n in list(tree.body) + list(ast.walk(fn)):
		if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("erpnext"):
			for a in n.names:
				out[a.asname or a.name] = f"{n.module}.{a.name}"
	return out


def analyze_creator(path: str, fname: str, depth: int = 0, seen=None):
	"""Collect (source, target) from get_mapped_doc and targets from new_doc / get_doc(doctype=...)."""
	seen = seen if seen is not None else set()
	pairs, targets = set(), set()
	if (path, fname) in seen or depth > 3:
		return pairs, targets
	seen.add((path, fname))
	tree = parse_py(path)
	fn = top_level(tree, fname)
	if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
		return pairs, targets
	for c in ast.walk(fn):
		if not isinstance(c, ast.Call):
			continue
		name = c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", None)
		if name == "get_mapped_doc" and c.args:
			src = _const(c.args[0])
			table = _mapping_dict(fn, c.args[2]) if len(c.args) > 2 else None
			if src and table is not None:
				for k, v in zip(table.keys, table.values):
					if _const(k) == src and isinstance(v, ast.Dict):
						for k2, v2 in zip(v.keys, v.values):
							if _const(k2) == "doctype" and _const(v2):
								pairs.add((src, _const(v2)))
		elif name == "new_doc" and c.args and _const(c.args[0]):
			targets.add(_const(c.args[0]))
		elif name == "get_doc":
			for kw in c.keywords:
				if kw.arg == "doctype" and _const(kw.value):
					targets.add(_const(kw.value))
			if c.args and isinstance(c.args[0], ast.Dict):
				for k, v in zip(c.args[0].keys, c.args[0].values):
					if _const(k) == "doctype" and _const(v):
						targets.add(_const(v))
	imports = _imports(tree, fn)
	for callee in calls_in(fn) - {fname, None}:
		if top_level(tree, callee) is not None:
			p, t = analyze_creator(path, callee, depth + 1, seen)
		elif callee in imports:
			res = resolve_dotted(imports[callee])
			if not res or res[1] is None:
				continue
			p, t = analyze_creator(res[0], callee if imports[callee].endswith(callee) else imports[callee].rpartition(".")[2], depth + 1, seen)
		else:
			continue
		pairs |= p
		targets |= t
	return pairs, targets


def uses_mapped_doc(path: str, fname: str) -> bool:
	tree = parse_py(path)
	todo, seen = [fname], set()
	while todo:
		name = todo.pop()
		if name in seen:
			continue
		seen.add(name)
		fn = top_level(tree, name)
		if not isinstance(fn, ast.FunctionDef):
			continue
		called = calls_in(fn)
		if "get_mapped_doc" in called:
			return True
		todo += [c for c in called if c and top_level(tree, c) is not None]
	return False


def dotted_of(path: str, fname: str) -> str:
	return path[:-3].replace("/", ".") + "." + fname


# ---------------------------------------------------------------- generic reference checks

PATH_RE = re.compile(r"(?<![\w/])((?:erpnext|banking|\.github|semgrep)/[\w./-]*)(?:#([\w.]+))?")
ROOT_FILES = ["pyproject.toml", "crowdin.yml", "babel_extractors.csv", ".eslintrc", ".pre-commit-config.yaml", "package.json"]
DOTTED_RE = re.compile(r"^erpnext(?:\.\w+){2,}$")
SKELETON_REF_RE = re.compile(r"(?<![\w./-])(\w+)\.yaml(?:#(\w+))?")
SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd)\s*[:=]\s*['\"]?[A-Za-z0-9/+_\-]{8,}|\b[A-Fa-f0-9]{32,}\b|\bsk_[A-Za-z0-9]{16,}")


def walk_strings(obj, where=""):
	if isinstance(obj, dict):
		for k, v in obj.items():
			yield from walk_strings(v, f"{where}.{k}")
	elif isinstance(obj, list):
		for i, v in enumerate(obj):
			yield from walk_strings(v, f"{where}[{i}]")
	elif isinstance(obj, str):
		yield where, obj


def ids_in(obj) -> set:
	out = set()
	if isinstance(obj, dict):
		if isinstance(obj.get("id"), str):
			out.add(obj["id"])
		for v in obj.values():
			out |= ids_in(v)
	elif isinstance(obj, list):
		for v in obj:
			out |= ids_in(v)
	return out


def check_references(name: str, data, skel: dict) -> None:
	for where, s in walk_strings(data, name):
		for m in PATH_RE.finditer(s):
			path, symbol = m.group(1).rstrip("./"), m.group(2)
			if not exists(path):
				err(where, f"path not found: {path}")
				continue
			if symbol and os.path.isfile(rel(path)):
				symbol = symbol.rstrip(".")
				if not resolve_symbol(path, symbol):
					err(where, f"symbol {symbol!r} not found in {path}")
		for f in ROOT_FILES:
			if re.search(rf"(?<![\w/.]){re.escape(f)}\b", s) and not exists(f):
				err(where, f"root file not found: {f}")
		if DOTTED_RE.match(s) and resolve_dotted(s) is None:
			err(where, f"python reference not found: {s}")
		for m in SKELETON_REF_RE.finditer(s):
			target, anchor = m.group(1), m.group(2)
			if target in ("crowdin", "check_config"):
				continue
			if target not in skel:
				err(where, f"ontology file not found: {target}.yaml")
			elif anchor and anchor not in ids_in(skel[target]) and anchor not in (skel[target] or {}):
				err(where, f"{target}.yaml has no id or section {anchor!r}")


# ---------------------------------------------------------------- domain


def check_entities(domain: dict, copy_ids: set) -> dict:
	entities = {e["id"]: e for e in domain["entities"]}
	if len(entities) != len(domain["entities"]):
		err("domain", "duplicate entity ids")
	index = doctype_index()

	status_map = None
	node = top_level(parse_py("erpnext/controllers/status_updater.py"), "status_map")
	if node is not None:
		status_map = ast.literal_eval(node.value)

	for eid, e in entities.items():
		w = f"domain.entities.{eid}"
		dt = e.get("doctype")
		if dt not in index:
			err(w, f"doctype {dt!r} not found in any DocType JSON")
			continue
		if e.get("json") != index[dt]:
			err(w, f"json should be {index[dt]}")
		meta = doctype_json(dt)
		fields = fields_of(dt)
		kind = e.get("kind")
		if kind == "child" and not meta.get("istable"):
			err(w, "kind child but DocType is not a child table")
		if kind == "settings" and not meta.get("issingle"):
			err(w, "kind settings but DocType is not single")
		if kind == "transaction" and not meta.get("is_submittable"):
			err(w, "kind transaction but DocType is not submittable")
		if e.get("context") == "selling" and meta.get("module") != "Selling":
			err(w, f"context selling but module is {meta.get('module')}")
		if e.get("code"):
			path, _, cls = e["code"].partition("#")
			if cls and not resolve_symbol(path, cls):
				err(w, f"class {cls} not in {path}")

		for f in e.get("key_fields") or []:
			if f not in fields:
				err(w, f"key field {f!r} not in {dt}")

		for f, target in (e.get("links") or {}).items():
			fd = fields.get(f)
			if not fd:
				err(w, f"link field {f!r} not in {dt}")
				continue
			targets = target if isinstance(target, list) else [target]
			for t in targets:
				if t not in entities:
					err(w, f"link {f} -> unknown entity {t!r}")
			if isinstance(target, list):
				if fd["fieldtype"] != "Dynamic Link":
					err(w, f"{f} is {fd['fieldtype']}, expected Dynamic Link")
				ctrl = fields.get(fd.get("options"))
				if ctrl and ctrl["fieldtype"] == "Select":
					allowed = select_options(ctrl)
					for t in targets:
						if t in entities and entities[t]["doctype"] not in allowed:
							err(w, f"{f}: {entities[t]['doctype']} not in {fd['options']} options")
			elif t in entities:
				if fd["fieldtype"] != "Link" or fd.get("options") != entities[t]["doctype"]:
					err(w, f"{f} is {fd['fieldtype']}->{fd.get('options')}, expected Link->{entities[t]['doctype']}")

		for f, t in (e.get("tables") or {}).items():
			fd = fields.get(f)
			if t not in entities:
				err(w, f"table {f} -> unknown entity {t!r}")
			elif not fd or fd["fieldtype"] not in ("Table", "Table MultiSelect") or fd.get("options") != entities[t]["doctype"]:
				err(w, f"table field {f} is not Table->{entities[t]['doctype']}")

		for f, t in (e.get("row_refs") or {}).items():
			if f not in fields:
				err(w, f"row_ref field {f!r} not in {dt}")
			if t not in entities:
				err(w, f"row_ref {f} -> unknown entity {t!r}")
			elif not doctype_json(entities[t]["doctype"]).get("istable"):
				err(w, f"row_ref {f} -> {t} is not a child table")

		st = e.get("status")
		if st:
			fd = fields.get(st["field"])
			if not fd:
				err(w, f"status field {st['field']!r} missing")
			elif st.get("options") and select_options(fd) != st["options"]:
				err(w, f"status options differ from JSON: {select_options(fd)}")
			if st.get("computed_by") == "status_map":
				if dt not in (status_map or {}):
					err(w, f"status_map has no entry for {dt}")
				elif fd:
					labels = [row[0] for row in status_map[dt]]
					extra = [x for x in labels if x not in select_options(fd)]
					if extra:
						err(w, f"status_map labels not in options: {extra}")
					for label, fn in (st.get("set_outside_status_map") or {}).items():
						if label in labels:
							err(w, f"{label} is in status_map, not outside it")
						res = resolve_dotted(fn)
						if not res or res[1] is None or repr(label) not in ast.unparse(res[1]):
							err(w, f"{fn} does not set {label!r}")
			for sf, opts in (st.get("sub_status") or {}).items():
				if sf not in fields or select_options(fields[sf]) != opts:
					err(w, f"sub_status {sf} options differ from JSON")

		if e.get("lifecycle"):
			path, _, cls = e["code"].partition("#")
			cnode = resolve_symbol(path, cls)
			for event, methods in e["lifecycle"].items():
				m = member(cnode, event) if isinstance(cnode, ast.ClassDef) else None
				if m is None:
					err(w, f"{cls}.{event} not defined")
					continue
				missing = [x for x in methods if x not in calls_in(m)]
				if missing:
					err(w, f"{cls}.{event} does not call {missing}")

		for c in e.get("copy") or []:
			if c not in copy_ids:
				err(w, f"copy id {c!r} not in copy.yaml")

	# every selling doctype folder is either an entity or listed as minor
	covered = {e["json"] for e in entities.values()} | set(domain.get("minor_doctypes") or [])
	for p in sorted(glob.glob(rel(domain["module_dir"] + "/doctype/*/*.json"))):
		r = os.path.relpath(p, ROOT)
		if os.path.basename(p)[:-5] == os.path.basename(os.path.dirname(p)) and r not in covered:
			err("domain", f"selling doctype not covered: {r}")
	return entities


def check_flows(domain: dict, entities: dict) -> dict:
	flows = {f["id"]: f for f in domain["flows"]}
	index = doctype_index()

	def dt_of(ref):
		return entities[ref]["doctype"] if ref in entities else ref

	for fid, f in flows.items():
		w = f"domain.flows.{fid}"
		for side in ("from", "to"):
			if dt_of(f[side]) not in index:
				err(w, f"{side} {f[side]!r} is neither an entity id nor a doctype")
		res = resolve_dotted(f["fn"])
		if not res or not isinstance(res[1], ast.FunctionDef):
			err(w, f"function not found: {f['fn']}")
			continue
		path, node = res
		if not is_whitelisted(node):
			err(w, "function is not @frappe.whitelist()")
		if f.get("guard"):
			gdt, _, gfield = f["guard"].partition(".")
			if gfield not in fields_of(gdt):
				err(w, f"guard field {f['guard']} not found")
		if f.get("delegates_to"):
			d = resolve_dotted(f["delegates_to"])
			if not d or d[1] is None:
				err(w, f"delegate not found: {f['delegates_to']}")
			elif f["delegates_to"].rpartition(".")[2] not in calls_in(node):
				err(w, f"{f['fn']} does not call {f['delegates_to']}")
			continue
		pairs, targets = analyze_creator(path, node.name)
		src, tgt = dt_of(f["from"]), dt_of(f["to"])
		if pairs:
			if (src, tgt) not in pairs:
				err(w, f"get_mapped_doc maps {sorted(pairs)}, not ({src}, {tgt})")
		elif tgt not in targets:
			err(w, f"creates {sorted(targets) or 'nothing detectable'}, not {tgt}")

	declared = {f["fn"] for f in flows.values()} | set(domain.get("flows_out_of_scope") or [])
	for d in domain.get("flows_out_of_scope") or []:
		res = resolve_dotted(d)
		if not res or res[1] is None:
			err("domain.flows_out_of_scope", f"not found: {d}")
	for scan in domain.get("flow_scan") or []:
		files = [scan] if scan.endswith(".py") else glob.glob(rel(scan + "/**/*.py"), recursive=True)
		for p in files:
			r = os.path.relpath(rel(p), ROOT) if not p.startswith(ROOT) else os.path.relpath(p, ROOT)
			if "/test_" in r or "/patches/" in r:
				continue
			if "get_mapped_doc" not in read(r):
				continue
			for n in parse_py(r).body:
				if isinstance(n, ast.FunctionDef) and is_whitelisted(n) and uses_mapped_doc(r, n.name):
					if dotted_of(r, n.name) not in declared:
						err("domain.flows", f"converter not described: {dotted_of(r, n.name)}")
	return flows


# ---------------------------------------------------------------- features


def check_settings(w: str, settings) -> None:
	for s in settings if isinstance(settings, list) else [settings]:
		dt = s["doctype"]
		if dt not in doctype_index():
			err(w, f"settings doctype {dt!r} not found")
			continue
		fields = fields_of(dt)
		for f, default in (s.get("fields") or {}).items():
			if f not in fields:
				err(w, f"{dt}.{f} not found")
				continue
			actual = fields[f].get("default")
			if (None if default is None else str(default)) != (None if actual is None else str(actual)):
				err(w, f"{dt}.{f} default is {actual!r}, ontology says {default!r}")


def literal_hooks() -> dict:
	out = {}
	for node in parse_py("erpnext/hooks.py").body:
		if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
			out[node.targets[0].id] = node.value
	return out


def hook_lookup(node, keys):
	for k in keys:
		if not isinstance(node, ast.Dict):
			return None
		nxt = None
		for kn, vn in zip(node.keys, node.values):
			if _const(kn) == k:
				nxt = vn
		node = nxt
	return node


def hook_contains(node, value) -> bool:
	if node is None:
		return False
	if isinstance(node, ast.Constant):
		return node.value == value
	if isinstance(node, (ast.List, ast.Tuple)):
		return any(hook_contains(e, value) for e in node.elts)
	return False


def check_features(features: dict, entities: dict) -> dict:
	feats = {f["id"]: f for f in features["features"]}
	for fid, f in feats.items():
		w = f"features.{fid}"
		for key in ("settings", "settings_2"):
			if f.get(key):
				check_settings(w, f[key])
		for dep in f.get("depends_on") or []:
			if dep not in entities and dep not in feats:
				err(w, f"depends_on unknown id {dep!r}")

	for i, d in enumerate(features.get("status_dependencies") or []):
		w = f"features.status_dependencies[{i}]"
		want = {k: v for k, v in d.items() if k not in ("declared_in", "note")}
		found = None
		for n in ast.walk(parse_py(d["declared_in"])):
			if isinstance(n, ast.Dict):
				kv = {_const(k): _const(v) for k, v in zip(n.keys, n.values) if k is not None}
				if all(kv.get(k) == v for k, v in want.items()):
					found = kv
		if not found:
			err(w, f"no status_updater entry {want} in {d['declared_in']}")
			continue
		if d["join_field"] not in fields_of(d["source_dt"]):
			err(w, f"{d['source_dt']}.{d['join_field']} not found")
		if d["target_field"] not in fields_of(d["target_dt"]):
			err(w, f"{d['target_dt']}.{d['target_field']} not found")
		if d.get("target_parent_field") and d["target_parent_field"] not in fields_of(found["target_parent_dt"]):
			err(w, f"{found['target_parent_dt']}.{d['target_parent_field']} not found")

	hooks = literal_hooks()
	for i, h in enumerate(features.get("hooks") or []):
		head, *rest = h["path"].split(".")
		if not hook_contains(hook_lookup(hooks.get(head), rest), h["value"]):
			err(f"features.hooks[{i}]", f"{h['value']!r} not found under {h['path']} in erpnext/hooks.py")
	return feats


# ---------------------------------------------------------------- screens, copy, analytics, code map


def check_screens(screens: dict, entities: dict, flows: dict, copy_ids: set, event_ids: set) -> None:
	ids = {s["id"] for s in screens["screens"]}
	for s in screens["screens"]:
		w = f"screens.{s['id']}"
		for e in s.get("entities") or []:
			if e not in entities:
				err(w, f"unknown entity {e!r}")
		for o in s.get("opens_from") or []:
			if o not in ids:
				err(w, f"opens_from unknown screen {o!r}")
		logic_text = ""
		for p in s.get("logic") or []:
			path = p.partition("#")[0]
			if os.path.isfile(rel(path)) and path.endswith((".js", ".py")):
				logic_text += read(path)
		for fl in s.get("leads_to") or []:
			if fl not in flows:
				err(w, f"leads_to unknown flow {fl!r}")
			elif flows[fl]["fn"] not in logic_text:
				err(w, f"{flows[fl]['fn']} is not called from the screen logic")
		for c in s.get("calls") or []:
			res = resolve_dotted(c)
			if not res or not is_whitelisted(res[1]):
				err(w, f"call {c} is not a whitelisted function")
			if c not in logic_text:
				err(w, f"call {c} not found in screen logic")
		for c in s.get("copy") or []:
			if c not in copy_ids:
				err(w, f"copy id {c!r} not in copy.yaml")
		for ev in s.get("events") or []:
			if ev not in event_ids:
				err(w, f"event {ev!r} not in analytics.yaml")
		if s.get("reports") is not None:
			listed = set(s["reports"])
			for r in s["reports"]:
				p = f"{s['view']}/{r}/{r}.json"
				if not exists(p) or json.loads(read(p)).get("doctype") != "Report":
					err(w, f"report {r} has no Report JSON")
			for p in glob.glob(rel(s["view"] + "/*/")):
				name = os.path.basename(p.rstrip("/"))
				if name not in listed and exists(f"{s['view']}/{name}/{name}.json"):
					err(w, f"report not listed: {name}")


def po_has(text: str, msgid: str) -> bool:
	esc = msgid.replace("\\", "\\\\").replace('"', '\\"')
	return f'msgid "{esc}"\n' in text


def check_copy(copy: dict) -> set:
	langs = sorted(os.path.basename(p)[:-3] for p in glob.glob(rel(copy["catalogs_dir"] + "/*.po")))
	if sorted(copy["languages"]) != langs:
		err("copy.languages", f"catalogs on disk: {langs}")
	behind = set(copy.get("catalogs_behind") or [])
	for lang in ("ar", "fa"):
		if lang not in langs:
			err("copy.rules", f"RTL language {lang} not present")
	pot = read(copy["catalog_template"])
	catalogs = {lang: read(f"{copy['catalogs_dir']}/{lang}.po") for lang in langs}
	really_behind = set()
	for k in copy["keys"]:
		w = f"copy.keys.{k['id']}"
		if k["msgid"] not in read(k["source"]):
			err(w, f"msgid not found in {k['source']}")
		if not po_has(pot, k["msgid"]):
			err(w, "msgid not in main.pot")
		for lang, text in catalogs.items():
			if not po_has(text, k["msgid"]):
				if lang in behind:
					really_behind.add(lang)
				else:
					err(w, f"msgid missing in {lang}.po")
	pot_count = pot.count('\nmsgid "')
	for lang in behind:
		if lang not in really_behind and catalogs.get(lang, "").count('\nmsgid "') >= pot_count:
			err("copy.catalogs_behind", f"{lang} is not behind main.pot; remove it from the list")
	if really_behind:
		notes.append(f"copy: keys not yet in lagging catalogs {sorted(really_behind)}")
	return {k["id"] for k in copy["keys"]}


def check_analytics(an: dict, entities: dict) -> set:
	for e in an.get("events") or []:
		w = f"analytics.events.{e['id']}"
		for side in ("emitted_in", "received_in"):
			for p in e.get(side) or []:
				path = p.partition("#")[0]
				if exists(path) and e["match"] not in read(path):
					err(w, f"{e['match']!r} not found in {path}")
		if not e.get("received_in"):
			err(w, "event has no receiver")
	attr = an.get("attribution")
	if attr:
		dt, _, f = attr["setting"].partition(".")
		if f not in fields_of(dt):
			err("analytics.attribution", f"{attr['setting']} not found")
		for eid in attr["entities"]:
			for fld in attr["fields"]:
				if fld not in fields_of(entities[eid]["doctype"]):
					err("analytics.attribution", f"{fld} not on {eid}")
	for section, key, folder in (("number_cards", "document_type", "number_card"), ("dashboard_charts", "report_name", "dashboard_chart")):
		listed = set()
		for c in an.get(section) or []:
			listed.add(c["json"])
			d = json.loads(read(c["json"]))
			for k in (key, "function"):
				if k in c and d.get(k) != c[k]:
					err(f"analytics.{section}.{c['id']}", f"{k} is {d.get(k)!r} in JSON")
		for p in glob.glob(rel(f"erpnext/selling/{folder}/*/*.json")):
			if os.path.relpath(p, ROOT) not in listed:
				err(f"analytics.{section}", f"not listed: {os.path.relpath(p, ROOT)}")
	return {e["id"] for e in an.get("events") or []} | {"number_cards", "dashboard_charts"}


def check_code_map(cm: dict) -> None:
	for dt, c in (cm.get("controllers") or {}).items():
		cls = top_level(parse_py(c["file"]), dt.replace(" ", ""))
		if not isinstance(cls, ast.ClassDef):
			err(f"code_map.controllers.{dt}", f"class {dt.replace(' ', '')} not in {c['file']}")
		elif c["base"] not in [ast.unparse(b).split(".")[-1] for b in cls.bases]:
			err(f"code_map.controllers.{dt}", f"base is {[ast.unparse(b) for b in cls.bases]}")
	listed = read(cm["patches_list"]).splitlines()
	for p in cm.get("patches") or []:
		if p not in listed:
			err("code_map.patches", f"{p} not in {cm['patches_list']}")
		if not module_file(p):
			err("code_map.patches", f"patch module not found: {p}")


def check_decisions(dec: dict, entities: dict) -> None:
	for d in (dec.get("decisions") or []) + (dec.get("open_questions") or []):
		if not d.get("evidence"):
			err(f"decisions.{d['id']}", "no evidence")
		for a in d.get("affects") or []:
			if a not in entities:
				err(f"decisions.{d['id']}", f"unknown entity {a!r}")


# ---------------------------------------------------------------- main


def main() -> int:
	skel = {}
	for name in YAML_FILES:
		path = os.path.join(HERE, name + ".yaml")
		lines = open(path, encoding="utf-8").read().count("\n")
		if lines > MAX_YAML_LINES:
			err(name, f"{lines} lines, limit {MAX_YAML_LINES}")
		try:
			skel[name] = load_yaml(path)
		except Exception as e:  # report and stop: nothing else can be checked
			err(name, f"cannot parse: {e}")
	readme = os.path.join(HERE, "README.md")
	if open(readme, encoding="utf-8").read().count("\n") > MAX_README_LINES:
		err("README.md", f"more than {MAX_README_LINES} lines")
	if errors:
		return report()

	for name in YAML_FILES + ["README"]:
		text = open(os.path.join(HERE, name + (".md" if name == "README" else ".yaml")), encoding="utf-8").read()
		if SECRET_RE.search(text):
			err(name, "looks like a secret or key")
	check_references("README", open(readme, encoding="utf-8").read(), skel)
	for name, data in skel.items():
		check_references(name, data, skel)

	copy_ids = check_copy(skel["copy"])
	entities = check_entities(skel["domain"], copy_ids)
	flows = check_flows(skel["domain"], entities)
	check_features(skel["features"], entities)
	event_ids = check_analytics(skel["analytics"], entities)
	check_screens(skel["screens"], entities, flows, copy_ids, event_ids)
	check_code_map(skel["code_map"])
	check_decisions(skel["decisions"], entities)
	return report(len(entities), len(flows))


def report(n_entities: int = 0, n_flows: int = 0) -> int:
	for n in notes:
		print("note:", n)
	if errors:
		for e in errors:
			print("FAIL", e)
		print(f"\n{len(errors)} problem(s)")
		return 1
	print(f"OK: {n_entities} entities, {n_flows} flows, all references resolve")
	return 0


if __name__ == "__main__":
	sys.exit(main())
