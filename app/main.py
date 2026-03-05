"""
FastAPI Application - Multi-Agent Research Assistant API

Main entry point for the research assistant API with endpoints for
starting research, checking status, and retrieving results.
"""

import structlog
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List

from app.core.config import get_settings
from app.core.logger import setup_logging
from app.core.database import Database
from app.agents.graph import run_research
from app.models.schemas import (
    ResearchRequest,
    ResearchResponse,
    ResearchStatus,
    ResearchResult,
    ResearchHistoryItem
)

# Setup logging
setup_logging()
logger = structlog.get_logger()

# In-memory store for ongoing researches
active_researches: Dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    
    Initializes database on startup and closes on shutdown
    """
    logger.info("application_starting")
    
    # Initialize database
    db = Database()
    await db.initialize()
    app.state.db = db
    
    yield
    
    # Cleanup
    logger.info("application_shutting_down")
    await db.close()


# Create FastAPI application
app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="""
    A production-ready AI research assistant that autonomously researches topics 
    and generates comprehensive reports with citations.
    
    Built with LangGraph to orchestrate multiple specialized agents:
    - **Planner Agent**: Breaks down research topics into focused sub-questions
    - **Web Search Agent**: Searches the web using Tavily API
    - **Analyzer Agent**: Synthesizes results and extracts key insights
    - **Report Writer Agent**: Generates markdown reports with citations
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Routes ====================

@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint
    
    Returns application status and version
    """
    return {
        "status": "healthy",
        "service": "Multi-Agent Research Assistant",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/research", response_model=ResearchResponse, tags=["Research"])
async def create_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new research task
    
    The research runs in the background. Use the returned research_id
    to poll for status and retrieve results.
    
    Args:
        request: ResearchRequest with query
        background_tasks: FastAPI background tasks
        
    Returns:
        ResearchResponse with research_id and status
    """
    research_id = str(uuid.uuid4())
    
    logger.info("research_request_received", research_id=research_id, query=request.query)
    
    # Store in active researches
    active_researches[research_id] = {
        "status": "started",
        "query": request.query,
        "research_id": research_id,
        "created_at": datetime.now()
    }
    
    # Start research in background
    background_tasks.add_task(execute_research, research_id, request.query)
    
    return ResearchResponse(
        research_id=research_id,
        status="started",
        message="Research started successfully. Poll /research/{research_id}/status for updates."
    )


async def execute_research(research_id: str, query: str):
    """
    Background task to execute research workflow
    
    Args:
        research_id: Unique research identifier
        query: Research question
    """
    try:
        # Update status to running
        active_researches[research_id]["status"] = "running"
        
        # Run research workflow
        result = await run_research(query)
        
        # Save to database
        db: Database = app.state.db
        await db.save_research(
            research_id=research_id,
            query=query,
            report=result.get("final_report", ""),
            num_sources=result.get("total_sources", 0),
            execution_time=result.get("execution_time", 0),
            status=result.get("status", "error"),
            error_message=result.get("error_message")
        )
        
        # Update active researches with result
        active_researches[research_id] = {
            "status": result.get("status", "error"),
            "query": query,
            "research_id": research_id,
            "result": result,
            "created_at": active_researches[research_id].get("created_at", datetime.now())
        }
        
        logger.info("research_completed_background", research_id=research_id)
        
    except Exception as e:
        logger.error("research_background_failed", research_id=research_id, error=str(e))
        active_researches[research_id]["status"] = "error"
        active_researches[research_id]["error"] = str(e)


@app.get("/research/{research_id}/status", response_model=ResearchStatus, tags=["Research"])
async def get_research_status(research_id: str):
    """
    Get status of a research task
    
    Args:
        research_id: Research identifier
        
    Returns:
        ResearchStatus with current status and metadata
    """
    # Check active researches first (for running tasks)
    if research_id in active_researches:
        active = active_researches[research_id]
        return ResearchStatus(
            research_id=research_id,
            status=active["status"],
            query=active["query"],
            execution_time=active.get("result", {}).get("execution_time"),
            error_message=active.get("error"),
            created_at=active.get("created_at", datetime.now())
        )
    
    # Check database for completed tasks
    db: Database = app.state.db
    research = await db.get_research(research_id)
    
    if not research:
        raise HTTPException(status_code=404, detail="Research not found")
    
    return ResearchStatus(
        research_id=research_id,
        status=research["status"],
        query=research["query"],
        execution_time=research.get("execution_time"),
        error_message=research.get("error_message"),
        created_at=research["created_at"]
    )


@app.get("/research/{research_id}", response_model=ResearchResult, tags=["Research"])
async def get_research_result(research_id: str):
    """
    Get completed research result
    
    Args:
        research_id: Research identifier
        
    Returns:
        ResearchResult with full report
    """
    db: Database = app.state.db
    research = await db.get_research(research_id)
    
    if not research:
        raise HTTPException(status_code=404, detail="Research not found")
    
    if research["status"] != "complete":
        raise HTTPException(
            status_code=400,
            detail=f"Research not complete. Current status: {research['status']}"
        )
    
    return ResearchResult(
        research_id=research_id,
        query=research["query"],
        report=research["report"],
        num_sources=research["num_sources"],
        execution_time=research["execution_time"],
        created_at=research["created_at"]
    )


@app.get("/research", response_model=List[ResearchHistoryItem], tags=["Research"])
async def get_research_history(limit: int = 10):
    """
    Get research history
    
    Args:
        limit: Maximum number of results (default: 10)
        
    Returns:
        List of research history items
    """
    db: Database = app.state.db
    history = await db.get_history(limit=limit)
    
    return [
        ResearchHistoryItem(
            research_id=item["research_id"],
            query=item["query"],
            status=item["status"],
            created_at=item["created_at"]
        )
        for item in history
    ]


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload
    )
