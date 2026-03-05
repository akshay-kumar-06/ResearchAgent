"""
Pydantic models for API request/response schemas

Provides validation and serialization for all API interactions
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ResearchRequest(BaseModel):
    """Request model for starting research"""
    query: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Research question to investigate"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Compare AI regulations in EU vs US"
            }
        }


class ResearchResponse(BaseModel):
    """Response model for research request"""
    research_id: str
    status: str
    message: str


class ResearchStatus(BaseModel):
    """Status of ongoing research"""
    research_id: str
    status: str
    query: str
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime


class ResearchResult(BaseModel):
    """Complete research result with report"""
    research_id: str
    query: str
    report: str
    num_sources: int
    execution_time: float
    created_at: datetime


class ResearchHistoryItem(BaseModel):
    """Item in research history list"""
    research_id: str
    query: str
    status: str
    created_at: datetime
