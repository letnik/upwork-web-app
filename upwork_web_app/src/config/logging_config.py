"""
Конфігурація логування
"""

import os
from pathlib import Path
from typing import Dict, Any


class LoggingConfig:
    """Конфігурація системи логування"""
    
    # Основні налаштування
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    JSON_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    
    # Шляхи до лог-файлів
    LOG_DIR = Path("logs")
    APP_LOG_FILE = LOG_DIR / "app.log"
    APP_JSON_LOG_FILE = LOG_DIR / "app.json"
    PARSING_LOG_FILE = LOG_DIR / "parsing.log"
    PARSING_JSON_LOG_FILE = LOG_DIR / "parsing.json"
    ERROR_LOG_FILE = LOG_DIR / "errors.log"
    ERROR_JSON_LOG_FILE = LOG_DIR / "errors.json"
    SECURITY_LOG_FILE = LOG_DIR / "security.log"
    SECURITY_JSON_LOG_FILE = LOG_DIR / "security.json"
    PROXY_LOG_FILE = LOG_DIR / "proxy.log"
    PROXY_JSON_LOG_FILE = LOG_DIR / "proxy.json"
    
    # Налаштування ротації
    ROTATION_SIZE = "10 MB"
    ROTATION_TIME = "1 day"
    RETENTION_DAYS = 30
    COMPRESSION = "zip"
    
    # Налаштування для різних типів логів
    LOG_CONFIGS = {
        "app": {
            "file": APP_LOG_FILE,
            "json_file": APP_JSON_LOG_FILE,
            "level": "INFO",
            "rotation": ROTATION_SIZE,
            "retention": f"{RETENTION_DAYS} days",
            "compression": COMPRESSION,
            "format": LOG_FORMAT,
            "json_format": JSON_FORMAT
        },
        "parsing": {
            "file": PARSING_LOG_FILE,
            "json_file": PARSING_JSON_LOG_FILE,
            "level": "INFO",
            "rotation": ROTATION_SIZE,
            "retention": f"{RETENTION_DAYS} days",
            "compression": COMPRESSION,
            "format": LOG_FORMAT,
            "json_format": JSON_FORMAT
        },
        "errors": {
            "file": ERROR_LOG_FILE,
            "json_file": ERROR_JSON_LOG_FILE,
            "level": "ERROR",
            "rotation": ROTATION_SIZE,
            "retention": f"{RETENTION_DAYS} days",
            "compression": COMPRESSION,
            "format": LOG_FORMAT,
            "json_format": JSON_FORMAT
        },
        "security": {
            "file": SECURITY_LOG_FILE,
            "json_file": SECURITY_JSON_LOG_FILE,
            "level": "WARNING",
            "rotation": ROTATION_SIZE,
            "retention": f"{RETENTION_DAYS} days",
            "compression": COMPRESSION,
            "format": LOG_FORMAT,
            "json_format": JSON_FORMAT
        },
        "proxy": {
            "file": PROXY_LOG_FILE,
            "json_file": PROXY_JSON_LOG_FILE,
            "level": "INFO",
            "rotation": ROTATION_SIZE,
            "retention": f"{RETENTION_DAYS} days",
            "compression": COMPRESSION,
            "format": LOG_FORMAT,
            "json_format": JSON_FORMAT
        }
    }
    
    # Налаштування для різних середовищ
    ENVIRONMENT_CONFIGS = {
        "development": {
            "console_output": True,
            "file_output": True,
            "json_output": True,
            "log_level": "DEBUG"
        },
        "production": {
            "console_output": False,
            "file_output": True,
            "json_output": True,
            "log_level": "INFO"
        },
        "testing": {
            "console_output": True,
            "file_output": False,
            "json_output": False,
            "log_level": "DEBUG"
        }
    }
    
    @classmethod
    def get_environment_config(cls, environment: str = None) -> Dict[str, Any]:
        """Отримання конфігурації для середовища"""
        if not environment:
            environment = os.getenv("ENVIRONMENT", "development")
        
        return cls.ENVIRONMENT_CONFIGS.get(environment, cls.ENVIRONMENT_CONFIGS["development"])
    
    @classmethod
    def get_log_config(cls, log_type: str) -> Dict[str, Any]:
        """Отримання конфігурації для типу логу"""
        return cls.LOG_CONFIGS.get(log_type, cls.LOG_CONFIGS["app"])
    
    @classmethod
    def create_log_dirs(cls):
        """Створення директорій для логів"""
        cls.LOG_DIR.mkdir(exist_ok=True)
        
        # Створюємо піддиректорії для різних типів логів
        for log_type in cls.LOG_CONFIGS.keys():
            log_dir = cls.LOG_DIR / log_type
            log_dir.mkdir(exist_ok=True)
    
    @classmethod
    def get_log_file_path(cls, log_type: str, json: bool = False) -> Path:
        """Отримання шляху до лог-файлу"""
        config = cls.get_log_config(log_type)
        
        if json:
            return config["json_file"]
        else:
            return config["file"]
    
    @classmethod
    def get_log_level(cls, log_type: str = None) -> str:
        """Отримання рівня логування"""
        if log_type:
            config = cls.get_log_config(log_type)
            return config["level"]
        else:
            return cls.LOG_LEVEL
    
    @classmethod
    def get_rotation_settings(cls, log_type: str) -> Dict[str, Any]:
        """Отримання налаштувань ротації"""
        config = cls.get_log_config(log_type)
        
        return {
            "rotation": config["rotation"],
            "retention": config["retention"],
            "compression": config["compression"]
        }


# Глобальний екземпляр конфігурації
logging_config = LoggingConfig() 