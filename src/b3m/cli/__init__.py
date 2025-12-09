"""CLI module for b3m."""

import sys
from pathlib import Path

from treeparse import cli
from .build import build_group as build_app

build_app.sort_key = 0

super_app = cli(
    name="b3m",
    help="b3m CLI for blade modeling.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    subgroups=[build_app],
)


def main():
    super_app.run()


if __name__ == "__main__":
    main()
