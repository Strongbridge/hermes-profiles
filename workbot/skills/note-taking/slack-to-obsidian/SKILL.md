---
name: slack-to-obsidian
description: Save Slack messages to Obsidian vault on @hermes save.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Slack, Obsidian, note-taking, vault]
    related_skills: [obsidian]
---

# Slack → Obsidian Save Skill

## When to Use

Use when a Slack message addressed to the Hermes agent contains `save this`, `add to obsidian`, or `remember` and you want the content saved as a note in the local Obsidian vault. The agent must be addressed (e.g. `@hermes`, `@hermes Agent`); ambient trigger phrases in unaddressed messages are ignored.

## Trigger Patterns

The skill activates when a Slack message **addressed to the Hermes agent** contains any of these phrases:

- `save this`
- `add to obsidian`
- `remember`

The agent mention can be `@hermes`, `@hermes Agent`, or any variation that routes to the agent. The trigger phrase can appear anywhere in the message.

**Examples:**
- `@hermes Agent save this: deployment checklist for the FRA pipeline`
- `remember that the federal team prefers async updates over calls`
- `add to obsidian: Q3 review notes — 40 apps, 300 SharePoint sites, .NET/React/Angular`

## Response Behavior

When triggered, the agent:

1. **Identifies the sender** — capture the Slack sender's display name or user identity (whatever the agent channel exposes, e.g. `Jane Smith` or `@jane`). If sender info is not available, use `author: "unknown"`.

2. **Extracts the content** — everything after the trigger phrase. If the message is just `@hermes save this` with no content, ask for the content before saving.

3. **Resolves the save path** — the active Obsidian vault on this system is `SB-Hermes/` (it contains `.obsidian/`). Files saved outside `SB-Hermes/` will not be visible in Obsidian. The save target base path is:
   ```
   C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes
   ```
   Do not use the parent `Documents/Obsidian/` path for saves — notes written there are invisible to Obsidian.

4. **Creates the note** — one file per message, written directly into `SB-Hermes/`. The folder already exists and is the active Obsidian vault. No subfolder is created unless the user asks.

5. **Names the file** — `YYYY-MM-DD-HHMMSS.md` (local time, zero-padded). Add a short slug from the content if the message is long enough to derive one meaningfully (e.g. `2026-08-25-143000-federal-team-preferences.md`). When in doubt, use the timestamp only.

6. **Writes frontmatter** — every note starts with YAML frontmatter:

   ```yaml
   ---
   created: 2026-08-25T14:30:00-04:00
   source: slack
   triggered_by: "@hermes Agent save this"
   author: "Jane Smith"
   content_summary: "Deployment checklist for the FRA pipeline"
   ---
   ```

   Fields:
   - `created` — ISO 8601 with timezone offset (Eastern time for this system)
   - `source` — always `slack`
   - `triggered_by` — the exact trigger phrase used
   - `author` — the Slack sender's display name or user identity (e.g. `Jane Smith`, `@jane`). If sender info is not available, use `"unknown"`.
   - `content_summary` — a one-line summary of what was saved (first sentence or a distilled version of the content)

7. **Writes the body** — the full content the user provided, as markdown, after the frontmatter. Preserve the user's wording. Do not summarize or rewrite unless the user asks.

8. **Confirms the save** — reply in Slack: `Saved to Obsidian: YYYY-MM-DD-HHMMSS.md` (with the actual filename). If a slug was added, include it.

## Folder Structure

```
SB-Hermes/ (active Obsidian vault root)
├── 2026-08-25-143000.md
├── 2026-08-25-143000-federal-team-preferences.md
├── 2026-08-26-091500.md
└── ...
```

Notes are saved directly into `SB-Hermes/`. Do not nest further unless the user asks.

## Linking to Earlier Notes

When a save request includes a reference to an earlier note — phrases like:
- "link it to the note from yesterday"
- "connect this to the FRA pipeline note"
- "relate this to what I saved about the federal team"
- "link to the note about [topic]"

The agent:

1. **Reads the reference** — identify what the user is pointing to. It may be a date ("yesterday", "last week"), a topic ("the FRA pipeline note"), or a summary ("what I saved about SharePoint").

2. **Searches existing notes** — search the `SB-Hermes/` vault for notes whose content or filename matches the reference. Use `search_files` with `target: "content"` and `file_glob: "*.md"` scoped to the `SB-Hermes/` path, or read notes by filename if the user was specific.

3. **Adds a wikilink** — in the new note's body, add a line like:
   ```markdown
   Related: [[2026-08-24-160000-fra-pipeline-checklist]]
   ```
   Use the actual filename of the matched note. If multiple notes match, pick the most relevant and mention the others if useful.

4. **If no match is found** — tell the user in Slack: "I didn't find a matching note for '[reference]'. Saved your content anyway." Do not invent a link.

## When the agent fails before saving

If the Hermes agent itself fails (transient model error, 404, timeout) before it can execute the save tool, the message IS still persisted — the gateway saves it to its local `state.db` (SQLite sessions database at `C:\Users\DanRighter\AppData\Local\hermes\state.db`) before falling back. In that case:

1. **Check the gateway logs** — `gateway.log` will show `Transient agent failure in session <session_key> — persisting user message so conversation context is preserved on retry`. The user's message is preserved in the session transcript.
2. **Retrieve from state.db** — query the `messages` table for the session key. The message content is in the `content` column. Example:
   ```python
   import sqlite3
   db = r'C:\Users\DanRighter\AppData\Local\hermes\state.db'
   conn = sqlite3.connect(db)
   cur = conn.execute(
       "SELECT content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 1",
       (session_key,)
   )
   content = cur.fetchone()[0]
   ```
3. **Save to Obsidian manually** — once retrieved from state.db, create the note in `SB-Hermes/` with the standard frontmatter (see above). Use the gateway log timestamp for the `created` field.
4. **Tell the user** — "The agent hit a transient error so the save didn't auto-execute, but I retrieved your message from the gateway's session store and saved it here: `<filename>`."

This recovery path is common when:
- The gateway's model alias isn't resolved (e.g. `local-ollama` sent to Ollama → 404). See `hermes-ollama-alias-resolution` skill.
- Ollama isn't running or the model isn't loaded.
- The model is OOM or the provider is unreachable.

The gateway's `state.db` is the safety net — user messages survive agent failures there. The save tool just needs a working agent to execute it.

## Example Note

**User message:** `@hermes Agent save this: the federal team on the FRA contract prefers async updates over calls. They respond better to written status in the ticket than a spontaneous meeting request.`

**Resulting note (`2026-08-25-143000-federal-team-preferences.md` in `SB-Hermes/`):**

```yaml
---
created: 2026-08-25T14:30:00-04:00
source: slack
triggered_by: "@hermes Agent save this"
author: "Dan Righter"
content_summary: "Federal team prefers async updates over calls"
---

The federal team on the FRA contract prefers async updates over calls. They respond better to written status in the ticket than a spontaneous meeting request.
```

**Agent reply in Slack:** `Saved to Obsidian: 2026-08-25-143000-federal-team-preferences.md`
