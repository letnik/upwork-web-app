"""
Розширена конфігурація логування для всіх мікросервісів
"""

import logging
import sys
import json
import traceback
import time
import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any, Union
from contextvars import ContextVar
from loguru import logger
from .settings import settings
from .logging_config import (
    get_logging_config, 
    LOG_TYPES, 
    LOG_FILTERS, 
    ENVIRONMENT_CONFIGS
)

# Контекстні змінні для зберігання інформації про запит
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)
test_context_var: ContextVar[Optional[str]] = ContextVar('test_context', default=None)


class StructuredLogger:
    """Розширений логер з структурованими логами"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(module=name)
    
    def _get_context(self) -> Dict[str, Any]:
        """Отримання контекстної інформації"""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.SERVICE_NAME,
            "environment": settings.ENVIRONMENT,
            "module": self.name
        }
        
        # Додаємо request_id якщо є
        request_id = request_id_var.get()
        if request_id:
            context["request_id"] = request_id
        
        # Додаємо user_id якщо є
        user_id = user_id_var.get()
        if user_id:
            context["user_id"] = user_id
        
        # Додаємо session_id якщо є
        session_id = session_id_var.get()
        if session_id:
            context["session_id"] = session_id
        
        # Додаємо test_context якщо є (для тестів)
        test_context = test_context_var.get()
        if test_context:
            context["test_context"] = test_context
        
        return context
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Форматування повідомлення з контекстом"""
        context = self._get_context()
        if extra:
            context.update(extra)
        
        return json.dumps({
            "message": message,
            "context": context
        }, ensure_ascii=False, default=str)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Логування інформації"""
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Логування попереджень"""
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """Логування помилок з детальною інформацією"""
        error_context = extra or {}
        
        if exc_info:
            error_context.update({
                "traceback": traceback.format_exc(),
                "exception_type": sys.exc_info()[0].__name__ if sys.exc_info()[0] else None,
                "exception_message": str(sys.exc_info()[1]) if sys.exc_info()[1] else None
            })
        
        self.logger.error(self._format_message(message, error_context))
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Логування для дебагу"""
        self.logger.debug(self._format_message(message, extra))
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Логування критичних помилок"""
        self.logger.critical(self._format_message(message, extra))
    
    def performance(self, operation: str, duration: float, extra: Optional[Dict[str, Any]] = None):
        """Логування метрик продуктивності"""
        perf_context = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "performance_category": "slow" if duration > 1.0 else "normal" if duration > 0.1 else "fast"
        }
        if extra:
            perf_context.update(extra)
        
        self.logger.info(self._format_message(f"Performance: {operation}", perf_context))
    
    def security(self, event: str, extra: Optional[Dict[str, Any]] = None):
        """Логування подій безпеки"""
        security_context = {
            "security_event": event,
            "ip_address": extra.get("ip_address") if extra else None,
            "user_agent": extra.get("user_agent") if extra else None
        }
        if extra:
            security_context.update(extra)
        
        self.logger.warning(self._format_message(f"Security: {event}", security_context))
    
    def api_call(self, method: str, endpoint: str, status_code: int, duration: float, extra: Optional[Dict[str, Any]] = None):
        """Логування API викликів"""
        api_context = {
            "api_method": method,
            "api_endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "success": 200 <= status_code < 400
        }
        if extra:
            api_context.update(extra)
        
        level = "error" if status_code >= 400 else "info"
        getattr(self.logger, level)(self._format_message(f"API: {method} {endpoint}", api_context))
    
    def database(self, operation: str, table: str, duration: float, rows_affected: Optional[int] = None, extra: Optional[Dict[str, Any]] = None):
        """Логування операцій з базою даних"""
        db_context = {
            "db_operation": operation,
            "db_table": table,
            "duration_ms": round(duration * 1000, 2),
            "rows_affected": rows_affected
        }
        if extra:
            db_context.update(extra)
        
        self.logger.info(self._format_message(f"Database: {operation} on {table}", db_context))
    
    def test(self, test_name: str, status: str, duration: float = None, extra: Optional[Dict[str, Any]] = None):
        """Логування тестів"""
        test_context = {
            "test_name": test_name,
            "test_status": status,
            "test_duration_ms": round(duration * 1000, 2) if duration else None
        }
        if extra:
            test_context.update(extra)
        
        level = "error" if status == "FAILED" else "info"
        getattr(self.logger, level)(self._format_message(f"Test: {test_name} - {status}", test_context))


def setup_logging(
    service_name: Optional[str] = None,
    log_level: Optional[str] = None,
    test_mode: bool = False
) -> None:
    """
    Розширене налаштування логування для сервісу
    
    Args:
        service_name: Назва сервісу
        log_level: Рівень логування
        test_mode: Режим тестування
    """
    
    # Отримуємо конфігурацію
    config = get_logging_config(service_name, log_level)
    
    # Визначаємо чи це тестовий режим
    is_testing = test_mode or config.is_test_environment()
    
    # Видаляємо стандартний handler
    logger.remove()
    
    # Отримуємо конфігурацію середовища
    env_config = ENVIRONMENT_CONFIGS.get(config.environment, ENVIRONMENT_CONFIGS["development"])
    
    # Додаємо console handler з кольорами
    if env_config["console_output"]:
        logger.add(
            sys.stdout,
            format=config.console_format,
            level=config.log_level,
            colorize=env_config["colorize"],
            backtrace=True,
            diagnose=True,
            enqueue=True
        )
    
    # Створюємо директорію для логів
    base_log_dir = config.test_logs_directory if is_testing else config.logs_directory
    os.makedirs(base_log_dir, exist_ok=True)
    
    # Додаємо handlers для різних типів логів
    _add_log_handlers(config, is_testing)


def _add_log_handlers(config, is_testing: bool):
    """Додавання handlers для різних типів логів"""
    
    # Основні логи
    _add_handler(config, "main", "INFO", is_testing)
    
    # Помилки
    _add_handler(config, "error", "ERROR", is_testing)
    
    # Безпека
    _add_handler(config, "security", "WARNING", is_testing, LOG_FILTERS["security"])
    
    # Продуктивність
    _add_handler(config, "performance", "INFO", is_testing, LOG_FILTERS["performance"])
    
    # API
    _add_handler(config, "api", "INFO", is_testing, LOG_FILTERS["api"])
    
    # База даних
    _add_handler(config, "database", "INFO", is_testing, LOG_FILTERS["database"])
    
    # Тести (тільки в тестовому режимі)
    if is_testing:
        _add_handler(config, "test", "INFO", is_testing, LOG_FILTERS["test"])


def _add_handler(config, log_type: str, level: str, is_testing: bool, filter_func=None):
    """Додавання окремого handler"""
    file_path = config.get_log_file_path(log_type, is_testing)
    rotation_config = config.get_rotation_config(log_type)
    
    logger.add(
        file_path,
        format=config.file_format,
        level=level,
        filter=filter_func,
        rotation=rotation_config["rotation"],
        retention=rotation_config["retention"],
        compression=rotation_config["compression"],
        enqueue=True,
        encoding="utf-8"
    )


def get_logger(name: str) -> StructuredLogger:
    """
    Отримання розширеного логера для конкретного модуля
    
    Args:
        name: Назва модуля
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


def set_request_context(request_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None):
    """Встановлення контексту запиту"""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if session_id:
        session_id_var.set(session_id)


def clear_request_context():
    """Очищення контексту запиту"""
    request_id_var.set(None)
    user_id_var.set(None)
    session_id_var.set(None)


def set_test_context(test_name: str, test_file: str = None):
    """Встановлення контексту тесту"""
    test_context = {
        "test_name": test_name,
        "test_file": test_file,
        "timestamp": datetime.utcnow().isoformat()
    }
    test_context_var.set(json.dumps(test_context))


def clear_test_context():
    """Очищення контексту тесту"""
    test_context_var.set(None)


def generate_request_id() -> str:
    """Генерація унікального ID для запиту"""
    return str(uuid.uuid4())


class PerformanceLogger:
    """Контекстний менеджер для логування продуктивності"""
    
    def __init__(self, logger: StructuredLogger, operation: str, extra: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.operation = operation
        self.extra = extra
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.logger.performance(self.operation, duration, self.extra)


class TestLogger:
    """Контекстний менеджер для логування тестів"""
    
    def __init__(self, logger: StructuredLogger, test_name: str, test_file: str = None):
        self.logger = logger
        self.test_name = test_name
        self.test_file = test_file
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        set_test_context(self.test_name, self.test_file)
        self.logger.test(self.test_name, "STARTED")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "FAILED" if exc_type else "PASSED"
        self.logger.test(self.test_name, status, duration, {
            "test_file": self.test_file,
            "exception": str(exc_val) if exc_val else None
        })
        clear_test_context()


class InterceptHandler(logging.Handler):
    """Handler для перехоплення стандартних логів Python"""
    
    def emit(self, record):
        # Отримуємо відповідний Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Знаходимо caller
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def intercept_standard_logging():
    """Перехоплення стандартних логів Python"""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Перехоплюємо логи від uvicorn та інших бібліотек
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True 