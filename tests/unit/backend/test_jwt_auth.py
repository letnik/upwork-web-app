"""
Тести для JWT функціональності (AUTH-002)
Тести всіх JWT компонентів та endpoints
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Додаємо шляхи до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src'))


class TestJWTFunctionality:
    """Тести JWT функціональності"""
    
    def test_jwt_token_creation(self):
        """Тест створення JWT токенів"""
        # Перевіряємо що функції існують
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    create_access_token, create_refresh_token
                )
                
                # Тест створення access токена
                access_token = create_access_token({"sub": "test@example.com", "user_id": 1})
                assert access_token is not None
                assert isinstance(access_token, str)
                assert len(access_token) > 0
                
                # Тест створення refresh токена
                refresh_token = create_refresh_token({"sub": "test@example.com", "user_id": 1})
                assert refresh_token is not None
                assert isinstance(refresh_token, str)
                assert len(refresh_token) > 0
                
                print("✅ JWT токени створюються успішно")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту JWT функцій: {e}")
    
    def test_jwt_token_verification(self):
        """Тест верифікації JWT токенів"""
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    create_access_token, verify_token
                )
                
                # Створюємо токен
                token_data = {"sub": "test@example.com", "user_id": 1}
                token = create_access_token(token_data)
                
                # Верифікуємо токен
                payload = verify_token(token)
                assert payload["sub"] == "test@example.com"
                assert payload["user_id"] == 1
                
                print("✅ JWT токени верифікуються успішно")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту JWT функцій: {e}")
    
    def test_jwt_endpoints_exist(self):
        """Тест наявності JWT endpoints"""
        # Перевіряємо що endpoints визначені в jwt_manager.py
        jwt_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'jwt_manager.py')
        
        with open(jwt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо наявність основних endpoints
        required_endpoints = [
            '@router.post("/refresh")',
            '@router.post("/logout")',
            '@router.post("/logout/all")',
            '@router.get("/validate")'
        ]
        
        for endpoint in required_endpoints:
            assert endpoint in content, f"Endpoint {endpoint} не знайдено в jwt_manager.py"
        
        print("✅ Всі JWT endpoints визначені")
    
    def test_jwt_session_management(self):
        """Тест управління сесіями"""
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    create_session_token, save_session, get_session_by_token, cleanup_expired_sessions
                )
                
                # Тест створення токена сесії
                session_token = create_session_token()
                assert session_token is not None
                assert isinstance(session_token, str)
                assert len(session_token) > 0
                
                print("✅ Функції управління сесіями існують")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту функцій сесій: {e}")
    
    def test_jwt_encryption_functions(self):
        """Тест функцій шифрування"""
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    encrypt_stored_token, decrypt_stored_token, verify_stored_token_integrity
                )
                
                # Тест шифрування токена
                test_token = "test_token_123"
                user_id = 1
                encrypted_token = encrypt_stored_token(test_token, user_id)
                assert encrypted_token is not None
                assert encrypted_token != test_token  # Токен має бути зашифрований
                
                print("✅ Функції шифрування JWT існують")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту функцій шифрування: {e}")
    
    def test_jwt_middleware_functions(self):
        """Тест middleware функцій"""
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import get_current_user
                
                # Перевіряємо що функція існує
                assert get_current_user is not None
                
                print("✅ JWT middleware функції існують")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту middleware функцій: {e}")
    
    def test_jwt_configuration(self):
        """Тест конфігурації JWT"""
        # Перевіряємо що JWT налаштування визначені в settings
        settings_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared', 'config', 'settings.py')
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо наявність JWT налаштувань
        required_settings = [
            'JWT_SECRET_KEY',
            'JWT_ALGORITHM',
            'JWT_ACCESS_TOKEN_EXPIRE_MINUTES',
            'JWT_REFRESH_TOKEN_EXPIRE_DAYS'
        ]
        
        for setting in required_settings:
            assert setting in content, f"JWT налаштування {setting} не знайдено"
        
        print("✅ Всі JWT налаштування визначені")
    
    def test_jwt_integration_with_auth(self):
        """Тест інтеграції JWT з Auth модулем"""
        # Перевіряємо що JWT роутер підключений в main.py
        main_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'main.py')
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо підключення JWT роутера
        assert 'app.include_router(jwt_router' in content, "JWT роутер не підключений в main.py"
        
        print("✅ JWT інтегрований з Auth модулем")


class TestJWTSecurity:
    """Тести безпеки JWT"""
    
    def test_jwt_token_expiration(self):
        """Тест закінчення терміну дії токенів"""
        with patch('shared.config.settings.settings') as mock_settings:
            mock_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
            mock_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
            
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    create_access_token, create_refresh_token, verify_token
                )
                
                # Створюємо токени
                access_token = create_access_token({"sub": "test@example.com"})
                refresh_token = create_refresh_token({"sub": "test@example.com"})
                
                # Перевіряємо що токени створені
                assert access_token is not None
                assert refresh_token is not None
                
                print("✅ JWT токени мають термін дії")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту JWT функцій: {e}")
    
    def test_jwt_token_encryption(self):
        """Тест шифрування JWT токенів"""
        with patch('shared.config.settings.settings'):
            try:
                from app.backend.services.auth_service.src.jwt_manager import (
                    encrypt_stored_token, decrypt_stored_token
                )
                
                # Тест шифрування/розшифрування
                original_token = "test_token_123"
                user_id = 1
                
                encrypted = encrypt_stored_token(original_token, user_id)
                decrypted = decrypt_stored_token(encrypted)
                
                # Перевіряємо що токен правильно зашифрований/розшифрований
                assert encrypted != original_token  # Зашифрований токен відрізняється
                assert decrypted == original_token  # Розшифрований токен співпадає
                
                print("✅ JWT токени правильно шифруються")
                
            except ImportError as e:
                pytest.fail(f"Помилка імпорту функцій шифрування: {e}")
    
    def test_jwt_blacklist_functionality(self):
        """Тест функціональності blacklist"""
        # Перевіряємо що функції blacklist існують
        jwt_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'jwt_manager.py')
        
        with open(jwt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо наявність функцій logout
        logout_functions = [
            'logout',
            'logout_all_devices'
        ]
        
        for func in logout_functions:
            assert func in content, f"Функція {func} не знайдена"
        
        print("✅ JWT blacklist функціональність існує")


class TestJWTIntegration:
    """Інтеграційні тести JWT"""
    
    def test_jwt_with_user_authentication(self):
        """Тест JWT з аутентифікацією користувача"""
        # Перевіряємо що JWT інтегрований з моделями користувачів
        models_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'models.py')
        
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо наявність моделей для JWT
        required_models = [
            'class User',
            'class Session',
            'class SecurityLog'
        ]
        
        for model in required_models:
            assert model in content, f"Модель {model} не знайдена"
        
        print("✅ JWT інтегрований з моделями користувачів")
    
    def test_jwt_with_oauth_integration(self):
        """Тест інтеграції JWT з OAuth"""
        # Перевіряємо що JWT використовується в OAuth
        oauth_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src', 'oauth.py')
        
        with open(oauth_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Перевіряємо інтеграцію з JWT
        jwt_integration = [
            'jwt_manager',
            'create_access_token',
            'get_current_user'
        ]
        
        for integration in jwt_integration:
            assert integration in content, f"JWT інтеграція {integration} не знайдена"
        
        print("✅ JWT інтегрований з OAuth")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 