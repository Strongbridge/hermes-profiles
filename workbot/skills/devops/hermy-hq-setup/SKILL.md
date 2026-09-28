---
name: hermy-hq-setup
description: Set up Hermy HQ dashboard + hermes-bridge locally on Windows
---

## When to Use
Use when setting up the Hermy HQ dashboard (github.com/sharbelxyz/hermes-agent-mission-control) paired with a local Hermes agent via the hermes-bridge, on Windows. Covers: clone, npm install, .env writing with real secrets (never fabricate), prisma db push, dev server, auth.ts wildcard patch if needed, Windows bridge service (scheduled task or WinSW), EnterpriseDB PostgreSQL silent install, and Google OAuth walkthrough.

## Prerequisites
- Node 24+, npm 11+ (verified working)
- git (for clone)
- A Postgres database URL (hosted OR local via EnterpriseDB Windows installer). The bridge rejects `prisma://` Accelerate URLs but accepts `postgresql://` including localhost.
- Google Cloud OAuth Web client (Client ID + Secret) for NextAuth Google login. Redirect URIs: `http://localhost:3000/api/auth/callback/google` (dev) and `https://<your-vercel-app>/api/auth/callback/google` (prod).
- Optional: Vercel account for deploying the dashboard (not needed for local-only use).

## Clone + install
```
cd /c/Users/DanRighter
git clone https://github.com/sharbelxyz/hermes-agent-mission-control hermy-hq
cd hermy-hq
npm install              # 581 packages, Prisma Client v6.19.2 generated
cd hermes-bridge
npm install              # pg only, 14 packages, 0 vulns
```

## .env writing — NEVER fabricate secrets
Copy `.env.example` to `.env`, then fill ONLY with real values you provide. Generate locally-creatable secrets and show before writing:

```
NEXTAUTH_SECRET=$(openssl rand -base64 32)
INTERNAL_API_SECRET=$(openssl rand -hex 32)
CRON_SECRET=$(openssl rand -hex 32)
```

Required real values (never guess):
- `DATABASE_URL=postgresql://user:***@host:5432/db?sslmode=require`
- `POSTGRES_URL=` (same as DATABASE_URL)
- `NEXTAUTH_URL=http://localhost:3000` (local dev)
- `GOOGLE_CLIENT_ID=`
- `GOOGLE_CLIENT_SECRET=`
- `ALLOWED_EMAILS=` (comma-separated Google emails)
- `NEXT_PUBLIC_OWNER_NAME=`
- `NEXT_PUBLIC_BASE_URL=http://localhost:3000`
- Optional: HERMES_WIKI, HERMES_BIN, BRIEF_HOUR (defaults fine)

Optional (leave blank to disable):
- OpenAI/OpenRouter/xAI/Brave/YouTube/Twitter/Notion keys — core dashboard runs without them.

## Database push
```
cd /c/Users/DanRighter/hermy-hq
npx prisma db push
```

## Dev server
```
cd /c/Users/DanRighter/hermy-hq
npm run dev
```
Verify at `http://localhost:3000`. Google login gated to ALLOWED_EMAILS.

## Bridge Windows service — continuous mode

User chose continuous Windows service over on-demand. Two options:

### Option A: `sc.exe` Windows service (native, no extra install)

```powershell
sc.exe create "HermyHQBridge" binPath= "C:\Program Files\nodejs\node.exe \"C:\Users\DanRighter\hermy-hq\hermes-bridge\bridge.mjs\"" start= auto displayName= "Hermy HQ Bridge" description= "Local Hermes ↔ Hermy HQ dashboard bridge (poll + mirror)"
sc.exe failure "HermyHQBridge" reset= 86400 actions= restart/60000/restart/60000/restart/60000
sc.exe start "HermyHQBridge"
```

Notes: spaces after `=` are required by `sc.exe`. Use absolute paths. The bridge needs `DATABASE_URL`, `HERMES_BIN` (absolute path to hermes.exe), and other `HERMES_*` env vars — set these in the system environment or in a wrapper batch file that the `binPath` calls.

### Option B: Windows Scheduled Task (more flexible for env vars)

Create a wrapper batch (`start-bridge.bat`) that sets env vars then launches node, then schedule it:

```batch
@echo off
set DATABASE_URL=postgresql://postgres:***@localhost:5432/hermyhq?sslmode=disable
set HERMES_BIN=C:\Users\DanRighter\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe
set HERMES_BOARD=default
set HERMES_WIKI=C:\Users\DanRighter\OneDrive - Strongbridge\Documents\Obsidian
cd /d C:\Users\DanRighter\hermy-hq\hermes-bridge
"C:\Program Files\nodejs\node.exe" bridge.mjs
```

Then create the task:
```powershell
schtasks /create /tn "HermyHQBridge" /tr "C:\Users\DanRighter\hermy-hq\hermes-bridge\start-bridge.bat" /sc onstart /ru SYSTEM /rl HIGHEST /f
```

### Restarting the gateway after a code patch

See the `hermes-ollama-alias-resolution` skill for the gateway restart procedure — when patching `gateway/run.py` (e.g. the model alias resolution fix), the running gateway process must be killed and restarted for the patch to take effect. `taskkill /F` may report success without actually killing the process; verify by checking `gateway_state.json` for a new PID.

## Local PostgreSQL via EnterpriseDB
Download from https://sbp.enterprisedb.com/getfile.jsp?fileid=1260436 (Windows x86-64 installer). During install: set superuser password, choose port 5432, create a database (e.g. `hermyhq`). Connection string: `postgresql://postgres:***@localhost:5432/hermyhq?sslmode=disable`. No TLS needed for localhost.

## Google OAuth creation walkthrough
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID, type: Web application
3. Add authorized redirect URIs: `http://localhost:3000/api/auth/callback/google` (dev) and production URL
4. Copy Client ID + Client Secret into `.env`
5. Add your Google email to `ALLOWED_EMAILS`

## Auth wildcard for domain-suffix allowlists

When `ALLOWED_EMAILS` uses a domain wildcard like `*@sb-llc.com`, the default NextAuth `includes()` check won't match because it looks for the literal string `*@sb-llc.com` in the email, not a domain suffix match. The fix is in `src/lib/auth.ts` — patch the `signIn` callback to support `*@domain` patterns:

```typescript
// In the signIn callback, after loading allowed emails:
const allowedPatterns = allowedEmails
  .split(',')
  .map(e => e.trim().toLowerCase())
  .filter(Boolean);

const email = profile?.email?.toLowerCase() ?? '';
const match = allowedPatterns.some(pattern => {
  if (pattern.startsWith('*@')) {
    // Domain suffix wildcard: *@domain.com matches anyone @domain.com
    return email.endsWith(pattern.slice(1));
  }
  return email === pattern;
});
if (!match) return false;
```

The full `auth.ts` (NextAuth config with GoogleProvider, JWT strategy, `session: { strategy: 'jwt' }`) lives in `C:\Users\DanRighter\hermy-hq\src\lib\auth.ts`.

After patching, `npx prisma db push` and restart the dev server. Verify the login page at `http://localhost:3000/login` shows the Google sign-in button (the login page is a client component — it only renders "Sign in with Google", no owner name there by design; the owner name renders on the dashboard home page `src/app/page.tsx` via `process.env.NEXT_PUBLIC_OWNER_NAME || "Founder"`).

## Dev server troubleshooting

**Turbopack cache corruption:** If `rm -rf .next` is run while the dev server is running, the Turbopack state DB gets corrupted and the next start fails with errors like `ENOENT: no such file or directory, open '...build-manifest.json'` and `Failed to restore task data (corrupted database or bug)`. Fix: `rm -rf .next` (complete removal) then restart.

**Port conflicts:** The dev server may fail to start if port 3000 is held by a stale process. Check with `netstat -ano | grep ":3000"` or `fuser 3000/tcp`. Kill the holder and restart. The dev server will use the next available port if 3000 is taken (e.g. 3001).

**`npm run dev` exit codes that look like failures but aren't:** `exit 127` from a background `npm run dev` with a `PATH` override often means `npm` wasn't on the modified PATH. Run `npm run dev` directly in the project directory without a `PATH` override. `exit -1` with empty output usually means the background process was killed by the shell; check if it's still running via `ps aux | grep node`.

## Cron job pinning

Cron job `490b2baf1fc4` (RSIS Helpdesk Follow-up Reminder, daily) stores a model/provider snapshot from when it was created. If that snapshot references a model/provider that no longer works (e.g. a cloud model that's been switched off, or a local Ollama model that's been removed), the cron job will fail on its next run. Pin it to the current working config:

```bash
hermes cron edit 490b2baf1fc4 --model local-ollama --provider custom
```

Or pin to a cloud model if preferred:
```bash
hermes cron edit 490b2baf1fc4 --model upstage/solar-pro4:free --provider nous
```

Check current cron state with `hermes cron list` and `hermes cron show <job_id>`.
