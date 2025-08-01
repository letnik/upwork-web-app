"""
Спільні утиліти шифрування для всіх мікросервісів
Покращена версія для SECURITY-007
"""

import base64
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from ..config.settings import settings


class TokenEncryptionManager:
    """Менеджер шифрування токенів з додатковою безпекою"""
    
    def __init__(self, key: str = None):
        """
        Ініціалізація менеджера шифрування токенів
        
        Args:
            key: Ключ шифрування (якщо не передано, використовується з налаштувань)
        """
        self.key = key or settings.ENCRYPTION_KEY
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Налаштування шифрування"""
        try:
            # Генеруємо ключ з пароля або використовуємо готовий
            if len(self.key) < 32:
                # Генеруємо ключ з пароля
                salt = b'upwork_token_salt_2024'
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                    backend=default_backend()
                )
                key_bytes = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
            else:
                # Використовуємо готовий ключ
                key_bytes = base64.urlsafe_b64encode(self.key.encode()[:32])
            
            self.fernet = Fernet(key_bytes)
        except Exception as e:
            raise Exception(f"Помилка налаштування шифрування токенів: {e}")
    
    def encrypt_token(self, token: str, metadata: Dict[str, Any] = None) -> str:
        """
        Шифрування токена з метаданими
        
        Args:
            token: Токен для шифрування
            metadata: Додаткові метадані (timestamp, user_id, etc.)
            
        Returns:
            Зашифрований токен з метаданими
        """
        try:
            if not token:
                return ""
            
            # Створюємо структуру даних
            data = {
                "token": token,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Конвертуємо в JSON та шифруємо
            import json
            json_data = json.dumps(data)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise Exception(f"Помилка шифрування токена: {e}")
    
    def decrypt_token(self, encrypted_token: str) -> Dict[str, Any]:
        """
        Розшифрування токена з метаданими
        
        Args:
            encrypted_token: Зашифрований токен
            
        Returns:
            Словник з токеном та метаданими
        """
        try:
            if not encrypted_token:
                return {"token": "", "metadata": {}}
            
            # Декодуємо з base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # Конвертуємо з JSON
            import json
            data = json.loads(decrypted_data.decode())
            
            return data
        except Exception as e:
            raise Exception(f"Помилка розшифрування токена: {e}")
    
    def verify_token_integrity(self, encrypted_token: str) -> bool:
        """
        Перевірка цілісності токена
        
        Args:
            encrypted_token: Зашифрований токен
            
        Returns:
            True якщо токен цілісний
        """
        try:
            data = self.decrypt_token(encrypted_token)
            
            # Перевіряємо наявність обов'язкових полів
            if "token" not in data or "timestamp" not in data:
                return False
            
            # Перевіряємо timestamp (токен не старіше 30 днів)
            timestamp = datetime.fromisoformat(data["timestamp"])
            if datetime.utcnow() - timestamp > timedelta(days=30):
                return False
            
            return True
        except Exception:
            return False


class SensitiveDataEncryptionManager:
    """Менеджер шифрування чутливих даних"""
    
    def __init__(self, key: str = None):
        """
        Ініціалізація менеджера шифрування чутливих даних
        
        Args:
            key: Ключ шифрування
        """
        self.key = key or settings.ENCRYPTION_KEY
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Налаштування шифрування"""
        try:
            # Генеруємо ключ з пароля
            salt = b'upwork_sensitive_salt_2024'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key_bytes = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
            self.fernet = Fernet(key_bytes)
        except Exception as e:
            raise Exception(f"Помилка налаштування шифрування чутливих даних: {e}")
    
    def encrypt_sensitive_data(self, data: str, data_type: str = "general") -> str:
        """
        Шифрування чутливих даних
        
        Args:
            data: Дані для шифрування
            data_type: Тип даних (api_key, password, personal_info, etc.)
            
        Returns:
            Зашифровані дані
        """
        try:
            if not data:
                return ""
            
            # Додаємо тип даних для додаткової безпеки
            enhanced_data = f"{data_type}:{data}"
            encrypted_data = self.fernet.encrypt(enhanced_data.encode())
            
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise Exception(f"Помилка шифрування чутливих даних: {e}")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Розшифрування чутливих даних
        
        Args:
            encrypted_data: Зашифровані дані
            
        Returns:
            Розшифровані дані
        """
        try:
            if not encrypted_data:
                return ""
            
            # Декодуємо з base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # Видаляємо тип даних
            data_with_type = decrypted_data.decode()
            if ":" in data_with_type:
                return data_with_type.split(":", 1)[1]
            return data_with_type
        except Exception as e:
            raise Exception(f"Помилка розшифрування чутливих даних: {e}")


class EncryptionManager:
    """Менеджер шифрування для чутливих даних (покращена версія)"""
    
    def __init__(self, key: str = None):
        """
        Ініціалізація менеджера шифрування
        
        Args:
            key: Ключ шифрування (якщо не передано, використовується з налаштувань)
        """
        self.key = key or settings.ENCRYPTION_KEY
        self.token_manager = TokenEncryptionManager(self.key)
        self.sensitive_manager = SensitiveDataEncryptionManager(self.key)
        self._setup_fernet()
    
    def _setup_fernet(self):
        """Налаштування Fernet шифрування"""
        try:
            # Конвертуємо ключ в bytes
            if isinstance(self.key, str):
                # Якщо ключ вже в base64 форматі
                if len(self.key) == 44:
                    key_bytes = base64.urlsafe_b64decode(self.key)
                else:
                    # Генеруємо ключ з пароля
                    salt = b'upwork_salt_2024'  # Фіксована сіль для консистентності
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key_bytes = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
            else:
                key_bytes = self.key
            
            self.fernet = Fernet(key_bytes)
        except Exception as e:
            raise Exception(f"Помилка налаштування шифрування: {e}")
    
    def encrypt(self, data: str) -> str:
        """
        Шифрування даних
        
        Args:
            data: Дані для шифрування
            
        Returns:
            Зашифровані дані в base64 форматі
        """
        try:
            if not data:
                return ""
            
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise Exception(f"Помилка шифрування: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Розшифрування даних
        
        Args:
            encrypted_data: Зашифровані дані в base64 форматі
            
        Returns:
            Розшифровані дані
        """
        try:
            if not encrypted_data:
                return ""
            
            # Декодуємо з base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            raise Exception(f"Помилка розшифрування: {e}")
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Шифрування словника даних
        
        Args:
            data: Словник для шифрування
            
        Returns:
            Словник з зашифрованими значеннями
        """
        encrypted_dict = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                encrypted_dict[key] = self.encrypt(value)
            else:
                encrypted_dict[key] = value
        return encrypted_dict
    
    def decrypt_dict(self, encrypted_data: dict) -> dict:
        """
        Розшифрування словника даних
        
        Args:
            encrypted_data: Словник з зашифрованими даними
            
        Returns:
            Словник з розшифрованими значеннями
        """
        decrypted_dict = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str) and value:
                try:
                    decrypted_dict[key] = self.decrypt(value)
                except Exception:
                    # Якщо не вдалося розшифрувати, повертаємо як є
                    decrypted_dict[key] = value
            else:
                decrypted_dict[key] = value
        return decrypted_dict
    
    def encrypt_token(self, token: str, metadata: Dict[str, Any] = None) -> str:
        """Шифрування токена з метаданими"""
        return self.token_manager.encrypt_token(token, metadata)
    
    def decrypt_token(self, encrypted_token: str) -> Dict[str, Any]:
        """Розшифрування токена з метаданими"""
        return self.token_manager.decrypt_token(encrypted_token)
    
    def verify_token_integrity(self, encrypted_token: str) -> bool:
        """Перевірка цілісності токена"""
        return self.token_manager.verify_token_integrity(encrypted_token)
    
    def encrypt_sensitive_data(self, data: str, data_type: str = "general") -> str:
        """Шифрування чутливих даних"""
        return self.sensitive_manager.encrypt_sensitive_data(data, data_type)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Розшифрування чутливих даних"""
        return self.sensitive_manager.decrypt_sensitive_data(encrypted_data)


# Глобальний екземпляр менеджера шифрування
encryption_manager = EncryptionManager()


def encrypt_data(data: str) -> str:
    """Швидка функція шифрування"""
    return encryption_manager.encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Швидка функція розшифрування"""
    return encryption_manager.decrypt(encrypted_data)


def encrypt_token(token: str, metadata: Dict[str, Any] = None) -> str:
    """Швидка функція шифрування токена"""
    return encryption_manager.encrypt_token(token, metadata)


def decrypt_token(encrypted_token: str) -> Dict[str, Any]:
    """Швидка функція розшифрування токена"""
    return encryption_manager.decrypt_token(encrypted_token)


def encrypt_sensitive_data(data: str, data_type: str = "general") -> str:
    """Швидка функція шифрування чутливих даних"""
    return encryption_manager.encrypt_sensitive_data(data, data_type)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Швидка функція розшифрування чутливих даних"""
    return encryption_manager.decrypt_sensitive_data(encrypted_data)


def generate_encryption_key() -> str:
    """Генерація нового ключа шифрування"""
    return Fernet.generate_key().decode()


def generate_secure_token(length: int = 32) -> str:
    """Генерація безпечного токена"""
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    """
    Хешування пароля з bcrypt
    
    Args:
        password: Пароль для хешування
        
    Returns:
        Хеш пароля
    """
    import bcrypt
    
    # Генеруємо сіль та хешуємо пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Перевірка пароля
    
    Args:
        password: Пароль для перевірки
        hashed_password: Хеш пароля
        
    Returns:
        True якщо пароль правильний
    """
    import bcrypt
    
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def hash_token(token: str) -> str:
    """
    Хешування токена для зберігання в БД
    
    Args:
        token: Токен для хешування
        
    Returns:
        Хеш токена
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """
    Перевірка хешу токена
    
    Args:
        token: Токен для перевірки
        token_hash: Хеш токена
        
    Returns:
        True якщо хеш співпадає
    """
    return hash_token(token) == token_hash 