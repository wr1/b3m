#!/usr/bin/env python3
"""
Minimal, robust, future-proof dependency switcher (direct TOML edit).
No uv add calls → never triggers workspace/unmanaged errors again.

Usage:
    uv run python scripts/manage_deps.py --git      # default (everyone/CI)
    uv run python scripts/manage_deps.py --local    # your machine only
"""
import argparse
import os
from pathlib import Path
import tomli
import tomli_w

def load():
    p = Path("pyproject.toml")
    with open(p, "rb") as f:
        return tomli.load(f), p

def save(data, p):
    with open(p, "wb") as f:
        tomli_w.dump(data, f)

def main():
    os.environ.pop("VIRTUAL_ENV", None)

    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--git", action="store_true")
    g.add_argument("--local", action="store_true")
    args = parser.parse_args()

    data, path = load()

    # Remove any old tool.uv section completely
    data.pop("tool", None)

    deps = data.setdefault("project", {}).setdefault("dependencies", [])
    bem = data.setdefault("project", {}).setdefault("optional-dependencies", {}).setdefault("bem", [])

    if args.git:
        print("🌐 Setting git URLs (standalone mode)...")
        git_map = {
            "b3-geo": "b3-geo @ git+https://github.com/wr1/b3_geo.git@dev1",
            "b3_msh": "b3_msh @ git+https://github.com/wr1/b3_msh.git@mul3d1",
            "b3_drp": "b3_drp @ git+https://github.com/wr1/b3_drp.git@dev1",
            "b3-2d": "b3-2d @ git+https://github.com/wr1/b3_2d.git@dev3",
            "b3_mat": "b3_mat @ git+https://github.com/wr1/b3_mat.git@dev1",
            "cgfoil": "cgfoil @ git+https://github.com/wr1/cgfoil.git@dev1",
        }
        for i, line in enumerate(deps[:]):
            for pkg, url in git_map.items():
                if pkg in line:
                    deps[i] = url
                    break
        bem[:] = [x for x in bem if "b3_bem" not in x] + ["b3_bem @ git+https://github.com/wr1/b3_bem.git@dev1"]
    else:
        print("🔧 Setting local editable mode...")
        local_map = {
            "b3-geo": "b3-geo @ ../b3_geo",
            "b3_msh": "b3_msh @ ../b3_msh",
            "b3_drp": "b3_drp @ ../b3_drp",
            "b3-2d": "b3-2d @ ../b3_2d",
            "b3_mat": "b3_mat @ ../b3_mat",
            "cgfoil": "cgfoil @ ../cgfoil",
        }
        for i, line in enumerate(deps[:]):
            for pkg, path in local_map.items():
                if pkg in line:
                    deps[i] = path
                    break
        bem[:] = [x for x in bem if "b3_bem" not in x] + ["b3_bem @ ../b3_bem"]

    Path("uv.lock").unlink(missing_ok=True)
    save(data, path)
    print("✅ pyproject.toml updated")
    print("Run: uv sync")

if __name__ == "__main__":
    main()
