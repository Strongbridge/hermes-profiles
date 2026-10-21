---
name: dashboard-maintenance
trigger: "Use when fixing bugs or overlap in the dashboard HTML"
description: "Fix dashboard HTML bugs across the deploy pipeline."
version: 1.0.0
author: Dan Righter, Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [dashboard, html, fix, maintenance, firebase, deploy]
    related_skills: [firebase-dashboard-deploy, dashboard-module, python-utility]
---

# Dashboard Maintenance

Fix bugs, layout issues, overlap, and visual problems in the CLIN9 dashboard HTML files.

## When to Use

- User reports visual bugs, overlapping elements, layout issues in the dashboard
- Timeline nodes overlap, cards collide, CSS conflicts
- Any HTML/CSS fix needed in the dashboard files
- User asks to "reload" or "refresh" the dashboard after a fix

## Don't Use For

- Adding new tabs/modules → dashboard-module skill
- Deploy config, envsubst, Firebase Hosting issues → firebase-dashboard-deploy skill
- Python calculation utilities → python-utility skill

## File Structure (CRITICAL — all three copies must be patched)

The dashboard exists in three copies. Patching only one means the fix gets lost:
1. `v2_fixed/index.html` — source template; envsubst produces the deployed file from this
2. `index.html` — deployed output at the dashboard root; what Firebase Hosting serves
3. `dashboard-standalone.html` — standalone copy with hardcoded Firebase config

**Rule: always patch all three files for any visual/HTML fix.** If you only patch `index.html`, the next `deploy.sh` run overwrites it from the template. If you only patch `v2_fixed/index.html`, the live site doesn't change until redeploy.

## Procedure

1. **Read all three files** — `dashboard-standalone.html`, `index.html`, `v2_fixed/index.html`. Identify the overlapping code in each.
2. **Patch all three** — apply the same fix to each file. Use `patch` with unique `old_string` matches per file.
3. **Check for CSS collisions** — inspect the style section for conflicting rules (e.g., `.node-label` defined in both main and mobile media queries). Add `white-space:nowrap` where text overflow causes overlap.
4. **Verify responsive gap** — for timeline/positioned elements, replace fixed pixel gaps with `Math.max(MIN, Math.min(MAX, (avail - padding) / count))` calculations using `vp.clientWidth`.
5. **Use short labels** — the `TT` array has `short` names for compact display; use `task.short` not `task.name` in tight spaces.
6. **Reload the dashboard** — the user must refresh their browser (Ctrl+Shift+R to bypass cache). There is no server-side reload; the HTML files are static.
7. **Deploy if needed** — if the user wants the fix live for others, run the deploy pipeline (see firebase-dashboard-deploy skill). Remember `deploy.sh` regenerates `index.html` from `v2_fixed/index.html` via envsubst.

## Pitfalls

- **Fix overwritten on next deploy** — patching only `index.html` without also patching `v2_fixed/index.html` means `deploy.sh` envsubst overwrites the fix. Always patch both the template and the deployed output.
- **JS function definitions must be patched in all three copies** — `window.signInWithGoogle` (and any `window.*` function) defined in the `<script type="module">` block lives in the same code as the Firebase config. If you patch `index.html` without also patching `v2_fixed/index.html`, the next deploy regenerates `index.html` from the template and the fix is lost. `dashboard-standalone.html` is patched independently. Same rule as CSS fixes in dashboard-maintenance.
- **Fixed gaps cause overlap** — hardcoded pixel gaps (e.g., `const gap=140`) overflow when task names are long. Use responsive gap calculation based on `vp.clientWidth` and short labels (`task.short`).
- **CSS text wrapping** — `.node-label` without `white-space:nowrap` wraps onto the progress bar row, causing visual overlap. Add `white-space:nowrap` to label styles.
- **Inline HTML label/value spacing** — `</strong><span>` in dashboard strings renders label and value with no gap (e.g., `Relationship Health` stuck to its value). Always insert `&nbsp;` between the closing `</strong>` tag and the opening `<span>` tag in inline badge/cards.
- **Browser cache** — after patching files, the user's browser may serve cached HTML. Force refresh with Ctrl+Shift+R.
- **API key still masked after patch** — `index.html` may show `apiKey: "AIzaSy...K2q4"` after a patch that was supposed to fix it. The `...` is a truncated placeholder, NOT a real key. The browser sends this to Firebase auth and gets rejected silently (no console error visible on the dashboard page). Fix: verify the actual bytes in index.html with `python3 -c "import re; print(repr(re.search(r'apiKey:\s*\"([^\"]+)\"', open('index.html').read()).group(1)))"` — if it contains `...`, the patch didn't reach the file or was overwritten by envsubst. Patch `v2_fixed/index.html` (the template) with the real key, then re-run envsubst, then redeploy. Never patch only the root `index.html` without also patching `v2_fixed/index.html` — deploy regenerates the root from the template.
- **Firebase Hosting REST API deploy is broken** — `populateFiles` + upload + finalize cycle consistently fails (400 Bad Request on uploads, FAILED_PRECONDITION on finalize). The signed upload URLs from `populateFiles` reject content uploads. Use `firebase deploy` CLI instead of the REST API for all deploys.

## Verification

- All three HTML files contain the same fix (grep for the patched string in each)
- Timeline nodes use short labels, not full names
- Gap calculation uses `vp.clientWidth` not a fixed constant
- `white-space:nowrap` present on `.node-label` rules
- Dashboard reloads without overlap in the browser