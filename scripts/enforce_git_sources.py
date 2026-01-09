#!/usr/bin/env python3
"""
Pre-commit hook: Enforce only Git sources are active in [tool.uv.sources].
- Blocks commit if any uncommented 'path =' or 'editable = true' exists for active deps.
- Optionally auto-fixes by commenting out local lines (--fix).
- Ignores commented local lines (they are allowed as dev helpers).
"""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PYPROJECT_PATH = ROOT / "pyproject.toml"


def get_active_deps(content: str) -> set:
    """Extract package names from [project.dependencies] and optional-dependencies."""
    active = set()
    lines = content.splitlines()
    in_deps = False
    in_optional = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[project.dependencies]"):
            in_deps = True
            continue
        if stripped.startswith("[project.optional-dependencies]"):
            in_deps = False
            in_optional = True
            continue
        if stripped.startswith("["):
            in_deps = in_optional = False
        if (in_deps or in_optional) and stripped and not stripped.startswith("#"):
            # Extract package name (before any ==, >=, [, {, etc.)
            match = re.match(r"^([a-zA-Z0-9_-]+)", stripped)
            if match:
                active.add(match.group(1))
    return active


def has_uncommented_local_source(content: str, active_deps: set) -> list:
    """Return list of lines (index, package) with uncommented local path/editable."""
    bad_lines = []
    lines = content.splitlines()
    in_sources = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[tool.uv.sources]"):
            in_sources = True
            continue
        if in_sources and stripped and not stripped.startswith("#"):
            for pkg in active_deps:
                # Look for path = or editable = true
                if re.search(
                    rf"^{re.escape(pkg)}\s*=\s*{{.*?\bpath\s*=", stripped, re.IGNORECASE
                ):
                    bad_lines.append((i, pkg, "path"))
                elif re.search(
                    rf"^{re.escape(pkg)}\s*=\s*{{.*?\beditable\s*=\s*true",
                    stripped,
                    re.IGNORECASE,
                ):
                    bad_lines.append((i, pkg, "editable"))
    return bad_lines


def auto_comment_local(lines: list[str], bad_lines: list) -> list[str]:
    """Comment out the bad local source lines."""
    for i, pkg, kind in sorted(bad_lines, reverse=True):
        lines[i] = (
            f"# {lines[i].rstrip()}  # AUTO-COMMENTED by pre-commit: use Git sources for commits\n"
        )
    return lines


def main():
    if not PYPROJECT_PATH.exists():
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    content = PYPROJECT_PATH.read_text()
    active_deps = get_active_deps(content)

    if not active_deps:
        print("No active dependencies found – skipping check.")
        sys.exit(0)

    bad = has_uncommented_local_source(content, active_deps)

    if not bad:
        print(
            "✓ All active dependencies use Git sources (or no local paths active) – commit allowed."
        )
        sys.exit(0)

    print(
        "✗ ERROR: Uncommented local path or editable=true found for active dependencies!"
    )
    print(
        "  These must be commented out before committing (production/CI must use Git sources)."
    )
    print("  Bad entries:")
    for i, pkg, kind in bad:
        print(f"    - Line {i + 1}: {pkg} ({kind})")

    # Optional: auto-fix if --fix is passed
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        print("\nAuto-fixing: commenting out local sources...")
        lines = content.splitlines()
        fixed_lines = auto_comment_local(lines, bad)
        PYPROJECT_PATH.write_text("\n".join(fixed_lines) + "\n")
        print("Fixed! Please stage the changes and commit again.")
        sys.exit(0)
    else:
        print("\nFix options:")
        print("  1. Manually comment out the local lines in [tool.uv.sources]")
        print("  2. Run with --fix to auto-comment them:")
        print("     python scripts/enforce_git_sources.py --fix")
        print("  3. Use your toggle script if you have one.")
        sys.exit(1)


if __name__ == "__main__":
    main()
