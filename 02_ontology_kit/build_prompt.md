# Ontology build prompt

**English** · [Русский](build_prompt.ru.md)

Give this prompt once to a strong model in an agent environment (Claude Code, Codex, Cursor and the like), at the repository root. Before the run, `product/` already holds the scripts from `tools/` and the file `ontology_template.md`. The prompts are in English: that is easier for models and leaves no room for translation errors. Replace the values in angle brackets with those of your system.

Opus built the Selling ontology of ERPNext from the example with an early version of this prompt in 18 minutes; the build cost about $5 at API list prices.

## Document and link level

```
Build the product ontology in `product/` for the part of the system <name of the part, e.g. "Sales">: <folders or modules>, and its links to neighbouring parts (<neighbours>). The format, the set of files and the rules are described in `product/ontology_template.md`. Do not describe the whole system: neighbouring parts are needed only as the points where they meet this part.

Build from what the system already describes formally, and check against it:
- take entities and their links from <data schemas / document definitions / ORM models / exported configuration metadata>; do not copy fields in full, give a reference to the definition (`definition`);
- take conversions ("which document or screen is created from which") from the functions that create one object from another and from routes; for every document, list every path that creates it;
- take events and status dependencies from event handlers and shared controllers;
- give reports, print formats, translations, migrations and tests as references.
If there are no formal descriptions, build the structure from the code.

The scripts in `product/` are already there; do not rewrite them. Then:
1. Run `python3 product/index.py` and `python3 product/check.py` and make the check pass. List documents of other parts that conversions refer to under `external_ids` in `product/check_config.yaml`.
2. Write `product/check_local.py` with checks specific to this system: fields from `key_fields` exist in the definitions, conversion functions really create the declared document, texts exist in the translation files. The form of the file is described in the template.
3. Carry decisions and requirements from <documents / tasks> into `product/decisions.yaml`, citing the source. Whatever the sources do not settle, leave as an open question.
4. Write `product/README.md`: which files exist, what each holds, in which order to read them for typical tasks.
5. At the end, run `python3 product/index.py` and `python3 product/check.py` again: the check must pass.

Write the ontology in English. Do not create an agent rules file. Do not change other files in the repository.
At the end, list briefly what is included, what is not, and what you are unsure about.
```

After the build:
- a person reviews `domain.yaml` and the conversions: the model can miss a path that creates a document;
- people add the requirements and decisions that are not in the sources to `decisions.yaml` themselves;
- `python3 product/check.py` goes into CI on every change.

## Field level, optional

Run the second prompt after the document level is built and `check.py` passes. The field level costs more to build and to read. On an open-source system it did not raise answer quality; on a closed one it has not been tested yet. So it is built for one part of the system, where a mistake costs most.

```
`product/` holds the ontology of the part of the system <name of the part> at the document level: entities, conversions, screens, decisions, code map, with the scripts `index.py`, `find.py`, `check.py` and `check_local.py`. Add the field level to it.

Create `product/fields.yaml` for the documents <list of documents and their line tables>, and for the source documents they are created from. For each document record:
- key fields: name, type, mandatory flag, no-copy flag, hidden in print, visibility and mandatory conditions if set; do not copy the full list of fields, take only the fields that take part in the links below, plus the mandatory ones;
- link fields: which document the field refers to;
- computed fields and statuses: which fields they depend on and which function computes them (reference to the code);
- where the field is shown: print formats and reports of this part that use the field (references to files).
For each conversion in `domain.yaml`, record which fields it carries into the target document: what is copied by the system's rule, what by an explicit mapping, what by a post-processing function, with a reference to the code. If the source document lacks a field that is mandatory in the target, mark it (`missing_in_source`).

Then:
1. Add checks to `product/check_local.py`: every field from `fields.yaml` exists in the document definition with the stated type and flags; print formats and reports really contain the field name. Make `python3 product/check.py` pass.
2. Run `python3 product/index.py` and `python3 product/check.py`, and make sure `python3 product/find.py <field>` finds records from `fields.yaml`.
3. Add to `product/README.md` what `fields.yaml` holds and which questions to read it for: what a field change affects, where the field is carried, where it is shown.

Write in English. The size of `fields.yaml` is not limited: agents read it through record search. Do not change other files in the repository. At the end, briefly: what is included, how many records, what you are unsure about.
```
