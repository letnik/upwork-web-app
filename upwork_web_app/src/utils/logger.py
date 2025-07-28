"""
Структурований логер для Upwork Web App
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from loguru import logger
from .config.logging_config import logging_config


class StructuredLogger:
    """Структурований логер для системи"""
    
    def __init__(self, log_dir: str = None):
        """Ініціалізація логера"""
        self.log_dir = log_dir or "logs"
        self.env_config = {
            "log_level": "INFO",
            "file_output": True,
            "json_output": True,
            "console_output": True
        }
        
        # Створюємо папку для логів
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Налаштовуємо loguru
        self._setup_loguru()
    
    def _setup_loguru(self):
        """Налаштування loguru"""
        # Видаляємо стандартний handler
        logger.remove()
        
        # Додаємо handlers
        self._add_app_handlers()
        self._add_error_handlers()
        self._add_security_handlers()
        self._add_console_handler()
    
    def _add_app_handlers(self):
        """Додавання handlers для загального логування додатку"""
        config = logging_config.get_log_config("app")
        
        if self.env_config["file_output"]:
            logger.add(
                config["file"],
                format=config["format"],
                level=config["level"],
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"]
            )
        
        if self.env_config["json_output"]:
            logger.add(
                config["json_file"],
                format=config["json_format"],
                level=config["level"],
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"],
                serialize=True
            )
    
    def _add_error_handlers(self):
        """Додавання handlers для помилок"""
        config = logging_config.get_log_config("error")
        
        if self.env_config["file_output"]:
            logger.add(
                config["file"],
                format=config["format"],
                level="ERROR",
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"]
            )
        
        if self.env_config["json_output"]:
            logger.add(
                config["json_file"],
                format=config["json_format"],
                level="ERROR",
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"],
                serialize=True
            )
    
    def _add_security_handlers(self):
        """Додавання handlers для безпеки"""
        config = logging_config.get_log_config("security")
        
        if self.env_config["file_output"]:
            logger.add(
                config["file"],
                format=config["format"],
                level=config["level"],
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"],
                filter=lambda record: "security" in record["extra"]
            )
        
        if self.env_config["json_output"]:
            logger.add(
                config["json_file"],
                format=config["json_format"],
                level=config["level"],
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"],
                serialize=True,
                filter=lambda record: "security" in record["extra"]
            )
    
    def _add_console_handler(self):
        """Додавання консольного handler"""
        logger.add(
            lambda msg: print(msg, end=""),
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.env_config["log_level"]
        )
    
    def log_app_event(self, 
                     event_type: str,
                     message: str,
                     data: Dict[str, Any] = None,
                     level: str = "INFO"):
        """Логування події додатку"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            "level": level,
            "data": data or {}
        }
        
        if level == "ERROR":
            logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))
    
    def log_security_event(self,
                          event_type: str,
                          message: str,
                          ip: str = None,
                          domain: str = None,
                          user_agent: str = None,
                          data: Dict[str, Any] = None):
        """Логування події безпеки"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "security",
            "security_type": event_type,
            "message": message,
            "ip": ip,
            "domain": domain,
            "user_agent": user_agent,
            "data": data or {}
        }
        
        # Використовуємо extra для фільтрації
        extra = {"security": True}
        logger.bind(**extra).warning(json.dumps(log_entry))
    
    def log_api_event(self,
                     api_endpoint: str,
                     method: str,
                     status_code: int,
                     response_time: float = None,
                     user_id: str = None,
                     data: Dict[str, Any] = None):
        """Логування API подій"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "api",
            "api_endpoint": api_endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id,
            "data": data or {}
        }
        
        level = "ERROR" if status_code >= 400 else "INFO"
        
        if level == "ERROR":
            logger.error(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))
    
    def log_rate_limit_event(self,
                           identifier: str,
                           domain: str,
                           event_type: str,
                           message: str,
                           data: Dict[str, Any] = None):
        """Логування події rate limiting"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rate_limit",
            "identifier": identifier,
            "domain": domain,
            "rate_limit_type": event_type,
            "message": message,
            "data": data or {}
        }
        
        # Використовуємо extra для фільтрації
        extra = {"security": True}
        logger.bind(**extra).warning(json.dumps(log_entry))
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Отримання статистики логів"""
        try:
            stats = {
                "total_logs": 0,
                "error_logs": 0,
                "security_logs": 0,
                "api_logs": 0,
                "log_files": [],
                "last_cleanup": None
            }
            
            # Підрахунок файлів логів
            if os.path.exists(self.log_dir):
                log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
                stats["log_files"] = log_files
                stats["total_logs"] = len(log_files)
            
            return stats
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_old_logs(self, days: int = 30):
        """Очищення старих лог файлів"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = 0
            
            if os.path.exists(self.log_dir):
                for filename in os.listdir(self.log_dir):
                    filepath = os.path.join(self.log_dir, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            deleted_count += 1
            
            return deleted_count
        except Exception as e:
            logger.error(f"Помилка очищення логів: {e}")
            return 0
    
    def export_logs(self, start_date: str = None, end_date: str = None, event_type: str = None) -> list:
        """Експорт логів з фільтрацією"""
        try:
            logs = []
            
            # TODO: Реалізувати експорт логів з фільтрацією
            # Це потребує парсингу лог файлів та фільтрації по датах/типах
            
            return logs
        except Exception as e:
            logger.error(f"Помилка експорту логів: {e}")
            return []


# Глобальний екземпляр логера
structured_logger = StructuredLogger() 