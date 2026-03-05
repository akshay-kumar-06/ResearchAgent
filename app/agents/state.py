"""
LangGraph state definition for research workflow

Defines the state schema that is passed between all agents
"""

from typing import TypedDict, Annotated, List, Dict, Optional
from langgraph.graph import add_messages
from pydantic import BaseModel


class SearchResult(BaseModel):
    """Individual search result from web search"""
    url: str
    title: str
    content: str
    relevance_score: float


class Citation(BaseModel):
    """Citation information for report"""
    source_url: str
    source_title: str
    quote: str
    relevance: str


class ResearchState(TypedDict):
    """
    LangGraph state for research workflow
    
    This state is passed between all agents and updated as the workflow progresses.
    Each agent reads from and writes to specific fields in the state.
    """
    # Input
    original_query: str
    
    # Planner outputs
    research_plan: Optional[str]   # Overall research strategy
    sub_questions: List[str]       # List of 3-5 focused questions
    
    # Search outputs
    search_results: Dict[str, List[SearchResult]]  # Keyed by sub_question
    total_sources: int
    
    # Analyzer outputs
    key_findings: List[str]        # Main insights extracted
    citations: List[Citation]       # Tracked citations
    synthesis: str                  # Combined analysis
    
    # Report outputs
    final_report: str               # Markdown formatted report
    
    # Metadata
    status: str                     # "planning", "searching", "analyzing", "writing", "complete", "error"
    error_message: Optional[str]
    execution_time: float
    
    # Messages for LangGraph
    messages: Annotated[List, add_messages]
