---
name: scrum-master
version: 1.0.0
description: >
  Help a Scrum Master run ceremonies, track sprint health,
  surface blockers and risks, extract action items, and
  prepare stakeholder-facing status. Covers daily standups,
  sprint planning, review, retrospective, backlog refinement,
  velocity/burndown awareness, impediment escalation, and
  Agile coaching reminders.
  Works for Scrum teams in any domain (e.g. FRADevOps).
category: project-management
author: Dan Righter
created: 2026-09
tags:
  - scrum
  - agile
  - scrum-master
  - ceremonies
  - sprint-planning
  - retrospective
  - standup
  - blockers
  - impediments
  - stakeholder-reporting
  - fradevops
---

# Scrum Master Skill

Help a Scrum Master do a better job — run better ceremonies, keep the sprint healthy, catch problems early, and communicate clearly with the team and stakeholders.

Designed for use in FRADevOps and similar delivery environments. Fits alongside existing skills like `morning-triage`, `meeting-action-items`, `daily-status-digest`, and `weekly-review-planning`; this skill is sprint/ceremony-specific.

## When to use this skill

Invoke when the Scrum Master needs help with:

- Preparing for or running a Scrum ceremony (planning, daily standup, review, retrospective, backlog refinement)
- Tracking sprint health: blockers, risks, velocity, burndown, scope changes
- Extracting action items and owners from meeting notes or transcripts
- Writing stakeholder updates, status reports, or escalation messages
- Coaching the team: Agile reminders, anti-pattern spotting, retro insights
- Preparing inputs for managers meetings (bi-weekly status, risks, asks)

## Ceremonies

### Daily Standup

**Before the standup:**
- Pull the sprint board state (whatever tool the team uses — Jira, Azure DevOps, GitHub Projects, etc.) and identify:
  - What's in progress, what's blocked, what's at risk of slipping
  - Anything that moved out of "In Progress" without moving to "Done"
  - Items aging past their expected duration
- Note any new blockers reported since last standup
- Have 2-3 focus questions ready (e.g. "any dependencies on the Capital Presence team?", "is the RSIS helpdesk contact resolved?")

**During the standup:**
- Keep it tight: each person answers "What did I do? What will I do? Any blockers?" — watch for people going deep into problem-solving and park those for after.
- Capture blockers and impediments in real time.
- Note items that need follow-up with the product owner, other teams, or management.

**After the standup:**
- Summarize: what was accomplished, what's in progress, blockers, and follow-ups with owners and due dates.
- Escalate blockers that the Scrum Master can't resolve directly — format a clear message to the right person/team.
- Update the team's shared status if there's a channel for it (Slack, Teams, etc.).

### Sprint Planning

**Inputs to gather ahead of planning:**
- Current sprint burndown / velocity trend (last 3 sprints if available)
- Backlog items ranked by the product owner, with acceptance criteria
- Team capacity: who's on vacation, on other work, or otherwise unavailable
- Carry-over from the previous sprint (incomplete items, why they didn't finish)
- Known dependencies on other teams (TTC, Capital Presence, Strongbridge, etc.)

**Facilitation prompts:**
- "What's the goal for this sprint? Can we state it in one sentence?"
- "Which items are clear enough to pull in? Which need refinement first?"
- "What are the risks to committing to this load?"
- "Are there any cross-team dependencies we need to call out now?"

**Outputs:**
- Sprint goal (one sentence)
- Committed backlog items with owners and acceptance criteria
- Capacity note (anyone partially allocated? any known constraints?)
- Risk list with owners for mitigation

### Sprint Review

**Before the review:**
- Confirm what's actually "Done" against the sprint goal and acceptance criteria
- Prepare a demo/preview for each completed item
- Note anything that's partially done or deferred — be ready to explain why

**During the review:**
- Walk through completed work against the sprint goal
- Get feedback from stakeholders (Shristy/COR, Christina/ACOR, TTC, Capital Presence, etc.)
- Capture any new requests or changes to priority

**After the review:**
- Update the product backlog with new/changed items from the review
- Note any scope decisions that affect the next sprint

### Sprint Retrospective

**Frame the retro around:**
- What went well (keep doing)
- What didn't go well (stop/change)
- What we want to try (experiment for next sprint)

**Facilitation:**
- Keep it blameless — focus on the process, not people.
- Prioritize 1-3 actionable improvements for the next sprint, each with an owner.
- Check whether any of the action items from the previous retro were completed.

**Outputs:**
- 1-3 action items with owners and due dates (feed these into the next sprint's tracking)
- Any systemic issues to raise with management (e.g. persistent blockers from another team, tooling problems, ATO delays)

### Backlog Refinement

**Goals of a refinement session:**
- Make sure upcoming items have clear acceptance criteria
- Identify dependencies and risks early
- Size items or at least get relative sizing agreement
- Flag items that need clarification from the product owner or a subject-matter expert

**Prompts:**
- "What does 'done' mean for this item? Is the acceptance criteria specific enough?"
- "Do we know what's needed from the other teams involved?"
- "Is this small enough to fit in a sprint, or do we need to break it down?"

## Sprint health tracking

Track these continuously during the sprint — flag any that look off:

- **Blockers/impediments:** any item that can't move forward; who's blocking it, what's needed to unblock, who owns the escalation
- **Aging items:** tasks or stories in progress longer than expected; potential scope risk
- **Scope changes:** items added or removed mid-sprint — note the reason and impact
- **Velocity trend:** last 3 sprints' completed work vs. planned; useful for planning confidence
- **Burndown:** is the team on track to complete committed work by sprint end?
- **Carry-over:** work that didn't finish — understand why and whether it should come back next sprint

**Red flags to surface early:**
- Blocker that's been open more than a day with no owner assigned
- A critical-path item at risk with no mitigation
- Scope creep that's pushing the sprint goal out of reach
- Team member overloaded or blocked on something outside the team's control (e.g. an ATO waiting on a security review, a dependency on Capital Presence)

## Action item extraction

After any meeting (standup, planning, review, retro, managers meeting), extract:

- What needs to happen
- Who owns it
- By when (if specified)
- Any dependency or context needed

Feed action items into whatever tracking the Scrum Master uses (sprint board, a task list, the team's shared doc, etc.).

For action items that span teams or need management attention, format a clear message: what's needed, from whom, by when, and why it matters to the sprint.

## Stakeholder reporting and status

When the Scrum Master needs to report status to management or stakeholders:

- **Sprint status:** on track / at risk / off track, with one-line reason
- **Sprint goal:** state it clearly and whether it's still achievable
- **Completed this sprint:** brief list of what's done
- **In progress:** what's moving and any items at risk
- **Blockers:** what's blocked, by what, and what's being done about it
- **Risks:** anything that could affect the next sprint or the broader program (e.g. ATO delays, cross-team dependencies, resource constraints)
- **Asks:** what you need from management or other teams — specific and time-bound

Keep it concise. Management wants the headline, the risk, and the ask — not the full board.

For the FRADevOps managers meeting (bi-weekly, Tuesdays 10:30 AM EST), prepare:
- A one-paragraph sprint/program status
- Any blockers or risks that need escalation or visibility
- Specific asks (e.g. "need Shristy to follow up on the RSIS helpdesk contact", "need ATO reviewer assignment for the Records Management digitization work")

## Agile coaching and anti-patterns

Watch for these and call them out gently:

- **Standups turning into problem-solving sessions** — park the deep dive, take it offline
- **Sprint goal being unclear or forgotten** — restate it, make sure the team knows what "done" for the sprint looks like
- **Items in progress for too long** — a task that's been "in progress" for most of the sprint is a risk
- **Carry-over every sprint** — indicates planning or sizing issues; worth a retro conversation
- **No clear acceptance criteria** — leads to rework and disagreements at review time; push for clarity before committing
- **Retro action items not followed up** — if last sprint's retro actions didn't happen, ask why and make the next set more concrete
- **Stakeholders not seeing progress** — more frequent, concise updates; show completed work, not just activity

## Inputs this skill can work from

- Sprint board / backlog (Jira, Azure DevOps, GitHub Projects, or any tool the team uses)
- Meeting notes or transcripts (standup, planning, review, retro, refinement)
- Team capacity information (vacations, other commitments)
- Velocity/burndown data if available
- Stakeholder or management communication threads
- The FRADevOps project context (OY5/TOMR response, Security ATO requests, Records Management digitization, Google Workspace migration, RSIS helpdesk, etc.)

## Outputs this skill produces

- Standup summary with blockers and follow-ups
- Sprint planning inputs and facilitation prompts
- Review prep: what's done, what to demo, what's deferred
- Retro summary with action items and owners
- Stakeholder status report or escalation message
- Action-item list from any meeting
- Risk/blocker list for the sprint or managers meeting

## How it fits with other skills

- **`morning-triage`** — use for personal daily prioritization; this skill handles the team-facing standup and sprint piece
- **`meeting-action-items`** — this skill extracts and formats action items in a Scrum context with sprint-specific follow-ups
- **`daily-status-digest`** — personal daily summary; scrum-master produces the team/program status
- **`weekly-review-planning`** — personal weekly reset; scrum-master handles sprint-level review and planning
- **`document-to-action-items`** — can be used alongside this skill when action items come from documents rather than meetings

## Examples

**Standup input:**
> "Yesterday: finished the TOMR response draft, waiting on Shristy for review.
> Today: starting the Records Management digitization demo.
> Blockers: need the RSIS helpdesk contact — still waiting on follow-up from last week."

**Scrum-master output:**
> Standup summary:
> - Done: TOMR response draft (pending Shristy's review)
> - In progress: Records Management digitization demo
> - Blocker: RSIS helpdesk contact — follow-up sent last week, still no response. Action: Dan to re-follow up with RSIS today, escalate to Christina if no reply by EOD.
> - Watch: TOMR response review — if Shristy doesn't review by tomorrow, flag as at risk for the sprint goal.

**Retro action item extraction:**
> From retro notes: "The standups have been running long — people keep going into detail."
> - Action: Time-box standups to 15 minutes; park deep dives for after.
> - Owner: Scrum Master (Dan)
> - Due: next sprint start

## Limitations

- This skill helps the Scrum Master do the work better; it doesn't replace the Scrum Master's judgment or the team's ownership of the work.
- It doesn't have direct access to the team's board or tools — it works from what you give it (notes, transcripts, data you paste in).
- For FRADevOps-specific context, feed in the relevant work-stream details (OY5/TOMR, ATO requests, Records Management, Google Workspace migration, RSIS, etc.) so outputs are grounded in the actual program.
