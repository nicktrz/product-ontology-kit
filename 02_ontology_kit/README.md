# Product ontology kit

**English** · [Русский](README.ru.md)

Materials for the talk "GenAI in product management. Working with virtual employees", meetup "AI in software development", 20 October 2026. Nicolay Amiel Trzhascal, FabricaONE.AI.

## What it is

A product ontology is a small set of files in a `product/` folder next to the code. It records what the product consists of, how its parts are connected, and which decisions and requirements apply, with references to the code. An agent starts from the ontology and follows the references into the code. Scripts make sure the ontology stays in line with the code and check an agent's changes against the requirements.

The ontology has two layers:
- **requirements and decisions** are written by people: the model cannot recover the product owner's intent from the code;
- **the structure** (entities, links, code map) is built by a model, and a script checks it against the code.

## What is in the folder

| File or folder | Purpose |
|---|---|
| `ontology_template.md` | Set of files, form of records and requirements, levels of detail, what the scripts check, settings |
| `build_prompt.md` | Prompts for a strong model: build the ontology of your system and, optionally, the field level |
| `tools/` | Scripts for any system: check against the code `check.py`, index `index.py`, search `find.py`, change check `check_change.py` |
| `agent_rules/` | The rule an agent reads in every task: `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex and other environments that read it, `.cursor/rules/ontology.mdc` for Cursor; `.claude/settings.json` lets the agent run the scripts without asking |
| `example_erpnext/product/` | A finished ontology of the Selling module of the open-source ERP system ERPNext at the document level: records, ERPNext-specific checks, a requirement in the checkable form |

The template, build prompts, agent rules and scripts are in English: agents read them, and English is easier for models and leaves no room for translation errors.

The `.cursor` and `.claude` folders are hidden. In Finder, Cmd+Shift+. shows them.

## How to build the ontology of your product

1. **Pick a part of the system** where a mistake costs most: documents, money, access rights, mandatory fields. For an existing product, the part that is being changed now.
2. **Put the scripts and the template in place.** Create `product/` at the repository root and copy everything from `tools/` and the file `ontology_template.md` into it.
3. **Build the structure with a model.** Give a strong model the first prompt from `build_prompt.md`. It builds the YAML files, the `check_config.yaml` settings and its own checks `check_local.py`, and makes `check.py` pass.
4. **Review.** A person checks the links and the paths that create documents: the model can miss a path or invent a link.
5. **Write down requirements and decisions.** In `product/decisions.yaml`, in the form from the "Decisions and requirements" section of the template. `check_change.py` checks a requirement that lists its exceptions and every path that creates the document. After editing the ontology, run `python3 product/index.py` and `python3 product/check.py` again.
6. **Put the agent rule** at the repository root: `CLAUDE.md`, `AGENTS.md` or the `.cursor` folder, and for Claude Code also the `.claude` folder. If such a file already exists in the repository, append the rule text to it and add the permission lines to `permissions.allow` in your `.claude/settings.json`. If Claude Code still asks for permission to run the scripts (it did for me in non-interactive mode, `claude -p`), pass the file explicitly: `claude -p "..." --settings .claude/settings.json`.
7. **Add to CI.** On every change:
   ```
   python3 product/check.py
   python3 product/check_change.py --base origin/main
   ```
   The first command fails if the ontology no longer matches the code. The second fails if the change violates an approved requirement. It needs the history of `main` in CI: a full clone or `git fetch origin main` before the check. Exit code 2 means a usage error: no such branch or no such requirement.

The scripts need Python 3.9 or newer and git. No other dependencies.

**For 1C and other metadata-driven platforms**, the source of the structure is the configuration exported to files and modules in git. The scripts work with any text files; references to code are written as paths: `src/CommonModules/Orders/Ext/Module.bsl#СоздатьЗаказ`. The scripts have not been tested on 1C; they have been tested on Python and TypeScript.

## How to look at the example

The example shows what the files and records look like. You can run it on the ERPNext code:

```
git clone https://github.com/frappe/erpnext && cd erpnext
git checkout 59ef251a961dff39f3296f84a1bd14bd106959af
cp -R "<path to the kit>/example_erpnext/product" .
python3 product/check.py
```

The last line of output: `OK: 167 records in 7 files, ...`. Before it, the script prints notes (`note:`): repeated ids and translation files that lag behind the main one.

Fetching one record: `python3 product/find.py sales_order_to_sales_invoice` prints the record of the order → invoice conversion and the screens it starts from.

Checking changes: on untouched code, `python3 product/check_change.py --base HEAD` lists everything missing for the requirement "the customer contract number is mandatory on the order": the field in the documents, filling it on every path that creates an order, showing it in reports and print formats, a migration for existing orders.

Clone the full repository: a shallow clone (`--depth 1`) may not contain this commit.

The Selling ontology was built by Opus with an early version of the first prompt from `build_prompt.md`: 18 minutes, about $5 at API list prices. The generic scripts, index, search and requirement were added later. The content is in English, like the ERPNext code. The ontology lacks the blanket order → sales order path; this is noted in `product/README.md`.
