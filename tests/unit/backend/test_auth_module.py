"""
Тести для Auth модуля (AUTH-001)
Комплексні тести всіх компонентів авторизації
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'auth-service', 'src'))

from app.backend.services.auth_service.src.models import User, UserSecurity, Role, Session
from app.backend.services.auth_service.src.jwt_manager import create_access_token, create_refresh_token, verify_token
from app.backend.services.auth_service.src.mfa import generate_mfa_secret, generate_backup_codes, verify_mfa_code


class TestAuthModule:
    """Тести для Auth модуля"""
    
    def test_user_model_creation(self):
        """Тест створення моделі користувача"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_user_security_model_creation(self):
        """Тест створення моделі безпеки користувача"""
        user_security = UserSecurity(
            user_id=1,
            mfa_enabled=True,
            failed_login_attempts=0
        )
        
        assert user_security.user_id == 1
        assert user_security.mfa_enabled is True
        assert user_security.failed_login_attempts == 0
    
    def test_role_model_creation(self):
        """Тест створення моделі ролі"""
        role = Role(
            name="user",
            description="Regular user",
            permissions=["read", "write"]
        )
        
        assert role.name == "user"
        assert role.description == "Regular user"
        assert role.permissions == ["read", "write"]
    
    def test_session_model_creation(self):
        """Тест створення моделі сесії"""
        session = Session(
            user_id=1,
            session_token="encrypted_session_token",
            refresh_token="encrypted_refresh_token",
            ip_address="127.0.0.1",
            user_agent="test-agent",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert session.user_id == 1
        assert session.session_token == "encrypted_session_token"
        assert session.refresh_token == "encrypted_refresh_token"
        assert session.ip_address == "127.0.0.1"
        assert session.user_agent == "test-agent"
    
    @patch('app.backend.services.auth_service.src.jwt_manager.settings')
    def test_jwt_token_creation(self, mock_settings):
        """Тест створення JWT токенів"""
        mock_settings.JWT_SECRET_KEY = "test_secret_key"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
        
        # Тест access токена
        access_token = create_access_token({"sub": "test@example.com", "user_id": 1})
        assert access_token is not None
        assert isinstance(access_token, str)
        
        # Тест refresh токена
        refresh_token = create_refresh_token({"sub": "test@example.com", "user_id": 1})
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
    
    @patch('app.backend.services.auth_service.src.jwt_manager.settings')
    def test_jwt_token_verification(self, mock_settings):
        """Тест верифікації JWT токенів"""
        mock_settings.JWT_SECRET_KEY = "test_secret_key"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Створюємо токен
        token_data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(token_data)
        
        # Верифікуємо токен
        payload = verify_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
    
    def test_mfa_secret_generation(self):
        """Тест генерації MFA секрету"""
        secret = generate_mfa_secret()
        
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) > 0
    
    def test_backup_codes_generation(self):
        """Тест генерації резервних кодів"""
        codes = generate_backup_codes(count=5)
        
        assert len(codes) == 5
        assert all(isinstance(code, str) for code in codes)
        assert all(len(code) == 8 for code in codes)
        assert all(code.isdigit() for code in codes)
    
    def test_mfa_code_verification(self):
        """Тест перевірки MFA коду"""
        secret = generate_mfa_secret()
        
        # Тест правильного коду (мокаємо TOTP)
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp_instance = Mock()
            mock_totp_instance.verify.return_value = True
            mock_totp.return_value = mock_totp_instance
            
            result = verify_mfa_code(secret, "123456")
            assert result is True
    
    def test_auth_module_structure(self):
        """Тест структури Auth модуля"""
        # Перевіряємо що всі необхідні компоненти існують
        from app.backend.services.auth_service.src import models, jwt_manager, oauth, mfa
        
        assert hasattr(models, 'User')
        assert hasattr(models, 'UserSecurity')
        assert hasattr(models, 'Role')
        assert hasattr(models, 'Session')
        
        assert hasattr(jwt_manager, 'create_access_token')
        assert hasattr(jwt_manager, 'create_refresh_token')
        assert hasattr(jwt_manager, 'verify_token')
        
        assert hasattr(oauth, 'router')
        assert hasattr(mfa, 'router')
    
    def test_auth_endpoints_availability(self):
        """Тест доступності Auth endpoints"""
        # Перевіряємо що всі роутери підключені
        from app.backend.services.auth_service.src.main import app
        
        # Отримуємо всі роути
        routes = [route.path for route in app.routes]
        
        # Перевіряємо наявність основних endpoints
        assert "/" in routes
        assert "/health" in routes
        assert "/auth/register" in routes
        assert "/auth/login" in routes
        assert "/auth/profile" in routes
    
    def test_auth_security_features(self):
        """Тест функцій безпеки Auth модуля"""
        # Перевіряємо наявність функцій безпеки
        from app.backend.services.auth_service.src.models import SecurityLog, OAuthConnection
        
        assert SecurityLog is not None
        assert OAuthConnection is not None
        
        # Перевіряємо поля безпеки
        security_log = SecurityLog(
            user_id=1,
            event_type="login",
            ip_address="127.0.0.1",
            success=True
        )
        
        assert security_log.user_id == 1
        assert security_log.event_type == "login"
        assert security_log.success is True
    
    def test_auth_oauth_integration(self):
        """Тест OAuth інтеграції"""
        from app.backend.services.auth_service.src.models import OAuthConnection
        
        oauth_connection = OAuthConnection(
            user_id=1,
            provider="upwork",
            provider_user_id="upwork_user_123",
            access_token="encrypted_access_token",
            refresh_token="encrypted_refresh_token",
            scopes=["jobs:read", "jobs:write"]
        )
        
        assert oauth_connection.user_id == 1
        assert oauth_connection.provider == "upwork"
        assert oauth_connection.provider_user_id == "upwork_user_123"
        assert "jobs:read" in oauth_connection.scopes


class TestAuthModuleIntegration:
    """Інтеграційні тести для Auth модуля"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock для сесії бази даних"""
        return Mock()
    
    def test_user_registration_flow(self, mock_db_session):
        """Тест процесу реєстрації користувача"""
        # Створюємо користувача
        user = User(
            email="newuser@example.com",
            password_hash="hashed_password",
            first_name="New",
            last_name="User"
        )
        
        # Створюємо запис безпеки
        user_security = UserSecurity(
            user_id=user.id,
            mfa_enabled=False,
            failed_login_attempts=0
        )
        
        assert user.email == "newuser@example.com"
        assert user_security.mfa_enabled is False
    
    def test_user_login_flow(self, mock_db_session):
        """Тест процесу входу користувача"""
        # Створюємо користувача
        user = User(
            email="loginuser@example.com",
            password_hash="hashed_password"
        )
        
        # Створюємо сесію
        session = Session(
            user_id=user.id,
            session_token="encrypted_session_token",
            refresh_token="encrypted_refresh_token",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert session.user_id == user.id
        assert session.session_token is not None
        assert session.refresh_token is not None
    
    def test_mfa_setup_flow(self, mock_db_session):
        """Тест процесу налаштування MFA"""
        # Генеруємо секрет
        secret = generate_mfa_secret()
        
        # Генеруємо резервні коди
        backup_codes = generate_backup_codes(count=10)
        
        # Створюємо запис безпеки з MFA
        user_security = UserSecurity(
            user_id=1,
            mfa_enabled=True,
            mfa_secret=secret,
            mfa_backup_codes=backup_codes
        )
        
        assert user_security.mfa_enabled is True
        assert user_security.mfa_secret == secret
        assert len(user_security.mfa_backup_codes) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 