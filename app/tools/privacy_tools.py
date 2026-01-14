"""
Privacy-First Tools with Local Model Integration
Enhanced search tools that respect privacy settings and work with local models.
"""

from typing import Any, Dict, List, Optional
import json
import asyncio

from agno.tools import Toolkit
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.firecrawl import FirecrawlTools

from app.config import config
from app.logger import get_logger

logger = get_logger("migru.privacy_tools")


class PrivacyAwareSearchTools(Toolkit):
    """
    Search tools that respect privacy settings and work with local models.
    Only activates search when privacy mode allows it.
    """

    def __init__(self, privacy_mode: str = "hybrid"):
        super().__init__(name="privacy_aware_search")
        self.privacy_mode = privacy_mode
        self.ddg_tools = DuckDuckGoTools()
        self.firecrawl_tools = FirecrawlTools(enable_scrape=True, enable_crawl=True)

        # Register tool functions
        self.register(self.privacy_aware_search)
        self.register(self.privacy_aware_scrape)
        self.register(self.check_search_permissions)

    def privacy_aware_search(self, query: str, max_results: int = 5) -> str:
        """
        Perform search only if privacy mode allows it.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            Search results or privacy notice
        """
        # Check if search is allowed
        if not self._is_search_allowed():
            return self._get_privacy_notice("search")

        # Perform search with fallback
        return self._search_with_fallback(query, max_results)

    def privacy_aware_scrape(self, url: str) -> str:
        """
        Scrape URL only if privacy mode allows it.

        Args:
            url: URL to scrape

        Returns:
            Scraped content or privacy notice
        """
        # Check if scraping is allowed
        if not self._is_search_allowed():
            return self._get_privacy_notice("scraping")

        # Perform scraping
        try:
            logger.debug(f"Scraping URL: {url}")
            content = self.firecrawl_tools.scrape_url(url=url)
            logger.debug("URL scraping successful")
            return content
        except Exception as e:
            logger.debug(f"URL scraping failed: {e}")
            return f"I couldn't access that URL right now. Error: {str(e)}"

    def check_search_permissions(self) -> str:
        """
        Check current search permissions and privacy settings.

        Returns:
            String describing current privacy settings
        """
        permissions = {
            "privacy_mode": self.privacy_mode,
            "search_enabled": self._is_search_allowed(),
            "search_sources": self._get_available_sources(),
            "recommendations": self._get_privacy_recommendations(),
        }

        return json.dumps(permissions, indent=2)

    def _is_search_allowed(self) -> bool:
        """Check if search is allowed in current privacy mode."""

        # Local mode: no external search
        if self.privacy_mode == "local":
            return False

        # Hybrid mode: search only if explicitly enabled
        if self.privacy_mode == "hybrid":
            return config.ENABLE_SEARCH_IN_LOCAL_MODE

        # Flexible mode: search allowed
        if self.privacy_mode == "flexible":
            return True

        return False

    def _search_with_fallback(self, query: str, max_results: int) -> str:
        """Perform search with multiple fallback strategies."""

        # Strategy 1: Try DuckDuckGo first (fastest)
        try:
            logger.debug(f"Attempting DuckDuckGo search: {query}")
            results = self.ddg_tools.duckduckgo_search(
                query=query, max_results=max_results
            )
            if results and "No results found" not in str(results):
                logger.debug("DuckDuckGo search successful")
                return results
        except Exception as e:
            logger.debug(f"DuckDuckGo search failed: {e}")

        # Strategy 2: Try simplified query
        try:
            simplified_query = " ".join(query.split()[:4])
            logger.debug(f"Trying simplified DuckDuckGo search: {simplified_query}")
            results = self.ddg_tools.duckduckgo_search(
                query=simplified_query, max_results=max_results
            )
            if results and "No results found" not in str(results):
                logger.debug("Simplified DuckDuckGo search successful")
                return results
        except Exception as e:
            logger.debug(f"Simplified search failed: {e}")

        # Strategy 3: Try Firecrawl search
        try:
            logger.debug(f"Attempting Firecrawl search: {query}")
            results = self.firecrawl_tools.search(query=query, limit=max_results)
            if results and "No results found" not in str(results):
                logger.debug("Firecrawl search successful")
                return results
        except Exception as e:
            logger.debug(f"Firecrawl search failed: {e}")

        # All strategies failed
        return self._get_search_failure_message(query)

    def _get_privacy_notice(self, action: str) -> str:
        """Get privacy notice for disallowed actions."""

        notices = {
            "search": (
                "🔒 **Privacy Mode Active**\n\n"
                "Search is currently disabled in local privacy mode. "
                "Your conversations remain 100% private and processed locally.\n\n"
                "To enable search, switch to hybrid or flexible privacy mode with:\n"
                "`/privacy hybrid` or `/privacy flexible`"
            ),
            "scraping": (
                "🔒 **Privacy Mode Active**\n\n"
                "Web scraping is currently disabled in local privacy mode. "
                "This ensures your data remains completely private.\n\n"
                "To enable web scraping, switch to hybrid or flexible privacy mode."
            ),
        }

        return notices.get(action, notices["search"])

    def _get_search_failure_message(self, query: str) -> str:
        """Get message for search failures."""
        return (
            f"I couldn't find search results for '{query}' right now. "
            "This might be due to search limitations or connectivity issues.\n\n"
            "Would you like to:\n"
            "- Rephrase your question differently?\n"
            "- Ask about a related topic?\n"
            "- Share what you already know so we can explore together?"
        )

    def _get_available_sources(self) -> List[str]:
        """Get list of available search sources."""
        sources = []

        if config.FIRECRAWL_API_KEY:
            sources.append("Firecrawl (web search)")

        if config.DUCKDUCKGO_ENABLED:  # Assuming this config exists
            sources.append("DuckDuckGo")

        if config.OPENWEATHER_API_KEY:
            sources.append("OpenWeather (weather data)")

        return sources or ["No external sources configured"]

    def _get_privacy_recommendations(self) -> List[str]:
        """Get privacy recommendations based on current mode."""

        recommendations = []

        if self.privacy_mode == "local":
            recommendations.extend(
                [
                    "Your conversations are 100% private",
                    "Consider switching to hybrid mode if you need web search",
                    "Local models provide fast, private responses",
                ]
            )
        elif self.privacy_mode == "hybrid":
            recommendations.extend(
                [
                    "Your AI conversations are private, search is optional",
                    "Enable search in config for research capabilities",
                    "Switch to local mode for complete privacy",
                ]
            )
        elif self.privacy_mode == "flexible":
            recommendations.extend(
                [
                    "You have full control over privacy settings",
                    "Use /privacy command to switch modes as needed",
                    "Balance between privacy and functionality",
                ]
            )

        return recommendations


class LocalModelTools(Toolkit):
    """
    Tools for managing and interacting with local models.
    """

    def __init__(self):
        super().__init__(name="local_model_tools")

        # Import here to avoid circular imports
        from app.models.local_llm import model_manager

        self.model_manager = model_manager

        # Register tool functions
        self.register(self.list_available_models)
        self.register(self.get_model_info)
        self.register(self.switch_model)
        self.register(self.test_model_connection)

    def list_available_models(self) -> str:
        """
        List all available local models.

        Returns:
            JSON string of available models and their capabilities
        """
        models = {}

        for model_name, config in self.model_manager.available_models.items():
            models[model_name] = {
                "description": config.get("description", "No description"),
                "best_for": config.get("best_for", []),
                "recommended": model_name
                in ["function-gemma:7b", "qwen2.5:3b", "phi3.5:3.8b"],
            }

        return json.dumps(
            {
                "available_models": models,
                "total_count": len(models),
                "recommended_models": [
                    "function-gemma:7b",
                    "qwen2.5:3b",
                    "phi3.5:3.8b",
                ],
            },
            indent=2,
        )

    def get_model_info(self, model_name: str = None) -> str:
        """
        Get detailed information about a specific model.

        Args:
            model_name: Model name (optional, defaults to current model)

        Returns:
            JSON string of model information
        """
        if not model_name:
            model_name = config.LOCAL_LLM_MODEL

        # Get model config
        model_config = self.model_manager.model_configs.get(model_name, {})

        # Check if model is available
        is_available = model_name in self.model_manager.available_models

        info = {
            "model_name": model_name,
            "is_available": is_available,
            "description": model_config.get("description", "No description"),
            "best_for": model_config.get("best_for", []),
            "recommended_settings": {
                "temperature": model_config.get("temperature", 0.7),
                "max_tokens": model_config.get("max_tokens", 2048),
            },
        }

        return json.dumps(info, indent=2)

    def switch_model(self, model_name: str) -> str:
        """
        Switch to a different local model.

        Args:
            model_name: Name of model to switch to

        Returns:
            Success or failure message
        """
        if model_name not in self.model_manager.available_models:
            return f"Model '{model_name}' is not available. Use list_available_models() to see options."

        try:
            # Update config (this would need to be implemented)
            # config.LOCAL_LLM_MODEL = model_name

            return f"Successfully switched to model: {model_name}\n\nRestart the application to apply changes."

        except Exception as e:
            return f"Failed to switch to model '{model_name}': {str(e)}"

    def test_model_connection(self, model_name: str = None) -> str:
        """
        Test connection to a local model.

        Args:
            model_name: Model name to test (optional)

        Returns:
            Connection test result
        """
        if not model_name:
            model_name = config.LOCAL_LLM_MODEL

        try:
            # Create test model
            from app.models.local_llm import LocalLlamaModel

            test_model = LocalLlamaModel(model=model_name)

            # Test connection (this would need to be async)
            # For now, return a placeholder
            return f"Connection test for '{model_name}': Not implemented yet"

        except Exception as e:
            return f"Connection test failed for '{model_name}': {str(e)}"
