import sys
from pathlib import Path

# Add paths to sub-project source directories
sys.path.append(str(Path(__file__).parent.parent.parent / "b3_geo" / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "b3_msh" / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "b3_pln" / "src"))

from treeparse import cli
from b3_geo.cli import app as geo_app
from b3_msh.cli import app as msh_app
from b3_pln.cli import app as pln_app

# Set names for subgroups
geo_app.name = "geo"
msh_app.name = "msh"
pln_app.name = "pln"

super_app = cli(
    name="b3m",
    help="b3m CLI for blade modeling.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    theme="monochrome",
    subgroups=[geo_app, msh_app, pln_app],
)


def main():
    super_app.run()


if __name__ == "__main__":
    main()
