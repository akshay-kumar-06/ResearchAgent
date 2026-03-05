"""
SQLite database handler for research history

Provides async database operations using aiosqlite
"""

import aiosqlite
import structlog
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from app.core.config import get_settings

logger = structlog.get_logger()


class Database:
    """SQLite database handler for research history"""
    
    def __init__(self):
        settings = get_settings()
        self.db_path = settings.database_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self) -> None:
        """Initialize database and create tables"""
        # Ensure data directory exists
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.connection = await aiosqlite.connect(self.db_path)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS researches (
                research_id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                report TEXT,
                num_sources INTEGER,
                execution_time REAL,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.commit()
        logger.info("database_initialized", db_path=self.db_path)
    
    async def save_research(
        self,
        research_id: str,
        query: str,
        report: str,
        num_sources: int,
        execution_time: float,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Save research result to database
        
        Args:
            research_id: Unique identifier for the research
            query: Original research query
            report: Generated markdown report
            num_sources: Number of sources used
            execution_time: Time taken to complete research
            status: Final status (complete, error)
            error_message: Error message if failed
        """
        await self.connection.execute(
            """
            INSERT INTO researches 
            (research_id, query, report, num_sources, execution_time, status, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (research_id, query, report, num_sources, execution_time, status, error_message, datetime.now())
        )
        await self.connection.commit()
        logger.info("research_saved", research_id=research_id)
    
    async def get_research(self, research_id: str) -> Optional[Dict]:
        """
        Get research by ID
        
        Args:
            research_id: Unique identifier
            
        Returns:
            Research data dict or None if not found
        """
        async with self.connection.execute(
            "SELECT * FROM researches WHERE research_id = ?",
            (research_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "research_id": row[0],
                    "query": row[1],
                    "report": row[2],
                    "num_sources": row[3],
                    "execution_time": row[4],
                    "status": row[5],
                    "error_message": row[6],
                    "created_at": row[7]
                }
        return None
    
    async def get_history(self, limit: int = 10) -> List[Dict]:
        """
        Get research history
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of research history items
        """
        async with self.connection.execute(
            "SELECT research_id, query, status, created_at FROM researches ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "research_id": row[0],
                    "query": row[1],
                    "status": row[2],
                    "created_at": row[3]
                }
                for row in rows
            ]
    
    async def close(self) -> None:
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("database_closed")
