"""Custom exceptions for minicraft."""


class MiniCraftError(Exception):
    """Base exception for all minicraft errors."""


class ProjectValidationError(MiniCraftError):
    """Raised when a project YAML file fails validation."""


class PluginNotFoundError(MiniCraftError):
    """Raised when a requested plugin does not exist."""


class LifecycleError(MiniCraftError):
    """Raised when the lifecycle encounters an unrecoverable error."""
