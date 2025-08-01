"""
Rate Limiter - Middleware для обмеження частоти запитів
"""

import time
import hashlib
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config.settings import settings
from shared.config.logging import get_logger

logger = get_logger("rate-limiter")


class RateLimiter:
    """Клас для обмеження частоти запитів"""
    
    def __init__(self):
        """Ініціалізація rate limiter"""
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Ініціалізація Redis підключення"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            # Тестуємо підключення
            self.redis_client.ping()
            logger.info("✅ Redis підключення успішне")
        except Exception as e:
            logger.warning(f"⚠️ Redis недоступний: {e}")
            self.redis_client = None
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Отримання ідентифікатора клієнта
        
        Args:
            request: FastAPI запит
            
        Returns:
            Унікальний ідентифікатор клієнта
        """
        # Спробуємо отримати IP адресу
        client_ip = request.client.host if request.client else "unknown"
        
        # Якщо є X-Forwarded-For заголовок (за проксі)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Якщо є X-Real-IP заголовок
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        
        # Додаємо User-Agent для більшої унікальності
        user_agent = request.headers.get("User-Agent", "")
        
        # Створюємо хеш
        identifier = f"{client_ip}:{user_agent}"
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def _get_rate_limit_key(self, identifier: str, window: str) -> str:
        """
        Створення ключа для rate limiting
        
        Args:
            identifier: Ідентифікатор клієнта
            window: Вікно часу (minute, hour, day)
            
        Returns:
            Ключ для Redis
        """
        current_time = int(time.time())
        
        if window == "minute":
            window_time = current_time - (current_time % 60)
        elif window == "hour":
            window_time = current_time - (current_time % 3600)
        elif window == "day":
            window_time = current_time - (current_time % 86400)
        else:
            window_time = current_time
        
        return f"rate_limit:{identifier}:{window}:{window_time}"
    
    def _check_rate_limit(
        self, 
        identifier: str, 
        limit: int, 
        window: str
    ) -> Tuple[bool, int, int]:
        """
        Перевірка rate limit
        
        Args:
            identifier: Ідентифікатор клієнта
            limit: Ліміт запитів
            window: Вікно часу
            
        Returns:
            (is_allowed, current_count, remaining)
        """
        if not self.redis_client:
            # Якщо Redis недоступний, дозволяємо всі запити
            return True, 0, limit
        
        key = self._get_rate_limit_key(identifier, window)
        
        try:
            # Отримуємо поточну кількість запитів
            current_count = self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            
            # Перевіряємо чи не перевищено ліміт
            if current_count >= limit:
                return False, current_count, 0
            
            # Збільшуємо лічильник
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            
            # Встановлюємо TTL для ключа
            if window == "minute":
                pipe.expire(key, 60)
            elif window == "hour":
                pipe.expire(key, 3600)
            elif window == "day":
                pipe.expire(key, 86400)
            
            pipe.execute()
            
            # Отримуємо оновлену кількість
            new_count = self.redis_client.get(key)
            new_count = int(new_count) if new_count else 1
            
            remaining = max(0, limit - new_count)
            
            return True, new_count, remaining
            
        except Exception as e:
            logger.error(f"Помилка rate limiting: {e}")
            # У випадку помилки дозволяємо запит
            return True, 0, limit
    
    async def check_request_rate_limit(self, request: Request) -> None:
        """
        Перевірка rate limit для запиту
        
        Args:
            request: FastAPI запит
            
        Raises:
            HTTPException: Якщо перевищено ліміт
        """
        identifier = self._get_client_identifier(request)
        
        # Перевіряємо різні вікна часу
        windows = [
            ("minute", settings.RATE_LIMIT_PER_MINUTE),
            ("hour", settings.RATE_LIMIT_PER_HOUR)
        ]
        
        for window, limit in windows:
            is_allowed, current_count, remaining = self._check_rate_limit(
                identifier, limit, window
            )
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded: {identifier} - {current_count}/{limit} "
                    f"requests per {window}"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "window": window,
                        "limit": limit,
                        "current": current_count,
                        "retry_after": self._get_retry_after(window)
                    }
                )
        
        # Додаємо заголовки з інформацією про rate limit
        request.state.rate_limit_info = {
            "identifier": identifier,
            "remaining_minute": remaining,
            "remaining_hour": remaining
        }
    
    def _get_retry_after(self, window: str) -> int:
        """Отримання часу очікування для retry"""
        if window == "minute":
            return 60
        elif window == "hour":
            return 3600
        else:
            return 60
    
    def allow_request(self, key: str, max_requests: int, window: int) -> bool:
        """
        Простий метод для перевірки rate limit
        
        Args:
            key: Унікальний ключ для rate limiting
            max_requests: Максимальна кількість запитів
            window: Вікно часу в секундах
            
        Returns:
            True якщо запит дозволений, False якщо перевищено ліміт
        """
        if not self.redis_client:
            # Якщо Redis недоступний, дозволяємо всі запити
            return True
        
        current_time = int(time.time())
        window_time = current_time - (current_time % window)
        redis_key = f"rate_limit:{key}:{window_time}"
        
        try:
            # Отримуємо поточну кількість запитів
            current_count = self.redis_client.get(redis_key)
            current_count = int(current_count) if current_count else 0
            
            # Перевіряємо чи не перевищено ліміт
            if current_count >= max_requests:
                return False
            
            # Збільшуємо лічильник
            pipe = self.redis_client.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, window)
            pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Помилка rate limiting: {e}")
            # У випадку помилки дозволяємо запит
            return True


# Глобальний екземпляр rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware для rate limiting
    
    Args:
        request: FastAPI запит
        call_next: Наступна функція в ланцюжку
        
    Returns:
        FastAPI відповідь
    """
    try:
        # Перевіряємо rate limit
        await rate_limiter.check_request_rate_limit(request)
        
        # Виконуємо запит
        response = await call_next(request)
        
        # Додаємо заголовки з інформацією про rate limit
        if hasattr(request.state, 'rate_limit_info'):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Remaining-Minute"] = str(info.get("remaining_minute", 0))
            response.headers["X-RateLimit-Remaining-Hour"] = str(info.get("remaining_hour", 0))
        
        return response
        
    except HTTPException as e:
        if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            # Додаємо заголовок Retry-After
            retry_after = e.detail.get("retry_after", 60) if isinstance(e.detail, dict) else 60
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        raise


def get_rate_limiter() -> RateLimiter:
    """Отримання екземпляра rate limiter"""
    return rate_limiter 