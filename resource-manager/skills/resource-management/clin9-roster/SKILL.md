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

## Capacity & Availability Updates

When a team member reports OOO, reduced capacity, or sick leave:

1. **Update `team_profiles.json` notes field** for the affected member with the date, reason, and capacity level
2. **Update `resource_capacity.json`** — adjust `total_team_capacity_hours` and `utilization_pct`; flag members exceeding 85% allocation
3. **Assess task-level impact** — single-BA tasks (Tasks 3, 4, 5 all depend on Melissa) are at risk when a BA is reduced
4. **Identify backup** — cross-functional team members who can absorb work (e.g., Amivi Seddoh for BA support)
5. **Flag to @drighter** if the reduction threatens a sprint deadline

### Example: Reduced BA capacity
- Melissa OOO (pink eye) → Task 5 RSAC user story entry stalls
- Amivi Seddoh (TTC BA) is the backup for RSAC story entry
- If Melissa doesn't recover, pair Amivi on Task 5 and defer Tasks 3/4 requirements work

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
- **Capacity updates go in notes, not a separate file** — append capacity events to the member's `notes` field in `team_profiles.json` rather than creating per-incident files; keep the roster as the single source of truth