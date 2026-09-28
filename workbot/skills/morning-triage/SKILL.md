---
name: morning-triage
description: Organize today's tasks into a prioritized checklist.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [triage, morning, prioritization, task-list, Slack, Obsidian]
    related_skills: [slack-to-obsidian]
---

# Morning Triage Skill

Takes a list of items a user pastes into Slack (emails to answer, fires to put out,
deadlines approaching, routine tasks) and organizes them into a prioritized checklist.
The output is a triage note saved to SB-Hermes and a readable summary in Slack.

## When to Use

Use when a Slack message addressed to the Hermes agent contains a list of things the user
needs to deal with and asks for help organizing, prioritizing, or just "what's my day look
like". Typical triggers:

- `@hermes triage: here's what I'm facing today: ...`
- `@hermes what's my day look like`
- `@hermes help me prioritize`
- `@hermes morning triage: [list of items]`
- `@hermes organize these tasks`

The agent must be addressed (`@hermes`, `@hermes Agent`); ambient requests are not treated
as triage requests.

## Trigger Signals

- "triage" + list of items
- "what's my day" / "what's my day look like"
- "help me prioritize" / "organize these"
- "morning triage" + list
- A pasted list of tasks/emails/fires preceded by "here's what I'm facing" or similar

A message counts as a triage request when it is both addressed to the agent and contains a
list of actionable items the user wants organized.

## Input Format

The user can paste items in any format. Examples:

```
@hermes triage: here's what I'm facing today:

- 17 personnel reviews due by Friday (BambooHR)
- QPR meeting at 2pm (already done, PPT ready)
- Team status updates from 30 people (need to chase)
- Weekly report skeleton to fill in (NotebookLM data challenge)
- GMail inbox — about 40 unread across DOT and Strongbridge
- Google Chat messages waiting for response
```

Or freeform:
```
@hermes what's my day look like — got 40 emails in Gmail, 17 reviews due, team status to chase, weekly report to finish.
```

The agent extracts the actionable items regardless of format.

## Triage Logic

When a triage request is recognized, the agent:

1. **Extracts the items** — identify each distinct actionable item from the user's input.
   May be bulleted, numbered, or freeform prose. Split on clear boundaries (newlines, bullet
   markers, conjunctions). If an item is vague ("a lot of emails"), keep it as one item but
   note the nature.

2. **Classifies each item** into one of these buckets:
   - **FIRE** — urgent, time-sensitive, must act now today (e.g. "meeting in 30 min",
     "production down", "angry client waiting", "deadline today")
   - **DEADLINE** — due soon but not this instant (e.g. "due by Friday", "this week",
     "end of month"). Act on this week.
   - **ROUTINE** — regular recurring task, can be scheduled at the user's discretion
     (e.g. "weekly report", "team status check", "inbox zero")
   - **FOLLOW-UP** — waiting on someone else, no immediate action until a response arrives
     (e.g. "waiting on HR for API access", "pending approval")
   - **WATCH** — something to keep an eye on but no action now (e.g. "monitor the FRA pipeline",
     "check on the status of X later")

3. **Assigns a suggested order within each bucket** — fires first (chronological within fires
   if times are known), then deadlines (earliest first), then routine, then follow-ups, then
   watch items.

4. **Adds a one-line action suggestion** for each item when helpful (e.g. "send HR the API
   access request email", "schedule 30 min to chase team status"). Keep suggestions brief.

5. **Saves the triage note** to SB-Hermes:
   ```
   C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes
   ```
   Filename: `YYYY-MM-DD-HHMMSS-triage.md`
   Example: `2026-08-25-090000-triage.md`

6. **Writes frontmatter**:
   ```yaml
   ---
   created: 2026-08-25T09:00:00-04:00
   source: slack
   triggered_by: "@hermes morning triage"
   type: triage
   content_summary: "Triage list — 5 items across fires, deadlines, routine"
   ---
   ```

7. **Writes the body** — the prioritized checklist, organized by bucket:

   ```markdown
   # Triage — August 25, 2026

   ## Fires (act now)
   1. **QPR meeting at 2pm** — already prepared (PPT ready). Action: attend.
   2. ...

   ## Deadlines (this week)
   1. **17 personnel reviews due Friday** — BambooHR. Action: ask HR for API access today.
   2. ...

   ## Routine (schedule at your discretion)
   1. **Weekly report skeleton** — fill in from NotebookLM data. Data challenge is the
      second brain accuracy. Action: work on when data is available.
   2. ...

   ## Follow-ups (waiting on someone)
   1. **HR API access for BambooHR** — requested, waiting. Action: follow up if no response
      by tomorrow.
   2. ...

   ## Watch
   1. **FRA pipeline status** — monitor. Action: check daily status digest for updates.
   ```

8. **Confirms in Slack** — reply with the prioritized summary and the filename:
   ```
   Triage organized — 5 items across 5 buckets.

   Fires (2): QPR meeting, production issue
   Deadlines (2): 17 reviews due Friday, weekly report
   Routine (1): team status chase
   Follow-ups (1): HR API access
   Watch (1): FRA pipeline

   Saved to SB-Hermes: 2026-08-25-090000-triage.md
   ```

## Running Triage Note

The user can update a triage note throughout the day. If the user says "added: X" or "done:
Y" in a follow-up message, the agent updates the saved triage note (mark items done, add new
items to the appropriate bucket). The agent can also be asked "what's still open?" and reads
the triage note to report remaining items.

To update: the agent reads the existing triage note, patches the body (strikethrough done
items with `~~item~~`, adds new items to the right bucket), and saves.

## Morning Kickstart

When the user says "@hermes what's my day look like" WITHOUT pasting a new list, the agent:

1. Reads the most recent triage note from SB-Hermes (today's, or the most recent one)
2. Reads any status notes saved today (via `daily-status-digest` logic — blockers first)
3. Synthesizes a combined view: triage items + team blockers that need action
4. Returns a prioritized morning checklist

This bridges the triage skill with the status digest skill — team blockers bubble up as
action items in the user's morning view.

## What Not to Do

- Do not invent items the user didn't mention.
- Do not over-classify — if an item is genuinely ambiguous, put it in the most conservative
  bucket (watch or routine) and flag it.
- Do not make decisions for the user about time allocation — suggest order, not schedule.
- Do not save triage notes outside SB-Hermes/.
- Do not treat triage as a substitute for the user's judgment about what's truly urgent.

## Example Exchange

**User (Slack):**
```
@hermes morning triage: here's what I'm facing today:
- 17 personnel reviews due Friday
- QPR meeting at 2pm (PPT ready)
- Team status from 30 people — need to chase
- Weekly report skeleton to fill
- 40 unread emails in Gmail
- Google Chat waiting for response
```

**Agent:**
1. Extracts 6 items
2. Classifies: QPR = fire (scheduled), reviews = deadline (Friday), team status = routine,
   weekly report = routine, emails = routine, Google Chat = follow-up
3. Writes triage note
4. Returns:
```
Triage organized — 6 items across 4 buckets.

Fires (1): QPR meeting at 2pm (PPT ready — just attend)
Deadlines (1): 17 personnel reviews due Friday — ask HR for API access today
Routine (3): team status chase, weekly report, 40 unread Gmail emails
Follow-ups (1): Google Chat messages waiting

Saved to SB-Hermes: 2026-08-25-090000-triage.md
```
