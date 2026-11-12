# Git Push Credentials

## Symptom
`git push -u origin main` hangs or times out with no output. `GIT_TRACE=1` shows `git credential-helper-selector get` spinning indefinitely, then `GIT_TERMINAL_PROMPT=0` produces no error — just silence.

## Root Cause
The `credential-helper-selector` helper tries to prompt for credentials interactively (TTY), which doesn't exist in non-interactive contexts. Git waits forever for input that never comes.

## Fix Options

### Option A — PAT in remote URL (fastest)
```bash
git remote set-url origin https://<PAT>@github.com/Strongbridge/HermesDashboard.git
git push -u origin main
```
PAT needs `repo` scope. Remove from URL after push: `git remote set-url origin https://github.com/Strongbridge/HermesDashboard.git`.

### Option B — SSH remote
```bash
git remote set-url origin git@github.com:Strongbridge/HermesDashboard.git
git push -u origin main
```
Requires SSH key added to GitHub account settings → SSH keys.

### Option C — Credential helper cache (interactive session only)
```bash
git config credential.helper cache
# Then enter credentials when prompted (works only in a real terminal)
git push -u origin main
```
Does NOT work from background/PTY contexts without a TTY.

## Verification
After push, confirm: `git log --oneline -1` should show the commit, and the repo on GitHub should list the new file.

## Pitfall
`git add -A` without a `.gitignore` picks up parent directories (AppData, browser caches, node_modules). Always create a `.gitignore` first:
```
node_modules/
.env
.env.*
```