---
name: strongbridge-proposal-generator
description: Use when generating draft proposals from pipelines.
version: 1.2.0
author: Technical Writer
license: MIT
metadata:
  hermes:
    tags: [proposals, templates, pipeline, automation, weekly-report]
    related_skills: [elephant-goldfish-review, docx, obsidian]
---

# Strongbridge Proposal Generator Skill

## When to Use
Use when: Generating, tracking, and drafting professional government contract proposals from active procurement pipelines, posting weekly syntheses to Slack `#proposal-opportunities` (`C0CGLS772AG`), and emailing reports/attachments via Microsoft Graph API on Mondays at 8:00 AM ET.

## Guidelines
1. **Source Ingestion & Line-by-Line Parsing**:
   - Do NOT use multiline regular expressions across full markdown files; tables bleed and match headers/footers.
   - Implement a line-by-line parser (`parse_pipeline`) that isolates active register tables under Section 1 (e.g., `## 1.`) and exits immediately when reaching subsequent sections.
   - Explicitly filter out any rows with date-formatted cells in the first column (e.g., `\d{2}/\d{2}/\d{4}` or `\d{4}-\d{2}-\d{2}`) to avoid parsing historical maintenance logs as active opportunities.
2. **Deduplication**: Check the target output directory (`Procurement/Draft-Proposals/`) to ensure a proposal file is not created twice for the same Solicitation/Notice ID.
3. **Information Infill**: Leverage `Corporate-Offerings/` (master profile, technical capabilities, and past performance case studies) to populate company credentials, certifications (CMMI Level 3, ISO 9001/20000/27001), and relevant case study content.
4. **Elephant Goldfish Review**: Pass the draft through the Elephant Goldfish review protocol to ensure strict compliance, citations, and structural standards.
5. **Information Gaps**: If critical requirements are unknown, generate a gap action item in `Procurement/Research-Gaps.md` so the research assistant agent knows to find the answer.
6. **Weekly Report & Slack Dispatch**:
   - Every Monday at 8:00 AM, compile a structured summary report (`weekly_proposal_opportunities_report.py`) detailing all upcoming deadlines, priorities, and draft statuses.
   - Deliver the report directly to the Slack channel `#proposal-opportunities` (`C0CGLS772AG`).
7. **Azure/Microsoft Graph Email Dispatch**:
   - Utilize Azure Client Credentials (tenant, client ID, client secret) stored securely in `.env` to authenticate with Microsoft Graph API.
   - Email the report to `drighter@sb-llc.com` with clean, modern HTML styling mimicking corporate helpdesk templates (colored headers, structured status tables, highlighted alerts).
   - Automatically convert markdown proposal drafts to clean MS Word (`.docx`) files on-the-fly at runtime and attach them as base64-encoded files.
8. **Review & Compliance**: All generated proposals and reports must pass the Elephant Goldfish review protocol before finalization.
   - **Reference Integrity**: All claims must cite `Corporate-Offerings/`.
   - **Validation**: Run `docx_validate.py` on the final output to ensure package health.
   - **Tracking**: Log the activity in `documentation/Procurement-Document-Tracking.md`.

## Pitfalls
- **Python-Docx Environment Errors**: Standard `pip install` may target system-level packages while the active Hermes execution runs on a separate isolated virtual environment (`venv`). Always use `uv pip install --python <venv_path> python-docx` to bind libraries specifically to the active interpreter environment.
- **Header Parsing Bleed**: Ingestion tables and maintenance tables often share similar pipe structures. Always ensure the first cell matches robust validation checks (excluding headers and log titles) before instantiating proposal drafting.
- **Unsanitized Filepath Construction**: Solicitation IDs containing slashes (e.g., `ID / Sol #`) must be sanitized using regex (e.g., `re.sub(r'[\\/*?:"<>|]', '_', notice_id)`) to prevent operating systems from interpreting them as directory structures, which fails with `FileNotFoundError`.