"""
Тести безпеки OAuth інтеграції
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Додаємо шлях до тестових утиліт
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.utils.test_helpers import create_test_user, get_test_db
from app.backend.services.auth_service.src.main import app
from app.backend.services.auth_service.src.models import User, OAuthConnection
from app.backend.shared.database.connection import get_db

# Мокаємо базу даних
def override_get_db():
    return get_test_db()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestOAuthSecurity:
    """Тести безпеки OAuth інтеграції"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user = create_test_user()
        self.test_token = "test_jwt_token"
    
    def test_oauth_authorize_rate_limiting(self):
        """Тест rate limiting для OAuth authorize"""
        # Мокаємо rate limiter
        with patch('app.backend.services.auth_service.src.oauth.rate_limiter') as mock_limiter:
            mock_limiter.allow_request.return_value = False
            
            response = client.get(
                "/auth/oauth/upwork/authorize",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 429
            assert "Забагато запитів на авторизацію" in response.json()["detail"]
    
    def test_oauth_callback_rate_limiting(self):
        """Тест rate limiting для OAuth callback"""
        with patch('app.backend.services.auth_service.src.oauth.rate_limiter') as mock_limiter:
            mock_limiter.allow_request.return_value = False
            
            response = client.get(
                "/auth/oauth/upwork/callback?code=test_code&state=test_state",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 429
            assert "Забагато спроб callback" in response.json()["detail"]
    
    def test_oauth_refresh_rate_limiting(self):
        """Тест rate limiting для OAuth refresh"""
        with patch('app.backend.services.auth_service.src.oauth.rate_limiter') as mock_limiter:
            mock_limiter.allow_request.return_value = False
            
            response = client.post(
                "/auth/oauth/upwork/refresh",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 429
            assert "Забагато запитів на оновлення токена" in response.json()["detail"]
    
    def test_oauth_state_validation(self):
        """Тест валідації state параметра"""
        with patch('app.backend.services.auth_service.src.oauth.state_cache') as mock_cache:
            mock_cache.get.return_value = None  # Неправильний state
            
            response = client.get(
                "/auth/oauth/upwork/callback?code=test_code&state=invalid_state",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 400
            assert "Invalid state parameter" in response.json()["detail"]
    
    def test_oauth_user_hash_validation(self):
        """Тест валідації хешу користувача в state"""
        with patch('app.backend.services.auth_service.src.oauth.state_cache') as mock_cache:
            # Правильний state формат
            mock_cache.get.return_value = "test_state.valid_hash"
            
            response = client.get(
                "/auth/oauth/upwork/callback?code=test_code&state=test_state.invalid_hash",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 400
            assert "Invalid state parameter" in response.json()["detail"]
    
    def test_oauth_invalid_state_format(self):
        """Тест валідації формату state"""
        with patch('app.backend.services.auth_service.src.oauth.state_cache') as mock_cache:
            mock_cache.get.return_value = "test_state.valid_hash"
            
            response = client.get(
                "/auth/oauth/upwork/callback?code=test_code&state=invalid_format",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 400
            assert "Invalid state format" in response.json()["detail"]
    
    def test_oauth_invalid_authorization_code(self):
        """Тест валідації authorization code"""
        with patch('app.backend.services.auth_service.src.oauth.state_cache') as mock_cache:
            mock_cache.get.return_value = "test_state.valid_hash"
            
            response = client.get(
                "/auth/oauth/upwork/callback?code=short&state=test_state.valid_hash",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 400
            assert "Invalid authorization code" in response.json()["detail"]
    
    def test_oauth_disconnect_invalid_provider(self):
        """Тест валідації провайдера при відключенні"""
        response = client.delete(
                "/auth/oauth/connections/invalid_provider",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
        
        assert response.status_code == 400
        assert "Непідтримуваний провайдер" in response.json()["detail"]
    
    def test_oauth_security_features_list(self):
        """Тест списку функцій безпеки"""
        response = client.get("/auth/oauth/upwork/test")
        
        assert response.status_code == 200
        data = response.json()
        assert "security_features" in data
        assert "Rate limiting" in data["security_features"]
        assert "State validation" in data["security_features"]
        assert "User hash verification" in data["security_features"]
        assert "Token encryption" in data["security_features"]
        assert "Secure callback handling" in data["security_features"]
    
    def test_oauth_authorize_success_with_security(self):
        """Тест успішної авторизації з функціями безпеки"""
        with patch('app.backend.services.auth_service.src.oauth.rate_limiter') as mock_limiter:
            mock_limiter.allow_request.return_value = True
            
            response = client.get(
                "/auth/oauth/upwork/authorize",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "authorization_url" in data
            assert "state" in data
            assert "expires_in" in data
            assert data["expires_in"] == 300  # 5 хвилин
    
    def test_oauth_callback_success_with_security(self):
        """Тест успішного callback з функціями безпеки"""
        with patch('app.backend.services.auth_service.src.oauth.rate_limiter') as mock_limiter:
            mock_limiter.allow_request.return_value = True
            
        with patch('app.backend.services.auth_service.src.oauth.state_cache') as mock_cache:
            # Симулюємо правильний state
            mock_cache.get.return_value = "test_state.valid_hash"
            
        with patch('app.backend.services.auth_service.src.oauth.requests.post') as mock_post:
            # Симулюємо успішну відповідь від Upwork
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "expires_in": 3600,
                "scope": "jobs:read jobs:write",
                "user_id": "test_user_123"
            }
            mock_post.return_value = mock_response
            
            response = client.get(
                "/auth/oauth/upwork/callback?code=valid_code&state=test_state.valid_hash",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["provider"] == "upwork"
            assert "expires_at" in data


class TestOAuthStateCache:
    """Тести для StateCache класу"""
    
    def test_state_cache_set_get(self):
        """Тест збереження та отримання state"""
        from app.backend.services.auth_service.src.oauth import StateCache
        
        cache = StateCache()
        user_id = 1
        state = "test_state"
        
        cache.set(user_id, state)
        retrieved_state = cache.get(user_id)
        
        assert retrieved_state == state
    
    def test_state_cache_expiration(self):
        """Тест закінчення терміну дії state"""
        from app.backend.services.auth_service.src.oauth import StateCache
        import time
        
        cache = StateCache()
        user_id = 1
        state = "test_state"
        
        cache.set(user_id, state)
        
        # Симулюємо закінчення терміну дії
        cache._cache[user_id]['timestamp'] = time.time() - 400  # 6.7 хвилин тому
        
        retrieved_state = cache.get(user_id)
        
        assert retrieved_state is None
        assert user_id not in cache._cache
    
    def test_state_cache_remove(self):
        """Тест видалення state"""
        from app.backend.services.auth_service.src.oauth import StateCache
        
        cache = StateCache()
        user_id = 1
        state = "test_state"
        
        cache.set(user_id, state)
        cache.remove(user_id)
        
        retrieved_state = cache.get(user_id)
        assert retrieved_state is None 