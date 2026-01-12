class MigruError(Exception):
    """Base exception for the Migru application."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join([f"{k}={v}" for k, v in self.details.items()])
            return f"{self.message} (details: {details_str})"
        return self.message


class ConfigurationError(MigruError):
    """Raised when there is a configuration issue."""
    pass


class DatabaseError(MigruError):
    """Raised when there is a database operation failure."""
    pass


class AgentError(MigruError):
    """Raised when there is an agent operation failure."""
    pass


class MemoryError(MigruError):
    """Raised when there is a memory operation failure."""
    pass


class ValidationError(MigruError):
    """Raised when input validation fails."""
    pass


class NetworkError(MigruError):
    """Raised when there is a network or API failure."""
    pass
