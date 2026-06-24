"""Python plugin - creates a venv and installs dependencies."""

from minicraft.plugins.base import Plugin


class PythonPlugin(Plugin):
    """A plugin for building Python parts.

    Creates a virtual environment and installs packages,
    mirroring the craft-parts Python plugin pattern.
    """

    def get_pull_commands(self) -> list[str]:
        """Pull commands to fetch Python dependencies.
        For now, it just echoes a message cuz the real pull mechanism is a TODO
        (and I don't need it for the 'mini' implementation)"""
        return [
            'echo "Fetching Python dependencies"',
        ]

    def get_build_commands(self) -> list[str]:
        """Return commands to create venv and install packages."""
        return [
            f'echo "Creating virtual environment for {self.part_name}"',
            "python -m venv install\\.venv",
            'echo "Installing dependencies"',
            "install\\.venv\\Scripts\\pip.exe install -r requirements.txt",
        ]

    def get_build_environment(self) -> dict[str, str]:
        """Return Python-specific build environment."""
        return {
            "PARTS_PYTHON_INTERPRETER": "python3",
            "PARTS_PYTHON_VENV_ARGS": "",
        }
