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
from b3_2d.state import B32dStep, B32dAnbaStep
from b3_2d.core.plotting import plot_anba_results
import json
import pyvista as pv
import multiprocessing
from rich.progress import Progress

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


def process_mesh(config: str, force: bool = False) -> None:
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


def process_anba(config: str, force: bool = False) -> None:
    """Process ANBA from config."""
    logger.info("Processing ANBA...")
    b3_2d_anba_step = B32dAnbaStep(config)
    b3_2d_anba_step.run(force=force)


def plot_single(anba_file: Path, log_file: Path, lock) -> None:
    """Plot a single ANBA result."""
    section_dir = anba_file.parent
    vtk_file = section_dir / "output.vtk"
    if not vtk_file.exists():
        with lock:
            with open(log_file, "a") as f:
                f.write(f"VTK file not found: {vtk_file}\n")
        return
    with open(anba_file, "r") as f:
        data = json.load(f)
    output_file = section_dir / "anba_plot.png"
    mesh = pv.read(str(vtk_file))
    plot_anba_results(mesh, data, str(output_file), log_file, lock)


def plot_anba(config: str, force: bool = False) -> None:
    """Plot ANBA results from config."""
    logger.info("Plotting ANBA results...")
    config_dir = Path(config).parent
    with open(config, "r") as f:
        config_data = yaml.safe_load(f)
    workdir = config_dir / config_data["workdir"]
    output_dir = workdir / "b3_2d"
    anba_results_dir = workdir / "anba4_results"
    anba_results_dir.mkdir(exist_ok=True)
    plot_log_file = anba_results_dir / "anba_plot.log"
    with open(plot_log_file, "w") as f:
        f.write("Starting ANBA plotting\n")
    anba_files = list(output_dir.glob("section_*/anba_out.json"))
    if not anba_files:
        with open(plot_log_file, "a") as f:
            f.write("No anba_out.json files found\n")
        logger.warning("No anba_out.json files found")
        return
    num_processes = min(multiprocessing.cpu_count(), len(anba_files))
    with multiprocessing.Manager() as manager:
        lock = manager.Lock()
        with Progress() as progress:
            spinner = progress.add_task("Plotting ANBA results...", total=None)
            with multiprocessing.Pool(processes=num_processes) as pool:
                pool.starmap(plot_single, [(f, plot_log_file, lock) for f in anba_files])
            progress.update(spinner, completed=True)
    with open(plot_log_file, "a") as f:
        f.write(f"ANBA plotting completed, log saved to {plot_log_file}\n")
    logger.info(f"ANBA plotting completed, log saved to {plot_log_file}.")


def build_blade(config: str, force: bool = False) -> None:
    """Build blade build from config."""
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
    process_mesh(config, force)
    assign_plies(config, force)
    process_2d_meshing(config, force)
    process_anba(config, force)
    plot_anba(config, force)
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
