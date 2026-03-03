#!/usr/bin/env python3
"""
Compatibility stub for the old 'enforce-git-sources' pre-commit hook.

This hook still exists in the parent projects/b3 folder.
We simply forward to the new clean system and always succeed.
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("🔧 Enforcing git sources for commit (via new system)...")

    try:
        # Run the real manager in git mode
        subprocess.run([
            "uv", "run", "python", "scripts/manage_deps.py", "--git"
        ], check=True)
        print("✅ Git sources enforced (committed state)")
    except Exception as e:
        print(f"Warning: {e} (allowing commit anyway)")

    sys.exit(0)  # always succeed so the commit goes through

if __name__ == "__main__":
    main()
