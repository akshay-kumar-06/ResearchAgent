"""
Configuration management using pydantic-settings

Load settings from environment variables and .env file
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    google_api_key: str
    tavily_api_key: str
    
    # Model Configuration
    llm_model: str = "gemini-2.5-flash-lite"
    llm_temperature: float = 0.3
    max_tokens: int = 8000
    
    # Tavily Configuration
    tavily_max_results: int = 5
    tavily_search_depth: str = "basic"
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True
    log_level: str = "INFO"
    
    # Database
    database_path: str = "./data/research.db"
    
    # Rate Limiting
    max_concurrent_researches: int = 3
    request_timeout: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings: Application settings
    """
    return Settings()
