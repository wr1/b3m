#!/usr/bin/env python3
"""
b3m override helper (after the workspace fix).

Recommended commands:
  • Any machine / CI / default:   python scripts/setup-git.py && uv sync --override git-overrides.txt
  • Local editable dev:           python scripts/setup-dev.py && uv sync --override dev-overrides.txt
"""

print(
    "See setup-git.py (default) or setup-dev.py (local) + the matching --override flag."
)
print("This completely avoids the parent workspace member conflict.")
