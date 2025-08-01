"""
AI API Configuration
Configuration file for OpenAI and Anthropic API keys and settings.
"""

import os
from typing import Optional


class AIConfig:
    """Configuration class for AI API settings."""
    
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        # Anthropic Configuration
        self.anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_model: str = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        # API Base URLs
        self.openai_base_url: str = "https://api.openai.com/v1"
        self.anthropic_base_url: str = "https://api.anthropic.com"
        
        # Rate limiting and timeout settings
        self.request_timeout: int = int(os.getenv('AI_REQUEST_TIMEOUT', '30'))
        self.max_retries: int = int(os.getenv('AI_MAX_RETRIES', '3'))
    
    def validate_config(self) -> bool:
        """Validate that required API keys are set."""
        if not self.openai_api_key:
            print("Warning: OPENAI_API_KEY not set")
        if not self.anthropic_api_key:
            print("Warning: ANTHROPIC_API_KEY not set")
        
        return bool(self.openai_api_key or self.anthropic_api_key)
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration dictionary."""
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model,
            'base_url': self.openai_base_url,
            'timeout': self.request_timeout,
            'max_retries': self.max_retries
        }
    
    def get_anthropic_config(self) -> dict:
        """Get Anthropic configuration dictionary."""
        return {
            'api_key': self.anthropic_api_key,
            'model': self.anthropic_model,
            'base_url': self.anthropic_base_url,
            'timeout': self.request_timeout,
            'max_retries': self.max_retries
        }


# Global configuration instance
ai_config = AIConfig() 