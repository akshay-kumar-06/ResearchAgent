"""
Citation Tracker Tool

Manages citations for research reports, tracks sources and quotes
"""

import structlog
from typing import List, Dict
from app.agents.state import Citation, SearchResult

logger = structlog.get_logger()


class CitationTracker:
    """Tracks and manages citations for research reports"""
    
    def __init__(self):
        self.citations: List[Citation] = []
        self._url_index: Dict[str, int] = {}
    
    def add_citation(
        self,
        source_url: str,
        source_title: str,
        quote: str,
        relevance: str = "medium"
    ) -> int:
        """
        Add a new citation
        
        Args:
            source_url: URL of the source
            source_title: Title of the source
            quote: Relevant quote or paraphrase
            relevance: Citation relevance (low, medium, high)
            
        Returns:
            Citation index (1-based)
        """
        citation = Citation(
            source_url=source_url,
            source_title=source_title,
            quote=quote,
            relevance=relevance
        )
        self.citations.append(citation)
        
        index = len(self.citations)
        self._url_index[source_url] = index
        
        logger.debug("citation_added", index=index, url=source_url)
        return index
    
    def get_citation_from_result(
        self,
        result: SearchResult,
        quote: str,
        relevance: str = "medium"
    ) -> int:
        """
        Create citation from a SearchResult
        
        Args:
            result: SearchResult to cite
            quote: Relevant quote
            relevance: Citation relevance
            
        Returns:
            Citation index
        """
        return self.add_citation(
            source_url=result.url,
            source_title=result.title,
            quote=quote,
            relevance=relevance
        )
    
    def get_citation_by_url(self, url: str) -> int:
        """
        Get citation index by URL
        
        Args:
            url: Source URL
            
        Returns:
            Citation index or -1 if not found
        """
        return self._url_index.get(url, -1)
    
    def format_citations_list(self) -> str:
        """
        Format citations as numbered list for report
        
        Returns:
            Formatted citation list string
        """
        lines = []
        for idx, citation in enumerate(self.citations, 1):
            lines.append(f"[{idx}] {citation.source_title} - {citation.source_url}")
        
        return "\n".join(lines)
    
    def get_all_citations(self) -> List[Citation]:
        """Get all tracked citations"""
        return self.citations.copy()
    
    def clear(self) -> None:
        """Clear all citations"""
        self.citations.clear()
        self._url_index.clear()
        logger.debug("citations_cleared")
