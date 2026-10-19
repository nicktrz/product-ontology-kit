# Product ontology: Selling

> Describes [ERPNext](https://github.com/frappe/erpnext) (GPLv3) at commit `59ef251` of the `develop` branch.
> No ERPNext code is included: the ontology references ERPNext files and quotes a few UI strings.

Map of the **Selling** bounded context of ERPNext (`erpnext/selling`) and its joints with
neighbour contexts: invoices (`accounts`), delivery and stock (`stock`), CRM (`crm`) and the
shared controllers (`erpnext/controllers`). Neighbours are described only where they touch Selling.

Every record points to code: a file path, a `path.py#Class.method` symbol, a dotted server method
or a DocType name. Nothing is copied from code except values that matter for the product
(status options, setting defaults, UI strings); `check.py` compares those with the code.

## Files

| File | What it holds |
|---|---|
| `domain.yaml` | Entities (DocTypes): key fields, links to other entities, child tables, row references, statuses, lifecycle methods, tests. Document conversions (`flows`). |
| `screens.yaml` | Desk forms, lists, calendar, POS and funnel pages, workspace, customer portal, reports: files, entry points, which conversions each screen starts. |
| `features.yaml` | Cross-cutting functions (settings, credit limit, stock reservation, proforma, item close, pricing, portal, ...), status dependencies between documents, relevant `hooks.py` entries. |
| `copy.yaml` | Translation setup: languages, catalogs, key format, rules, the key strings of the context. |
| `analytics.yaml` | Realtime events, UTM attribution, number cards, dashboard charts. |
| `code_map.yaml` | Layers and where they live, controller inheritance, neighbour paths, naming conventions, what to skip, patches, how to run tests. |
| `decisions.yaml` | Product decisions visible in code (with evidence), open questions, and requirements in the checkable form (`requirements`). |
| `check_config.yaml` | Settings of the scripts: path roots, documents outside this ontology. |
| `INDEX.md`, `index.py`, `find.py` | Index of record ids with line numbers, its generator, and search that prints only matching records. |
| `check.py`, `ontology.py` | Generic check of the ontology against the code (ids, links, paths, symbols, requirements, size, secrets). |
| `check_local.py`, `erpnext_checks.py` | ERPNext-specific checks called by `check.py`: DocType fields, mappers, statuses, translations, settings. |
| `check_change.py` | Checks a change against the requirements: `python3 product/check_change.py --base <commit>`. |

## Reading order by task

- **Change a document's fields or rules** (Quotation, Sales Order, Customer...): `domain.yaml`
  entity -> its `json` and `code` -> `features.yaml` if a setting or shared behaviour is involved.
- **Change what a "Create" button produces**: `domain.yaml#flows` -> the `fn` -> `screens.yaml`
  for the client side.
- **Status looks wrong** (e.g. order stays "To Bill"): `domain.yaml` entity `status` ->
  `features.yaml#status_dependencies` -> `erpnext/controllers/status_updater.py`.
- **Work on Delivery Note / Sales Invoice behaviour seen from Selling**: boundary entities in
  `domain.yaml`, `features.yaml#status_dependencies`, `code_map.yaml#neighbours`.
- **UI text or translation**: `copy.yaml`.
- **Form or list behaviour**: `screens.yaml` -> `logic` files.
- **Settings switch**: `features.yaml#selling_settings`.
- **Before deciding product behaviour**: `decisions.yaml`.
- **Running tests**: `code_map.yaml#build_and_test`.

## Ids

Entity ids are the snake_case of the DocType name (`sales_order` = "Sales Order"), the same as the
DocType folder. Screens, flows, features, copy keys and events have their own ids; references
between files always use ids.

## Keeping it current

Whoever changes behaviour, texts or structure of the context updates the matching record and runs:

```
python3 product/index.py
python3 product/check.py
```

The scripts need only Python 3.9+ and git (PyYAML optional). Besides the generic checks, `erpnext_checks.py` verifies:

- every path and `#symbol` exists; every dotted server method resolves;
- every DocType, field, link target, child table, status option and setting default matches the JSON;
- every lifecycle method listed is called from the named hook method;
- every conversion function exists, is whitelisted and maps the declared source to the declared
  target (reads `get_mapped_doc` / `new_doc` in the function and its helpers);
- every whitelisted converter in the scanned files is described or explicitly out of scope;
- every selling DocType, report, number card and chart is covered;
- status dependencies and hooks exist in the controllers and `hooks.py`;
- copy keys occur in source, `main.pot` and every catalog not marked as lagging;
- file size limits, and no secrets.

The ontology does not replace reading code: links can be missed. When the check passes but a
relation looks absent, search the code and add the record. Known gap: the Blanket Order -> Sales Order
conversion (`erpnext/manufacturing/doctype/blanket_order/blanket_order.py#make_order`) is not in `flows` yet.
