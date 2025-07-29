"""
Validation Middleware - Middleware для валідації вхідних даних
"""

import re
import json
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from config.settings import settings
from config.logging import get_logger

logger = get_logger("validation-middleware")


class ValidationMiddleware:
    """Клас для валідації вхідних даних"""
    
    def __init__(self):
        """Ініціалізація middleware"""
        # Патерни для виявлення підозрілого контенту
        self.suspicious_patterns = [
            # SQL Injection
            r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
            r"(\b(or|and)\b\s+\d+\s*=\s*\d+)",
            r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(union|select|insert|update|delete|drop|create|alter)\b)",
            
            # XSS атаки
            r"(<script[^>]*>.*?</script>)",
            r"(javascript:)",
            r"(on\w+\s*=)",
            r"(<iframe[^>]*>)",
            r"(<object[^>]*>)",
            r"(<embed[^>]*>)",
            
            # Path traversal
            r"(\.\./)",
            r"(\.\.\\)",
            
            # Command injection
            r"(\b(cmd|command|exec|system|eval|exec)\b)",
            
            # NoSQL injection
            r"(\$where)",
            r"(\$ne)",
            r"(\$gt)",
            r"(\$lt)",
            
            # LDAP injection
            r"(\*\)|\(\|)",
            
            # XML injection
            r"(<!\[CDATA\[)",
            r"(<!DOCTYPE)",
            
            # Template injection
            r"(\{\{.*\}\})",
            r"(\{%.*%\})",
            
            # File inclusion
            r"(php://)",
            r"(file://)",
            r"(data://)",
        ]
        
        # Компілюємо патерни
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        
        # Максимальний розмір тіла запиту (10MB)
        self.max_content_length = 10 * 1024 * 1024
        
        # Дозволені Content-Type
        self.allowed_content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ]
    
    def _check_content_length(self, request: Request) -> bool:
        """
        Перевірка розміру тіла запиту
        
        Args:
            request: FastAPI запит
            
        Returns:
            True якщо розмір допустимий
        """
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_content_length:
                    return False
            except ValueError:
                return False
        return True
    
    def _check_content_type(self, request: Request) -> bool:
        """
        Перевірка Content-Type
        
        Args:
            request: FastAPI запит
            
        Returns:
            True якщо Content-Type допустимий
        """
        content_type = request.headers.get("content-type", "")
        
        # Для multipart/form-data дозволяємо додаткові параметри
        if content_type.startswith("multipart/form-data"):
            return True
        
        # Для інших типів перевіряємо точний збіг
        for allowed_type in self.allowed_content_types:
            if content_type == allowed_type:
                return True
        
        return False
    
    def _check_suspicious_content(self, content: str) -> Optional[str]:
        """
        Перевірка на підозрілий контент
        
        Args:
            content: Контент для перевірки
            
        Returns:
            Знайдений підозрілий патерн або None
        """
        for pattern in self.compiled_patterns:
            match = pattern.search(content)
            if match:
                return match.group(0)
        return None
    
    def _validate_json_body(self, body: str) -> Dict[str, Any]:
        """
        Валідація JSON тіла запиту
        
        Args:
            body: JSON рядок
            
        Returns:
            Парсений JSON
            
        Raises:
            HTTPException: Якщо JSON невірний
        """
        try:
            # Перевіряємо на підозрілий контент
            suspicious = self._check_suspicious_content(body)
            if suspicious:
                logger.warning(f"Підозрілий контент в JSON: {suspicious}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недопустимий контент в запиті"
                )
            
            # Парсимо JSON
            data = json.loads(body)
            
            # Перевіряємо глибину об'єкта (не більше 10 рівнів)
            if self._get_object_depth(data) > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Занадто глибокий JSON об'єкт"
                )
            
            return data
            
        except json.JSONDecodeError as e:
            logger.warning(f"Невірний JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний JSON формат"
            )
    
    def _get_object_depth(self, obj: Any, current_depth: int = 0) -> int:
        """
        Отримання глибини об'єкта
        
        Args:
            obj: Об'єкт для перевірки
            current_depth: Поточна глибина
            
        Returns:
            Максимальна глибина об'єкта
        """
        if current_depth > 10:
            return current_depth
        
        if isinstance(obj, dict):
            max_depth = current_depth
            for value in obj.values():
                depth = self._get_object_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            return max_depth
        elif isinstance(obj, list):
            max_depth = current_depth
            for item in obj:
                depth = self._get_object_depth(item, current_depth + 1)
                max_depth = max(max_depth, depth)
            return max_depth
        else:
            return current_depth
    
    def _validate_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валідація query параметрів
        
        Args:
            params: Query параметри
            
        Returns:
            Валідовані параметри
            
        Raises:
            HTTPException: Якщо параметри невірні
        """
        validated_params = {}
        
        for key, value in params.items():
            # Перевіряємо довжину ключа
            if len(key) > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Занадто довгий ключ параметра"
                )
            
            # Перевіряємо довжину значення
            if isinstance(value, str) and len(value) > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Занадто довге значення параметра"
                )
            
            # Перевіряємо на підозрілий контент
            if isinstance(value, str):
                suspicious = self._check_suspicious_content(value)
                if suspicious:
                    logger.warning(f"Підозрілий контент в query параметрі: {suspicious}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Недопустимий контент в параметрах"
                    )
            
            validated_params[key] = value
        
        return validated_params
    
    async def validate_request(self, request: Request) -> None:
        """
        Валідація запиту
        
        Args:
            request: FastAPI запит
            
        Raises:
            HTTPException: Якщо запит невірний
        """
        # Перевіряємо розмір тіла
        if not self._check_content_length(request):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Занадто великий розмір запиту"
            )
        
        # Перевіряємо Content-Type
        if request.method in ["POST", "PUT", "PATCH"]:
            if not self._check_content_type(request):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Непідтримуваний тип контенту"
                )
        
        # Перевіряємо query параметри
        if request.query_params:
            query_dict = dict(request.query_params)
            validated_query = self._validate_query_params(query_dict)
            request.state.validated_query = validated_query
        
        # Перевіряємо тіло запиту для JSON
        if request.headers.get("content-type") == "application/json":
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")
                    validated_body = self._validate_json_body(body_str)
                    request.state.validated_body = validated_body
            except Exception as e:
                logger.error(f"Помилка валідації тіла запиту: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Помилка валідації тіла запиту"
                )


# Глобальний екземпляр middleware
validation_middleware = ValidationMiddleware()


async def validation_middleware_handler(request: Request, call_next):
    """
    Middleware handler для валідації
    
    Args:
        request: FastAPI запит
        call_next: Наступна функція в ланцюжку
        
    Returns:
        FastAPI відповідь
    """
    try:
        # Валідуємо запит
        await validation_middleware.validate_request(request)
        
        # Виконуємо запит
        response = await call_next(request)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка валідації: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка валідації запиту"
        )


def get_validation_middleware() -> ValidationMiddleware:
    """Отримання екземпляра validation middleware"""
    return validation_middleware 