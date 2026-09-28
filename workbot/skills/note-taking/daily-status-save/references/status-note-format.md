# Status Note Format Reference

Spec for the daily status notes saved by `daily-status-save` and consumed by
`daily-status-digest`.

## Frontmatter Fields

All status notes carry these frontmatter fields:

| Field | Value | Used by |
|-------|-------|---------|
| `created` | ISO 8601 with tz offset, e.g. `2026-08-25T15:30:00-04:00` | Digest date scoping |
| `source` | `slack` | Filter for Slack-sourced notes |
| `triggered_by` | The exact trigger phrase, e.g. `"@hermes status"` | Audit trail |
| `author` | Slack sender's display name, e.g. `Jane Smith` | Digest grouping by person |
| `type` | `status` | Digest filter — the primary search signal |
| `content_summary` | One-line summary of the status | Digest quick-scan |

## Body

The body is the verbatim content the team member posted after the trigger phrase.
Preserve wording. Do not summarize unless asked.

## Filename

`YYYY-MM-DD-HHMMSS-status-{author_slug}.md`

- `YYYY-MM-DD` — local date
- `HHMMSS` — local time, zero-padded
- `status` — literal marker so filename search works as a fallback
- `{author_slug}` — lowercase, spaces replaced with hyphens, truncated if long

Example: `2026-08-25-153000-status-jane-smith.md`

## Search Strategy (digest skill)

**Primary:** `search_files` with `target: "content"`, `pattern: "type:\\s*status"`,
`path: SB-Hermes/`, `file_glob: "*.md"`.

This regex matches the `type: status` frontmatter line. Tested and confirmed working
on 4 fake status notes (returned all 4, filenames correct).

**Fallback (if primary returns 0 — indexing lag on newly written files):**
`search_files` with `target: "files"`, `pattern: "status-"`, `path: SB-Hermes/`,
`file_glob: "*.md"`. Then read each candidate's frontmatter to confirm `type: status`.

**Date scoping:** after finding candidate notes, read frontmatter `created` field and
filter by date. For "today", compare against current Eastern date. For "yesterday",
compare against yesterday's Eastern date.

## Digest Output Shape

1. Blockers / help needed (first — most actionable)
2. What everyone's working on
3. Milestones / deadlines

Surfaces `author`, extracts blocker/help/milestone signals from body text.

## Trigger Discrimination

`type: status` notes are ONLY created when a team member posts a status update
(`@hermes status: ...`). The phrase "what's the status of X?" does NOT trigger a save —
that's a query, not a status post. The save skill must not save query messages as status
notes.
