"""
Спільна конфігурація логування для всіх мікросервісів
"""

import logging
import sys
from typing import Optional
from loguru import logger
from .settings import settings


def setup_logging(
    service_name: Optional[str] = None,
    log_level: Optional[str] = None
) -> None:
    """
    Налаштування логування для сервісу
    
    Args:
        service_name: Назва сервісу
        log_level: Рівень логування
    """
    
    # Використовуємо налаштування з конфігурації або передані параметри
    service_name = service_name or settings.SERVICE_NAME
    log_level = log_level or settings.LOG_LEVEL
    
    # Видаляємо стандартний handler
    logger.remove()
    
    # Додаємо console handler
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Додаємо file handler для production
    if settings.ENVIRONMENT == "production":
        logger.add(
            f"logs/{service_name}.log",
            format=settings.LOG_FORMAT,
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    # Додаємо error handler
    logger.add(
        f"logs/{service_name}_error.log",
        format=settings.LOG_FORMAT,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )


def get_logger(name: str) -> logger:
    """
    Отримання логера для конкретного модуля
    
    Args:
        name: Назва модуля
        
    Returns:
        Logger instance
    """
    return logger.bind(module=name)


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
    
    # Перехоплюємо логи від uvicorn
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True 