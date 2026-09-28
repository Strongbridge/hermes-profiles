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

### Quick method: Python one-liner from bash

```bash
cd "C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/data"
python3 -c "
import json, datetime
from pathlib import Path
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
DASH = Path('.')
f = DASH / 'pm_status.json'
data = json.loads(open(f).read()) if f.exists() else {}
data.update({
    'last_updated': now,
    'updated_by': 'PM',
    'overall_health': 'yellow',
    'health_rationale': 'Project at risk from 2 blockers.',
    'task_health': {
        '2': {'health': 'red', 'notes': 'Track Inspection POC — BLOCKED.'},
        '5': {'health': 'red', 'notes': 'RSAC — BLOCKED.'}
    },
    'notes': '@Project Manager assessment. 2 blockers active.'
})
open(f, 'w').write(json.dumps(data, indent=2))
print('Updated pm_status.json')
"
```

Replace `pm_status.json` and the field names with your bot's file and schema (see below). **Always read the existing file first** — the `json.loads(open(f).read()) if f.exists() else {}` pattern preserves fields you don't touch.

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

## Pitfalls

- **Read before write** — load the existing file first so you don't lose other tasks' status
- **JSON errors break dashboard silently** — always validate after writing
- **`blockers[].task` must be a string** — use `"2"` not `2`; dashboard compares with `String(b.task) === String(task.num)`
- **Timestamps must be ISO** — `2026-09-22T17:50:00Z` format
- **Server must be running** — `python3 -m http.server 8080` from `dashboard/` dir, or browser can't fetch JSON
- **Don't use `file://`** — open via `http://127.0.0.1:8080/index.html`, not the file path
