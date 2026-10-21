# envsubst/JS Template Literal Collision

envsubst replaces ALL `${VAR}` patterns in template files — including JavaScript template literal expressions that use the same syntax. This is the #1 cause of deploy-time SyntaxErrors.

## Collision Patterns

| Template syntax | envsubst interprets as | Result |
|---|---|---|
| `` `${path}` `` | `${path}` env var | Windows PATH injected → SyntaxError |
| `` `${FIREBASE_*}` `` | invalid glob | Left as-is → `firebase_auth_domain` in iframe URL |
| `` `${FIREBASE_API_KEY}` `` | env var | Correct substitution ✅ |

## Fixes

1. **JS variables**: use string concatenation instead of template literals:
   ```js
   // Bad — envsubst replaces ${path}
   console.error(`Listener error on ${path}:`, err)
   // Good — envsubst leaves it alone
   console.error('Listener error on ' + path + ':', err)
   ```
2. **Comments**: avoid `${...}` in comments entirely:
   ```
   // Bad — envsubst tries to parse
   // substitutes ${FIREBASE_*}
   // Good — plain text
   // substitutes all FIREBASE_* placeholders
   ```
3. **Deploy script**: include envsubst as Step 0 in the deploy pipeline, not as a manual pre-step.

## Detection

After deploy, fetch the live HTML and grep for remaining `${...}` patterns:
```python
import re, urllib.request
with urllib.request.urlopen('https://<project>.web.app/') as r:
    content = r.read().decode()
placeholders = re.findall(r'\$\{([^}]+)\}', content)
```
Any `${FIREBASE_*}` or `${FIRESTORE_*}` in the output means envsubst didn't run or missed a variable.