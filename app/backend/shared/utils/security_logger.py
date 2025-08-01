"""
Система логування безпеки
SECURITY-008: Логування безпеки та моніторинг
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from config.logging import get_logger
from database.connection import get_db
from .encryption import encrypt_sensitive_data


class SecurityEventType(Enum):
    """Типи подій безпеки"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_FAILED = "mfa_failed"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    SESSION_REVOKED = "session_revoked"
    API_ACCESS = "api_access"
    API_RATE_LIMIT = "api_rate_limit"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_ALERT = "security_alert"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    ENCRYPTION_EVENT = "encryption_event"
    DECRYPTION_EVENT = "decryption_event"


class SecurityLevel(Enum):
    """Рівні безпеки"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SecurityLogger:
    """Менеджер логування безпеки"""
    
    def __init__(self, db_session=None):
        self.db = db_session or next(get_db())
        self.logger = get_logger("security")
        self.alert_system = SecurityAlertSystem()
        self.anomaly_detector = AnomalyDetector()
    
    def log_event(self, 
                  event_type: SecurityEventType,
                  user_id: Optional[int] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  level: SecurityLevel = SecurityLevel.INFO,
                  success: bool = True) -> None:
        """
        Логує подію безпеки
        
        Args:
            event_type: Тип події
            user_id: ID користувача
            ip_address: IP адреса
            user_agent: User Agent
            details: Додаткові деталі
            level: Рівень безпеки
            success: Успішність операції
        """
        try:
            # Створюємо запис логу
            security_log = SecurityLog(
                user_id=user_id,
                event_type=event_type.value,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                success=success,
                level=level.value,
                created_at=datetime.utcnow()
            )
            
            # Зберігаємо в БД
            self.db.add(security_log)
            self.db.commit()
            
            # Логуємо в систему логування
            self._log_to_system(event_type, user_id, ip_address, details, level, success)
            
            # Перевіряємо аномалії
            asyncio.create_task(self._check_anomalies(security_log))
            
            # Перевіряємо алерти
            asyncio.create_task(self._check_alerts(security_log))
            
        except Exception as e:
            self.logger.error(f"Помилка логування події безпеки: {e}")
    
    def _log_to_system(self, event_type: SecurityEventType, user_id: Optional[int],
                       ip_address: Optional[str], details: Optional[Dict[str, Any]],
                       level: SecurityLevel, success: bool) -> None:
        """Логує подію в систему логування"""
        log_message = {
            "event_type": event_type.value,
            "user_id": user_id,
            "ip_address": ip_address,
            "level": level.value,
            "success": success,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if level == SecurityLevel.CRITICAL:
            self.logger.critical(json.dumps(log_message))
        elif level == SecurityLevel.ERROR:
            self.logger.error(json.dumps(log_message))
        elif level == SecurityLevel.WARNING:
            self.logger.warning(json.dumps(log_message))
        else:
            self.logger.info(json.dumps(log_message))
    
    async def _check_anomalies(self, security_log) -> None:
        """Перевіряє аномалії"""
        try:
            anomaly_score = await self.anomaly_detector.detect_anomaly(security_log)
            if anomaly_score > 0.7:  # Високий рівень аномалії
                self.log_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_id=security_log.user_id,
                    ip_address=security_log.ip_address,
                    details={"anomaly_score": anomaly_score, "original_event": security_log.event_type},
                    level=SecurityLevel.WARNING
                )
        except Exception as e:
            self.logger.error(f"Помилка перевірки аномалій: {e}")
    
    async def _check_alerts(self, security_log) -> None:
        """Перевіряє алерти"""
        try:
            await self.alert_system.check_alerts(security_log)
        except Exception as e:
            self.logger.error(f"Помилка перевірки алертів: {e}")
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str, 
                         user_agent: str, user_id: Optional[int] = None) -> None:
        """Логує спробу входу"""
        event_type = SecurityEventType.LOGIN_SUCCESS if success else SecurityEventType.LOGIN_FAILED
        level = SecurityLevel.ERROR if not success else SecurityLevel.INFO
        
        details = {
            "email": email,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            level=level,
            success=success
        )
    
    def log_mfa_event(self, user_id: int, success: bool, event_type: str,
                     ip_address: Optional[str] = None) -> None:
        """Логує події MFA"""
        if event_type == "enabled":
            event = SecurityEventType.MFA_ENABLED
        elif event_type == "disabled":
            event = SecurityEventType.MFA_DISABLED
        elif event_type == "failed":
            event = SecurityEventType.MFA_FAILED
        else:
            event = SecurityEventType.MFA_FAILED
        
        level = SecurityLevel.ERROR if not success else SecurityLevel.INFO
        
        self.log_event(
            event_type=event,
            user_id=user_id,
            ip_address=ip_address,
            details={"event_type": event_type, "success": success},
            level=level,
            success=success
        )
    
    def log_api_access(self, user_id: int, endpoint: str, method: str,
                      ip_address: str, response_time: float) -> None:
        """Логує доступ до API"""
        details = {
            "endpoint": endpoint,
            "method": method,
            "response_time": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.log_event(
            event_type=SecurityEventType.API_ACCESS,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            level=SecurityLevel.INFO,
            success=True
        )
    
    def log_rate_limit(self, ip_address: str, endpoint: str, limit: int) -> None:
        """Логує перевищення rate limit"""
        details = {
            "endpoint": endpoint,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.log_event(
            event_type=SecurityEventType.API_RATE_LIMIT,
            ip_address=ip_address,
            details=details,
            level=SecurityLevel.WARNING,
            success=False
        )
    
    def log_encryption_event(self, user_id: Optional[int], operation: str,
                           data_type: str, success: bool) -> None:
        """Логує події шифрування"""
        event_type = SecurityEventType.ENCRYPTION_EVENT if operation == "encrypt" else SecurityEventType.DECRYPTION_EVENT
        
        details = {
            "operation": operation,
            "data_type": data_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            details=details,
            level=SecurityLevel.INFO,
            success=success
        )


class SecurityAlertSystem:
    """Система сповіщень безпеки"""
    
    def __init__(self):
        self.logger = get_logger("security-alerts")
        self.alert_rules = self._load_alert_rules()
    
    def _load_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Завантажує правила алертів"""
        return {
            "multiple_failed_logins": {
                "threshold": 5,
                "window": 300,  # 5 хвилин
                "level": "warning"
            },
            "suspicious_ip": {
                "threshold": 10,
                "window": 3600,  # 1 година
                "level": "critical"
            },
            "api_rate_limit_exceeded": {
                "threshold": 3,
                "window": 60,  # 1 хвилина
                "level": "warning"
            },
            "mfa_failures": {
                "threshold": 3,
                "window": 300,  # 5 хвилин
                "level": "critical"
            }
        }
    
    async def check_alerts(self, security_log) -> None:
        """Перевіряє алерти на основі події"""
        try:
            # Перевіряємо різні типи алертів
            await self._check_failed_logins(security_log)
            await self._check_suspicious_ips(security_log)
            await self._check_api_rate_limits(security_log)
            await self._check_mfa_failures(security_log)
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки алертів: {e}")
    
    async def _check_failed_logins(self, security_log) -> None:
        """Перевіряє алерти на невдалі спроби входу"""
        if security_log.event_type == SecurityEventType.LOGIN_FAILED.value:
            # Логіка перевірки кількості невдалих спроб
            pass
    
    async def _check_suspicious_ips(self, security_log) -> None:
        """Перевіряє підозрілі IP адреси"""
        if security_log.ip_address:
            # Логіка перевірки IP адреси
            pass
    
    async def _check_api_rate_limits(self, security_log) -> None:
        """Перевіряє перевищення rate limits"""
        if security_log.event_type == SecurityEventType.API_RATE_LIMIT.value:
            # Логіка перевірки rate limits
            pass
    
    async def _check_mfa_failures(self, security_log) -> None:
        """Перевіряє невдалі спроби MFA"""
        if security_log.event_type == SecurityEventType.MFA_FAILED.value:
            # Логіка перевірки MFA невдач
            pass


class AnomalyDetector:
    """Детектор аномалій"""
    
    def __init__(self):
        self.logger = get_logger("anomaly-detector")
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Завантажує паттерни аномалій"""
        return {
            "unusual_login_time": {
                "weight": 0.3,
                "description": "Незвичайний час входу"
            },
            "unusual_location": {
                "weight": 0.5,
                "description": "Незвичайна локація"
            },
            "rapid_requests": {
                "weight": 0.4,
                "description": "Швидкі запити"
            },
            "failed_attempts": {
                "weight": 0.6,
                "description": "Невдалі спроби"
            }
        }
    
    async def detect_anomaly(self, security_log) -> float:
        """
        Виявляє аномалії в події безпеки
        
        Args:
            security_log: Запис логу безпеки
            
        Returns:
            float: Оцінка аномалії (0.0 - 1.0)
        """
        try:
            anomaly_score = 0.0
            
            # Перевіряємо різні типи аномалій
            anomaly_score += await self._check_unusual_login_time(security_log)
            anomaly_score += await self._check_unusual_location(security_log)
            anomaly_score += await self._check_rapid_requests(security_log)
            anomaly_score += await self._check_failed_attempts(security_log)
            
            # Нормалізуємо результат
            anomaly_score = min(anomaly_score, 1.0)
            
            return anomaly_score
            
        except Exception as e:
            self.logger.error(f"Помилка виявлення аномалії: {e}")
            return 0.0
    
    async def _check_unusual_login_time(self, security_log) -> float:
        """Перевіряє незвичайний час входу"""
        # Логіка перевірки часу
        return 0.0
    
    async def _check_unusual_location(self, security_log) -> float:
        """Перевіряє незвичайну локацію"""
        # Логіка перевірки локації
        return 0.0
    
    async def _check_rapid_requests(self, security_log) -> float:
        """Перевіряє швидкі запити"""
        # Логіка перевірки швидкості запитів
        return 0.0
    
    async def _check_failed_attempts(self, security_log) -> float:
        """Перевіряє невдалі спроби"""
        # Логіка перевірки невдалих спроб
        return 0.0


# Глобальний екземпляр логера безпеки
security_logger = SecurityLogger()


def log_security_event(event_type: SecurityEventType, **kwargs) -> None:
    """Швидка функція логування події безпеки"""
    security_logger.log_event(event_type, **kwargs)


def log_login_attempt(email: str, success: bool, ip_address: str, 
                     user_agent: str, user_id: Optional[int] = None) -> None:
    """Швидка функція логування спроби входу"""
    security_logger.log_login_attempt(email, success, ip_address, user_agent, user_id)


def log_api_access(user_id: int, endpoint: str, method: str,
                  ip_address: str, response_time: float) -> None:
    """Швидка функція логування доступу до API"""
    security_logger.log_api_access(user_id, endpoint, method, ip_address, response_time)


def log_rate_limit(ip_address: str, endpoint: str, limit: int) -> None:
    """Швидка функція логування rate limit"""
    security_logger.log_rate_limit(ip_address, endpoint, limit) 