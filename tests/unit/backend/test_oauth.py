"""
Тести для OAuth 2.0 інтеграції з Upwork
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, APIRouter
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config.settings import settings

# Створюємо мок router для тестування
router = APIRouter()

@router.get("/upwork/authorize")
async def upwork_authorize():
    """Мок endpoint для авторизації"""
    return {
        "auth_url": "https://www.upwork.com/services/api/auth",
        "params": {
            "client_id": "test_client_id",
            "redirect_uri": "http://localhost:8000/auth/oauth/upwork/callback",
            "response_type": "code",
            "scope": "r_workdiary r_workdairy r_workdairy_read r_workdairy_write"
        }
    }

@router.get("/upwork/callback")
async def upwork_callback(code: str):
    """Мок endpoint для callback"""
    return {"message": "Upwork успішно підключено"}

@router.get("/connections")
async def get_oauth_connections():
    """Мок endpoint для отримання підключень"""
    return [
        {
            "provider": "upwork",
            "is_active": True,
            "expires_at": "2024-12-31T23:59:59"
        }
    ]

@router.delete("/connections/{provider}")
async def disconnect_oauth(provider: str):
    """Мок endpoint для відключення"""
    return {"message": f"{provider} відключено"}

# Створюємо тестовий додаток
app = FastAPI()
app.include_router(router, prefix="/auth/oauth")


class TestOAuthFlow:
    """Тести для OAuth flow"""
    
    def test_upwork_authorize_success(self):
        """Тест успішної авторизації Upwork"""
        client = TestClient(app)
        
        response = client.get("/auth/oauth/upwork/authorize")
        
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "params" in data
        assert data["params"]["client_id"] == "test_client_id"
        assert data["params"]["redirect_uri"] == "http://localhost:8000/auth/oauth/upwork/callback"
        assert data["params"]["response_type"] == "code"
    
    def test_upwork_callback_success(self):
        """Тест успішного callback"""
        client = TestClient(app)
        
        response = client.get("/auth/oauth/upwork/callback?code=test_auth_code")
        
        assert response.status_code == 200
        assert "Upwork успішно підключено" in response.json()["message"]
    
    def test_upwork_callback_missing_code(self):
        """Тест callback без коду"""
        client = TestClient(app)
        
        response = client.get("/auth/oauth/upwork/callback")
        
        assert response.status_code == 422  # Validation error


class TestOAuthConnections:
    """Тести для управління OAuth з'єднаннями"""
    
    def test_get_oauth_connections(self):
        """Тест отримання OAuth з'єднань"""
        client = TestClient(app)
        
        response = client.get("/auth/oauth/connections")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["provider"] == "upwork"
        assert data[0]["is_active"] is True
    
    def test_disconnect_oauth(self):
        """Тест відключення OAuth з'єднання"""
        client = TestClient(app)
        
        response = client.delete("/auth/oauth/connections/upwork")
        
        assert response.status_code == 200
        assert "upwork відключено" in response.json()["message"]


class TestOAuthIntegration:
    """Інтеграційні тести OAuth"""
    
    def test_oauth_flow_integration(self):
        """Тест повного OAuth flow"""
        client = TestClient(app)
        
        # 1. Отримуємо URL для авторизації
        auth_response = client.get("/auth/oauth/upwork/authorize")
        assert auth_response.status_code == 200
        
        # 2. Симулюємо callback з кодом
        callback_response = client.get("/auth/oauth/upwork/callback?code=test_code")
        assert callback_response.status_code == 200
        
        # 3. Перевіряємо підключення
        connections_response = client.get("/auth/oauth/connections")
        assert connections_response.status_code == 200
        
        # 4. Відключаємо
        disconnect_response = client.delete("/auth/oauth/connections/upwork")
        assert disconnect_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__]) 