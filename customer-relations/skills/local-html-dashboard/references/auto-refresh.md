# Adding auto-refresh to a static dashboard

## Pattern

```javascript
async function refreshDashboard() {
  // 1. Update timestamp
  document.getElementById('update-time').textContent = timeStr();

  // 2. Fetch all data files
  const [pm, ba, sm] = await Promise.all([
    loadJSON('data/pm_status.json'),
    loadJSON('data/ba_status.json'),
    loadJSON('data/sm_status.json')
  ]);

  // 3. Render everything (clear and rebuild dynamic sections)
  // ...
}

async function init() {
  await refreshDashboard();
  setInterval(refreshDashboard, 60000); // 60 seconds
}

init();
```

## Key points

- **Clear and rebuild dynamic sections** (task grid, blockers list) on each refresh to avoid duplicate elements accumulating.
- **Update the timestamp inside `refreshDashboard()`**, not just in `init()`, so it reflects each refresh cycle.
- **60 seconds** is a reasonable default interval; adjust based on how often the data sources actually update.
- **Watch for overlapping requests** if data files are large or fetch is slow — consider a guard flag if the refresh interval is shorter than the fetch time.
- **The data files are snapshots** written by external processes. If the sources don't update, the dashboard won't either — check the data file `last_updated` field to confirm freshness.
