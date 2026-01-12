"""Unit tests for logger module."""

import logging
import pytest
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

from app.logger import (
    get_logger,
    log_function_calls,
    suppress_verbose_logging,
    PerformanceLogger,
    log_memory_usage
)


class TestLogger:
    """Test logger functionality."""

    def test_get_logger_returns_instance(self):
        """Test get_logger returns a logger instance."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test"

    def test_get_logger_adds_handler_only_once(self):
        """Test get_logger doesn't add duplicate handlers."""
        logger = get_logger("test")
        initial_handler_count = len(logger.handlers)

        # Get logger again with same name
        logger2 = get_logger("test")
        assert len(logger2.handlers) == initial_handler_count

    def test_get_logger_configures_format(self):
        """Test get_logger configures proper formatting."""
        logger = get_logger("test")
        handler = logger.handlers[0]
        formatter = handler.formatter

        assert formatter is not None
        assert "%(asctime)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(message)s" in formatter._fmt


class TestLogFunctionCalls:
    """Test function call logging decorator."""

    def test_log_function_calls_decorator(self):
        """Test the log_function_calls decorator."""
        mock_logger = Mock()

        @log_function_calls(mock_logger)
        def test_function():
            return "result"

        result = test_function()

        assert result == "result"
        mock_logger.debug.assert_any_call("Entering test_function")
        mock_logger.debug.assert_any_call("Exiting test_function successfully")

    def test_log_function_calls_decorator_with_exception(self):
        """Test the log_function_calls decorator with exceptions."""
        mock_logger = Mock()

        @log_function_calls(mock_logger)
        def test_function():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            test_function()

        mock_logger.debug.assert_any_call("Entering test_function")
        mock_logger.error.assert_called_once()


class TestSuppressVerboseLogging:
    """Test verbose logging suppression."""

    @patch('logging.getLogger')
    def test_suppress_verbose_logging(self, mock_get_logger):
        """Test suppress_verbose_logging sets correct log levels."""
        mock_logger_instance = Mock()
        mock_get_logger.return_value = mock_logger_instance

        suppress_verbose_logging()

        # Check that get_logger was called for all expected modules
        expected_calls = [
            "agno.tools",
            "agno.agent",
            "agno.team",
            "agno.memory",
            "agno.culture",
            "httpx",
            "httpcore",
            "ddgs",
            "firecrawl",
            "requests",
            "urllib3",
            "agno.tools.function"
        ]

        for call in expected_calls:
            mock_get_logger.assert_any_call(call)

        # Check that setLevel was called with appropriate levels
        assert mock_logger_instance.setLevel.called

    @patch('logging.getLogger')
    def test_suppress_verbose_logging_sets_root_level(self, mock_get_logger):
        """Test suppress_verbose_logging sets root logger level."""
        mock_root_logger = Mock()
        mock_get_logger.return_value = mock_root_logger

        suppress_verbose_logging()

        # Root logger should be set to WARNING
        mock_root_logger.setLevel.assert_called_once_with(logging.WARNING)


class TestPerformanceLogger:
    """Test performance logging context manager."""

    @patch('app.logger.PerformanceLogger')
    def test_performance_logger_context_manager(self, mock_performance_logger):
        """Test PerformanceLogger as context manager."""
        mock_logger = Mock()
        mock_performance_logger.return_value = Mock()

        with PerformanceLogger(mock_logger, "test_operation"):
            pass

        mock_logger.debug.assert_called_with("Starting test_operation")
        mock_logger.info.assert_called_with("test_operation completed in 0.00 seconds")

    @patch('app.logger.PerformanceLogger')
    def test_performance_logger_with_exception(self, mock_performance_logger):
        """Test PerformanceLogger handles exceptions."""
        mock_logger = Mock()
        mock_performance_logger.return_value = Mock()

        with pytest.raises(ValueError):
            with PerformanceLogger(mock_logger, "test_operation"):
                raise ValueError("test error")

        mock_logger.error.assert_called_with("test_operation failed with ValueError: test error")


class TestLogMemoryUsage:
    """Test memory usage logging."""

    @patch('psutil.Process')
    def test_log_memory_usage_with_psutil(self, mock_process):
        """Test log_memory_usage with psutil available."""
        mock_logger = Mock()
        mock_process_instance = Mock()
        mock_process.return_value = mock_process_instance
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 50  # 50 MB

        log_memory_usage(mock_logger)

        mock_logger.debug.assert_called_with("Memory usage: 50.00 MB")

    @patch('builtins.__import__')
    def test_log_memory_usage_without_psutil(self, mock_import):
        """Test log_memory_usage without psutil available."""
        mock_import.side_effect = ImportError("No module named 'psutil'")

        mock_logger = Mock()
        log_memory_usage(mock_logger)

        mock_logger.debug.assert_called_with("psutil not available, skipping memory logging")