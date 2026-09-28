---
name: fradevops-clin9-obsidian-sync
description: Save CLIN9 project content from Slack to Obsidian vault.
version: 1.0.0
author: scrum_master
license: MIT
platforms: [windows]
metalnx:
  hermes:
    tags: [CLIN9, Obsidian, Slack, project-content, capture]
    related_skills: [obsidian, slack-to-obsidian]
---

# FRADevOps CLIN9 — Obsidian Capture Standard

## Standing Rule

All project-related content from every CLIN9 Slack channel must be captured in the Obsidian vault (`SB-Hermes/`). Content left only in Slack is considered lost for planning, audit, and continuity purposes.

## Channels Covered

All CLIN9 Slack channels (IDs confirmed 2026-09-23):

- `<#C0C2HAS5M8W>` — current session channel; name mapping unconfirmed
- `<#C0C2K6CMCN6>` — name mapping unconfirmed
- `<#C0C2HAGS2QN>` — name mapping unconfirmed
- `<#C0C2NUQ1T6G>` — name mapping unconfirmed

Confirmed channel names (ID mapping not yet established):

- **#clin9-standup** — daily async standup threads, sprint velocity, burn-down charts, Sprint Review and Retrospective minutes
- **#clin9-blockers** — critical defect alerts, CI/CD pipeline failures, missing dependency alerts (time-sensitive)
- **#clin9-requirements** — requirements posted by @business_analyst, QA audit results
- **#clin9-management** — weekly R/Y/G health reports, deliverable packages, risk logs, vendor/contractor communications, staffing notes, ADO tracking updates

## Vault Path

```
C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes\
```

This is the active Obsidian vault root (contains `.obsidian/`). Notes saved here are visible in Obsidian. Do NOT save to parent folders like `FRA-DevOps-CLIN9/` — those are invisible in Obsidian.

## What Gets Captured

- Decisions and rationale
- Requirements (from @business_analyst or QA)
- Blocker summaries and resolutions
- Sprint artifacts (velocity, burn-down, backlog changes)
- Meeting minutes (Sprint Reviews, Retrospectives)
- Technical analyses and option comparisons
- Process requirements and working agreements
- Status updates and project reports

## File Naming

- `YYYY-MM-DD-HHMMSS-short-slug.md` when a meaningful slug is available
- `YYYY-MM-DD-HHMMSS.md` otherwise
- Always include YAML frontmatter: `created` (ISO 8601 with tz), `source: slack`, `triggered_by`, `author`, `content_summary`

## Existing Notes in Vault

- `2026-09-23-151900-project-content-obsidian-directive.md` — the directive captured this session
- `2026-09-23-143000-clin9-obsidian-policy.md` — earlier Obsidian policy note (same day)
- `FRADevOps-CLIN9-Obsidian-Capture-Standard.md` — this file
- `MFA-Implementation-Options-Developer-Input.md`
- `Track-Inspection-POC-Process-Requirements.md`
- `CLIN9-Sprint-Timelines.md`
- `ONBOARDING_CHECKLIST.md`

## Notes Still Outside Vault (need bringing in)

- `Project Status Reports/2026-08-25_CUI_Sanitized_Project_Status.md` — in `Documents/Obsidian/Project Status Reports/`, not in vault root
- `SB-Hermes/2026-09-23-143000-clin9-obsidian-policy.md` — earlier policy note (same day, 14:30); may overlap with this standard

## When a Slack Message Needs Saving

1. Identify the sender (display name / user identity)
2. Extract the content (everything after the trigger phrase, or the full message if no trigger)
3. Resolve the save path: `SB-Hermes/` (vault root)
4. Create the note with frontmatter + body
5. Confirm in Slack: "Saved to Obsidian: <filename>"

See `slack-to-obsidian` skill for full trigger-pattern and linking details.

## Post-Save Verification

After saving, confirm the file exists in `SB-Hermes/` before telling the user it's done. A write that silently fails (disk full, permission) leaves the user thinking the save happened when it didn't.

## Links

Use Obsidian wikilinks `[[Note Name]]` to connect related notes. When a save references an earlier note, search `SB-Hermes/` for it and add the link.