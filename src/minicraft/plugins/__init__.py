"""Plugin registry for minicraft."""

from minicraft.errors import PluginNotFoundError
from minicraft.models import PartSpec
from minicraft.plugins.base import Plugin
from minicraft.plugins.dump_plugin import DumpPlugin
from minicraft.plugins.python_plugin import PythonPlugin

_PLUGIN_REGISTRY: dict[str, type[Plugin]] = {
    "dump": DumpPlugin,
    "python": PythonPlugin,
}


def get_plugin(name: str, part_name: str, part_spec: PartSpec) -> Plugin:
    """Instantiate a plugin by name.

    :param name: The plugin identifier.
    :param part_name: The name of the part using this plugin.
    :param part_spec: The part specification.
    :returns: An instantiated Plugin.
    :raises PluginNotFoundError: If the plugin name is not registered.
    """
    plugin_class = _PLUGIN_REGISTRY.get(name)
    if plugin_class is None:
        available = ", ".join(sorted(_PLUGIN_REGISTRY.keys()))
        raise PluginNotFoundError(f"Plugin '{name}' not found. Available plugins: {available}")
    return plugin_class(part_name=part_name, part_spec=part_spec)
