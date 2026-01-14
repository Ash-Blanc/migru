import logging
import sys
import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with structured logging configuration."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Default to WARNING to suppress INFO/DEBUG noise unless requested
        log_level = logging.WARNING

        logger.setLevel(log_level)

        # Create console handler with structured format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create structured formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger


def log_function_calls(logger: logging.Logger) -> Callable:
    """Decorator to log function entry/exit and exceptions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug(f"Entering {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__} successfully")
                return result
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                logger.debug(f"Stack trace: {traceback.format_exc()}")
                raise
        return wrapper
    return decorator


def suppress_verbose_logging() -> None:
    """Suppress verbose logging from third-party libraries and Agno tools."""
    
    # Aggressively silence agno loggers and AI providers
    loggers_to_silence = [
        "agno",
        "agno.tools",
        "agno.agent", 
        "agno.team",
        "agno.memory",
        "agno.culture",
        "agno.db",
        "agno.storage",
        "agno.utils",
        "agno.models",
        "agno.models.base",
        "agno.agent.agent",
        "redis",
        "httpx",
        "httpcore", 
        "ddgs",
        "firecrawl",
        "requests",
        "urllib3",
        "mistralai",
        "cerebras",
        "cerebras_cloud_sdk",
        "openai",
        "pathway",
        "youtube_transcript_api",
    ]

    for logger_name in loggers_to_silence:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        logger.handlers = [] # Remove specific handlers to force bubble-up
        logger.propagate = False # STOP propagation to root (which might print WARNINGs)
        logger.addHandler(logging.NullHandler()) # Swallow everything

    # Brute force: check all existing loggers
    for name in logging.root.manager.loggerDict:
        if any(name.startswith(prefix) for prefix in ["agno", "redis", "mistral", "cerebras", "openai"]):
            logger = logging.getLogger(name)
            logger.setLevel(logging.CRITICAL)
            logger.handlers = []
            logger.propagate = False
            logger.addHandler(logging.NullHandler())

    # Suppress all function execution warnings and retry warnings
    logging.getLogger("agno.tools.function").setLevel(logging.CRITICAL)
    logging.getLogger("agno.agent.run").setLevel(logging.CRITICAL)
    logging.getLogger("agno.models.retry").setLevel(logging.CRITICAL)

    # Keep only warnings and errors visible for user-facing logs (unless overridden by main)
    # But since we want to be very quiet, we let main handle the root logger level.
    # logging.getLogger().setLevel(logging.WARNING) 


class PerformanceLogger:
    """Context manager for performance logging."""

    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = self.logger.perf_counter()
        self.logger.debug(f"Starting {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = self.logger.perf_counter()
        duration = end_time - self.start_time
        self.logger.info(f"{self.operation_name} completed in {duration:.2f} seconds")

        if exc_type:
            self.logger.error(f"{self.operation_name} failed with {exc_type.__name__}: {exc_val}")


def log_memory_usage(logger: logging.Logger) -> None:
    """Log current memory usage if psutil is available."""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger.debug(f"Memory usage: {memory_mb:.2f} MB")
    except ImportError:
        logger.debug("psutil not available, skipping memory logging")
