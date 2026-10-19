# Модели по ролям в других семействах: открытые бенчмарки и цены

Собрано 19.10.2026. Все цены в долларах за 1 млн токенов (вход / кешированный вход / выход), стандартный тариф API у разработчика модели. **[незав.]** — цифру получил независимый лидерборд, **[произв.]** — цифру заявил производитель модели на своих прогонах. Если у цифры нет даты публикации, указан день проверки (19.10.2026).

В докладе роли распределены так: сильная модель у аналитика и ведущего, средняя у UX, копирайтера и разработчика, дешёвая у тестировщика. На Claude это Opus 5.5, Sonnet 5.5 и Haiku 5.5.

## 1. Раскладка «роль → модель»

| Семейство | Сильная: аналитик, ведущий | Средняя: UX, копирайтер, разработчик | Дешёвая: тестировщик | Почему так |
|---|---|---|---|---|
| Claude (как в докладе) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 | Индекс AA: 58 / 56 / 43; Terminal-Bench 4.0: 64,8 / 61,8 / нет прогона |
| OpenAI | GPT-6 Astra | GPT-6.1 Sol | GPT-6 Luna | AA: 53 / 52 / 38. На Terminal-Bench 4.0 у Sol и Astra поровну (58,2), а прогон Sol стоил примерно в 5,5 раза меньше |
| Google Gemini | Gemini 4 Argon | Gemini 3.8 Flash | Gemini 3.5 Flash-Lite | AA: 53 / 41 / 22. На DeepSWE у Flash 74%, столько же, сколько у GPT-6 Astra и Opus 5 |
| DeepSeek | DeepSeek-V4.1-Flash-1017, режим max | та же модель, режим high | та же модель без рассуждения | Отдельной сильной модели нет. В карточках DeepSeek у Flash-1017 DeepSWE 77,0, у V4-Pro-0813 62,7; на HLE без инструментов они наравне (42,6 и 42,7). Независимых прогонов Flash-1017 пока нет: модель вышла 17.10.2026 |
| Qwen | Qwen3.8-Max | Qwen3.8-Flash (Flash-Next) | Qwen3.8-Flash без рассуждения; в контуре Qwen3.8-27B | AA: 45 / 40 / 34 (27B). Qwen3.7-Plus слабее Flash и по AA (25), и в таблице самих Qwen (DeepSWE 16,5 против 58,7) |
| Kimi (Moonshot) | Kimi K3, режим max | Kimi K2.7 Code | дешёвой модели в линейке нет: K2.6 и K2.7 Code стоят одинаково | AA: K3 44, K2.7 Code 26. Тестировщику лучше дать дешёвую модель другого семейства |
| GLM (Zhipu, Z.ai) | GLM-5.3, режим max | GLM-5.3-Flash | GLM-5.3-Flash с низким усилием | AA: 45 / 42. DeepSWE 69 и 63; Flash стоит примерно в 9 раз дешевле по токенам |
| MiniMax | сильной модели нет | MiniMax-M3 | MiniMax-M3 | Актуальная модель одна. AA: 29, это ниже GPT-6 Luna (38) и Haiku 5.5 (43) |

**Вариант «всё внутри контура»** (наше предложение, не рыночная норма): сильная GLM-5.3 (753 млрд параметров, лицензия разрешает внутреннее коммерческое использование) или Kimi K3 (2,8 трлн, очень тяжёлая); средняя GLM-5.3-Flash (320 млрд, из них 18 млрд активных, MIT) или Qwen3.8-Flash-Next (125 млрд, 6 млрд активных); дешёвая Qwen3.8-27B (Apache 2.0). Независимые цифры для этой связки: AA 45 / 42 / 34; DeepSWE 69 / 63 / нет прогона.

## 2. Независимые цифры: одна таблица на все семейства

Источники столбцов:
- **AA** — Artificial Analysis Intelligence Index v4.3.2, лидерборд проверен 19.10.2026. 10 тестов, 30% веса у агентных задач, 20% у кода (Terminal-Bench 4.0, SciCode). В скобках цена прогона на задачу при этом уровне рассуждения. https://artificialanalysis.ai/leaderboards/models, методика https://artificialanalysis.ai/methodology/intelligence-benchmarking
- **AA-код** — AA Coding Agent Index v1.5: DeepSWE v1.1 + Terminal-Bench 4.0 + SWE-Atlas-QnA поровну. Меряется связка «агент + модель», агент указан. Открыты 15 из 42 строк, остальное за платной подпиской. https://artificialanalysis.ai/agents/coding-agents (19.10.2026)
- **DeepSWE** — DeepSWE v1.1 (Datacurve), 113 новых задач, 91 репозиторий, 5 языков. Все модели прогнаны в одном агенте mini-swe-agent, показан лучший уровень рассуждения, ± — доверительный интервал. Обновлено 22.09.2026, поэтому более поздних моделей там нет. https://deepswe.datacurve.ai/
- **TB 4.0** — Terminal-Bench 4.0 (Stanford, Laude Institute), ± — 95% доверительный интервал. Агент у разных моделей разный, он указан в скобках. https://www.tbench.ai/leaderboard (19.10.2026)
- **τ³** — τ³-bench, домен banking_knowledge, pass^1. Прогоны Sierra, опубликованы 04.08.2026. https://github.com/sierra-research/tau2-bench/tree/main/web/leaderboard/public/submissions

Все цифры в таблице [незав.].

| Модель | AA (усилие, $/задача) | AA-код (агент, $/задача) | DeepSWE v1.1 | TB 4.0 (агент) | τ³ banking |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 58 (max, $5,98) | 66 (Claude Code, $13,04) | нет прогона | 64,8 ± 3,1 (Claude Code) | нет прогона |
| Claude Sonnet 5.5 | 56 (max, $5,46) | 68 (Claude Code, $14,19) | нет прогона | 61,8 ± 2,9 (Claude Code) | нет прогона |
| Claude Haiku 5.5 | 43 (max, $0,21) | 36 (Claude Code) | нет прогона | нет прогона | нет прогона |
| GPT-6 Astra | 53 (max, $3,26) | 62 (Codex, $7,47) | 74 ± 3 (xhigh, $4,43) | 58,2 ± 2,8 (Codex) | нет прогона |
| GPT-6.1 Sol | 52 (max, $0,72) | 60 (Codex, $1,55) | нет прогона | 58,2 ± 3,1 (Codex) | нет прогона |
| GPT-6 Sol | нет индекса | — | нет прогона | 49,4 ± 3,2 (Codex) | нет прогона |
| GPT-6 Luna | 38 (max, $0,07) | — | нет прогона | 16,4 ± 2,7 (Codex) | нет прогона |
| Gemini 4 Argon | 53 (high, $1,99) | 64 (Antigravity CLI, $5,84) | нет прогона | нет прогона | нет прогона |
| Gemini 3.8 Flash | 41 (high, $1,24) | — | 74 ± 1 (high, $2,36) | 19,1 ± 3,4 (mini-SWE-agent) | нет прогона |
| Gemini 3.5 Flash-Lite | 22 ($0,19) | — | нет прогона | нет прогона | нет прогона |
| DeepSeek V4.1 Flash¹ | 39 (max, $0,49) | — | нет прогона | нет прогона | нет прогона |
| DeepSeek V4 Pro 0813 | 36 (max, $0,67) | — | 63 ± 6 (max, $1,67) | нет прогона | нет прогона |
| DeepSeek V4 Flash (старая, 0731) | — | — | 53 ± 4 (max, $0,46) | нет прогона | нет прогона |
| Kimi K3 | 44 (max, $2,00) | 52 (Kimi Code CLI) | 69 ± 5 (max, $4,65) | нет прогона | 37,1 (max) |
| Kimi K2.7 Code | 26 ($0,54) | — | нет прогона | нет прогона | нет прогона |
| Qwen3.8-Max (0902) | 45 ($5,41) | — | 57 ± 3 (xhigh, $3,73) | 27,0 ± 3,8 (Claude Code) | 55,2 (xhigh)² |
| Qwen3.8-Flash-Next | 40 ($0,37) | — | нет прогона | нет прогона | нет прогона |
| Qwen3.8-27B | 34 (xhigh, $1,01) | — | нет прогона | нет прогона | нет прогона |
| Qwen3.7-Plus | 25 ($0,22) | — | нет прогона | нет прогона | нет прогона |
| GLM-5.3 | 45 (max, $2,01) | 54 (Opencode) | 69 ± 3 (max, $3,99) | 41,8 ± 3,2 (Claude Code) | нет прогона |
| GLM-5.3-Flash | 42 ($0,28) | — | 63 ± 4 (max, $0,24) | 35,8 ± 3,5 (Claude Code, без рассуждения) | нет прогона |
| MiniMax-M3 | 29 ($0,51) | — | нет прогона | нет прогона | нет прогона |

¹ AA не указывает снимок. Скорее всего, это версия от сентября, до Flash-1017.
² Прогон Sierra от 03.08.2026, модель названа «Qwen 3.8 Max» с датой выхода 19.07.2026. Это более ранний снимок, чем 0902.

Для сравнения на τ³ banking (тот же прогон Sierra): Claude Opus 5 48,7; GPT-5.6 Sol 46,9; GLM-5.2 37,1. Новых моделей OpenAI, Google и Anthropic в этом прогоне нет.

## 3. По семействам: версии, цены, контекст, веса, заявленные цифры

### OpenAI

| Модель (id в API) | Уровень | Вышла | Цена: вход / кеш / выход | Контекст | Веса |
|---|---|---|---|---|---|
| GPT-6 Astra (`gpt-6-astra`) | сильная | 03.09.2026 | 10 / 1 / 50; при входе больше 272 тыс. токенов 20 / 2 / 75 | 1,05 млн, выход до 128 тыс. | закрыты |
| GPT-6.1 Sol (`gpt-6.1-sol`) | средняя | 29.09.2026 | 2 / 0,10 / 10; больше 272 тыс.: 4 / 0,20 / 15 | 1,05 млн / 128 тыс. | закрыты |
| GPT-6 Luna (`gpt-6-luna`) | дешёвая | 22.09.2026 | 0,10 / 0,01 / 0,50; больше 272 тыс.: 0,20 / 0,02 / 0,75 | 1,05 млн / 128 тыс. | закрыты |

Цены: https://developers.openai.com/api/docs/pricing; модели и контекст: https://developers.openai.com/api/docs/models (19.10.2026). Открытые веса у OpenAI есть только у gpt-oss-120b (2025); по AA у неё 12, для этих ролей она слабая.

Заявлено OpenAI [произв.]:
- GPT-6 Astra: Terminal-Bench 4.0 — 57,9%; DeepSWE v1.1 — 74,1%; BrowseComp — 91,5%; OSWorld 2.0 (офлайн-набор) — 72,6%. Берётся максимум по уровням рассуждения. https://openai.com/index/gpt-6-astra/ (03.09.2026)
- GPT-6 Sol (max): DeepSWE v1.1 — 68,8%. GPT-6 Luna (max): DeepSWE v1.1 — 66,6%, «на уровне Opus 5 и Fable 5 на среднем усилии» и на 93% дешевле Opus 5 за задачу. GPT-6 Sol (xhigh) на AutomationBench — 33,2% при $0,27 за задачу. https://openai.com/index/introducing-gpt-6-sol-and-luna/ (22.09.2026)
- GPT-6.1 Sol на DeepSWE v1.1 «совпадает с Astra примерно за пятую часть цены», на Terminal-Bench Science 0.1 — $5,47 за задачу против $23,80 у Astra. Точного числа по DeepSWE в тексте нет, оно только на графике. https://openai.com/index/introducing-gpt-6-1-sol/ (29.09.2026)

### Google Gemini

| Модель (id) | Уровень | Вышла | Цена: вход / кеш / выход | Контекст | Веса |
|---|---|---|---|---|---|
| Gemini 4 Argon (`gemini-4-argon`) | сильная | общий доступ 13.10.2026 | 2 / 0,10 / 10 до 30.11.2026, затем 4 / 0,20 / 20 | 1 млн на вход и выход вместе | закрыты |
| Gemini 3.8 Flash (`gemini-3.8-flash`) | средняя | 02.09.2026 (по таблице Terminal-Bench) | 0,75 / 0,075 / 3,75 до 31.12.2026, затем 1,50 / 0,15 / 7,50 | 1 млн (по AA) | закрыты |
| Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) | дешёвая | не нашла | 0,30 / 0,03 / 2,50 | 1 млн (по AA) | закрыты |

Цены: https://ai.google.dev/gemini-api/docs/pricing; список моделей: https://ai.google.dev/gemini-api/docs/models (обновлено 13.10.2026). Анонс Argon: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/ (13.10.2026). У кешированного входа Flash и Flash-Lite есть ещё плата за хранение. Открытые модели Google — семейство Gemma 4; у Gemma 4 31B по AA 15.

Заявлено Google [произв.]: таблица бенчмарков в карточке модели (https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-4-Argon-Model-Card.pdf, октябрь 2026) дана картинкой, текстом цифры извлечь не удалось. Числа по DeepSWE и Terminal-Bench, которые пересказывает пресса, в первоисточнике не нашла и сюда не беру.

### DeepSeek

| Модель (id) | Уровень | Вышла | Цена: вход / кеш / выход | Контекст | Веса |
|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash-1017 (`deepseek-flash`) | все три уровня через режим рассуждения | 17.10.2026 | час пик 0,30 / 0,006 / 1,20; вне пика вдвое дешевле: 0,15 / 0,003 / 0,60 | 1 млн, выход до 384 тыс. | открыты, MIT; 763 млрд параметров |
| DeepSeek-V4-Pro-0813 (`deepseek-v4-pro`) | запасная сильная | 13.08.2026 (по номеру версии) | пик 1,32 / 0,044 / 3,96; вне пика 0,66 / 0,022 / 1,98 | 1 млн, выход до 384 тыс. | открыты, MIT; 1,7 трлн параметров |

Час пик: 01:00–04:00 и 06:00–10:00 UTC по будням. Цены и версии: https://api-docs.deepseek.com/quick_start/pricing (19.10.2026). Старое имя `deepseek-v4-flash` уже обслуживает Flash-1017. Карточки моделей: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813

Заявлено DeepSeek [произв.]:
- V4.1-Flash-1017: Terminal-Bench 4.0 — 42,3 (агент Claude Code); DeepSWE v1.1 — 77,0 (агент Mini-SWE-V2); AutomationBench — 60,5. В той же таблице у Opus 5 51,8 и 74,0, у GPT-5.6 Sol 39,9 и 73,0. https://api-docs.deepseek.com/news/news261017 (17.10.2026)
- V4-Pro-0813: Terminal-Bench 2.1 — 87,9; DeepSWE — 62,7; Toolathlon-Verified — 74,1 (собственный агент DeepSeek, режим max). Независимый DeepSWE дал 63 ± 6, то есть заявление подтверждается.

### Kimi (Moonshot AI)

| Модель (id) | Уровень | Вышла | Цена: вход / кеш / выход | Контекст | Веса |
|---|---|---|---|---|---|
| Kimi K3 (`kimi-k3`) | сильная | 16.07.2026 | 3,00 / 0,30 / 15,00; запись в кеш 3,00 на 5 мин, 6,00 на час | 1 048 576 | открыты, Kimi K3 License; 2,8 трлн параметров, из них 104 млрд активных |
| Kimi K2.7 Code (`kimi-k2.7-code`) | средняя | 12.06.2026 (по прессе) | 0,95 / 0,19 / 4,00 | 262 144 | открыты, Modified MIT; 1 трлн, 32 млрд активных |
| Kimi K2.6 (`kimi-k2.6`) | вместо дешёвой | не проверяла | 0,95 / 0,16 / 4,00 | 262 144 | открыты |

Цены: https://platform.kimi.ai/docs/pricing/chat (19.10.2026). Дата K3 взята из метаданных прогона Sierra, где указан блог https://www.kimi.com/blog/kimi-k3. Карточки: https://huggingface.co/moonshotai/Kimi-K3, https://huggingface.co/moonshotai/Kimi-K2.7-Code

Лицензия K3: внутреннее использование без передачи модели и её ответов третьим лицам свободно. Компании, которая продаёт доступ к модели как сервис и получает больше $20 млн за 12 месяцев, нужен отдельный договор с Moonshot. Продукты с аудиторией больше 100 млн пользователей в месяц или выручкой больше $20 млн в месяц должны показывать «Kimi K3» в интерфейсе. https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE

Заявлено Moonshot [произв.]:
- K3 (max, агент Kimi Code): DeepSWE — 67,5 (в mini-SWE-agent — 67,3); Terminal-Bench 2.1 — 88,3; BrowseComp — 91,2 (со сжатием контекста на 300 тыс.); MCP-Atlas — 84,2; MCPMark-Verified — 94,5; Toolathlon-Verified — 76,5. Независимый DeepSWE дал 69 ± 5.
- K2.7 Code: Kimi Code Bench v2 — 62,0 (у K2.6 — 50,9); MCP Atlas — 76,0; MCPMark Verified — 81,1. Kimi Code Bench — собственный тест Moonshot.

### Qwen (Alibaba)

| Модель (id) | Уровень | Вышла | Цена: вход / выход | Контекст | Веса |
|---|---|---|---|---|---|
| Qwen3.8-Max (`qwen3.8-max`, снимок `qwen3.8-max-0902`) | сильная | 19.07.2026, снимок 0902 — 02.09.2026 | 2 / 6 | до 1 млн | у API закрыты; открыта базовая Qwen3.8-2.4T-A95B (12.08.2026, лицензия qwen3.8-max), Max построена на ней |
| Qwen3.8-Flash (`qwen3.8-flash`) | средняя | веса Flash-Next на HF от 27.08.2026 | 0,15 / 0,47 | до 1 млн | у API закрыты; открыта база Qwen3.8-Flash-Next (125 млрд, 6 млрд активных, qwen-community-1.0) |
| Qwen3.8-27B (`qwen3.8-27b`) | дешёвая для контура | 14.08.2026 (HF) | 0,5 / 3 через API | 262 тыс., можно растянуть до 1 млн | открыты, Apache 2.0 |
| Qwen3.7-Plus (`qwen3.7-plus`) | не рекомендую | 26.05.2026 | 0,4 / 1,6 до 256 тыс. (сейчас скидка 20%) | 1 млн, дороже после 256 тыс. | закрыты |

Цены, регион «международный»: https://www.alibabacloud.com/help/en/model-studio/model-pricing (обновлено 15.10.2026). Кешированный вход стоит 10% от обычного. Рекомендуемая тройка Alibaba (max / plus / flash): https://www.alibabacloud.com/help/en/model-studio/models (обновлено 10.10.2026). Даты весов: https://huggingface.co/Qwen

Лицензия Qwen3.8-2.4T-A95B: внутреннее использование без доступа третьих лиц свободно. Компаниям, которые продают модель как сервис или ИИ-ассистента и получают больше $50 млн за 12 месяцев, нужна отдельная лицензия. https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/blob/main/LICENSE

Заявлено Qwen [произв.]:
- Qwen3.8-Max: Terminal-Bench 2.1 — 86,6; SWE-bench Pro — 67,7 (агент Claude Code, на исправленной Qwen версии теста); DeepSWE 1.1 — 56,6; Toolathlon Verified — 72,5. Независимый DeepSWE дал 57 ± 3. https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B
- Qwen3.8-Flash-Next: DeepSWE 1.1 — 58,7; SWE-bench Pro — 62,5; SWE-bench Multilingual — 81,0; Toolathlon Verified — 73,5. В той же таблице у Qwen3.7-Plus DeepSWE 16,5 и SWE-bench Pro 55,8. https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- Qwen3.8-27B: Terminal-Bench 2.1 — 73,0; SWE-bench Pro — 61,7; DeepSWE — 42,2. https://huggingface.co/Qwen/Qwen3.8-27B

### GLM (Zhipu, Z.ai)

| Модель | Уровень | Вышла | Цена: вход / кеш / выход | Контекст | Веса |
|---|---|---|---|---|---|
| GLM-5.3 | сильная | 14.08.2026 (по таблице Terminal-Bench) | 1,4 / 0,26 / 4,4 | 1 млн (по AA) | открыты, лицензия glm-5.3; 753 млрд параметров |
| GLM-5.3-Flash | средняя и дешёвая | 26.08.2026 (там же) | 0,15 / 0,03 / 0,50 | 1 млн (по AA) | открыты, MIT; 320 млрд, 18 млрд активных |
| GLM-5.3-FlashX | не оценивала | не нашла | 0,37 / 0,075 / 1,25 | не нашла | не нашла |

Цены: https://docs.z.ai/guides/overview/pricing (19.10.2026). Карточки: https://huggingface.co/zai-org/GLM-5.3, https://huggingface.co/zai-org/GLM-5.3-Flash

Лицензия GLM-5.3: разрешено использовать, разворачивать и дообучать, в том числе в коммерческих целях. Только компании, которая продаёт модель как сервис и получает больше $10 млрд в год, нужна проверка безопасности Z.ai. https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE

Заявлено Z.ai [произв.]: GLM-5.3 — Terminal-Bench 2.1 88,2; Terminal-Bench 3.0 28,3; DeepSWE v1.1 66,9 (mini-swe-agent); Toolathlon Verified 73,0; AutomationBench 48,2. Независимые: DeepSWE 69 ± 3, Terminal-Bench 4.0 41,8 ± 3,2. Таблица GLM-5.3-Flash дана картинкой, цифры не извлекала.

### MiniMax

| Модель | Уровень | Вышла | Цена: вход / кеш / выход | Контекст | Веса |
|---|---|---|---|---|---|
| MiniMax-M3 | средняя или дешёвая | около 01.06.2026 (пресса); техотчёт arXiv 2606.13392 | до 512 тыс. токенов: 0,30 / 0,06 / 1,20 (постоянная скидка 50% от 0,60 / 0,12 / 2,40); больше 512 тыс.: 0,60 / 0,12 / 2,40 | 1 млн | открыты, лицензия minimax-community; 428 млрд, 23 млрд активных |
| MiniMax-M2.7 | старая | апрель 2026 (HF) | 0,3 / 0,06 / 1,2 | не проверяла | открыты |

Цены: https://platform.minimax.io/docs/pricing/overview (19.10.2026). Карточка: https://huggingface.co/MiniMaxAI/MiniMax-M3

Лицензия M3: некоммерческое использование свободно. Для коммерческого нужна надпись «Built with MiniMax M3» и разовое уведомление MiniMax по почте. При выручке больше $20 млн в год нужно отдельное разрешение. Запрещено военное применение. Внутреннее использование отдельно не оговорено, его стоит уточнить у MiniMax. https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/LICENSE

Заявлено MiniMax [произв.]: SWE-bench Verified — 80,5; SWE-bench Pro — 59. Обе цифры отмечены звёздочкой без пояснения. Long-Horizon Terminal Bench 2.0 — 46,9 (агент terminus-2, 3 часа на задачу).

## 4. Оговорки: что сравнимо, а что нет

1. **SWE-bench Verified для этого сравнения не годится.** На официальном лидерборде swebench.com (режим bash-only, mini-SWE-agent) последние записи от 26.02.2026, актуальных моделей там нет. Сами производители перешли на DeepSWE, SWE-bench Pro и Terminal-Bench. Verified сейчас приводит только MiniMax (80,5), и сравнить это число не с чем. https://www.swebench.com/
2. **Из перечисленных тестов кода сопоставим по всем семействам только DeepSWE v1.1.** Там у всех один агент (mini-swe-agent). Заявления производителей по DeepSWE сходятся с независимыми прогонами в пределах погрешности: Kimi K3 67,5 и 69 ± 5, GLM-5.3 66,9 и 69 ± 3, DeepSeek V4-Pro 62,7 и 63 ± 6, Qwen3.8-Max 56,6 и 57 ± 3. Минус DeepSWE: лидерборд обновлён 22.09.2026, моделей новее этой даты в нём нет.
3. **Terminal-Bench 4.0 мерит связку модели и агента.** Claude, GLM и Qwen прогонялись в Claude Code, OpenAI — в Codex, Gemini 3.8 Flash — в mini-SWE-agent. Поэтому 19,1 у Gemini 3.8 Flash, скорее всего, занижено: на DeepSWE у неё 74. В таблицах производителей стоят Terminal-Bench 2.1 (у лидеров около 88%) и 3.0. Это другие наборы задач, с версией 4.0 их не сравнивать.
4. **Уровень рассуждения меняет результат сильнее, чем переход на соседнюю модель.** GPT-6.1 Sol по индексу AA набирает 42 на low и 52 на max; Claude Haiku 5.5 — 29 и 43. Дешёвая роль часто получается из той же модели с низким усилием. В новых открытых семействах «быстрая» модель уже догнала флагман: DeepSeek V4.1-Flash-1017 выше V4-Pro на DeepSWE (по карточкам DeepSeek), Qwen3.8-Flash-Next обходит 3.8-Max на DeepSWE (по заявлению Qwen), GLM-5.3-Flash отстаёт от GLM-5.3 на 3 пункта AA при цене в 9 раз ниже.
5. **Независимый индекс кода ставит Sonnet 5.5 выше Opus 5.5:** 68 против 66 в AA Coding Agent Index. На Terminal-Bench 4.0 и в общем индексе AA впереди Opus (64,8 против 61,8 и 58 против 56). Интервалы на Terminal-Bench пересекаются. Сильную модель в докладе ставили на анализ и итоговую проверку, и это с данными согласуется: на тестах кода разница между Opus и Sonnet небольшая.
6. **Цена за токен не равна цене за задачу.** Sonnet 5.5 на max потратил на задачу индекса кода $14,19, больше Opus 5.5 ($13,04), потому что расходует больше токенов. GPT-6.1 Sol прошёл тот же индекс за $1,55. Сравнивать стоит столбец «$/задача» у AA.
7. **Версии индекса AA разные.** OpenAI в своём анонсе цитирует индекс v4.1.1 (у Astra 61,2), сейчас на сайте v4.3.2 (у Astra на max 53). Числа из разных версий не сравнивать.
8. **У Claude в AA отмечено «with fallback».** При отказе по соображениям безопасности задачу доделывает запасная модель Anthropic. На итоговый балл это влияет.
9. **Таблицы производителей сравнивают с прошлыми версиями конкурентов.** DeepSeek и Moonshot сравниваются с Opus 4.8, Opus 5 и GPT-5.6 Sol, хотя актуальны уже Opus 5.5 и GPT-6. Toolathlon-Verified, BrowseComp и MCP-бенчмарки (MCP-Atlas, MCPMark) я нашла только в отчётах производителей.
10. **Цены временные.** Gemini 4 Argon дорожает вдвое с 01.12.2026, Gemini 3.8 Flash — с 01.01.2027. У MiniMax-M3 «постоянная скидка 50%», у Qwen3.7-Plus временная скидка 20%. DeepSeek берёт вдвое больше в часы пик. На длинном контексте цена растёт: OpenAI — после 272 тыс. токенов входа, Haiku 5.5 — после 100 тыс., MiniMax — после 512 тыс., Qwen3.7-Plus — после 256 тыс.
11. **Открытые веса не значат «легко развернуть».** Kimi K3 — 2,8 трлн параметров, Qwen3.8-2.4T — 2,4 трлн, DeepSeek V4-Pro — 1,7 трлн, им нужен кластер. Реалистичны для контура GLM-5.3-Flash (18 млрд активных), Qwen3.8-Flash-Next (6 млрд активных), Qwen3.8-27B, MiniMax-M3 (23 млрд активных). Лицензии Modified MIT (Kimi K2.7 Code) и qwen-community-1.0 (Qwen3.8-Flash-Next) я не читала.
12. **Чего не нашла.** LMArena WebDev: страница закрыта проверкой на бота, не открывала. LiveCodeBench: окно задач заканчивается 01.05.2025, актуальных моделей нет. Aider Polyglot: последнее обновление 20.11.2025, актуальных моделей нет. τ²/τ³-bench: актуальные модели есть только у Kimi K3 и Qwen3.8-Max, и только в домене banking_knowledge. Дату выхода Gemini 3.5 Flash-Lite и Claude Haiku 5.5 не нашла.

## 5. Ссылки

Независимые лидерборды:
- Artificial Analysis, общий индекс: https://artificialanalysis.ai/leaderboards/models (проверено 19.10.2026)
- Artificial Analysis, методика v4.3.2: https://artificialanalysis.ai/methodology/intelligence-benchmarking
- Artificial Analysis, индекс агентов для кода v1.5: https://artificialanalysis.ai/agents/coding-agents (проверено 19.10.2026)
- DeepSWE v1.1 (Datacurve): https://deepswe.datacurve.ai/ (обновлено 22.09.2026)
- Terminal-Bench 4.0: https://www.tbench.ai/leaderboard (проверено 19.10.2026)
- τ³-bench, прогоны Sierra: https://github.com/sierra-research/tau2-bench/tree/main/web/leaderboard/public/submissions (04.08.2026); сайт https://taubench.com/
- SWE-bench Verified: https://www.swebench.com/ (последние записи 26.02.2026)
- Aider Polyglot: https://aider.chat/docs/leaderboards/ (обновлено 20.11.2025)
- LiveCodeBench: https://livecodebench.github.io/leaderboard.html (окно задач до 01.05.2025)

Производители и прайсы:
- OpenAI: https://openai.com/index/gpt-6-astra/ (03.09.2026), https://openai.com/index/introducing-gpt-6-sol-and-luna/ (22.09.2026), https://openai.com/index/introducing-gpt-6-1-sol/ (29.09.2026), https://developers.openai.com/api/docs/pricing, https://developers.openai.com/api/docs/models
- Google: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/ (13.10.2026), https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-4-Argon-Model-Card.pdf, https://ai.google.dev/gemini-api/docs/pricing, https://ai.google.dev/gemini-api/docs/models
- DeepSeek: https://api-docs.deepseek.com/quick_start/pricing, https://api-docs.deepseek.com/news/news261017 (17.10.2026), https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813
- Moonshot: https://platform.kimi.ai/docs/pricing/chat, https://huggingface.co/moonshotai/Kimi-K3, https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE, https://huggingface.co/moonshotai/Kimi-K2.7-Code
- Alibaba: https://www.alibabacloud.com/help/en/model-studio/model-pricing (15.10.2026), https://www.alibabacloud.com/help/en/model-studio/models (10.10.2026), https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B, https://huggingface.co/Qwen/Qwen3.8-Flash-Next, https://huggingface.co/Qwen/Qwen3.8-27B
- Z.ai: https://docs.z.ai/guides/overview/pricing, https://huggingface.co/zai-org/GLM-5.3, https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE, https://huggingface.co/zai-org/GLM-5.3-Flash
- MiniMax: https://platform.minimax.io/docs/pricing/overview, https://huggingface.co/MiniMaxAI/MiniMax-M3, https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/LICENSE
- Anthropic (для сравнения): https://platform.claude.com/docs/en/about-claude/pricing, https://platform.claude.com/docs/en/about-claude/models/overview. Opus 5.5: 4 / 0,20 / 20; Sonnet 5.5: 2 / 0,10 / 10; Haiku 5.5: 0,10 / 0,01 / 0,50 до 100 тыс. токенов в запросе и 0,50 / 0,05 / 2,50 сверх этого; контекст у всех 1 млн, выход до 128 тыс.
