---
name: dashboard-module
trigger: "Use when adding a tab to a Vite + Firebase SPA dashboard"
description: "Add a new tab/module to a Vite + Firestore SPA dashboard."
version: 1.0.0
author: Dan Righter, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vite, firebase, dashboard, module, tab, navigation]
    related_skills: [firebase-dashboard-deploy, python-utility]
---

# Dashboard Module Addition

Add a new tab/page to a Vite + Firestore SPA dashboard (hash-based routing, ES modules).

## When to Use

- User asks for a new tab, page, or feature module in the dashboard
- Dashboard follows the Vite + Firestore pattern (hash router, ES module per tab, Firestore for state)

## Don't Use For

- Pure Python/CLI tools (use python-utility)
- Firebase deploy/config changes (use firebase-dashboard-deploy)
- Framework-native routing (React Router, Vue Router) — different pattern

## Procedure

1. **Inspect the existing tab pattern first.** Read one existing tab module (e.g. `Dashboard.js`, `RiskRegister.js`) to confirm the export shape: `render` returns HTML string, `init(userProfile, clientConfig)` sets up listeners and returns cleanup function. Read `main.js` for routes object shape and `Sidebar.js` for menuItems shape.
2. **Create the module** in `src/<kebab-name>.js`. Export `render` and `init`. Keep calculation engine self-contained inside the module or import from a shared file; no Firestore dependency unless the tab needs live data.
3. **Register the route** in `main.js`: add import and `'route-name': { render: X, init: initX }` to the routes object.
4. **Add sidebar item** in `Sidebar.js`: append `{ id: 'route-name', label: 'Display Name', icon: 'emoji' }` to `menuItems`.
5. **Add CSS** in `style.css`: use existing class names (`.data-table`, `.stat-card`, `.btn-primary`, `.glass`, `.modal-overlay`). Add component-specific classes scoped to the tab.
6. **Verify syntax**: `node --check src/<module>.js` and `node --check src/main.js`.
7. **Verify load**: import the module in node and call `render()`; confirm HTML contains expected IDs.

## Pitfalls

- **Forgot to register route AND sidebar** — tab is inaccessible. Both `routes` in main.js and `menuItems` in Sidebar.js must be updated together.
- **init returns nothing instead of cleanup** — the router expects `currentCleanup = res` then calls it on unmount. Return the unsubscribe function (Firestore listener, interval, etc.) or `null`.
- **Hash routing conflicts** — the sidebar `data-page` attribute must match the route key exactly, and `window.location.hash` drives navigation. A typo means the tab never activates.
- **CSS class collision** — the dashboard uses semantic class names (`stat-card`, `data-table`, `badge-high-risk`). Reuse them instead of inventing new ones; check style.css before adding a new class.
- **Missing null guards in init** — elements queried in init may not exist if render changed. Always guard: `const el = document.querySelector('#id'); if (!el) return;`.

## Verification

- `node --check` passes on all modified JS files
- Module loads: `import` succeeds, `render()` returns string with expected IDs
- Sidebar and route keys match exactly (typo is the #1 bug)
