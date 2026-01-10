from agno.models.mistral import Mistral
from agno.models.cerebras import Cerebras
from app.config import config
import os

class ModelFactory:
    @staticmethod
    def get_model(model_id: str, fallback_id: str = config.MODEL_FALLBACK):
        """
        Returns a primary model instance. 
        Note: True runtime fallback requires wrapping the Agent execution loop.
        This factory prepares the models for use.
        """
        # Primary: Mistral
        # In a robust system, we might check for API availability here, 
        # but standard practice is to configure the agent with the primary.
        return Mistral(id=model_id)

    @staticmethod
    def get_fallback_model():
        """Returns the Cerebras fallback model instance."""
        if config.CEREBRAS_API_KEY:
            return Cerebras(id=config.MODEL_FALLBACK)
        return None

model_factory = ModelFactory()
