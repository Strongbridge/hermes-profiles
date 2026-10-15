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

- **Roster changes**: additions, removals, role updates, PTO/availability changes, and Performance Improvement Plans (PIP) / disciplinary logging. Triggered by PM (@drighter) directives or standup reports.
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
3. **Check for duplicate/renamed profiles** — cross-reference the roster against the org chart and any human-reported naming discrepancies (e.g. a PM flagging "Amivi Seddoh goes by Anna"). If the same person appears under two names, consolidate into ONE profile: `name` = the preferred name, `legal_name` = the legal name, and `alias` = "Legal Name (goes by Preferred)". Update the JSON, the Obsidian roster, the org chart, and any capacity/skill-coverage references before posting. Verify with grep that only one active row/card remains.
4. **Apply roster changes** — add/remove entries; mark departed as `(Departed)` with inactive status
5. **Apply org chart changes** — remove/add rows; update section header counts
6. **Validate** — grep for removed names (should return 0); verify JSON parses; check header count matches listed members
7. **Update capacity tracker** — adjust `capacity.json` for leave/PTO: `total_team_capacity_hours`, `utilization_pct`, `leave_log`

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
2. **Verify the PTO date before recording** — confirm the weekday (e.g., `datetime.date(2027,3,18).strftime('%A')`) and check that no federal holiday falls on it; record `day_of_week` and `hours_lost` per date (8h for a standard day, 4h for a half-day, less for part-day). Never assume 8h without checking.
3. **Update `capacity.json`** — adjust `total_team_capacity_hours` and `utilization_pct`; add an entry to `leave_log` with affected tasks, sprint impact, and per-date hours; flag members exceeding 85% allocation
4. **Assess task-level impact** — single-BA tasks (Tasks 3, 4, 5 all depend on Melissa) are at risk when a BA is reduced
5. **Identify backup** — cross-functional team members who can absorb work (e.g., Amivi Seddoh for BA support)
6. **Flag to @drighter** if the reduction threatens a sprint deadline
7. **Post capacity summary** — write a markdown file to the Obsidian vault covering leave impact, capacity numbers, and risk items
8. **Flag missing CLIN9 task mapping** — if the member has no current task allocation in `capacity.json` (e.g., O&M staff with no assignment), state in `sprint_impact` that the task is 'unmapped / confirm assignment,' and note the data gap in `availability_notes`. Do not guess hours lost against a task you cannot attribute. Ask the relevant task managers to confirm the sprint assignment before recomputing capacity.

### Performance Improvement Plan (PIP) & Disciplinary Updates

When updating a team member with a PIP or formal performance notice:

1. **Fallback for Slack attachments**: If reading a Slack attachment fails with HTTP 403, search local directories (`OneDrive`, `Downloads`, `Microsoft Teams Chat Files`) with `search_files` for the PDF/file name and parse text layer directly via `read_file`.
2. **Record in `team_profiles.json`**:
   - Update `responsibilities` to reflect management review / oversight conditions.
   - Update `notes` with a `⚠️ Active Performance Improvement Plan (PIP)` flag, effective date, supervisor name, key concerns, and mandatory standards.
   - Add structured fields: `performance_status` (e.g., `"Active PIP (effective YYYY-MM-DD)"`) and `pip_details` dict containing `effective_date`, `supervisor`, `review_level`, `reasons`, `expectations`, and `consequences`.
3. **Update `team-profiles.md`**: Update the person's row in the roster markdown table with `⚠️ **Active PIP (Date)**` and summary of conditions.
4. **Archive in Obsidian Vault**: Create a dedicated record in `O&M/Personnel/` or `Personnel/` (e.g., `PIP Notice - <Name>.md`) containing full document text, background context, review requirements, and disciplinary escalation levels.

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

- **Slack attachment 403 fallback** — when Slack file download returns 403, search local synced folders (`Downloads`, `Microsoft Teams Chat Files`, `OneDrive`) for the file by name rather than halting.
- **Name discrepancies must be merged across all data sources** — when the PM flags that two entries are the same person (e.g. "Amivi Seddoh goes by Anna"), consolidate into ONE profile: `name` = the preferred name, `legal_name` = the legal name, and `alias` = "Legal Name (goes by Preferred)". Update the JSON, the Obsidian roster, the org chart, and any capacity/skill-coverage references before posting. Verify with grep that only one active row/card remains.
- **JSON schema uses `role`** — not `title`; keep field names consistent
- **Validate after write** — `python3 -c "import json; json.load(open('team_profiles.json'))"`; `python3 -c "import json; json.load(open('capacity.json'))"`; grep removed names to confirm
- **Headcount in org chart header** — e.g. `CLIN9 *(15 people)*` must equal actual listed active members
- **Don't assign tasks** — roster changes only; task assignment is @carl's job
- **Capacity watch** — removing a member from a small team (e.g. TTC with 4 people) may create a bottleneck; flag to @drighter
- **Capacity updates go in BOTH team_profiles.json AND capacity.json** — the capacity tracker is a separate file (`capacity.json`), not just the notes field; keep both in sync
- **Verify weekday and holidays before recording PTO** — every leave entry must carry `day_of_week` and `hours_lost`, since capacity math is exact: a standard day = 8h, a federal holiday drops the whole day. E.g., no federal holiday falls in March, so Mar 18, 2027 is a full 8h day. Always check the weekday before logging hours.
- **Data files live in the Obsidian vault, not the Hermes profile dir** — the roster and capacity JSONs live at `C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes\dashboard\data\`; checking the Hermes profile `data/` folder returns nothing. Verify the vault path before reading.

- **Slack vs. Vault formatting** — Markdown tables render in Obsidian but are NOT supported in Slack; use bullet lists or labeled lines for Slack posts
- **JSON mutation via Python, not patch** — the patch tool fails on JSON files containing unicode escapes (e.g. `\\u2014` em dash in notes) with `JSONDecodeError`. Mutate with `json.load()` + `json.dump()` in a Python script, then re-validate that the file parses.
- **Windows native Python path** — when running `python3` through bash (git-bash), a path starting `/c/Users/...` double-escapes to `C:\\c\\Users\\...` and the file is not found. Use the Windows-native path `C:/Users/...` (no leading slash) for `python3 -c` and for running a script file.
- **Validate JSON after every write** — always re-run `python3 -c \"import json; json.load(open('dashboard/data/capacity.json'))\"` (and `team_profiles.json`) before reporting success; a syntax error breaks the dashboard silently.
- **Alert before acting** — if a critical shortage emerges, alert #clin9-management and tag @drighter first; do not unilaterally reassign team members
- **Agent-to-Slack constraint** — the agent has no Slack-post API, so the vault file is the authoritative record; the human posts the summary into #clin9-capacity

## Weekly Capacity Summary Protocol