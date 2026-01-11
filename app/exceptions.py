class MigruError(Exception):
    """Base exception for the Migru application."""
    pass

class ConfigurationError(MigruError):
    """Raised when there is a configuration issue."""
    pass
