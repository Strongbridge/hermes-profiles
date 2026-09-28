# Alias Resolution Checklist — Verify Across ALL Hermes Code Paths

When you fix a model alias resolution bug (e.g., `local-ollama` not being dereferenced to `gemma4:e4b`), you must check EVERY Hermes code path that sends model names to the LLM provider. Fixing one path leaves others broken.

## Checklist

### 1. CLI one-shot path (`hermes -z`)
- **File**: `hermes_cli/oneshot.py`
- **What to check**: After `effective_model` is computed from env/config, is there a `DIRECT_ALIASES` lookup?
- **Symptom if missing**: `hermes -z file.txt "prompt"` fails with HTTP 404 `model '<alias>' not found`
- **Fix**: Add alias lookup after effective_model computation (~line 386-405)

### 2. CLI interactive path (`hermes chat -q`)
- **File**: `hermes_cli/cli.py`
- **What to check**: Where `self.model = model or _config_model or _DEFAULT_CONFIG_MODEL` is set, is there a `DIRECT_ALIASES` lookup for `_config_model`?
- **Symptom if missing**: `hermes chat -q "Say hello"` fails with HTTP 404
- **Fix**: Add alias lookup near the model assignment (~line 16280)

### 3. Gateway agent runtime (`gateway/run.py`)
- **File**: `gateway/run.py`, method `_resolve_session_agent_runtime()` (~line 8060-8150)
- **What to check**: After `model = _resolve_gateway_model(user_config)`, is there a `DIRECT_ALIASES` lookup?
- **Symptom if missing**: Slack messages fail with HTTP 404, agent never reaches tool loop, Obsidian save never happens
- **Fix**: Add alias lookup after `_resolve_gateway_model` call (~line 8080)

### 4. Reactive dispatch (`run_agent.py`)
- **File**: `run_agent.py`, reactive turn routing (~line 4023)
- **What to check**: Does the reactive path dereference aliases when it receives `user_config, model, runtime_kwargs` from channel overrides?
- **Symptom if missing**: Messages routed via channel overrides still 404 even after gateway/run.py is fixed
- **Fix**: Check and patch the reactive dispatch model resolution

### 5. Verify all paths

After patching all applicable paths:

```bash
# CLI paths
hermes chat -q "Say hello in one word."         # Should get response, not 404
hermes -z test.txt "Summarize this"              # Should get response, not 404

# Direct curl (sanity check Ollama is working)
curl -s -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma4:e4b","messages":[{"role":"user","content":"Say hello"}],"max_tokens":5}'

# Gateway path — send a Slack message and check logs
# Check gateway.log for: model=gemma4:e4b (NOT model=local-ollama)
# Check gateway.log for: NO "404 ... not found" errors
```

### 6. Common pitfalls

- **CLI fix ≠ gateway fix**: The CLI and gateway are completely separate code paths. Fixing `cli.py` and `oneshot.py` does NOT fix the gateway. Both must be fixed independently.
- **restart is required**: After patching `gateway/run.py`, the running gateway process still has the old code in memory. You MUST kill and restart the gateway for the patch to take effect.
- **stale PID**: `taskkill /F` may report success without actually killing the process. Verify the new PID in `gateway_state.json` and `ps aux | grep python.*gateway`.
- **`re.search(r"[/:]", model)` guard**: Only apply alias lookup when the model name has no `/` or `:` — these indicate a fully-qualified model ID (e.g., `anthropic/claude-sonnet-4` or `gemma4:e4b` itself) that doesn't need dereferencing.
- **`_ensure_direct_aliases()` must be called first**: The `DIRECT_ALIASES` dict is populated lazily. Call `_ms._ensure_direct_aliases()` before accessing `_ms.DIRECT_ALIASES`.

## When to use this checklist

- After fixing an alias 404 error in one Hermes path and wanting to confirm all paths are covered
- When Slack messages still 404 after the CLI paths were already fixed
- When setting up a new Hermes deployment with Ollama + alias configuration
- During debugging of "model not found" errors that persist after apparent fix
