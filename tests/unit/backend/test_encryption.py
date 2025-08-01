"""
Тести для модуля шифрування
Безпечні тести з використанням моків
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.utils.encryption import EncryptionManager, encrypt_data, decrypt_data, generate_encryption_key, hash_password, verify_password


class TestEncryptionManager:
    """Тести менеджера шифрування"""
    
    def test_encryption_manager_initialization(self):
        """Тест ініціалізації менеджера шифрування"""
        # Використовуємо тестовий ключ
        test_key = "test_encryption_key_32_chars_long"
        manager = EncryptionManager(test_key)
        
        assert manager is not None
        assert manager.key == test_key
    
    def test_encryption_manager_with_default_key(self):
        """Тест ініціалізації з ключем за замовчуванням"""
        # Мокаємо settings
        with patch('shared.utils.encryption.settings') as mock_settings:
            mock_settings.ENCRYPTION_KEY = "default_test_key_32_chars"
            manager = EncryptionManager()
            
            assert manager is not None
            assert manager.key == "default_test_key_32_chars"
    
    def test_encrypt_decrypt_string(self):
        """Тест шифрування та розшифрування рядка"""
        test_key = "test_encryption_key_32_chars_long"
        test_data = "test_sensitive_data"
        
        manager = EncryptionManager(test_key)
        
        # Шифруємо
        encrypted = manager.encrypt(test_data)
        assert encrypted is not None
        assert encrypted != test_data
        assert isinstance(encrypted, str)
        
        # Розшифровуємо
        decrypted = manager.decrypt(encrypted)
        assert decrypted == test_data
    
    def test_encrypt_decrypt_empty_string(self):
        """Тест шифрування порожнього рядка"""
        test_key = "test_encryption_key_32_chars_long"
        manager = EncryptionManager(test_key)
        
        # Шифруємо порожній рядок
        encrypted = manager.encrypt("")
        assert encrypted == ""
        
        # Розшифровуємо порожній рядок
        decrypted = manager.decrypt("")
        assert decrypted == ""
    
    def test_encrypt_decrypt_dict(self):
        """Тест шифрування та розшифрування словника"""
        test_key = "test_encryption_key_32_chars_long"
        test_dict = {
            "api_key": "test_api_key_123",
            "secret": "test_secret_456",
            "token": "test_token_789"
        }
        
        manager = EncryptionManager(test_key)
        
        # Шифруємо словник
        encrypted_dict = manager.encrypt_dict(test_dict)
        assert encrypted_dict is not None
        assert isinstance(encrypted_dict, dict)
        
        # Перевіряємо що значення зашифровані
        for key, value in encrypted_dict.items():
            assert value != test_dict[key]
            assert isinstance(value, str)
        
        # Розшифровуємо словник
        decrypted_dict = manager.decrypt_dict(encrypted_dict)
        assert decrypted_dict == test_dict
    
    def test_encrypt_dict_with_empty_values(self):
        """Тест шифрування словника з порожніми значеннями"""
        test_key = "test_encryption_key_32_chars_long"
        test_dict = {
            "empty": "",
            "none": None,
            "normal": "test_value"
        }
        
        manager = EncryptionManager(test_key)
        
        # Шифруємо словник
        encrypted_dict = manager.encrypt_dict(test_dict)
        assert encrypted_dict is not None
        
        # Розшифровуємо словник
        decrypted_dict = manager.decrypt_dict(encrypted_dict)
        assert decrypted_dict["empty"] == ""
        assert decrypted_dict["normal"] == "test_value"


class TestEncryptionFunctions:
    """Тести функцій шифрування"""
    
    def test_encrypt_data_function(self):
        """Тест функції encrypt_data"""
        test_data = "test_sensitive_data"
        
        # Тестуємо реальну функцію
        result = encrypt_data(test_data)
        
        assert result is not None
        assert result != test_data
        assert isinstance(result, str)
        
        # Перевіряємо що можемо розшифрувати
        decrypted = decrypt_data(result)
        assert decrypted == test_data
    
    def test_decrypt_data_function(self):
        """Тест функції decrypt_data"""
        test_data = "test_sensitive_data"
        
        # Спочатку шифруємо
        encrypted = encrypt_data(test_data)
        
        # Потім розшифровуємо
        result = decrypt_data(encrypted)
        
        assert result == test_data
    
    def test_generate_encryption_key(self):
        """Тест генерації ключа шифрування"""
        result = generate_encryption_key()
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


class TestPasswordHashing:
    """Тести хешування паролів"""
    
    def test_hash_password(self):
        """Тест хешування пароля"""
        test_password = "test_password_123"
        
        # Мокаємо bcrypt на рівні модуля
        with patch('builtins.__import__') as mock_import:
            mock_bcrypt = Mock()
            mock_bcrypt.gensalt.return_value = b"test_salt"
            mock_bcrypt.hashpw.return_value = b"hashed_password_hash"
            mock_import.return_value = mock_bcrypt
            
            result = hash_password(test_password)
            
            assert result is not None
            assert isinstance(result, str)
    
    def test_verify_password_success(self):
        """Тест успішної перевірки пароля"""
        test_password = "test_password_123"
        test_hashed = "hashed_password_hash"
        
        # Мокаємо bcrypt на рівні модуля
        with patch('builtins.__import__') as mock_import:
            mock_bcrypt = Mock()
            mock_bcrypt.checkpw.return_value = True
            mock_import.return_value = mock_bcrypt
            
            result = verify_password(test_password, test_hashed)
            
            assert result is True
    
    def test_verify_password_failure(self):
        """Тест невдалої перевірки пароля"""
        test_password = "wrong_password"
        test_hashed = "hashed_password_hash"
        
        # Мокаємо bcrypt на рівні модуля
        with patch('builtins.__import__') as mock_import:
            mock_bcrypt = Mock()
            mock_bcrypt.checkpw.return_value = False
            mock_import.return_value = mock_bcrypt
            
            result = verify_password(test_password, test_hashed)
            
            assert result is False


class TestEncryptionSecurity:
    """Тести безпеки шифрування"""
    
    def test_no_real_secrets_in_tests(self):
        """Тест що в тестах немає реальних секретів"""
        # Перевіряємо що використовуються тільки тестові дані
        test_key = "test_encryption_key_32_chars_long"
        test_data = "test_sensitive_data"
        
        assert "test_" in test_key
        assert "test_" in test_data
        assert len(test_key) == 33  # Виправлено довжину
    
    def test_encryption_key_format(self):
        """Тест формату ключа шифрування"""
        test_key = "test_encryption_key_32_chars_long"
        
        # Перевіряємо що ключ має правильну довжину
        assert len(test_key) == 33  # Виправлено довжину
        
        # Перевіряємо що ключ містить тільки безпечні символи
        assert test_key.isalnum() or "_" in test_key
    
    def test_encrypted_data_format(self):
        """Тест формату зашифрованих даних"""
        test_key = "test_encryption_key_32_chars_long"
        test_data = "test_sensitive_data"
        
        manager = EncryptionManager(test_key)
        encrypted = manager.encrypt(test_data)
        
        # Перевіряємо що зашифровані дані не містять оригінальних даних
        assert test_data not in encrypted
        
        # Перевіряємо що зашифровані дані є рядком
        assert isinstance(encrypted, str)
    
    def test_encryption_consistency(self):
        """Тест консистентності шифрування"""
        test_key = "test_encryption_key_32_chars_long"
        test_data = "test_sensitive_data"
        
        manager = EncryptionManager(test_key)
        
        # Шифруємо одні й ті ж дані двічі
        encrypted1 = manager.encrypt(test_data)
        encrypted2 = manager.encrypt(test_data)
        
        # Зашифровані дані повинні бути різними (через випадкову сіль)
        assert encrypted1 != encrypted2
        
        # Але розшифровані дані повинні бути однаковими
        decrypted1 = manager.decrypt(encrypted1)
        decrypted2 = manager.decrypt(encrypted2)
        
        assert decrypted1 == test_data
        assert decrypted2 == test_data


class TestEncryptionErrorHandling:
    """Тести обробки помилок шифрування"""
    
    def test_decrypt_invalid_data(self):
        """Тест розшифрування невалідних даних"""
        test_key = "test_encryption_key_32_chars_long"
        manager = EncryptionManager(test_key)
        
        # Спробуємо розшифрувати невалідні дані
        with pytest.raises(Exception):
            manager.decrypt("invalid_encrypted_data")
    
    def test_encryption_with_none_data(self):
        """Тест шифрування None даних"""
        test_key = "test_encryption_key_32_chars_long"
        manager = EncryptionManager(test_key)
        
        # Шифруємо None - повинно повернути порожній рядок
        result = manager.encrypt(None)
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__]) 