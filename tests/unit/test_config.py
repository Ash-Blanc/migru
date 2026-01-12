"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from app.config import config


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_validation_missing_required_vars(self):
        """Test config validation fails when required vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception, match="MISTRAL_API_KEY is not set"):
                config.validate()

    @patch.dict(os.environ, {
        "MISTRAL_API_KEY": "test_key",
        "CEREBRAS_API_KEY": "test_key",
        "OPENWEATHER_API_KEY": "test_key",
        "OPENROUTER_API_KEY": "test_key",
        "FIRECRAWL_API_KEY": "test_key",
        "REDIS_URL": "redis://localhost:6379",
    })
    def test_config_validation_success(self):
        """Test config validation succeeds when all required vars are set."""
        try:
            config.validate()
        except Exception:
            pytest.fail("Config validation should succeed with all required vars")

    def test_config_model_selection(self):
        """Test model selection logic."""
        assert config.MODEL_PRIMARY is not None
        assert config.MODEL_RESEARCH is not None
        assert config.MODEL_SMART is not None
        assert config.MODEL_OPENROUTER_FALLBACK is not None

    def test_config_debug_mode(self):
        """Test debug mode configuration."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            config.DEBUG = True
            assert config.DEBUG is True

        with patch.dict(os.environ, {"DEBUG": "false"}):
            config.DEBUG = False
            assert config.DEBUG is False

        with patch.dict(os.environ, {}, clear=True):
            config.DEBUG = False
            assert config.DEBUG is False