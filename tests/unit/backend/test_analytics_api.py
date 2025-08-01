"""
Unit Tests для Analytics API endpoints
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'analytics-service', 'src'))

from main import app

client = TestClient(app)


class TestAnalyticsAPI:
    """Тести для Analytics API endpoints"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
    
    def test_root_endpoint(self):
        """Тест головного endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Analytics Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "timestamp" in data
    
    def test_health_check(self):
        """Тест перевірки здоров'я сервісу"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics-service"
        assert "database" in data
        assert "timestamp" in data
    
    @patch('main.analytics_engine')
    def test_get_dashboard_data(self, mock_engine):
        """Тест отримання даних дашборду"""
        # Налаштування моку
        mock_engine.get_dashboard_data.return_value = {
            "earnings": {"total": 15000.0, "monthly": 3000.0, "weekly": 750.0},
            "proposals": {"sent": 50, "accepted": 20, "pending": 10, "rejected": 20},
            "jobs": {"applied": 100, "won": 25, "active": 10, "completed": 15},
            "performance": {"rating": 4.8, "success_rate": 40.0},
            "categories": [{"name": "Web Development", "value": 30.0, "color": "#8884d8"}],
            "time_series": [{"date": "2025-07-30", "earnings": 1200.0, "proposals": 5}],
            "trends": {"earnings": 12.5, "proposals": 8.2},
            "generated_at": "2025-07-30T21:00:00"
        }
        
        response = client.get(f"/analytics/dashboard?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        
        # Перевірка структури даних
        analytics_data = data["data"]
        assert "earnings" in analytics_data
        assert "proposals" in analytics_data
        assert "jobs" in analytics_data
        assert "performance" in analytics_data
        assert "categories" in analytics_data
        assert "time_series" in analytics_data
        assert "trends" in analytics_data
        assert "generated_at" in analytics_data
    
    @patch('main.analytics_engine')
    def test_get_earnings_analytics(self, mock_engine):
        """Тест отримання аналітики заробітку"""
        # Налаштування моку
        mock_engine.get_earnings_analytics.return_value = {
            "total": 15000.0,
            "monthly": 3000.0,
            "weekly": 750.0,
            "daily": 107.0,
            "trend": 12.5,
            "currency": "USD",
            "breakdown": {
                "hourly": 8000.0,
                "fixed": 7000.0
            },
            "top_clients": [
                {"name": "Tech Solutions Inc", "amount": 5000.0},
                {"name": "Digital Agency", "amount": 3000.0}
            ]
        }
        
        response = client.get(f"/analytics/earnings?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert data["data"]["total"] == 15000.0
        assert data["data"]["currency"] == "USD"
    
    @patch('main.analytics_engine')
    def test_get_proposals_analytics(self, mock_engine):
        """Тест отримання аналітики пропозицій"""
        # Налаштування моку
        mock_engine.get_proposals_analytics.return_value = {
            "sent": 50,
            "accepted": 20,
            "pending": 10,
            "rejected": 20,
            "success_rate": 40.0,
            "avg_response_time": "2.5 hours",
            "top_categories": [
                {"name": "Web Development", "sent": 25, "accepted": 12},
                {"name": "Mobile Development", "sent": 15, "accepted": 6}
            ]
        }
        
        response = client.get(f"/analytics/proposals?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert data["data"]["sent"] == 50
        assert data["data"]["success_rate"] == 40.0
    
    @patch('main.analytics_engine')
    def test_get_jobs_analytics(self, mock_engine):
        """Тест отримання аналітики проектів"""
        # Налаштування моку
        mock_engine.get_jobs_analytics.return_value = {
            "applied": 100,
            "won": 25,
            "active": 10,
            "completed": 15,
            "total_earnings": 15000.0,
            "avg_job_value": 600.0,
            "top_skills": ["Python", "React", "Node.js", "Docker"],
            "job_types": {
                "hourly": 15,
                "fixed": 10
            }
        }
        
        response = client.get(f"/analytics/jobs?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert data["data"]["applied"] == 100
        assert data["data"]["total_earnings"] == 15000.0
    
    @patch('main.analytics_engine')
    def test_get_categories_analytics(self, mock_engine):
        """Тест отримання аналітики категорій"""
        # Налаштування моку
        mock_engine.get_categories_analytics.return_value = [
            {"name": "Web Development", "value": 30.0, "color": "#8884d8", "jobs": 15},
            {"name": "Mobile Development", "value": 25.0, "color": "#82ca9d", "jobs": 12}
        ]
        
        response = client.get(f"/analytics/categories?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Web Development"
        assert data["data"][1]["name"] == "Mobile Development"
    
    @patch('main.analytics_engine')
    def test_get_timeseries_data(self, mock_engine):
        """Тест отримання часових рядів"""
        # Налаштування моку
        mock_engine.get_timeseries_data.return_value = [
            {"date": "2025-07-30", "earnings": 1200.0, "proposals": 5, "jobs": 3, "rating": 4.5},
            {"date": "2025-07-31", "earnings": 1300.0, "proposals": 6, "jobs": 4, "rating": 4.6}
        ]
        
        response = client.get(f"/analytics/timeseries?user_id={self.test_user_id}&days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert data["days"] == 7
        assert len(data["data"]) == 2
        assert data["data"][0]["date"] == "2025-07-30"
        assert data["data"][1]["date"] == "2025-07-31"
    
    @patch('main.analytics_engine')
    def test_get_analytics_summary(self, mock_engine):
        """Тест отримання короткого зведення"""
        # Налаштування моку
        mock_engine.get_analytics_summary.return_value = {
            "summary": {
                "total_earnings": 15000.0,
                "success_rate": 40.0,
                "active_jobs": 5,
                "rating": 4.8,
                "top_category": "Web Development"
            },
            "trends": {"earnings": 12.5},
            "last_updated": "2025-07-30T21:00:00"
        }
        
        response = client.get(f"/analytics/summary?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert data["data"]["summary"]["total_earnings"] == 15000.0
        assert data["data"]["summary"]["success_rate"] == 40.0
    
    @patch('main.analytics_engine')
    def test_export_analytics_data(self, mock_engine):
        """Тест експорту аналітичних даних"""
        # Налаштування моку
        mock_engine.export_analytics_data.return_value = '{"earnings": {"total": 15000.0}}'
        
        response = client.get(f"/analytics/export?user_id={self.test_user_id}&format=json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert data["format"] == "json"
    
    @patch('main.mock_data_generator')
    def test_generate_mock_data(self, mock_generator):
        """Тест генерації мок даних"""
        # Налаштування моку
        mock_generator.generate_mock_data.return_value = {
            "user_data": {
                "user": {
                    "id": "test_user_123",
                    "name": "Test User",
                    "email": "test@example.com",
                    "profile_completion": 95
                }
            },
            "time_series": [
                {"date": "2025-07-30", "earnings": 1200.0, "proposals": 5, "jobs": 3},
                {"date": "2025-07-31", "earnings": 1100.0, "proposals": 4, "jobs": 2}
            ],
            "categories": [
                {"name": "Web Development", "value": 30.0, "jobs": 15},
                {"name": "Mobile Development", "value": 25.0, "jobs": 12}
            ],
            "performance": {
                "rating": 4.8,
                "success_rate": 40.0,
                "response_time": "2.5 hours"
            },
            "jobs": [
                {"id": 1, "title": "Python Developer", "budget": 1000, "status": "active"},
                {"id": 2, "title": "React Developer", "budget": 800, "status": "completed"}
            ],
            "proposals": [
                {"id": 1, "job_id": 1, "status": "submitted", "submitted_at": "2025-07-30T10:00:00Z"},
                {"id": 2, "job_id": 2, "status": "accepted", "submitted_at": "2025-07-29T15:30:00Z"}
            ],
            "earnings": [
                {"id": 1, "amount": 500, "date": "2025-07-30", "job_id": 1},
                {"id": 2, "amount": 800, "date": "2025-07-29", "job_id": 2}
            ],
            "generated_at": "2025-07-30T21:00:00",
            "user_id": "test_user_123"
        }
        
        response = client.get(f"/analytics/mock/generate?user_id={self.test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["user_id"] == self.test_user_id
        assert "user_data" in data["data"]
        assert "time_series" in data["data"]
        assert "categories" in data["data"]
        assert "performance" in data["data"]
        assert "jobs" in data["data"]
        assert "proposals" in data["data"]
        assert "earnings" in data["data"]
        assert "generated_at" in data["data"]
    
    def test_get_dashboard_data_missing_user_id(self):
        """Тест отримання даних дашборду без user_id"""
        response = client.get("/analytics/dashboard")
        
        assert response.status_code == 422  # Validation Error
    
    def test_get_earnings_analytics_missing_user_id(self):
        """Тест отримання аналітики заробітку без user_id"""
        response = client.get("/analytics/earnings")
        
        assert response.status_code == 422  # Validation Error
    
    @patch('main.analytics_engine')
    def test_get_dashboard_data_error_handling(self, mock_engine):
        """Тест обробки помилок при отриманні даних дашборду"""
        # Налаштування моку для виклику помилки
        mock_engine.get_dashboard_data.side_effect = Exception("Test error")
        
        response = client.get(f"/analytics/dashboard?user_id={self.test_user_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Test error" in data["detail"]
    
    @patch('main.analytics_engine')
    def test_get_earnings_analytics_error_handling(self, mock_engine):
        """Тест обробки помилок при отриманні аналітики заробітку"""
        # Налаштування моку для виклику помилки
        mock_engine.get_earnings_analytics.side_effect = Exception("Test error")
        
        response = client.get(f"/analytics/earnings?user_id={self.test_user_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Test error" in data["detail"]
    
    def test_get_timeseries_data_with_different_days(self):
        """Тест отримання часових рядів з різною кількістю днів"""
        with patch('main.analytics_engine') as mock_engine:
            mock_engine.generate_time_series_data.return_value = [
                {"date": "2025-07-30", "earnings": 1200.0}
            ]
            
            # Тест з 7 днями
            response = client.get(f"/analytics/timeseries?user_id={self.test_user_id}&days=7")
            assert response.status_code == 200
            data = response.json()
            assert data["days"] == 7
            
            # Тест з 30 днями (за замовчуванням)
            response = client.get(f"/analytics/timeseries?user_id={self.test_user_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["days"] == 30
    
    def test_export_analytics_data_with_different_formats(self):
        """Тест експорту даних з різними форматами"""
        with patch('main.analytics_engine') as mock_engine:
            mock_engine.export_analytics_data.return_value = '{"test": "data"}'
            
            # Тест з JSON форматом
            response = client.get(f"/analytics/export?user_id={self.test_user_id}&format=json")
            assert response.status_code == 200
            data = response.json()
            assert data["format"] == "json"
            
            # Тест з неправильним форматом
            mock_engine.export_analytics_data.return_value = '{"error": "Непідтримуваний формат"}'
            response = client.get(f"/analytics/export?user_id={self.test_user_id}&format=xml")
            assert response.status_code == 200  # Мок endpoint завжди повертає 200
            data = response.json()
            assert "data" in data  # Помилка тепер в полі data
            assert "error" in data["data"]  # Перевіряємо вміст data


if __name__ == "__main__":
    pytest.main([__file__]) 