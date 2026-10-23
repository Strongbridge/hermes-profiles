---
name: dashboard-status-sync
description: Write bot status updates to the CLIN9 dashboard JSON files so the HTML dashboard stays current.
---

# Dashboard Status Sync

## When to use

You (PM, BA, or SM bot) have assessed project status in Slack and need to persist it to the dashboard JSON file so the HTML dashboard reflects your latest assessment.

## Dashboard data directory

```
C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/data/
```

Always serve the dashboard via HTTP: `python3 -m http.server 8080` from the `dashboard/` directory, then open `http://127.0.0.1:8080/index.html`.

## Your status file

| Bot | File |
|-----|------|
| PM (@project_manager) | `pm_status.json` |
| BA (@business_analyst) | `ba_status.json` |
| SM (@scrum_master) | `sm_status.json` |

## How to write your status

### Correct workflow: read → modify → write → validate

**Never write to a JSON file without reading it first.** The dashboard files are shared across bots — overwriting without reading loses other bots' updates.

1. **Read** the existing file with the read_file tool
2. **Modify** the relevant fields in the parsed JSON
3. **Write** back with write_file (full rewrite) or patch (targeted edit)
4. **Validate** by reading back with read_file — confirm the JSON structure is intact and other bots' fields are preserved
5. **Confirm** in Slack — tell the human the dashboard is updated

Example (PM health update):
1. `read_file pm_status.json` — get current state
2. Update `overall_health`, `health_rationale`, `task_health`, `notes`
3. `write_file` the full updated JSON object
4. `read_file pm_status.json` — verify `overall_health` changed and other fields preserved

**Why not the Python one-liner?** The one-liner reads the file, modifies it in-memory, and writes it back in one shot. If another bot updated the file between your read and write, you overwrite their changes silently. The read→modify→write→validate pattern with explicit tool calls makes every step visible and preserves concurrent updates.

### CLI method (write_status.py)

When using the script directly, the portfolio flag routes updates to the correct tab:

```bash
cd "C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/data"
python write_status.py --portfolio clin9 --role pm --health green \
  --health_rationale "5 of 7 tasks on track; Task 2 unblocked." \
  --task-health '{"1":{"health":"pass","notes":"PMT on track"},"2":{"health":"in_progress","notes":"SafeSpect POC — scope decision pending"}}' \
  --notes "@Project Manager assessment."
```

**Flag reference (actual script args — not hyphenated aliases):**
| Flag | PM | BA | SM |
|------|----|----|-----|
| Health/coverage/status | `--health` | `--requirements-coverage` | `--sprint-status` |
| Rationale | `--health_rationale` | `--coverage_rationale` | `--sprint_rationale` |
| Task detail | `--task-health` (JSON) | `--task-requirements` (JSON) | `--task-progress` (JSON) |
| Blockers | — | — | `--blockers` (JSON array) |
| Notes | `--notes` | `--notes` | `--notes` |
| Portfolio | `--portfolio <id>` (default: clin9) | `--portfolio <id>` | `--portfolio <id>` |

### Validate after writing

```bash
python3 -c "import json; json.load(open('pm_status.json')); print('JSON OK')"
```

A syntax error breaks the dashboard silently — always validate.

---

## JSON schema templates

### PM (`pm_status.json`)

| Field | Type | Values |
|-------|------|--------|
| `overall_health` | string | `green` \| `yellow` \| `red` \| `gray` |
| `health_rationale` | string | Why this rating |
| `task_health` | object | `{ "1": {"health": "green", "notes": "..."}, ... }` keyed by task number 1–7 |
| `task_health[].health` | string | `green` \| `yellow` \| `red` \| `gray` |
| `task_health[].notes` | string | Task-specific note |
| `notes` | string | Free-text executive assessment |
| `last_updated` | ISO string | Auto-set on write |
| `updated_by` | string | `"PM"` |

### BA (`ba_status.json`)

| Field | Type | Values |
|-------|------|--------|
| `requirements_coverage` | string | `"43%"` or `"—"` |
| `coverage_rationale` | string | Why this level |
| `task_requirements` | object | `{ "1": {"status": "pass", "notes": "..."}, ... }` keyed by task number 1–7 |
| `task_requirements[].status` | string | `pass` \| `fail` \| `in_progress` \| `pending` \| `complete` \| `incomplete` |
| `task_requirements[].notes` | string | Task-specific note |
| `notes` | string | Free-text assessment |

### SM (`sm_status.json`)

| Field | Type | Values |
|-------|------|--------|
| `sprint_status` | string | `in_progress` \| `completed` \| `pending` \| `planning` \| `paused` \| `blocked` \| `not_started` |
| `sprint_rationale` | string | Sprint context |
| `task_progress` | object | `{ "1": {"status": "on_track", "notes": "..."}, ... }` keyed by task number 1–7 |
| `task_progress[].status` | string | `on_track` \| `in_progress` \| `delayed` \| `at_risk` \| `pending` \| `complete` \| `queued` |
| `task_progress[].notes` | string | Task-specific note |
| `blockers` | array | `[{"task": "2", "description": "...", "severity": "high", "source": "@PM", "date": "2026-09-22"}]` |
| `blockers[].task` | **string** | Task number as string — MUST be `"2"` not `2` |
| `blockers[].severity` | string | `high` \| `medium` \| `low` |
| `blockers[].source` | string | Who reported it |
| `blockers[].date` | string | ISO date |
| `notes` | string | Free-text assessment |

---

## Task status value mapping

| You say | JSON value | Dashboard shows |
|---------|-----------|----------------|
| On track / healthy / pass / complete / done | `green`, `on_track`, `pass`, `complete`, `done` | Green dot |
| At risk / in progress / pending | `yellow`, `at_risk`, `in_progress`, `pending` | Yellow or blue |
| Blocked / delayed / fail | `red`, `delayed`, `fail` | Red dot |
| No status / unknown | `gray`, `—`, `pending` | Gray dot |

---

## Workflow

1. Assess in Slack
2. Determine what changed in your JSON file
3. Write the update (load existing first, modify, write back)
4. Validate JSON syntax
5. Confirm in Slack — tell the human the dashboard is updated
6. Dashboard auto-refreshes every 60 seconds — no manual reload needed

---

## Capturing a new or commencing task

When a team member posts that work is beginning (e.g., "Arsene is beginning work on X"), run this branch before touching any health value:

1. **Do not accept the report at face value.** Find the originating record — ADO/CLIN9 status docs, weekly reports, or CLIN9 Sprint Status.md — and confirm the work actually exists.
2. **Map it.** Check the baseline 7-task structure (Task 1–7: PMT, Track Inspection POC, MCIA RCA, Visualizer, RSAC, Quiet Zone, SharePoint). If the item matches a task, update that task entry. If not, record it as a **new task**.
3. **Set the health.** A new commencing item is at minimum `yellow` (unmapped, not yet productive). Do not mark `green` until it maps and shows delivered value.
4. **Record it.** Add a `task_health` entry (and a note) in `pm_status.json`, and a matching section in `CLIN9 Sprint Status.md`. Refresh `last_updated` and `updated_by`.
5. **Flag for sign-off.** Tag @drighter (PM) to confirm or exclude the mapping. An unmapped item is a sign-off item, not a resolved health status.
6. **Confirm in Slack.** Only if the Slack connector is `connected: true`; otherwise leave the update as a note and flag the posting gap.

| New item in baseline? | Starting health | Action |
|---------------------|----------------|--------|
| Yes (task 1–7) | green / yellow / red | Update that task's entry only |
| No | yellow | Add a new task entry + flag mapping to PM |

### Pitfalls
- **Verify the work item's mapping to the baseline 7-task structure before recording health.** A team member's report of new work is a proposal, not a confirmed status — check the baseline 7-task structure first.
- **Record a new item at yellow until its mapping is confirmed.** An unmapped item cannot be `green` until it is validated against the baseline structure.

---

## Confirming task-status requests (CLIN9)

When a requester asks to "confirm [task] — [status]" (e.g., "Confirm Imelda's site visit — Complete"), run this workflow:

1. **Investigate the source.** Find the originating note/record — Granola notes, weekly reports, or CLIN9 status docs in the Obsidian vault. Do not accept the requested status at face value.
2. **Verify against reality.** Determine the true status from the project record (e.g., Imelda departed the project → the site visit is no longer applicable → close the task as complete).
3. **Update tracking docs.** Record the confirmation in the CLIN9 Sprint Status.md and/or the relevant status summary.
4. **Push the dashboard.** Run `write_status.py` for the PM role (or the relevant role) so the Firestore status reflects the change.
5. **Confirm the dashboard.** Tell the requester the status is confirmed and the dashboard is updated.

### Closing a decision item (e.g., scope decision)

When a requester asks to "close" a decision item (e.g., "close the Track Inspection scope decision"), the item is only closable once the decision has actually been made and recorded. Follow this workflow:

1. **Investigate the source.** Search the Obsidian vault for the originating note/record, ADO exports, or CLIN9 status docs. In this session: the scope decision came from `clin9_daily_brief.md` (Sept 18, asking Robert for the go/no-go) and `CLIN9-Status-Update-2026-09-23.md` (listing it as Next Steps/Asks item #2).
2. **Verify against reality.** Determine the true decision from the project record. In the CLIN9 scope-decision case: Robert's PM-status note already recorded `Scope decision confirmed with Federal PM (Robert): No formal scope change needed at this time. Removing 4 out-of-scope items. Mapped scope proceeding.` Verify the actual resolution before closing anything — a requester's instruction is a proposal, not a completed fact.
3. **Update tracking docs.** Record the closed decision in every relevant tracker:
   - `dashboard/data/pm_status.json` — Task `health` stays `yellow` (POC still in progress) but update `task_health["2"].notes` to record the closure and the resolution facts (removed items, retained items, mapped scope direction).
   - `clin9_daily_brief.md` — replace the open-question/ask with a `**RESOLVED — <date>**` note showing the decision and resolution.
   - Any `CLIN9-Status-Update-*.md` or Sprint Status file — mark the decision item `✅ RESOLVED <date>` with the resolution facts.
4. **Push the dashboard.** Run `write_status.py` for the PM role so the Firestore status reflects the change:
   ```bash
   python write_status.py --role pm --health yellow --health-rationale "..." --tasks "1:green,2:yellow,3:green,4:gray,5:yellow,6:green,7:gray"
   ```
5. **Confirm the dashboard.** Tell the requester the decision item is closed and the dashboard is updated. The dashboard auto-refreshes every 60 seconds.

### Pitfall
- **Do not close a decision based only on the request.** Verify the decision was actually made and recorded before marking it closed. A requester's instruction to "close this item" is a proposal — the decision must be confirmed against the source record first. In this session, the scope decision was already confirmed in Robert's PM-status note (Sept 13), so it was safe to close; but always confirm the source record first.
## Slack posting gate

Before posting to Slack, run `manage_connections(action='status')` and verify the connector is `connected: true`. If the connector shows `connected: false`, the post will fail until the Slack connector is configured. The dashboard pipeline (write_status.py → Firebase) works independently of Slack.

## Pitfalls

- **Read before write** — load the existing file first so you don't lose other tasks' status
- **JSON errors break dashboard silently** — always validate after writing
- **`blockers[].task` must be a string** — use `"2"` not `2`; dashboard compares with `String(b.task) === String(task.num)`
- **Timestamps must be ISO** — `2026-09-22T17:50:00Z` format
- **Server must be running** — `python3 -m http.server 8080` from `dashboard/` dir, or browser can't fetch JSON
- **Don't use `file://`** — open via `http://127.0.0.1:8080/index.html`, not the file path

### Workflow pitfall: write_file is blocked after reads; patch is the fallback
- **write_file may refuse even after a full read** — the stale-write guard can trigger on any read pattern. If write_file returns a "stale write" or "last read with offset/limit pagination" error, switch to `patch` for targeted edits.
- **patch fails on Unicode-encoded files** — fuzzy matching can choke on Windows text files with em dashes (—), arrows (→), or emojis. When patch returns "Could not find a match", use `terminal` with Python and exact string matching instead:
  ```python
  import io
  p = "SB-Hermes/CLIN9 5009/CLIN9 Sprint Status.md"
  with io.open(p, encoding='utf-8') as f:
      content = f.read()
  content = content.replace(old_unicode, new_string)
  with io.open(p, 'w', encoding='utf-8') as f:
      f.write(content)
  ```
- **Validate after every write** — read back with `read_file` or run `python3 -c "import json; json.load(open('pm_status.json')); print('JSON OK')"` to catch silent JSON corruption before Slack confirmation.
