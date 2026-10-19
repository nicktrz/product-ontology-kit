# Models by role in other families: open benchmarks and prices

**English** · [Русский](models_detailed.ru.md)

Collected on 19 October 2026. All prices are in US dollars per 1M tokens (input / cached input / output), the vendor's standard API rate. **[indep.]** means an independent leaderboard produced the number, **[vendor]** means the model vendor reported it from its own runs. Where a number has no publication date, the date of the check (19 October 2026) is given.

In the talk, roles are assigned as follows: a strong model for the analyst and the lead, a mid-range one for UX, copywriter and developer, a cheap one for the tester. On Claude these are Opus 5.5, Sonnet 5.5 and Haiku 5.5.

## 1. Role → model

| Family | Strong: analyst, lead | Mid-range: UX, copywriter, developer | Cheap: tester | Why |
|---|---|---|---|---|
| Claude (as in the talk) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 | AA index: 58 / 56 / 43; Terminal-Bench 4.0: 64.8 / 61.8 / no run |
| OpenAI | GPT-6 Astra | GPT-6.1 Sol | GPT-6 Luna | AA: 53 / 52 / 38. On Terminal-Bench 4.0, Sol and Astra are tied (58.2), and the Sol run cost about 5.5 times less |
| Google Gemini | Gemini 4 Argon | Gemini 3.8 Flash | Gemini 3.5 Flash-Lite | AA: 53 / 41 / 22. On DeepSWE, Flash scores 74%, the same as GPT-6 Astra and Opus 5 |
| DeepSeek | DeepSeek-V4.1-Flash-1017, max mode | the same model, high mode | the same model without reasoning | There is no separate strong model. In DeepSeek's model cards, Flash-1017 has DeepSWE 77.0 and V4-Pro-0813 62.7; on HLE without tools they are level (42.6 and 42.7). There are no independent runs of Flash-1017 yet: the model came out on 17 October 2026 |
| Qwen | Qwen3.8-Max | Qwen3.8-Flash (Flash-Next) | Qwen3.8-Flash without reasoning; on-premises Qwen3.8-27B | AA: 45 / 40 / 34 (27B). Qwen3.7-Plus is weaker than Flash both on AA (25) and in Qwen's own table (DeepSWE 16.5 versus 58.7) |
| Kimi (Moonshot) | Kimi K3, max mode | Kimi K2.7 Code | no cheap model in the lineup: K2.6 and K2.7 Code cost the same | AA: K3 44, K2.7 Code 26. Better to give the tester a cheap model from another family |
| GLM (Zhipu, Z.ai) | GLM-5.3, max mode | GLM-5.3-Flash | GLM-5.3-Flash at low reasoning | AA: 45 / 42. DeepSWE 69 and 63; Flash is about 9 times cheaper per token |
| MiniMax | no strong model | MiniMax-M3 | MiniMax-M3 | Only one current model. AA: 29, below GPT-6 Luna (38) and Haiku 5.5 (43) |

**The fully on-premises option** (our proposal, not a market norm): strong GLM-5.3 (753B parameters, the license allows internal commercial use) or Kimi K3 (2.8T, very heavy); mid-range GLM-5.3-Flash (320B, 18B active, MIT) or Qwen3.8-Flash-Next (125B, 6B active); cheap Qwen3.8-27B (Apache 2.0). Independent numbers for this set: AA 45 / 42 / 34; DeepSWE 69 / 63 / no run.

## 2. Independent numbers: one table for all families

Column sources:
- **AA**: Artificial Analysis Intelligence Index v4.3.2, leaderboard checked 19 October 2026. 10 tests, 30% weight on agentic tasks, 20% on code (Terminal-Bench 4.0, SciCode). In brackets, the cost of a run per task at that reasoning level. https://artificialanalysis.ai/leaderboards/models, methodology https://artificialanalysis.ai/methodology/intelligence-benchmarking
- **AA-code**: AA Coding Agent Index v1.5: DeepSWE v1.1 + Terminal-Bench 4.0 + SWE-Atlas-QnA in equal parts. It measures an "agent + model" pair; the agent is shown. 15 of 42 rows are public, the rest are behind a paid subscription. https://artificialanalysis.ai/agents/coding-agents (19 October 2026)
- **DeepSWE**: DeepSWE v1.1 (Datacurve), 113 new tasks, 91 repositories, 5 languages. All models run in the same agent, mini-swe-agent; the best reasoning level is shown, ± is the confidence interval. Updated 22 September 2026, so later models are not there. https://deepswe.datacurve.ai/
- **TB 4.0**: Terminal-Bench 4.0 (Stanford, Laude Institute), ± is the 95% confidence interval. The agent differs between models and is shown in brackets. https://www.tbench.ai/leaderboard (19 October 2026)
- **τ³**: τ³-bench, banking_knowledge domain, pass^1. Runs by Sierra, published 4 August 2026. https://github.com/sierra-research/tau2-bench/tree/main/web/leaderboard/public/submissions

All numbers in the table are [indep.].

| Model | AA (effort, $/task) | AA-code (agent, $/task) | DeepSWE v1.1 | TB 4.0 (agent) | τ³ banking |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 58 (max, $5.98) | 66 (Claude Code, $13.04) | no run | 64.8 ± 3.1 (Claude Code) | no run |
| Claude Sonnet 5.5 | 56 (max, $5.46) | 68 (Claude Code, $14.19) | no run | 61.8 ± 2.9 (Claude Code) | no run |
| Claude Haiku 5.5 | 43 (max, $0.21) | 36 (Claude Code) | no run | no run | no run |
| GPT-6 Astra | 53 (max, $3.26) | 62 (Codex, $7.47) | 74 ± 3 (xhigh, $4.43) | 58.2 ± 2.8 (Codex) | no run |
| GPT-6.1 Sol | 52 (max, $0.72) | 60 (Codex, $1.55) | no run | 58.2 ± 3.1 (Codex) | no run |
| GPT-6 Sol | no index | — | no run | 49.4 ± 3.2 (Codex) | no run |
| GPT-6 Luna | 38 (max, $0.07) | — | no run | 16.4 ± 2.7 (Codex) | no run |
| Gemini 4 Argon | 53 (high, $1.99) | 64 (Antigravity CLI, $5.84) | no run | no run | no run |
| Gemini 3.8 Flash | 41 (high, $1.24) | — | 74 ± 1 (high, $2.36) | 19.1 ± 3.4 (mini-SWE-agent) | no run |
| Gemini 3.5 Flash-Lite | 22 ($0.19) | — | no run | no run | no run |
| DeepSeek V4.1 Flash¹ | 39 (max, $0.49) | — | no run | no run | no run |
| DeepSeek V4 Pro 0813 | 36 (max, $0.67) | — | 63 ± 6 (max, $1.67) | no run | no run |
| DeepSeek V4 Flash (old, 0731) | — | — | 53 ± 4 (max, $0.46) | no run | no run |
| Kimi K3 | 44 (max, $2.00) | 52 (Kimi Code CLI) | 69 ± 5 (max, $4.65) | no run | 37.1 (max) |
| Kimi K2.7 Code | 26 ($0.54) | — | no run | no run | no run |
| Qwen3.8-Max (0902) | 45 ($5.41) | — | 57 ± 3 (xhigh, $3.73) | 27.0 ± 3.8 (Claude Code) | 55.2 (xhigh)² |
| Qwen3.8-Flash-Next | 40 ($0.37) | — | no run | no run | no run |
| Qwen3.8-27B | 34 (xhigh, $1.01) | — | no run | no run | no run |
| Qwen3.7-Plus | 25 ($0.22) | — | no run | no run | no run |
| GLM-5.3 | 45 (max, $2.01) | 54 (Opencode) | 69 ± 3 (max, $3.99) | 41.8 ± 3.2 (Claude Code) | no run |
| GLM-5.3-Flash | 42 ($0.28) | — | 63 ± 4 (max, $0.24) | 35.8 ± 3.5 (Claude Code, no reasoning) | no run |
| MiniMax-M3 | 29 ($0.51) | — | no run | no run | no run |

¹ AA does not state the snapshot. Most likely this is the September version, before Flash-1017.
² Sierra's run of 3 August 2026; the model is called "Qwen 3.8 Max" with a release date of 19 July 2026. This is an earlier snapshot than 0902.

For comparison, on τ³ banking (the same Sierra run): Claude Opus 5 48.7; GPT-5.6 Sol 46.9; GLM-5.2 37.1. New OpenAI, Google and Anthropic models are not in this run.

## 3. By family: versions, prices, context, weights, vendor numbers

### OpenAI

| Model (API id) | Level | Released | Price: input / cache / output | Context | Weights |
|---|---|---|---|---|---|
| GPT-6 Astra (`gpt-6-astra`) | strong | 3 Sep 2026 | 10 / 1 / 50; input over 272K tokens 20 / 2 / 75 | 1.05M, output up to 128K | closed |
| GPT-6.1 Sol (`gpt-6.1-sol`) | mid-range | 29 Sep 2026 | 2 / 0.10 / 10; over 272K: 4 / 0.20 / 15 | 1.05M / 128K | closed |
| GPT-6 Luna (`gpt-6-luna`) | cheap | 22 Sep 2026 | 0.10 / 0.01 / 0.50; over 272K: 0.20 / 0.02 / 0.75 | 1.05M / 128K | closed |

Prices: https://developers.openai.com/api/docs/pricing; models and context: https://developers.openai.com/api/docs/models (19 October 2026). OpenAI has open weights only for gpt-oss-120b (2025); its AA score is 12, too weak for these roles.

Reported by OpenAI [vendor]:
- GPT-6 Astra: Terminal-Bench 4.0 57.9%; DeepSWE v1.1 74.1%; BrowseComp 91.5%; OSWorld 2.0 (offline set) 72.6%. The maximum across reasoning levels is taken. https://openai.com/index/gpt-6-astra/ (3 Sep 2026)
- GPT-6 Sol (max): DeepSWE v1.1 68.8%. GPT-6 Luna (max): DeepSWE v1.1 66.6%, "on par with Opus 5 and Fable 5 at medium effort" and 93% cheaper than Opus 5 per task. GPT-6 Sol (xhigh) on AutomationBench: 33.2% at $0.27 per task. https://openai.com/index/introducing-gpt-6-sol-and-luna/ (22 Sep 2026)
- GPT-6.1 Sol on DeepSWE v1.1 "matches Astra at about a fifth of the cost"; on Terminal-Bench Science 0.1, $5.47 per task versus $23.80 for Astra. The text gives no exact DeepSWE number, only a chart. https://openai.com/index/introducing-gpt-6-1-sol/ (29 Sep 2026)

### Google Gemini

| Model (id) | Level | Released | Price: input / cache / output | Context | Weights |
|---|---|---|---|---|---|
| Gemini 4 Argon (`gemini-4-argon`) | strong | GA 13 Oct 2026 | 2 / 0.10 / 10 until 30 Nov 2026, then 4 / 0.20 / 20 | 1M for input and output together | closed |
| Gemini 3.8 Flash (`gemini-3.8-flash`) | mid-range | 2 Sep 2026 (per the Terminal-Bench table) | 0.75 / 0.075 / 3.75 until 31 Dec 2026, then 1.50 / 0.15 / 7.50 | 1M (per AA) | closed |
| Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) | cheap | not found | 0.30 / 0.03 / 2.50 | 1M (per AA) | closed |

Prices: https://ai.google.dev/gemini-api/docs/pricing; model list: https://ai.google.dev/gemini-api/docs/models (updated 13 October 2026). Argon announcement: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/ (13 October 2026). Cached input for Flash and Flash-Lite also has a storage fee. Google's open models are the Gemma 4 family; Gemma 4 31B scores 15 on AA.

Reported by Google [vendor]: the benchmark table in the model card (https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-4-Argon-Model-Card.pdf, October 2026) is an image; the numbers could not be extracted as text. DeepSWE and Terminal-Bench numbers quoted by the press were not found in the primary source and are not used here.

### DeepSeek

| Model (id) | Level | Released | Price: input / cache / output | Context | Weights |
|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash-1017 (`deepseek-flash`) | all three levels through the reasoning mode | 17 Oct 2026 | peak 0.30 / 0.006 / 1.20; off-peak half: 0.15 / 0.003 / 0.60 | 1M, output up to 384K | open, MIT; 763B parameters |
| DeepSeek-V4-Pro-0813 (`deepseek-v4-pro`) | fallback strong | 13 Aug 2026 (by version number) | peak 1.32 / 0.044 / 3.96; off-peak 0.66 / 0.022 / 1.98 | 1M, output up to 384K | open, MIT; 1.7T parameters |

Peak hours: 01:00–04:00 and 06:00–10:00 UTC on weekdays. Prices and versions: https://api-docs.deepseek.com/quick_start/pricing (19 October 2026). The old name `deepseek-v4-flash` already serves Flash-1017. Model cards: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813

Reported by DeepSeek [vendor]:
- V4.1-Flash-1017: Terminal-Bench 4.0 42.3 (Claude Code agent); DeepSWE v1.1 77.0 (Mini-SWE-V2 agent); AutomationBench 60.5. In the same table, Opus 5 has 51.8 and 74.0, GPT-5.6 Sol 39.9 and 73.0. https://api-docs.deepseek.com/news/news261017 (17 October 2026)
- V4-Pro-0813: Terminal-Bench 2.1 87.9; DeepSWE 62.7; Toolathlon-Verified 74.1 (DeepSeek's own agent, max mode). The independent DeepSWE gave 63 ± 6, so the claim holds.

### Kimi (Moonshot AI)

| Model (id) | Level | Released | Price: input / cache / output | Context | Weights |
|---|---|---|---|---|---|
| Kimi K3 (`kimi-k3`) | strong | 16 Jul 2026 | 3.00 / 0.30 / 15.00; cache write 3.00 for 5 min, 6.00 for an hour | 1,048,576 | open, Kimi K3 License; 2.8T parameters, 104B active |
| Kimi K2.7 Code (`kimi-k2.7-code`) | mid-range | 12 Jun 2026 (per the press) | 0.95 / 0.19 / 4.00 | 262,144 | open, Modified MIT; 1T, 32B active |
| Kimi K2.6 (`kimi-k2.6`) | instead of cheap | not checked | 0.95 / 0.16 / 4.00 | 262,144 | open |

Prices: https://platform.kimi.ai/docs/pricing/chat (19 October 2026). The K3 date is taken from the metadata of the Sierra run, which cites the blog post https://www.kimi.com/blog/kimi-k3. Model cards: https://huggingface.co/moonshotai/Kimi-K3, https://huggingface.co/moonshotai/Kimi-K2.7-Code

K3 license: internal use without passing the model or its outputs to third parties is free. A company that sells access to the model as a service with more than $20M over 12 months needs a separate agreement with Moonshot. Products with more than 100M monthly users or more than $20M monthly revenue must show "Kimi K3" in the interface. https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE

Reported by Moonshot [vendor]:
- K3 (max, Kimi Code agent): DeepSWE 67.5 (67.3 in mini-SWE-agent); Terminal-Bench 2.1 88.3; BrowseComp 91.2 (with context compression at 300K); MCP-Atlas 84.2; MCPMark-Verified 94.5; Toolathlon-Verified 76.5. The independent DeepSWE gave 69 ± 5.
- K2.7 Code: Kimi Code Bench v2 62.0 (K2.6: 50.9); MCP Atlas 76.0; MCPMark Verified 81.1. Kimi Code Bench is Moonshot's own test.

### Qwen (Alibaba)

| Model (id) | Level | Released | Price: input / output | Context | Weights |
|---|---|---|---|---|---|
| Qwen3.8-Max (`qwen3.8-max`, snapshot `qwen3.8-max-0902`) | strong | 19 Jul 2026, snapshot 0902 on 2 Sep 2026 | 2 / 6 | up to 1M | closed in the API; the base Qwen3.8-2.4T-A95B is open (12 Aug 2026, qwen3.8-max license), Max is built on it |
| Qwen3.8-Flash (`qwen3.8-flash`) | mid-range | Flash-Next weights on HF from 27 Aug 2026 | 0.15 / 0.47 | up to 1M | closed in the API; the base Qwen3.8-Flash-Next is open (125B, 6B active, qwen-community-1.0) |
| Qwen3.8-27B (`qwen3.8-27b`) | cheap for on-premises | 14 Aug 2026 (HF) | 0.5 / 3 via API | 262K, extendable to 1M | open, Apache 2.0 |
| Qwen3.7-Plus (`qwen3.7-plus`) | not recommended | 26 May 2026 | 0.4 / 1.6 up to 256K (currently 20% off) | 1M, more expensive past 256K | closed |

Prices, international region: https://www.alibabacloud.com/help/en/model-studio/model-pricing (updated 15 October 2026). Cached input costs 10% of regular input. Alibaba's recommended trio (max / plus / flash): https://www.alibabacloud.com/help/en/model-studio/models (updated 10 October 2026). Weight dates: https://huggingface.co/Qwen

Qwen3.8-2.4T-A95B license: internal use without third-party access is free. Companies that sell the model as a service or an AI assistant and earn more than $50M over 12 months need a separate license. https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/blob/main/LICENSE

Reported by Qwen [vendor]:
- Qwen3.8-Max: Terminal-Bench 2.1 86.6; SWE-bench Pro 67.7 (Claude Code agent, on Qwen's corrected version of the test); DeepSWE 1.1 56.6; Toolathlon Verified 72.5. The independent DeepSWE gave 57 ± 3. https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B
- Qwen3.8-Flash-Next: DeepSWE 1.1 58.7; SWE-bench Pro 62.5; SWE-bench Multilingual 81.0; Toolathlon Verified 73.5. In the same table, Qwen3.7-Plus has DeepSWE 16.5 and SWE-bench Pro 55.8. https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- Qwen3.8-27B: Terminal-Bench 2.1 73.0; SWE-bench Pro 61.7; DeepSWE 42.2. https://huggingface.co/Qwen/Qwen3.8-27B

### GLM (Zhipu, Z.ai)

| Model | Level | Released | Price: input / cache / output | Context | Weights |
|---|---|---|---|---|---|
| GLM-5.3 | strong | 14 Aug 2026 (per the Terminal-Bench table) | 1.4 / 0.26 / 4.4 | 1M (per AA) | open, glm-5.3 license; 753B parameters |
| GLM-5.3-Flash | mid-range and cheap | 26 Aug 2026 (same source) | 0.15 / 0.03 / 0.50 | 1M (per AA) | open, MIT; 320B, 18B active |
| GLM-5.3-FlashX | not assessed | not found | 0.37 / 0.075 / 1.25 | not found | not found |

Prices: https://docs.z.ai/guides/overview/pricing (19 October 2026). Model cards: https://huggingface.co/zai-org/GLM-5.3, https://huggingface.co/zai-org/GLM-5.3-Flash

GLM-5.3 license: use, deployment and fine-tuning are allowed, including commercially. Only a company that sells the model as a service and earns more than $10B a year needs a Z.ai security review. https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE

Reported by Z.ai [vendor]: GLM-5.3: Terminal-Bench 2.1 88.2; Terminal-Bench 3.0 28.3; DeepSWE v1.1 66.9 (mini-swe-agent); Toolathlon Verified 73.0; AutomationBench 48.2. Independent: DeepSWE 69 ± 3, Terminal-Bench 4.0 41.8 ± 3.2. The GLM-5.3-Flash table is an image; its numbers were not extracted.

### MiniMax

| Model | Level | Released | Price: input / cache / output | Context | Weights |
|---|---|---|---|---|---|
| MiniMax-M3 | mid-range or cheap | around 1 Jun 2026 (press); technical report arXiv 2606.13392 | up to 512K tokens: 0.30 / 0.06 / 1.20 (permanent 50% discount from 0.60 / 0.12 / 2.40); over 512K: 0.60 / 0.12 / 2.40 | 1M | open, minimax-community license; 428B, 23B active |
| MiniMax-M2.7 | old | April 2026 (HF) | 0.3 / 0.06 / 1.2 | not checked | open |

Prices: https://platform.minimax.io/docs/pricing/overview (19 October 2026). Model card: https://huggingface.co/MiniMaxAI/MiniMax-M3

M3 license: non-commercial use is free. Commercial use requires a "Built with MiniMax M3" notice and a one-time email notification to MiniMax. Revenue above $20M a year requires separate permission. Military use is prohibited. Internal use is not addressed separately; it is worth confirming with MiniMax. https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/LICENSE

Reported by MiniMax [vendor]: SWE-bench Verified 80.5; SWE-bench Pro 59. Both numbers carry an asterisk without explanation. Long-Horizon Terminal Bench 2.0 46.9 (terminus-2 agent, 3 hours per task).

## 4. Caveats: what is comparable and what is not

1. **SWE-bench Verified does not fit this comparison.** On the official swebench.com leaderboard (bash-only mode, mini-SWE-agent), the latest entries are from 26 February 2026; current models are not there. Vendors have moved to DeepSWE, SWE-bench Pro and Terminal-Bench. Only MiniMax still quotes Verified (80.5), and there is nothing to compare it with. https://www.swebench.com/
2. **Of the coding tests listed, only DeepSWE v1.1 is comparable across all families.** All models run in the same agent (mini-swe-agent) there. Vendor DeepSWE claims match the independent runs within the margin of error: Kimi K3 67.5 and 69 ± 5, GLM-5.3 66.9 and 69 ± 3, DeepSeek V4-Pro 62.7 and 63 ± 6, Qwen3.8-Max 56.6 and 57 ± 3. The downside: the leaderboard was updated on 22 September 2026, so newer models are missing.
3. **Terminal-Bench 4.0 measures a model-and-agent pair.** Claude, GLM and Qwen ran in Claude Code, OpenAI in Codex, Gemini 3.8 Flash in mini-SWE-agent. So Gemini 3.8 Flash's 19.1 is probably understated: it scores 74 on DeepSWE. Vendor tables cite Terminal-Bench 2.1 (leaders around 88%) and 3.0. These are different task sets; do not compare them with 4.0.
4. **The reasoning level changes the result more than moving to a neighbouring model.** GPT-6.1 Sol scores 42 on low and 52 on max in the AA index; Claude Haiku 5.5 scores 29 and 43. The cheap role often comes from the same model at low effort. In the new open families, the "fast" model has caught up with the flagship: DeepSeek V4.1-Flash-1017 is above V4-Pro on DeepSWE (per DeepSeek's cards), Qwen3.8-Flash-Next beats 3.8-Max on DeepSWE (per Qwen), GLM-5.3-Flash trails GLM-5.3 by 3 AA points at a price 9 times lower.
5. **The independent coding index puts Sonnet 5.5 above Opus 5.5:** 68 versus 66 in the AA Coding Agent Index. On Terminal-Bench 4.0 and the overall AA index, Opus leads (64.8 versus 61.8 and 58 versus 56). The Terminal-Bench intervals overlap. In the talk, the strong model was put on analysis and the final review, which agrees with the data: on coding tests the gap between Opus and Sonnet is small.
6. **The price per token is not the price per task.** Sonnet 5.5 at max spent $14.19 per task of the coding index, more than Opus 5.5 ($13.04), because it uses more tokens. GPT-6.1 Sol completed the same index at $1.55. Compare the "$/task" column of AA.
7. **AA index versions differ.** OpenAI's announcement cites index v4.1.1 (Astra 61.2); the site now shows v4.3.2 (Astra at max 53). Do not compare numbers from different versions.
8. **Claude is marked "with fallback" on AA.** When a task is refused for safety reasons, a fallback Anthropic model finishes it. This affects the final score.
9. **Vendor tables compare against previous versions of competitors.** DeepSeek and Moonshot compare with Opus 4.8, Opus 5 and GPT-5.6 Sol, while Opus 5.5 and GPT-6 are already current. Toolathlon-Verified, BrowseComp and the MCP benchmarks (MCP-Atlas, MCPMark) were found only in vendor reports.
10. **Prices are temporary.** Gemini 4 Argon doubles in price from 1 December 2026, Gemini 3.8 Flash from 1 January 2027. MiniMax-M3 has a "permanent 50% discount", Qwen3.7-Plus a temporary 20% discount. DeepSeek charges double at peak hours. Long context costs more: OpenAI past 272K input tokens, Haiku 5.5 past 100K, MiniMax past 512K, Qwen3.7-Plus past 256K.
11. **Open weights do not mean "easy to deploy".** Kimi K3 has 2.8T parameters, Qwen3.8-2.4T 2.4T, DeepSeek V4-Pro 1.7T; they need a cluster. Realistic on-premises options are GLM-5.3-Flash (18B active), Qwen3.8-Flash-Next (6B active), Qwen3.8-27B, MiniMax-M3 (23B active). The Modified MIT (Kimi K2.7 Code) and qwen-community-1.0 (Qwen3.8-Flash-Next) licenses were not read.
12. **Not found.** LMArena WebDev: the page is behind a bot check and was not opened. LiveCodeBench: the task window ends on 1 May 2025, no current models. Aider Polyglot: last updated 20 November 2025, no current models. τ²/τ³-bench: current models only for Kimi K3 and Qwen3.8-Max, and only in the banking_knowledge domain. The release dates of Gemini 3.5 Flash-Lite and Claude Haiku 5.5 were not found.

## 5. Links

Independent leaderboards:
- Artificial Analysis, overall index: https://artificialanalysis.ai/leaderboards/models (checked 19 October 2026)
- Artificial Analysis, methodology v4.3.2: https://artificialanalysis.ai/methodology/intelligence-benchmarking
- Artificial Analysis, coding agent index v1.5: https://artificialanalysis.ai/agents/coding-agents (checked 19 October 2026)
- DeepSWE v1.1 (Datacurve): https://deepswe.datacurve.ai/ (updated 22 September 2026)
- Terminal-Bench 4.0: https://www.tbench.ai/leaderboard (checked 19 October 2026)
- τ³-bench, Sierra runs: https://github.com/sierra-research/tau2-bench/tree/main/web/leaderboard/public/submissions (4 August 2026); site https://taubench.com/
- SWE-bench Verified: https://www.swebench.com/ (latest entries 26 February 2026)
- Aider Polyglot: https://aider.chat/docs/leaderboards/ (updated 20 November 2025)
- LiveCodeBench: https://livecodebench.github.io/leaderboard.html (task window up to 1 May 2025)

Vendors and price lists:
- OpenAI: https://openai.com/index/gpt-6-astra/ (3 Sep 2026), https://openai.com/index/introducing-gpt-6-sol-and-luna/ (22 Sep 2026), https://openai.com/index/introducing-gpt-6-1-sol/ (29 Sep 2026), https://developers.openai.com/api/docs/pricing, https://developers.openai.com/api/docs/models
- Google: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/ (13 Oct 2026), https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-4-Argon-Model-Card.pdf, https://ai.google.dev/gemini-api/docs/pricing, https://ai.google.dev/gemini-api/docs/models
- DeepSeek: https://api-docs.deepseek.com/quick_start/pricing, https://api-docs.deepseek.com/news/news261017 (17 Oct 2026), https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813
- Moonshot: https://platform.kimi.ai/docs/pricing/chat, https://huggingface.co/moonshotai/Kimi-K3, https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE, https://huggingface.co/moonshotai/Kimi-K2.7-Code
- Alibaba: https://www.alibabacloud.com/help/en/model-studio/model-pricing (15 Oct 2026), https://www.alibabacloud.com/help/en/model-studio/models (10 Oct 2026), https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B, https://huggingface.co/Qwen/Qwen3.8-Flash-Next, https://huggingface.co/Qwen/Qwen3.8-27B
- Z.ai: https://docs.z.ai/guides/overview/pricing, https://huggingface.co/zai-org/GLM-5.3, https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE, https://huggingface.co/zai-org/GLM-5.3-Flash
- MiniMax: https://platform.minimax.io/docs/pricing/overview, https://huggingface.co/MiniMaxAI/MiniMax-M3, https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/LICENSE
- Anthropic (for comparison): https://platform.claude.com/docs/en/about-claude/pricing, https://platform.claude.com/docs/en/about-claude/models/overview. Opus 5.5: 4 / 0.20 / 20; Sonnet 5.5: 2 / 0.10 / 10; Haiku 5.5: 0.10 / 0.01 / 0.50 up to 100K tokens per request and 0.50 / 0.05 / 2.50 beyond that; context 1M for all, output up to 128K.
