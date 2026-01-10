class MigruError(Exception):
    """Base exception for the Migru application."""
    pass

class ConfigurationError(MigruError):
    """Raised when there is a configuration issue."""
    pass

class AgentExecutionError(MigruError):
    """Raised when an agent fails to execute a task."""
    pass

class DatabaseConnectionError(MigruError):
    """Raised when connection to the database fails."""
    pass
