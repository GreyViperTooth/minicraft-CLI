"""Abstract base class for minicraft plugins."""

import abc

from minicraft.models import PartSpec


class Plugin(abc.ABC):
    """The base class for plugins.

    Subclasses must implement the abstract methods to define how a part
    is built within the lifecycle.
    """

    def __init__(self, *, part_name: str, part_spec: PartSpec) -> None:
        self._part_name = part_name
        self._part_spec = part_spec

    @property
    def part_name(self) -> str:
        """The name of the part this plugin is building."""
        return self._part_name

    @property
    def source(self) -> str:
        """The source directory for this part."""
        return self._part_spec.source

    def get_pull_commands(self) -> list[str]:
        """Return commands to retrieve dependencies during the pull step."""
        return []

    @abc.abstractmethod
    def get_build_commands(self) -> list[str]:
        """Return commands to execute during the build step."""

    @abc.abstractmethod
    def get_build_environment(self) -> dict[str, str]:
        """Return environment variables for the build step."""
