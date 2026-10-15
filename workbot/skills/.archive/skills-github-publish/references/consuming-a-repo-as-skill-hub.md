---
title: Consuming a GitHub org repo as a Hermes skill hub
---

# Consuming a GitHub org repo as a Hermes skill hub

A user (or org teammate) wants to add a GitHub repository like `Strongbridge/Hermes` as a skill source in their Hermes instance, so skills from that repo become available in their Hermes.

This is the **consumption** side. For the **publishing/distribution** side, see `skills-github-publish`.

## Two supported paths

### Path A — `skills.external_dirs` (supported mechanism for external org/user repos)

Hermes supports externally-owned skill directories through the `skills.external_dirs` config key in `config.yaml`. This is the intended path for adding an org or user repo as a skill source.

**What to do on the user's machine:**

1. **Each user needs their own GitHub classic PAT with `repo` scope** (at least read access to the org repo). Put it in their `~/.hermes/.env` as `GITHUB_TOKEN`. Do NOT share tokens across users.

2. **Clone the repo to a local path** (or have it available locally):
   ```bash
   git clone https://github.com/Strongbridge/Hermes.git /path/to/local/hermes-skills-repo
   ```

3. **Add the path to `skills.external_dirs`** in the user's `~/.hermes/config.yaml`:
   ```yaml
   skills:
     external_dirs:
       - /path/to/local/hermes-skills-repo/skills
   ```
   The exact config shape (list of paths vs. list of repo URLs, whether a `repo_url` variant exists) should be confirmed against the Hermes version on the user's machine — check `hermes_cli/AGENTS.md` or the runtime code for the current `skills.external_dirs` contract. If `skills.external_dirs` takes repo URLs instead of local paths, point it at `https://github.com/Strongbridge/Hermes`.

4. **Restart Hermes** (or reload skills) so the new skill source is picked up.

Skills from the repo then appear alongside the user's other skills and can be invoked per their `SKILL.md`.

PITFALL: if `skills.external_dirs` points at a local clone, the user must keep it updated (`git pull`) to get new/updated skills from the repo. If it points at a repo URL, Hermes pulls on its own schedule (confirm the update cadence for the Hermes version in use).

### Path B — clone-into-skills fallback (guaranteed to work)

If `skills.external_dirs` is not configured or not working on the user's machine, the guaranteed fallback is to clone the repo directly into the user's local `skills/` directory:

```bash
# WARNING: this overwrites the local skills/ directory.
# Back up any user-owned skills first if they exist.
# Or, to add only ONE skill without wiping existing skills:
#   clone to a temp dir, then copy only the desired skill subdir into the local skills/ folder.

rm -rf ~/.hermes/skills          # only if the user is OK replacing all local skills
git clone https://github.com/Strongbridge/Hermes.git ~/.hermes/skills
```

To add only one skill without wiping existing skills:

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/Strongbridge/Hermes.git "$tmp"
cp -r "$tmp/skills/<category>/<skill-name>" ~/.hermes/skills/
rm -rf "$tmp"
```

### Token requirement for both paths

- Each user needs a GitHub classic PAT with `repo` scope (at least read for consumption; write if they also want to contribute skills back).
- Put it in `~/.hermes/.env` (or the profile's `.env` for profile-scoped use) as `GITHUB_TOKEN`.
- Do NOT share tokens across users — each user generates their own.

## What the repo's README should document

The repo's `README.md` should tell users:

- What skills are in the repo (a table by category).
- The two consumption paths above (Path A: `skills.external_dirs`; Path B: clone-into-skills fallback).
- That each user needs their own `GITHUB_TOKEN` (classic PAT, `repo` scope).
- How to contribute a skill back (clone, add skill dir, commit, push).

See the `Strongbridge/Hermes` repo README for an example.

## What NOT to tell users

- Do NOT tell users to put a repo URL in the `.env` `SKILLS HUB (GitHub integration for skill search/install/publish)` section. That section is for the **centralized Hermes skills hub** (search/install/publish to the centralized index), a different mechanism from consuming an arbitrary org repo.
- Do NOT tell users to share one `GITHUB_TOKEN` across the team.

## Quick reference

| Goal | Path |
|------|------|
| Add org repo as skill source, keep it maintained | `skills.external_dirs` (Path A) |
| One-off skill, or `external_dirs` not working | Clone into `~/.hermes/skills/` (Path B) |
| Add just one skill without wiping existing skills | Clone to temp dir, copy one subdir (Path B variant) |
| Team distribution | Each user needs their own PAT + the repo URL |
| Contribute a skill back | Clone, add skill dir, commit, push (see `skills-github-publish`) |
