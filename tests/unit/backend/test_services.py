import pytest
import sys
import os
from pathlib import Path

# Додаємо шлях до backend модулів
backend_path = Path(__file__).parent.parent.parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

class TestServices:
    """Тести для сервісів"""
    
    def test_ai_service_exists(self):
        """Перевіряємо, що AI сервіс існує"""
        ai_service_path = backend_path / "services" / "ai-service" / "src" / "main.py"
        assert ai_service_path.exists()
    
    def test_auth_service_exists(self):
        """Перевіряємо, що Auth сервіс існує"""
        auth_service_path = backend_path / "services" / "auth-service" / "src" / "main.py"
        assert auth_service_path.exists()
    
    def test_analytics_service_exists(self):
        """Перевіряємо, що Analytics сервіс існує"""
        analytics_service_path = backend_path / "services" / "analytics-service" / "src" / "main.py"
        assert analytics_service_path.exists()
    
    def test_notification_service_exists(self):
        """Перевіряємо, що Notification сервіс існує"""
        notification_service_path = backend_path / "services" / "notification-service" / "src" / "main.py"
        assert notification_service_path.exists()
    
    def test_upwork_service_exists(self):
        """Перевіряємо, що Upwork сервіс існує"""
        upwork_service_path = backend_path / "services" / "upwork-service" / "src" / "main.py"
        assert upwork_service_path.exists()
    
    def test_api_gateway_exists(self):
        """Перевіряємо, що API Gateway існує"""
        api_gateway_path = backend_path / "api-gateway" / "src" / "main.py"
        assert api_gateway_path.exists()
    
    def test_shared_utils_exist(self):
        """Перевіряємо, що shared утиліти існують"""
        shared_utils_path = backend_path / "shared" / "utils"
        assert shared_utils_path.exists()
        assert (shared_utils_path / "encryption.py").exists()
        assert (shared_utils_path / "rate_limiter.py").exists()
        assert (shared_utils_path / "validation_middleware.py").exists()
        assert (shared_utils_path / "oauth_manager.py").exists()
        assert (shared_utils_path / "auth_middleware.py").exists()
    
    def test_database_connection_exists(self):
        """Перевіряємо, що database connection існує"""
        db_connection_path = backend_path / "shared" / "database" / "connection.py"
        assert db_connection_path.exists()
    
    def test_config_files_exist(self):
        """Перевіряємо, що конфігураційні файли існують"""
        config_path = backend_path / "shared" / "config"
        assert config_path.exists()
        assert (config_path / "settings.py").exists()
        assert (config_path / "logging.py").exists()
    
    def test_mock_data_exists(self):
        """Перевіряємо, що mock дані існують"""
        mock_data_path = backend_path / "data" / "mock_upwork_data.py"
        assert mock_data_path.exists() 