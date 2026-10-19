# Product ontology for a team of AI agents

**English** · [Русский](README.ru.md)

Materials for the talk "GenAI in product management. Working with virtual employees" at the Softline Group meetup "AI in software development", 20 October 2026. Nicolay Amiel Trzhascal, Director of AI Technology Development, FabricaONE.AI.

**A product ontology** is a set of files in a `product/` folder next to the code. It records what the product consists of, how its parts are connected, and which decisions and requirements apply, with references to the code. An agent fetches the records it needs and follows the references into the code. Scripts check the ontology against the code and check an agent's changes against the requirements.

## What is here

| What | Where |
|---|---|
| One-page memo | [01_memo.md](01_memo.md), printable [01_memo.pdf](01_memo.pdf); in Russian [01_memo.ru.md](01_memo.ru.md) |
| Product ontology kit: template, build prompts for a model, scripts that check the ontology against the code, search it and check changes, for any system; agent rules; an ERPNext example | [02_ontology_kit/](02_ontology_kit/README.md) |
| Agent team: which model to use for which role in the OpenAI, Gemini, GLM, Qwen, Kimi, DeepSeek and MiniMax families and on-premises; task templates for six roles | [03_agent_team/](03_agent_team/README.md) |

## Getting started

The steps are described in [02_ontology_kit/README.md](02_ontology_kit/README.md). In short:

```
mkdir product
cp 02_ontology_kit/tools/*.py 02_ontology_kit/ontology_template.md product/
```

Then a strong model builds the ontology with the first prompt from [build_prompt.md](02_ontology_kit/build_prompt.md), and the checks go into CI:

```
python3 product/check.py
python3 product/check_change.py --base origin/main
```

The scripts need Python 3.9 or newer and git, nothing else.

The template, prompts, agent rules, role tasks and scripts are in English: agents read them. Guides for people are in English and in Russian (`*.ru.md`).

## What was tested

The talk's measurements were made on Claude models. The scripts were tested on ERPNext and on a small TypeScript project. The model-by-role guide for other families is based on open benchmarks as of 19 October 2026; the team setup was not tested on those models.

## Licenses

- **Code** (`*.py`, files in `agent_rules/`): MIT, see [LICENSE](LICENSE).
- **Texts** (`*.md`, PDF): CC BY 4.0, see [LICENSE-docs.md](LICENSE-docs.md).
- **The example** [02_ontology_kit/example_erpnext/](02_ontology_kit/example_erpnext/product/README.md) describes the Selling module of the open-source ERP system [ERPNext](https://github.com/frappe/erpnext) (GPLv3). The repository contains no ERPNext code: the ontology refers to its files and quotes a few UI strings.
