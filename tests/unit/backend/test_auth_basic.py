"""
Простий тест для Auth модуля (AUTH-001)
Базові тести без складних імпортів
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Додаємо шляхи до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src'))


class TestAuthBasic:
    """Базові тести для Auth модуля"""
    
    def test_auth_service_structure(self):
        """Тест структури Auth сервісу"""
        # Перевіряємо що файли існують
        auth_service_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src')
        
        required_files = [
            'main.py',
            'models.py', 
            'jwt_manager.py',
            'oauth.py',
            'mfa.py',
            'session_manager.py',
            'password_reset.py'
        ]
        
        for file_name in required_files:
            file_path = os.path.join(auth_service_path, file_name)
            assert os.path.exists(file_path), f"Файл {file_name} не знайдено"
        
        print("✅ Всі необхідні файли Auth сервісу існують")
    
    def test_auth_models_structure(self):
        """Тест структури моделей Auth"""
        # Перевіряємо що моделі можна імпортувати (з моками)
        with patch('shared.database.connection.Base'):
            with patch('shared.config.settings.settings'):
                try:
                    from app.backend.services.auth_service.src.models import User, UserSecurity, Role, Session
                    print("✅ Моделі Auth імпортуються успішно")
                except ImportError as e:
                    pytest.fail(f"Помилка імпорту моделей: {e}")
    
    def test_auth_jwt_functions(self):
        """Тест JWT функцій"""
        # Перевіряємо що JWT функції існують
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    create_access_token, create_refresh_token, verify_token
                )
                print("✅ JWT функції імпортуються успішно")
            except ImportError as e:
                pytest.fail(f"Помилка імпорту JWT функцій: {e}")
    
    def test_auth_mfa_functions(self):
        """Тест MFA функцій"""
        # Перевіряємо що MFA функції існують
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.mfa import (
                    generate_mfa_secret, generate_backup_codes, verify_mfa_code
                )
                print("✅ MFA функції імпортуються успішно")
            except ImportError as e:
                pytest.fail(f"Помилка імпорту MFA функцій: {e}")
    
    def test_auth_oauth_structure(self):
        """Тест OAuth структури"""
        # Перевіряємо що OAuth роутер існує
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.oauth import router as oauth_router
                assert oauth_router is not None
                print("✅ OAuth роутер існує")
            except ImportError as e:
                pytest.fail(f"Помилка імпорту OAuth: {e}")
    
    def test_auth_mfa_structure(self):
        """Тест MFA структури"""
        # Перевіряємо що MFA роутер існує
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.mfa import router as mfa_router
                assert mfa_router is not None
                print("✅ MFA роутер існує")
            except ImportError as e:
                pytest.fail(f"Помилка імпорту MFA: {e}")
    
    def test_auth_jwt_structure(self):
        """Тест JWT структури"""
        # Перевіряємо що JWT роутер існує
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import router as jwt_router
                assert jwt_router is not None
                print("✅ JWT роутер існує")
            except ImportError as e:
                pytest.fail(f"Помилка імпорту JWT: {e}")
    
    def test_auth_endpoints_defined(self):
        """Тест що endpoints визначені"""
        # Перевіряємо що основні endpoints визначені в main.py
        main_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'main.py')
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо наявність основних endpoints
        required_endpoints = [
            '/auth/register',
            '/auth/login', 
            '/auth/profile',
            '/health'
        ]
        
        for endpoint in required_endpoints:
            assert endpoint in content, f"Endpoint {endpoint} не знайдено в main.py"
        
        print("✅ Всі необхідні endpoints визначені")
    
    def test_auth_router_integration(self):
        """Тест інтеграції роутерів"""
        # Перевіряємо що роутери підключені в main.py
        main_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'main.py')
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо підключення роутерів
        router_includes = [
            'app.include_router(oauth_router',
            'app.include_router(mfa_router',
            'app.include_router(jwt_router',
            'app.include_router(password_reset_router',
            'app.include_router(session_manager_router'
        ]
        
        for router_include in router_includes:
            assert router_include in content, f"Роутер {router_include} не підключений"
        
        print("✅ Всі роутери підключені")
    
    def test_auth_requirements(self):
        """Тест залежностей Auth сервісу"""
        # Перевіряємо що файл залежностей існує
        requirements_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'requirements', 'auth-service.txt')
        
        assert os.path.exists(requirements_path), "Файл auth-service.txt не знайдено"
        
        with open(requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо наявність основних залежностей
        required_deps = [
            'bcrypt',
            'cryptography', 
            'pyotp'
        ]
        
        for dep in required_deps:
            assert dep in content, f"Залежність {dep} не знайдена"
        
        print("✅ Всі необхідні залежності визначені")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 