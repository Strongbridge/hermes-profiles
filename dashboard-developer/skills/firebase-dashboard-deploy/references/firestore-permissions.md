# Firestore Permission Errors After Deploy

## Symptom
Console shows `FirebaseError: Missing or insufficient permissions` on all collections. Dashboard shows "Awaiting PM/BA/SM assessment" despite correct Firestore data.

## Root Cause
Google Auth provider is not enabled in Firebase Console → Authentication → Sign-in method → Google. Without it, `request.auth` is null even after client-side Google Sign-In, so Firestore rules that check `request.auth != null` deny all reads.

## Fix
1. **Enable Google Auth provider** in Firebase Console → Authentication → Sign-in method → Google (primary fix).
2. **Fallback**: make `isAuthorizedReader()` return `true` in firestore.rules (reads are team-visible; writes stay email-gated via `isAuthorizedWriter()`).

## Verification
Read docs back with the Firestore client:
```python
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '<path-to-sa-key>'
from google.cloud import firestore
db = firestore.Client(project='fradevops-a51a2', database='devopsstore')
doc = db.collection('status').document('pm').get()
print(doc.to_dict())
```

## Note
deploy_populate.py only uploads static Hosting files; it does NOT write to Firestore or modify rules. Seed data with `seed_firestore.py` and deploy rules separately.