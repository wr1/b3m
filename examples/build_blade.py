import sys
from pathlib import Path

# Add paths to sub-project source directories
sys.path.append(str(Path(__file__).parent.parent / "b3_geo" / "src"))
sys.path.append(str(Path(__file__).parent.parent / "b3_msh" / "src"))
sys.path.append(str(Path(__file__).parent.parent / "b3_drp" / "src"))

from b3_geo.api.plan import process_plan
from b3_geo.api.af_step import AFStep
from b3_geo.api.loft_step import LoftStep
from b3_msh.core.mesh import MeshStep


def build_blade(config_path: str):
    """Run the full blade building workflow: planform -> geometry -> mesh."""
    print(f"Starting blade build with config: {config_path}")

    # Step 1: Process planform
    print("Processing planform...")
    process_plan(config_path)

    # Step 2: Process airfoils
    print("Processing airfoils...")
    af_step = AFStep(config_path)
    af_step.run()

    # Step 3: Process loft
    print("Processing loft...")
    loft_step = LoftStep(config_path)
    loft_step.run()

    # Step 4: Generate mesh
    print("Generating mesh...")
    mesh_step = MeshStep(config_path)
    mesh_step.run()

    print("Blade build completed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Demo script to build a blade using b3m workflow."
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to the YAML config file",
    )

    args = parser.parse_args()
    build_blade(args.config)
