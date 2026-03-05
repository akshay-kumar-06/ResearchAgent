"""
Tool Integration Tests

Tests for web search and citation tracker tools
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.tools.web_search import TavilySearchTool
from app.tools.citation_tracker import CitationTracker
from app.agents.state import SearchResult


class TestTavilySearchTool:
    """Tests for Tavily search tool"""
    
    @pytest.mark.asyncio
    async def test_search_success(self, mock_tavily_response, mock_settings):
        """Test successful search"""
        with patch("app.tools.web_search.get_settings") as mock_get_settings, \
             patch("app.tools.web_search.AsyncTavilyClient") as mock_client:
            
            mock_get_settings.return_value = mock_settings
            
            mock_instance = AsyncMock()
            mock_instance.search.return_value = mock_tavily_response
            mock_client.return_value = mock_instance
            
            tool = TavilySearchTool()
            results = await tool.search("AI regulations")
            
            assert len(results) == 2
            assert isinstance(results[0], SearchResult)
            assert results[0].url == "https://example.com/ai-regulations"
    
    @pytest.mark.asyncio
    async def test_search_empty_results(self, mock_settings):
        """Test search with no results"""
        with patch("app.tools.web_search.get_settings") as mock_get_settings, \
             patch("app.tools.web_search.AsyncTavilyClient") as mock_client:
            
            mock_get_settings.return_value = mock_settings
            
            mock_instance = AsyncMock()
            mock_instance.search.return_value = {"results": []}
            mock_client.return_value = mock_instance
            
            tool = TavilySearchTool()
            results = await tool.search("obscure topic")
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, mock_settings):
        """Test search error handling"""
        with patch("app.tools.web_search.get_settings") as mock_get_settings, \
             patch("app.tools.web_search.AsyncTavilyClient") as mock_client:
            
            mock_get_settings.return_value = mock_settings
            
            mock_instance = AsyncMock()
            mock_instance.search.side_effect = Exception("API error")
            mock_client.return_value = mock_instance
            
            tool = TavilySearchTool()
            results = await tool.search("test query")
            
            # Should return empty list on error
            assert results == []


class TestCitationTracker:
    """Tests for citation tracker tool"""
    
    def test_add_citation(self):
        """Test adding a citation"""
        tracker = CitationTracker()
        index = tracker.add_citation(
            source_url="https://example.com",
            source_title="Example Title",
            quote="Example quote",
            relevance="high"
        )
        
        assert index == 1
        assert len(tracker.citations) == 1
    
    def test_add_multiple_citations(self):
        """Test adding multiple citations"""
        tracker = CitationTracker()
        
        idx1 = tracker.add_citation("url1", "title1", "quote1")
        idx2 = tracker.add_citation("url2", "title2", "quote2")
        idx3 = tracker.add_citation("url3", "title3", "quote3")
        
        assert idx1 == 1
        assert idx2 == 2
        assert idx3 == 3
        assert len(tracker.citations) == 3
    
    def test_get_citation_from_result(self, sample_search_results):
        """Test creating citation from search result"""
        tracker = CitationTracker()
        result = sample_search_results[0]
        
        index = tracker.get_citation_from_result(
            result=result,
            quote="Important quote",
            relevance="high"
        )
        
        assert index == 1
        assert tracker.citations[0].source_url == result.url
        assert tracker.citations[0].source_title == result.title
    
    def test_get_citation_by_url(self):
        """Test getting citation by URL"""
        tracker = CitationTracker()
        tracker.add_citation("https://example.com", "Title", "Quote")
        
        index = tracker.get_citation_by_url("https://example.com")
        assert index == 1
        
        index = tracker.get_citation_by_url("https://nonexistent.com")
        assert index == -1
    
    def test_format_citations_list(self):
        """Test formatting citations as list"""
        tracker = CitationTracker()
        tracker.add_citation("url1", "Title 1", "Quote 1")
        tracker.add_citation("url2", "Title 2", "Quote 2")
        
        formatted = tracker.format_citations_list()
        
        assert "[1]" in formatted
        assert "[2]" in formatted
        assert "Title 1" in formatted
        assert "url1" in formatted
    
    def test_clear_citations(self):
        """Test clearing all citations"""
        tracker = CitationTracker()
        tracker.add_citation("url", "title", "quote")
        
        assert len(tracker.citations) == 1
        
        tracker.clear()
        
        assert len(tracker.citations) == 0
    
    def test_get_all_citations(self):
        """Test getting all citations returns copy"""
        tracker = CitationTracker()
        tracker.add_citation("url", "title", "quote")
        
        citations = tracker.get_all_citations()
        
        assert len(citations) == 1
        # Should return copy, not reference
        citations.clear()
        assert len(tracker.citations) == 1
