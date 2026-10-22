---
name: daily-from-notes
description: "Daily brief from local notes: today's items, waiting, stale."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Daily-Brief, Planning, Notes, Local-Capture]
---

# Daily Brief from Local Notes

Produce a lightweight, action-oriented "what should I be doing today" answer from the user's locally captured notes — meeting transcripts, project status reports, task inventories, and ad-hoc task capture. This is the local-notes complement to the Gmail+Calendar daily brief in `google-workspace`; use it when the user's primary capture is local notes rather than (or in addition to) email and calendar.

## When to Use

- "What should I be doing today?"
- "What's on my plate?"
- "Anything I'm waiting on?"
- "What did I leave undone?"
- A daily check-in where the user's notes are the authoritative source.

Don't use for: weekly reviews (`weekly-review-planning`), Gmail+Calendar-only briefs (`google-workspace` daily-brief reference), or when the user explicitly wants calendar/email sources.

## Procedure

### 1. Locate the note capture

Identify the user's local note capture — the folder or set of files where meeting notes, project status, and task items land. Discover the capture location from the vault, not from assumptions; different users organize differently. For many users this is a dated-notes subfolder of the Obsidian vault, but the shape varies.

### 2. Read recent notes (last 1–3 days)

Read the most recent meeting notes, project status reports, and task trackers. Focus on:
- Carry-over action items with owners and due dates
- Items marked pending / waiting / follow-up
- Overdue or at-risk items
- Newly logged risks or escalations

Do not read everything — target notes that changed recently or are flagged as open.

### 3. Read stale-waiting items

Read items flagged as "pending follow-up" or "waiting on" even when the note is older — these are the items that silently age. A follow-up from weeks ago that never got resolved is often more important than a fresh note.

### 4. Synthesize into a prioritized today-list

Group into:
- **Do today / time-sensitive** — items with a near due date, overdue, or that the note itself says to handle today
- **Waiting on others** — items where the user is waiting for a reply or action from someone else; name the person and the last touch date
- **Stale / needs a decision** — items open without movement, where a nudge or decision is needed

### 5. Flag what's NOT covered

State explicitly what sources were checked and what was NOT checked (e.g., "Checked SB-Hermes meeting notes and project status reports; did not check email or calendar"). A notes-only brief is not a substitute for calendar/email awareness; name the gap rather than silently claiming completeness.

## Output Shape

Present as a short prioritized list, not a dump. Each item: what it is, why it's on the list today, and the owner/next step if known. Lead with the most time-sensitive.

- **Do today** — item, source note, why today
- **Waiting / follow-up** — item, who it's waiting on, last touch
- **Recent wins / completed** — optional; only if the user wants confirmation or morale

Keep it short. The user asked "is there anything we should be doing today?" — answer that question directly; do not pad with everything in the notes.

## Pitfalls

- Reading every note in the vault instead of the recent/open ones — the answer gets buried in noise.
- Treating a "pending follow-up" note as resolved because time passed — silence is not completion; flag it for a nudge.
- Failing to name the source note for each item — the user can't verify or act on an unattributed item.
- Presenting a notes-only brief as complete — name the coverage gap (calendar, email, other inboxes not checked).
- Carrying every open item forward as equally urgent — rank by time-sensitivity and consequence, not by existence.

## Verification

- [ ] Recent notes (last 1–3 days) were read for carry-over actions.
- [ ] Stale waiting/follow-up items were checked, not just recent notes.
- [ ] Each listed item traces to a specific note and has a reason for being on the list today.
- [ ] Coverage gaps (sources not checked) are stated.
- [ ] The answer is short and prioritized, not a full note dump.
