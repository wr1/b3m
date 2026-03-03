#!/usr/bin/env python3
"""
Generate git-overrides.txt (git branches by default).

Run once on any machine (including clean/CI):
    python scripts/setup-git.py
    uv sync --override git-overrides.txt

This is the robust default that works inside the projects/b3 workspace.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()

# Exact git references (update branches here if needed)
GIT_OVERRIDES = {
    "b3-geo": "git+https://github.com/wr1/b3_geo.git@dev1",
    "b3_msh": "git+https://github.com/wr1/b3_msh.git@mul3d1",
    "b3_drp": "git+https://github.com/wr1/b3_drp.git@dev1",
    "b3-2d": "git+https://github.com/wr1/b3_2d.git@dev3",
    "b3_bem": "git+https://github.com/wr1/b3_bem.git@dev1",
    "b3_mat": "git+https://github.com/wr1/b3_mat.git@dev1",
    "cgfoil": "git+https://github.com/wr1/cgfoil.git@dev1",
}

lines = [f"{pkg} @ {url}" for pkg, url in GIT_OVERRIDES.items()]

(ROOT / "git-overrides.txt").write_text("\n".join(lines) + "\n")
print("✅ Generated git-overrides.txt")
print("\nNow run:")
print("   uv sync --override git-overrides.txt")
print("\n(After this, future uv sync commands can reuse the override)")
