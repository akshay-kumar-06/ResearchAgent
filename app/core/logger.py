"""
Structured logging configuration using structlog

Provides JSON-formatted logs with timestamps and log levels
"""

import structlog
import logging
from app.core.config import get_settings


def setup_logging() -> None:
    """
    Configure structured logging for the application
    
    Sets up structlog with JSON rendering, timestamps,
    and log level filtering based on settings
    """
    settings = get_settings()
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )
