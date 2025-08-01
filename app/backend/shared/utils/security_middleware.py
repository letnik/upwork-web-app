"""
Middleware для автоматичного логування безпеки
SECURITY-008: Логування безпеки та моніторинг
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .security_logger import (
    SecurityLogger, SecurityEventType, SecurityLevel,
    log_api_access, log_rate_limit
)
from .rate_limiter import RateLimiter


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматичного логування безпеки"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_logger = SecurityLogger()
        self.rate_limiter = RateLimiter()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обробляє запит з логуванням безпеки"""
        start_time = time.time()
        
        # Отримуємо інформацію про запит
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        endpoint = str(request.url.path)
        method = request.method
        
        # Перевіряємо rate limiting
        rate_limit_result = await self._check_rate_limit(request, ip_address, endpoint)
        
        # Виконуємо запит
        try:
            response = await call_next(request)
            success = response.status_code < 400
        except Exception as e:
            success = False
            raise e
        finally:
            # Обчислюємо час відповіді
            response_time = time.time() - start_time
            
            # Логуємо доступ до API
            await self._log_api_access(
                request, ip_address, endpoint, method, 
                response_time, success, rate_limit_result
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Отримує IP адресу клієнта"""
        # Перевіряємо заголовки проксі
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Повертаємо IP з request
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limit(self, request: Request, ip_address: str, endpoint: str) -> dict:
        """Перевіряє rate limiting"""
        try:
            # Отримуємо користувача з токена (якщо є)
            user_id = await self._get_user_id_from_request(request)
            
            # Перевіряємо rate limit
            is_allowed = self.rate_limiter.is_allowed(ip_address, endpoint)
            
            if not is_allowed:
                # Логуємо перевищення rate limit
                log_rate_limit(ip_address, endpoint, self.rate_limiter.requests_per_minute)
            
            return {
                "is_allowed": is_allowed,
                "user_id": user_id,
                "limit_exceeded": not is_allowed
            }
            
        except Exception as e:
            # У випадку помилки дозволяємо запит
            return {
                "is_allowed": True,
                "user_id": None,
                "limit_exceeded": False,
                "error": str(e)
            }
    
    async def _get_user_id_from_request(self, request: Request) -> int:
        """Отримує ID користувача з запиту"""
        try:
            # Тут можна додати логіку отримання користувача з JWT токена
            # Поки що повертаємо None
            return None
        except Exception:
            return None
    
    async def _log_api_access(self, request: Request, ip_address: str, endpoint: str,
                             method: str, response_time: float, success: bool, 
                             rate_limit_result: dict) -> None:
        """Логує доступ до API"""
        try:
            user_id = rate_limit_result.get("user_id")
            
            # Логуємо тільки успішні запити або помилки
            if success or response_time > 1.0:  # Повільні запити
                log_api_access(
                    user_id=user_id or 0,
                    endpoint=endpoint,
                    method=method,
                    ip_address=ip_address,
                    response_time=response_time
                )
            
            # Логуємо підозрілу активність
            if self._is_suspicious_activity(request, response_time, rate_limit_result):
                self.security_logger.log_event(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=request.headers.get("user-agent", ""),
                    details={
                        "endpoint": endpoint,
                        "method": method,
                        "response_time": response_time,
                        "rate_limit_exceeded": rate_limit_result.get("limit_exceeded", False)
                    },
                    level=SecurityLevel.WARNING,
                    success=False
                )
                
        except Exception as e:
            # Логуємо помилку логування
            self.security_logger.logger.error(f"Помилка логування API доступу: {e}")
    
    def _is_suspicious_activity(self, request: Request, response_time: float, 
                               rate_limit_result: dict) -> bool:
        """Перевіряє чи є підозріла активність"""
        # Повільні запити (> 5 секунд)
        if response_time > 5.0:
            return True
        
        # Перевищення rate limit
        if rate_limit_result.get("limit_exceeded", False):
            return True
        
        # Підозрілі User-Agent
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["bot", "crawler", "scraper", "spider"]
        if any(agent in user_agent for agent in suspicious_agents):
            return True
        
        # Підозрілі endpoints
        suspicious_endpoints = ["/admin", "/config", "/debug", "/test"]
        if any(endpoint in str(request.url.path) for endpoint in suspicious_endpoints):
            return True
        
        return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для додавання заголовків безпеки"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Додає заголовки безпеки до відповіді"""
        response = await call_next(request)
        
        # Додаємо заголовки безпеки
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (тільки для HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Middleware для аудиту безпеки"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_logger = SecurityLogger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Виконує аудит безпеки"""
        # Логуємо важливі події
        await self._audit_request(request)
        
        response = await call_next(request)
        
        # Логуємо важливі відповіді
        await self._audit_response(request, response)
        
        return response
    
    async def _audit_request(self, request: Request) -> None:
        """Аудит запиту"""
        # Логуємо доступ до чутливих endpoints
        sensitive_endpoints = ["/auth", "/admin", "/api/v1/users", "/api/v1/security"]
        if any(endpoint in str(request.url.path) for endpoint in sensitive_endpoints):
            self.security_logger.log_event(
                event_type=SecurityEventType.DATA_ACCESS,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent", ""),
                details={
                    "endpoint": str(request.url.path),
                    "method": request.method,
                    "query_params": str(request.query_params)
                },
                level=SecurityLevel.INFO
            )
    
    async def _audit_response(self, request: Request, response: Response) -> None:
        """Аудит відповіді"""
        # Логуємо помилки сервера
        if response.status_code >= 500:
            self.security_logger.log_event(
                event_type=SecurityEventType.SECURITY_ALERT,
                ip_address=self._get_client_ip(request),
                details={
                    "endpoint": str(request.url.path),
                    "status_code": response.status_code,
                    "error": "Server error"
                },
                level=SecurityLevel.ERROR,
                success=False
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Отримує IP адресу клієнта"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown" 