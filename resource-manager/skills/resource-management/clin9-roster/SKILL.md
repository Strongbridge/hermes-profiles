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

- **Roster changes**: additions, removals, role updates, PTO/availability changes, Performance Improvement Plans (PIP) / disciplinary logging, and Annual Merit Increase / Compensation updates. Triggered by PM (@drighter) directives or standup reports.
- **Capacity tracker updates**: leave, sick, reduced capacity, or overtime requiring capacity recalculation.
- **Capacity reporting**: weekly capacity summaries posted to #clin9-capacity before Sprint Planning.
- **Capacity alerts**: critical resource shortages threatening project deadlines.

## Data files

| File | Path | Purpose |
|------|------|---------|
| `team_profiles.json` | `dashboard/data/team_profiles.json` | Full roster: name, role, org, slack_handle, channels, responsibilities, influence, notes, availability |
| `capacity.json` | `dashboard/data/capacity.json` | Capacity tracker: total hours, utilization %, leave log, task capacity, sprint context |
| `team_pto.json` | `dashboard/data/team_pto.json` | Leave/PTO log: `leaves` array of {id, member_name, role, organization, type, start_date, end_date, days, status, coverage, notes} |
| `resource_capacity.json` | `dashboard/data/resource_capacity.json` | Live HTML dashboard status sync: total capacity hours, utilization %, pto_impact, skill_coverage |
| `FRADevOps Team - Org Chart.md` | `SB-Hermes/FRADevOps Team - Org Chart.md` | Markdown table — must match active members in JSON |

## Workflow

1. **Receive directive** — PM names who is added/removed/changed
2. **Read relevant files** — `team_profiles.json` and `capacity.json` (roster AND capacity tracker)
3. **Check for duplicate/renamed profiles** — cross-reference the roster against the org chart and any human-reported naming discrepancies (e.g. a PM flagging "Amivi Seddoh goes by Anna"). If the same person appears under two names, consolidate into ONE profile: `name` = the preferred name, `legal_name` = the legal name, and `alias` = "Legal Name (goes by Preferred)". Update the JSON, the Obsidian roster, the org chart, and any capacity/skill-coverage references before posting. Verify with grep that only one active row/card remains.
4. **Apply roster changes** — add/remove entries; mark departed as `(Departed)` with inactive status
5. **Apply org chart changes** — remove/add rows; update section header counts
6. **Validate** — grep for removed names (should return 0); verify JSON parses; check header count matches listed members
7. **Update capacity tracker** — adjust `capacity.json` for leave/PTO: `total_team_capacity_hours`, `utilization_pct`, `leave_log`

### Firestore Auto-Push (mandatory final step)
EVERY team_profiles.json, capacity.json, team_pto.json, or leave/PTO change MUST end with the Firestore push before you reply. See the **Firestore Auto-Push Protocol** below for the exact commands and the required success format.

8. **Update memory** — record what changed
9. **Post capacity summary** — write to Obsidian vault (`2026-10-14-clin9-capacity-summary.md` pattern)
10. **Confirm in Slack** — summarize changes and capacity impact in #clin9-capacity

### JSON mutation workflow (for capacity/PTO updates)
When editing `team_profiles.json` or `capacity.json` (capacity tracker, PTO log, leave log, availability blocks):
- **Mutate with Python, not the patch tool.** The patch tool fails on JSON files containing unicode escapes (e.g. `\u2014` em dash in notes) with `JSONDecodeError`. Use `json.load()` + `json.dump()` in a Python script and always re-validate the output parses.
- **Path for native Python on Windows.** When running `python3` through bash (git-bash), a path starting `/c/Users/...` double-escapes to `C:\c\Users\...` and the file is not found. Use the Windows-native path `C:/Users/...` (no leading slash) for `python3 -c` and for running a script file.
- **Write scripts via write_file** to a scratch working dir (e.g. `dashboard/data/update_*.py`) when the change is multi-step; run with `python3 <script>` from the repo root (the git-bash working directory is `C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian`).
- **Validate after every write** of a JSON file: `python3 -c "import json; json.load(open('dashboard/data/capacity.json')); print('OK')"` and the same for `team_profiles.json`.
- **Re-read before every patch — the tracker files are externally synced.** `capacity.json` and `team_profiles.json` are rewritten by the dashboard sync process between agent reads. A patch attempt may return 'modified since last read' because the file already contains new changes (e.g., separate leave entries added by another process). Re-read the file, then patch again with the CURRENT content. Never assume a failed patch means your change was lost — check the file state first.

- **Markdown reports can also be externally modified.** The weekly capacity summary (`2026-10-14-clin9-capacity-summary.md`) may receive new sections from other agents or updates between your reads. Re-read before patching and confirm the section you intend to edit exists exactly as expected.

## Capacity & Availability Updates

When a team member reports OOO, reduced capacity, or sick leave:

1. **Record in `team_profiles.json`** — append leave/PTO event to the affected member's `availability` field (status, dates, return date, affected tasks)
2. **Verify the PTO date before recording** — confirm the weekday (e.g., `datetime.date(2027,3,18).strftime('%A')`) and check that no federal holiday falls on it; record `day_of_week` and `hours_lost` per date (8h for a standard day, 4h for a half-day, less for part-day). Never assume 8h without checking.
3. **Update `capacity.json`** — adjust `total_team_capacity_hours` and `utilization_pct`; add an entry to `leave_log` with affected tasks, sprint impact, and per-date hours; flag members exceeding 85% allocation. Then push both trackers to Firestore (mandatory final step):
   `python write_status.py --role rm --json-file "<path/to/team_profiles.json>"`
   `python write_status.py --role capacity --json-file "<path/to/capacity.json>"`

4. **Update `resource_capacity.json`** — sync live dashboard state: ISO timestamp, `total_team_capacity_hours`, `utilization_pct`, `pto_impact`, and `skill_coverage`. Then push:
   `python write_status.py --role rm --json-file "<path/to/team_profiles.json>"`

5. **Assess task-level impact** — single-point-of-failure roles (e.g. Technical Lead Ryan Powell across Tasks 1–7, single BAs across Tasks 3–5) are at risk when reduced
6. **Identify backup** — cross-functional team members who can absorb work (e.g., Amivi Seddoh for BA support)
7. **Flag to @drighter** if the reduction threatens a sprint deadline
8. **Update `team_pto.json`** — append new leave entry to `leaves` array with fields {id, member_name, role, organization, type, start_date, end_date, days, status, coverage, notes}. Then push:
   `python write_status.py --role pto --json-file "<path/to/team_pto.json>"`
9. **Post capacity summary** — write a markdown file to the Obsidian vault covering leave impact, capacity numbers, and risk items

### Firestore Auto-Push Protocol (mandatory final step)
EVERY roster, capacity, or leave/PTO change MUST end with the Firestore push before you reply. Never consider an update complete until `write_status.py` prints the `[write_status] ✅` confirmation line.

1. **Pull the latest `write_status.py`** from the HermesDashboard repo (`git pull origin main`) or run `write_status.py` from the dashboard repo directory (`dashboard/`).
2. **Whenever `team_profiles.json` is modified**, execute:
   `python write_status.py --role rm --json-file "<path/to/team_profiles.json>"`
3. **Whenever `capacity.json` is modified**, execute:
   `python write_status.py --role capacity --json-file "<path/to/capacity.json>"`
4. **Whenever a new leave entry is appended to `team_pto.json` under `leaves`**, execute:
   `python write_status.py --role pto --json-file "<path/to/team_pto.json>"`
5. **Verify each run prints the required success format** (below) before replying. If any step fails or prints a warning, stop and fix before replying.

Required success format (exact), printed by `write_status.py`:
- `[write_status] ✅ rm status updated -> team/members`
- `[write_status] ✅ capacity status updated -> team/capacity`
- `[write_status] ✅ pto status updated -> team/pto`

### Team Calendar Maintenance
A running 'who is in / who is out' artifact is the team's shared capacity-availability layer. When the PM or a human asks to 'update the team calendar,' maintain a calendar artifact (not only the JSON leave-log entries):

1. **Locate an existing calendar artifact first** — search the vault for '*calendar*' / '*Calendar*' files (e.g., `team/Calendar/*.md`). If one exists, append to it; do not create a second calendar per session.
2. **Base entries on the JSON availability fields** — `team_profiles.json` per-member `availability` and `capacity.json` `leave_log` are the source of truth; the markdown calendar is a presentation layer that must stay in sync with them.
3. **Render the calendar as a Markdown table** (Obsidian renders tables; Slack does NOT). For Slack posts, translate the table into bullet lines or labeled lines.
4. **Show the current sprint window** — today's status plus the next 7-14 days, so overlapping leaves are visible (e.g., Ryan Powell's Oct 16 sick leave alongside Melissa Willis's Oct 22/Oct 29-30 PTO).
5. **Flag uncovered roles** — single-point-of-failure roles (e.g., Technical Lead across Tasks 1-7, single BAs across Tasks 3/4/5) are at risk when those members are out.
6. **Write the calendar file** to `team/Calendar/<Project> Team Calendar.md` in the Obsidian vault.
7. **Notify in Slack** — post the calendar's headliner to `#clin9-capacity` (bullet/labeled lines, not tables) and tag relevant stakeholders; if a shortage threatens a deadline, alert `#clin9-management` and tag `@drighter`.

### Performance Improvement Plan (PIP) & Disciplinary Updates

When updating a team member with a PIP or formal performance notice:

1. **Fallback for Slack attachments**: If reading a Slack attachment fails with HTTP 403, search local directories (`OneDrive`, `Downloads`, `Microsoft Teams Chat Files`) with `search_files` for the PDF/file name and parse text layer directly via `read_file`.
2. **Record in `team_profiles.json`**:
   - Update `responsibilities` to reflect management review / oversight conditions.
   - Update `notes` with a `⚠️ Active Performance Improvement Plan (PIP)` flag, effective date, supervisor name, key concerns, and mandatory standards.
   - Add structured fields: `performance_status` (e.g., `"Active PIP (effective YYYY-MM-DD)"`) and `pip_details` dict containing `effective_date`, `supervisor`, `review_level`, `reasons`, `expectations`, and `consequences`.
3. **Update `team-profiles.md`**: Update the person's row in the roster markdown table with `⚠️ **Active PIP (Date)**` and summary of conditions.
4. **Archive in Obsidian Vault**: Create a dedicated record in `O&M/Personnel/` or `Personnel/` (e.g., `PIP Notice - <Name>.md`) containing full document text, background context, review requirements, and disciplinary escalation levels.

### Annual Merit Increases & Performance Review Updates

When the PM (@drighter) or management provides team merit increase data:

1. **Slack Attachment Fallback**: If a Slack file attachment (e.g. `image.png` or spreadsheet) fails with HTTP 403, search local synced directories (`OneDrive`, `Microsoft Teams Chat Files`, `Downloads`, `Pictures\Screenshots`) using `search_files` or a Python script filtering recent mtime and keywords (`Merit`, `Screenshot`, `.xlsx`, `.png`).
2. **Cross-Reference Source Files**: Raw Excel spreadsheets (`Merit 2026 - Dan.xlsx`) may show pre-adjusted Manager Input percentages. Visual schedules or screenshots (`Screenshot...png`) reveal the final pro-rated factor and effective rate. Parse Excel via `read_file` and screenshots via `vision_analyze` to verify all numbers.
3. **Archive in Obsidian Vault**: Save the complete merit increase table (appraisal ratings, manager inputs, pro-rated factors, final rates) to `O&M/Personnel/YYYY-MM-DD-team-merit-increases.md` with standard frontmatter (`type: personnel-compensation`, `status: approved`).
4. **Report in Slack**: Provide a structured summary grouped by performance tier (Exceptional, Strong, Consistent) using bullet lists or labeled lines (no Markdown tables in Slack).

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

## Dashboard sync (RM rolls)

For Resource Manager updates that include team member arrays or candidate data, use the **dashboard's own write_status.py** — the script at `C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/write_status.py` (the dashboard root, not a copy elsewhere in the file system):

```bash
cd "C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard"
python write_status.py --portfolio clin9 --role rm --json-file "data/team_update.json" --tasks "1:pass,2:in_progress,3:in_progress,4:in_progress,5:in_progress,6:in_progress,7:in_progress" --notes "..."
```

**Required flags for every RM dashboard write:**
- `--portfolio clin9` (default portfolio)
- `--role rm`
- `--json-file` pointing to the JSON payload
- `--tasks` MUST map out every single task in the sprint (format: `"1:pass,2:in_progress,3:in_progress,4:in_progress,5:in_progress,6:in_progress,7:in_progress"`)

**Read-before-write:** load `data/team_profiles.json` (and/or `data/capacity.json`) first so you don't lose other data. These files are externally synced and can change between reads. A patch attempt may return 'modified since last read' — check the file state first.

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
- **Spreadsheet vs Pro-rated Visual Schedule** — raw merit spreadsheets often contain unadjusted manager inputs; always check for pro-rated factor visual schedules or screenshots to confirm the actual final effective rate when tenure pro-rating applies.
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
- **Single source of truth for calendar/summary files** — the running team calendar and weekly capacity summary live at ONE canonical location (vault root). Do not mirror the same Markdown summary into both the vault root and `dashboard/data/`; updates will drift apart. `dashboard/data/` holds tracker JSONs and status files; published Markdown summaries live at the vault root.
- **JSON mutation via Python, not patch** — the patch tool fails on JSON files containing unicode escapes (e.g. `\\u2014` em dash in notes) with `JSONDecodeError`. Mutate with `json.load()` + `json.dump()` in a Python script, then re-validate that the file parses.
- **Windows native Python path** — when running `python3` through bash (git-bash), a path starting `/c/Users/...` double-escapes to `C:\\c\\Users\\...` and the file is not found. Use the Windows-native path `C:/Users/...` (no leading slash) for `python3 -c` and for running a script file.
- **Validate JSON after every write** — always re-run `python3 -c \"import json; json.load(open('dashboard/data/capacity.json'))\"` (and `team_profiles.json`) before reporting success; a syntax error breaks the dashboard silently.
- **Alert before acting** — if a critical shortage emerges, alert #clin9-management and tag @drighter first; do not unilaterally reassign team members
- **Agent-to-Slack posting** — the agent CAN post to Slack via `connectors__slack__SEND_MESSAGE` once the Slack connector is authorized (`manage_connections` action=connect). Verify connection status first — `manage_connections` action=status shows `connected:false` until authorized. When authorized, post capacity summaries directly to `#clin9-capacity` using the Slack send_message connector. Channel IDs: `#devops-team` = `C0C4APQ8EJ1`.

## Related Skills

- [[lcq-form-management]] — subcontractor Labor Qualification (Exhibit D) form processing: PDF fetch, extraction, team_profiles.json updates, and Firebase sync
- [[dashboard-status-sync]] — Firestore push protocol

## Weekly Capacity Summary Protocol