---
name: credential-redaction
trigger: "Use when handling API keys, tokens, or credentials in files, logs, or memory."
description: Redact credentials before storing or committing.
version: 1.0.0
author: dashboard-developer
license: internal
metadata:
  hermes:
    tags: [security, credentials, redaction, devops]
    related_skills: [firebase-deploy]
---

## Rules

- **Real keys never in memory** — use `[REDACTED]` convention in all notes and logs.
- **`.env` files are secret-bearing** — `read_file` refuses to read them; use `terminal` with Python to inspect specific lines instead.
- **Commit-time redaction** — patch `***` placeholders into `.env` before git add; restore real values only at deploy time via envsubst.
- **Never type credentials into chat** — if a token is needed, ask the user to provide it inline; do not echo it back.

## Pattern

```
# Before commit: patch real values to placeholders
patch(old_string='GEMINI_API_KEY=AQ.xxx', new_string='GEMINI_API_KEY=***', path='.env')

# At deploy time: envsubst restores real values from .env
```
