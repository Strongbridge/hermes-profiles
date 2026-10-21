---
name: firebase-deploy
trigger: "Use when deploying to Firebase Hosting or managing the deploy pipeline."
description: Deploy to Firebase Hosting via REST API.
version: 1.0.0
author: dashboard-developer
license: internal
metadata:
  hermes:
    tags: [deploy, firebase, hosting, devops]
    related_skills: [credential-redaction]
---

## Standing rules (apply to every deploy)

- **Never preserve API keys, tokens, or credentials in memory.** Use `[REDACTED]` in notes.
- **Service account JWT auth may return 401** — `deploy.py` generates a JWT from the service account, but the token is rejected if the account lacks `roles/firebasehosting.admin` in GCP IAM. Verify the role before debugging auth.
- **Firestore lives in `devopsstore`**, not the default database.
- **Deploy pipeline**: envsubst on `v2_fixed/index.html` → `index.html` → Firebase Hosting REST API (broken for uploads — see pitfalls).
- **Root `index.html` must use envsubst placeholders** (`${FIREBASE_API_KEY}`, etc.), NOT hardcoded keys or broken placeholders.
- **Redact credentials before committing** — `.env` files with real keys must never enter git.

## Deploy procedure

1. **Verify the source** — confirm `index.html` has real Firebase config values, no `***` or broken placeholders.
2. **Run deploy** — `python3 deploy.py` from the dashboard working directory.
3. **If 403 Access Denied** — the service account needs `roles/firebasehosting.admin` in GCP IAM. Add the role, then retry. If 401 Unauthorized on JWT auth, the same IAM fix applies.
4. **If firebase CLI auth is expired** — run `firebase login --reauth` interactively, then `firebase deploy --only hosting`.
5. **If release finalization fails with INVALID_ARGUMENT** — the version was uploaded but not finalized correctly; check that all required files were uploaded before finalizing.
4. **If release finalization fails with INVALID_ARGUMENT** — the version was uploaded but not finalized correctly; check that all required files were uploaded before finalizing.

## GitHub push procedure

1. **Require a GitHub PAT** (classic, `repo` scope) — password auth is not supported.
2. **Add PAT to `.env` as `GITHUB_TOKEN`** before pushing.
3. **Set git credential helper** — `git config credential.helper ''` to avoid interactive prompts, then push.

## Pitfalls

- **`signInWithGoogle is not defined`** — caused by invalid JS syntax (e.g., `apiKey: ***`) crashing the module script before auth functions load. Fix the syntax, reload.
- **`auth/api-key-not-valid`** — caused by `***` placeholder in FirebaseConfig. Replace with the real key from the user's config.
- **`write_file` refuses to overwrite** — the file exists and the task hasn't read its full content. Use `patch` for targeted edits, or `read_file` first then `write_file`.
- **Git push hangs on credential prompt** — `credential-helper-selector` blocks waiting for interactive input. Disable with `git config credential.helper ''` and provide `GITHUB_TOKEN` in `.env`.
- **`git add -A` picks up parent directories** — always use a `.gitignore` to exclude `node_modules/`, `.env`, and browser/cache directories before staging.
- **REST API file upload returns 403 Access Denied** — the `populateFiles` flow returns a signed upload URL, but uploading content to it is rejected with HTTP 403. The version ends up with 0 files and finalize fails with INVALID_ARGUMENT. Workaround: use `firebase deploy` CLI after `firebase login --reauth`. Do not retry the populateFiles/upload/finalize cycle via raw REST — it will not work.
- **Service account JWT returns 401 Unauthorized** — the service account key generates a JWT successfully, but the token is rejected at the Hosting API if the account lacks `roles/firebasehosting.admin` in GCP IAM. Fix: grant the role in IAM → add member → `gemini-enterprise-agent@project-mgt-report.iam.gserviceaccount.com` → Firebase Hosting Admin.
- **gcloud auth expired** — `gcloud auth print-access-token` fails with "Reauthentication failed" when the credential is stale. Fix: run `firebase login --reauth` interactively once, then `firebase deploy --only hosting` works for subsequent deploys.
- **Version files endpoint returns 404** — `/{version_name}/files/{path}` returns 404 for all uploads regardless of URL encoding. The correct upload path is the `uploadUrl` from `populateFiles` response, but that endpoint also returns 400/403 for content uploads. Do not waste time debugging URL encoding — the API flow itself is broken for this project.
- **Release creation fails with INVALID_ARGUMENT** — caused by deploying a version with 0 files (upload never succeeded). Fix the upload step first, then finalize, then release.
