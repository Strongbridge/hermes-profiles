#!/usr/bin/env python3
"""Clean stale git lock files from the backup repo."""
from pathlib import Path

backup_root = Path(r"C:/Users/DanRighter/hermes-profiles-backup/.git")
lock_files = ["index.lock", "HEAD.lock", "refs/heads/master.lock"]

for lock_file in lock_files:
    lock_path = backup_root / lock_file
    if lock_path.exists():
        lock_path.unlink()
        print(f"Removed: {lock_path}")
    else:
        # Check in refs/heads/ subdirectory
        if "refs" in str(lock_file):
            parent = backup_root / "refs" / "heads"
        else:
            parent = backup_root
        alt_path = parent / Path(lock_file).name
        if alt_path.exists():
            alt_path.unlink()
            print(f"Removed: {alt_path}")

print("Lock file cleanup complete")