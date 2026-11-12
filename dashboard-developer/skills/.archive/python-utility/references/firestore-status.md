# Firestore Status Writer — Firebase Admin SDK Pattern

## Why Admin SDK, not OAuth2 token

`gcloud auth print-access-token` produces an OAuth2 access token that lacks the email claim. Firestore rules checking `request.auth.token.email` return 403. Use Firebase Admin SDK with a service account JSON key instead — Admin SDK authenticates as the service account, bypassing Auth token claims.

## Setup

1. Download service account JSON from Firebase Console → Project Settings → Service Accounts.
2. Set `GOOGLE_APPLICATION_CREDENTIALS` env var to the JSON file path.
3. Initialize: `firebase_admin.initialize_app(cred, {'databaseURL': ...})`.
4. Reference the non-default database: `firestore.Client(project=PROJECT, database=DB_NAME)`.

## Field mapping — PM task_health

The dashboard reads `pm.task_health[num].health` expecting **color values** (green/yellow/red/gray), not status values. The writer must map:
- `pass`, `on_track`, `complete` → `green`
- `yellow`, `at_risk`, `in_progress` → `yellow`
- `fail`, `delayed`, `blocked` → `red`
- `pending`, `queued`, `none` → `gray`

## Field names per role

| Role | Top-level field | Task sub-field |
|------|----------------|----------------|
| PM | `overall_health` | `task_health[num].health` |
| BA | `requirements_coverage` | `task_requirements[num].status` |
| SM | `sprint_status` | `task_progress[num].status` |

## Firestore rules — deploy to correct database

`firebase deploy --only firestore:rules` targets the default database. For `devopsstore`: `firebase deploy --only firestore:rules --project PROJECT` with `database: devopsstore` in firestore.rules. Verify with: `firebase firestore:rules:deploy --project PROJECT`.

## Pitfalls

- **Empty FIREBASE_TOKEN in .env** — `gcloud auth print-access-token` returns empty or invalid token; Admin SDK bypasses this entirely.
- **FIREBASE_API_KEY=*** in index.html — invalid JS syntax crashes the module script before `signInWithGoogle` is defined; use envsubst to substitute real values before deploying.
- **Rules on default DB, not devopsstore** — data written to default DB is invisible to rules on devopsstore; redeploy rules targeting the correct database.
- **git push requires PAT, not password** — GitHub rejects password auth for Git operations; use a Personal Access Token (classic, `repo` scope) as the credential, or SSH key. The `credential.helper=helper-selector` prompts interactively and blocks non-interactive pushes.
