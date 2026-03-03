#!/usr/bin/env python3
"""
Final robust dependency switcher for b3m.

Rebuilds everything + adds the hatchling allow-direct-references flag.
This is the permanent fix for the metadata error.
"""
import argparse
import os
from pathlib import Path
import tomli
import tomli_w

def main():
    os.environ.pop("VIRTUAL_ENV", None)

    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--git", action="store_true")
    g.add_argument("--local", action="store_true")
    args = parser.parse_args()

    p = Path("pyproject.toml")
    with open(p, "rb") as f:
        data = tomli.load(f)

    project = data.setdefault("project", {})

    base = [
        "treeparse",
        "statesman",
        "pydantic",
        "pyyaml",
        "tomli>=2.3.0",
        "tomli-w>=1.2.0",
    ]

    root = Path.cwd().parent.resolve()

    if args.git:
        print("🌐 Setting git URLs (default/committed state)...")
        b3 = [
            "b3-geo @ git+https://github.com/wr1/b3_geo.git@dev1",
            "b3_msh @ git+https://github.com/wr1/b3_msh.git@mul3d1",
            "b3_drp @ git+https://github.com/wr1/b3_drp.git@dev1",
            "b3-2d @ git+https://github.com/wr1/b3_2d.git@dev3",
            "b3_mat @ git+https://github.com/wr1/b3_mat.git@dev1",
            "cgfoil @ git+https://github.com/wr1/cgfoil.git@dev1",
        ]
        bem_line = "b3_bem @ git+https://github.com/wr1/b3_bem.git@dev1"
    else:
        print("🔧 Setting local editable mode (absolute file://)...")
        b3 = [
            f"b3-geo @ file://{root / 'b3_geo'}",
            f"b3_msh @ file://{root / 'b3_msh'}",
            f"b3_drp @ file://{root / 'b3_drp'}",
            f"b3-2d @ file://{root / 'b3_2d'}",
            f"b3_mat @ file://{root / 'b3_mat'}",
            f"cgfoil @ file://{root / 'cgfoil'}",
        ]
        bem_line = f"b3_bem @ file://{root / 'b3_bem'}"

    project["dependencies"] = base + b3
    project.setdefault("optional-dependencies", {})["bem"] = ["ccblade", bem_line]

    # Force build-system + hatchling flag (this fixes the metadata error)
    data["build-system"] = {"requires": ["hatchling"], "build-backend": "hatchling.build"}
    data.setdefault("tool", {}).setdefault("hatch", {}).setdefault("metadata", {})["allow-direct-references"] = True

    # Remove any old tool.uv section
    data.pop("tool", None) if "uv" in data.get("tool", {}) else None

    Path("uv.lock").unlink(missing_ok=True)

    with open(p, "wb") as f:
        tomli_w.dump(data, f)

    print("✅ pyproject.toml rebuilt with allow-direct-references = true")
    print("Run: uv sync")

if __name__ == "__main__":
    main()
