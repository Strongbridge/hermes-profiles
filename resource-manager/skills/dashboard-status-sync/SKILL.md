---
name: dashboard-status-sync
description: Write bot status updates to the CLIN9 dashboard JSON files so the HTML dashboard stays current.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Slack, Obsidian, note-taking, vault]
    related_skills: [obsidian]
---

# Dashboard Status Sync

## When to use

You (PM, BA, SM, or Resource Manager bot) have assessed project status in Slack and need to persist it to the dashboard JSON file so the HTML dashboard reflects your latest assessment.

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
| Resource Manager (@Resource_Manager) | `resource_capacity.json` |

## How to write your status

### Quick method: Python one-liner from bash

```bash
cd "C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/data"
python3 -c "
import json, datetime
from pathlib import Path
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
DASH = Path('.')
f = DASH / 'resource_capacity.json'
data = json.loads(open(f).read()) if f.exists() else {}
data.update({
    'last_updated': now,
    'updated_by': 'Resource Manager',
    'total_team_capacity_hours': 340,
    'utilization_pct': 78,
    'over_allocated_members': ['Jane Doe (Task 2, Task 5)'],
    'skill_coverage': {
        '.NET': 'Full',
        'PWA/React': 'Partial — 1 developer available',
        'Azure DevOps': 'Full',
        'Python': 'Gap — no dedicated resource this sprint'
    },
    'notes': 'Resource Manager weekly capacity report. 3 team members on PTO this week reducing capacity by 45 hours.'
})
open(f, 'w').write(json.dumps(data, indent=2))
print('Updated resource_capacity.json')
"
```

Replace `resource_capacity.json` and the field names with your bot's file and schema.

### Validate after writing

```bash
python3 -c "import json; json.load(open('resource_capacity.json')); print('JSON OK')"
```

A syntax error breaks the dashboard silently — always validate.

## JSON schema template

### Resource Manager (`resource_capacity.json`)

| Field | Type | Values |
|-------|------|--------|
| `last_updated` | ISO string | Auto-set on write |
| `updated_by` | string | `"Resource Manager"` |
| `total_team_capacity_hours` | number | Total available hours this sprint |
| `utilization_pct` | number | Overall team utilization percentage |
| `over_allocated_members` | array | List of names with conflict details |
| `skill_coverage` | object | `{ "skill": "status" }` — Full/Partial/Gap |
| `pto_impact` | object | `{ "date": "hours_lost" }` for planned absences |
| `notes` | string | Free-text capacity assessment |

## Workflow

1. Assess team capacity in Slack or from the Obsidian roster
2. Determine what changed in your JSON file
3. Write the update (load existing first, modify, write back)
4. Validate JSON syntax
5. Confirm in Slack — tell the team the capacity report is updated
6. Dashboard auto-refreshes every 60 seconds — no manual reload needed

## Pitfalls

- **Read before write** — load the existing file first so you don't lose other data
- **JSON errors break dashboard silently** — always validate after writing
- **Timestamps must be ISO** — `2026-09-22T17:50:00Z` format
- **Server must be running** — `python3 -m http.server 8080` from `dashboard/` dir
- **Don't use `file://`** — open via `http://127.0.0.1:8080/index.html`
