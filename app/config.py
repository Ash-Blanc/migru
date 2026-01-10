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
    
    # Models
    MODEL_SMALL = "mistral:mistral-small-latest"
    MODEL_MEDIUM = "mistral:mistral-medium-latest"
    MODEL_LARGE = "mistral:mistral-large-latest"
    MODEL_FALLBACK = "llama3.1-8b" # Cerebras fallback
    MODEL_OPENROUTER_FALLBACK = "google/gemini-2.0-flash-001" # OpenRouter fallback

    def validate(self):
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