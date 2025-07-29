"""
Спільні налаштування для всіх мікросервісів
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Базові налаштування для всіх сервісів"""
    
    # Загальні налаштування
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    SERVICE_NAME: str = Field(default="upwork-service", env="SERVICE_NAME")
    
    # База даних
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/upwork_app",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        env="REDIS_URL"
    )
    
    # JWT налаштування
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Шифрування
    ENCRYPTION_KEY: str = Field(
        default="your-encryption-key-change-in-production",
        env="ENCRYPTION_KEY"
    )
    
    # Upwork API
    UPWORK_CLIENT_ID: Optional[str] = Field(default=None, env="UPWORK_CLIENT_ID")
    UPWORK_CLIENT_SECRET: Optional[str] = Field(default=None, env="UPWORK_CLIENT_SECRET")
    UPWORK_CALLBACK_URL: str = Field(
        default="http://localhost:8000/auth/upwork/callback",
        env="UPWORK_CALLBACK_URL"
    )
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    CLAUDE_API_KEY: Optional[str] = Field(default=None, env="CLAUDE_API_KEY")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    
    # Email
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Логування
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # CORS
    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # API Gateway
    API_GATEWAY_URL: str = Field(
        default="http://localhost:8000",
        env="API_GATEWAY_URL"
    )
    
    # Сервіси
    AUTH_SERVICE_URL: str = Field(
        default="http://auth-service:8001",
        env="AUTH_SERVICE_URL"
    )
    UPWORK_SERVICE_URL: str = Field(
        default="http://upwork-service:8002",
        env="UPWORK_SERVICE_URL"
    )
    AI_SERVICE_URL: str = Field(
        default="http://ai-service:8003",
        env="AI_SERVICE_URL"
    )
    ANALYTICS_SERVICE_URL: str = Field(
        default="http://analytics-service:8004",
        env="ANALYTICS_SERVICE_URL"
    )
    NOTIFICATION_SERVICE_URL: str = Field(
        default="http://notification-service:8005",
        env="NOTIFICATION_SERVICE_URL"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальний екземпляр налаштувань
settings = Settings()


def get_settings() -> Settings:
    """Отримання налаштувань"""
    return settings 