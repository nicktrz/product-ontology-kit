# Which model for which role: OpenAI, Gemini, GLM, Qwen, Kimi, DeepSeek, MiniMax

**English** · [Русский](models_by_role.ru.md)

Materials for the talk "GenAI in product management. Working with virtual employees", meetup "AI in software development", 20 October 2026. Nicolay Amiel Trzhascal, FabricaONE.AI.

## Principle

The model is chosen by the difficulty of the work the role does. In the talk, the team on Claude models was set up this way, and the guide below carries the same setup over to other families. The models were chosen **from independent open benchmarks as of 19 October 2026**; I have not tested the team on these models.

| Level | Roles | What the model has to do |
|---|---|---|
| Strong | analyst, lead | analyse requirements, do the final review, make hard fixes: write order, concurrent operations |
| Mid-range | UX, copywriter, developer | code and texts from a specification |
| Cheap | tester | a pass over a ready checklist |

## Models by family

The number in brackets is the Artificial Analysis index: an independent aggregate score over 10 tests, on a scale up to 100. The index is taken at the reasoning level shown on the AA leaderboard; for most models that is the maximum.

| Family | Strong | Mid-range | Cheap | Open weights |
|---|---|---|---|---|
| OpenAI | GPT-6 Astra (53) | GPT-6.1 Sol (52) | GPT-6 Luna (38) | no |
| Google Gemini | Gemini 4 Argon (53) | Gemini 3.8 Flash (41) | Gemini 3.5 Flash-Lite (22) | no |
| GLM (Z.ai) | GLM-5.3 (45) | GLM-5.3-Flash (42) | GLM-5.3-Flash at low reasoning | yes |
| Qwen (Alibaba) | Qwen3.8-Max (45) | Qwen3.8-Flash (40) | Qwen3.8-Flash without reasoning | the base models of Max and Flash are open; Qwen3.8-27B is fully open |
| Kimi (Moonshot) | Kimi K3 (44) | Kimi K2.7 Code (26) | no cheap model of its own: K2.6 and K2.7 Code cost the same, so the tester gets a model from another family | yes |
| DeepSeek | V4.1-Flash-1017 in max mode (39¹) | the same model in high mode | the same model without reasoning | yes |
| MiniMax | no strong model | MiniMax-M3 (29) | MiniMax-M3 | yes, with conditions |
| Claude, for comparison | Opus 5.5 (58) | Sonnet 5.5 (56) | Haiku 5.5 (43) | no |

¹ The index was probably measured on the previous V4.1 Flash snapshot: the 17 October 2026 version came out two days before the check and has no independent runs yet. It is listed as DeepSeek's strong model based on the vendor's model card: DeepSWE 77.0 for Flash-1017 versus 62.7 for V4-Pro. This is the only place in the guide where the choice rests on vendor numbers.

## On-premises

For code that must not be sent to an external API, open-weight models fit. The strong model needs a cluster; the mid-range and cheap ones are easier to deploy:
- **strong:** GLM-5.3 (index 45, DeepSWE 69%), 753B parameters;
- **mid-range:** GLM-5.3-Flash (index 42, DeepSWE 63%; 320B parameters, 18B active) or Qwen3.8-Flash-Next (125B parameters, 6B active);
- **cheap:** Qwen3.8-27B (index 34): 27B parameters, the easiest to host.

I chose this set from benchmarks and have not tested it in practice.

**Licenses** (from the license texts as of 19 October 2026):
- GLM-5.3 allows commercial use and deployment; a Z.ai security review is required only for companies that sell the model as a service with revenue above $10B a year. GLM-5.3-Flash is MIT;
- Qwen3.8-27B is Apache 2.0;
- Kimi K3 is free for internal use as long as neither the model nor its outputs are passed to third parties; this matters for an integrator writing code for clients;
- the Qwen3.8-Max base model is free inside a company if third parties have no access to it;
- MiniMax-M3: commercial use requires a "Built with MiniMax M3" notice and a notification to MiniMax; revenue above $20M a year requires separate permission; military use is prohibited; internal use is not addressed separately in the license;
- the licenses of Qwen3.8-Flash-Next (qwen-community-1.0) and Kimi K2.7 Code (Modified MIT) were not checked.

## What to know

1. **The reasoning level changes the result more than moving to a neighbouring model.** GPT-6.1 Sol scores 42 at low reasoning and 52 at maximum. Compare models only at the same level. The cheap role often comes from the same model at low reasoning.
2. **The cost of a task matters more than the cost of a token.** In the Artificial Analysis coding agent index, one task cost: Sonnet 5.5 $14.19, Opus 5.5 $13.04, GPT-6.1 Sol $1.55. A Sonnet token costs half as much as an Opus token, but Sonnet spends more tokens on the task, so the task costs more. The cost per task for each model is in the "AA ($/task)" column of `models_detailed.md`.
3. **Coding benchmarks score a model together with the agent environment it ran in.** On Terminal-Bench, Claude, GLM and Qwen ran in Claude Code, OpenAI in Codex, Gemini Flash in mini-SWE-agent. Only DeepSWE runs all models in the same environment (updated 22 September 2026, newer models are not there).
4. **SWE-bench Verified, Aider and LiveCodeBench are outdated for this choice:** current models are not in them.
5. **Open-weight models can be too large for your hardware.** Kimi K3 has 2.8T parameters, the Qwen3.8-Max base 2.4T: they need a cluster.
6. **Prices are temporary.** Gemini 4 Argon doubles in price from 1 December 2026, Gemini 3.8 Flash from 1 January 2027. DeepSeek charges double at peak hours. OpenAI, MiniMax and Haiku charge more for long inputs.

Prices, context, release dates, vendor-reported numbers and all caveats are collected in `models_detailed.md`.

## Sources

- Artificial Analysis, model index: https://artificialanalysis.ai/leaderboards/models (checked 19 October 2026)
- Artificial Analysis, coding agent index: https://artificialanalysis.ai/agents/coding-agents
- DeepSWE v1.1 (Datacurve): https://deepswe.datacurve.ai/ (updated 22 September 2026)
- Terminal-Bench 4.0: https://www.tbench.ai/leaderboard
- Prices and licenses: official API pages and model cards of the vendors (OpenAI, Google, DeepSeek, Moonshot, Alibaba, Z.ai, MiniMax, Anthropic), 19 October 2026; links in `models_detailed.md`
