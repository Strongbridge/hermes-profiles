---
name: stakeholder-profiling
description: Build stakeholder profiles and track relationship health.
version: 1.0.0
author: Customer Relations (CRS)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [stakeholder, relationship, communication, engagement]
    related_skills: [obsidian, dashboard-status-sync]
---

# Stakeholder Profiling

## When to use

- Building the first profile for a new stakeholder (internal or external) on the CLIN9 contract.
- Updating a stakeholder's relationship health after an interaction.
- Flagging an emerging relationship risk (dropping engagement, feeling unheard, misrepresentation to management).
- Deciding how the team should engage a stakeholder — requesting a tailored communication approach.

## Artifacts

1. Markdown profile: `SB-Hermes/stakeholders/<Name>.md` — the canonical stakeholder record.
   - Field format is defined in that folder's `README.md` (role, channels, communication style, decision style, idiosyncrasies, what works, what to avoid, health, recent interactions, notes).
2. Dashboard entry: `SB-Hermes/dashboard/data/stakeholders_update.json` — one object per stakeholder plus an `engagement_summary` block with green/yellow/red counts.

## Procedure

1. **Identify** the stakeholder's formal role, organization, and position in the chain (COR, ACOR, management representative, etc.).
2. **Discover channels** they participate in — ask the team. Do not assume; record "To be observed — need team input" until you have data.
3. **Observe and record communication style** — concise vs detailed, formal vs casual, async vs sync-preferring.
4. **Record decision-making style** — data-driven, intuition-led, consensus-builder, top-down.
5. **Record known idiosyncrasies as observed patterns, not character judgments.** Example: "asks leading questions in standups and directs devs outside process" is an observed pattern; "difficult person" is a judgment and not a usable data point.
6. **Record what works well and what to avoid** as actionable guidance for the team (e.g., "share the specific question in advance," "do not feed status expecting it to reach management unfiltered").
7. **Set relationship health** — green / yellow / red, with a one-line reason.
8. **Log recent interactions** — date, stakeholder, context, outcome, lessons.
9. **Update the dashboard JSON** — add the per-stakeholder object, adjust the green/yellow/red counts, append notes.
10. If the risk is executive-level (e.g., a stakeholder consistently re-framing your status for management), flag to @drighter for executive handling.

## Standing rules

- **Do not share profiles outside the project team.** Confidentiality applies even when the stakeholder is friendly.
- **Be objective.** Record patterns observed; describe idiosyncrasies as data points, not flaws.
- **Focus on what the team controls** — communication approach, timing, format, framing.
- **"To be observed" is an acceptable interim state.** Keep it until the team supplies observations; do not guess.
- **Capture verifiable status in writing.** If a stakeholder re-frames information for management, the accurate written record is the only defense against it being re-framed again.

## Pointers

- Profile field format: [`SB-Hermes/stakeholders/README.md`](README.md)
- Dashboard schema: [`SB-Hermes/dashboard/data/stakeholders_update.json`](stakeholders_update.json)
