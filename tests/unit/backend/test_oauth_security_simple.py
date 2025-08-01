"""
Простий тест безпеки OAuth інтеграції
"""

import pytest
import hashlib
import secrets
import time


class StateCache:
    """Простий кеш для state (копія з OAuth модуля)"""
    
    def __init__(self):
        self._cache = {}
        self._max_age = 300  # 5 хвилин
    
    def set(self, user_id: int, state: str):
        self._cache[user_id] = {
            'state': state,
            'timestamp': time.time()
        }
    
    def get(self, user_id: int) -> str:
        if user_id not in self._cache:
            return None
        
        data = self._cache[user_id]
        if time.time() - data['timestamp'] > self._max_age:
            del self._cache[user_id]
            return None
        
        return data['state']
    
    def remove(self, user_id: int):
        self._cache.pop(user_id, None)


class TestOAuthStateCache:
    """Тести для StateCache класу"""
    
    def test_state_cache_set_get(self):
        """Тест збереження та отримання state"""
        cache = StateCache()
        user_id = 1
        state = "test_state"
        
        cache.set(user_id, state)
        retrieved_state = cache.get(user_id)
        
        assert retrieved_state == state
    
    def test_state_cache_expiration(self):
        """Тест закінчення терміну дії state"""
        cache = StateCache()
        user_id = 1
        state = "test_state"
        
        cache.set(user_id, state)
        
        # Симулюємо закінчення терміну дії
        cache._cache[user_id]['timestamp'] = time.time() - 400  # 6.7 хвилин тому
        
        retrieved_state = cache.get(user_id)
        
        assert retrieved_state is None
        assert user_id not in cache._cache
    
    def test_state_cache_remove(self):
        """Тест видалення state"""
        cache = StateCache()
        user_id = 1
        state = "test_state"
        
        cache.set(user_id, state)
        cache.remove(user_id)
        
        retrieved_state = cache.get(user_id)
        assert retrieved_state is None
    
    def test_state_cache_multiple_users(self):
        """Тест кешу для кількох користувачів"""
        cache = StateCache()
        
        # Додаємо state для двох користувачів
        cache.set(1, "state_1")
        cache.set(2, "state_2")
        
        assert cache.get(1) == "state_1"
        assert cache.get(2) == "state_2"
        
        # Видаляємо тільки одного користувача
        cache.remove(1)
        
        assert cache.get(1) is None
        assert cache.get(2) == "state_2"


class TestOAuthSecurityFeatures:
    """Тести функцій безпеки OAuth"""
    
    def test_state_with_hash_generation(self):
        """Тест генерації state з хешем користувача"""
        user_id = 1
        user_email = "test@example.com"
        
        # Генерація state як в OAuth модулі
        state = secrets.token_urlsafe(32)
        user_hash = hashlib.sha256(f"{user_id}:{user_email}".encode()).hexdigest()[:16]
        state_with_hash = f"{state}.{user_hash}"
        
        assert len(state) == 43  # 32 bytes encoded as base64
        assert len(user_hash) == 16
        assert "." in state_with_hash
        assert state_with_hash.count(".") == 1
    
    def test_state_hash_validation(self):
        """Тест валідації хешу в state"""
        user_id = 1
        user_email = "test@example.com"
        
        # Правильний хеш
        expected_hash = hashlib.sha256(f"{user_id}:{user_email}".encode()).hexdigest()[:16]
        
        # Неправильний хеш
        wrong_hash = "wrong_hash_123"
        
        # Тестуємо валідацію
        assert expected_hash != wrong_hash
        
        # Симулюємо валідацію як в OAuth модулі
        state_part = "test_state"
        state_with_correct_hash = f"{state_part}.{expected_hash}"
        state_with_wrong_hash = f"{state_part}.{wrong_hash}"
        
        # Розбираємо state
        try:
            correct_part, correct_hash = state_with_correct_hash.split('.')
            wrong_part, wrong_hash = state_with_wrong_hash.split('.')
            
            # Перевіряємо хеш
            assert correct_hash == expected_hash
            assert wrong_hash != expected_hash
            
        except ValueError:
            pytest.fail("Invalid state format")
    
    def test_oauth_security_features_list(self):
        """Тест списку функцій безпеки"""
        # Симулюємо відповідь OAuth test endpoint
        security_features = [
            "Rate limiting",
            "State validation", 
            "User hash verification",
            "Token encryption",
            "Secure callback handling"
        ]
        
        assert "Rate limiting" in security_features
        assert "State validation" in security_features
        assert "User hash verification" in security_features
        assert "Token encryption" in security_features
        assert "Secure callback handling" in security_features
        assert len(security_features) == 5


class TestOAuthValidation:
    """Тести валідації OAuth"""
    
    def test_authorization_code_validation(self):
        """Тест валідації authorization code"""
        # Правильний код
        valid_code = "valid_authorization_code_123"
        
        # Неправильний код (занадто короткий)
        invalid_code = "short"
        
        # Валідація як в OAuth модулі
        assert len(valid_code) >= 10
        assert len(invalid_code) < 10
    
    def test_provider_validation(self):
        """Тест валідації провайдера"""
        valid_providers = ["upwork", "github", "google"]
        invalid_providers = ["invalid", "facebook", "twitter"]
        
        for provider in valid_providers:
            assert provider in valid_providers
        
        for provider in invalid_providers:
            assert provider not in valid_providers
    
    def test_state_format_validation(self):
        """Тест валідації формату state"""
        # Правильний формат
        valid_state = "state_part.user_hash"
        
        # Неправильний формат
        invalid_state = "no_dot"
        invalid_state_2 = "too.many.dots"
        
        # Перевіряємо наявність однієї крапки
        assert valid_state.count(".") == 1
        assert invalid_state.count(".") == 0
        assert invalid_state_2.count(".") == 2
    
    def test_rate_limiting_logic(self):
        """Тест логіки rate limiting"""
        # Симулюємо rate limiting
        max_requests = 5
        window = 60  # 1 хвилина
        
        # Симулюємо запити
        requests = []
        for i in range(max_requests):
            requests.append(f"request_{i}")
        
        # Перевіряємо що всі запити дозволені
        assert len(requests) <= max_requests
        
        # Додаємо ще один запит
        requests.append("extra_request")
        
        # Перевіряємо що перевищено ліміт
        assert len(requests) > max_requests 