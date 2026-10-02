---
name: clin9-roster
description: "Manage CLIN9 team roster: add, remove, update members."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Slack, Obsidian, resource-management, roster]
    related_skills: [dashboard-status-sync]
---

# CLIN9 Roster Management

## When to use

Team member changes: additions, removals, role updates, PTO/availability changes. Triggered by PM (@drighter) directives or standup reports.

## Data files

| File | Path | Purpose |
|------|------|---------|
| `team_profiles.json` | `dashboard/data/team_profiles.json` | Full roster: name, role, org, slack_handle, channels, responsibilities, influence, notes |
| `Org Chart` | `FRADevOps Team - Org Chart.md` | Markdown table — must match active members in JSON |

## Workflow

1. **Receive directive** — PM names who is added/removed/changed
2. **Read both files** — `team_profiles.json` and `FRADevOps Team - Org Chart.md`
3. **Apply changes to JSON** — add/remove entries; mark departed as `(Departed)` with inactive status
4. **Apply changes to org chart** — remove/add rows; update section header counts
5. **Validate** — grep for removed names (should return 0); verify JSON parses; check header count matches listed members
6. **Update memory** — record what changed
7. **Confirm in Slack** — summarize changes, flag capacity risks

## Departed member pattern

Keep in JSON but mark inactive:
```json
{
  "name": "Name (Departed)",
  "role": "Role (Former)",
  "organization": "Org",
  "channels": [],
  "responsibilities": "Former role description.",
  "influence": "None — Inactive",
  "notes": "❌ Inactive / Departed."
}
```
Remove from org chart active tables only; update CLIN9 header count.

## Pitfalls

- **Two files must stay in sync** — roster changes need BOTH team_profiles.json AND org chart updates; mismatched counts are a silent failure
- **JSON schema uses `role`** — not `title`; keep field names consistent
- **Validate after write** — `python3 -c "import json; json.load(open('team_profiles.json'))"`; grep removed names to confirm
- **Headcount in org chart header** — e.g. `CLIN9 *(15 people)*` must equal actual listed active members
- **Don't assign tasks** — roster changes only; task assignment is @carl's job
- **Capacity watch** — removing a member from a small team (e.g. TTC with 4 people) may create a bottleneck; flag to @drighter