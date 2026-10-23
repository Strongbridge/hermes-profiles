---
name: model-connectivity-testing
description: "Test model connectivity and report verbose feedback."
version: 1.0.0
author: technical-writer
tags: [hermes, testing, connectivity, models, feedback]
metadata:
  hermes:
    tags: [hermes, testing, connectivity, models, feedback]
    homepage: https://hermes-agent.nousresearch.com/docs/
---

# Model Connectivity Testing

Test AI model endpoints for connectivity and report verbose, structured feedback. Use when the user asks: "test your models", "test your model connectivity", "are you online", "list your model information", or any request to verify which models/providers are reachable.

## Always-on Rules

1. **Define the fallback chain before testing.** Read `config.yaml` (or `provider_models_cache.json`) to determine the ordered primary → fallback model/provider list. Test in that order; do not test every possible endpoint.
2. **Probe TCP before HTTP.** Resolve the hostname via `socket.getaddrinfo` first. A DNS failure is a configuration/runtime issue; a TCP timeout is a network/firewall issue. Distinguish and report.
3. **Measure real latency.** Record HTTP status code, latency in ms, and the error type (HTTPError, ConnectionRefusedError, URLError, timeout, DNS failure). Report all three.
4. **Never read the credential store directly.** `auth.json` and `.env` are read-restricted (defense-in-depth). Provider tools consume credentials through internal channels. Do not attempt to read or parse these files.
5. **Distinguish config-level from runtime failures.** A 401/403 with "auth header missing" or "invalid_api_key" means credentials are missing/absent — this is a config issue, not a model outage. A 5xx or timeout means the endpoint is down. A 404 on a model page means the model repo is not public or requires HF auth.
6. **Report structured, verbose feedback.** Use a table or bullet list. Include: terminal/time, provider, model, endpoint URL, TCP result, HTTP status, latency, and error detail. No filler, no re-stating the request, no narrating tool calls the user can see.
7. **Do not promise to run the model now.** The user is asking about the agent's own connectivity, not about running a model you don't have credentials for.
8. **Save findings to the Hermes scratch/cache if output is large.** The `execute_code` stdout spill path is `C:\Users\DanRighter\AppData\Local\hermes\profiles\technical-writer\cache\exec\stdout-*.txt`. The browser workspace is `C:\Users\DanRighter\AppData\Local\hermes\profiles\technical-writer\cache\browser-use\workspace\...`. Write large outputs to files, not to the conversation.

## Procedure

1. Read `config.yaml` to extract the fallback model chain (primary + fallbacks).
2. Read `provider_models_cache.json` if available to list known model names per provider.
3. For each endpoint in the fallback chain:
   a. Resolve hostname → get IP and port (socket.getaddrinfo).
   b. Send a minimal chat-completions payload (model name + one-word prompt).
   c. Record: DNS result, TCP result, HTTP status, latency, error detail.
4. If TCP fails, retry once after 5 seconds; if it still fails, classify as DNS/runtime failure (do not conclude endpoint is down without retry).
5. If HTTP fails with 4xx auth error, note that credentials are required but do not mark the endpoint as down.
6. If all endpoints fail, summarize the pattern: DNS failures vs. auth failures vs. timeouts vs. DNS failures.
7. Output the final report in a table: Endpoint | TCP | HTTP | Latency | Status/Error.
8. If the report exceeds the output limit, write it to a file in the Hermes cache and provide the file path.

## Pitfalls

- **Do not hand-read `auth.json`.** It is a Hermes credential store; direct reads are denied (defense-in-depth). This is a config restriction, not an endpoint outage.
- **DNS failure ≠ endpoint down.** `api.nousresearch.com` intermittently fails DNS resolution. Retry before concluding.
- **A 401 on chat-completions is expected when no API key is available.** It does not mean the model is broken.
- **Browser harness daemon permission errors** (WinError 5 on port files under `.config\browser-harness\runtime\`) are a Windows filesystem race condition in the Hermes tooling, not a test-result issue. Do not re-run the browser tool to "fix" the endpoint.
- **Do not save credentials.** Never echo API keys, tokens, or bearer values in reports.
- **Config cache (`provider_models_cache.json`) is authoritative for known models** but does not prove endpoint reachability — test each endpoint to know.

## References

- `references/fallback-chain.md` — annotated fallback chain extracted from config.yaml
- `references/endpoint-test-procedure.md` — ordered endpoint testing procedure with commands
