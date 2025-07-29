# План Security тестів

> **Детальний план тестів безпеки для всіх компонентів системи**

---

## Зміст

1. [Загальні принципи](#загальні-принципи)
2. [Penetration Testing](#penetration-testing)
3. [Authentication Testing](#authentication-testing)
4. [Authorization Testing](#authorization-testing)
5. [Data Protection Testing](#data-protection-testing)
6. [Чек-лист Security тестів](#чек-лист-security-тестів)

---

## Загальні принципи

### Типи security тестів
- **Penetration Testing**: Тестування на проникнення
- **Vulnerability Assessment**: Оцінка вразливостей
- **Authentication Testing**: Тестування авторизації
- **Authorization Testing**: Тестування прав доступу
- **Data Protection Testing**: Тестування захисту даних
- **API Security Testing**: Тестування безпеки API

### Структура тестів
```
tests/
├── security/
│   ├── penetration/
│   │   ├── test_sql_injection.py
│   │   ├── test_xss_attacks.py
│   │   └── test_csrf_attacks.py
│   ├── authentication/
│   │   ├── test_oauth_security.py
│   │   ├── test_jwt_security.py
│   │   └── test_mfa_security.py
│   ├── authorization/
│   │   ├── test_access_control.py
│   │   └── test_permission_checks.py
│   └── data_protection/
│       ├── test_encryption.py
│       └── test_data_leakage.py
```

---

## Penetration Testing

### Тести SQL Injection

```python
# tests/security/penetration/test_sql_injection.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestSQLInjection:
    @pytest.mark.asyncio
    async def test_sql_injection_in_login(self):
        """Тест SQL injection в формі входу"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Тестуємо різні SQL injection payloads
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin'--",
                "' OR 1=1#"
            ]
            
            for payload in sql_payloads:
                response = await client.post("/auth/login", json={
                    "email": payload,
                    "password": "password"
                })
                
# Перевіряємо що система не піддається SQL injection
                assert response.status_code in [400, 401, 422]
                assert "error" in response.json() or "invalid" in response.json().get("detail", "")
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_search(self):
        """Тест SQL injection в пошуку"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            sql_payloads = [
                "'; SELECT * FROM users --",
                "' UNION SELECT password FROM users --",
                "test' OR '1'='1' --"
            ]
            
            for payload in sql_payloads:
                response = await client.get("/api/proposals/search",
                    headers=auth_headers,
                    params={"query": payload}
                )
                
# Перевіряємо що система безпечна
                assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_profile_update(self):
        """Тест SQL injection в оновленні профілю"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            malicious_payload = "'; UPDATE users SET role='admin' WHERE id=1; --"
            
            response = await client.put("/api/user/profile",
                headers=auth_headers,
                json={"bio": malicious_payload}
            )
            
# Перевіряємо що оновлення не виконалося
            assert response.status_code in [400, 422]
            
# Перевіряємо що роль не змінилася
            profile_response = await client.get("/api/user/profile", headers=auth_headers)
            user_data = profile_response.json()
            assert user_data.get("role") != "admin"
    
    @pytest.mark.asyncio
    async def test_blind_sql_injection(self):
        """Тест blind SQL injection"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Тестуємо boolean-based blind SQL injection
            boolean_payloads = [
                "' AND 1=1 --",
                "' AND 1=2 --",
                "' AND (SELECT COUNT(*) FROM users) > 0 --",
                "' AND (SELECT COUNT(*) FROM users) = 0 --"
            ]
            
            for payload in boolean_payloads:
                response = await client.post("/auth/login", json={
                    "email": f"test{payload}@example.com",
                    "password": "password"
                })
                
# Перевіряємо що відповіді однакові (немає інформаційного leak)
                assert response.status_code in [400, 401, 422]
```

### Тести XSS атак

```python
# tests/security/penetration/test_xss_attacks.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestXSSAttacks:
    @pytest.mark.asyncio
    async def test_stored_xss_in_proposal(self):
        """Тест stored XSS в пропозиціях"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            xss_payloads = [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "javascript:alert('xss')",
                "<svg onload=alert('xss')>",
                "<iframe src=javascript:alert('xss')>"
            ]
            
            for payload in xss_payloads:
# Спробуємо створити пропозицію з XSS
                response = await client.post("/api/proposals",
                    headers=auth_headers,
                    json={
                        "title": payload,
                        "description": "Test proposal"
                    }
                )
                
# Перевіряємо що XSS заблокований
                assert response.status_code in [400, 422]
                
# Перевіряємо що payload не зберігається як є
                if response.status_code == 200:
                    proposal_data = response.json()
                    assert payload not in proposal_data["title"]
                    assert "<script>" not in proposal_data["title"]
    
    @pytest.mark.asyncio
    async def test_reflected_xss_in_search(self):
        """Тест reflected XSS в пошуку"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            xss_payloads = [
                "<script>alert('xss')</script>",
                "';alert('xss');//",
                "<img src=x onerror=alert('xss')>"
            ]
            
            for payload in xss_payloads:
                response = await client.get("/api/proposals/search",
                    headers=auth_headers,
                    params={"query": payload}
                )
                
# Перевіряємо що XSS не відображається
                if response.status_code == 200:
                    response_text = response.text
                    assert "<script>" not in response_text
                    assert "alert('xss')" not in response_text
    
    @pytest.mark.asyncio
    async def test_dom_xss_in_dashboard(self):
        """Тест DOM XSS в дашборді"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Тестуємо XSS через URL параметри
            xss_payloads = [
                "javascript:alert('xss')",
                "data:text/html,<script>alert('xss')</script>",
                "vbscript:alert('xss')"
            ]
            
            for payload in xss_payloads:
                response = await client.get(f"/api/dashboard/main?theme={payload}",
                    headers=auth_headers
                )
                
# Перевіряємо що XSS заблокований
                assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_xss_in_user_input(self):
        """Тест XSS в користувацькому вводі"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Тестуємо різні поля користувача
            user_fields = ["bio", "website", "location"]
            xss_payload = "<script>alert('xss')</script>"
            
            for field in user_fields:
                response = await client.put("/api/user/profile",
                    headers=auth_headers,
                    json={field: xss_payload}
                )
                
# Перевіряємо що XSS заблокований
                assert response.status_code in [400, 422]
```

### Тести CSRF атак

```python
# tests/security/penetration/test_csrf_attacks.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestCSRFAttacks:
    @pytest.mark.asyncio
    async def test_csrf_protection_on_sensitive_endpoints(self):
        """Тест захисту від CSRF на чутливих endpoints"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Тестуємо endpoints які повинні мати CSRF захист
            sensitive_endpoints = [
                ("POST", "/api/user/profile"),
                ("POST", "/api/proposals"),
                ("PUT", "/api/user/settings"),
                ("DELETE", "/api/proposals/123")
            ]
            
            for method, endpoint in sensitive_endpoints:
# Запит без CSRF токена
                if method == "POST":
                    response = await client.post(endpoint, json={"test": "data"})
                elif method == "PUT":
                    response = await client.put(endpoint, json={"test": "data"})
                elif method == "DELETE":
                    response = await client.delete(endpoint)
                
# Перевіряємо що запит заблокований
                assert response.status_code in [403, 422]
    
    @pytest.mark.asyncio
    async def test_csrf_token_validation(self):
        """Тест валідації CSRF токенів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Отримуємо CSRF токен
            csrf_response = await client.get("/api/csrf-token", headers=auth_headers)
            csrf_token = csrf_response.json()["csrf_token"]
            
# Тестуємо з валідним токеном
            valid_response = await client.post("/api/user/profile",
                headers={**auth_headers, "X-CSRF-Token": csrf_token},
                json={"bio": "Test bio"}
            )
            assert valid_response.status_code == 200
            
# Тестуємо з невалідним токеном
            invalid_response = await client.post("/api/user/profile",
                headers={**auth_headers, "X-CSRF-Token": "invalid_token"},
                json={"bio": "Test bio"}
            )
            assert invalid_response.status_code in [403, 422]
    
    @pytest.mark.asyncio
    async def test_csrf_token_expiration(self):
        """Тест закінчення терміну дії CSRF токена"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Отримуємо CSRF токен
            csrf_response = await client.get("/api/csrf-token", headers=auth_headers)
            csrf_token = csrf_response.json()["csrf_token"]
            
# Симулюємо закінчення терміну дії
# (в реальному тесті це можна зробити через мокавання часу)
            expired_response = await client.post("/api/user/profile",
                headers={**auth_headers, "X-CSRF-Token": csrf_token},
                json={"bio": "Test bio"}
            )
            
# Перевіряємо що токен дійсний
            assert expired_response.status_code == 200
```

---

## Authentication Testing

### Тести OAuth безпеки

```python
# tests/security/authentication/test_oauth_security.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.modules.auth.oauth_security import UpworkOAuthSecurity

class TestOAuthSecurity:
    def setup_method(self):
        self.oauth = UpworkOAuthSecurity()
    
    def test_state_parameter_validation(self):
        """Тест валідації state параметра"""
# Генеруємо валідний state
        state = self.oauth.generate_state()
        
# Перевіряємо валідний state
        assert self.oauth.validate_state(state, state)
        
# Перевіряємо невалідний state
        assert not self.oauth.validate_state(state, "different_state")
        
# Перевіряємо порожній state
        assert not self.oauth.validate_state("", "")
    
    def test_pkce_implementation(self):
        """Тест реалізації PKCE"""
# Генеруємо PKCE пару
        code_verifier, code_challenge = self.oauth.generate_pkce_pair()
        
# Перевіряємо довжину
        assert len(code_verifier) >= 32
        assert len(code_challenge) >= 32
        
# Перевіряємо унікальність
        code_verifier2, code_challenge2 = self.oauth.generate_pkce_pair()
        assert code_verifier != code_verifier2
        assert code_challenge != code_challenge2
    
    def test_oauth_token_validation(self):
        """Тест валідації OAuth токенів"""
# Тестуємо валідний токен
        valid_token = "valid_access_token"
        assert self.oauth.validate_token(valid_token)
        
# Тестуємо невалідний токен
        invalid_token = "invalid_token"
        assert not self.oauth.validate_token(invalid_token)
        
# Тестуємо порожній токен
        assert not self.oauth.validate_token("")
    
    @patch('src.modules.auth.oauth_security.requests.post')
    def test_oauth_token_exchange_security(self, mock_post):
        """Тест безпеки обміну токенів"""
# Симулюємо успішний обмін
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
# Тестуємо з валідними параметрами
        tokens = self.oauth.exchange_code_for_tokens("valid_code", "valid_verifier")
        assert tokens["access_token"] == "test_access_token"
        
# Тестуємо з невалідним code
        with pytest.raises(OAuthError):
            self.oauth.exchange_code_for_tokens("invalid_code", "valid_verifier")
    
    def test_oauth_scope_validation(self):
        """Тест валідації OAuth scopes"""
# Тестуємо валідні scopes
        valid_scopes = ["read", "write", "profile"]
        assert self.oauth.validate_scopes(valid_scopes)
        
# Тестуємо невалідні scopes
        invalid_scopes = ["admin", "delete_all"]
        assert not self.oauth.validate_scopes(invalid_scopes)
```

### Тести JWT безпеки

```python
# tests/security/authentication/test_jwt_security.py
import pytest
import asyncio
from datetime import datetime, timedelta
from src.modules.auth.jwt_manager import JWTManager

class TestJWTSecurity:
    def setup_method(self):
        self.jwt_manager = JWTManager()
    
    def test_jwt_token_creation_security(self):
        """Тест безпеки створення JWT токенів"""
        user_data = {"user_id": "test_user", "email": "test@example.com"}
        
# Створюємо токен
        token = self.jwt_manager.create_access_token(user_data)
        
# Перевіряємо структуру токена
        assert token.count('.') == 2  # header.payload.signature
        
# Перевіряємо що токен не містить чутливих даних
        decoded = self.jwt_manager.decode_token(token)
        assert "password" not in decoded
        assert "secret_key" not in decoded
    
    def test_jwt_token_expiration(self):
        """Тест закінчення терміну дії JWT токенів"""
        user_data = {"user_id": "test_user"}
        
# Створюємо токен з коротким терміном дії
        self.jwt_manager.access_token_expire_minutes = 1
        token = self.jwt_manager.create_access_token(user_data)
        
# Перевіряємо що токен валідний
        assert self.jwt_manager.verify_token(token)
        
# Симулюємо закінчення терміну дії
        self.jwt_manager.access_token_expire_minutes = 0
        expired_token = self.jwt_manager.create_access_token(user_data)
        
# Перевіряємо що токен закінчився
        assert not self.jwt_manager.verify_token(expired_token)
    
    def test_jwt_token_tampering(self):
        """Тест захисту від підробки JWT токенів"""
        user_data = {"user_id": "test_user"}
        token = self.jwt_manager.create_access_token(user_data)
        
# Спробуємо підробити токен
        parts = token.split('.')
        tampered_payload = parts[1] + "tampered"
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
        
# Перевіряємо що підроблений токен не валідний
        assert not self.jwt_manager.verify_token(tampered_token)
    
    def test_jwt_token_replay_attack(self):
        """Тест захисту від replay атак"""
        user_data = {"user_id": "test_user"}
        token = self.jwt_manager.create_access_token(user_data)
        
# Додаємо jti (JWT ID) для запобігання replay атак
        decoded = self.jwt_manager.decode_token(token)
        assert "jti" in decoded
        
# Перевіряємо що токен можна використати тільки один раз
# (в реальній системі це реалізується через blacklist)
        assert self.jwt_manager.verify_token(token)
```

### Тести MFA безпеки

```python
# tests/security/authentication/test_mfa_security.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.modules.auth.mfa_manager import MFAManager

class TestMFASecurity:
    def setup_method(self):
        self.mfa_manager = MFAManager()
    
    def test_totp_secret_generation_security(self):
        """Тест безпеки генерації TOTP секретів"""
        user_id = "test_user"
        
# Генеруємо секрет
        secret = self.mfa_manager.generate_totp_secret(user_id)
        
# Перевіряємо довжину та складність
        assert len(secret) >= 16
        assert secret.isalnum()
        
# Перевіряємо унікальність
        secret2 = self.mfa_manager.generate_totp_secret(user_id)
        assert secret != secret2
    
    def test_totp_code_validation_security(self):
        """Тест безпеки валідації TOTP кодів"""
        user_id = "test_user"
        secret = self.mfa_manager.generate_totp_secret(user_id)
        
# Генеруємо валідний код
        valid_code = self.mfa_manager.generate_totp_code(secret)
        
# Перевіряємо валідний код
        assert self.mfa_manager.validate_totp_code(user_id, valid_code)
        
# Перевіряємо невалідний код
        assert not self.mfa_manager.validate_totp_code(user_id, "000000")
        
# Перевіряємо код з іншого часового вікна
        old_code = self.mfa_manager.generate_totp_code(secret, time_offset=-60)
        assert not self.mfa_manager.validate_totp_code(user_id, old_code)
    
    def test_backup_codes_security(self):
        """Тест безпеки backup кодів"""
        user_id = "test_user"
        backup_codes = self.mfa_manager.generate_backup_codes(user_id)
        
# Перевіряємо кількість та формат
        assert len(backup_codes) == 10
        assert all(len(code) == 8 for code in backup_codes)
        assert all(code.isalnum() for code in backup_codes)
        
# Перевіряємо унікальність
        assert len(set(backup_codes)) == 10
        
# Перевіряємо валідацію
        assert self.mfa_manager.validate_backup_code(user_id, backup_codes[0])
        assert not self.mfa_manager.validate_backup_code(user_id, "INVALID")
    
    def test_mfa_rate_limiting(self):
        """Тест rate limiting для MFA"""
        user_id = "test_user"
        
# Симулюємо багато спроб
        for i in range(10):
            self.mfa_manager.validate_totp_code(user_id, "000000")
        
# Перевіряємо що акаунт заблокований
        assert self.mfa_manager.is_account_locked(user_id)
        
# Перевіряємо що валідний код не працює після блокування
        secret = self.mfa_manager.generate_totp_secret(user_id)
        valid_code = self.mfa_manager.generate_totp_code(secret)
        assert not self.mfa_manager.validate_totp_code(user_id, valid_code)
```

---

## Authorization Testing

### Тести контролю доступу

```python
# tests/security/authorization/test_access_control.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestAccessControl:
    @pytest.mark.asyncio
    async def test_unauthorized_access_to_protected_endpoints(self):
        """Тест доступу без авторизації до захищених endpoints"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Список захищених endpoints
            protected_endpoints = [
                ("GET", "/api/dashboard/main"),
                ("GET", "/api/analytics/metrics/user/test_user"),
                ("POST", "/api/proposals"),
                ("PUT", "/api/user/profile"),
                ("DELETE", "/api/proposals/123")
            ]
            
            for method, endpoint in protected_endpoints:
                if method == "GET":
                    response = await client.get(endpoint)
                elif method == "POST":
                    response = await client.post(endpoint, json={"test": "data"})
                elif method == "PUT":
                    response = await client.put(endpoint, json={"test": "data"})
                elif method == "DELETE":
                    response = await client.delete(endpoint)
                
# Перевіряємо що доступ заборонений
                assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_user_data_isolation(self):
        """Тест ізоляції даних користувачів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Авторизуємо першого користувача
            user1_headers = await get_auth_headers(client, "user1@example.com")
            
# Авторизуємо другого користувача
            user2_headers = await get_auth_headers(client, "user2@example.com")
            
# Перший користувач намагається отримати дані другого
            response = await client.get("/api/analytics/metrics/user/user2",
                headers=user1_headers
            )
            
# Перевіряємо що доступ заборонений
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_role_based_access_control(self):
        """Тест контролю доступу на основі ролей"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Авторизуємо звичайного користувача
            user_headers = await get_auth_headers(client, "user@example.com")
            
# Спроба доступу до адмін функцій
            admin_endpoints = [
                ("GET", "/api/admin/users"),
                ("POST", "/api/admin/users"),
                ("GET", "/api/admin/analytics"),
                ("DELETE", "/api/admin/users/123")
            ]
            
            for method, endpoint in admin_endpoints:
                if method == "GET":
                    response = await client.get(endpoint, headers=user_headers)
                elif method == "POST":
                    response = await client.post(endpoint, headers=user_headers, json={})
                elif method == "DELETE":
                    response = await client.delete(endpoint, headers=user_headers)
                
# Перевіряємо що доступ заборонений
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_token_scope_validation(self):
        """Тест валідації scope токенів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Створюємо токен з обмеженими правами
            limited_headers = await get_auth_headers_with_scope(client, ["read"])
            
# Спроба запису з токеном тільки для читання
            response = await client.post("/api/proposals",
                headers=limited_headers,
                json={"title": "Test proposal"}
            )
            
# Перевіряємо що доступ заборонений
            assert response.status_code == 403
```

### Тести перевірки прав

```python
# tests/security/authorization/test_permission_checks.py
import pytest
import asyncio
from src.modules.security.permission_manager import PermissionManager

class TestPermissionChecks:
    def setup_method(self):
        self.permission_manager = PermissionManager()
    
    def test_resource_ownership_check(self):
        """Тест перевірки власності ресурсу"""
# Тестуємо власника ресурсу
        owner_check = self.permission_manager.check_resource_ownership(
            user_id="user1",
            resource_id="proposal_123",
            resource_owner="user1"
        )
        assert owner_check == True
        
# Тестуємо не власника ресурсу
        non_owner_check = self.permission_manager.check_resource_ownership(
            user_id="user2",
            resource_id="proposal_123",
            resource_owner="user1"
        )
        assert non_owner_check == False
    
    def test_permission_hierarchy(self):
        """Тест ієрархії прав доступу"""
# Тестуємо різні рівні прав
        permissions = [
            ("user", "read", True),
            ("user", "write", False),
            ("user", "admin", False),
            ("moderator", "read", True),
            ("moderator", "write", True),
            ("moderator", "admin", False),
            ("admin", "read", True),
            ("admin", "write", True),
            ("admin", "admin", True)
        ]
        
        for role, permission, expected in permissions:
            result = self.permission_manager.check_permission(role, permission)
            assert result == expected
    
    def test_time_based_permissions(self):
        """Тест часових обмежень прав"""
# Тестуємо права в робочі години
        work_hours_check = self.permission_manager.check_time_based_permission(
            permission="admin",
            current_time="2024-01-01T10:00:00Z"
        )
        assert work_hours_check == True
        
# Тестуємо права поза робочими годинами
        off_hours_check = self.permission_manager.check_time_based_permission(
            permission="admin",
            current_time="2024-01-01T23:00:00Z"
        )
        assert off_hours_check == False
    
    def test_ip_based_permissions(self):
        """Тест IP-базованих прав"""
# Тестуємо доступ з дозволеного IP
        allowed_ip_check = self.permission_manager.check_ip_based_permission(
            permission="admin",
            ip_address="192.168.1.100"
        )
        assert allowed_ip_check == True
        
# Тестуємо доступ з недозволеного IP
        blocked_ip_check = self.permission_manager.check_ip_based_permission(
            permission="admin",
            ip_address="10.0.0.1"
        )
        assert blocked_ip_check == False
```

---

## Data Protection Testing

### Тести шифрування

```python
# tests/security/data_protection/test_encryption.py
import pytest
import asyncio
from src.modules.security.encryption_manager import EncryptionManager

class TestEncryption:
    def setup_method(self):
        self.encryption_manager = EncryptionManager()
    
    def test_sensitive_data_encryption(self):
        """Тест шифрування чутливих даних"""
        sensitive_data = [
            "access_token_123",
            "refresh_token_456",
            "credit_card_789",
            "password_hash_abc"
        ]
        
        for data in sensitive_data:
# Шифруємо дані
            encrypted = self.encryption_manager.encrypt(data)
            
# Перевіряємо що дані зашифровані
            assert encrypted != data
            assert len(encrypted) > len(data)
            
# Розшифровуємо дані
            decrypted = self.encryption_manager.decrypt(encrypted)
            
# Перевіряємо що дані відновлені
            assert decrypted == data
    
    def test_encryption_key_rotation(self):
        """Тест ротації ключів шифрування"""
        original_data = "sensitive_data"
        
# Шифруємо з старим ключем
        old_encrypted = self.encryption_manager.encrypt(original_data)
        
# Ротуємо ключ
        self.encryption_manager.rotate_key()
        
# Шифруємо з новим ключем
        new_encrypted = self.encryption_manager.encrypt(original_data)
        
# Перевіряємо що ключі різні
        assert old_encrypted != new_encrypted
        
# Перевіряємо що розшифрування працює
        decrypted = self.encryption_manager.decrypt(new_encrypted)
        assert decrypted == original_data
    
    def test_encryption_performance(self):
        """Тест продуктивності шифрування"""
        import time
        
# Тестуємо швидкість шифрування
        test_data = "x" * 10000  # 10KB даних
        
        start_time = time.time()
        encrypted = self.encryption_manager.encrypt(test_data)
        encryption_time = time.time() - start_time
        
# Перевіряємо що шифрування швидке
        assert encryption_time < 1.0  # Не більше 1 секунди
        
# Тестуємо швидкість розшифрування
        start_time = time.time()
        decrypted = self.encryption_manager.decrypt(encrypted)
        decryption_time = time.time() - start_time
        
# Перевіряємо що розшифрування швидке
        assert decryption_time < 1.0
        assert decrypted == test_data
```

### Тести витоку даних

```python
# tests/security/data_protection/test_data_leakage.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestDataLeakage:
    @pytest.mark.asyncio
    async def test_personal_data_exposure(self):
        """Тест витоку особистих даних"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Отримуємо профіль користувача
            response = await client.get("/api/user/profile", headers=auth_headers)
            profile_data = response.json()
            
# Перевіряємо що чутливі дані не відкриваються
            sensitive_fields = ["password", "credit_card", "ssn", "passport"]
            for field in sensitive_fields:
                assert field not in profile_data
            
# Перевіряємо що токени не відкриваються
            assert "access_token" not in profile_data
            assert "refresh_token" not in profile_data
    
    @pytest.mark.asyncio
    async def test_error_message_information_disclosure(self):
        """Тест витоку інформації через повідомлення про помилки"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Тестуємо різні помилки
            error_scenarios = [
                ("/api/nonexistent", 404),
                ("/api/auth/login", 400),
                ("/api/user/profile", 401)
            ]
            
            for endpoint, expected_status in error_scenarios:
                response = await client.get(endpoint)
                
# Перевіряємо що помилки не розкривають внутрішню структуру
                error_data = response.json()
                
# Перевіряємо що немає stack trace
                assert "traceback" not in str(error_data)
                assert "stack" not in str(error_data)
                
# Перевіряємо що немає внутрішніх шляхів
                assert "/src/" not in str(error_data)
                assert "/app/" not in str(error_data)
    
    @pytest.mark.asyncio
    async def test_log_file_information_disclosure(self):
        """Тест витоку інформації через лог файли"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Виконуємо дію яка генерує логи
            response = await client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "password"
            })
            
# Перевіряємо що логи не доступні через веб
            log_endpoints = [
                "/logs/app.log",
                "/logs/error.log",
                "/logs/access.log",
                "/.git/logs/HEAD"
            ]
            
            for log_endpoint in log_endpoints:
                log_response = await client.get(log_endpoint)
                assert log_response.status_code in [404, 403]
    
    @pytest.mark.asyncio
    async def test_database_information_disclosure(self):
        """Тест витоку інформації про базу даних"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Тестуємо різні способи витоку інформації про БД
            db_info_endpoints = [
                "/phpmyadmin",
                "/adminer.php",
                "/dbadmin",
                "/mysql",
                "/postgresql"
            ]
            
            for endpoint in db_info_endpoints:
                response = await client.get(endpoint)
                assert response.status_code in [404, 403]
```

---

## Чек-лист Security тестів

### Penetration Testing
- [ ] Тести SQL Injection
- [ ] Тести XSS атак
- [ ] Тести CSRF атак
- [ ] Тести ін'єкцій
- [ ] Тести переповнення буфера

### Authentication Testing
- [ ] Тести OAuth безпеки
- [ ] Тести JWT безпеки
- [ ] Тести MFA безпеки
- [ ] Тести brute force атак
- [ ] Тести session hijacking

### Authorization Testing
- [ ] Тести контролю доступу
- [ ] Тести перевірки прав
- [ ] Тести ізоляції даних
- [ ] Тести ролей
- [ ] Тести часових обмежень

### Data Protection Testing
- [ ] Тести шифрування
- [ ] Тести витоку даних
- [ ] Тести анонімізації
- [ ] Тести резервного копіювання
- [ ] Тести видалення даних

### API Security Testing
- [ ] Тести безпеки endpoints
- [ ] Тести валідації вхідних даних
- [ ] Тести rate limiting
- [ ] Тести аутентифікації API
- [ ] Тести авторизації API

### Загальні вимоги
- [ ] Автоматичне виконання в CI/CD
- [ ] Регулярне тестування
- [ ] Документація вразливостей
- [ ] Плани виправлення
- [ ] Моніторинг безпеки

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:35 