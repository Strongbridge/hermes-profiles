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
| `task_requirements` | object | `{ "1": {"status": "pass", ...}, ... }` keyed by task number 1–7 |
| `task_requirements[].status` | string | `pass \| fail \| in_progress \| pending \| complete \| incomplete` |
| `task_requirements[].notes` | string | Task-specific note |
| `notes` | string | Free-text assessment |

#### CLIN 9 BA extensions

For CLIN 9 status briefs, extend the BA schema with task-specific tracking:

| Field | Type | Values |
|-------|------|--------|
| `task_health` | object | `{ "2": {"health": "red", "notes": "..."}, ... }` keyed by task number |
| `task_health[].health` | string | `green \| yellow \| red \| gray` |
| `task_health[].notes` | string | Task-specific status note |
| `blockers` | array | `[{"task": "2", "description": "...", "severity": "high", "source": "@PM", "date": "2026-09-22"}]` |
| `blockers[].task` | string | Task number as string — MUST be `"2"` not `2` |
| `blockers[].severity` | string | `high \| medium \| low` |
| `blockers[].source` | string | Who reported it |
| `blockers[].date` | string | ISO date |

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
5. Post brief to Slack #clin9-requirements (BA only — see BA Slack posting below)
6. Confirm in Slack — tell the human the dashboard is updated
7. Dashboard auto-refreshes every 60 seconds — no manual reload needed

### BA Slack posting workflow

After writing the dashboard JSON, post a concise brief to `#clin9-requirements` using the hermes CLI:

```bash
/c/Users/DanRighter/AppData/Local/hermes/bin/hermes.exe send \
  --to slack:Clin9-Requirements \
  --subject "📬 CLIN 9 Brief — <date>: <summary>" \
  --file '<brief-file-path>' \
  --quiet 2>&1
```

The brief file should be written first (see BA brief format below), then posted. Use `— quiet 2>&1` to suppress echo on success; check exit code 0 for confirmation.

**Brief format rules:**
- Subject line: `📬 CLIN 9 Brief — <date>: <one-line summary>`
- Use 🚨 for blockers, 🟢 for unblocked/started, 🔴 for active blockers
- Tag @drighter for scope approval, @Carl Jackson for technical feasibility
- Sections: Track Inspection POC, Quiet Zone Phase 2, MCIA, Form 96, RSAC/Google Transition
- Highlight only status changes from the previous brief — don't re-list unchanged items
- Save brief to `C:/Users/DanRighter/AppData/Local/hermes/clin9_<date>_brief.md`

## CLIN 9 task status value mapping

Extends the generic mapping above for CLIN 9-specific statuses:

| You say | JSON value | Dashboard shows |
|---------|-----------|----------------|
| Repo access resolved, dev started | `yellow`, `in_progress` | Yellow dot |
| Offline capability not started | `gray`, `pending` | Gray dot |
| FIPS encryption work in progress | `yellow`, `in_progress` | Yellow dot |
| QA/QC queue | `yellow`, `at_risk` | Yellow dot |
| Ready for UAT | `yellow`, `pending` | Yellow dot |
| SafeSpect PoC items all New | `gray`, `pending` | Gray dot |

---

## Pitfalls

- **Read before write** — load the existing file first so you don't lose other tasks' status
- **JSON errors break dashboard silently** — always validate after writing
- **`blockers[].task` must be a string** — use `"2"` not `2`; dashboard compares with `String(b.task) === String(task.num)`
- **Timestamps must be ISO** — `2026-09-22T17:50:00Z` format
- **Server must be running** — `python3 -m http.server 8080` from `dashboard/` dir, or browser can't fetch JSON
- **Don't use `file://`** — open via `http://127.0.0.1:8080/index.html`, not the file path
- **Multi-field JSON updates** — `write_file` refuses files read with pagination; sequential `patch` calls validate each candidate independently and can leave the file inconsistent if one succeeds and another fails. For any update touching more than one field, use Python's `json` module via `execute_code`: load → modify in memory → write → validate.
- **Slack post timeout** — `hermes send` can hang on slow connections; use a 120s timeout, not 30s. If it times out, retry once before flagging.
- **Brief file path** — save briefs to `C:/Users/DanRighter/AppData/Local/hermes/clin9_<date>_brief.md`, NOT the Obsidian vault directory. The vault path (`SB-Hermes/`) is for Obsidian-sourced notes only; hermes briefs go in the profiles cache for Slack posting.
- **Status drift between Slack and dashboard** — the Slack brief is the human-facing update; the dashboard JSON is the system of record. Always update the JSON first, then post the Slack brief. If they disagree, the JSON wins.

## References

- `references/clin9-status-areas.md` — CLIN 9 tracking areas, SafeSpect PoC status map, task health values, Slack channel info
