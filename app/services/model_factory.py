from agno.models.mistral import Mistral
from agno.models.cerebras import Cerebras
from agno.models.openrouter import OpenRouter
from app.config import config
import os

class ModelFactory:
    @staticmethod
    def get_model(model_id: str):
        """Returns the primary Mistral model."""
        return Mistral(id=model_id)

    @staticmethod
    def get_cerebras_fallback():
        """Returns the Cerebras fallback model instance."""
        if config.CEREBRAS_API_KEY:
            return Cerebras(id=config.MODEL_FALLBACK)
        return None

    @staticmethod
    def get_openrouter_fallback():
        """Returns the OpenRouter fallback model instance."""
        if config.OPENROUTER_API_KEY:
            return OpenRouter(id=config.MODEL_OPENROUTER_FALLBACK)
        return None

model_factory = ModelFactory()