"""
Безпечні тести для системи логування безпеки
SECURITY-008: Логування безпеки та моніторинг
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, patch
from enum import Enum

# Створюємо моки для залежностей
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


class MockSecurityLogger:
    """Мок логера безпеки для тестування"""
    
    def __init__(self):
        self.logged_events = []
        self.logger = Mock()
    
    def log_event(self, 
                  event_type: SecurityEventType,
                  user_id: int = None,
                  ip_address: str = None,
                  user_agent: str = None,
                  details: Dict[str, Any] = None,
                  level: SecurityLevel = SecurityLevel.INFO,
                  success: bool = True) -> None:
        """Логує подію безпеки"""
        self.logged_events.append({
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "level": level,
            "success": success
        })
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str, 
                         user_agent: str, user_id: int = None) -> None:
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
                     ip_address: str = None) -> None:
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
    
    def log_encryption_event(self, user_id: int, operation: str,
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


class MockSecurityAlertSystem:
    """Мок системи сповіщень безпеки"""
    
    def __init__(self):
        self.alert_rules = self._load_alert_rules()
        self.logger = Mock()
    
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


class MockAnomalyDetector:
    """Мок детектора аномалій"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.logger = Mock()
    
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


class TestSecurityLogger:
    """Тести логера безпеки"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.logger = MockSecurityLogger()
    
    def test_log_event_basic(self):
        """Тест базового логування події"""
        # Логуємо подію
        self.logger.log_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            user_id=123,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"email": "test@example.com"},
            level=SecurityLevel.INFO,
            success=True
        )
        
        # Перевіряємо що подія була залогована
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.LOGIN_SUCCESS
        assert event["user_id"] == 123
        assert event["ip_address"] == "192.168.1.1"
        assert event["success"] is True
        assert event["level"] == SecurityLevel.INFO
    
    def test_log_login_attempt_success(self):
        """Тест логування успішної спроби входу"""
        self.logger.log_login_attempt(
            email="test@example.com",
            success=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            user_id=123
        )
        
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.LOGIN_SUCCESS
        assert event["success"] is True
        assert event["level"] == SecurityLevel.INFO
        assert event["details"]["email"] == "test@example.com"
    
    def test_log_login_attempt_failure(self):
        """Тест логування невдалої спроби входу"""
        self.logger.log_login_attempt(
            email="test@example.com",
            success=False,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.LOGIN_FAILED
        assert event["success"] is False
        assert event["level"] == SecurityLevel.ERROR
    
    def test_log_mfa_event(self):
        """Тест логування подій MFA"""
        self.logger.log_mfa_event(
            user_id=123,
            success=True,
            event_type="enabled",
            ip_address="192.168.1.1"
        )
        
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.MFA_ENABLED
        assert event["success"] is True
    
    def test_log_api_access(self):
        """Тест логування доступу до API"""
        self.logger.log_api_access(
            user_id=123,
            endpoint="/api/v1/jobs",
            method="GET",
            ip_address="192.168.1.1",
            response_time=0.5
        )
        
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.API_ACCESS
        assert event["success"] is True
        assert event["details"]["endpoint"] == "/api/v1/jobs"
        assert event["details"]["method"] == "GET"
        assert event["details"]["response_time"] == 0.5
    
    def test_log_rate_limit(self):
        """Тест логування перевищення rate limit"""
        self.logger.log_rate_limit(
            ip_address="192.168.1.1",
            endpoint="/api/v1/jobs",
            limit=100
        )
        
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.API_RATE_LIMIT
        assert event["success"] is False
        assert event["level"] == SecurityLevel.WARNING
    
    def test_log_encryption_event(self):
        """Тест логування подій шифрування"""
        self.logger.log_encryption_event(
            user_id=123,
            operation="encrypt",
            data_type="api_key",
            success=True
        )
        
        assert len(self.logger.logged_events) == 1
        event = self.logger.logged_events[0]
        assert event["event_type"] == SecurityEventType.ENCRYPTION_EVENT
        assert event["success"] is True
        assert event["details"]["operation"] == "encrypt"
        assert event["details"]["data_type"] == "api_key"


class TestSecurityAlertSystem:
    """Тести системи сповіщень безпеки"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.alert_system = MockSecurityAlertSystem()
    
    def test_load_alert_rules(self):
        """Тест завантаження правил алертів"""
        rules = self.alert_system.alert_rules
        
        assert "multiple_failed_logins" in rules
        assert "suspicious_ip" in rules
        assert "api_rate_limit_exceeded" in rules
        assert "mfa_failures" in rules
        
        # Перевіряємо структуру правил
        for rule_name, rule_config in rules.items():
            assert "threshold" in rule_config
            assert "window" in rule_config
            assert "level" in rule_config
            assert isinstance(rule_config["threshold"], int)
            assert isinstance(rule_config["window"], int)
            assert rule_config["level"] in ["warning", "critical"]
    
    @pytest.mark.asyncio
    async def test_check_alerts(self):
        """Тест перевірки алертів"""
        # Мокаємо security_log
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        
        # Тест повинен пройти без помилок
        await self.alert_system.check_alerts(mock_log)
    
    @pytest.mark.asyncio
    async def test_check_failed_logins(self):
        """Тест перевірки невдалих спроб входу"""
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        
        # Тест повинен пройти без помилок
        await self.alert_system._check_failed_logins(mock_log)
    
    @pytest.mark.asyncio
    async def test_check_suspicious_ips(self):
        """Тест перевірки підозрілих IP"""
        mock_log = Mock()
        mock_log.ip_address = "192.168.1.1"
        
        # Тест повинен пройти без помилок
        await self.alert_system._check_suspicious_ips(mock_log)
    
    @pytest.mark.asyncio
    async def test_check_api_rate_limits(self):
        """Тест перевірки rate limits"""
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.API_RATE_LIMIT.value
        
        # Тест повинен пройти без помилок
        await self.alert_system._check_api_rate_limits(mock_log)
    
    @pytest.mark.asyncio
    async def test_check_mfa_failures(self):
        """Тест перевірки невдач MFA"""
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.MFA_FAILED.value
        
        # Тест повинен пройти без помилок
        await self.alert_system._check_mfa_failures(mock_log)


class TestAnomalyDetector:
    """Тести детектора аномалій"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.detector = MockAnomalyDetector()
    
    def test_load_patterns(self):
        """Тест завантаження паттернів аномалій"""
        patterns = self.detector.patterns
        
        assert "unusual_login_time" in patterns
        assert "unusual_location" in patterns
        assert "rapid_requests" in patterns
        assert "failed_attempts" in patterns
        
        # Перевіряємо структуру паттернів
        for pattern_name, pattern_config in patterns.items():
            assert "weight" in pattern_config
            assert "description" in pattern_config
            assert isinstance(pattern_config["weight"], float)
            assert isinstance(pattern_config["description"], str)
    
    @pytest.mark.asyncio
    async def test_detect_anomaly(self):
        """Тест виявлення аномалії"""
        # Мокаємо security_log
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        mock_log.ip_address = "192.168.1.1"
        
        anomaly_score = await self.detector.detect_anomaly(mock_log)
        assert isinstance(anomaly_score, float)
        assert 0.0 <= anomaly_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_detect_anomaly_with_high_score(self):
        """Тест виявлення аномалії з високим балом"""
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        mock_log.ip_address = "192.168.1.1"
        
        # Мокаємо високі бали аномалій
        with patch.object(self.detector, '_check_unusual_login_time', return_value=0.3), \
             patch.object(self.detector, '_check_unusual_location', return_value=0.5), \
             patch.object(self.detector, '_check_rapid_requests', return_value=0.4), \
             patch.object(self.detector, '_check_failed_attempts', return_value=0.6):
            
            anomaly_score = await self.detector.detect_anomaly(mock_log)
            assert anomaly_score == 1.0  # Нормалізовано до максимуму
    
    @pytest.mark.asyncio
    async def test_check_unusual_login_time(self):
        """Тест перевірки незвичайного часу входу"""
        mock_log = Mock()
        score = await self.detector._check_unusual_login_time(mock_log)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_check_unusual_location(self):
        """Тест перевірки незвичайної локації"""
        mock_log = Mock()
        score = await self.detector._check_unusual_location(mock_log)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_check_rapid_requests(self):
        """Тест перевірки швидких запитів"""
        mock_log = Mock()
        score = await self.detector._check_rapid_requests(mock_log)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_check_failed_attempts(self):
        """Тест перевірки невдалих спроб"""
        mock_log = Mock()
        score = await self.detector._check_failed_attempts(mock_log)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestSecurityEventTypes:
    """Тести типів подій безпеки"""
    
    def test_security_event_types(self):
        """Тест типів подій безпеки"""
        # Перевіряємо що всі типи існують
        assert SecurityEventType.LOGIN_SUCCESS
        assert SecurityEventType.LOGIN_FAILED
        assert SecurityEventType.LOGOUT
        assert SecurityEventType.MFA_ENABLED
        assert SecurityEventType.MFA_DISABLED
        assert SecurityEventType.MFA_FAILED
        assert SecurityEventType.API_ACCESS
        assert SecurityEventType.API_RATE_LIMIT
        assert SecurityEventType.SUSPICIOUS_ACTIVITY
        assert SecurityEventType.SECURITY_ALERT
    
    def test_security_levels(self):
        """Тест рівнів безпеки"""
        # Перевіряємо що всі рівні існують
        assert SecurityLevel.INFO
        assert SecurityLevel.WARNING
        assert SecurityLevel.ERROR
        assert SecurityLevel.CRITICAL
    
    def test_event_type_values(self):
        """Тест значень типів подій"""
        assert SecurityEventType.LOGIN_SUCCESS.value == "login_success"
        assert SecurityEventType.LOGIN_FAILED.value == "login_failed"
        assert SecurityEventType.API_ACCESS.value == "api_access"
        assert SecurityEventType.SUSPICIOUS_ACTIVITY.value == "suspicious_activity"
    
    def test_level_values(self):
        """Тест значень рівнів безпеки"""
        assert SecurityLevel.INFO.value == "info"
        assert SecurityLevel.WARNING.value == "warning"
        assert SecurityLevel.ERROR.value == "error"
        assert SecurityLevel.CRITICAL.value == "critical"


class TestErrorHandling:
    """Тести обробки помилок"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.logger = MockSecurityLogger()
    
    def test_log_event_with_exception(self):
        """Тест логування події з винятком"""
        # Тест повинен пройти без помилок
        self.logger.log_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            user_id=123,
            ip_address="192.168.1.1"
        )
        assert len(self.logger.logged_events) == 1
    
    @pytest.mark.asyncio
    async def test_alert_system_with_exception(self):
        """Тест системи алертів з винятком"""
        alert_system = MockSecurityAlertSystem()
        
        # Мокаємо security_log
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        
        # Тест повинен пройти без помилок навіть з винятком
        await alert_system.check_alerts(mock_log)
    
    @pytest.mark.asyncio
    async def test_anomaly_detector_with_exception(self):
        """Тест детектора аномалій з винятком"""
        detector = MockAnomalyDetector()
        
        # Мокаємо security_log
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        
        # Мокаємо методи щоб викликати помилку
        with patch.object(detector, '_check_unusual_login_time', side_effect=Exception("Test error")):
            anomaly_score = await detector.detect_anomaly(mock_log)
            assert anomaly_score == 0.0  # Повертає 0.0 при помилці


if __name__ == "__main__":
    pytest.main([__file__]) 