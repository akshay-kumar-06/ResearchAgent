"""
FastAPI Endpoint Tests

Tests for API endpoints using httpx test client
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport
from datetime import datetime

# Import app after setting environment variables
import os
os.environ["GOOGLE_API_KEY"] = "test-google-api-key"
os.environ["TAVILY_API_KEY"] = "test-tavily-api-key"

from app.main import app


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check returns healthy status"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Multi-Agent Research Assistant"


class TestResearchEndpoints:
    """Tests for research API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_research_valid_query(self):
        """Test creating research with valid query"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/research",
                json={"query": "Compare AI regulations in EU vs US"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "research_id" in data
        assert data["status"] == "started"
    
    @pytest.mark.asyncio
    async def test_create_research_short_query(self):
        """Test creating research with too short query"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/research",
                json={"query": "short"}
            )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_research_status_not_found(self):
        """Test getting status of non-existent research"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/research/non-existent-id/status")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_research_result_not_found(self):
        """Test getting result of non-existent research"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/research/non-existent-id")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_research_history_empty(self):
        """Test getting empty research history"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/research?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestRequestValidation:
    """Tests for request validation"""
    
    @pytest.mark.asyncio
    async def test_missing_query_field(self):
        """Test request with missing query field"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/research", json={})
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_json(self):
        """Test request with invalid JSON"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/research",
                content="not valid json",
                headers={"Content-Type": "application/json"}
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_query_too_long(self):
        """Test request with query exceeding max length"""
        long_query = "a" * 600  # Exceeds 500 char limit
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/research",
                json={"query": long_query}
            )
        
        assert response.status_code == 422
