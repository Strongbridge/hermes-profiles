---
name: lcq-form-management
description: "Process Exhibit D LCQ forms for CLIN9 team profiles."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Slack, resource-management, subcontractors, lcq, exhibit-d]
  related_skills: [clin9-roster]
---

# LCQ Form Management

## When to use

- Receiving a directive to update team profiles with Exhibit D Subcontractor Labor Qualification (LCQ) forms
- TTC or subcontractor personnel qualify for a task and need their LCQ form verified and stored
- New team member onboarding requires qualification form documentation
- Confirming LCQ approval status for a candidate who has achieved offer acceptance (e.g., Trevor Jones)

## Workflow

### Phase 1 — Locate and read the source documents

1. **Search for the PDF files first.** When Slack attachment access fails with HTTP 403, search local synced folders (`OneDrive`, `Downloads`, `Microsoft Teams Chat Files`) with `search_files` for the file by name. Do NOT halt — the local paths exist and are readable.
2. **Read the PDF text layer** with `read_file` (docx/PDF support is built in). Extract the structured fields from the Exhibit D form.
3. **Capture all LCQ fields**: form name, subcontractor, employee name, labor category, subcontract number, project title, effective date, subcontract end date, signatory name/title, approval date, qualification status for each area (Functions, General Experience, Education), and any education details.

### Phase 2 — Check for existing profiles and merge if needed

4. **Search `team_profiles.json`** for an existing entry by name or last name. Use `json.load()` + list comprehension in Python to search; do not use grep for JSON.
5. **If a profile exists**, append `lcq_details` to it (do not duplicate the profile).
6. **If no profile exists**, create a new entry with `name`, `role`, `organization`, `slack_handle`, `channels`, `responsibilities`, `influence`, `notes`, and `lcq_details` fields. Add to the `team_members` array.
7. **Check `potential_google_candidates`** — if the person is a candidate there, update their `status` to reflect onboarding/LCQ approval. Also add `lcq_status` field.

### Phase 3 — Create and store the LCQ form record

8. **Create an Obsidian form record** at `team/TTC/{Employee Name}/LCQ - Subcontractor Labor Qualification Form - {Employee Name}.md` (or last name if preferred). Use the YAML frontmatter pattern:
   ```yaml
   ---
   type: lcq-form
   subcontractor: TTC, Inc.
   employee_name: {Full Name}
   labor_category: {Category}
   subcontract_number: {Number}
   project_title: {Title}
   effective_date: {Date}
   subcontract_end_date: {Date}
   signatory: {Name, Title}
   approval_date: {Date}
   status: Approved (Meets/Exceeds All Qualifications)
   ---
   {
   # Full form details...
   }
   ```
9. **Create a team member profile note** at `team/TTC/{Employee Name}/{Employee-Lastname}.md` with structured overview, technical stack, qualifications, and education. This is the person's living profile card.
10. **Update the organizational record** — add an LCQ section to `team-profiles.md` listing all processed forms, and update `FRADevOps Team - Org Chart.md` to reflect the new status in the candidate table.

### Phase 4 — Push and notify

11. **Validate the JSON** — run `python3 -c "import json; json.load(open('dashboard/data/team_profiles.json')); print('OK')"`.
12. **Push to Firebase** via `write_status.py`: `python write_status.py --role rm --json-file "dashboard/data/team_profiles.json"`.
13. **Confirm the success line** — `[write_status] ✅ rm status updated -> team/members` must print before you reply.

## Format for LCQ documents

- **Obsidian (vault)**: Markdown tables for LCQ qualification assessment (Meets/Exceeds columns).
- **Slack (channel posts)**: bullet lists or labeled lines — markdown tables NOT supported in Slack.
- **Lead with the outcome**: LCQ approved, approval date, effective period, signatory.
- **Always include**: form name, employee, labor category, subcontract number, approval status, signatory.

## Pitfalls

- **Slack attachment 403 fallback** — when Slack file download returns 403, search local synced folders (`OneDrive`, `Microsoft Teams Chat Files`, `Downloads`) for the file by name rather than halting. The local files are readable.
- **PDF text extraction may mangle unicode** — e.g., `B.S. in Urban and Regional Planning, plus two master's degrees` may appear as `B.S. in Urban and Regional Planning, plus two master�s degrees`. Human-read and normalize the text, not the data.
- **JSON mutation via Python, not patch** — the patch tool fails on JSON files containing unicode escapes (e.g., `\u2014` em dash in notes) with `JSONDecodeError`. Use `json.load()` + `json.dump()` in a Python script, then re-validate that the file parses.
- **Windows native Python path** — when running `python3` through bash (git-bash), a path starting `/c/Users/...` double-escapes to `C:\\c\\Users\\...` and the file is not found. Use the Windows-native path `C:/Users/...` (no leading slash) for `python3 -c` and for running a script file.
- **Validate JSON after every write** — always re-run `python3 -c "import json; json.load(open('dashboard/data/team_profiles.json'))"` (and `capacity.json`) before reporting success; a syntax error breaks the dashboard silently.
- **Firestore push is a hard gate** — every LCQ-related roster change MUST end with `write_status.py --role rm --json-file` printing `[write_status] ✅ rm status updated -> team/members` before you reply. Never consider the update complete without that confirmation.
- **LCQ details live in two places** — the per-member `lcq_details` field in `team_profiles.json` AND the standalone Obsidian form record. Both must be populated and consistent.
- **Do not create duplicate profiles** — check for existing entries by name before appending. The consolidated profile list in `team_profiles.json` must have exactly one active row per person.
- **Section renumbering falls through** — when adding a new section to `team-profiles.md`, verify that all subsequent section numbers stay in sequence. Patch renumbering a middle section misnumbers the later ones.
- **Agent-to-Slack constraint** — the agent has no Slack-post API, so the vault file is the authoritative record; the human posts the summary into #clin9-capacity.

## Related

- [[clin9-roster]] — roster management, capacity tracking, and Slack attachment handling
- [[dashboard-status-sync]] — Firestore push protocol for status updates