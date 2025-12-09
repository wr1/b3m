"""CLI for blade build functionality."""

import logging
from pathlib import Path
from rich.logging import RichHandler
from treeparse import cli, command, argument, option
import yaml
import shutil
import os
from b3_geo.api.af_step import AFStep
from b3_geo.api.loft_step import LoftStep
from b3_msh.statesman.statesman_step import B3MshStep as MeshStep
from b3_drp import DrapeStep
from b3_2d.statesman.b3_2d_step import B32dStep

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_time=False)],
)
logger = logging.getLogger(__name__)


def process_airfoils(config: str) -> None:
    """Process airfoils from config."""
    logger.info("Processing airfoils...")
    af_step = AFStep(config)
    af_step.run()


def process_loft(config: str) -> None:
    """Process loft from config."""
    logger.info("Processing loft...")
    loft_step = LoftStep(config)
    loft_step.run()


def generate_mesh(config: str) -> None:
    """Generate mesh from config."""
    logger.info("Generating mesh...")
    mesh_step = MeshStep(config)
    mesh_step.run()


def assign_plies(config: str) -> None:
    """Assign plies from config."""
    logger.info("Assigning plies...")
    drape_step = DrapeStep(config)
    drape_step.run()


def process_2d_meshing(config: str) -> None:
    """Process 2D meshing from config."""
    logger.info("Processing 2D meshing...")
    b3_2d_step = B32dStep(config)
    b3_2d_step.run()


def build_blade(config: str, force: bool = False) -> None:
    """Build blade from config."""
    logger.info(f"Starting blade build with config: {config}")
    # Load config to get workdir
    with open(config) as f:
        config_data = yaml.safe_load(f)
    config_dir = Path(config).parent
    workdir = config_dir / config_data["workdir"]
    if force and workdir.exists():
        logger.info(f"Force overwrite: removing existing workdir {workdir}")
        shutil.rmtree(workdir)
    process_airfoils(config)
    process_loft(config)
    generate_mesh(config)
    assign_plies(config)
    process_2d_meshing(config)
    logger.info("Blade build completed.")


airfoils_cmd = command(
    name="airfoils",
    help="Process airfoils step.",
    callback=process_airfoils,
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
)

loft_cmd = command(
    name="loft",
    help="Process loft step.",
    callback=process_loft,
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
)

mesh_cmd = command(
    name="mesh",
    help="Generate mesh step.",
    callback=generate_mesh,
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
)

drape_cmd = command(
    name="drape",
    help="Assign plies step.",
    callback=assign_plies,
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
)

b3_2d_cmd = command(
    name="2d",
    help="Process 2D meshing step.",
    callback=process_2d_meshing,
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
)

build_cmd = command(
    name="full",
    help="Build blade from config.",
    callback=build_blade,
    arguments=[argument(name="config", arg_type=str, help="Path to config file")],
)

app = cli(
    name="build",
    help="Blade build CLI.",
    commands=[airfoils_cmd, loft_cmd, mesh_cmd, drape_cmd, b3_2d_cmd, build_cmd],
    options=[
        option(
            flags=["--force", "-f"],
            arg_type=bool,
            default=False,
            help="Force overwrite by cleaning the workdir first",
        )
    ],
)
