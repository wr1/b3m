from pydantic import BaseModel, ValidationError, RootModel
from typing import Dict, List, Any, Optional
import yaml


class Geometry(BaseModel):
    planform: Dict[str, Any]  # Placeholder; can be expanded with specific fields


class AirfoilItem(BaseModel):
    path: str
    name: str
    thickness: float


class Airfoils(RootModel[List[AirfoilItem]]):
    pass


class Mesh(BaseModel):
    z: List[Dict[str, Any]]
    chordwise: Dict[str, Any]


class Structure(BaseModel):
    webs: List[Dict[str, Any]]


class B3mConfig(BaseModel):
    """Top-level config for b3m YAML validation."""
    workdir: str
    geometry: Geometry
    airfoils: Airfoils
    mesh: Mesh
    structure: Structure
    # Add other sections as needed


def validate_config(config_path: str) -> B3mConfig:
    """Load and validate the YAML config."""
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    try:
        config = B3mConfig(**data)
        return config
    except ValidationError as e:
        raise ValueError(f"YAML validation failed: {e}")
