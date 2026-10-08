---
name: dashboard-status-sync
description: Write bot status updates to the CLIN9 dashboard JSON files so the HTML dashboard stays current.
---

# Dashboard Status Sync

## When to use

You (PM, BA, or SM bot) have assessed project status and need to push it to the
live CLIN 9 dashboard via Firestore.

## Dashboard script — Firebase (authoritative)

The dashboard runs on Firebase Firestore. All status writes go through:

```
C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/write_status.py
```

**This is the only write_status.py to use.** Do NOT use any local copy in the
agent directory or `data/` folder — those are stale and will not reach Firestore.

### Prerequisites

- `google-cloud-firestore` installed (`pip install google-cloud-firestore`)
- `GOOGLE_APPLICATION_CREDENTIALS` env var set to the service account JSON key
  (configured in `SB-Hermes/dashboard/.env`)
- Execute from the `SB-Hermes/dashboard/` directory (where `write_status.py` lives)

### Execution command

```bash
cd "C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian/SB-Hermes/dashboard"
python write_status.py \
  --portfolio clin9 \
  --role <pm|ba|sm> \
  --notes "<assessment>" \
  --tasks "1:<status>,2:<status>,3:<status>,4:<status>,5:<status>,6:<status>,7:<status>" \
  [--coverage "<pct>"] \
  [--coverage-rationale "<explanation>"] \
  [--health <green|yellow|red|gray>] \
  [--health-rationale "<why>"] \
  [--sprint "<status>"] \
  [--blockers "<severity:task:desc;...>"]
```

### `--tasks` argument — REQUIRED for every call

Map ALL 7 task IDs to their status. Valid statuses: `pass`, `in_progress`, `pending`, `complete`, `fail`, `delayed`, `gray`.

Format: `"1:status,2:status,3:status,4:status,5:status,6:status,7:status"`

**Never omit --tasks or leave a task unmapped.** Every call must include all seven.

### `--portfolio` argument

Use `--portfolio clin9` (default if omitted) for CLIN 9. For other portfolios use
the assigned ID (e.g. `--portfolio onm`). Omit only if targeting clin9 explicitly.

### Read before write

Always read the existing status file before updating so you don't lose data from
other tasks or roles. Then validate by re-reading the Firestore document after
writing.

### Verify after writing

Read back the Firestore document to confirm the update landed:

```python
import os, json
from google.cloud import firestore
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/DanRighter/AppData/Local/hermes/secrets/project-mgt-report-sa.json"
client = firestore.Client(project="fradevops-a51a2", database="devopsstore")
doc = client.collection("status").document("ba").get()
print(json.dumps(doc.to_dict(), indent=2))
```

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
- **File path for `hermes.exe send`**: use the Windows-native path (`C:/Users/DanRighter/...`), NOT `/tmp/` — bash `/tmp` does not resolve for the Windows Hermes binary

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

- **`--tasks` is REQUIRED** — every call must map all 7 task IDs (1–7).
  Never omit or leave a task unmapped; the dashboard shows stale data.
- **Use the Firestore script only** — `C:/Users/DanRighter/OneDrive -
  Strongbridge/Documents/Obsidian/SB-Hermes/dashboard/write_status.py`.
  Do NOT use local copies in the agent directory or `data/` folder.
- **`--portfolio clin9` for CLIN 9** — other portfolios need `--portfolio <id>`.
  Omitting defaults to clin9.
- **Read before write** — load the existing status file first so you don't
  lose data from other tasks or roles. Then validate by re-reading the
  Firestore document after writing.
- **Timestamps must be ISO** — `2026-09-22T17:50:00Z` format

## References

- `references/clin9-status-areas.md` — CLIN 9 tracking areas, SafeSpect PoC status map, task health values, Slack channel info
