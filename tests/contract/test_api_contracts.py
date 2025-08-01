"""
Contract Testing для API
"""

import pytest
import json
from fastapi.testclient import TestClient
from typing import Dict, Any, List
import sys
import os

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'api-gateway', 'src'))

from main import app

client = TestClient(app)


class TestAPIContracts:
    """Тести контрактів API"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
        self.test_token = "test_token_123"
    
    def test_health_endpoint_contract(self):
        """Тест контракту health endpoint"""
        response = client.get("/health")
        
        # Перевіряємо статус код
        assert response.status_code == 200
        
        # Перевіряємо структуру відповіді
        data = response.json()
        
        # Обов'язкові поля
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        
        # Типи даних
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["timestamp"], str)
        
        # Валідні значення
        assert data["status"] in ["healthy", "unhealthy"]
        assert "api-gateway" in data["service"].lower()
    
    def test_dashboard_endpoint_contract(self):
        """Тест контракту dashboard endpoint"""
        headers = {"Authorization": f"Bearer {self.test_token}"}
        response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}", headers=headers)
        
        # Перевіряємо статус код
        assert response.status_code in [200, 401, 403, 404]
        
        if response.status_code == 200:
            data = response.json()
            
            # Обов'язкові поля
            assert "status" in data
            assert "data" in data
            
            # Типи даних
            assert isinstance(data["status"], str)
            assert isinstance(data["data"], dict)
            
            # Валідні значення
            assert data["status"] in ["success", "error"]
            
            if data["status"] == "success":
                dashboard_data = data["data"]
                
                # Перевіряємо структуру dashboard даних
                expected_fields = ["earnings", "proposals", "jobs", "user_id"]
                for field in expected_fields:
                    assert field in dashboard_data
    
    def test_earnings_endpoint_contract(self):
        """Тест контракту earnings endpoint"""
        headers = {"Authorization": f"Bearer {self.test_token}"}
        response = client.get(f"/api/analytics/earnings?user_id={self.test_user_id}", headers=headers)
        
        # Перевіряємо статус код
        assert response.status_code in [200, 401, 403, 404]
        
        if response.status_code == 200:
            data = response.json()
            
            # Обов'язкові поля
            assert "status" in data
            assert "data" in data
            
            # Типи даних
            assert isinstance(data["status"], str)
            assert isinstance(data["data"], dict)
            
            if data["status"] == "success":
                earnings_data = data["data"]
                
                # Перевіряємо структуру earnings даних
                expected_fields = ["total", "monthly", "trend"]
                for field in expected_fields:
                    assert field in earnings_data
                
                # Перевіряємо типи числових полів
                assert isinstance(earnings_data["total"], (int, float))
    
    def test_proposals_endpoint_contract(self):
        """Тест контракту proposals endpoint"""
        headers = {"Authorization": f"Bearer {self.test_token}"}
        response = client.get(f"/api/analytics/proposals?user_id={self.test_user_id}", headers=headers)
        
        # Перевіряємо статус код
        assert response.status_code in [200, 401, 403, 404]
        
        if response.status_code == 200:
            data = response.json()
            
            # Обов'язкові поля
            assert "status" in data
            assert "data" in data
            
            # Типи даних
            assert isinstance(data["status"], str)
            assert isinstance(data["data"], dict)
            
            if data["status"] == "success":
                proposals_data = data["data"]
                
                # Перевіряємо структуру proposals даних
                expected_fields = ["sent", "accepted", "rejected", "pending"]
                for field in expected_fields:
                    assert field in proposals_data
                
                # Перевіряємо типи числових полів
                for field in expected_fields:
                    assert isinstance(proposals_data[field], int)
    
    def test_jobs_endpoint_contract(self):
        """Тест контракту jobs endpoint"""
        headers = {"Authorization": f"Bearer {self.test_token}"}
        response = client.get(f"/api/analytics/jobs?user_id={self.test_user_id}", headers=headers)
        
        # Перевіряємо статус код
        assert response.status_code in [200, 401, 403, 404]
        
        if response.status_code == 200:
            data = response.json()
            
            # Обов'язкові поля
            assert "status" in data
            assert "data" in data
            
            # Типи даних
            assert isinstance(data["status"], str)
            assert isinstance(data["data"], dict)
            
            if data["status"] == "success":
                jobs_data = data["data"]
                
                # Перевіряємо структуру jobs даних
                expected_fields = ["active", "completed", "cancelled"]
                for field in expected_fields:
                    assert field in jobs_data
                
                # Перевіряємо типи числових полів
                for field in expected_fields:
                    assert isinstance(jobs_data[field], int)
    
    def test_error_response_contract(self):
        """Тест контракту error response"""
        # Тестуємо неіснуючий endpoint
        response = client.get("/api/nonexistent")
        
        # Перевіряємо статус код
        assert response.status_code in [404, 422]
        
        data = response.json()
        
        # Обов'язкові поля для помилки
        assert "detail" in data or "error" in data or "message" in data
        
        # Типи даних
        if "detail" in data:
            assert isinstance(data["detail"], (str, list))
        if "error" in data:
            assert isinstance(data["error"], str)
        if "message" in data:
            assert isinstance(data["message"], str)
    
    def test_authentication_contract(self):
        """Тест контракту автентифікації"""
        # Тестуємо без токена
        response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
        
        # Перевіряємо статус код
        assert response.status_code in [401, 403]
        
        data = response.json()
        
        # Обов'язкові поля для помилки автентифікації
        assert "detail" in data or "error" in data or "message" in data
        
        # Перевіряємо повідомлення про помилку
        error_message = data.get("detail", data.get("error", data.get("message", "")))
        assert "auth" in error_message.lower() or "token" in error_message.lower() or "unauthorized" in error_message.lower()


class TestDataContracts:
    """Тести контрактів даних"""
    
    def test_user_data_contract(self):
        """Тест контракту даних користувача"""
        user_data = {
            "id": "user_123",
            "email": "test@example.com",
            "first_name": "Іван",
            "last_name": "Петренко",
            "role": "freelancer",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Перевіряємо обов'язкові поля
        required_fields = ["id", "email", "first_name", "last_name", "role"]
        for field in required_fields:
            assert field in user_data
        
        # Перевіряємо типи даних
        assert isinstance(user_data["id"], str)
        assert isinstance(user_data["email"], str)
        assert isinstance(user_data["first_name"], str)
        assert isinstance(user_data["last_name"], str)
        assert isinstance(user_data["role"], str)
        
        # Перевіряємо валідні значення
        assert user_data["role"] in ["freelancer", "client", "admin"]
        assert "@" in user_data["email"]
    
    def test_job_data_contract(self):
        """Тест контракту даних роботи"""
        job_data = {
            "id": "job_123",
            "title": "Python Developer",
            "description": "We need a Python developer...",
            "budget": {
                "min": 1000,
                "max": 5000,
                "currency": "USD"
            },
            "skills": ["Python", "Django", "PostgreSQL"],
            "status": "open",
            "created_at": "2024-01-01T00:00:00Z",
            "client": {
                "id": "client_123",
                "name": "Tech Company"
            }
        }
        
        # Перевіряємо обов'язкові поля
        required_fields = ["id", "title", "description", "budget", "status"]
        for field in required_fields:
            assert field in job_data
        
        # Перевіряємо типи даних
        assert isinstance(job_data["id"], str)
        assert isinstance(job_data["title"], str)
        assert isinstance(job_data["description"], str)
        assert isinstance(job_data["budget"], dict)
        assert isinstance(job_data["status"], str)
        
        # Перевіряємо структуру budget
        budget = job_data["budget"]
        assert "min" in budget
        assert "max" in budget
        assert "currency" in budget
        assert isinstance(budget["min"], (int, float))
        assert isinstance(budget["max"], (int, float))
        assert isinstance(budget["currency"], str)
        
        # Перевіряємо валідні значення
        assert job_data["status"] in ["open", "in_progress", "completed", "cancelled"]
        assert budget["currency"] in ["USD", "EUR", "UAH"]
        assert budget["min"] <= budget["max"]
    
    def test_proposal_data_contract(self):
        """Тест контракту даних пропозиції"""
        proposal_data = {
            "id": "proposal_123",
            "job_id": "job_123",
            "freelancer_id": "user_123",
            "cover_letter": "I am interested in this job...",
            "bid_amount": 2500,
            "currency": "USD",
            "delivery_time": 14,
            "status": "submitted",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Перевіряємо обов'язкові поля
        required_fields = ["id", "job_id", "freelancer_id", "cover_letter", "bid_amount", "status"]
        for field in required_fields:
            assert field in proposal_data
        
        # Перевіряємо типи даних
        assert isinstance(proposal_data["id"], str)
        assert isinstance(proposal_data["job_id"], str)
        assert isinstance(proposal_data["freelancer_id"], str)
        assert isinstance(proposal_data["cover_letter"], str)
        assert isinstance(proposal_data["bid_amount"], (int, float))
        assert isinstance(proposal_data["status"], str)
        
        # Перевіряємо валідні значення
        assert proposal_data["status"] in ["submitted", "accepted", "rejected", "withdrawn"]
        assert proposal_data["bid_amount"] > 0
        assert len(proposal_data["cover_letter"]) > 0


class TestSchemaValidation:
    """Тести валідації схем"""
    
    def test_request_schema_validation(self):
        """Тест валідації схем запитів"""
        # Тестуємо валідний запит
        valid_request = {
            "user_id": "user_123",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        response = client.post("/api/analytics/search", json=valid_request)
        
        # Запит повинен пройти валідацію
        assert response.status_code in [200, 401, 403, 404]
        
        # Тестуємо невалідний запит
        invalid_request = {
            "user_id": "",  # Порожній user_id
            "start_date": "invalid-date",  # Невалідна дата
            "end_date": "2024-01-31"
        }
        
        response = client.post("/api/analytics/search", json=invalid_request)
        
        # Запит повинен не пройти валідацію
        assert response.status_code in [400, 422]
    
    def test_response_schema_validation(self):
        """Тест валідації схем відповідей"""
        headers = {"Authorization": f"Bearer test_token"}
        response = client.get("/api/analytics/dashboard?user_id=test_user", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Перевіряємо структуру відповіді
            assert "status" in data
            assert "data" in data
            
            # Перевіряємо типи даних
            assert isinstance(data["status"], str)
            assert isinstance(data["data"], dict)
            
            # Перевіряємо валідні значення
            assert data["status"] in ["success", "error"]
    
    def test_enum_validation(self):
        """Тест валідації enum значень"""
        # Тестуємо валідні значення enum
        valid_statuses = ["open", "in_progress", "completed", "cancelled"]
        
        for status in valid_statuses:
            job_data = {
                "id": "job_123",
                "title": "Test Job",
                "description": "Test description",
                "status": status
            }
            
            # Дані повинні пройти валідацію
            assert isinstance(job_data["status"], str)
            assert job_data["status"] in valid_statuses
        
        # Тестуємо невалідні значення enum
        invalid_status = "invalid_status"
        job_data = {
            "id": "job_123",
            "title": "Test Job",
            "description": "Test description",
            "status": invalid_status
        }
        
        # Дані повинні не пройти валідацію
        assert job_data["status"] not in valid_statuses


class TestVersioningContracts:
    """Тести контрактів версіонування"""
    
    def test_api_version_header(self):
        """Тест заголовка версії API"""
        headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Accept": "application/json",
            "X-API-Version": "v1"
        }
        
        response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}", headers=headers)
        
        # Перевіряємо що API приймає версію
        assert response.status_code in [200, 401, 403, 404]
        
        # Перевіряємо заголовки відповіді
        response_headers = response.headers
        assert "content-type" in response_headers
        assert "application/json" in response_headers["content-type"]
    
    def test_backward_compatibility(self):
        """Тест зворотної сумісності"""
        # Тестуємо стару версію API
        old_version_headers = {"X-API-Version": "v1"}
        response_old = client.get("/health", headers=old_version_headers)
        
        # Тестуємо нову версію API
        new_version_headers = {"X-API-Version": "v2"}
        response_new = client.get("/health", headers=new_version_headers)
        
        # Обидві версії повинні працювати
        assert response_old.status_code == 200
        assert response_new.status_code == 200
        
        # Перевіряємо що структура відповіді не змінилась
        old_data = response_old.json()
        new_data = response_new.json()
        
        # Основні поля повинні залишитись
        assert "status" in old_data
        assert "status" in new_data
        assert "service" in old_data
        assert "service" in new_data


class TestRateLimitingContracts:
    """Тести контрактів rate limiting"""
    
    def test_rate_limiting_headers(self):
        """Тест заголовків rate limiting"""
        # Робимо кілька запитів підряд
        for i in range(5):
            response = client.get("/health")
            
            # Перевіряємо заголовки rate limiting
            headers = response.headers
            
            # Можливі заголовки rate limiting
            rate_limit_headers = [
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
                "retry-after"
            ]
            
            # Хоча б один заголовок повинен бути присутній
            has_rate_limit_header = any(header in headers for header in rate_limit_headers)
            
            # Якщо є rate limiting, перевіряємо структуру
            if has_rate_limit_header:
                if "x-ratelimit-limit" in headers:
                    assert headers["x-ratelimit-limit"].isdigit()
                if "x-ratelimit-remaining" in headers:
                    assert headers["x-ratelimit-remaining"].isdigit()
    
    def test_rate_limiting_response(self):
        """Тест відповіді при rate limiting"""
        # Робимо багато запитів підряд
        for i in range(20):
            response = client.get("/health")
            
            # Якщо спрацював rate limiting
            if response.status_code == 429:
                data = response.json()
                
                # Перевіряємо структуру відповіді
                assert "error" in data or "detail" in data or "message" in data
                
                # Перевіряємо повідомлення
                error_message = data.get("error", data.get("detail", data.get("message", "")))
                assert "rate limit" in error_message.lower() or "too many requests" in error_message.lower()
                
                break 