---
name: candidate-pipeline-tracking
description: Use when logging candidate interviews.
version: 1.0.0
---

# Candidate Pipeline Tracking

Use this skill when logging candidate interviews, managing staffing requisitions, or tracking candidate pipelines across contract tasks.

## Procedure

1. **Extract Interview Context**
   - Candidate full name
   - Requisition/role and target task assignment (e.g., Task 7 Google Workspace/Cloud Developer)
   - Scheduled date, time, and timezone
   - Interviewer(s) / host(s)

2. **Log Candidate Interview in Obsidian Vault**
   - Path: `SB-Hermes/YYYY-MM-DD-interview-{candidate-kebab-case}.md`
   - Use standard frontmatter:
     ```yaml
     ---
     created: YYYY-MM-DDTHH:MM:SS-04:00
     author: Resource Manager
     type: candidate-interview
     candidate: <Candidate Name>
     position: <Role / Task Requisition>
     interview_date: YYYY-MM-DDTHH:MM:SS-04:00
     status: scheduled
     ---
     ```
   - Body structure:
     - Requisition & Task Context (e.g., open FTE allocation, task dependencies)
     - Interview Details (date, time, host)
     - Empty `## Notes & Feedback` section for post-interview evaluation

3. **Assess Capacity Impact**
   - Check if the requisition addresses an open bottleneck or open allocation gap (e.g. 0.83 FTE position for Task 7).
   - Flag upcoming decision points or required follow-ups for task managers post-interview.

4. **Update Team Profiles & Dashboard Data**
   - Add candidate profile details to `dashboard/data/team_profiles.json` under `potential_google_candidates[]` including: `name`, `target_role`, `status`, `requisition_fte`, `contact`, `summary`, `certifications`, `key_skills`, `pertinent_experience`, and `notes`.
   - Update Obsidian team roster files (`FRADevOps Team - Org Chart.md`, `team-profiles.md`, and `team/{Candidate-Name}.md`) with candidate qualifications and resume highlights.
   - Verify `dashboard/index.html` renders the new `potential_google_candidates` section.

## Pitfalls & Rules

- **Always anchor to a CLIN9 task requisition**: Connect candidates to specific contract tasks so capacity forecasts reflect potential staffing changes.
- **Preserve ISO timestamps**: Use explicit timezones (`-04:00` EDT) in frontmatter to prevent calendar shift errors.
- **Leave feedback placeholders**: Include an explicit feedback section so post-interview updates can be appended cleanly without changing file structure.
