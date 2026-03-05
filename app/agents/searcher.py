"""
Search Agent - Performs web searches for each sub-question

Uses Tavily API to search for information related to each sub-question concurrently
"""

import structlog
import asyncio
from typing import Dict, List
from app.agents.state import ResearchState, SearchResult
from app.tools.web_search import TavilySearchTool

logger = structlog.get_logger()


async def search_node(state: ResearchState) -> ResearchState:
    """
    Search agent node - performs web searches for each sub-question
    
    Args:
        state: Current research state with sub_questions
        
    Returns:
        Updated state with search_results
    """
    logger.info("search_agent_started", num_questions=len(state["sub_questions"]))
    
    try:
        search_tool = TavilySearchTool()
        search_results: Dict[str, List[SearchResult]] = {}
        
        # Search for each sub-question concurrently
        tasks = []
        for question in state["sub_questions"]:
            tasks.append(search_tool.search(question))
        
        # Execute all searches in parallel
        results_list = await asyncio.gather(*tasks)
        
        # Map results to questions
        total_sources = 0
        for question, results in zip(state["sub_questions"], results_list):
            search_results[question] = results
            total_sources += len(results)
        
        logger.info(
            "search_agent_completed",
            total_sources=total_sources,
            questions_searched=len(state["sub_questions"]),
            avg_per_question=total_sources / len(state["sub_questions"]) if state["sub_questions"] else 0
        )
        
        return {
            **state,
            "search_results": search_results,
            "total_sources": total_sources,
            "status": "analyzing"
        }
        
    except Exception as e:
        logger.error("search_agent_failed", error=str(e))
        return {
            **state,
            "status": "error",
            "error_message": f"Search failed: {str(e)}"
        }
