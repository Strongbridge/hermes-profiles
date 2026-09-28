#!/usr/bin/env python3
"""
Hermes Agent Profile Backup Script
Runs periodically to sync live profiles to the GitHub backup repo.
"""
import os
import shutil
import subprocess
import sys
import datetime
from pathlib import Path

# Configuration
HERMES_HOME = Path(r"C:\Users\DanRighter\AppData\Local\hermes")
PROFILES_DIR = HERMES_HOME / "profiles"
BACKUP_ROOT = Path(r"C:\Users\DanRighter\hermes-profiles-backup")
SSH_KEY = Path(r"C:\Users\DanRighter\.ssh\id_ed25519_hermes")
LOG_FILE = BACKUP_ROOT / "backup.log"
GITIGNORE = Path(r"C:/Users/DanRighter/AppData/Local/hermes/profiles/.gitignore")

# Profiles to back up
PROFILES = ["pm", "sm", "ba", "customer-relations", "resource-manager", "workbot"]

# Paths that should NEVER be backed up (secrets, runtime state)
EXCLUDE_DIRS = {
    ".env", ".env.*", "state.db", "state.db-*",
    "state", "gateway_state.json", "gateway.pid", "gateway.lock",
    "logs", "sessions", "cache", "attachments", "assets",
    "models_dev_cache.json", "projects.db", "provider_models_cache.json",
    "events.db", ".hermes", "backups",
}

EXCLUDE_FILES = {
    ".env", ".env.*", "*.env",
    "state.db", "state.db-*",
    "gateway_state.json", "gateway.pid", "gateway.lock",
    "gateway-stdio.log", "gateway-starts.log",
    "models_dev_cache.json", "projects.db", "provider_models_cache.json",
    "events.db",
}

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def should_exclude(name):
    """Check if a file/dir name matches exclusion patterns."""
    for pattern in EXCLUDE_DIRS:
        if name == pattern or (pattern.endswith("*") and name.startswith(pattern[:-1])):
            return True
    for pattern in EXCLUDE_FILES:
        if name == pattern or (pattern.endswith("*") and name.startswith(pattern[:-1])):
            return True
    return False

def copy_profile(src_profile_dir: Path, dst_profile_dir: Path):
    """Copy a profile's relevant files to the backup directory."""
    if not src_profile_dir.exists():
        log(f"SKIP {src_profile_dir.name}: source not found")
        return 0
    
    dst_profile_dir.mkdir(parents=True, exist_ok=True)
    total_bytes = 0
    copied = []
    
    # Direct files to copy
    direct_files = ["config.yaml", "SOUL.md"]
    for fname in direct_files:
        src = src_profile_dir / fname
        dst = dst_profile_dir / fname
        if src.exists() and not should_exclude(fname):
            shutil.copy2(str(src), str(dst))
            copied.append(fname)
            total_bytes += src.stat().st_size
    
    # Subdirectories to copy
    subdirs = ["skills", "cron", "platforms", "plans", "attachments", "assets"]
    for subdir in subdirs:
        src_subdir = src_profile_dir / subdir
        dst_subdir = dst_profile_dir / subdir
        if src_subdir.exists() and src_subdir.is_dir():
            # Remove existing destination
            if dst_subdir.exists():
                shutil.rmtree(str(dst_subdir))
            shutil.copytree(str(src_subdir), str(dst_subdir))
            # Count what we copied
            for root, dirs, files in os.walk(str(dst_subdir)):
                for f in files:
                    fp = Path(root) / f
                    if not should_exclude(f):
                        total_bytes += fp.stat().st_size
            copied.append(f"{subdir}/")
    
    # Remove excluded files/dirs from destination
    for item in dst_profile_dir.iterdir():
        if should_exclude(item.name):
            if item.is_dir():
                shutil.rmtree(str(item))
            else:
                item.unlink()
    
    log(f"BACKED UP {src_profile_dir.name}: {copied} ({total_bytes/1024:.1f} KB)")
    return total_bytes

def git_push():
    """Push changes to the remote repo."""
    env = os.environ.copy()
    # SSH command for Windows paths (use forward slashes, no spaces)
    ssh_key_str = str(SSH_KEY).replace("\\", "/")
    env["GIT_SSH_COMMAND"] = f'ssh -i "{ssh_key_str}" -o ConnectTimeout=15 -o StrictHostKeyChecking=no -o BatchMode=yes'
    
    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=str(BACKUP_ROOT),
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode != 0:
            log(f"git add failed: {result.stderr}")
            return False
        
        # Check if there's anything to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(BACKUP_ROOT),
            capture_output=True, text=True, timeout=10, env=env
        )
        if result.returncode == 0:
            log("No changes to commit — skipping push")
            return True  # Nothing changed is still success
        
        commit_msg = f"Automated backup: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(BACKUP_ROOT),
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode != 0:
            log(f"git commit failed: {result.stderr}")
            return False
        
        log(f"Committed: {commit_msg}")
        
        result = subprocess.run(
            ["git", "push", "origin", "HEAD"],
            cwd=str(BACKUP_ROOT),
            capture_output=True, text=True, timeout=300, env=env
        )
        if result.returncode != 0:
            log(f"git push FAILED: {result.stderr}")
            return False
        
        log(f"PUSHED to origin/master")
        return True
    except subprocess.TimeoutExpired:
        log("git push timed out after 5 minutes")
        return False
    except Exception as e:
        log(f"git push error: {type(e).__name__}: {e}")
        return False

def main():
    log("=" * 60)
    log("Hermes Profile Backup Starting")
    
    total_size = 0
    profiles_count = 0
    
    for profile_name in PROFILES:
        src = PROFILES_DIR / profile_name
        dst = BACKUP_ROOT / profile_name
        size = copy_profile(src, dst)
        total_size += size
        if size > 0 or (src.exists() and any(src.iterdir())):
            profiles_count += 1
    
    log(f"Total: {profiles_count} profiles, {total_size/1024:.1f} KB copied")
    
    # Push to GitHub
    success = git_push()
    
    if success:
        log("Backup completed successfully")
        sys.exit(0)
    else:
        log("Backup completed with push issues — check log")
        sys.exit(1)

if __name__ == "__main__":
    main()
