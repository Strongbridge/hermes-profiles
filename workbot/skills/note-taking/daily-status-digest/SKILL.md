# Daily Status Digest Skill

Aggregates team status updates saved in the SB-Hermes vault into a readable daily digest.
Reads status notes, groups by author, and surfaces blockers + help-needed items first.

## When to Use

Use when the Hermes agent is asked (in Slack, addressed) to summarize the day's team status.
Typical triggers:

- `@hermes what's the status for the team today`
- `@hermes daily digest`
- `@hermes status summary`
- `@hermes what is everyone working on`
- `@hermes team status`
- `@hermes where are we on the status notes`

The agent must be addressed (`@hermes`, `@hermes Agent`); ambient requests are not treated
as digest requests.

## Trigger Signals

- "status" + "today" / "summary" / "digest" / "everyone" / "team"
- "what's the status" / "where are we" / "how is the team doing"
- "give me a digest" / "run the status digest"

A message counts as a digest request when it is both addressed to the agent and asks for a
summary of saved status notes. Purely conversational messages ("how are you?") are not digests.

## Query Behavior

When a digest is recognized, the agent:

1. **Extracts the query intent** — identify whether the user wants today's status only, a
   date range, or all status notes. If no date is specified, default to today (notes created
   today). If a date is mentioned ("yesterday", "this week"), scope accordingly.

2. **Searches the SB-Hermes vault for status notes** — use `search_files` with:
   - `target: "content"`
   - `path`: `C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes`
   - `file_glob: "*.md"`
   - `pattern`: `type:\s*status` (matches frontmatter `type: status`) OR a broader search
     for `status` across filenames.

   If searching by content for frontmatter is unreliable, fall back to searching filenames
   for `status-` and reading those notes' frontmatter to confirm they are status notes.

3. **Filters by date** — for "today" or date-scoped digests, filter by the `created` frontmatter
   field. Compare against the current date (Eastern time). For "all status", include all.

4. **Reads matching notes** — for each status note hit, read the full note (frontmatter + body).
   The key fields are `author`, `content_summary`, and the body content. Extract:
   - What the person is working on
   - Blockers (look for "blocker", "blocked", "stuck", "waiting on")
   - Help needed (look for "help", "need help", "can you help", "need from")
   - Milestones (look for "milestone", "due", "by Friday", "deadline", "target")

5. **Groups by author** — organize the digest by person (author field). If multiple status
   notes exist for the same person today, show the most recent one and note if there are
   multiple.

6. **Synthesize the digest** — compose a readable summary. Rules:
   - Start with blockers and help-needed items (these are the most actionable).
   - Then show what each person is working on.
   - Then show milestones / deadlines.
   - If a person has no blockers, say so briefly.
   - If a person posted multiple status notes, show the latest and note there are updates.
   - If no status notes exist for the requested period, say so.

7. **Cites sources** — in the Slack reply, list the filenames of the notes that informed the
   digest (e.g. `Sources: 2026-08-25-153000-status-jane-smith.md, 2026-08-25-153100-status-mike-jones.md`).

## Digest Format in Slack

The reply format:

```
## Team Status Digest — {date}

### Blockers / Help Needed
- **Jane Smith**: Blocked on API key from IT. Needs help getting it.
- **Mike Jones**: Waiting on design review before proceeding.

### What Everyone's Working On
- **Jane Smith**: FRA pipeline integration.
- **Mike Jones**: SharePoint migration, on track.
- **Tess**: WireGuard client provisioning for Dan.

### Milestones / Deadlines
- **Jane Smith**: Complete API integration by Friday.
- **Tess**: All clients provisioned — done.

Sources: 2026-08-25-153000-status-jane-smith.md, 2026-08-25-153100-status-mike-jones.md,
         2026-08-25-153200-status-tess.md
```

If no status notes exist:
```
No status notes in the vault for {date}. No one has posted status today.
```

## Date Scoping

| Query | Scope |
|-------|-------|
| "today" / "current status" / no date | Notes with `created` today (Eastern time) |
| "yesterday" | Notes with `created` yesterday (Eastern time) |
| "this week" | Notes with `created` in the current week (Mon-Sun) |
| "all" / "ever" / no time constraint | All status notes in the vault |

## Search Strategy Notes

Status notes have frontmatter `type: status`. The digest skill should search for these.
If `search_files` with `pattern: "type:\\s*status"` does not return results reliably,
fall back to filename search (`status-` in filename) and read each candidate's frontmatter
to confirm it's a status note (check `type: status`).

## What Not to Do

- Do not fabricate status information not present in saved notes.
- Do not return raw note dumps unless asked — keep it readable in Slack.
- Do not attribute a status to the wrong person — use the `author` frontmatter field.
- Do not summarize multiple notes for the same person as one when they are clearly different
  updates — show the latest and note there are earlier entries.

## Example Exchange

**User (Slack):**
```
@hermes what's the team status today
```

**Agent:**
1. Searches SB-Hermes for `type: status` notes created today
2. Reads matching notes (Jane Smith, Mike Jones, Tess)
3. Groups by author, surfaces blockers first
4. Returns digest as shown above

**User (Slack):**
```
@hermes status for yesterday
```

**Agent:**
1. Searches for `type: status` notes with `created` yesterday
2. Returns digest scoped to yesterday
