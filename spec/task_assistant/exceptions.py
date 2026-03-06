"""Custom exceptions for the Task Management Assistant."""


class TaskNotFoundError(Exception):
    """Raised when a task ID cannot be found."""
    pass


class TaskStoreError(Exception):
    """Raised when task storage operations fail."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass
