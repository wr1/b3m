#!/usr/bin/env python3
"""
Unified b3m dependency manager for git <-> local mode.

Merges former manage_deps.py + local_git.py stub.
- Uses currently checked-out local branches for git URLs
- Checks sync status vs origin (with fetch)
- Prints clear summary + warnings for unsynced repos
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

import tomli
import tomli_w


DEPS_CONFIG: List[Dict[str, str]] = [
    {"name": "b3-geo", "local_dir": "b3_geo", "repo": "b3_geo"},
    {"name": "b3_msh", "local_dir": "b3_msh", "repo": "b3_msh"},
    {"name": "b3_drp", "local_dir": "b3_drp", "repo": "b3_drp"},
    {"name": "b3-2d", "local_dir": "b3_2d", "repo": "b3_2d"},
    {"name": "b3_mat", "local_dir": "b3_mat", "repo": "b3_mat"},
    {"name": "cgfoil", "local_dir": "cgfoil", "repo": "cgfoil"},
    {"name": "b3_state", "local_dir": "b3_state", "repo": "b3_state"},
    {"name": "b3_yml", "local_dir": "b3_yml", "repo": "b3_yml"},
]

BEM_CONFIG: Dict[str, str] = {"name": "b3_bem", "local_dir": "b3_bem", "repo": "b3_bem"}


def get_current_branch(repo_path: Path) -> str:
    """Return current branch name. Falls back to 'main'."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        branch = result.stdout.strip()
        return branch if branch and branch != "HEAD" else "main"
    except Exception:
        return "main"


def check_sync_status(repo_path: Path, branch: str) -> Tuple[bool, str]:
    """Return (is_synced, status_message). Performs git fetch."""
    try:
        subprocess.run(
            ["git", "-C", str(repo_path), "fetch", "--quiet", "origin", branch],
            capture_output=True,
            check=True,
            timeout=12,
        )

        local_sha = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        remote_sha = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", f"origin/{branch}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        if local_sha == remote_sha:
            return True, "synced ✓"

        # Count ahead/behind
        behind = int(
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo_path),
                    "rev-list",
                    "--count",
                    f"HEAD..origin/{branch}",
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )

        ahead = int(
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo_path),
                    "rev-list",
                    "--count",
                    f"origin/{branch}..HEAD",
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )

        if ahead > 0 and behind > 0:
            status = f"diverged ({ahead}↑ {behind}↓)"
        elif behind > 0:
            status = f"behind by {behind}"
        else:
            status = f"ahead by {ahead}"
        return False, f"needs sync ❌ ({status})"

    except Exception as e:
        return False, f"check failed ⚠️ ({str(e)[:60]})"


def main() -> None:
    os.environ.pop("VIRTUAL_ENV", None)

    parser = argparse.ArgumentParser(description="b3m dep switcher (git/local)")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--git", action="store_true", help="Switch to git+ URLs using local branches"
    )
    g.add_argument(
        "--local", action="store_true", help="Switch to local file:// editable installs"
    )
    args = parser.parse_args()

    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("❌ pyproject.toml not found in current directory")
        sys.exit(1)

    with open(pyproject, "rb") as f:
        data = tomli.load(f)

    project = data.setdefault("project", {})
    base_deps = [
        "treeparse",
        "b3_state",
        "pydantic",
        "pyyaml",
        "tomli>=2.3.0",
        "tomli-w>=1.2.0",
    ]

    root = Path.cwd().parent.resolve()

    print("🔧 b3m Dependency Manager")
    print("=" * 55)

    sync_issues = []

    if args.git:
        print("🌐 Switching to GIT mode (dynamic branches from local repos)...\n")
        dep_lines: List[str] = []

        for d in DEPS_CONFIG:
            repo_path = root / d["local_dir"]
            branch = get_current_branch(repo_path)

            if repo_path.exists():
                synced, status = check_sync_status(repo_path, branch)
                if not synced:
                    sync_issues.append(f"{d['name']}@{branch} → {status}")
                print(f"   {d['name']:12} @ {branch:<12} {status}")
            else:
                print(f"   {d['name']:12} @ {branch:<12} (dir missing)")
            dep_lines.append(
                f"{d['name']} @ git+https://github.com/wr1/{d['repo']}.git@{branch}"
            )

        # b3_bem (optional)
        bem_path = root / BEM_CONFIG["local_dir"]
        bem_branch = get_current_branch(bem_path)
        if bem_path.exists():
            synced, status = check_sync_status(bem_path, bem_branch)
            if not synced:
                sync_issues.append(f"b3_bem@{bem_branch} → {status}")
            print(f"   b3_bem      @ {bem_branch:<12} {status}")
            bem_line = f"b3_bem @ git+https://github.com/wr1/b3_bem.git@{bem_branch}"
        else:
            bem_line = "b3_bem @ git+https://github.com/wr1/b3_bem.git@main"

        project["dependencies"] = base_deps + dep_lines
        project.setdefault("optional-dependencies", {})["bem"] = ["ccblade", bem_line]

    else:  # --local
        print("📁 Switching to LOCAL editable mode...\n")
        dep_lines: List[str] = []

        for d in DEPS_CONFIG:
            p = root / d["local_dir"]
            url = f"{d['name']} @ file://{p}"
            dep_lines.append(url)
            print(f"   {d['name']:12} → local ({d['local_dir']})")

        project["dependencies"] = base_deps + dep_lines

        bem_p = root / BEM_CONFIG["local_dir"]
        if bem_p.exists():
            bem_line = f"b3_bem @ file://{bem_p}"
            project.setdefault("optional-dependencies", {})["bem"] = [
                "ccblade",
                bem_line,
            ]
            print("   b3_bem       → local")
        else:
            print("   b3_bem       (not found locally)")

    # Common fixes
    data["build-system"] = {
        "requires": ["hatchling"],
        "build-backend": "hatchling.build",
    }
    data.setdefault("tool", {}).setdefault("hatch", {}).setdefault("metadata", {})[
        "allow-direct-references"
    ] = True

    # Cleanup
    if "tool" in data and isinstance(data["tool"], dict):
        data["tool"].pop("uv", None)
    Path("uv.lock").unlink(missing_ok=True)

    with open(pyproject, "wb") as f:
        tomli_w.dump(data, f)

    print("\n✅ pyproject.toml updated successfully.")
    print("   Run: uv sync")

    if args.git:
        if sync_issues:
            print("\n⚠️  SOME REPOS NOT SYNCED WITH REMOTE:")
            for issue in sync_issues:
                print(f"     ❌ {issue}")
            print(
                "\n   Git installs will differ from your local work until you push or pull."
            )
            print("   Recommended: git push in the affected repositories.")
        else:
            print("\n🎉 All repositories are synced with their remote branches.")
            print("   Git mode will behave identically to your local code.")

    print("=" * 55)


if __name__ == "__main__":
    main()
