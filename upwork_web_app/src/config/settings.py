"""
Налаштування проекту Upwork Parser
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Налаштування проекту"""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@postgres:5432/upwork_parser"
    redis_url: str = "redis://redis:6379"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/upwork_parser.log"
    
    # Upwork Configuration
    upwork_base_url: str = "https://www.upwork.com"
    upwork_search_url: str = "https://www.upwork.com/nx/search/jobs/"
    parsing_interval: int = 300  # 5 minutes in seconds (оптимізовано для IPv4 проксі)
    rate_limit_delay: int = 30   # 30 seconds between requests (обережно для IPv4)
    
    # Google Drive Configuration
    google_credentials_file: str = "credentials.json"
    google_sheets_folder_id: Optional[str] = None
    
    # Web Interface
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    
    # Development
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальний екземпляр налаштувань
settings = Settings() 