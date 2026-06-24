"""Project loading and validation."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from minicraft.errors import ProjectValidationError
from minicraft.models import Project


def load_project(filepath: Path) -> Project:
    """Load and validate a project from a YAML file.

    :param filepath: Path to the project YAML file.
    :returns: A validated Project instance.
    :raises ProjectValidationError: If the file is invalid.
    """
    if not filepath.exists():
        raise ProjectValidationError(f"Project file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    if not isinstance(raw_data, dict):
        raise ProjectValidationError("Project file must contain a YAML mapping.")

    try:
        return Project.model_validate(raw_data)
    except ValidationError as e:
        raise ProjectValidationError(f"Invalid project spec:\n{e}") from e


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m minicraft.project <path-to-yaml>")
        sys.exit(1)

    project = load_project(Path(sys.argv[1]))
    print(f"Loaded project: {project.name}")
    for part_name, spec in project.parts.items():
        print(f"  Part '{part_name}': plugin={spec.plugin}, source={spec.source}")
