"""Dump plugin - copies files from source to install directory."""

from minicraft.plugins.base import Plugin


class DumpPlugin(Plugin):
    """A plugin that copies source files directly into the install area.

    This is equivalent to craft-parts' dump plugin: no build step,
    just file transfer from source to the staging area.
    """

    def get_build_commands(self) -> list[str]:
        """Return commands to copy source files."""
        return [
            f'echo "Copying files from {self.source} to install directory"',
            f"xcopy /E /I /Y {self.source} install\\",
        ]

    def get_build_environment(self) -> dict[str, str]:
        """No special environment needed for dump."""
        return {}
