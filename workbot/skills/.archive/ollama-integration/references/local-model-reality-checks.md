# Local Model Reality Checks — 2026-09-04

Benchmark data, provider/geography notes, and Gemini access state captured during a local model selection session on Dan's Windows box (16 GB RAM, Intel Iris Xe, no GPU).

## This machine's profile

- **Hardware:** 16 GB RAM, Intel Iris Xe (no discrete GPU), Windows 11. CPU-only for LLM inference — the iGPU gives negligible speedup.
- **Usable RAM budget for a model:** ~8-12 GB (Windows + Hermes + Ollama server consume ~4-6 GB baseline).

## Benchmark results (CPU-only, 2026-09-04)

All numbers from `ollama generate` API, 2-3 runs each, quick prompt (~150 chars, ~20 tokens) and reasoning prompt (~200 chars, ~250-300 tokens).

| Model | Provider | Size (RAM) | Quick warm TTFB | Quick tok/s | Reasoning tok/s | Comfort |
|---|---|---|---|---|---|---|
| gemma2:2b | Google (US) | 1.6 GB | 0.15-0.28s | 9-12 | 10-12 | Leaves ~14 GB free |
| llama3.2:3b | Meta (US) | 2.0 GB | 0.13-0.25s | 6-9 | 8-10 | Leaves ~14 GB free |
| llama3.1:8b | Meta (US) | 4.9 GB | 0.2s | 5-6 | 5-6 | Leaves ~11 GB free |
| gemma4:e4b | Google (US) | 9.6 GB | 0.4s | 5-8 | ~5 | Near ceiling; TTFB spikes 30-60s cold |
| mistral:7b | Mistral (FR) | 4.4 GB | 0.18s | 5-6 | 5-6 | French — not US; exclude if geography matters |
| gemma4:31b | Google (US) | 19.9 GB | — | — | — | OOM on this machine (confirmed 2026-08-27 + 2026-09-04) |

Cold-start TTFB spikes (30-60s before settling) on gemma4:e4b indicate the model is near the RAM ceiling — the system swaps or starves the CPU to load it.

## Provider/geography filter

When the user constrains by provider origin (e.g. "US-based models only"), filter before pulling:

- **Google (US):** gemma2:2b, gemma2:9b, gemma4:e4b — free, open weights, US-based
- **Meta (US):** llama3.2:3b, llama3.2:11b, llama3.1:8b — free, open weights, US-based
- **Nous Research (US):** nous-hermes-2:7b, Hermes series — free, open weights, US-based
- **Mistral (France):** mistral:7b — NOT US; exclude if geography matters
- **Anthropic (US):** Claude — no local open weights; API paid; free tier via claude.ai web only
- **xAI (US):** Grok — API paid; limited free via X/Twitter app

## Gemini / Google subscription access state

Machine owner has a Google/Gemini subscription through a DOT-governed Google Workspace. As of 2026-09-04:

- **API access blocked organization-wide.** No API key exists on the machine; no `GOOGLE_API_KEY`, no ADC credential, no `credentials.db`, no `application_default_credentials.json`. Gemini API returns 403 without a key.
- **UI-only access exists:** Gemini inside Google Docs, NotebookLM, Gems, chat.google.com — all within Google's tools. No programmatic access.
- Owner's own notes (Obsidian `2026-08-26.md`): "Gemini suite access still blocked by DOT; team continuing to push for Firebase and broader Google AI access."
- **`google-generativeai` Python package NOT installed** on this machine.
- **Implication:** do not promise a zero-RAM Gemini API option until a key actually exists. The path to programmatic Gemini access is through the org (DOT/Strongbridge) getting Firebase/Google AI access approved — not something Hermes can fix locally.

## Pull strategies that worked on this machine

- Small models (~1.6-2 GB): foreground `ollama pull` with `timeout=600` — completes in a few minutes.
- Larger pulls: background `terminal(..., background=true, timeout=900)`, then poll with `curl http://localhost:11434/api/tags`. Ollama's pull process exits 0 even when stalled — real signal is model appearing in `ollama list`.
- Pulls can appear stalled at a percent for a long time — give time before concluding failure.
- gemma2:9b (~5 GB) failed to land on this machine during this session — likely OOM during extraction/validation. Pull lighter models first.

## Practical recommendation tiers

When asked "what should I run on this machine?", give:

1. **Comfortable** (leaves 6+ GB headroom): gemma2:2b, llama3.2:3b, llama3.1:8b
2. **Use with caution** (fits but < 4 GB headroom): gemma4:e4b (close other apps first)
3. **Don't bother** (confirmed OOM): gemma4:31b
4. **Best day-to-day pick:** llama3.1:8b for capability, gemma2:2b or llama3.2:3b for speed
