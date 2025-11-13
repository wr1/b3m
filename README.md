# b3m

b3m is a command-line interface (CLI) tool for blade modeling, integrating functionalities from three sub-projects: geometry processing (b3_geo), meshing (b3_msh), and draping (b3_drp). It leverages the `treeparse` library for CLI management and provides a unified interface for blade-related workflows.

## Features

- **Geometry Processing**: Handle airfoils and lofting steps.
- **Meshing**: Generate meshes for blade models.
- **Draping**: Assign plies to blade structures.
- **Modular CLI**: Organized subgroups for different functionalities.
- **Example Workflow**: Includes a sample script for building blades from configuration files.

## Installation

Ensure you have Python 3.8+ and `uv` installed. Clone the repository and install dependencies:

```bash
git clone https://github.com/wr1/b3m.git
cd b3m
uv sync --dev
```

For local development with sub-projects, ensure the paths in `pyproject.toml` point to your local copies of `b3_geo`, `b3_msh`, and `b3_drp`.

## Usage

### CLI

Run the CLI with:

```bash
uv run b3m
```

This will display the help for the main CLI, with subgroups:

- `geo`: Geometry-related commands.
- `msh`: Meshing-related commands.
- `drp`: Draping-related commands.

Each subgroup has its own commands; use `uv run b3m <subgroup> --help` for details.

### Example: Build Blade

Use the provided example script to build a blade from a YAML config file:

```bash
python examples/build_blade.py -c path/to/config.yaml --force
```

The config file should specify the workdir and other parameters. See the script for details.

## Development

- **Linting and Formatting**: Use `ruff` for code quality.
- **Testing**: Run tests with `pytest`.
- **Local Admin Script**: Use `admin.sh` for automated checks and commits (see the script for details).

To contribute:

1. Fork the repo.
2. Create a feature branch.
3. Make changes, ensuring tests pass.
4. Submit a PR.

## License

MIT
