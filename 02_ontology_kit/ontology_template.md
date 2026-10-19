# Product ontology: template

The product ontology lives in `product/` at the repository root. It records what the product consists of, how its parts are connected, and which decisions and requirements apply, with references to the code. An agent reads the index, fetches the records it needs by search, and opens only the code files it needs.

## Contents

| File | What it holds |
|---|---|
| `README.md` | Map of the ontology: which files exist, what each holds, in which order to read them for typical tasks. Up to 120 lines |
| `INDEX.md` | Index: one line per file, each line lists record ids with line numbers. Written by `index.py` |
| `domain.yaml` | Entities: documents and master data, user-facing name, definition file in the code, key fields, links. Conversions `flows`: which document is created from which, by which function |
| `screens.yaml` | Screens and routes: purpose, view and logic files, where the screen opens from, where it leads, which texts and events it uses |
| `features.yaml` | Cross-cutting functions: settings, notifications, payments, permissions, integrations; where they live in the code, what they depend on |
| `copy.yaml` | Texts: languages, translation files, key rules, key strings |
| `analytics.yaml` | Events: name, where declared, where sent, required properties |
| `code_map.yaml` | Modules and layers, naming conventions, what can be skipped, how to build and run tests |
| `fields.yaml` | Optional, field level: where a field is filled from, where it is carried to, where it is printed and shown in reports |
| `decisions.yaml` | Decisions (`decisions`), open questions (`open_questions`) and requirements in the checkable form (`requirements`) |
| `check_config.yaml` | Script settings, optional |

The scripts from the kit's `tools/` folder go into the same `product/` folder:

| Script | What it does |
|---|---|
| `check.py` | Checks the ontology against the code. Exit code 1 on any mismatch |
| `check_local.py` | Checks specific to your system. The model writes it while building the ontology; `check.py` calls it at the end |
| `index.py` | Writes `INDEX.md` |
| `find.py` | Prints only the records that contain the given words |
| `check_change.py` | Checks a change against the requirements in `decisions.yaml`. Exit code 1 on a violation |
| `ontology.py` | Shared code of the scripts: YAML reading, records, code references |

The scripts need Python 3.9 or newer and git. PyYAML is optional: without it, a built-in parser reads the YAML.

## How a record is written

- **A record** is a list item that starts with `id`: `- id: order` or `- {id: order, ...}`. Otherwise the index and the search do not see it. An id must be unique across all files; `check.py` reports a repeated id as a note (`note:`) and still passes, but a reference to such an id is ambiguous.
- **A reference to another record** is its id under a link key: `entities`, `entity`, `from`, `to`, `leads_to`, `opens_from`, `depends_on`, `affects`, `applies_to`, `carried_to`, `value_from`, `screen`, `screens`, `events`, `copy`, `links`, `tables`. The list of keys is set in `check_config.yaml`.
- **A reference to code** is a path from the repository root, optionally with a symbol or a line: `src/orders/order_service.py#OrderService.submit`, `docs/api.md#errors`, `src/app.ts:42`. Under the keys `fn`, `delegates_to`, `calls`, `method`, `handler` a function can also be named by module: the scripts look for `orders.mapper.make_invoice` as the file `orders/mapper.py` from the repository root or from the folders in `path_roots`. For Java, C#, Go, 1C and code deep inside `src/`, a path is more reliable: `src/orders/mapper.ts#makeInvoice`.
- **A document of another part of the system** that the ontology does not describe is listed in `external_ids`.

```yaml
entities:
  - id: order
    label: Customer order
    definition: src/orders/models/order.py#Order      # where the document is defined in the code
    key_fields: [customer, status, contract_no]
    links: {customer: customer, contract_no: contract}
flows:
  - {id: quote_to_order, fn: src/orders/mapper.py#make_order_from_quote, from: quote, to: order}
  - {id: group_po_to_order, fn: src/purchasing/mapper.py#make_group_order, from: purchase_order, to: order}
```

A screen record and a decision record:

```yaml
screens:
  - id: order_form
    purpose: Create and submit a customer order
    view: src/ui/orders/OrderForm.tsx
    logic: [src/ui/orders/orderForm.ts]
    entities: [order, customer]
    opens_from: [order_list]
    leads_to: [order_to_invoice]
decisions:
  - id: closed_order_not_cancellable
    decision: A closed order cannot be cancelled; it has to be reopened first
    evidence: [src/orders/order_service.py#OrderService.cancel]
    affects: [order]
```

## Levels of detail

Requirements and decisions are written at any level.

| Level | What is recorded | Files | When needed |
|---|---|---|---|
| Map | Parts of the product, modules, conventions, how to build and run tests | `README.md`, `code_map.yaml` | always |
| Documents and links | Entities, conversions between screens and documents, every path that creates each document, events and statuses | `domain.yaml`, `screens.yaml`, `features.yaml`, `copy.yaml`, `analytics.yaml` | the main level: record search and change checks work on it |
| Fields | Where a field is filled from, where it is carried to, whether it is mandatory, link fields, computed fields, where it is printed and shown in reports | `fields.yaml` | optional, for the part of the system where a mistake costs most. This level costs more to build and to read. On an open-source system it did not raise answer quality; on a closed one it has not been tested yet |
| Functions and calls | Code graph: what calls what | not part of the ontology | built by code analysis tools |

## Rules

- **References to code.** The ontology holds the path to a file, the name of a type or a function; code is not copied into it. A value that matters for the product may be written down; its check against the code goes into `check_local.py`.
- **Short.** Each YAML file stays under 300 lines; everything else stays in the code and documents. The exception is `fields.yaml`: agents read it only through search.
- **Explicit links.** A screen refers to entities; a conversion refers to the source and the target document.
- **No secrets.** Keys, tokens, passwords, SDK identifiers, commercial data and prices never go into the ontology. `check.py` looks for strings that look like secrets.
- **The ontology changes with the code.** Whoever changes behaviour, texts or structure updates the record and runs `index.py` and `check.py`.

## Decisions and requirements

Decisions visible in the code and documents are carried over by the model during the build, with a reference to the source. The product owner's intent that exists neither in the code nor in documents is written down by people. Decisions and requirements an agent writes on its own are marked `status: proposed`, and people approve them in review, like code. The scripts skip a requirement with `status: proposed` until it is approved.

A requirement is written so that an agent cannot work around it and `check_change.py` can check it:

```yaml
requirements:
  - id: contract_no_required
    kind: product              # product: the product owner resolves a violation; technical: the author of the change fixes it
    rule: The customer contract number is mandatory on the order. It is carried from the quote to the order, from the order to the invoice and the delivery note, printed on the invoice, shown in sales reports
    field: contract_no         # field name in the code; a list if layers name it differently: [contractNo, contract_no]
    entity: order              # where the rule applies
    value_from: contract       # where the value comes from: the Contract document
    carried_to: [quote, invoice, delivery_note]       # where the field must also exist
    required_near_field: ['required:\s*true']         # regex: the mandatory flag within 15 lines of the field in the entity definition
    applies_to: [quote_to_order, group_po_to_order]   # creation paths that must fill the field
    exceptions: []             # paths where the rule does not apply; an empty list means no exceptions
    shown_in: [src/reports/sales_register.py, templates/print/invoice.html]
    forbidden_values: [N/A, TBD]                      # stubs next to the field, case-insensitive
    forbidden_in_change: ['required:\s*false']        # regex: weakening the rule next to the field
    migration: ^migrations/.*\.py$                    # path regex: a migration for existing records
    open_questions: []         # while not empty, a change to this field does not pass the check
    approved_by: product owner
```

An agent given a requirement in plain words may exempt some cases on its own or put in a stub. `check_change.py` checks the explicit exceptions and the full list of paths on every change. It catches stubs only from the `forbidden_values` list. It does not check where the value actually comes from: `value_from` is there for the human reviewer, to notice that an agent put in the number of some other document.

## What the scripts check

`check.py`:
- the YAML parses; repeated ids are reported as notes;
- every reference to a record points to an existing id;
- every path to code exists, the function or class name is in the file, the line number is within the file;
- a requirement has `kind` and `exceptions`, and every path that creates its document is listed in `applies_to` or `exceptions`;
- `INDEX.md` matches the records;
- files are not longer than 300 lines, there are no strings that look like secrets;
- `check_local.py` is called at the end.

`check_change.py --base <branch or commit before the change> [requirement id]`:
- the field is in the document's definition and in every document from `carried_to`, the mandatory flag is in place;
- every path that creates the document is named in the requirement;
- every path from `applies_to` fills the field: the source document has the field, or the conversion function or functions from the same file that it calls mention it;
- the field is in every file from `shown_in`;
- the change adds no stubs from `forbidden_values` next to the field and does not weaken the rule;
- if the field is new, the change contains a migration for existing records;
- the change does not edit or delete approved requirements;
- if the change touches the field, there are no open questions.

The change is the difference from the point where the branch left `--base`, together with new files. The `product/` and `work/` folders are not part of it. Exit code 0: the requirements are met; 1: there are violations; 2: a usage error.

A violation tagged `[product]` goes back to the product owner; one tagged `[technical]` is fixed by the author of the change. A creation path without the value is tagged by the requirement's `kind`: with `kind: product`, the product owner decides where the value comes from.

The scripts look for names in the text of files; they do not run the code and do not replace tests. What they do not see:
- where the value comes from: the number of another document instead of the contract number passes the check;
- a check removed from the code, if the rule is written only in the definition;
- paths that create the documents from `carried_to`: if the rule applies there too, they get a requirement of their own;
- creation paths missing from the ontology: a person is responsible for the completeness of paths.

## Settings: `check_config.yaml`

| Key | What it sets | Default |
|---|---|---|
| `path_roots` | Folders to also resolve paths from (for paths relative to an app folder) | `[""]`, the repository root |
| `external_ids` | Documents outside the ontology that records may refer to | empty |
| `ref_keys`, `extra_ref_keys` | Link keys: replace the list or add to it | the list above |
| `dotted_keys`, `dotted_extensions` | Keys holding functions named by module, and file extensions for them; the second key replaces the whole list | `fn`, `delegates_to`, `calls`, `method`, `handler`; `.py`, `.js`, `.ts`, `.java`, `.kt`, `.cs`, `.go`, `.rb`, `.php` |
| `definition_keys` | Entity keys holding the definition file | `definition`, `schema`, `json`, `model`, `code` |
| `max_lines`, `size_exempt` | File length limit and exempt files | 300; `fields.yaml` |
| `ignore_paths` | Path prefixes `check.py` does not check | empty |
| `no_path_keys` | Keys whose values are not treated as paths | `forbidden_values`, `forbidden_in_change`, `required_near_field`, `migration` |
| `change_ignore` | Folders `check_change.py` does not count as a code change | `work/` |

## System-specific checks: `check_local.py`

```python
def check(ont, error, warn):
    # ont.records: id -> record; ont.root: repository root; ont.flows(): conversions
    for rid, rec in ont.records.items():
        for f in rec.get("key_fields") or []:
            ...  # find the field in the definition file; if missing: error(f"{ont.loc(rid)}: no field {f}")
```

In the ERPNext example, `check_local.py` runs the checks for that system: fields exist in the document definitions, conversion functions create the declared document, texts exist in the translation files.

## How to build

The prompt for a strong model is in `build_prompt.md`, the order of steps is in the kit's `README.md`. A person reviews the finished ontology: the model can miss a path that creates a document or invent a link.
