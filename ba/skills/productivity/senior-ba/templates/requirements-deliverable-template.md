# Requirements Deliverable Template

Use this template for every CLIN9 BA requirements deliverable: Epic, Feature, User Story, Gherkin AC, Requirements Traceability Matrix (RTM), and an open-questions block for reviewers.

**Context:**
- **Stakeholders:** Angela (FRA), @drighter (PM for scope), @Carl Jackson (Task Manager for technical feasibility).
- **Task mapping:** which CLIN9 task/index carries this; default `new` if unnumbered.
- **Status:** `Req Elicitation` → `AC Locked` → `QA Passed` → `Released`.

## Constraints (must appear in the ACs they touch)
- **BR-1/BR-2** offline mobility — coverage decision on offline access to self-paced training.
- **NFR-3/NFR-4** FIPS-compliant encryption — hosted PDFs/keys require FIPS-compliant encrypted storage.
- **Hard deadline gates** — e.g. content list Thu Nov 19 → build complete Fri Nov 20 → go-live Dec 1. Encode each gate in the relevant AC.

## Epics
### Epic A — [one-line value statement]
- [Business need / value]

## Features
- **F1 — [title]**: [one-line scope]
- **F2 — [title]**: [one-line scope]

## User Stories
### US-1 — [persona] [action]
- **As a** [persona], **I want** [action], **so that** [business value].
- **Acceptance Criteria** (Given/When/Then):
  - Given [context], When [action], Then [result].
  - Given [context], When [action], Then [result].

## Requirements Traceability Matrix (RTM)
| Req ID | Feature | Source / Constraint | Key AC(s) | Deadline / Risk |
|---|---|---|---|---|
| FR-01 | F1 | ... | US-1.1–1.3 | ... |

## Risks & Open Questions (for @drighter scope + @Carl Jackson technical review)
- Task mapping / access / structure / offline coverage / QA approach / long-term ownership

## Next Actions
- Lock ACs, generate QA test script, schedule staging review ahead of the release gate