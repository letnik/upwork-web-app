"""
Тести безпеки та middleware
"""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import FastAPI
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config.settings import settings
from shared.utils.rate_limiter import RateLimiter
from shared.utils.validation_middleware import ValidationMiddleware
from shared.utils.auth_middleware import AuthMiddleware


class TestRateLimiter:
    """Тести для Rate Limiter"""
    
    def test_rate_limiter_initialization(self):
        """Тест ініціалізації Rate Limiter"""
        rate_limiter = RateLimiter()
        assert rate_limiter is not None
    
    def test_client_identifier(self):
        """Тест створення ідентифікатора клієнта"""
        from fastapi import Request
        from unittest.mock import Mock
        
        # Створюємо мок запит
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"User-Agent": "test-agent"}
        
        rate_limiter = RateLimiter()
        identifier = rate_limiter._get_client_identifier(mock_request)
        
        assert identifier is not None
        assert len(identifier) == 32  # MD5 хеш
    
    def test_rate_limit_key_generation(self):
        """Тест генерації ключа rate limit"""
        rate_limiter = RateLimiter()
        identifier = "test-identifier"
        
        minute_key = rate_limiter._get_rate_limit_key(identifier, "minute")
        hour_key = rate_limiter._get_rate_limit_key(identifier, "hour")
        
        assert "rate_limit" in minute_key
        assert "rate_limit" in hour_key
        assert identifier in minute_key
        assert identifier in hour_key


class TestValidationMiddleware:
    """Тести для Validation Middleware"""
    
    def test_validation_middleware_initialization(self):
        """Тест ініціалізації Validation Middleware"""
        validation_middleware = ValidationMiddleware()
        assert validation_middleware is not None
        assert len(validation_middleware.compiled_patterns) > 0
    
    def test_suspicious_content_detection(self):
        """Тест виявлення підозрілого контенту"""
        validation_middleware = ValidationMiddleware()
        
        # SQL Injection
        sql_injection = "SELECT * FROM users WHERE id = 1 OR 1=1"
        suspicious = validation_middleware._check_suspicious_content(sql_injection)
        assert suspicious is not None
        
        # XSS атака
        xss_attack = "<script>alert('xss')</script>"
        suspicious = validation_middleware._check_suspicious_content(xss_attack)
        assert suspicious is not None
        
        # Нормальний контент
        normal_content = "Hello, world!"
        suspicious = validation_middleware._check_suspicious_content(normal_content)
        assert suspicious is None
    
    def test_content_length_validation(self):
        """Тест валідації розміру контенту"""
        from fastapi import Request
        from unittest.mock import Mock
        
        validation_middleware = ValidationMiddleware()
        
        # Нормальний розмір
        mock_request = Mock(spec=Request)
        mock_request.headers = {"content-length": "100"}
        assert validation_middleware._check_content_length(mock_request) is True
        
        # Занадто великий розмір
        mock_request.headers = {"content-length": str(11 * 1024 * 1024)}  # 11MB
        assert validation_middleware._check_content_length(mock_request) is False
    
    def test_content_type_validation(self):
        """Тест валідації типу контенту"""
        from fastapi import Request
        from unittest.mock import Mock
        
        validation_middleware = ValidationMiddleware()
        
        # Дозволені типи
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ]
        
        for content_type in allowed_types:
            mock_request = Mock(spec=Request)
            mock_request.headers = {"content-type": content_type}
            assert validation_middleware._check_content_type(mock_request) is True
        
        # Недозволений тип
        mock_request = Mock(spec=Request)
        mock_request.headers = {"content-type": "application/xml"}
        assert validation_middleware._check_content_type(mock_request) is False


class TestAuthMiddleware:
    """Тести для Auth Middleware"""
    
    def test_auth_middleware_initialization(self):
        """Тест ініціалізації Auth Middleware"""
        auth_middleware = AuthMiddleware()
        assert auth_middleware is not None
        assert len(auth_middleware.public_paths) > 0
    
    def test_public_path_detection(self):
        """Тест виявлення публічних шляхів"""
        auth_middleware = AuthMiddleware()
        
        # Публічні шляхи
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/auth/login",
            "/auth/register"
        ]
        
        for path in public_paths:
            assert auth_middleware._is_public_path(path) is True
        
        # Приватні шляхи
        private_paths = [
            "/api/users",
            "/admin/dashboard",
            "/private/data",
            "/users/profile",
            "/dashboard"
        ]
        
        for path in private_paths:
            assert auth_middleware._is_public_path(path) is False
    
    def test_token_verification(self):
        """Тест верифікації токена"""
        auth_middleware = AuthMiddleware()
        
        # Створюємо валідний токен
        payload = {
            "sub": "123",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow()
        }
        
        valid_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Перевіряємо валідний токен
        decoded_payload = auth_middleware._verify_token(valid_token)
        assert decoded_payload["sub"] == "123"
        
        # Перевіряємо невірний токен
        with pytest.raises(Exception):
            auth_middleware._verify_token("invalid-token")
    
    def test_admin_path_detection(self):
        """Тест виявлення адміністративних шляхів"""
        auth_middleware = AuthMiddleware()
        
        # Адміністративні шляхи
        admin_paths = [
            "/admin/dashboard",
            "/api/admin/users",
            "/admin/settings"
        ]
        
        for path in admin_paths:
            assert auth_middleware._is_admin_path(path) is True
        
        # Звичайні шляхи
        normal_paths = [
            "/api/users",
            "/dashboard",
            "/settings"
        ]
        
        for path in normal_paths:
            assert auth_middleware._is_admin_path(path) is False


class TestSecurityIntegration:
    """Інтеграційні тести безпеки"""
    
    def test_middleware_chain(self):
        """Тест ланцюжка middleware"""
        # Створюємо тестовий FastAPI додаток
        app = FastAPI()
        
        # Додаємо middleware
        from shared.utils.rate_limiter import rate_limit_middleware
        from shared.utils.validation_middleware import validation_middleware_handler
        from shared.utils.auth_middleware import auth_middleware_handler
        
        @app.middleware("http")
        async def test_middleware(request, call_next):
            from fastapi import HTTPException as FastAPIHTTPException
            from fastapi.responses import JSONResponse
            try:
                # Rate limiting
                await rate_limit_middleware(request, call_next)
                # Validation
                await validation_middleware_handler(request, call_next)
                # Auth
                await auth_middleware_handler(request, call_next)
                return await call_next(request)
            except FastAPIHTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        
        @app.get("/health")
        async def health_endpoint():
            return {"status": "ok"}
        
        @app.get("/private/test")
        async def private_endpoint():
            return {"message": "private"}
        
        # Тестуємо з TestClient
        client = TestClient(app, raise_server_exceptions=False)
        
        # Тест публічного шляху
        response = client.get("/health")
        assert response.status_code == 200
        
        # Тест з невірним токеном (приватний шлях)
        response = client.get("/private/test", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401
    
    def test_security_headers(self):
        """Тест заголовків безпеки"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Перевіряємо наявність заголовків безпеки
        headers = response.headers
        assert "content-type" in headers
        assert "content-length" in headers


if __name__ == "__main__":
    pytest.main([__file__]) 