"""CLI module for b3m."""

import sys
from pathlib import Path

# Add paths to sub-project source directories
sys.path.append(str(Path(__file__).parent.parent.parent / "b3_geo" / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "b3_msh" / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "b3_drp" / "src"))

from treeparse import cli
from b3_geo.cli import app as geo_app
from b3_msh.cli.cli import app as msh_app
from b3_drp.cli.cli import app as drp_app

# Set names and sort keys for subgroups
geo_app.name = "geo"
geo_app.sort_key = 0
msh_app.name = "msh"
msh_app.sort_key = 1
drp_app.name = "drp"
drp_app.sort_key = 2

super_app = cli(
    name="b3m",
    help="b3m CLI for blade modeling.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    subgroups=[geo_app, msh_app, drp_app],
)


def main():
    super_app.run()


if __name__ == "__main__":
    main()
