#!/usr/bin/env python3
"""Minimal example showing how b3m now uses b3-yml datasets."""

from b3_yml import prepare_dataset

# Option 1: Get a clean folder (recommended for examples / integration)
yml_path = prepare_dataset("blade_test")  # or "blade_test_ribbon"
print(f"✅ Dataset ready at: {yml_path}")
print("   airfoils/ and polars/ copied automatically")

# Option 2: Direct access (fast for unit tests)
# from b3_yml import load_yaml, get_path
# config = load_yaml("blade_test")
# airfoil = get_path("airfoils", "DU93-W-210_smoothed_dero_0.210.dat")

# Now feed into your existing b3m loader (it already expects relative paths)
print("\nNow pass yml_path to your b3m build pipeline!")
