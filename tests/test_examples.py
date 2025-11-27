import subprocess
import sys
from pathlib import Path


def test_validate_config_example():
    """Test the validate_config example script."""
    script_path = Path(__file__).parent.parent / "examples" / "validate_config.py"
    config_path = Path(__file__).parent.parent / "examples" / "sample_config.yaml"
    
    result = subprocess.run([sys.executable, str(script_path), str(config_path)], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert "Config validation successful" in result.stdout
