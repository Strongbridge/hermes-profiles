# "save this:" → Cloud Model Routing Configuration

## Problem
Local small models (gemma4:e4b) fail to reliably follow "save this:" instructions. They produce long text responses with zero tool turns instead of calling `write_file` to save to Obsidian.

## Solution
Route "save this:" messages to a stronger cloud model that has proven it follows the save instruction.

## Configuration: config.yaml channel override

Routes ALL messages from a Slack channel to the cloud model:

```yaml
platforms:
  slack:
    channel_overrides:
      C0BSK6369D0:          # Replace with your channel ID
        provider: nous
        model: upstage/solar-pro4:free
```

Find channel IDs in `~/.hermes/channel_directory.json`.

## Configuration: gateway/run.py "save this:" prefix detection

Routes only "save this:" prefixed messages to the cloud model. Inject after the channel override block in `_resolve_session_agent_runtime()` (~line 8182):

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

## Provider requirement

The `nous` provider requires OAuth credentials in `~/.hermes/auth.json`. Check with:

```bash
# Verify nous provider is configured and active
grep -A5 '"nous"' ~/.hermes/auth.json
grep "active_provider" ~/.hermes/auth.json
```

If `active_provider` is not `nous` or the `nous` entry is missing, the cloud model routing will fail.

## Verification steps

After applying config + patch and restarting the gateway:

1. Send "save this: Test content for routing verification" to the Slack channel
2. Check `gateway.log` for `save-this: route to cloud model` log line
3. Check `gateway.log` for `model=upstage/solar-pro4:free provider=nous` in API calls
4. Check the Obsidian vault for the new file (typically in `SB-Hermes/` subfolder)
5. Check Slack for the confirmation response

## Fallback behavior

If the cloud model routing fails (OAuth not configured, network error, etc.):
- The patch's except block logs a warning: `save-this: failed to resolve cloud runtime, staying on <model>`
- The message stays on the local model (gemma4:e4b)
- The "save this:" may still work but is less reliable

## Alternative model options

If `upstage/solar-pro4:free` via `nous` is not available, other cloud providers that have proven reliable for save commands:

- `openrouter` with any capable model (requires OPENROUTER_API_KEY in .env)
- Any provider with a model known to follow tool-use instructions well

Avoid routing to local Ollama models for save commands — the small models consistently underperform on instruction following for this task.
