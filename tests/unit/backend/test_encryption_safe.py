"""
Безпечні тести для системи шифрування токенів
SECURITY-007: Шифрування токенів та чутливих даних
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))

from shared.utils.encryption import (
    EncryptionManager, TokenEncryptionManager, SensitiveDataEncryptionManager,
    encrypt_token, decrypt_token,
    encrypt_sensitive_data, decrypt_sensitive_data,
    generate_secure_token, hash_token, verify_token_hash,
    encrypt_data, decrypt_data
)


class TestTokenEncryption:
    """Тести шифрування токенів"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.encryption_manager = EncryptionManager("test-key-12345")
        self.token_manager = TokenEncryptionManager("test-key-12345")
    
    def test_encrypt_decrypt_token(self):
        """Тест шифрування та розшифрування токена"""
        # Тестові дані
        test_token = "test-jwt-token-12345"
        metadata = {"user_id": 123, "session_id": "session-456"}
        
        # Шифруємо токен
        encrypted_token = self.token_manager.encrypt_token(test_token, metadata)
        
        # Перевіряємо що токен зашифрований
        assert encrypted_token != test_token
        assert len(encrypted_token) > len(test_token)
        
        # Розшифровуємо токен
        decrypted_data = self.token_manager.decrypt_token(encrypted_token)
        
        # Перевіряємо результати
        assert decrypted_data["token"] == test_token
        assert decrypted_data["metadata"]["user_id"] == 123
        assert decrypted_data["metadata"]["session_id"] == "session-456"
        assert "timestamp" in decrypted_data
    
    def test_token_integrity_verification(self):
        """Тест перевірки цілісності токена"""
        # Створюємо валідний токен
        test_token = "valid-token-12345"
        encrypted_token = self.token_manager.encrypt_token(test_token)
        
        # Перевіряємо цілісність
        assert self.token_manager.verify_token_integrity(encrypted_token) is True
        
        # Перевіряємо невалідний токен
        assert self.token_manager.verify_token_integrity("invalid-token") is False
    
    def test_token_with_metadata(self):
        """Тест токена з метаданими"""
        test_token = "test-token"
        metadata = {
            "user_id": 123,
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "created_at": datetime.utcnow().isoformat()
        }
        
        encrypted_token = self.token_manager.encrypt_token(test_token, metadata)
        decrypted_data = self.token_manager.decrypt_token(encrypted_token)
        
        assert decrypted_data["token"] == test_token
        assert decrypted_data["metadata"]["user_id"] == 123
        assert decrypted_data["metadata"]["ip_address"] == "192.168.1.1"
    
    def test_empty_token_handling(self):
        """Тест обробки порожніх токенів"""
        # Порожній токен
        encrypted_empty = self.token_manager.encrypt_token("")
        decrypted_empty = self.token_manager.decrypt_token(encrypted_empty)
        assert decrypted_empty["token"] == ""
        
        # None токен
        encrypted_none = self.token_manager.encrypt_token(None)
        decrypted_none = self.token_manager.decrypt_token(encrypted_none)
        assert decrypted_none["token"] == ""


class TestSensitiveDataEncryption:
    """Тести шифрування чутливих даних"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.sensitive_manager = SensitiveDataEncryptionManager("test-key-12345")
    
    def test_encrypt_decrypt_sensitive_data(self):
        """Тест шифрування та розшифрування чутливих даних"""
        # Тестові дані
        test_data = "sensitive-api-key-12345"
        data_type = "api_key"
        
        # Шифруємо дані
        encrypted_data = self.sensitive_manager.encrypt_sensitive_data(test_data, data_type)
        
        # Перевіряємо що дані зашифровані
        assert encrypted_data != test_data
        assert len(encrypted_data) > len(test_data)
        
        # Розшифровуємо дані
        decrypted_data = self.sensitive_manager.decrypt_sensitive_data(encrypted_data)
        
        # Перевіряємо результати
        assert decrypted_data == test_data
    
    def test_different_data_types(self):
        """Тест різних типів чутливих даних"""
        test_cases = [
            ("api_key", "sk-1234567890abcdef"),
            ("password", "my-secure-password"),
            ("personal_info", "John Doe, 123 Main St"),
            ("credit_card", "4111-1111-1111-1111"),
            ("ssn", "123-45-6789")
        ]
        
        for data_type, test_data in test_cases:
            encrypted = self.sensitive_manager.encrypt_sensitive_data(test_data, data_type)
            decrypted = self.sensitive_manager.decrypt_sensitive_data(encrypted)
            assert decrypted == test_data
    
    def test_empty_data_handling(self):
        """Тест обробки порожніх даних"""
        # Порожні дані
        encrypted_empty = self.sensitive_manager.encrypt_sensitive_data("", "test")
        decrypted_empty = self.sensitive_manager.decrypt_sensitive_data(encrypted_empty)
        assert decrypted_empty == ""
        
        # None дані
        encrypted_none = self.sensitive_manager.encrypt_sensitive_data(None, "test")
        decrypted_none = self.sensitive_manager.decrypt_sensitive_data(encrypted_none)
        assert decrypted_none == ""


class TestEncryptionManager:
    """Тести основного менеджера шифрування"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.manager = EncryptionManager("test-key-12345")
    
    def test_basic_encryption(self):
        """Тест базового шифрування"""
        test_data = "test-data-12345"
        
        encrypted = self.manager.encrypt(test_data)
        decrypted = self.manager.decrypt(encrypted)
        
        assert encrypted != test_data
        assert decrypted == test_data
    
    def test_dict_encryption(self):
        """Тест шифрування словника"""
        test_dict = {
            "api_key": "sk-1234567890abcdef",
            "password": "my-password",
            "normal_field": "not-encrypted",
            "empty_field": ""
        }
        
        encrypted_dict = self.manager.encrypt_dict(test_dict)
        decrypted_dict = self.manager.decrypt_dict(encrypted_dict)
        
        # Перевіряємо що зашифровані поля відрізняються
        assert encrypted_dict["api_key"] != test_dict["api_key"]
        assert encrypted_dict["password"] != test_dict["password"]
        
        # Перевіряємо що всі рядки зашифровані (поточна логіка)
        assert encrypted_dict["normal_field"] != test_dict["normal_field"]
        assert encrypted_dict["empty_field"] == test_dict["empty_field"]  # Порожні рядки не шифруються
        
        # Перевіряємо розшифрування
        assert decrypted_dict["api_key"] == test_dict["api_key"]
        assert decrypted_dict["password"] == test_dict["password"]
        assert decrypted_dict["normal_field"] == test_dict["normal_field"]
    
    def test_token_methods(self):
        """Тест методів роботи з токенами"""
        test_token = "jwt-token-12345"
        metadata = {"user_id": 123}
        
        # Шифрування токена
        encrypted_token = self.manager.encrypt_token(test_token, metadata)
        decrypted_data = self.manager.decrypt_token(encrypted_token)
        
        assert decrypted_data["token"] == test_token
        assert decrypted_data["metadata"]["user_id"] == 123
        
        # Перевірка цілісності
        assert self.manager.verify_token_integrity(encrypted_token) is True
    
    def test_sensitive_data_methods(self):
        """Тест методів роботи з чутливими даними"""
        test_data = "sensitive-data-12345"
        data_type = "api_key"
        
        # Шифрування чутливих даних
        encrypted_data = self.manager.encrypt_sensitive_data(test_data, data_type)
        decrypted_data = self.manager.decrypt_sensitive_data(encrypted_data)
        
        assert decrypted_data == test_data


class TestUtilityFunctions:
    """Тести утилітарних функцій"""
    
    def test_generate_secure_token(self):
        """Тест генерації безпечного токена"""
        token1 = generate_secure_token(32)
        token2 = generate_secure_token(32)
        
        assert len(token1) == 43  # base64 encoded 32 bytes
        assert len(token2) == 43
        assert token1 != token2  # Токени повинні бути різними
    
    def test_hash_token(self):
        """Тест хешування токена"""
        test_token = "test-token-12345"
        hash1 = hash_token(test_token)
        hash2 = hash_token(test_token)
        
        assert len(hash1) == 64  # SHA256 hex
        assert hash1 == hash2  # Однаковий токен дає однаковий хеш
    
    def test_verify_token_hash(self):
        """Тест перевірки хешу токена"""
        test_token = "test-token-12345"
        token_hash = hash_token(test_token)
        
        assert verify_token_hash(test_token, token_hash) is True
        assert verify_token_hash("wrong-token", token_hash) is False
    
    def test_encrypt_decrypt_functions(self):
        """Тест швидких функцій шифрування"""
        test_data = "test-data-12345"
        
        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)
        
        assert encrypted != test_data
        assert decrypted == test_data
    
    def test_token_functions(self):
        """Тест швидких функцій роботи з токенами"""
        test_token = "jwt-token-12345"
        metadata = {"user_id": 123}
        
        encrypted_token = encrypt_token(test_token, metadata)
        decrypted_data = decrypt_token(encrypted_token)
        
        assert decrypted_data["token"] == test_token
        assert decrypted_data["metadata"]["user_id"] == 123
    
    def test_sensitive_data_functions(self):
        """Тест швидких функцій роботи з чутливими даними"""
        test_data = "sensitive-data-12345"
        data_type = "api_key"
        
        encrypted_data = encrypt_sensitive_data(test_data, data_type)
        decrypted_data = decrypt_sensitive_data(encrypted_data)
        
        assert decrypted_data == test_data


class TestErrorHandling:
    """Тести обробки помилок"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.manager = EncryptionManager("test-key-12345")
    
    def test_invalid_decryption(self):
        """Тест обробки невалідного розшифрування"""
        # Спроба розшифрувати невалідні дані
        with pytest.raises(Exception):
            self.manager.decrypt("invalid-encrypted-data")
    
    def test_invalid_token_decryption(self):
        """Тест обробки невалідного розшифрування токена"""
        # Спроба розшифрувати невалідний токен
        with pytest.raises(Exception):
            self.manager.decrypt_token("invalid-token")
    
    def test_invalid_sensitive_data_decryption(self):
        """Тест обробки невалідного розшифрування чутливих даних"""
        # Спроба розшифрувати невалідні чутливі дані
        with pytest.raises(Exception):
            self.manager.decrypt_sensitive_data("invalid-data")


class TestPerformance:
    """Тести продуктивності"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.manager = EncryptionManager("test-key-12345")
    
    def test_encryption_speed(self):
        """Тест швидкості шифрування"""
        import time
        
        test_data = "test-data-" * 1000  # Великий об'єм даних
        
        start_time = time.time()
        encrypted = self.manager.encrypt(test_data)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        decrypted = self.manager.decrypt(encrypted)
        decrypt_time = time.time() - start_time
        
        # Перевіряємо що операції виконались швидко (< 1 секунди)
        assert encrypt_time < 1.0
        assert decrypt_time < 1.0
        assert decrypted == test_data
    
    def test_token_encryption_speed(self):
        """Тест швидкості шифрування токенів"""
        import time
        
        test_token = "jwt-token-" * 100
        metadata = {"user_id": 123, "session_id": "session-456"}
        
        start_time = time.time()
        encrypted_token = self.manager.encrypt_token(test_token, metadata)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        decrypted_data = self.manager.decrypt_token(encrypted_token)
        decrypt_time = time.time() - start_time
        
        # Перевіряємо що операції виконались швидко
        assert encrypt_time < 1.0
        assert decrypt_time < 1.0
        assert decrypted_data["token"] == test_token


if __name__ == "__main__":
    pytest.main([__file__]) 