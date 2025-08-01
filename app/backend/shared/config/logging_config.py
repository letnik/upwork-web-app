"""
Централізована конфігурація логування для всіх мікросервісів
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .settings import settings


@dataclass
class LoggingConfig:
    """Конфігурація логування"""
    
    # Основні налаштування
    service_name: str
    log_level: str = "INFO"
    environment: str = "development"
    
    # Ротація логів
    rotation_config: Dict[str, Dict[str, Any]] = None
    
    # Формати логів
    console_format: str = None
    file_format: str = None
    
    # Шляхи до логів
    logs_directory: str = "logs"
    test_logs_directory: str = "logs/test"
    
    def __post_init__(self):
        """Ініціалізація після створення об'єкта"""
        if self.rotation_config is None:
            self.rotation_config = self._get_default_rotation_config()
        
        if self.console_format is None:
            self.console_format = self._get_console_format()
        
        if self.file_format is None:
            self.file_format = self._get_file_format()
    
    def _get_default_rotation_config(self) -> Dict[str, Dict[str, Any]]:
        """Отримання конфігурації ротації за замовчуванням"""
        return {
            "main": {
                "rotation": "50 MB",
                "retention": "90 days",
                "compression": "zip"
            },
            "error": {
                "rotation": "20 MB",
                "retention": "180 days",
                "compression": "zip"
            },
            "security": {
                "rotation": "10 MB",
                "retention": "365 days",
                "compression": "zip"
            },
            "performance": {
                "rotation": "20 MB",
                "retention": "90 days",
                "compression": "zip"
            },
            "api": {
                "rotation": "30 MB",
                "retention": "60 days",
                "compression": "zip"
            },
            "database": {
                "rotation": "20 MB",
                "retention": "90 days",
                "compression": "zip"
            },
            "test": {
                "rotation": "10 MB",
                "retention": "30 days",
                "compression": "zip"
            }
        }
    
    def _get_console_format(self) -> str:
        """Отримання формату для консолі"""
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    def _get_file_format(self) -> str:
        """Отримання формату для файлів"""
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    
    def get_log_file_path(self, log_type: str, is_test: bool = False) -> str:
        """Отримання шляху до файлу логу"""
        base_dir = self.test_logs_directory if is_test else self.logs_directory
        return f"{base_dir}/{self.service_name}_{log_type}.log"
    
    def get_rotation_config(self, log_type: str) -> Dict[str, Any]:
        """Отримання конфігурації ротації для типу логу"""
        return self.rotation_config.get(log_type, self.rotation_config["main"])
    
    def is_test_environment(self) -> bool:
        """Перевірка чи це тестове середовище"""
        return (
            self.environment == "test" or
            "pytest" in os.environ.get("PYTEST_CURRENT_TEST", "") or
            "test" in self.service_name.lower()
        )


def get_logging_config(
    service_name: Optional[str] = None,
    log_level: Optional[str] = None,
    environment: Optional[str] = None
) -> LoggingConfig:
    """Отримання конфігурації логування"""
    
    # Використовуємо налаштування з settings або передані параметри
    service_name = service_name or settings.SERVICE_NAME
    log_level = log_level or settings.LOG_LEVEL
    environment = environment or settings.ENVIRONMENT
    
    return LoggingConfig(
        service_name=service_name,
        log_level=log_level,
        environment=environment
    )


# Глобальні константи для логування
LOG_TYPES = {
    "main": "service",
    "error": "service_error",
    "security": "service_security",
    "performance": "service_performance",
    "api": "service_api",
    "database": "service_database",
    "test": "service_test"
}

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# Фільтри для різних типів логів
LOG_FILTERS = {
    "security": lambda record: "Security:" in record["message"],
    "performance": lambda record: "Performance:" in record["message"],
    "api": lambda record: "API:" in record["message"],
    "database": lambda record: "Database:" in record["message"],
    "test": lambda record: "Test:" in record["message"]
}

# Конфігурація для різних середовищ
ENVIRONMENT_CONFIGS = {
    "development": {
        "log_level": "DEBUG",
        "console_output": True,
        "file_output": True,
        "colorize": True
    },
    "production": {
        "log_level": "INFO",
        "console_output": False,
        "file_output": True,
        "colorize": False
    },
    "test": {
        "log_level": "DEBUG",
        "console_output": True,
        "file_output": True,
        "colorize": True
    }
} 