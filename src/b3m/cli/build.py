"""CLI for blade build functionality."""

import logging
from pathlib import Path
from rich.logging import RichHandler
from treeparse import command, argument, option, group
import yaml
import shutil
from .steps import (
    process_airfoils,
    process_loft,
    process_mesh,
    assign_plies,
    process_2d_meshing,
    process_anba,
    plot_anba,
    build_blade,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_time=False)],
)
logger = logging.getLogger(__name__)

airfoils_cmd = command(
    name="airfoils",
    help="Process airfoils step.",
    callback=process_airfoils,
)

loft_cmd = command(
    name="loft",
    help="Process loft step.",
    callback=process_loft,
)

mesh_cmd = command(
    name="mesh",
    help="Generate mesh step.",
    callback=process_mesh,
)

drape_cmd = command(
    name="drape",
    help="Assign plies step.",
    callback=assign_plies,
)

b3_2d_cmd = command(
    name="2d",
    help="Process 2D meshing step.",
    callback=process_2d_meshing,
)

anba_cmd = command(
    name="anba",
    help="Process ANBA step.",
    callback=process_anba,
)

plot_cmd = command(
    name="plot",
    help="Plot ANBA results.",
    callback=plot_anba,
)

full_cmd = command(
    name="full",
    help="Build full blade from config.",
    callback=build_blade,
)

build_group = group(
    name="build",
    help="Blade build CLI.",
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
    options=[
        option(
            flags=["--force", "-f"],
            arg_type=bool,
            default=False,
            help="Force overwrite by cleaning the workdir first",
        )
    ],
    commands=[
        airfoils_cmd,
        loft_cmd,
        mesh_cmd,
        drape_cmd,
        b3_2d_cmd,
        anba_cmd,
        plot_cmd,
        full_cmd,
    ],
)
