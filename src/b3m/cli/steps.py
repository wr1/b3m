"""Step functions for blade building."""

import json
import logging
import multiprocessing
import os
import shutil
import yaml
from pathlib import Path
from rich.logging import RichHandler
import pyvista as pv
from rich.progress import Progress

from b3_geo.api.af_step import AFStep
from b3_geo.api.loft_step import LoftStep
from b3_msh.step.blade_mesh_step import B3MshStep as MeshStep
from b3_drp import DrapeStep
from b3_2d.state import B32dStep
from b3_2d.state import B32dAnbaStep
from b3_2d.core.plotting import plot_section_anba
from b3_2d.core.span_plotting import plot_span_anba

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_time=False)],
)
logger = logging.getLogger(__name__)


def process_airfoils(config: str, force: bool = False) -> None:
    """Process airfoils from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
    logger.info("Processing airfoils...")
    af_step = AFStep(config)
    af_step.run(force=force)


def process_loft(config: str, force: bool = False) -> None:
    """Process loft from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
    logger.info("Processing loft...")
    loft_step = LoftStep(config)
    loft_step.run(force=force)


def process_mesh(config: str, force: bool = False) -> None:
    """Generate mesh from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
    logger.info("Generating mesh...")
    mesh_step = MeshStep(config)
    mesh_step.run(force=force)


def assign_plies(config: str, force: bool = False) -> None:
    """Assign plies from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
    logger.info("Assigning plies...")
    drape_step = DrapeStep(config)
    drape_step.run(force=force)


def process_2d_meshing(config: str, force: bool = False) -> None:
    """Process 2D meshing from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
    logger.info("Processing 2D meshing...")
    b3_2d_step = B32dStep(config)
    b3_2d_step.run(force=force)


def process_anba(config: str, force: bool = False) -> None:
    """Process ANBA from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
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
    plot_section_anba(mesh, data, str(output_file), log_file, lock)


def plot_anba(config: str, force: bool = False) -> None:
    """Plot ANBA results from config."""
    if force:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        config_dir = Path(config).parent
        workdir = config_dir / config_data["workdir"]
        state_file = workdir / ".statesman_state.yaml"
        if state_file.exists():
            state_file.unlink()
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
                pool.starmap(
                    plot_single, [(f, plot_log_file, lock) for f in anba_files]
                )
            progress.update(spinner, completed=True)
    # Span plotting
    span_output_file = anba_results_dir / "span_plot.png"
    plot_span_anba(str(output_dir), str(span_output_file))
    with open(plot_log_file, "a") as f:
        f.write(f"ANBA plotting completed, log saved to {plot_log_file}\n")
    logger.info(f"ANBA plotting completed, log saved to {plot_log_file}.")


def build_blade(config: str, force: bool = False) -> None:
    """Build blade from config."""
    config = os.path.abspath(config)
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
