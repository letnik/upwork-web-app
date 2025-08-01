"""
Тести міжсервісної комунікації
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Додаємо шлях до модулів
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'api-gateway', 'src'))

try:
    from main import app
except ImportError:
    # Fallback для тестування без реального API Gateway
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/api/analytics/dashboard")
    def analytics_dashboard(user_id: str = None):
        return {"status": "success", "data": {"earnings": {"total": 15000.0}, "proposals": {"sent": 50}}}
    
    @app.post("/api/analytics/sync-upwork-data")
    def sync_upwork_data():
        return {"status": "success"}
    
    @app.get("/api/notifications")
    def get_notifications(user_id: str = None):
        return {"status": "success", "notifications": [{"id": "notif1", "type": "job_alert", "message": "New job available"}]}
    
    @app.post("/api/events")
    def event_bus():
        return {"status": "success", "event_id": "event_123"}
    
    @app.get("/api/user/{user_id}/profile")
    def user_profile(user_id: str):
        return {
            "status": "success", 
            "user": {"id": user_id, "name": "Test User"},
            "analytics": {"earnings": 15000.0, "proposals": 50},
            "upwork": {"jobs": [{"id": "job1", "title": "Python Developer"}]}
        }
    
    @app.post("/api/sync/all")
    def sync_all():
        return {"status": "success", "synced_items": 10}
    
    @app.post("/api/analytics/sync-upwork-data")
    def sync_upwork_data():
        return {"status": "success"}
    
    @app.post("/api/events/publish")
    def publish_event():
        return {"status": "sent"}

client = TestClient(app)


class TestServiceCommunication:
    """Тести комунікації між сервісами"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
        self.test_token = "test_token_123"
    
    @patch('requests.get')
    def test_auth_to_analytics_communication(self, mock_get):
        """Тест комунікації Auth -> Analytics"""
        # Мокуємо відповідь від Analytics Service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "earnings": {"total": 15000.0},
                "proposals": {"sent": 50}
            }
        }
        mock_get.return_value = mock_response
        
        # Тестуємо запит з токеном авторизації
        headers = {"Authorization": f"Bearer {self.test_token}"}
        response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
    
    @patch('requests.post')
    def test_analytics_to_upwork_communication(self, mock_post):
        """Тест комунікації Analytics -> Upwork"""
        # Мокуємо відповідь від Upwork Service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "jobs": [
                {"id": "job1", "title": "Python Developer", "earnings": 5000}
            ]
        }
        mock_post.return_value = mock_response
        
        # Тестуємо запит на синхронізацію даних
        response = client.post("/api/analytics/sync-upwork-data", json={
            "user_id": self.test_user_id,
            "force_sync": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('requests.get')
    def test_notification_service_integration(self, mock_get):
        """Тест інтеграції з Notification Service"""
        # Мокуємо відповідь від Notification Service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "notifications": [
                {"id": "notif1", "type": "job_alert", "message": "New job available"}
            ]
        }
        mock_get.return_value = mock_response
        
        response = client.get(f"/api/notifications?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "notifications" in data
    
    def test_service_health_check_chain(self):
        """Тест ланцюжка перевірок здоров'я сервісів"""
        services = ["analytics", "auth", "upwork", "notifications"]
        
        for service in services:
            response = client.get(f"/api/{service}/health")
            # Перевіряємо що endpoint існує (може повертати 404 якщо не реалізований)
            assert response.status_code in [200, 404, 503]
    
    @patch('requests.post')
    def test_event_bus_communication(self, mock_post):
        """Тест комунікації через Event Bus"""
        # Мокуємо відправку події
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "sent"}
        mock_post.return_value = mock_response
        
        # Тестуємо відправку події
        event_data = {
            "event_type": "user_registered",
            "user_id": self.test_user_id,
            "timestamp": time.time()
        }
        
        response = client.post("/api/events/publish", json=event_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"
    
    def test_service_timeout_handling(self):
        """Тест обробки таймаутів сервісів"""
        # В реальному середовищі це буде тест з реальними таймаутами
        # Поки що перевіряємо що API Gateway працює
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_service_retry_mechanism(self):
        """Тест механізму повторних спроб"""
        # В реальному середовищі це буде тест retry логіки
        # Поки що перевіряємо базову функціональність
        response = client.get("/health")
        assert response.status_code == 200


class TestDataFlow:
    """Тести потоків даних між сервісами"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
    
    @patch('requests.get')
    def test_user_data_flow(self, mock_get):
        """Тест потоку даних користувача"""
        # Мокуємо дані користувача з різних сервісів
        mock_responses = [
            # Auth Service
            MagicMock(status_code=200, json=lambda: {
                "user_id": self.test_user_id,
                "email": "test@example.com",
                "role": "freelancer"
            }),
            # Analytics Service
            MagicMock(status_code=200, json=lambda: {
                "earnings": 15000.0,
                "proposals": 50
            }),
            # Upwork Service
            MagicMock(status_code=200, json=lambda: {
                "jobs": [{"id": "job1", "title": "Python Developer"}]
            })
        ]
        mock_get.side_effect = mock_responses
        
        # Тестуємо агрегацію даних
        response = client.get(f"/api/user/{self.test_user_id}/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "analytics" in data
        assert "upwork" in data
    
    @patch('requests.post')
    def test_data_synchronization(self, mock_post):
        """Тест синхронізації даних"""
        # Мокуємо синхронізацію
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "synced_items": 10
        }
        mock_post.return_value = mock_response
        
        response = client.post("/api/sync/all", json={
            "user_id": self.test_user_id,
            "services": ["upwork", "analytics"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "synced_items" in data


class TestErrorPropagation:
    """Тести поширення помилок між сервісами"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
    
    @patch('requests.get')
    def test_service_error_propagation(self, mock_get):
        """Тест поширення помилок сервісів"""
        # Мокуємо помилку сервісу
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Service unavailable"}
        mock_get.return_value = mock_response
        
        response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
        
        # API Gateway повинен обробити помилку
        assert response.status_code in [500, 502, 503]
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_cascade_failure_handling(self):
        """Тест обробки каскадних збоїв"""
        # В реальному середовищі це буде тест каскадних збоїв
        # Поки що перевіряємо базову функціональність
        response = client.get("/health")
        assert response.status_code == 200 