"""Custom tools with fallback mechanisms for robust search."""

from typing import List, Dict, Any, Optional
from agno.tools import Toolkit
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.firecrawl import FirecrawlTools
from app.logger import get_logger

logger = get_logger("migru.tools")


class SmartSearchTools(Toolkit):
    """Search tools with automatic fallback mechanisms."""

    def __init__(self):
        super().__init__(name="smart_search")
        self.ddg_tools = DuckDuckGoTools()
        self.firecrawl_tools = FirecrawlTools(enable_scrape=True, enable_crawl=True)
        self.register(self.search_with_fallback)
        self.register(self.scrape_url)

    def search_with_fallback(
        self, query: str, max_results: int = 5
    ) -> str:
        """
        Smart search with automatic fallback to multiple sources.
        
        Tries DuckDuckGo first, then Firecrawl search if DuckDuckGo fails.
        Returns formatted results or falls back gracefully.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            Formatted search results or a helpful message if no results found
        """
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

        # Strategy 2: Try with modified query (broader search)
        try:
            # Simplify query by taking first few keywords
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

        # Strategy 3: Try Firecrawl search (more reliable but slower)
        try:
            logger.debug(f"Attempting Firecrawl search: {query}")
            results = self.firecrawl_tools.search(query=query, limit=max_results)
            if results and "No results found" not in str(results):
                logger.debug("Firecrawl search successful")
                return results
        except Exception as e:
            logger.debug(f"Firecrawl search failed: {e}")

        # All strategies failed - return graceful message
        logger.debug("All search strategies failed")
        return (
            f"I couldn't find specific search results for '{query}' right now. "
            "This might be due to search limitations or connectivity. "
            "Would you like to try:\n"
            "- Rephrasing the question in a different way?\n"
            "- Asking about a related topic?\n"
            "- Sharing what you already know about this, so we can explore together?"
        )

    def scrape_url(self, url: str) -> str:
        """
        Scrape content from a specific URL using Firecrawl.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Scraped content or error message
        """
        try:
            logger.debug(f"Scraping URL: {url}")
            content = self.firecrawl_tools.scrape_url(url=url)
            logger.debug("URL scraping successful")
            return content
        except Exception as e:
            logger.debug(f"URL scraping failed: {e}")
            return f"I couldn't access that URL right now. Error: {str(e)}"
