import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from b3m.integration import build_blade


@pytest.fixture
def sample_config():
    """Create a sample config for testing."""
    config = {
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
        "laminates": {},
        "matdb": {}
    }
    return config


def test_full_pipeline(sample_config):
    """Test the full b3m pipeline with mocked file loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        # Create a dummy airfoil file
        airfoil_path = Path(tmpdir) / "naca0018.dat"
        airfoil_path.write_text("NACA0018\n0.0 0.0\n0.5 0.05\n1.0 0.0")
        
        # Mock the steps to avoid actual computation
        with patch('b3m.integration.AFStep') as mock_af, \
             patch('b3m.integration.LoftStep') as mock_loft, \
             patch('b3m.integration.MeshStep') as mock_mesh, \
             patch('b3m.integration.DrapeStep') as mock_drape, \
             patch('b3m.integration.B32dStep') as mock_2d:
            
            # Run the build
            build_blade(str(config_path), force=True)
            
            # Assert steps were called
            mock_af.assert_called_once_with(str(config_path))
            mock_af.return_value.run.assert_called_once()
            mock_loft.assert_called_once_with(str(config_path))
            mock_loft.return_value.run.assert_called_once()
            mock_mesh.assert_called_once_with(str(config_path))
            mock_mesh.return_value.run.assert_called_once()
            mock_drape.assert_called_once_with(str(config_path))
            mock_drape.return_value.run.assert_called_once()
            mock_2d.assert_called_once_with(str(config_path))
            mock_2d.return_value.run.assert_called_once()
