"""
Middleware для автоматичного логування запитів
"""

import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp

from shared.config.logging import (
    get_logger, 
    set_request_context, 
    clear_request_context, 
    generate_request_id
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логування всіх HTTP запитів"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("http-middleware")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Генеруємо унікальний ID для запиту
        request_id = generate_request_id()
        
        # Отримуємо інформацію про користувача з заголовків або токена
        user_id = self._extract_user_id(request)
        session_id = self._extract_session_id(request)
        
        # Встановлюємо контекст запиту
        set_request_context(request_id, user_id, session_id)
        
        # Логуємо початок запиту
        start_time = time.time()
        
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": self._sanitize_headers(dict(request.headers)),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "content_length": request.headers.get("content-length"),
            "request_id": request_id
        }
        
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra=request_data
        )
        
        try:
            # Виконуємо запит
            response = await call_next(request)
            
            # Розраховуємо тривалість
            duration = time.time() - start_time
            
            # Логуємо успішний запит
            response_data = {
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "response_headers": dict(response.headers),
                "content_length": response.headers.get("content-length"),
                "request_id": request_id
            }
            
            self.logger.api_call(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
                extra=response_data
            )
            
            # Додаємо request_id до заголовків відповіді
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Розраховуємо тривалість
            duration = time.time() - start_time
            
            # Логуємо помилку
            error_data = {
                "method": request.method,
                "url": str(request.url),
                "duration_ms": round(duration * 1000, 2),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "request_id": request_id
            }
            
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra=error_data
            )
            
            raise
        finally:
            # Очищуємо контекст запиту
            clear_request_context()
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Витягування ID користувача з заголовків або токена"""
        # Спробуємо отримати з заголовка
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return user_id
        
        # Спробуємо отримати з Authorization заголовка
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Тут можна додати логіку декодування JWT токена
            # для отримання user_id
            pass
        
        return None
    
    def _extract_session_id(self, request: Request) -> Optional[str]:
        """Витягування ID сесії з заголовків або cookies"""
        # Спробуємо отримати з заголовка
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            return session_id
        
        # Спробуємо отримати з cookies
        session_id = request.cookies.get("session_id")
        if session_id:
            return session_id
        
        return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Отримання IP адреси клієнта"""
        # Перевіряємо різні заголовки для отримання реального IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Очищення заголовків від чутливої інформації"""
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "x-password", "x-secret", "x-token"
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized


class DatabaseLoggingMiddleware:
    """Middleware для логування операцій з базою даних"""
    
    def __init__(self):
        self.logger = get_logger("database-middleware")
    
    def log_query(self, operation: str, table: str, duration: float, 
                  rows_affected: Optional[int] = None, query: Optional[str] = None,
                  extra: Optional[Dict[str, Any]] = None):
        """Логування SQL запиту"""
        query_data = {
            "query": query[:200] + "..." if query and len(query) > 200 else query,
            "rows_affected": rows_affected
        }
        if extra:
            query_data.update(extra)
        
        self.logger.database(
            operation=operation,
            table=table,
            duration=duration,
            rows_affected=rows_affected,
            extra=query_data
        )


class SecurityLoggingMiddleware:
    """Middleware для логування подій безпеки"""
    
    def __init__(self):
        self.logger = get_logger("security-middleware")
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str, 
                         user_agent: str, extra: Optional[Dict[str, Any]] = None):
        """Логування спроби входу"""
        event = "login_success" if success else "login_failed"
        security_data = {
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success
        }
        if extra:
            security_data.update(extra)
        
        self.logger.security(event, security_data)
    
    def log_unauthorized_access(self, endpoint: str, method: str, ip_address: str,
                               user_agent: str, reason: str, extra: Optional[Dict[str, Any]] = None):
        """Логування неавторизованого доступу"""
        security_data = {
            "endpoint": endpoint,
            "method": method,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "reason": reason
        }
        if extra:
            security_data.update(extra)
        
        self.logger.security("unauthorized_access", security_data)
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str, 
                               limit: int, window: str, extra: Optional[Dict[str, Any]] = None):
        """Логування перевищення ліміту запитів"""
        security_data = {
            "ip_address": ip_address,
            "endpoint": endpoint,
            "limit": limit,
            "window": window
        }
        if extra:
            security_data.update(extra)
        
        self.logger.security("rate_limit_exceeded", security_data)
    
    def log_suspicious_activity(self, activity_type: str, ip_address: str,
                               details: str, extra: Optional[Dict[str, Any]] = None):
        """Логування підозрілої активності"""
        security_data = {
            "activity_type": activity_type,
            "ip_address": ip_address,
            "details": details
        }
        if extra:
            security_data.update(extra)
        
        self.logger.security("suspicious_activity", security_data) 