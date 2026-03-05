"""
Tavily Web Search Tool

Wrapper for Tavily API to perform web searches and return structured results
"""

import structlog
from tavily import AsyncTavilyClient
from typing import List
from app.core.config import get_settings
from app.agents.state import SearchResult

logger = structlog.get_logger()


class TavilySearchTool:
    """Wrapper for Tavily search API"""
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        self.max_results = settings.tavily_max_results
        self.search_depth = settings.tavily_search_depth
    
    async def search(self, query: str) -> List[SearchResult]:
        """
        Perform web search using Tavily
        
        Args:
            query: Search query string
            
        Returns:
            List of SearchResult objects
        """
        try:
            logger.info("tavily_search_started", query=query)
            
            response = await self.client.search(
                query=query,
                max_results=self.max_results,
                search_depth=self.search_depth,
                include_raw_content=False,
                include_answer=True
            )
            
            results = []
            for idx, result in enumerate(response.get("results", [])):
                search_result = SearchResult(
                    url=result.get("url", ""),
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    relevance_score=result.get("score", 0.5)
                )
                results.append(search_result)
            
            logger.info(
                "tavily_search_completed",
                query=query,
                results_count=len(results)
            )
            
            return results
            
        except Exception as e:
            logger.error("tavily_search_failed", query=query, error=str(e))
            return []
