import pytest
from unittest.mock import patch
from examples.build_blade import build_blade


def test_build_blade(tmp_path):
    """Test the build_blade function with mocked dependencies."""
    # Create a temporary config file
    config_file = tmp_path / "config.yaml"
    config_file.write_text("workdir: test_workdir\n")
    # Create the workdir to simulate existing directory for force overwrite
    (tmp_path / "test_workdir").mkdir()

    with patch('examples.build_blade.AFStep') as mock_af_step, \
         patch('examples.build_blade.LoftStep') as mock_loft_step, \
         patch('examples.build_blade.MeshStep') as mock_mesh_step, \
         patch('examples.build_blade.DrapeStep') as mock_drape_step, \
         patch('examples.build_blade.shutil.rmtree') as mock_rmtree:

        # Call build_blade with force=True
        build_blade(str(config_file), force=True)

        # Assert that rmtree was called since force=True and workdir exists
        mock_rmtree.assert_called_once_with(tmp_path / "test_workdir")

        # Assert that each step was instantiated and run
        mock_af_step.assert_called_once_with(str(config_file))
        mock_af_step.return_value.run.assert_called_once()

        mock_loft_step.assert_called_once_with(str(config_file))
        mock_loft_step.return_value.run.assert_called_once()

        mock_mesh_step.assert_called_once_with(str(config_file))
        mock_mesh_step.return_value.run.assert_called_once()

        mock_drape_step.assert_called_once_with(str(config_file))
        mock_drape_step.return_value.run.assert_called_once()
