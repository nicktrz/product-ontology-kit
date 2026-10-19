# Agent team: roles, models, lead

**English** · [Русский](README.ru.md)

Materials for the talk "GenAI in product management. Working with virtual employees", meetup "AI in software development", 20 October 2026. Nicolay Amiel Trzhascal, FabricaONE.AI.

## How the team works

Five agents in team roles work on one task and pass files to each other in the repository's `work/` folder: analyst → UX → copywriter → developer → tester. At the end, a lead on a strong model reviews the overall result and fixes the hard parts. All of them share the product ontology (`product/`, see the product ontology kit).

| Role | Model level | What it does | Writes |
|---|---|---|---|
| Analyst | strong | specification: what changes, acceptance criteria, affected requirements and every path that creates the affected documents | `work/<id>-spec.md` |
| UX | mid-range | flow and screens as text, states, accessibility | `work/<id>-ux.md` |
| Copywriter | mid-range | texts in all product languages | `work/<id>-copy.md` |
| Developer | mid-range | code, texts in string files, ontology updates | `work/<id>-dev-notes.md` |
| Tester | cheap | tests, a pass over the acceptance criteria, a list of risks | `work/<id>-qa.md` |
| Lead | strong | reads the tester's risks, fixes the hard parts, adds tests | `work/<id>-review.md` |

Which model to use at each level in the OpenAI, Gemini, GLM, Qwen, Kimi, DeepSeek and MiniMax families and on-premises is described in `models_by_role.md`.

## What is in the folder

| File | Purpose |
|---|---|
| `role_tasks/` | Task templates for the six roles, in English: agents read them. Before a run, fill in the values in angle brackets in a copy: `<id>` is the task number, plus build and test commands and the path to the document with constraints |
| `models_by_role.md` | Which model to use for which role in different families, based on independent benchmarks as of 19 October 2026 |
| `models_detailed.md` | The full breakdown: prices, context, licenses, vendor-reported numbers, caveats about benchmarks |

## How to run it

The tasks are not tied to an agent environment. I ran them in Claude Code; I have not tested them in Codex, Cursor, Qwen Code, Kimi Code CLI or other environments. Each role runs as a separate session at the repository root, one after another, with its own model. A role's task is the text from `role_tasks/` with the values filled in. The agent rules and the ontology live in the repository, so every role reads them.

Running the team in a separate branch is convenient. Before the first role, note the commit the task starts from: the developer and the lead run `python3 product/check_change.py --base <commit before the task>` against it, and the lead reviews the changes with `git diff <commit before the task>`. Before the lead's turn, add new files with `git add -A` so that `git diff` shows them too. `check_change.py` does not count the `work/` folder with the team's documents as a code change; adding it to `.gitignore` is convenient.

If the environment runs without a person, allow file edits and build, test and ontology script commands in advance. In Claude Code this is the list of allowed commands in `.claude/settings.json`. A sample is in the product ontology kit, in `agent_rules/`: it allows only the ontology scripts; add build and test commands to the same list, and allow file edits with `--permission-mode acceptEdits`. In `claude -p` mode, pass the settings file explicitly with `--settings .claude/settings.json`.

## What matters

- **The strong model goes on task analysis and the final review.** A mid-range model writes code and texts from the specification, a cheap one goes through the checklist.
- **The lead sees the tester's report.** A cheap model working through a checklist notices a risk; a strong one confirms it with a test and fixes it.
- **The shared ontology and the shared `work/` folder tie the roles together.**
- **Agents do not make product decisions:** they write open questions down for the product owner.
- **Cost per role is counted per session.** In Claude Code in non-interactive mode (`claude -p --output-format stream-json --verbose`) it is in the `modelUsage` field of the final event; the `usage` field there covers only the last step.
