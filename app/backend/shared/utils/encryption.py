"""
Спільні утиліти шифрування для всіх мікросервісів
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ..config.settings import settings


class EncryptionManager:
    """Менеджер шифрування для чутливих даних"""
    
    def __init__(self, key: str = None):
        """
        Ініціалізація менеджера шифрування
        
        Args:
            key: Ключ шифрування (якщо не передано, використовується з налаштувань)
        """
        self.key = key or settings.ENCRYPTION_KEY
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


# Глобальний екземпляр менеджера шифрування
encryption_manager = EncryptionManager()


def encrypt_data(data: str) -> str:
    """Швидка функція шифрування"""
    return encryption_manager.encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Швидка функція розшифрування"""
    return encryption_manager.decrypt(encrypted_data)


def generate_encryption_key() -> str:
    """Генерація нового ключа шифрування"""
    return Fernet.generate_key().decode()


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