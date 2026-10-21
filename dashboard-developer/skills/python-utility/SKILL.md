---
name: python-utility
description: Build Python calculation utilities with dynamic models.
version: 1.0.0
author: Dan Righter, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [python, utility, calculation, cli, datamodel, cpm, estimation]
    related_skills: [spike, test-driven-development]
---

# Python Utility Scripting

Build standalone Python modules for project calculations — data models with dynamic structuring, CLI output, and verified results. No web framework, no external deps beyond stdlib.

## When to Use

- User asks for a calculation/estimation tool in Python
- Need a script with configurable inputs and tabular/structured output
- Verification by running against known inputs (not just "it printed")

## Don't Use For

- Web apps or APIs (use appropriate framework skill)
- One-liner data transforms (just use terminal + Python one-liner)
- Production services with config management, logging, error handling

## Procedure

1. **Define the data model first.** Use `dataclass` with validated fields (duration ≥ 0, no negative weights). Decide what's dynamic (user-added tasks/paths) vs. fixed (algorithm constants).
2. **Build core algorithm.** Isolate the calculation engine from I/O — a `.calculate()` method that returns structured data, not printed strings.
3. **Add CLI/display layer.** `.print_schedule()` or similar for stdout; keep it separate from the engine so it's testable.
4. **Verify with test runs.** Run against a known case with converging parallel paths — the float math must be right at merge points. Assert expected duration and critical path membership.
5. **Check edge cases.** Empty project, single task, cycle detection, zero-duration milestones.

## Pitfalls

- **Floating-point float comparison:** `total_float == 0` fails on rounding; use `abs(x) < 1e-9` (see references/critical-path.md).
- **Cycle detection is non-negotiable:** dependency graphs can loop silently — always validate before running passes (DFS or Kahn's).
- **Merge-point float is where errors hide:** parallel paths converging on one successor — the longest path drives the schedule; the shorter path gets float = diff. Verify at merge points explicitly.
- **Firestore OAuth2 token lacks email claim:** `gcloud auth print-access-token` returns a token without the email claim, causing 403 on Firestore writes. Use Firebase Admin SDK with service account credentials instead (see references/firestore-status.md).
- **PM task_health field mapping:** writer must map status values to color values (`pass`→green, `fail`→red, `on_track`→green, `at_risk`→yellow, `delayed`→red, `pending`→gray) — dashboard reads `health` key, not `status`.
- **API key still masked after patch:** `index.html` may show `apiKey: "AIzaSy...K2q4"` after a patch that was supposed to fix it. The `...` is a truncated placeholder, NOT a real key. The browser sends this to Firebase auth and gets rejected silently (no console error visible on the dashboard page). Fix: verify the actual bytes in index.html with `python3 -c "import re; print(repr(re.search(r'apiKey:\s*\"([^\"]+)\"', open('index.html').read()).group(1)))"` — if it contains `...`, the patch didn't reach the file or was overwritten by envsubst. Patch `v2_fixed/index.html` (the template) with the real key, then re-run envsubst, then redeploy. Never patch only the root `index.html` without also patching `v2_fixed/index.html` — deploy regenerates the root from the template.

## Verification

- Run the module directly (`python script.py`) — demo output prints
- Run a known-case assertion: expected duration + critical path membership
- Check cycle detection raises on circular input
- Confirm zero-duration milestone sits on critical path if it's on the longest chain
