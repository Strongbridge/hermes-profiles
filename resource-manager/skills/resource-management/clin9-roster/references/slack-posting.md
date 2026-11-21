# Slack Posting Reference

## Tool schema

The bot posts to Slack via `connectors__slack__SEND_MESSAGE`, a hosted Slack connector.

Exactly one visible content mode:
- `markdown_text` — normal LLM prose. Standard Markdown (headings, bold, lists, code, links, blockquotes). Supports Slack native markdown. **Do NOT use Markdown tables** — tables are not supported in Slack.
- `blocks` — raw Slack Block Kit JSON (array of blocks). Use for buttons, selectors, checkboxes, interactive workflow payloads, section accessories, image/video blocks, context rows, two-column fields, and multiple action buttons in one row.

Required:
- `channel` — channel ID or name, NO leading `#` (e.g. `C0C4FMUL3SS`, not `#clin9-capacity`).

Optional:
- `fallback_text` — only with `blocks`. Maps to Slack's top-level `text` fallback.
- `thread_ts` — timestamp of a parent message to make this a threaded reply.
- `unfurl_links` — defaults `false` for bots, `true` if `as_user` is `true`.
- `unfurl_media` — defaults `true`.
- `reply_broadcast` — if `true` for a threaded reply, also posts to main channel.

## Channel IDs

| Channel | ID |
|---|---|
| `#clin9-capacity` | `C0C4FMUL3SS` |
| `#devops-team` | `C0C4APQ8EJ1` |
| `#clin9-management` | `C0C2K6CMCN6` |
| `#clin9-standup` | `C0C2HAS5M8W` |
| `#clin9-requirements` | `C0C2HAGS2QN` |
| `#clin9-blockers` | `C0C2NUQ1T6G` |

## Authorization flow (always re-run per session)

1. `manage_connections` action=status (target `slack`) → must show `connected:true`.
2. If `connected:false`, run `manage_connections` action=connect (target `slack`) → returns a `connect_url`.
3. Present the `connect_url` to the user and wait for them to open it in a browser and authorize. Do NOT post to Slack until this completes.
4. Re-check `manage_connections` action=status → `connected:true` before posting.
5. Post using `connectors__slack__SEND_MESSAGE`.

## Formatting rules

- Slack posts: bullet/labeled lines only. NO Markdown tables.
- Vault files (`.md` in Obsidian): Markdown tables ARE supported.
- Lead with numbers: total hours available, utilization %, per-task allocation, skill coverage gaps.
- Objective tone: describe allocation patterns, not people's work ethic.
- Always include: who is allocated, to what tasks, at what percentage, and remaining capacity.
