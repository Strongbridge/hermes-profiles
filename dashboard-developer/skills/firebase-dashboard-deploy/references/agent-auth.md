# Agent Script Authentication

## Problem
gcloud OAuth2 access tokens (from `gcloud auth print-access-token`) do not carry an email claim. Firestore rules check `request.auth.token.email`, so the token is present but `email` is null → permission denied.

## Symptom
`write_status.py` fails with 403 or the Firestore console shows no recent writes from `agent-*` users despite the script reporting success.

## Fix
Use the Firebase Admin SDK instead of the REST API with OAuth2 tokens. The Admin SDK uses the service account credentials from `GOOGLE_APPLICATION_CREDENTIALS` and bypasses security rules entirely.

```python
import os, json
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

from google.cloud import firestore
db = firestore.Client(
    project=os.environ['FIREBASE_PROJECT_ID'],
    database='devopsstore'
)
db.collection('status').document('pm').set(data, merge=True)
```

## Verification
Read the document back and check `updated_by` reflects the agent name and `last_updated` is current:
```python
doc = db.collection('status').document('pm').get()
print(doc.to_dict().get('updated_by'), doc.to_dict().get('last_updated'))
```

## Key Point
The `GOOGLE_APPLICATION_CREDENTIALS` env var must point to the service account JSON file. Without it, the Admin SDK falls back to default credentials which may not exist in non-interactive environments.

## Deploy Script Auto-Auth (deploy.py)
The deploy script (`deploy.py`) generates its own OAuth2 access token from the service account key on each run — no `ACCESS_TOKEN` env var needed. It uses JWT bearer grant flow against `https://oauth2.googleapis.com/token` with scope `https://www.googleapis.com/auth/firebase.hosting`. This eliminates manual token pasting and token expiry issues.

```python
# deploy.py reads service account from GOOGLE_APPLICATION_CREDENTIALS env var
# or falls back to C:/Users/DanRighter/AppData/Local/hermes/secrets/project-mgt-report-sa.json
# Generates fresh JWT → exchanges for access token → uses Bearer token for REST API
```

**Pitfall:** If the service account JSON is missing or the private_key is empty, token generation fails with a JSON parse or KeyError. Verify the credentials file exists and contains a valid `private_key` field before debugging deploy failures.

**Verification:** Run `python3 deploy.py` — should print `Token: generated (1024 chars)` on stderr before any API calls. If it prints `ERROR: Failed to generate access token`, check the service account file path and key validity.

**Pitfall:** Even with a valid token, the `/versions` endpoint returns 403 PERMISSION_DENIED if the service account lacks `roles/firebasehosting.admin`. Service Usage Consumer alone is not sufficient for REST API deploys. Fix: grant `roles/firebasehosting.admin` to the service account in GCP IAM.