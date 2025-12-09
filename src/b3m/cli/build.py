"""CLI for blade build functionality."""

import logging
from pathlib import Path
from rich.logging import RichHandler
from treeparse import command, argument, option, group
import yaml
import shutil
from b3_geo.api.af_step import AFStep
from b3_geo.api.loft_step import LoftStep
from b3_msh.core.mesh_step import B3MshStep as MeshStep
from b3_drp import DrapeStep
from b3_2d.statesman.b3_2d_step import B32dStep

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_time=False)],
)
logger = logging.getLogger(__name__)


def process_airfoils(config: str, force: bool = False) -> None:
    """Process airfoils from config."""
    logger.info("Processing airfoils...")
    af_step = AFStep(config)
    af_step.run(force=force)


def process_loft(config: str, force: bool = False) -> None:
    """Process loft from config."""
    logger.info("Processing loft...")
    loft_step = LoftStep(config)
    loft_step.run(force=force)


def generate_mesh(config: str, force: bool = False) -> None:
    """Generate mesh from config."""
    logger.info("Generating mesh...")
    mesh_step = MeshStep(config)
    mesh_step.run(force=force)


def assign_plies(config: str, force: bool = False) -> None:
    """Assign plies from config."""
    logger.info("Assigning plies...")
    drape_step = DrapeStep(config)
    drape_step.run(force=force)


def process_2d_meshing(config: str, force: bool = False) -> None:
    """Process 2D meshing from config."""
    logger.info("Processing 2D meshing...")
    b3_2d_step = B32dStep(config)
    b3_2d_step.run(force=force)


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
    process_airfoils(config, force)
    process_loft(config, force)
    generate_mesh(config, force)
    assign_plies(config, force)
    process_2d_meshing(config, force)
    logger.info("Blade build completed.")


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
    callback=generate_mesh,
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
    commands=[airfoils_cmd, loft_cmd, mesh_cmd, drape_cmd, b3_2d_cmd, full_cmd],
)
