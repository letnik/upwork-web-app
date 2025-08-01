"""
Декоратори для автоматичного логування
"""

import time
import functools
import traceback
from typing import Dict, Any, Optional, Callable, TypeVar
try:
    from typing import ParamSpec
except ImportError:
    # Для Python < 3.10
    from typing_extensions import ParamSpec
from shared.config.logging import get_logger, PerformanceLogger

P = ParamSpec('P')
T = TypeVar('T')


def log_function_call(logger_name: str = None):
    """
    Декоратор для логування викликів функцій
    
    Args:
        logger_name: Назва логера (за замовчуванням використовується назва модуля)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            # Логуємо початок виклику
            func_name = func.__name__
            logger.debug(
                f"Function call started: {func_name}",
                extra={
                    "function": func_name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()) if kwargs else []
                }
            )
            
            start_time = time.time()
            
            try:
                # Виконуємо функцію
                result = func(*args, **kwargs)
                
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Логуємо успішне завершення
                logger.debug(
                    f"Function call completed: {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration * 1000, 2),
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Логуємо помилку
                logger.error(
                    f"Function call failed: {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration * 1000, 2),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "success": False
                    }
                )
                
                raise
        
        return wrapper
    return decorator


def log_performance(operation_name: str = None, logger_name: str = None):
    """
    Декоратор для логування продуктивності функцій
    
    Args:
        operation_name: Назва операції (за замовчуванням використовується назва функції)
        logger_name: Назва логера
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            # Назва операції
            op_name = operation_name or func.__name__
            
            # Використовуємо контекстний менеджер для логування продуктивності
            with PerformanceLogger(logger, op_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_database_operation(table: str, operation: str = None, logger_name: str = None):
    """
    Декоратор для логування операцій з базою даних
    
    Args:
        table: Назва таблиці
        operation: Тип операції (SELECT, INSERT, UPDATE, DELETE)
        logger_name: Назва логера
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            # Тип операції
            op_type = operation or func.__name__.upper()
            
            start_time = time.time()
            
            try:
                # Виконуємо операцію
                result = func(*args, **kwargs)
                
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Логуємо операцію з базою даних
                logger.database(
                    operation=op_type,
                    table=table,
                    duration=duration,
                    extra={
                        "function": func.__name__,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Логуємо помилку
                logger.error(
                    f"Database operation failed: {op_type} on {table}",
                    extra={
                        "db_operation": op_type,
                        "db_table": table,
                        "duration_ms": round(duration * 1000, 2),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "function": func.__name__
                    }
                )
                
                raise
        
        return wrapper
    return decorator


def log_api_call(endpoint: str = None, method: str = None, logger_name: str = None):
    """
    Декоратор для логування API викликів
    
    Args:
        endpoint: Endpoint API
        method: HTTP метод
        logger_name: Назва логера
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            # Endpoint та метод
            api_endpoint = endpoint or func.__name__
            http_method = method or "GET"
            
            start_time = time.time()
            
            try:
                # Виконуємо API виклик
                result = func(*args, **kwargs)
                
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Припускаємо успішний статус (200)
                status_code = 200
                
                # Логуємо API виклик
                logger.api_call(
                    method=http_method,
                    endpoint=api_endpoint,
                    status_code=status_code,
                    duration=duration,
                    extra={
                        "function": func.__name__,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Припускаємо помилку сервера (500)
                status_code = 500
                
                # Логуємо помилку API
                logger.api_call(
                    method=http_method,
                    endpoint=api_endpoint,
                    status_code=status_code,
                    duration=duration,
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "success": False
                    }
                )
                
                raise
        
        return wrapper
    return decorator


def log_security_event(event_type: str, logger_name: str = None):
    """
    Декоратор для логування подій безпеки
    
    Args:
        event_type: Тип події безпеки
        logger_name: Назва логера
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            try:
                # Виконуємо функцію
                result = func(*args, **kwargs)
                
                # Логуємо подію безпеки
                logger.security(
                    event=event_type,
                    extra={
                        "function": func.__name__,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                # Логуємо помилку безпеки
                logger.security(
                    event=f"{event_type}_failed",
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "success": False
                    }
                )
                
                raise
        
        return wrapper
    return decorator


def log_exceptions(logger_name: str = None, reraise: bool = True):
    """
    Декоратор для логування винятків
    
    Args:
        logger_name: Назва логера
        reraise: Чи перекидати виняток після логування
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Логуємо виняток з детальною інформацією
                logger.error(
                    f"Exception in {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()) if kwargs else [],
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "traceback": traceback.format_exc()
                    }
                )
                
                if reraise:
                    raise
        
        return wrapper
    return decorator


def log_async_function(logger_name: str = None):
    """
    Декоратор для логування асинхронних функцій
    
    Args:
        logger_name: Назва логера
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Отримуємо логер
            module_name = logger_name or func.__module__
            logger = get_logger(module_name)
            
            # Логуємо початок виклику
            func_name = func.__name__
            logger.debug(
                f"Async function call started: {func_name}",
                extra={
                    "function": func_name,
                    "async": True,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()) if kwargs else []
                }
            )
            
            start_time = time.time()
            
            try:
                # Виконуємо асинхронну функцію
                result = await func(*args, **kwargs)
                
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Логуємо успішне завершення
                logger.debug(
                    f"Async function call completed: {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration * 1000, 2),
                        "async": True,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                # Розраховуємо тривалість
                duration = time.time() - start_time
                
                # Логуємо помилку
                logger.error(
                    f"Async function call failed: {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration * 1000, 2),
                        "async": True,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "success": False
                    }
                )
                
                raise
        
        return wrapper
    return decorator 