# Gemma 4 Variants — Ollama Local Models

Sourced from public Ollama library docs and Gemma 4 launch coverage (Google DeepMind, 2026-04-02, Apache 2.0). Use as a quick model-selection reference before pulling.

## Variant table

| Variant | Ollama tag | On-disk size | Min VRAM/RAM (Q4) | Context | Multimodal | Best for |
|---|---|---|---|---|---|---|
| E2B | `gemma4:e2b` | ~7.2 GB | ~4 GB | 128K | Image in | Phones, Pi 5, low-end laptops |
| E4B (default) | `gemma4` / `gemma4:e4b` | ~9.6 GB | ~6 GB | 128K | Image + audio in | Most developer laptops; 16 GB M-series Macs |
| 26B MoE (A4B) | `gemma4:26b` | ~18 GB | ~16 GB | 256K | Image in | RTX 3090/4080+, 32 GB M-series Macs; consumer-GPU sweet spot |
| 31B Dense | `gemma4:31b` | ~19-20 GB | ~20 GB (24+ practical) | 256K | Image in | RTX 4090, M3/M4 Max with 64 GB; workstation-class quality |
| 12B Unified | `gemma4:12b` | (varies) | (TBD) | 256K | Image + audio in | Added June 2026; long context + native audio |

## Key facts

- Gemma 4 released 2026-04-02 by Google DeepMind under Apache 2.0. All variants available as base and instruction-tuned (IT) checkpoints on Hugging Face under `google/gemma-4-*`.
- E2B: 2.3B effective / 5.1B total. E4B: 4.5B effective / 8B total. Both use MoE; only a small subset of params active per token.
- 26B MoE: 26B total, ~4B activated per token. Runs faster than its on-disk size suggests.
- 31B Dense: full 31B active per token. Highest quality dense option. Best-documented local model with **reliable tool-call support** as of the docs.
- Multimodal: all four original variants take image input; E2B and E4B also take audio. Ollama exposes this via the standard `images` field on `/api/generate`.
- Context: E2B/E4B = 128K; 26B/31B/12B = 256K.
- Gemma 4 31B scores: 89.2% AIME 2026 (math), 80.0% LiveCodeBench v6 (coding), 84.3% GPQA Diamond (science). Gemma 3 scored 20.8% / 29.1% / 42.4% on the same tests.
- Leaderboard: 31B at #3 on LMArena open-model text leaderboard (~1452 ELO); 26B MoE at #6 with only 4B active params.

## Quantization

- For the 31B model, Q4_K_M is the commonly cited sweet spot (~18 GB, good quality).
- Higher quantization (q8_0) = more memory, slightly better quality.
- Lower quantization (q4_K_M already; below that) = less memory, slightly less quality.
- Do not assume the default `ollama pull` quantization is ideal for the target hardware. Pull a specific tag if control matters, e.g. `ollama pull gemma4:26b-q4_K_M`.

## Hermes relevance

- For full agentic work (file edits, terminal commands, web browsing via tool calls), **gemma4:31b** is currently the best-documented local model with reliable tool-call support — but only if the hardware can actually run it.
- If the machine cannot run 31B comfortably, Hermes will talk to the Ollama endpoint fine; generation will fail or crawl at the Ollama layer (OOM, timeout, no response).
- E4B is the safe default for a usable local model on typical developer hardware.

## Sources

- Ollama library / Gemma 4 model pages (ollama.com/library, ollama.com/blog).
- Gemma 4 launch coverage: codersera.com, dev.to, itechguides.com, medium.com (April-June 2026).
- Google DeepMind Gemma 4 release (2026-04-02, Apache 2.0).
