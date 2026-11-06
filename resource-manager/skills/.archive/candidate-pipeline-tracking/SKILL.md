---
name: candidate-pipeline-tracking
description: Use when logging candidate interviews, managing staffing requisitions, or tracking candidate pipelines across contract tasks.
version: 1.1.0
---

# Candidate Pipeline Tracking

Use this skill when logging candidate interviews, managing staffing requisitions, or tracking candidate pipelines across contract tasks.

## Procedure

1. **Extract Interview Context**
   - Candidate full name
   - Requisition/role and target task assignment (e.g., Task 7 Google Workspace/Cloud Developer)
   - Scheduled date, time, and timezone
   - Interviewer(s) / host(s)

2. **Save Resume to Obsidian** (if a resume file is provided)
   - Path: `SB-Hermes/YYYY-MM-DD-HHMMSS-{candidate-kebab-case}-resume.md`
   - Standard frontmatter: `created`, `source: slack`, `triggered_by`, `author`, `content_summary`
   - Full resume content as markdown body

3. **Save Candidate Interview Note to Obsidian Vault**
   - Path: `SB-Hermes/YYYY-MM-DD-HHMMSS-interview-{candidate-kebab-case}.md`
   - Use standard frontmatter:
     ```yaml
     ---
     created: YYYY-MM-DDTHH:MM:SS-04:00
     source: slack
     triggered_by: "@hermes Agent save this"
     author: <Slack sender name>
     content_summary: "<one-line summary>"
     ---
     ```
   - Body structure:
     - Interview outcome and status
     - Requisition & Task Context (open FTE allocation, task dependencies)
     - Key qualifications distilled from resume
     - `## Notes & Feedback` section for post-interview evaluation

4. **Assess Capacity Impact**
   - Check if the requisition addresses an open bottleneck or open allocation gap (e.g. 0.83 FTE position for Task 7).
   - Flag upcoming decision points or required follow-ups for task managers post-interview.

5. **Update Team Profiles & Dashboard Data**
   - Update `dashboard/data/team_profiles.json` under `potential_google_candidates[]` with the candidate's profile details: `name`, `target_role`, `status`, `requisition_fte`, `contact`, `summary`, `certifications`, `key_skills`, `pertinent_experience`, and `notes`.
   - Update `dashboard/data/team_update.json` with the **complete** `team_members` roster plus the updated `potential_google_candidates` array.
   - Push to dashboard via `python write_status.py --role rm --json-file data/team_update.json`.
   - If `write_status.py` does not support `--role rm` or `--json-file`, patch it: add `"rm"` to the `--role` choices list and add the `--json-file` argument handler that loads the JSON and updates the Firestore `status/rm` document.
   - If argparse help strings contain `%`, escape as `%%` to avoid Python 3.12+ `ValueError: unsupported format character`.

## Pitfalls & Rules

- **Always anchor to a CLIN9 task requisition**: Connect candidates to specific contract tasks so capacity forecasts reflect potential staffing changes.
- **Preserve ISO timestamps**: Use explicit timezones (`-04:00` EDT) in frontmatter to prevent calendar shift errors.
- **Leave feedback placeholders**: Include an explicit feedback section so post-interview updates can be appended cleanly without changing file structure.
- **`write_status.py` may lack `rm` role support**: The script ships without `--role rm` and `--json-file`. Always check the `--role` choices list before assuming `rm` is supported; patch in the `rm` branch and `--json-file` argument if missing.
- **`%%` in argparse help**: `%` is a format character in Python 3.12+ argparse help strings; bare `%` raises `ValueError: unsupported format character`. Escape as `%%` in help text.
- **`team_update.json` must be the full roster**: The dashboard merges, so omitting a member removes them from the dashboard. Load `data/team_profiles.json` first to get the current full list before writing `team_update.json`.
- **Save resume separately when provided**: A candidate resume is a distinct artifact from the interview note. Save it with a `-resume` slug in the filename so it's retrievable independently.
- **Melissa Willis OOO pattern**: BA covering 3 tasks (3, 4, 5) at reduced capacity creates bottleneck across all three. Check capacity impact across Tasks 3, 4, 5 when a BA is OOO; consider cross-training Amivi Seddoh on RSAC user story entry.
- **Resource Manager cannot post to Slack**: RM has no send-to-Slack capability. When a Slack response is needed, route through @carl or reply here so the user can copy back.
- **Save resume separately when provided**: A candidate resume is a distinct artifact from the interview note. Save it with a `-resume` slug in the filename so it's retrievable independently.
