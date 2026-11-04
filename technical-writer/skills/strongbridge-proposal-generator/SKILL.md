---
name: strongbridge-proposal-generator
description: Use when generating draft proposals from pipelines.
version: 1.0.0
author: Technical Writer
license: MIT
metadata:
  hermes:
    tags: [proposals, templates, pipeline, automation]
    related_skills: [elephant-goldfish-review, docx, obsidian]
---

# Strongbridge Proposal Generator Skill

## When to Use
Use when: Generating, tracking, and drafting professional government contract proposals from active procurement pipelines in the Obsidian vault.

## Guidelines
1. **Source Ingestion**: Automatically parse `Opportunity-Pipeline.md` and `SLED-Opportunity-Pipeline.md` to identify active solicitations.
2. **Deduplication**: Check the target output directory (`Procurement/Draft-Proposals/`) to ensure a proposal file is not created twice for the same Solicitation/Notice ID.
3. **Information Infill**: Leverage `Corporate-Offerings/` (master profile, technical capabilities, and past performance case studies) to populate company credentials, certifications (CMMI Level 3, ISO 9001/20000/27001), and relevant case study content.
4. **Elephant Goldfish Review**: Pass the draft through the Elephant Goldfish review protocol to ensure strict compliance, citations, and structural standards.
5. **Information Gaps**: If critical requirements are unknown, generate a gap action item in `Procurement/Research-Gaps.md` so the research assistant agent knows to find the answer.
6. **Review & Compliance**: All generated proposals must pass the Elephant Goldfish review protocol before finalization.
   - **Reference Integrity**: All claims must cite `Corporate-Offerings/`.
   - **Validation**: Run `docx_validate.py` on the final output to ensure package health.
   - **Tracking**: Log the activity in `documentation/Procurement-Document-Tracking.md`.