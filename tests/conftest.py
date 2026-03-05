"""
Pytest configuration and fixtures

Provides shared fixtures for async testing, mock LLM, and test database
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List
import tempfile
import os

# Set test environment variables before importing app modules
os.environ["GOOGLE_API_KEY"] = "test-google-api-key"
os.environ["TAVILY_API_KEY"] = "test-tavily-api-key"
os.environ["DATABASE_PATH"] = ":memory:"

from app.agents.state import ResearchState, SearchResult, Citation
from app.core.database import Database


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create a test database"""
    # Use temporary file for test database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    # Patch the settings
    with patch("app.core.database.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(database_path=db_path)
        
        db = Database()
        await db.initialize()
        yield db
        await db.close()
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def sample_search_results() -> List[SearchResult]:
    """Sample search results for testing"""
    return [
        SearchResult(
            url="https://example.com/article1",
            title="AI Regulations in Europe",
            content="The EU AI Act is a comprehensive framework for regulating artificial intelligence...",
            relevance_score=0.95
        ),
        SearchResult(
            url="https://example.com/article2",
            title="US AI Policy Overview",
            content="The United States takes a sector-specific approach to AI regulation...",
            relevance_score=0.88
        ),
        SearchResult(
            url="https://example.com/article3",
            title="Comparing Global AI Governance",
            content="Different regions have adopted varying approaches to AI governance...",
            relevance_score=0.82
        )
    ]


@pytest.fixture
def sample_citations() -> List[Citation]:
    """Sample citations for testing"""
    return [
        Citation(
            source_url="https://example.com/article1",
            source_title="AI Regulations in Europe",
            quote="The EU AI Act is a comprehensive framework",
            relevance="high"
        ),
        Citation(
            source_url="https://example.com/article2",
            source_title="US AI Policy Overview",
            quote="sector-specific approach to AI regulation",
            relevance="high"
        )
    ]


@pytest.fixture
def sample_research_state(sample_search_results, sample_citations) -> ResearchState:
    """Sample research state for testing"""
    return {
        "original_query": "Compare AI regulations in EU vs US",
        "research_plan": "Compare regulatory frameworks in EU and US",
        "sub_questions": [
            "What are the key AI regulations in the EU?",
            "What are the key AI regulations in the US?",
            "How do EU and US approaches differ?"
        ],
        "search_results": {
            "What are the key AI regulations in the EU?": sample_search_results[:2],
            "What are the key AI regulations in the US?": sample_search_results[1:],
            "How do EU and US approaches differ?": sample_search_results
        },
        "total_sources": 7,
        "key_findings": [
            "EU has comprehensive AI Act",
            "US uses sector-specific approach",
            "Different risk classification systems"
        ],
        "citations": sample_citations,
        "synthesis": "The EU and US have adopted different approaches...",
        "final_report": "",
        "status": "planning",
        "error_message": None,
        "execution_time": 0.0,
        "messages": []
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    response = MagicMock()
    response.content = """RESEARCH PLAN: Compare AI regulatory frameworks in EU and US

SUB-QUESTIONS:
1. What are the key AI regulations in the European Union?
2. What are the key AI regulations in the United States?
3. How do EU and US approaches differ in their regulatory philosophy?
"""
    return response


@pytest.fixture
def mock_tavily_response():
    """Mock Tavily API response"""
    return {
        "results": [
            {
                "url": "https://example.com/ai-regulations",
                "title": "AI Regulations Overview",
                "content": "Comprehensive overview of AI regulations worldwide...",
                "score": 0.9
            },
            {
                "url": "https://example.com/eu-ai-act",
                "title": "EU AI Act Explained",
                "content": "The European Union AI Act establishes...",
                "score": 0.85
            }
        ]
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = MagicMock()
    settings.google_api_key = "test-api-key"
    settings.tavily_api_key = "test-tavily-key"
    settings.llm_model = "gemini-2.0-flash-exp"
    settings.llm_temperature = 0.3
    settings.tavily_max_results = 5
    settings.tavily_search_depth = "basic"
    settings.database_path = ":memory:"
    return settings
