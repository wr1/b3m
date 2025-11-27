#!/usr/bin/env python3
"""Example script to validate a b3m config file."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from b3m.validator import validate_config


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_config.py <config.yaml>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    try:
        config = validate_config(config_path)
        print(f"Config validation successful for {config_path}")
        print(f"Workdir: {config.workdir}")
        print(f"Number of airfoils: {len(config.airfoils)}")
    except Exception as e:
        print(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
