#!/usr/bin/env python3
"""Diagnostic: test each git command the backup script uses."""
import subprocess, os, time
from pathlib import Path

BACKUP_ROOT = Path(r"C:\Users\DanRighter\hermes-profiles-backup")
SSH_KEY = Path(r"C:\Users\DanRighter\.ssh\id_ed25519_hermes")

# Remove stale lock
for lock in ["index.lock", "HEAD.lock"]:
    p = BACKUP_ROOT / ".git" / lock
    if p.exists():
        p.unlink()
        print(f"Removed stale lock: {lock}")

env = os.environ.copy()
ssh_key_str = str(SSH_KEY).replace('\\', '/')
env["GIT_SSH_COMMAND"] = f'ssh -i "{ssh_key_str}" -o ConnectTimeout=15 -o StrictHostKeyChecking=no -o BatchMode=yes'

print(f"PATH: {env.get('PATH', 'NOT SET')[:120]}")
print(f"HOME: {env.get('HOME', 'NOT SET')}")

steps = [
    ("git add -A", ["git", "add", "-A"], 30),
    ("git diff --cached --quiet", ["git", "diff", "--cached", "--quiet"], 10),
    ("git commit", ["git", "commit", "-m", "Test backup diagnostic"], 30),
    ("git push origin HEAD", ["git", "push", "origin", "HEAD"], 300),
]

for label, cmd, timeout in steps:
    t0 = time.time()
    try:
        result = subprocess.run(cmd, cwd=str(BACKUP_ROOT), capture_output=True, text=True, timeout=timeout, env=env)
        elapsed = time.time() - t0
        print(f"\n{'='*50}")
        print(f"CMD: {label}")
        print(f"Exit: {result.returncode}, Duration: {elapsed:.1f}s")
        if result.stdout:
            print(f"STDOUT: {result.stdout[:300]}")
        if result.stderr:
            print(f"STDERR: {result.stderr[:300]}")
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - t0
        print(f"\n{'='*50}")
        print(f"CMD: {label}")
        print(f"TIMED OUT after {elapsed:.1f}s (timeout was {timeout}s)")
        if e.stderr:
            stderr_text = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr)
            print(f"STDERR: {stderr_text[:300]}")
        break
