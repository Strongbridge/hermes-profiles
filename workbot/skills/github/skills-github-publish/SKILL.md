---
name: skills-github-publish
description: "Publish Hermes skills to an org GitHub repo."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Hermes, Skills, Distribution, Skill Hub, Org Repo]
    related_skills: [github-auth, github-repo-management]
---

# Publish Hermes Skills to a GitHub Org Repo

Publish user-created Hermes skills to a GitHub repository (e.g. `Strongbridge/Hermes`) so other Hermes users in the org can consume them as a skill hub, and optionally contribute their own skills back.

This is the **distribution/push** side of the workflow. For **consuming** a repo as a skill hub on another machine, see `references/consuming-a-repo-as-skill-hub.md`.

## Prerequisites

- A GitHub classic PAT with `repo` scope in `$GITHUB_TOKEN` (from `$HERMES_HOME/.env` or exported). See `github-auth` skill.
- `git` available (classic PAT embedded in URL works; credential helper also works).
- A destination org/repo that exists and the token can reach (verify with `curl` API before git operations).

## When to Use

- You've created or updated one or more Hermes skills locally and want to push them to the org skill hub repo.
- You need to set up the initial repo structure (skills/ layout, README, .gitignore) for a new skill hub.
- A user asks "how do I get this skill into the repo so the team can use it?"

## How It Works

### Token selection

For org repos, **use a classic PAT with `repo` scope**, not a fine-grained PAT, unless you have verified the fine-grained PAT can reach the org repo via the API first.

PITFALL: a fine-grained PAT with "Repository access: All repositories" often scopes to repos *owned by the PAT's personal account*, not to private org repos, even when the token owner is an org member/owner. For org repos, the "Organization access" grant in fine-grained PAT settings is a separate control from repo access — if missing, the token returns 404 via API and 403 on `git clone` for org repos. Prefer a classic PAT with `repo` scope for org repos; it applies to all repos the authenticated user can reach.

Verify before git operations:

```bash
curl -sS -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/<org>/<repo>"
```

A 200 means the token can see the repo. A 401 means the token is wrong/dead. A 404 or 403 means the token cannot reach the org repo — switch to a classic PAT with `repo` scope, or grant org access in the fine-grained PAT settings.

### Clone the repo (for editing / pushing)

Clone to a **user-owned writable path**, not a volatile or obscure temp location.

PITFALL (this machine): `/tmp` on Windows has a `.git`-visibility quirk — `git clone` and `git status` succeed, but `ls` may not show the `.git` directory afterward, and the directory can appear empty. Clone to `C:/Users/<user>/temp/<repo-slug>` or another user-owned path so file listings and git operations agree.

```bash
# Clone with token embedded in URL (works for classic PAT; fine-grained PAT only after org access verified)
git clone "https://<username>:$GITHUB_TOKEN@github.com/<org>/<repo>.git" /c/Users/<user>/temp/<repo-slug>

# Or use credential helper: git config --global credential.helper store, then plain clone
git clone https://github.com/<org>/<repo>.git /c/Users/<user>/temp/<repo-slug>
```

If the repo is empty (no commits yet), git warns "you appear to have cloned an empty repository" — that's normal; the `.git` is there, just no files to track yet.

### Set git identity

```bash
git config user.name "<your-github-username>"
git config user.email "<your-email>"
```

### Skill directory layout

Put skills under `skills/<category>/<skill-name>/` in the repo:

```
Strongbridge/Hermes/
├── skills/
│   └── <category>/
│       └── <skill-name>/
│           ├── SKILL.md          # skill definition (required)
│           ├── scripts/          # helper scripts (optional)
│           ├── references/       # depth files (optional)
│           ├── templates/        # starter files (optional)
│           └── tests/            # skill tests (optional)
├── README.md
└── .gitignore
```

### Copy a skill into the repo

Copy the **non-bundled** skill directories only — these are the ones the user created or owns. Bundled Hermes skills should not be pushed to an org repo (they ship with Hermes).

```bash
# From the local Hermes skills dir to the cloned repo
cp -r "$HERMES_HOME/skills/<category>/<skill-name>" "/c/Users/<user>/temp/<repo-slug>/skills/<category>/<skill-name>"
```

To decide which skills are bundled vs. user-owned, check for a `.bundled_manifest` file in the local `skills/` directory if one exists (Hermes writes it); skills listed in it are bundled. Skills not in the manifest are user-owned/created.

### Update the README

Keep the README's skill table in sync when adding or removing skills. Update the `| Category | Skills |` row for the affected category.

### .gitignore

Commit a `.gitignore` that excludes local env, Python/Node/OS artifacts, and IDE files. Skills themselves should not contain `.env` or secrets.

### Commit and push

```bash
cd /c/Users/<user>/temp/<repo-slug>
git add skills/<category>/<skill-name>/ README.md .gitignore
git commit -m "Add <skill-name> skill (<category>)"
git push origin main
```

If you amend a commit locally (e.g. to include a README update alongside the skill), you may need to force-push:

```bash
git push --force origin main
```

PITFALL (amend + force-push on a solo/few-collaborator repo): amending rewrites commit SHA; the remote rejects a normal push as non-fast-forward. For a repo with only one or a few trusted authors, force-push is acceptable. Coordinate with collaborators first if others have pulled the branch.

### After push

Skills in the repo become visible to users who have the repo as a skill hub (see `references/consuming-a-repo-as-skill-hub.md`).

## Distributing the repo to users

Users add the repo as an **external skill source** in their Hermes config — see `references/consuming-a-repo-as-skill-hub.md`. The README in the repo should document this so users can self-serve.

PITFALL (README accuracy): the `.env` `SKILLS HUB (GitHub integration for skill search/install/publish)` section with `GITHUB_TOKEN` is for the **centralized Hermes skills hub** (search/install/publish to the centralized index), NOT for pointing Hermes at an arbitrary org/user repo. Do not tell users to set a repo URL in that section — the supported path for an org repo is `skills.external_dirs` in `config.yaml`, or the clone-into-`skills/` fallback.

## One-skill-at-a-time updates

When a user creates or updates a single skill and wants it in the repo:

1. Clone (or use the existing clone) of the repo.
2. Copy only the changed skill's directory into `skills/<category>/<skill-name>/`.
3. Update the README table for that category if the skill list changed.
4. Commit + push.

Do not re-copy all skills every time — only the changed one(s).

## Pitfalls

- **Token in URL getting rejected after repeated attempts:** if `git` with an embedded-token URL starts returning "Invalid username or token" / "Authentication failed", the token may be rate-limited or the credential store may be holding a stale lock. Switch to the credential-helper path (`git config --global credential.helper store`, plain `git clone https://github.com/...`, then a single `git push` that prompts once) or generate a fresh token. Verify the token is still alive via the API first.

- **"fatal: unable to get credential storage lock"**: the credential store file or its parent directory doesn't exist or is inaccessible. Create the credential store file explicitly before cloning:
  ```bash
  mkdir -p "$(dirname "$CRED_FILE")"
  echo "https://github.com:443:<username>:<token>" > "$CRED_FILE"
  git config --global credential.helper store
  git config --global credential.helper "store --file=$CRED_FILE"
  ```

- **Empty-repo clone warning followed by "nothing to commit"**: the repo has no files yet. Add files (skills, README, .gitignore) and commit — the first commit creates `main`.

- **`git status` showing changes but `ls` showing an empty directory:** see the `/tmp` visibility quirk above — move the clone to a user-owned path and re-verify.

- **Amending and force-pushing overwrites remote history:** only do this when you're the sole author or have coordinated. Otherwise use a fresh commit on top.
- **GitHub API intermittency on file fetches:** the contents API, raw URL (`raw.githubusercontent.com`), and Git blobs/tree endpoints can intermittently return 404 for files that exist on GitHub (verified via commit/tree inspection or the web UI). When a skill file fails to download via the contents API or raw URL, try the zipball endpoint (`/zipball/<branch>`) instead — it uses a different CDN path and is more reliable. See `references/consuming-a-repo-as-skill-hub.md` for the full download-and-extract procedure, including the zip-entry path-prefix gotcha.

## Related skills

- `github-auth` — token selection, PAT scopes, troubleshooting 404/403.
- `github-repo-management` — clone, create, fork, remotes, releases.
- `github-issues`, `github-pr-workflow`, `github-code-review`, `github-github-issue-to-pr` — for the PR/issue workflow side.

## What this skill does NOT cover

- Writing or authoring the SKILL.md itself — that's the skill-authoring workflow.
- Consuming a repo as a skill hub on a user's machine — see `references/consuming-a-repo-as-skill-hub.md`.
- The centralized Hermes skills hub (search/install/publish to the index) — that's the `.env` `SKILLS HUB` mechanism, a different thing from an org repo.
