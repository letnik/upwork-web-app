import pytest
import sys
import os
from pathlib import Path

# Додаємо шлях до backend модулів
backend_path = Path(__file__).parent.parent.parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

class TestModels:
    """Тести для моделей"""
    
    def test_auth_models_exist(self):
        """Перевіряємо, що auth моделі існують"""
        auth_models_path = backend_path / "services" / "auth-service" / "src" / "models.py"
        assert auth_models_path.exists()
    
    def test_analytics_models_exist(self):
        """Перевіряємо, що analytics моделі існують"""
        analytics_models_path = backend_path / "services" / "analytics-service" / "src" / "models.py"
        assert analytics_models_path.exists()
    
    def test_jwt_manager_exists(self):
        """Перевіряємо, що JWT manager існує"""
        jwt_manager_path = backend_path / "services" / "auth-service" / "src" / "jwt_manager.py"
        assert jwt_manager_path.exists()
    
    def test_mfa_module_exists(self):
        """Перевіряємо, що MFA модуль існує"""
        mfa_path = backend_path / "services" / "auth-service" / "src" / "mfa.py"
        assert mfa_path.exists()
    
    def test_oauth_module_exists(self):
        """Перевіряємо, що OAuth модуль існує"""
        oauth_path = backend_path / "services" / "auth-service" / "src" / "oauth.py"
        assert oauth_path.exists()
    
    def test_file_structure_valid(self):
        """Перевіряємо валідність структури файлів"""
        # Перевіряємо, що всі необхідні папки існують
        required_dirs = [
            "services/ai-service/src",
            "services/auth-service/src", 
            "services/analytics-service/src",
            "services/notification-service/src",
            "services/upwork-service/src",
            "api-gateway/src",
            "shared/utils",
            "shared/database",
            "shared/config",
            "data"
        ]
        
        for dir_path in required_dirs:
            full_path = backend_path / dir_path
            assert full_path.exists(), f"Directory {dir_path} does not exist"
    
    def test_python_files_are_readable(self):
        """Перевіряємо, що Python файли читабельні"""
        python_files = [
            "services/ai-service/src/main.py",
            "services/auth-service/src/main.py",
            "services/auth-service/src/models.py",
            "services/auth-service/src/jwt_manager.py",
            "services/auth-service/src/mfa.py",
            "services/auth-service/src/oauth.py",
            "services/analytics-service/src/main.py",
            "services/analytics-service/src/models.py",
            "services/notification-service/src/main.py",
            "services/upwork-service/src/main.py",
            "api-gateway/src/main.py",
            "shared/utils/encryption.py",
            "shared/utils/rate_limiter.py",
            "shared/utils/validation_middleware.py",
            "shared/utils/oauth_manager.py",
            "shared/utils/auth_middleware.py",
            "shared/database/connection.py",
            "shared/config/settings.py",
            "shared/config/logging.py",
            "data/mock_upwork_data.py"
        ]
        
        for file_path in python_files:
            full_path = backend_path / file_path
            assert full_path.exists(), f"File {file_path} does not exist"
            assert full_path.is_file(), f"{file_path} is not a file"
            assert os.access(full_path, os.R_OK), f"File {file_path} is not readable" 