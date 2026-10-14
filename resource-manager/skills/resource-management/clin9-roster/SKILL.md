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

- **Roster changes**: additions, removals, role updates, PTO/availability changes. Triggered by PM (@drighter) directives or standup reports.
- **Capacity tracker updates**: leave, sick, reduced capacity, or overtime requiring capacity recalculation.
- **Capacity reporting**: weekly capacity summaries posted to #clin9-capacity before Sprint Planning.
- **Capacity alerts**: critical resource shortages threatening project deadlines.

## Data files

| File | Path | Purpose |
|------|------|---------|
| `team_profiles.json` | `dashboard/data/team_profiles.json` | Full roster: name, role, org, slack_handle, channels, responsibilities, influence, notes, availability |
| `capacity.json` | `dashboard/data/capacity.json` | Capacity tracker: total hours, utilization %, leave log, task capacity, sprint context |
| `FRADevOps Team - Org Chart.md` | `SB-Hermes/FRADevOps Team - Org Chart.md` | Markdown table — must match active members in JSON |

## Workflow

1. **Receive directive** — PM names who is added/removed/changed
2. **Read relevant files** — `team_profiles.json` and `capacity.json` (roster AND capacity tracker)
3. **Apply roster changes** — add/remove entries; mark departed as `(Departed)` with inactive status
4. **Apply org chart changes** — remove/add rows; update section header counts
5. **Validate** — grep for removed names (should return 0); verify JSON parses; check header count matches listed members
6. **Update capacity tracker** — adjust `capacity.json` for leave/PTO: `total_team_capacity_hours`, `utilization_pct`, `leave_log`

### JSON mutation workflow (for capacity/PTO updates)
When editing `team_profiles.json` or `capacity.json` (capacity tracker, PTO log, leave log, availability blocks):
- **Mutate with Python, not the patch tool.** The patch tool fails on JSON files containing unicode escapes (e.g. `\u2014` em dash in notes) with `JSONDecodeError`. Use `json.load()` + `json.dump()` in a Python script and always re-validate the output parses.
- **Path for native Python on Windows.** When running `python3` through bash (git-bash), a path starting `/c/Users/...` double-escapes to `C:\c\Users\...` and the file is not found. Use the Windows-native path `C:/Users/...` (no leading slash) for `python3 -c` and for running a script file.
- **Write scripts via write_file** to a scratch working dir (e.g. `dashboard/data/update_*.py`) when the change is multi-step; run with `python3 <script>` from the repo root (the git-bash working directory is `C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian`).
- **Validate after every write** of a JSON file: `python3 -c "import json; json.load(open('dashboard/data/capacity.json')); print('OK')"` and the same for `team_profiles.json`.
- **Re-read before every patch — the tracker files are externally synced.** `capacity.json` and `team_profiles.json` are rewritten by the dashboard sync process between agent reads. A patch attempt may return 'modified since last read' because the file already contains new changes (e.g., separate leave entries added by another process). Re-read the file, then patch again with the CURRENT content. Never assume a failed patch means your change was lost — check the file state first.

- **Markdown reports can also be externally modified.** The weekly capacity summary (`2026-10-14-clin9-capacity-summary.md`) may receive new sections from other agents or updates between your reads. Re-read before patching and confirm the section you intend to edit exists exactly as expected.

7. **Update memory** — record what changed
8. **Post capacity summary** — write to Obsidian vault (`2026-10-14-clin9-capacity-summary.md` pattern)
9. **Confirm in Slack** — summarize changes and capacity impact in #clin9-capacity

## Capacity & Availability Updates

When a team member reports OOO, reduced capacity, or sick leave:

1. **Record in `team_profiles.json`** — append leave/PTO event to the affected member's `availability` field (status, dates, return date, affected tasks)
2. **Update `capacity.json`** — adjust `total_team_capacity_hours` and `utilization_pct`; add entry to `leave_log` with affected tasks and sprint impact; flag members exceeding 85% allocation
3. **Assess task-level impact** — single-BA tasks (Tasks 3, 4, 5 all depend on Melissa) are at risk when a BA is reduced
4. **Identify backup** — cross-functional team members who can absorb work (e.g., Amivi Seddoh for BA support)
5. **Flag to @drighter** if the reduction threatens a sprint deadline
6. **Post capacity summary** — write a markdown file to the Obsidian vault covering leave impact, capacity numbers, and risk items

### Format for capacity reports

- **Obsidian vault**: Markdown tables for rosters and capacity forecasts
- **Slack (channel posts)**: bullet lists or labeled lines — tables are NOT supported in Slack
- **Lead with numbers**: total hours available, utilization %, per-task allocation, skill coverage gaps
- **Objective tone**: describe allocation patterns, not people's work ethic
- **Always include**: who is allocated, to what tasks, at what percentage, and whether they have capacity for more

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

## Weekly Capacity Summary Protocol

Before Sprint Planning, post a capacity summary to #clin9-capacity:

1. **Total team capacity** — available hours for the sprint (after PTO/holiday deductions)
2. **Per-team-member allocation** — who is on what task, at what percentage, and remaining capacity
3. **Utilization heatmap** — per-task utilization percentages across the 7 CLIN9 tasks
4. **Leave/holiday impact** — capacity reduction for upcoming sprint windows
5. **Skill coverage gaps** — where cross-functional capabilities are thin or missing
6. **Tag relevant stakeholders** — @Scrum_Master (Carl) and relevant task managers (e.g., @drighter for PM oversight)

## Alert Protocol

If a critical resource shortage threatens a project deadline:

1. **Alert #clin9-management** — post a clear, data-driven risk to the management channel
2. **Tag @drighter** — the PM must see the bottleneck directly
3. **Include**: affected task(s), member(s) at risk, remaining capacity, and proposed workarounds (if any)
4. **Do not assign tasks** — alerts identify problems; task assignment remains @Scrum_Master's (@carl) and @drighter's job

## Pitfalls

- **Two files must stay in sync** — roster changes need BOTH team_profiles.json AND org chart updates; mismatched counts are a silent failure
- **JSON schema uses `role`** — not `title`; keep field names consistent
- **Validate after write** — `python3 -c "import json; json.load(open('team_profiles.json'))"`; `python3 -c "import json; json.load(open('capacity.json'))"`; grep removed names to confirm
- **Headcount in org chart header** — e.g. `CLIN9 *(15 people)*` must equal actual listed active members
- **Don't assign tasks** — roster changes only; task assignment is @carl's job
- **Capacity watch** — removing a member from a small team (e.g. TTC with 4 people) may create a bottleneck; flag to @drighter
- **Capacity updates go in BOTH team_profiles.json AND capacity.json** — the capacity tracker is a separate file (`capacity.json`), not just the notes field; keep both in sync
- **Solar dates/leave logs must include SLA-holiday overlap** — when leave spans a sprint, account for federal holidays (e.g., Oct 12, 2026) in remaining-day calculations
- **Data files live in the Obsidian vault, not the Hermes profile dir** — the roster and capacity JSONs live at `C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes\dashboard\data\`; checking the Hermes profile `data/` folder returns nothing. Verify the vault path before reading.

- **Slack vs. Vault formatting** — Markdown tables render in Obsidian but are NOT supported in Slack; use bullet lists or labeled lines for Slack posts
- **JSON mutation via Python, not patch** — the patch tool fails on JSON files containing unicode escapes (e.g. `\\u2014` em dash in notes) with `JSONDecodeError`. Mutate with `json.load()` + `json.dump()` in a Python script, then re-validate that the file parses.
- **Windows native Python path** — when running `python3` through bash (git-bash), a path starting `/c/Users/...` double-escapes to `C:\\c\\Users\\...` and the file is not found. Use the Windows-native path `C:/Users/...` (no leading slash) for `python3 -c` and for running a script file.
- **Validate JSON after every write** — always re-run `python3 -c \"import json; json.load(open('dashboard/data/capacity.json'))\"` (and `team_profiles.json`) before reporting success; a syntax error breaks the dashboard silently.
- **Alert before acting** — if a critical shortage emerges, alert #clin9-management and tag @drighter first; do not unilaterally reassign team members
- **Agent-to-Slack constraint** — the agent has no Slack-post API, so the vault file is the authoritative record; the human posts the summary into #clin9-capacity

## Weekly Capacity Summary Protocol