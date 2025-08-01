"""
Безпечне логування з шифруванням чутливих даних
"""

import base64
import hashlib
import hmac
import json
import re
from typing import Dict, List, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

from shared.config.logging import get_logger


class SensitiveDataMasker:
    """Маскування чутливих даних"""
    
    def __init__(self):
        self.sensitive_patterns = {
            # Email адреси
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            
            # IP адреси
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            
            # Кредитні карти
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            
            # Телефонні номери
            'phone': r'\b\+?[\d\s\-\(\)]{10,}\b',
            
            # Паролі (в різних форматах)
            'password': r'["\']?password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            'passwd': r'["\']?passwd["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            'pwd': r'["\']?pwd["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            
            # Токени
            'token': r'["\']?token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            'jwt': r'["\']?jwt["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            'api_key': r'["\']?api_key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            'secret': r'["\']?secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            
            # UUID
            'uuid': r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
            
            # Соціальні номери
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            
            # Номери банківських рахунків
            'bank_account': r'\b\d{10,17}\b',
        }
        
        self.mask_char = '*'
        self.min_mask_length = 4
    
    def mask_sensitive_data(self, text: str) -> str:
        """Маскування чутливих даних в тексті"""
        masked_text = text
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, masked_text, re.IGNORECASE)
            
            for match in matches:
                original = match.group(0)
                masked = self._create_mask(original, pattern_name)
                masked_text = masked_text.replace(original, masked)
        
        return masked_text
    
    def _create_mask(self, original: str, pattern_type: str) -> str:
        """Створення маски для чутливих даних"""
        if len(original) <= self.min_mask_length:
            return self.mask_char * len(original)
        
        # Різні стратегії маскування для різних типів
        if pattern_type == 'email':
            # Зберігаємо перший символ та домен
            parts = original.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                masked_username = username[0] + self.mask_char * (len(username) - 1)
                return f"{masked_username}@{domain}"
        
        elif pattern_type == 'credit_card':
            # Зберігаємо перші 4 та останні 4 цифри
            digits = re.sub(r'[^\d]', '', original)
            if len(digits) >= 8:
                return f"{digits[:4]}{self.mask_char * (len(digits) - 8)}{digits[-4:]}"
        
        elif pattern_type == 'phone':
            # Зберігаємо країну та останні цифри
            digits = re.sub(r'[^\d]', '', original)
            if len(digits) >= 6:
                return f"{digits[:2]}{self.mask_char * (len(digits) - 6)}{digits[-4:]}"
        
        # Загальна стратегія: зберігаємо перший та останній символи
        return original[0] + self.mask_char * (len(original) - 2) + original[-1]
    
    def is_sensitive_field(self, field_name: str) -> bool:
        """Перевірка чи поле є чутливим"""
        sensitive_keywords = [
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
            'credential', 'private', 'sensitive', 'confidential'
        ]
        
        field_lower = field_name.lower()
        return any(keyword in field_lower for keyword in sensitive_keywords)


class SecureLogger:
    """Безпечний логер з шифруванням чутливих даних"""
    
    def __init__(self, logger, encryption_key: str = None):
        self.logger = logger
        self.masker = SensitiveDataMasker()
        self.encryption_key = encryption_key or os.getenv('LOG_ENCRYPTION_KEY')
        self.fernet = None
        
        if self.encryption_key:
            self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Ініціалізація шифрування"""
        try:
            # Генерація ключа з пароля
            salt = b'log_salt_123'  # В продакшені використовуйте унікальну сіль
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            self.fernet = Fernet(key)
            
        except Exception as e:
            self.logger.error("Помилка ініціалізації шифрування", extra={"error": str(e)})
            self.fernet = None
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Шифрування чутливих даних"""
        if not self.fernet:
            return data
        
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error("Помилка шифрування", extra={"error": str(e)})
            return data
    
    def _process_data(self, data: Any, encrypt: bool = False) -> Any:
        """Обробка даних (маскування та шифрування)"""
        if isinstance(data, str):
            # Маскування чутливих даних
            masked_data = self.masker.mask_sensitive_data(data)
            
            # Шифрування якщо потрібно
            if encrypt and self.fernet:
                return self._encrypt_sensitive_data(masked_data)
            
            return masked_data
        
        elif isinstance(data, dict):
            processed_dict = {}
            for key, value in data.items():
                # Перевіряємо чи поле є чутливим
                if self.masker.is_sensitive_field(key):
                    if isinstance(value, str):
                        processed_dict[key] = self._process_data(value, encrypt=True)
                    else:
                        processed_dict[key] = "[ENCRYPTED]"
                else:
                    processed_dict[key] = self._process_data(value, encrypt)
            return processed_dict
        
        elif isinstance(data, list):
            return [self._process_data(item, encrypt) for item in data]
        
        else:
            return data
    
    def info(self, message: str, extra: Dict[str, Any] = None, encrypt_sensitive: bool = True):
        """Безпечне логування інформації"""
        processed_extra = self._process_data(extra, encrypt_sensitive) if extra else None
        self.logger.info(message, extra=processed_extra)
    
    def warning(self, message: str, extra: Dict[str, Any] = None, encrypt_sensitive: bool = True):
        """Безпечне логування попереджень"""
        processed_extra = self._process_data(extra, encrypt_sensitive) if extra else None
        self.logger.warning(message, extra=processed_extra)
    
    def error(self, message: str, extra: Dict[str, Any] = None, encrypt_sensitive: bool = True):
        """Безпечне логування помилок"""
        processed_extra = self._process_data(extra, encrypt_sensitive) if extra else None
        self.logger.error(message, extra=processed_extra)
    
    def debug(self, message: str, extra: Dict[str, Any] = None, encrypt_sensitive: bool = True):
        """Безпечне логування для дебагу"""
        processed_extra = self._process_data(extra, encrypt_sensitive) if extra else None
        self.logger.debug(message, extra=processed_extra)
    
    def security(self, event: str, extra: Dict[str, Any] = None, encrypt_sensitive: bool = True):
        """Безпечне логування подій безпеки"""
        processed_extra = self._process_data(extra, encrypt_sensitive) if extra else None
        self.logger.security(event, extra=processed_extra)


class LogAuditTrail:
    """Аудит доступу до логів"""
    
    def __init__(self, logger):
        self.logger = logger
        self.access_log = []
    
    def log_access(self, user_id: str, action: str, log_file: str, 
                   timestamp: str = None, ip_address: str = None, 
                   user_agent: str = None, success: bool = True):
        """Логування доступу до логів"""
        audit_entry = {
            "user_id": user_id,
            "action": action,
            "log_file": log_file,
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "access_hash": self._generate_access_hash(user_id, action, log_file)
        }
        
        self.access_log.append(audit_entry)
        self.logger.info("Log access", extra=audit_entry)
    
    def _generate_access_hash(self, user_id: str, action: str, log_file: str) -> str:
        """Генерація хешу доступу"""
        data = f"{user_id}:{action}:{log_file}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_access_history(self, user_id: str = None, hours: int = 24) -> List[Dict]:
        """Отримання історії доступу"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        filtered_log = []
        for entry in self.access_log:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time > cutoff_time:
                if user_id is None or entry["user_id"] == user_id:
                    filtered_log.append(entry)
        
        return filtered_log
    
    def detect_suspicious_access(self) -> List[Dict]:
        """Виявлення підозрілого доступу"""
        suspicious_entries = []
        
        # Групуємо доступ по користувачах
        user_access = defaultdict(list)
        for entry in self.access_log:
            user_access[entry["user_id"]].append(entry)
        
        # Перевіряємо кожного користувача
        for user_id, entries in user_access.items():
            # Багато невдалих спроб
            failed_attempts = [e for e in entries if not e["success"]]
            if len(failed_attempts) > 5:
                suspicious_entries.extend(failed_attempts)
            
            # Доступ до багатьох файлів за короткий час
            recent_entries = [e for e in entries 
                            if datetime.fromisoformat(e["timestamp"]) > 
                            datetime.utcnow() - timedelta(minutes=10)]
            
            unique_files = set(e["log_file"] for e in recent_entries)
            if len(unique_files) > 10:
                suspicious_entries.extend(recent_entries)
        
        return suspicious_entries


class SecureLogAnalyzer:
    """Безпечний аналізатор логів"""
    
    def __init__(self, log_directory: str, encryption_key: str = None):
        self.log_directory = log_directory
        self.encryption_key = encryption_key
        self.logger = get_logger("secure-log-analyzer")
        self.fernet = None
        
        if self.encryption_key:
            self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Ініціалізація шифрування для аналізу"""
        try:
            salt = b'log_salt_123'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            self.fernet = Fernet(key)
        except Exception as e:
            self.logger.error("Помилка ініціалізації шифрування для аналізу", extra={"error": str(e)})
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Розшифрування даних"""
        if not self.fernet:
            return encrypted_data
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            self.logger.error("Помилка розшифрування", extra={"error": str(e)})
            return encrypted_data
    
    def analyze_secure_logs(self, hours: int = 24) -> Dict[str, Any]:
        """Аналіз зашифрованих логів"""
        try:
            # Аналіз без розшифрування чутливих даних
            analysis = {
                "period_hours": hours,
                "total_log_entries": 0,
                "encrypted_entries": 0,
                "sensitive_fields_detected": 0,
                "security_events": 0,
                "error_patterns": {},
                "performance_metrics": {},
                "access_patterns": {}
            }
            
            # Аналіз файлів логів
            for log_file in Path(self.log_directory).glob("*.log"):
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        analysis["total_log_entries"] += 1
                        
                        # Перевірка на зашифровані дані
                        if "[ENCRYPTED]" in line:
                            analysis["encrypted_entries"] += 1
                        
                        # Перевірка на чутливі поля
                        if any(pattern in line.lower() for pattern in ['password', 'token', 'secret']):
                            analysis["sensitive_fields_detected"] += 1
                        
                        # Підрахунок подій безпеки
                        if "Security:" in line:
                            analysis["security_events"] += 1
            
            return analysis
            
        except Exception as e:
            self.logger.error("Помилка аналізу захищених логів", extra={"error": str(e)})
            return {}


# Глобальні екземпляри
secure_logger = None
log_audit_trail = None
secure_analyzer = None


def initialize_secure_logging(service_name: str, encryption_key: str = None):
    """Ініціалізація безпечного логування"""
    global secure_logger, log_audit_trail, secure_analyzer
    
    logger = get_logger(f"secure-{service_name}")
    
    # Ініціалізація безпечного логера
    secure_logger = SecureLogger(logger, encryption_key)
    
    # Ініціалізація аудиту
    log_audit_trail = LogAuditTrail(logger)
    
    # Ініціалізація безпечного аналізатора
    secure_analyzer = SecureLogAnalyzer("logs", encryption_key)
    
    logger.info("Безпечне логування ініціалізовано", extra={
        "service_name": service_name,
        "encryption_enabled": encryption_key is not None,
        "components": ["secure_logger", "log_audit_trail", "secure_analyzer"]
    })


def get_secure_logger():
    """Отримання безпечного логера"""
    return secure_logger


def get_log_audit_trail():
    """Отримання аудиту логів"""
    return log_audit_trail


def get_secure_analyzer():
    """Отримання безпечного аналізатора"""
    return secure_analyzer 