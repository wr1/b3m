from pathlib import Path
import yaml
import pytest
from b3_yml import prepare_dataset, load_yaml


@pytest.fixture
def blade_test_path(tmp_path: Path):
    """Fixture that gives a clean blade_test dataset ready for b3m integration tests."""
    return prepare_dataset("blade_test", target_dir=tmp_path / "temp_blade")


def test_b3_yml_can_be_imported():
    """Sanity check that b3-yml is installed and importable."""
    assert prepare_dataset is not None
    assert load_yaml is not None


def test_prepare_dataset_creates_working_folder(blade_test_path: Path):
    """b3m can now get a full dataset with correct relative paths to airfoils/polars."""
    assert blade_test_path.exists()
    assert (blade_test_path.parent / "airfoils").is_dir()
    assert (blade_test_path.parent / "polars").is_dir()

    # Load the *actual copied YAML* we just prepared (not the global packaged version)
    with open(blade_test_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert config["workdir"] == str(blade_test_path.parent)
    assert "bem" in config
    assert config["bem"]["B"] == 3
