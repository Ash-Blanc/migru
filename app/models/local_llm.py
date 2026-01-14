"""
Local LLM Model Integration for Privacy-First Migru
Supports llama.cpp, Ollama, and other OpenAI-compatible local servers.
"""

from typing import Optional, Dict, Any, List
import httpx
import json
import logging

from agno.models.openai_like import OpenAILike
from agno.agent import Agent
from agno.tools import Toolkit

from app.config import config
from app.logger import get_logger

logger = get_logger("migru.local_llm")


class LocalLlamaModel(OpenAILike):
    """
    Local LLM integration with llama.cpp/Ollama support.
    Optimized for privacy-first conversations and tool calling.
    """

    def __init__(
        self,
        model: str = "function-gemma:7b",  # Tool calling optimized
        host: str = "http://localhost:8080",
        api_key: str = "not-needed",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        repeat_penalty: float = 1.1,
        **kwargs,
    ):
        """
        Initialize local LLM model.

        Args:
            model: Model name (function-gemma:7b recommended for tool calling)
            host: Local server URL
            api_key: API key (not needed for local)
            temperature: Response randomness
            max_tokens: Maximum response length
            top_p: Nucleus sampling parameter
            repeat_penalty: Penalty for repetition
        """
        super().__init__(
            id=model,
            api_key=api_key,
            base_url=f"{host}/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        self.top_p = top_p
        self.repeat_penalty = repeat_penalty
        self.host = host

        # Model capabilities
        self.supports_tools = (
            "function-gemma" in model.lower() or "tool" in model.lower()
        )
        self.is_local = True

        logger.info(f"Initialized LocalLlamaModel: {model} at {host}")

    def _optimize_for_conversation_type(self, message_type: str) -> None:
        """
        Dynamically adjust parameters based on conversation type.

        Args:
            message_type: Type of conversation (emotional_support, research, etc.)
        """
        if message_type == "emotional_support":
            # Higher creativity for empathy, shorter responses
            self.temperature = 0.8
            self.max_tokens = 512
        elif message_type == "research":
            # Lower temperature for accuracy, longer responses
            self.temperature = 0.3
            self.max_tokens = 1536
        elif message_type == "tool_calling":
            # Very low temperature for reliable tool execution
            self.temperature = 0.1
            self.max_tokens = 1024
        else:
            # Default balanced settings
            self.temperature = 0.7
            self.max_tokens = 2048

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the local model."""
        return {
            "model": self.id,
            "host": self.host,
            "supports_tools": self.supports_tools,
            "is_local": self.is_local,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "repeat_penalty": self.repeat_penalty,
        }

    async def test_connection(self) -> bool:
        """Test connection to local LLM server."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.host}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Local LLM connection test failed: {e}")
            return False


class LocalModelManager:
    """
    Manager for local LLM models with switching and optimization.
    """

    def __init__(self):
        self.available_models = {}
        self.current_model = None
        self.model_configs = {
            "function-gemma:7b": {
                "description": "Tool calling optimized model",
                "best_for": ["routing", "tool_execution", "research"],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            "qwen2.5:3b": {
                "description": "Fast empathetic model",
                "best_for": ["emotional_support", "companion"],
                "temperature": 0.8,
                "max_tokens": 512,
            },
            "phi3.5:3.8b": {
                "description": "Balanced reasoning model",
                "best_for": ["advisor", "general_conversation"],
                "temperature": 0.5,
                "max_tokens": 1024,
            },
            "gemma2:2b": {
                "description": "Lightweight backup model",
                "best_for": ["fallback", "simple_queries"],
                "temperature": 0.6,
                "max_tokens": 512,
            },
        }

    async def scan_available_models(self) -> List[str]:
        """Scan for available local models."""
        models = []

        # Try Ollama API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    logger.info(f"Found {len(models)} models via Ollama")
        except Exception as e:
            logger.debug(f"Ollama scan failed: {e}")

        # Try llama.cpp server
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8080/health")
                if response.status_code == 200:
                    # Assume function-gemma is available for llama.cpp
                    models.append("function-gemma:7b")
                    logger.info("Found function-gemma via llama.cpp")
        except Exception as e:
            logger.debug(f"llama.cpp scan failed: {e}")

        self.available_models = {
            model: self.model_configs.get(model, {}) for model in models
        }
        return models

    def get_optimal_model(self, task_type: str) -> str:
        """
        Get the optimal model for a specific task type.

        Args:
            task_type: Type of task (routing, emotional_support, research, etc.)

        Returns:
            Model name best suited for the task
        """
        for model_name, config in self.model_configs.items():
            if task_type in config.get("best_for", []):
                if model_name in self.available_models:
                    return model_name

        # Fallback to first available model
        if self.available_models:
            return list(self.available_models.keys())[0]

        # Ultimate fallback
        return config.LOCAL_LLM_MODEL

    def create_model_for_task(self, task_type: str) -> LocalLlamaModel:
        """
        Create a local model optimized for a specific task.

        Args:
            task_type: Type of task

        Returns:
            Optimized LocalLlamaModel instance
        """
        model_name = self.get_optimal_model(task_type)
        config = self.model_configs.get(model_name, {})

        return LocalLlamaModel(
            model=model_name,
            host=config.LOCAL_LLM_HOST,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2048),
            top_p=0.9,
            repeat_penalty=1.1,
        )


# Global model manager instance
model_manager = LocalModelManager()
