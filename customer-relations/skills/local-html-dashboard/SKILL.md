---
name: local-html-dashboard
description: Build and debug local HTML dashboards with live JSON data.
---

## Procedure

### 1. Serve the dashboard

```bash
cd /path/to/dashboard
python3 -m http.server 8080
```

The server serves `index.html` and any `data/*.json` files from the current directory. Browsers fetch JSON via `fetch('data/file.json')` — same-origin, no CORS issues. Verify the server is running and data files return 200 before debugging the dashboard itself.

### 2. Edit and validate JavaScript before serving

Edit the HTML/JS/CSS in place. Before serving changes, validate the JavaScript syntax:

```bash
node -e "const fs=require('fs'); const html=fs.readFileSync('index.html','utf8'); const s=html.indexOf('<script>')+8; const e=html.indexOf('</script>'); new Function(html.slice(s,e)); console.log('JS syntax: VALID')"
```

A syntax error in `<script>` (missing closing brace, unclosed template literal, mismatched paren) breaks the entire script silently — the page renders the static HTML but none of the dynamic content appears, often stuck on a "Loading..." placeholder. The browser console shows the error but the user may not check it. Always validate after editing the script block.

### 3. Add auto-refresh

When the dashboard should update without manual reload:

1. Extract all rendering logic into a named async function (e.g., `refreshDashboard()`)
2. Have `init()` call it once: `await refreshDashboard()`
3. Set up interval: `setInterval(refreshDashboard, 60000)` (60 seconds)
4. Update the "last updated" timestamp inside `refreshDashboard()` so it reflects each refresh cycle, not just initial page load

The data files are snapshots written by external processes (bots, scripts). The dashboard picks up new data on the next refresh cycle — no manual reload needed. See `references/auto-refresh.md` for the full recipe.

### 4. Style consistency across status cards

When multiple status cards (PM, BA, SM) share a layout, give them a consistent visual language:

- Use colored left borders to indicate status (green/yellow/red/blue/gray)
- Use badge functions that map status strings to emoji + color pairs (e.g., `healthBadge()`, `sprintBadge()`)
- Add a CSS class for each status color on the card (`.health-card.blue`, `.health-card.gray`, etc.)
- Map each data source's status vocabulary through a dedicated badge function rather than rendering raw strings

## Pitfalls

- **Patch tool with partially-read files:** When a file was last read with `offset`/`limit` pagination, the `patch` tool warns "was last read with offset/limit pagination (partial view)." The write may still proceed, but `old_string` matching can fail with "Could not find a match" if your search string spans regions not in the partial view. Read the full file first, or use `write_file` for large reconstructions. This affects any file type, not just HTML.

- **Silent JS failures:** A syntax error in `<script>` prevents the entire script from running. The page shows the static HTML shell but no dynamic content. Validate with Node before serving. Braces and template literals are the most common culprits — count opening/closing braces as a quick sanity check.

- **JSON fetch failures are silent:** A `loadJSON` helper that catches errors and returns `null` will leave placeholder text ("Awaiting...", "No assessment provided") instead of crashing. If a card shows placeholders, check that the server is running and the data file path is correct before debugging the rendering logic.

- **Orphaned code after incomplete patches:** When a `patch` replacement cuts a function short (e.g., replacing the start of `init()` but leaving the old body at module scope), the result is syntactically invalid JavaScript with code outside any function. Always verify brace balance and that all code is inside a function or the script scope after a patch that modifies function boundaries.

## References

- `references/auto-refresh.md` — recipe for adding auto-refresh to a static dashboard
