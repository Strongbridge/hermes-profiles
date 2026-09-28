---
name: hermes-ollama-alias-resolution
description: Fix Hermes Ollama alias 404 errors
author: Hermes Agent
version: 1.0.0
license: MIT
hermes:
  tags: [ollama, local-model, alias, 404, cpu-inference, config]
  catagory: devops
  updated-at: 2026-08-28
---

# Hermes + Ollama Model Alias Resolution

## Problem
Hermes configured with `model.default: local-ollama`, alias `local-ollama: gemma4:e4b`, `provider: custom`, `base_url: http://localhost:11434/v1`. Direct curl to Ollama works. But `hermes chat -q` sends the alias name `local-ollama` to Ollama → HTTP 404 `model 'local-ollama' not found`. Same for `hermes -z`.

Root cause: when a model comes from `config.yaml` `model.default` (not an explicit `--model` flag), the resolution path through `resolve_runtime_provider` in `main.py` / `cli.py` doesn't dereference direct aliases. It sends the alias name itself to Ollama instead of the real model id.

## Where it breaks

### `gateway/run.py` — `_resolve_session_agent_runtime` (the hidden production gap)

**This is the path that breaks Slack messages in production.** When the Hermes gateway handles a Slack message, it calls `_resolve_session_agent_runtime()` in `gateway/run.py` (around line 8080 in Hermes 0.20.5) to resolve the model for the agent turn. This method does NOT dereference `DIRECT_ALIASES` before returning the model name. If `config.yaml` has `model.default: local-ollama` (an alias), the gateway passes `local-ollama` to Ollama → HTTP 404 `model 'local-ollama' not found`.

**Agent log failure chain (Hermes 0.20.5, 2026-08-31):**
- `agent.model_metadata: Could not detect context length for model 'local-ollama' at http://localhost:11434/v1 — defaulting to 256,000 tokens` — agent probes Ollama for the alias name, Ollama doesn't recognize it
- `OpenAI client created ... model=local-ollama provider=custom base_url=http://localhost:11434/v1` — client built with unresolved alias
- `run_agent: OpenAI client created (chat_completion_stream_request ...) model=local-ollama` — the actual API call is made with the alias
- `API call failed (attempt 3/3) ... model='local-ollama' not found | provider=custom model=local-ollama msgs=2 tokens=~8,330` — Ollama rejects after 3 retries
- `Transient agent failure in session ... persisting user message so conversation context is preserved on retry` — gateway falls back, saves message to state.db, sends 120-char fallback to Slack
- **Obsidian save tool never runs — agent never reaches tool execution loop**

**Fix (patch `gateway/run.py` at `_resolve_session_agent_runtime`, after line `model = _resolve_gateway_model(user_config)`):**

```python
model = _resolve_gateway_model(user_config)
# Resolve config-default model aliases (e.g. local-ollama → gemma4:e4b)
# so custom-endpoint aliases work in the gateway agent runtime too —
# without this, Ollama receives the alias name and 404s (same bug
# fixed earlier in oneshot.py/cli.py for the CLI code paths).
if model and not re.search(r"[/:]", model):
    try:
        from hermes_cli import model_switch as _ms
        _ms._ensure_direct_aliases()
        _direct = _ms.DIRECT_ALIASES.get(model.strip().lower())
        if _direct is not None:
            model = _direct.model
    except Exception:
        pass
```

**Restart required after patch** — the running gateway process (PID from `gateway_state.json`) still has the old code in memory. After patching `gateway/run.py`:
1. Try graceful stop: `curl -s --data-binary message=graceful_stop http://localhost:60604/api/control` (port 60604 = gateway control port). If pipe doesn't respond, fall through to hard kill.
2. Hard kill: `taskkill /F /PID <pid>` or `kill -9 <pid>`.
3. Gateway auto-restarts via launcher. Verify new PID in `gateway_state.json` (`updated_at` newer than patch time) and `ps aux | grep python.*gateway`.
4. Verify fix: send a Slack message; agent logs should show resolved model (e.g. `model=gemma4:e4b`) NOT `model=local-ollama` and NO `404 ... not found` errors.

**Why the gateway didn't restart in this session:** `taskkill /F PID 5880` reported SUCCESS but the process did not die — `gateway_state.json` still showed PID 5880 as "running" with `updated_at` stuck at the pre-kill timestamp. Possible causes: gateway's child process in different PID namespace, or `taskkill` targeted a wrapper. If hard kill fails, the gateway may need launcher restart or system reboot.

**CRITICAL — CLI fix ≠ gateway fix:**
- CLI fix (`cli.py` + `oneshot.py` patches): makes `hermes chat -q` and `hermes -z` work. Verified via `hermes chat -q "Say hello"` → success.
- Gateway fix (`gateway/run.py` patch): makes Slack messages work. Must be deployed separately. Verifying CLI fix is NOT sufficient to confirm Slack works.
- Both paths share the same root cause (alias not dereferenced) but are completely separate code paths. Fix both independently.

## Fix approach

### Step 1: Add alias resolution in `cli.py` for the config-default path
In `cli.py`, where `self.model = model or _config_model or _DEFAULT_CONFIG_MODEL` is set, add a lookup through `DIRECT_ALIASES` (from `model_switch`) when the model matches a known alias name. This ensures `_config_model` (alias name) gets dereferenced to the real id before being used.

Patch location: `cli.py` near the line `self.model = model or _config_model or _DEFAULT_CONFIG_MODEL` (around line 16280 in the full file).

### Step 2: Add alias resolution in `oneshot.py` for the config-default path
In `oneshot.py`, after `effective_model` is computed from env/config, add a `DIRECT_ALIASES` lookup so the config-default path also dereferences aliases — same as the explicit-model path below.

Patch location: `oneshot.py` near the effective_model computation (around line 386-405).

### Step 3: Add alias resolution in `gateway/run.py` for the gateway agent runtime
This is the path that breaks Slack messages in production. `_resolve_session_agent_runtime()` in `gateway/run.py` (around line 8080) does NOT dereference `DIRECT_ALIASES` before returning the model name.

Patch location: `gateway/run.py` in `_resolve_session_agent_runtime()`, after `model = _resolve_gateway_model(user_config)`:

```python
model = _resolve_gateway_model(user_config)
# Resolve config-default model aliases (e.g. local-ollama → gemma4:e4b)
# so custom-endpoint aliases work in the gateway agent runtime too —
# without this, Ollama receives the alias name and 404s (same bug
# fixed earlier in oneshot.py/cli.py for the CLI code paths).
if model and not re.search(r"[/:]", model):
    try:
        from hermes_cli import model_switch as _ms
        _ms._ensure_direct_aliases()
        _direct = _ms.DIRECT_ALIASES.get(model.strip().lower())
        if _direct is not None:
            model = _direct.model
    except Exception:
        pass
```

### Step 4: Also check `run_agent.py` reactive dispatch path
The reactive turn routing in `run_agent.py` (around line 4023) also receives `user_config, model, runtime_kwargs` from channel overrides and may not dereference aliases. If messages still 404 after fixing gateway/run.py, check this path too.

### Step 5: Verify
After patching all applicable files:
1. `hermes chat -q "Say hello in one word."` → should return a response from gemma4:e4b (not 404)
2. `hermes -z test.txt "Summarize this"` → should resolve alias correctly
3. Direct curl test: `curl -s -X POST http://localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"gemma4:e4b","messages":[{"role":"user","content":"Say hello"}],"max_tokens":5,"temperature":0}'` should return `Hi`
4. **Gateway-specific**: send a Slack message; agent logs should show resolved model (e.g. `model=gemma4:e4b`) NOT `model=local-ollama` and NO `404 ... not found` errors.

## "save this:" reliability — route saves to a stronger model

Local small models (e.g., gemma4:e4b) often fail to follow "save this:" instructions reliably — they talk about the content instead of calling `write_file` to save to Obsidian. This produces long text responses with zero tool turns. Route save commands to a stronger cloud model.

### Option A: Channel override in config.yaml (routes ALL messages from a channel)

```yaml
platforms:
  slack:
    channel_overrides:
      C0BSK6369D0:          # Slack channel ID (find in ~/.hermes/channel_directory.json)
        provider: nous
        model: upstage/solar-pro4:free
```

Find your channel ID in `~/.hermes/channel_directory.json`. The `nous` provider requires OAuth credentials in `~/.hermes/auth.json`.

### Option B: "save this:" prefix detection in gateway/run.py (routes only save commands)

Inject after the channel override block in `_resolve_session_agent_runtime()`, around line 8182:

```python
            # Route "save this:" prefix messages to the cloud model when
            # the channel override did not already pick a cloud model.
            if model and runtime_kwargs.get("provider") == "custom":
                _msg_text = ""
                _msg = ctx.message
                if isinstance(_msg, str):
                    _msg_text = _msg
                elif isinstance(_msg, (list, tuple)):
                    for _m in _msg:
                        if isinstance(_m, dict):
                            _msg_text = _m.get("content", "") or _msg_text
                        elif isinstance(_m, str):
                            _msg_text = _m or _msg_text
                elif hasattr(_msg, "content"):
                    _msg_text = str(getattr(_msg, "content", ""))
                else:
                    _msg_text = str(_msg) if _msg else ""
                _msg_text = _msg_text.strip().lower()
                if _msg_text.startswith("save this:"):
                    try:
                        cloud_rt = _resolve_runtime_agent_kwargs_for_provider("nous")
                        model = "upstage/solar-pro4:free"
                        runtime_kwargs = cloud_rt
                        logger.info(
                            "save-this: route to cloud model session=%s model=%s provider=%s",
                            resolved_session_key or "",
                            model,
                            runtime_kwargs.get("provider"),
                        )
                    except Exception:
                        logger.warning(
                            "save-this: failed to resolve cloud runtime, staying on %s",
                            model,
                            exc_info=True,
                        )
```

### Verification after routing fix
1. Send "save this: [content]" to the Slack channel
2. Check `gateway.log` for `save-this: route to cloud model` log line
3. Check `gateway.log` for `model=upstage/solar-pro4:free provider=nous` in the API call
4. Check the Obsidian vault for the new file
5. Check Slack for the confirmation response

## Where it breaks
