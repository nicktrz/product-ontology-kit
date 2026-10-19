# Промпт сборки онтологии

Этот промпт дают сильной модели в агентной среде (Claude Code, Codex, Cursor и подобных) один раз, в корне репозитория. Перед запуском в папке `product/` уже лежат скрипты из `tools/` и файл `ontology_template.md`. Промпты написаны на английском: так модели проще работать и меньше ошибок перевода. Значения в угловых скобках подставляют под свою систему.

Онтологию модуля «Продажи» ERPNext из примера Opus собрал по ранней версии этого задания за 18 минут, сборка стоила около $5 по прейскуранту API.

## Уровень документов и связей

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

После сборки:
- человек просматривает `domain.yaml` и переходы: модель может пропустить путь создания документа;
- требования и решения, которых нет в источниках, люди дописывают в `decisions.yaml` сами;
- `python3 product/check.py` ставят в CI на каждое изменение.

## Уровень полей, по желанию

Второй промпт запускают после того, как уровень документов собран и `check.py` проходит. Уровень полей дороже в сборке и в чтении. На открытой системе качество он не поднял, на закрытой его пока не проверяли, поэтому его собирают для одной части системы, где ошибка дороже всего.

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
