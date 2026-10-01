---
name: daily-status-save
description: Save team status updates to the SB-Hermes vault.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Slack, status, daily, team, Obsidian, note-taking]
    related_skills: [slack-to-obsidian, daily-status-digest]
---

# Daily Status Save Skill

Saves a team member's daily status update to the SB-Hermes vault when posted in Slack.
Each status becomes one dated note with `type: status` frontmatter, grouped by author for
the daily digest skill.

## When to Use

Use when a Slack message addressed to the Hermes agent contains a team member's daily status.
The message must be addressed (`@hermes`, `@hermes Agent`). The trigger signal is the word
`status` (case-insensitive) appearing in an addressed message.

**Examples:**
- `@hermes status: working on the FRA pipeline, blocked on the API key, need help with the VPN config`
- `@hermes Agent status: Tess — finished the wireguard client, no blockers`
- `@hermes daily status: I'm working on the SharePoint migration, no blockers, on track`

## Trigger Patterns

The skill activates when a Slack message **addressed to the Hermes agent** contains `status`
and appears to be a status update (work / blockers / help / milestones).

If the message contains `status` but is not a status update (e.g. "what's the status of the
project?"), do NOT save it. That's a query, not a status post.

## Response Behavior

When triggered, the agent:

1. **Identifies the sender** — capture the Slack sender's display name (e.g. `Jane Smith`).
   This becomes the `author` field. If sender info is not available, use `author: "unknown"`.

2. **Extracts the content** — everything after the trigger phrase. Preserve the user's wording.
   Do not summarize or rewrite unless asked.

3. **Resolves the save path** — save to `SB-Hermes/` (the active Obsidian vault root):
   ```
   C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes
   ```

4. **Creates the note** — one file per status message, written directly into `SB-Hermes/`.
   Filename: `YYYY-MM-DD-HHMMSS-status-{author_slug}.md`
   Example: `2026-08-25-153000-status-jane-smith.md`

5. **Writes frontmatter** — every status note starts with YAML frontmatter:
   ```yaml
   ---
   created: 2026-08-25T14:30:00-04:00
   source: slack
   triggered_by: "@hermes status"
   author: "Jane Smith"
   type: status
   content_summary: "Working on the FRA pipeline, blocked on API key"
   ---
   ```

   Fields:
   - `created` — ISO 8601 with timezone offset (Eastern time)
   - `source` — always `slack`
   - `triggered_by` — the exact trigger phrase used
   - `author` — the Slack sender's display name
   - `type` — always `status` (so the digest skill can filter by it)
   - `content_summary` — a one-line summary (first sentence or distilled version)

6. **Writes the body** — the full content the user provided, as markdown, after the frontmatter.
   Preserve the user's wording.

7. **Confirms the save** — reply in Slack: `Saved status for <author> to YYYY-MM-DD-HHMMSS-status-{slug}.md`

## Status Note Format

Example note (`2026-08-25-153000-status-jane-smith.md`):

```yaml
---
created: 2026-08-25T15:30:00-04:00
source: slack
triggered_by: "@hermes status"
author: "Jane Smith"
type: status
content_summary: "Working on FRA pipeline, blocked on API key"
---

Working on the FRA pipeline. Blocked on the API key — need help getting it from IT.
Major milestone this week: complete the API integration by Friday.
```

## Digest Integration

Status notes are designed to be aggregated by the `daily-status-digest` skill. The key fields
are `type: status` and `author`.

See `references/status-note-format.md` for the full note format specification and the search
pattern the digest skill uses to find these notes.

## What Not to Do

- Do not save messages that are not addressed to the agent.
- Do not save a status update as a generic save — always use `type: status` in frontmatter.
- Do not save without content — ask for it first.
- Do not auto-summarize or rewrite the user's content unless explicitly asked.
- Do not save status notes to any path other than `SB-Hermes/`.
- Do not batch or queue saves — each status message is one note, written immediately.
- Do not treat "what's the status of X?" as a save trigger — that's a query, not a status post.

## Folder Structure

```
SB-Hermes/ (active Obsidian vault root)
├── 2026-08-25-143000-status-jane-smith.md
├── 2026-08-25-143100-status-mike-jones.md
├── 2026-08-25-143200-status-tess.md
```

Status notes sit alongside other saved notes. The `type: status` frontmatter field
distinguishes them from other saved content.

## Example Exchange

**Team member (Slack):**
```
@hermes status: working on the FRA pipeline integration, blocked on the API key from IT,
need help getting it. Major milestone: complete API integration by Friday.
```

**Agent:**
1. Extracts sender: (team member's display name)
2. Saves to `SB-Hermes/2026-08-25-153000-status-{author_slug}.md`
3. Writes frontmatter (`type: status`) + body
4. Replies: `Saved status for <author>: 2026-08-25-153000-status-{slug}.md`

**Team member (Slack):**
```
@hermes daily status: on track, no blockers. SharePoint migration sites 1-12 done.
```

**Agent:**
1. Recognizes `daily status` as a status trigger
2. Saves to `SB-Hermes/2026-08-25-153100-status-{author_slug}.md`
3. Replies: `Saved status for <author>: 2026-08-25-153100-status-{slug}.md`
