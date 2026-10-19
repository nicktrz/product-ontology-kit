# Product ontology

`product/` holds the product ontology: entities, conversions between documents and screens, decisions and requirements, and a code map with references to files.

## How to read it
1. Do not read the whole ontology. Start with `product/INDEX.md`, the index.
2. Fetch the records you need by search: `python3 product/find.py <id or word>`.
3. If the task is about a product decision or a requirement (what a change affects, which options exist, what the product owner has to decide), read `product/decisions.yaml` in full.
4. Read the code through the references in the ontology. Search the repository only when the ontology does not have what you need.

## How to change things
- Do not weaken or work around the requirements in the `requirements` section of `product/decisions.yaml`: do not drop a mandatory flag, do not put in stubs, do not add exceptions.
- If a requirement cannot be met without a product decision, stop and ask. Open questions (`open_questions`) are decided by the product owner.
- If you change code, texts or behaviour, update the ontology record and run `python3 product/index.py` and `python3 product/check.py`.
- At the start of the task, note the commit you start from: `git rev-parse HEAD`.
- Before handing over, check the change against the requirements: `python3 product/check_change.py --base <that commit>`. Fix violations tagged `[technical]`. Do not work around violations tagged `[product]`: describe them to the product owner.
- Add decisions and requirements you made yourself to `product/decisions.yaml` with `status: proposed`, so that they are approved in review. Do not edit approved requirements.
