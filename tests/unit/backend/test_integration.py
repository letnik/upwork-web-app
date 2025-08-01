import pytest
import sys
import os
from pathlib import Path

# Додаємо шлях до backend модулів
backend_path = Path(__file__).parent.parent.parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

class TestIntegration:
    """Інтеграційні тести"""
    
    def test_service_integration_structure(self):
        """Перевіряємо структуру інтеграції сервісів"""
        services = [
            "ai-service",
            "auth-service", 
            "analytics-service",
            "notification-service",
            "upwork-service"
        ]
        
        for service in services:
            service_path = backend_path / "services" / service
            assert service_path.exists(), f"Service {service} does not exist"
            assert (service_path / "src").exists(), f"Service {service} has no src directory"
            assert (service_path / "src" / "main.py").exists(), f"Service {service} has no main.py"
    
    def test_shared_modules_integration(self):
        """Перевіряємо інтеграцію shared модулів"""
        shared_modules = [
            "utils/encryption.py",
            "utils/rate_limiter.py", 
            "utils/validation_middleware.py",
            "utils/oauth_manager.py",
            "utils/auth_middleware.py",
            "database/connection.py",
            "config/settings.py",
            "config/logging.py"
        ]
        
        for module in shared_modules:
            module_path = backend_path / "shared" / module
            assert module_path.exists(), f"Shared module {module} does not exist"
    
    def test_api_gateway_integration(self):
        """Перевіряємо інтеграцію API Gateway"""
        api_gateway_path = backend_path / "api-gateway"
        assert api_gateway_path.exists()
        assert (api_gateway_path / "src" / "main.py").exists()
    
    def test_data_integration(self):
        """Перевіряємо інтеграцію даних"""
        data_path = backend_path / "data"
        assert data_path.exists()
        assert (data_path / "mock_upwork_data.py").exists()
    
    def test_project_structure_integration(self):
        """Перевіряємо загальну інтеграцію структури проекту"""
        # Перевіряємо основні компоненти
        main_components = [
            "services",
            "api-gateway", 
            "shared",
            "data"
        ]
        
        for component in main_components:
            component_path = backend_path / component
            assert component_path.exists(), f"Component {component} does not exist"
            assert component_path.is_dir(), f"Component {component} is not a directory"
    
    def test_file_permissions_integration(self):
        """Перевіряємо інтеграцію прав доступу до файлів"""
        # Перевіряємо, що всі Python файли мають правильні права
        python_files = list(backend_path.rglob("*.py"))
        
        for file_path in python_files:
            if "venv" not in str(file_path) and "__pycache__" not in str(file_path):
                assert file_path.exists(), f"File {file_path} does not exist"
                assert file_path.is_file(), f"{file_path} is not a file"
                assert os.access(file_path, os.R_OK), f"File {file_path} is not readable"
    
    def test_import_structure_integration(self):
        """Перевіряємо інтеграцію структури імпортів"""
        # Перевіряємо, що всі __init__.py файли існують
        init_files = [
            "shared/__init__.py",
            "shared/utils/__init__.py",
            "shared/database/__init__.py",
            "shared/config/__init__.py"
        ]
        
        for init_file in init_files:
            init_path = backend_path / init_file
            assert init_path.exists(), f"Init file {init_file} does not exist" 