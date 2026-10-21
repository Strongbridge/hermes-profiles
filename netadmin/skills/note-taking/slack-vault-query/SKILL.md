---
name: slack-vault-query
description: Answer Slack questions by searching saved Obsidian notes.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Slack, Obsidian, query, search, vault]
    related_skills: [slack-to-obsidian, obsidian]
---

# Slack Vault Query Skill

Answers natural-language questions by reading and synthesizing content from the local Obsidian vault — specifically notes saved via the `slack-to-obsidian` skill into the `SB-Hermes/` vault root.

## When to Use

Use when a Slack message addressed to the Hermes agent asks a question that should be answered from information previously saved to the vault. This includes:

- Status questions: "what's the latest status of [project]?"
- History questions: "what did we decide about [topic]?"
- Recall questions: "what was in the note about [topic]?"
- Summary questions: "what have I saved about [topic]?"
- Timeline questions: "what's the latest on [topic]?" / "what changed recently?"

The agent must be addressed (`@hermes`, `@hermes Agent`); ambient questions not addressed to the agent are not treated as vault queries.

## Trigger Signals

There is no fixed trigger phrase for queries — the skill activates when the addressed message is recognizably a question about saved vault content. Signals include:

- "what is the latest status of..."
- "what's the status of..."
- "what did we decide/save/note about..."
- "what have I saved about..."
- "what's the latest on..."
- "tell me about [topic] from the notes"
- "what was in the note about..."
- "what changed regarding..."
- "what do the notes say about..."
- "search the vault for..."
- "what notes do I have about..."

A message counts as a vault query when it is both addressed to the agent and asks about information that plausibly lives in the `SB-Hermes/` vault. Purely conversational questions ("how are you?", "what time is it?") are not vault queries.

## Query Behavior

When a vault query is recognized, the agent:

1. **Extracts the query intent** — identify the topic, project, or subject being asked about, and any time constraint (latest, recent, yesterday, this week, etc.). For "what is the latest status of the FRA DevOps Projects", the topic is "FRA DevOps" and the constraint is "latest status".

2. **Searches the `SB-Hermes/` vault** — use `search_files` with:
   - `target: "content"`
   - `path`: `C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian\SB-Hermes`
   - `file_glob: "*.md"`
   - `pattern`: a regex built from the key terms in the question, OR a broad search when the question is vague

   When the question is specific (named project, person, topic), constrain the search to those terms. When it's vague ("what have I saved?"), do a broad search and return a summary of available notes.

3. **Reads matching notes** — for each search hit, determine if the note is relevant to the question. Read the full note (frontmatter + body) with `read_file`. If there are more than ~5-8 matches, prioritize the most recent and most keyword-dense matches — do not read everything if the set is large.

4. **Synthesizes the answer** — compose a response from the note content. Rules:
   - Answer from the note content only. Do not add information the notes don't contain.
   - If multiple notes touch the topic, synthesize across them — note agreements, contradictions, or evolution over time.
   - If the question has a time constraint ("latest"), prioritize the most recent relevant notes and say what they say.
   - Preserve the specificity of the notes — if a note says "as of June 2026", include that timeframe rather than presenting it as current.
   - If the notes don't cover the question, say what the vault DOES contain related to the topic, and state clearly that the specific question isn't answered by saved notes.

5. **Cites sources** — in the Slack reply, list the filenames of the notes that informed the answer (e.g. `Sources: 2026-08-10-100000-fra-devops-status.md, 2026-08-18-140000-fra-devops-update.md`). This lets the user go read the originals if they want detail.

6. **States confidence / gaps** — if the answer is based on limited or dated notes, say so. "Based on two notes from July 2026 — nothing more recent is in the vault." If the vault has nothing on the topic, say: "No notes in the vault match [topic]."

## Search Strategy

**Specific topic queries** (e.g. "FRA DevOps status", "SharePoint migration", "federal team preferences"):

- Build a regex from the meaningful terms: `FRA|DevOps|status|project`
- Search `SB-Hermes/*.md` content
- Read the top matches

**Time-constrained queries** (e.g. "latest status", "what changed this week"):

- Search broadly for the topic in `SB-Hermes/*.md`
- Filter by date using the note filenames (`YYYY-MM-DD-HHMMSS-*.md`) and frontmatter `created` timestamps
- Prioritize newest matching notes

**Broad recall queries** (e.g. "what have I saved about DevOps?", "what notes do I have?"):

- Search for the topic broadly in `SB-Hermes/*.md`
- Return a summary listing: filename, date, content_summary from frontmatter, and a one-line gist of each note
- Do not read every note in full unless asked

**Vague/no-topic queries** (e.g. "what's in the vault?", "what notes do I have?"):

- List all notes in `SB-Hermes/` with filename, date, and content_summary
- Group by date or topic if there's enough to organize
- Do not read in full unless specific notes are requested

## Answer Format in Slack

The reply format depends on the query, but generally:

**Direct answer with sources:**
```
The latest saved status on FRA DevOps (from notes on Aug 20 and Aug 10):

- Aug 20 note: 40 apps, 300 SharePoint sites, .NET/React/Angular. Federal team prefers async updates. On track.
- Aug 10 note: earlier status — 38 apps migrated, 2 pending. Same tech stack.

Sources: 2026-08-20-140000-fra-devops-status.md, 2026-08-10-100000-fra-devops-migration.md
```

**When the vault doesn't have it:**
```
No notes in the vault specifically cover [topic]. The closest matches are:
- 2026-08-15-120000-other-topic.md — mentions [related thing] in passing

Nothing more specific is saved.
```

**When listing available notes:**
```
You have 6 notes touching DevOps in the vault:

1. 2026-08-20-140000-fra-devops-status.md — FRA DevOps contract status, 40 apps/300 SP sites
2. 2026-08-18-090000-devops-tooling.md — CI/CD tooling update
3. ... (etc)
```

Keep the reply readable in Slack — avoid dumping raw YAML frontmatter or full note text unless the user asks for a specific note.

## Scope and Limitations

- **Searches the `SB-Hermes/` vault** — this is the active Obsidian vault on this system. Notes saved outside this folder (e.g. in `Conversations/`, `Announcements/`, or `slack/` at the parent level) are invisible to Obsidian and will not be found by queries. If the user asks about something that might be in one of those sibling folders, mention that it exists on disk but is outside the Obsidian vault.
- **Vault state reflects what's synced.** Notes saved from an offline machine may not be present until OneDrive syncs them to this machine. If a note was just saved and isn't found, mention the possible sync delay.
- **No inference beyond the notes.** The agent synthesizes and summarizes, but does not invent status, decisions, or facts not present in the saved notes.
- **No writes.** Querying does not modify the vault. It is read-only.

## What Not to Do

- Do not answer from memory or general knowledge when the question is about saved vault content. Answer from the notes.
- Do not pretend a note says something it doesn't.
- Do not return raw note dumps unless asked.
- Do not search outside `SB-Hermes/` and present the results as vault notes.
- Do not treat a missed note (sync delay) as "no notes exist" — mention the possibility.

## Example Exchange

**User (Slack):** `@hermes what is the latest status of the FRA DevOps Projects`

**Agent:**
1. Extracts topic: FRA DevOps, constraint: latest status
2. Searches `SB-Hermes/*.md` for FRA|DevOps|status
3. Reads matching notes, prioritizes most recent
4. Synthesizes answer from note content
5. Returns:

```
Latest saved status on FRA DevOps Projects (from your saved notes):

- **Aug 20, 2026** — Contract covers 40+ applications and ~300 SharePoint sites. Stack is .NET with React/Angular front-ends. Federal team prefers async updates. Status: on track.
- **Aug 10, 2026** — Earlier point: 38 of 40 apps migrated, 2 pending. Same tech stack. Federal relationship good.

Nothing in the vault covers the period after Aug 20 — no more recent status note.

Sources: 2026-08-20-140000-fra-devops-status.md, 2026-08-10-100000-fra-devops-migration.md
```
