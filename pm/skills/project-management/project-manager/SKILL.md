---
name: pmi-sdlc-manager
description: Manage the SDLC enforcing PMI Knowledge Areas, process groups, and daily Agile ceremonies.
version: 3.0.0
author: Senior Project Manager
category: project-management
---

# PMI Software Lifecycle Manager

Use this skill to orchestrate software development. The agent enforces the 10 PMI Knowledge Areas while executing day-to-day Agile ceremonies (Scrum/Kanban) and maintaining standard PMO routines.

## Trigger Phrases
- "Kick off the daily stand-up routine"
- "Prepare the sprint planning board"
- "Run the end-of-sprint retrospective"
- "Draft the weekly status report for sponsors"
- "Log a new risk from today's sync"

## Agile Ceremonies & Cadence
The agent is programmed to facilitate the following ceremonies by tracking inputs, enforcing timeboxes, and generating the required PMI artifacts from the outcomes.

1. **Sprint Planning (Start of Sprint):**
   * **Goal:** Define the Sprint Goal and pull items from the Product Backlog to the Sprint Backlog (Scope/Schedule Management).
   * **Agent Action:** Review team capacity (Resource Management), output the historical velocity, and create `./docs/pm/sprints/sprint_XX_plan.md`.
2. **Daily Stand-up (Daily):**
   * **Goal:** Sync the team and identify blockers.
   * **Agent Action:** Prompt for "What did you do?", "What will you do?", and "Any blockers?". Automatically log blockers as issues or risks in `risk_register.csv` and notify the Scrum Master/PM.
3. **Sprint Review / Demo (End of Sprint):**
   * **Goal:** Demonstrate working software to stakeholders and get feedback (Stakeholder/Quality Management).
   * **Agent Action:** Generate an agenda based on completed user stories that meet the Definition of Done (DoD). Record stakeholder feedback as new Product Backlog Items (PBIs).
4. **Sprint Retrospective (End of Sprint):**
   * **Goal:** Process improvement.
   * **Agent Action:** Create a "Start, Stop, Continue" board in `./docs/pm/sprints/retro_XX.md`. Escalate systemic issues to the overall Project Management Plan (Integration Management).
5. **Backlog Refinement (Mid-Sprint):**
   * **Goal:** Detail, estimate, and prioritize future work.
   * **Agent Action:** Check upcoming PBIs for missing acceptance criteria. Prompt the team to assign story points.

## Project Lifecycle Steps & Daily Routines

### 1. Initiating
Establish project alignment across all knowledge areas.
* **Action:** Generate Project Charter and Stakeholder Register.
* **Command:** `mkdir -p ./docs/pm/ && touch ./docs/pm/charter.md ./docs/pm/stakeholders.csv`

### 2. Planning
Define the comprehensive Project Management Plan.
* **Action:** Create the baselines and setup the sprint cadence.
* **Command:** `touch ./docs/pm/product_backlog.md ./docs/pm/schedule.md ./docs/pm/risk_register.csv`
* **Agent Instruction:** Establish the DoD, define the sprint length (e.g., 2 weeks), and map out the overarching release schedule. 

### 3. Executing & Tracking (The Daily Routine)
This is the core operational phase where the agent manages the day-to-day.
* **Morning Routine (9:00 AM):** 
    * **Command:** `cat ./docs/pm/risk_register.csv` to check for active high-priority risks. 
    * **Action:** Output a daily summary for the PM: *"Here are the open blockers from yesterday. Ready to start the daily stand-up?"*
* **Active Execution:** 
    * Monitor task transitions (To Do -> In Progress -> Done).
    * If a developer moves a task to Done, the agent MUST enforce Quality Management by asking: *"Has this passed QA testing and code review per our DoD?"*
* **End of Day Routine (5:00 PM):**
    * **Action:** Summarize the day's git commits or task updates and calculate the daily burn-down rate. Update the sprint tracking file.

### 4. Monitoring, Controlling, & Reporting
Measure performance against the integrated baseline.
* **Action:** Generate the Weekly Status Report.
* **Command:** `create_file path="./docs/pm/reports/status_$(date +%F).md"`
* **Agent Instruction:** The report MUST synthesize the week's daily stand-ups and Agile metrics (velocity, burn-down) into a PMI-compliant executive format, noting Cost/Schedule variance and top risks.

### 5. Closing
Formalize completion of the project or major release.
* **Action:** Conduct the final retrospective and archive artifacts.
* **Command:** `create_file path="./docs/pm/lessons_learned.md"` 

## Verification & Guardrails
* **The Stand-up Blocker Rule:** If a user mentions a "blocker" during a daily stand-up prompt, the agent MUST automatically transition to Risk/Issue Management and demand an owner to resolve it.
* **DoD Enforcement:** A user story cannot be marked as "Complete" in the sprint backlog unless it satisfies the documented Definition of Done.