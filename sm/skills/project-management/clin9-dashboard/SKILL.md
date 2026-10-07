---
name: clin9-dashboard
description: Update the FRA DevOps dashboard via write_status.py
version: 1.0.0
author: Hermes Agent
license: internal
metadata:
  hermes:
    tags: [dashboard, write_status, portfolio, clin9]
    related_skills: []
---

# CLIN9 Dashboard Status Updates

## When to Use

Use whenever you need to post sprint status, task progress, blockers, or notes to the FRA DevOps dashboard via `write_status.py`. Triggered by daily standup updates, blocker resolutions, sprint lifecycle transitions, or any team member reporting a status change.

## Protocol

Always `read_file` the target JSON before writing. Never overwrite without inspecting current state.

### Write command

```
python write_status.py --portfolio <id> --role <role> ...
```

- `--portfolio`: defaults to `clin9`; use `onm`, `cloud_migration`, etc. for other portfolios
- `--role`: `sm`, `pm`, `ba`, or `crs`
- Script lives at `SB-Hermes/dashboard/data/write_status.py`; run from that directory

### SM arguments

| Arg | Valid values |
|-----|-------------|
| `--sprint-status` | `in_progress`, `completed`, `planning`, `not_started`, `paused`, `blocked` |
| `--task-progress` | JSON: `{"<id>": {"status": "<val>", "notes": "..."}}` |
| `--blockers` | JSON array: `[{"task":"<id>","description":"...","severity":"HIGH|MEDIUM|LOW","source":"@handle","date":"YYYY-MM-DD"}]` |

### Task status values (SM)

`on_track`, `at_risk`, `delayed`, `complete`, `pending`, `in_progress`

Format: `<TaskID>:<Status>` in comma-separated string; or full JSON object via `--task-progress`.

### Blocker format

`<SEVERITY>:<TaskID>:<Description>` — semicolon-separated list; empty string if none.

## Pitfalls

- **Read before write.** Always inspect the target JSON first; the script's `load_existing` merges, but you must decide what the current state demands.
- **argparse `%` in help strings crashes.** The `%` character is a format specifier in argparse — use `pct` or spell out instead. Fixed in write_status.py this session.
- **Portfolio routing.** Omit `--portfolio` for clin9; specify explicitly for other portfolios. New portfolios auto-create their subdirectory.
- **Script prerequisite.** `google-cloud-firestore` must be installed and `GOOGLE_APPLICATION_CREDENTIALS` set to the Firebase service account JSON key.