from unittest.mock import patch
from b3m.integration import build_blade


def test_build_blade(tmp_path):
    """Test the build_blade function with mocked dependencies."""
    # Create a temporary config file
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "workdir: test_workdir\nairfoils: []\ngeometry: {planform: {z: [[0.0, 0.0], [1.0, 1.0]], chord: [[0.0, 1.0], [1.0, 0.5]], thickness: [[0.0, 0.1], [1.0, 0.05]], twist: [[0.0, 0.0], [1.0, 10.0]], dx: [[0.0, 0.0], [1.0, 0.0]], dy: [[0.0, 0.0], [1.0, 0.0]], npchord: 200, npspan: 100}}\nmesh: {z: [{type: linspace, values: [0.0, 1.0], num: 10}], chordwise: {default: {n_elem: 100}, panels: []}}\nstructure: {webs: []}\nlaminates: {}\nmatdb: {}\nplies: {}"
    )
    # Create the workdir to simulate existing directory for force overwrite
    (tmp_path / "test_workdir").mkdir()

    with (
        patch("b3_geo.api.af_step.AFStep") as mock_af_step,
        patch("b3_geo.api.loft_step.LoftStep") as mock_loft_step,
        patch("b3_msh.step.blade_mesh_step.B3MshStep") as mock_mesh_step,
        patch("b3_drp.DrapeStep") as mock_drape_step,
        patch("b3_2d.state.B32dStep") as mock_b3_2d_step,
        patch("b3_2d.state.B32dAnbaStep") as mock_b3_2d_anba_step,
        patch("b3m.integration.shutil.rmtree") as mock_rmtree,
    ):
        # Call build_blade with force=True
        build_blade(str(config_file), force=True)

        # Assert that the steps were called
        mock_af_step.assert_called_once()
        mock_af_step.return_value.run.assert_called_once()
        mock_loft_step.assert_called_once()
        mock_loft_step.return_value.run.assert_called_once()
        mock_mesh_step.assert_called_once()
        mock_mesh_step.return_value.run.assert_called_once()
        mock_drape_step.assert_called_once()
        mock_drape_step.return_value.run.assert_called_once()
        mock_b3_2d_step.assert_called_once()
        mock_b3_2d_step.return_value.run.assert_called_once()
        mock_b3_2d_anba_step.assert_called_once()
        mock_b3_2d_anba_step.return_value.run.assert_called_once()
        mock_rmtree.assert_called_once_with(tmp_path / "test_workdir")
