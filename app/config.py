import os

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

# Import logger locally in validate to avoid circular imports if logger uses config later (though currently it doesn't)

load_dotenv()

class Config:
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Models (optimized for speed and intelligence)
    # Strategy: Use fastest models, fallback to Mistral for quality
    MODEL_PRIMARY = "mistral:mistral-small-latest"  # User requested default
    MODEL_SMART = "mistral:mistral-small-latest"  # High intelligence
    MODEL_FAST = "cerebras:llama3.1-8b"           # Ultra-low latency
    MODEL_RESEARCH = "mistral:mistral-small-latest"  # Fast research
    MODEL_FALLBACK_TIER2 = "openrouter:arcee-ai/trinity-mini:free"  # Fast fallback

    # Legacy model names (for compatibility)
    MODEL_SMALL = "cerebras:llama3.1-8b"
    MODEL_MEDIUM = "mistral:mistral-small-latest"
    MODEL_LARGE = "mistral:mistral-small-latest"
    MODEL_FALLBACK = "mistral:mistral-small-latest"
    MODEL_OPENROUTER_FALLBACK = "openrouter:arcee-ai/trinity-mini:free"

    # Resilience Settings (optimized for speed)
    RETRIES = 2  # Reduced for faster failures
    DELAY_BETWEEN_RETRIES = 1  # Faster retry
    EXPONENTIAL_BACKOFF = True

    # Performance Settings
    STREAMING = False  # Disabled due to rendering repetitions in CLI
    USE_TEAM = False  # Direct agent is faster than team coordination

    # UI & Accessibility Settings
    ACCESSIBILITY_MODE = False
    
    class UI:
        """UI Configuration"""
        REFRESH_RATE = 12
        SPINNER_STYLE = "dots"
        ANIMATION_SPEED = 0.05
        THEME = {
            "prompt": "#ansigreen bold",
            "input": "#ansiwhite",
            "toolbar": "#ansigray italic",
            "panel_border": "magenta",
            "title": "bold magenta",
        }

    def validate(self) -> None:
        if not self.MISTRAL_API_KEY:
            raise ConfigurationError("MISTRAL_API_KEY is not set in environment variables.")
        if not self.FIRECRAWL_API_KEY:
            # We just print/log a warning here, not raise an error, as it's optional but recommended
            print("Warning: FIRECRAWL_API_KEY is not set. Research capabilities may be limited.")
        if not self.OPENWEATHER_API_KEY:
             print("Warning: OPENWEATHER_API_KEY is not set. Weather capabilities will be disabled.")
        if not self.CEREBRAS_API_KEY:
             print("Warning: CEREBRAS_API_KEY is not set. Cerebras fallback disabled.")
        if not self.OPENROUTER_API_KEY:
             print("Warning: OPENROUTER_API_KEY is not set. OpenRouter fallback disabled.")

config = Config()
