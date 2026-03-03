#!/usr/bin/env python3
"""
Simple helper after switching to inline git dependencies.

Git is now the default (works perfectly on every machine / CI).

For local editable development (sibling repos):
    python scripts/setup-dev.py
    uv sync --override dev-overrides.txt

Usage (optional):
    ./scripts/local_git.py --local   # just prints the commands above
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="b3m dev helper (git is default)")
    parser.add_argument(
        "-l", "--local", action="store_true", help="Show local dev instructions"
    )
    args = parser.parse_args()

    if args.local:
        print("🔧 LOCAL DEV MODE")
        print("1. python scripts/setup-dev.py")
        print("2. uv sync --override dev-overrides.txt")
    else:
        print("🌍 GIT MODE (default - works everywhere)")
        print("Run: uv sync")

    print(
        "\n✅ No more source toggling needed - inline git in pyproject.toml fixes the workspace conflict."
    )


if __name__ == "__main__":
    main()
