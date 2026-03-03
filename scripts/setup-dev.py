#!/usr/bin/env python3
"""
Generate dev-overrides.txt for local editable mode (only on your dev machine with sibling repos).

Usage:
    python scripts/setup-dev.py
    uv sync --override dev-overrides.txt

This overrides the git version with editable local paths.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()

PACKAGES = {
    "b3-geo": "../b3_geo",
    "b3_msh": "../b3_msh",
    "b3_drp": "../b3_drp",
    "b3-2d": "../b3_2d",
    "b3_bem": "../b3_bem",
    "b3_mat": "../b3_mat",
    "cgfoil": "../cgfoil",
}

OVERRIDES_FILE = ROOT / "dev-overrides.txt"

lines = []
for pkg, rel_path in PACKAGES.items():
    abs_path = (ROOT / rel_path).resolve()
    if abs_path.exists():
        lines.append(f"{pkg} @ file://{abs_path}")
        print(f"✓ {pkg} → local editable")
    else:
        print(f"⚠️  {pkg} not found at {abs_path} (skipping)")

OVERRIDES_FILE.write_text("\n".join(lines) + "\n")
print(f"\n✅ Generated {OVERRIDES_FILE}")
print("\nLocal dev command:")
print("   uv sync --override dev-overrides.txt")
