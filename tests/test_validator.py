import pytest
import yaml
from pathlib import Path
from b3m.validator import validate_config, B3mConfig


def test_valid_config(tmp_path):
    """Test validation of a valid config."""
    config_data = {
        "workdir": "test_workdir",
        "geometry": {
            "planform": {
                "z": [[0.0, 0.0], [1.0, 1.0]],
                "chord": [[0.0, 1.0], [1.0, 0.5]],
                "thickness": [[0.0, 0.1], [1.0, 0.05]],
                "twist": [[0.0, 0.0], [1.0, 10.0]],
                "dx": [[0.0, 0.0], [1.0, 0.0]],
                "dy": [[0.0, 0.0], [1.0, 0.0]],
                "npchord": 200,
                "npspan": 100,
            }
        },
        "airfoils": [
            {"path": "naca0018.dat", "name": "naca0018", "thickness": 0.18}
        ],
        "mesh": {
            "z": [{"type": "linspace", "values": [0.0, 1.0], "num": 10}],
            "chordwise": {
                "default": {"n_elem": 100},
                "panels": []
            }
        },
        "structure": {
            "webs": []
        },
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    config = validate_config(str(config_file))
    assert isinstance(config, B3mConfig)
    assert config.workdir == "test_workdir"
    assert len(config.airfoils.root) == 1


def test_invalid_config_missing_workdir(tmp_path):
    """Test validation fails with missing workdir."""
    config_data = {
        "geometry": {},
        "airfoils": [],
        "mesh": {},
        "structure": {},
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    with pytest.raises(Exception):
        validate_config(str(config_file))


def test_invalid_config_bad_airfoil(tmp_path):
    """Test validation fails with invalid airfoil data."""
    config_data = {
        "workdir": "test",
        "geometry": {},
        "airfoils": [{"path": "file.dat", "name": "test", "thickness": "not_a_number"}],
        "mesh": {},
        "structure": {},
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    with pytest.raises(Exception):
        validate_config(str(config_file))
