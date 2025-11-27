import argparse
import logging
import os
import shutil
import yaml
from pathlib import Path
from rich.logging import RichHandler
from b3_geo.api.af_step import AFStep
from b3_geo.api.loft_step import LoftStep
from b3_msh.statesman.statesman_step import B3MshStep as MeshStep
from b3_drp import DrapeStep
from b3_2d.statesman.b3_2d_step import B32dStep
from b3_geo.api.planform import process_planform as process_plan

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_time=False)],
)
logger = logging.getLogger(__name__)


def build_blade(config_path, force=False):
    logger.info(f"Starting blade build with config: {config_path}")
    # Load config to get workdir
    with open(config_path) as f:
        config = yaml.safe_load(f)
    config_dir = Path(config_path).parent
    workdir = config_dir / config["workdir"]
    if force and workdir.exists():
        logger.info(f"Force overwrite: removing existing workdir {workdir}")
        shutil.rmtree(workdir)
    logger.info("Processing airfoils...")
    af_step = AFStep(config_path)
    af_step.run()
    logger.info("Processing loft...")
    loft_step = LoftStep(config_path)
    loft_step.run()
    logger.info("Generating mesh...")
    mesh_step = MeshStep(config_path)
    mesh_step.run()
    logger.info("Assigning plies...")
    drape_step = DrapeStep(config_path)
    drape_step.run()
    logger.info("Processing 2D meshing...")
    b3_2d_step = B32dStep(config_path)
    b3_2d_step.run()
    logger.info("Blade build completed.")


def main():
    parser = argparse.ArgumentParser(description="Build blade from config.")
    parser.add_argument(
        "-c", "--config", type=str, required=True, help="Path to config file"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite by cleaning the workdir first",
    )
    args = parser.parse_args()
    config_path = os.path.abspath(args.config)
    build_blade(config_path, force=args.force)


if __name__ == "__main__":
    main()
