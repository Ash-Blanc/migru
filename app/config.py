"""
Enhanced Configuration with Local LLM and Privacy Settings
Updated configuration to support local models and privacy modes.
"""

import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError
from app.ui.theme import Themes, UITheme

load_dotenv()


class Config:
    """Enhanced configuration with local LLM and privacy support."""

    # Existing API Keys
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Privacy and Local Model Configuration
    LOCAL_LLM_ENABLED = os.getenv("LOCAL_LLM_ENABLED", "true").lower() == "true"
    LOCAL_LLM_HOST = os.getenv("LOCAL_LLM_HOST", "http://localhost:11434")
    LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "gemma2:9b")
    LOCAL_LLM_API_KEY = os.getenv("LOCAL_LLM_API_KEY", "not-needed")

    # Med-Gemma / HAI-DEF Configuration
    MED_GEMMA_ENABLED = os.getenv("MED_GEMMA_ENABLED", "true").lower() == "true"
    MED_GEMMA_MODEL = os.getenv("MED_GEMMA_MODEL", "gemma2:9b")  # Use Gemma 2 as base for MedGemma

    # Privacy Mode Configuration
    PRIVACY_MODE = os.getenv("PRIVACY_MODE", "hybrid")  # "local", "hybrid", "flexible"
    ENABLE_SEARCH_IN_LOCAL_MODE = (
        os.getenv("ENABLE_SEARCH_IN_LOCAL_MODE", "false").lower() == "true"
    )

    # Local Server Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    LLAMACPP_HOST = os.getenv("LLAMACPP_HOST", "http://localhost:8080")
    LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://localhost:1234")

    # Model Server Type
    LOCAL_SERVER_TYPE = os.getenv(
        "LOCAL_SERVER_TYPE", "llamacpp"
    )  # "ollama", "llamacpp", "lmstudio"

    # Cloud Models (Fallback)
    MODEL_MISTRAL_CREATIVE = "mistral:labs-mistral-small-creative"
    MODEL_MISTRAL_SMALL = "mistral:mistral-small-latest"
    MODEL_MISTRAL_MEDIUM = "mistral:mistral-medium-latest"
    MODEL_MISTRAL_LARGE = "mistral:mistral-large-latest"

    MODEL_PRIMARY = MODEL_MISTRAL_CREATIVE
    MODEL_SMART = MODEL_MISTRAL_CREATIVE
    MODEL_FAST = "cerebras:llama3.1-8b"
    MODEL_RESEARCH = "mistral:mistral-small-latest"
    MODEL_FALLBACK_TIER2 = "openrouter:arcee-ai/trinity-mini:free"

    # Legacy Model Names (Compatibility)
    MODEL_SMALL = "cerebras:llama3.1-8b"
    MODEL_MEDIUM = "mistral:mistral-small-latest"
    MODEL_LARGE = "mistral:mistral-small-latest"
    MODEL_FALLBACK = "mistral:mistral-small-latest"
    MODEL_OPENROUTER_FALLBACK = "openrouter:arcee-ai/trinity-mini:free"

    # Resilience Settings
    RETRIES = 2
    DELAY_BETWEEN_RETRIES = 1
    EXPONENTIAL_BACKOFF = True

    # Performance Settings
    STREAMING = True
    USE_TEAM = False

    # UI & Accessibility Settings
    ACCESSIBILITY_MODE = False

    # DuckDuckGo Search (always available as fallback)
    DUCKDUCKGO_ENABLED = True

    @property
    def current_model_config(self) -> Dict[str, Any]:
        """Get current model configuration based on settings."""
        if self.LOCAL_LLM_ENABLED:
            return {
                "type": "local",
                "model": self.LOCAL_LLM_MODEL,
                "host": self.LOCAL_LLM_HOST,
                "server_type": self.LOCAL_SERVER_TYPE,
                "privacy_mode": self.PRIVACY_MODE,
            }
        else:
            return {
                "type": "cloud",
                "model": self.MODEL_PRIMARY,
                "privacy_mode": self.PRIVACY_MODE,
            }

    @property
    def search_enabled(self) -> bool:
        """Check if search is enabled based on privacy settings."""
        if self.PRIVACY_MODE == "local":
            return False
        elif self.PRIVACY_MODE == "hybrid":
            return self.ENABLE_SEARCH_IN_LOCAL_MODE
        elif self.PRIVACY_MODE == "flexible":
            return True
        return False

    def get_local_host(self) -> str:
        """Get the appropriate local host based on server type."""
        hosts = {
            "ollama": self.OLLAMA_HOST,
            "llamacpp": self.LLAMACPP_HOST,
            "lmstudio": self.LM_STUDIO_HOST,
        }
        return hosts.get(self.LOCAL_SERVER_TYPE, self.LLAMACPP_HOST)

    def update_privacy_mode(self, mode: str) -> bool:
        """
        Update privacy mode at runtime.

        Args:
            mode: New privacy mode

        Returns:
            True if update successful
        """
        valid_modes = ["local", "hybrid", "flexible"]
        if mode in valid_modes:
            self.PRIVACY_MODE = mode
            os.environ["PRIVACY_MODE"] = mode
            return True
        return False

    def update_local_model(self, model: str) -> bool:
        """
        Update local model at runtime.

        Args:
            model: New model name

        Returns:
            True if update successful
        """
        self.LOCAL_LLM_MODEL = model
        os.environ["LOCAL_LLM_MODEL"] = model
        return True

    class UIConfig:
        """UI Configuration"""

        def __init__(self):
            self.ACTIVE_THEME: UITheme = Themes.OCEAN
            self.AUTO_THEME_SWITCHING = True
            self.THEME_BASED_ON = "time"

        @property
        def REFRESH_RATE(self):
            return self.ACTIVE_THEME.refresh_rate

        @property
        def SPINNER_STYLE(self):
            return self.ACTIVE_THEME.spinner_style

        def switch_theme(self, theme_name: str) -> bool:
            """Switch to a new theme by name."""
            theme_map = {
                "ocean": Themes.OCEAN,
                "sunrise": Themes.SUNRISE,
                "forest": Themes.FOREST,
                "lavender": Themes.LAVENDER,
                "daylight": Themes.DAYLIGHT,
                "high_contrast": Themes.HIGH_CONTRAST,
            }
            if theme_name.lower() in theme_map:
                self.ACTIVE_THEME = theme_map[theme_name.lower()]
                return True
            return False

        def auto_switch_theme(self, user_mood: str = None):
            """Automatically switch theme based on time or mood."""
            if self.THEME_BASED_ON == "time":
                self.ACTIVE_THEME = Themes.get_time_based_theme()
            elif self.THEME_BASED_ON == "mood" and user_mood:
                self.ACTIVE_THEME = Themes.get_theme_by_mood(user_mood)
            elif self.THEME_BASED_ON == "random":
                self.ACTIVE_THEME = Themes.get_random_wellness_theme()

    UI = UIConfig()

    def validate(self) -> None:
        """Validate configuration with enhanced checks."""
        warnings = []

        # Check local LLM configuration
        if self.LOCAL_LLM_ENABLED:
            if not self.LOCAL_LLM_MODEL:
                raise ConfigurationError(
                    "LOCAL_LLM_MODEL must be set when LOCAL_LLM_ENABLED is true"
                )

            if not self.get_local_host():
                raise ConfigurationError("No valid local host configured")

        # Check privacy mode
        if self.PRIVACY_MODE not in ["local", "hybrid", "flexible"]:
            raise ConfigurationError(f"Invalid privacy mode: {self.PRIVACY_MODE}")

        # Check cloud API keys (for fallback)
        if not self.MISTRAL_API_KEY:
            warnings.append("MISTRAL_API_KEY not set - cloud fallback unavailable")

        if not self.FIRECRAWL_API_KEY and self.search_enabled:
            warnings.append(
                "FIRECRAWL_API_KEY not set - web search capabilities limited"
            )

        if not self.OPENWEATHER_API_KEY and self.search_enabled:
            warnings.append("OPENWEATHER_API_KEY not set - weather features disabled")

        if not self.CEREBRAS_API_KEY:
            warnings.append("CEREBRAS_API_KEY not set - Cerebras fallback disabled")

        if not self.OPENROUTER_API_KEY:
            warnings.append("OPENROUTER_API_KEY not set - OpenRouter fallback disabled")

        # Print warnings
        for warning in warnings:
            print(f"Warning: {warning}")

        # Check Redis
        if not self.REDIS_URL:
            raise ConfigurationError("REDIS_URL is required")

    def get_model_recommendations(self) -> Dict[str, Any]:
        """Get model recommendations based on privacy mode and use case."""

        recommendations = {
            "local_models": {
                "gemma2:9b": {
                    "description": "Google's Gemma 2 - High performance & efficient (Med-Gemma base)",
                    "best_for": ["medical_reasoning", "general_conversation", "reasoning"],
                    "recommended": True,
                    "privacy_mode": "all",
                },
                "gemma2:27b": {
                    "description": "High intelligence for complex medical analysis",
                    "best_for": ["complex_analysis", "research"],
                    "recommended": False,  # Requires more RAM
                    "privacy_mode": "all",
                },
                "function-gemma:7b": {
                    "description": "Tool calling and routing optimized",
                    "best_for": ["agent_routing", "tool_execution", "research"],
                    "recommended": True,
                    "privacy_mode": "all",
                },
                "qwen2.5:3b": {
                    "description": "Fast empathetic conversations",
                    "best_for": ["emotional_support", "companion"],
                    "recommended": True,
                    "privacy_mode": "all",
                },
                "phi3.5:3.8b": {
                    "description": "Balanced reasoning and advice",
                    "best_for": ["practical_advice", "general_conversation"],
                    "recommended": True,
                    "privacy_mode": "all",
                },
                "gemma2:2b": {
                    "description": "Lightweight backup option",
                    "best_for": ["fallback", "simple_queries"],
                    "recommended": False,
                    "privacy_mode": "all",
                },
            },
            "cloud_fallbacks": {
                "mistral:labs-mistral-small-creative": {
                    "description": "High quality creative responses",
                    "best_for": ["emotional_support", "creative_tasks"],
                },
                "cerebras:llama3.1-8b": {
                    "description": "Ultra-fast responses",
                    "best_for": ["quick_responses", "simple_queries"],
                },
            },
            "privacy_recommendations": {
                "local": {
                    "description": "Complete privacy, no external APIs (Ideal for Med-Gemma)",
                    "recommended_models": ["gemma2:9b"],
                    "search_available": False,
                },
                "hybrid": {
                    "description": "Local AI + optional search",
                    "recommended_models": ["gemma2:9b"],
                    "search_available": True,
                },
                "flexible": {
                    "description": "User choice per session",
                    "recommended_models": ["function-gemma:7b"],
                    "search_available": True,
                },
            },
        }

        return recommendations


config = Config()