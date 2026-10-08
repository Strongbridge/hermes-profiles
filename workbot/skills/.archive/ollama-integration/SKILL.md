---
name: ollama-integration
description: "Install Ollama and pull local models for Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ollama, local-llm, gemma, model-provider, integration]
    related_skills: [hermes-agent]
---

# Ollama Integration

Use this skill when connecting Hermes to a locally running Ollama instance, or when pulling/running local models (especially Google's gemma4 family) through Ollama.

This is **provider configuration + local model reality checks**, not just "how to download Ollama." It complements the generic model-provider docs: this skill carries the Ollama-specific gotchas, the gemma4:31b memory trap, and the command sequence that worked on this machine.

## When to Use

- User wants Hermes to use a local LLM (Ollama) instead of / in addition to a cloud provider.
- User asks to install Ollama.
- User asks to pull a specific local model (gemma4:31b, gemma4:e4b, etc.) and run it.
- User asks "will this model run on my hardware?" for a local Ollama model.
- A previously configured local Ollama provider stops working and needs diagnosis.

## Prerequisites

- Ollama installed and running locally.
- Ollama 0.22+ for Gemma 4 correctness (older builds have known llama.cpp correctness issues with Gemma 4).
- Enough RAM/VRAM for the chosen model (see reality checks below).
- Hermes config edited via `hermes config set` / `hermes config edit`, not hand-edited YAML with a UTF-8 BOM.

## Quick Start

### 1. Install Ollama

**Windows (PowerShell):**
```powershell
irm https://ollama.com/install.ps1 | iex
```
May take a few minutes. On a slow connection it can appear stuck at a progress bar — do not kill it prematurely. Default install path on this machine: `C:\Users\<user>\AppData\Local\Programs\Ollama\ollama.exe`.

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
(or download from https://ollama.com/download).

After install, verify:
```bash
ollama --version
ollama list
```

Note for the Windows bash/terminal layer: `ollama.exe` may not be on PATH in the git-bash layer even after a successful install. Use the full path, e.g. `/c/Users/<user>/AppData/Local/Programs/Ollama/ollama.exe` or `ollama.exe` from a PowerShell window.

### 2. Pull a model

```bash
ollama pull gemma4:31b    # 31B dense — large, ~19-20 GB on disk
ollama pull gemma4:e4b    # E4B — smaller, ~9.6 GB, good general-purpose local model
ollama pull gemma4:26b    # 26B MoE — middle ground, ~18 GB, consumer-GPU sweet spot
ollama pull gemma4        # untagged default; currently maps to gemma4:e4b
```

Watch the pull progress in the terminal. On a slow connection a single pull can take a long time; it is normal for it to look stalled at a percent for a while.

**Reality check before pulling gemma4:31b:**
- This is a 31B dense model. On-disk size is roughly 19-20 GB.
- Inference needs roughly 20+ GB RAM for comfortable run; practical minimum is more like 24 GB.
- On a machine with ~16 GB total RAM and no dedicated GPU (Intel Iris Xe only), gemma4:31b **will likely not run** — it may fail to load, or run so slowly it is unusable.
- If the goal is a *usable local model*, prefer gemma4:e4b or gemma4:26b first, and only pull 31B if there is real GPU/RAM headroom.
- Quantization matters: Q4_K_M is the sweet spot cited for the 31B model. Do not assume the default pull quantization is ideal for the hardware.

For the full variant table (E2B / E4B / 26B MoE / 31B dense / 12B unified), see `references/gemma4-variants.md`.

### 3. Configure Hermes to use the local Ollama provider

A local Ollama provider is "custom" in Hermes terms — set `model.base_url` and optionally `model.api_key`.

```bash
# Point Hermes at the local Ollama OpenAI-compatible endpoint
hermes config set model.provider custom
hermes config set model.base_url "http://localhost:11434/v1"
hermes config set model.api_key "ollama"      # required by the API shape, ignored by Ollama

# Set the default model to whatever you pulled (the model name as Ollama knows it)
hermes config set model.default "gemma4:31b"

# Optional: add a named alias for quick switching in-session (provider is already 'custom',
# base_url is already set, so the alias is just the model name under the 'custom' provider)
hermes config set model.aliases.local-ollama "custom/gemma4:31b"
```

Note: the alias form is `custom/<model-name>`, e.g. `custom/gemma4:31b`. Do **not** write `custom/ollama/gemma4:31b` or a full URL path inside the alias — provider and base_url are already set at the top level, so the alias only needs to name the model. A full URL-like alias will cause Hermes to call the wrong endpoint and return `model '<alias>' not found`.

After config changes:
- CLI: restart the CLI session (exit + relaunch), or run `/reload` to pick up `.env`/config reload where applicable.
- Gateway: `/restart` after config changes.
- In-session model switch: `/model local-ollama` (if you set the alias).

### 4. Verify end-to-end

```bash
# Quick non-interactive test via Hermes CLI with the local toolset
hermes chat -q "Use the local Ollama model to answer: what is 2+2? Keep it short." -t <toolset>
```

Or test the Ollama server directly:
```bash
ollama run gemma4:e4b "what is 2+2?"
curl http://localhost:11434/api/generate -d '{"model":"gemma4:31b","prompt":"hello"}' 2>/dev/null | head
```

If Hermes can call the model but the model fails to generate locally (OOM, timeout, no response), the problem is usually hardware, not the Hermes config. Check Ollama logs and free RAM.

## Gemma 4 Family — Model Selection Guide

Google released Gemma 4 on 2026-04-02 under Apache 2.0. Ollama distributes pre-quantized GGUF variants. Key points:

- **gemma4:e4b** (default untagged `gemma4`): ~9.6 GB on disk, fits most developer laptops. Good general-purpose local model. Multimodal (image in; E2B/E4B also audio in).
- **gemma4:26b**: 26B total, MoE with ~4B active params per token. ~18 GB on disk. Sleeper hit — runs faster than its size suggests. Fits a 24 GB GPU comfortably; good for RTX 3090/4080+, 32 GB M-series Macs.
- **gemma4:31b**: 31B dense, full 31B active per token. ~19-20 GB on disk, ~20+ GB RAM to run, 24+ GB practical minimum. Workstation-class quality. Best local option with **reliable tool-call support** as of the docs, but hardware-hungry.
- **gemma4:e2b**: ~7.2 GB, for phones / Pi 5 / low-end laptops.
- **gemma4:12b** (added June 2026): 256K context, native audio support at the Gemma model level.

For tool-calling / agentic work in Hermes, gemma4:31b is currently the best-documented local model with reliable tool calls — but only if the hardware can actually run it. If it cannot, Hermes will talk to the model endpoint fine but generation will fail or crawl at the Ollama layer.

## Pitfalls

- **Pulling gemma4:31b on a 16 GB machine and expecting it to run.** You can download it fine; you probably cannot run it. Check RAM before pulling large models. Prefer a variant that fits first, then pull the big one only if needed.
- **Assuming the default Ollama quantization is optimal.** It picks something that may fit, but not necessarily the quality/size tradeoff you want. For 31B, Q4_K_M is the commonly cited sweet spot; pull a specific quantization tag if control matters.
- **Hand-editing config.yaml with Notepad on Windows.** That writes a UTF-8 BOM, which produces `HTTP 400 "No models provided"` on first run. Use `hermes config edit` or `hermes config set`, which write correctly. If a BOM got in, re-save as UTF-8 without BOM.
- **Using `ollama` from git-bash on Windows after a successful install and concluding it is broken.** The binary landed; the bash layer just does not have it on PATH. Use the full path or a PowerShell window.
- **Waiting on a stalled-looking pull and killing it.** Ollama pulls can appear stalled at a percent for a long time on slow connections. Give it time before concluding it failed.
- **Config changes mid-session.** Toolset/provider changes take effect on `/reset` (new session), not mid-conversation, to preserve prompt caching. Config changes in the gateway need `/restart`; CLI needs exit + relaunch.
- **Running the desktop app without verifying the backend first.** `hermes desktop --build-only` first is a cheap way to catch build problems before launching the interactive app.

## Verification

- `ollama --version` returns 0.22+ (for Gemma 4 correctness).
- `ollama list` shows the pulled model.
- `hermes config show` reflects `model.provider: custom`, correct `base_url`, and the intended default model.
- A non-interactive Hermes CLI query against the local provider returns a real answer (not a timeout or empty response).
- If generation fails locally, check free RAM and Ollama logs — the failure is usually at the Ollama layer, not the Hermes provider config.

## References

- `references/gemma4-variants.md` — gemma4 variant table, on-disk sizes, RAM/VRAM minima, and multimodal capabilities, sourced from public Ollama/Gemma docs.
- `references/local-model-reality-checks.md` — benchmark data, provider/geography notes, Gemini access state, pull strategies, and recommendation tiers from 2026-09-04 local model benchmarking on this machine.
