"""
Безпечні тести для детекції аномалій
SECURITY-009: Детекція аномалій та система сповіщень
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from enum import Enum


class SecurityEventType(Enum):
    """Типи подій безпеки"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    API_ACCESS = "api_access"
    API_RATE_LIMIT = "api_rate_limit"
    MFA_FAILED = "mfa_failed"


class SecurityLevel(Enum):
    """Рівні безпеки"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AnomalySeverity(Enum):
    """Рівні серйозності аномалій"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MockSecurityLogger:
    """Мок логера безпеки"""
    
    def __init__(self):
        self.logged_events = []
        self.logger = Mock()
    
    def log_event(self, **kwargs):
        """Логує подію"""
        self.logged_events.append(kwargs)


class MockAnomalyDetector:
    """Мок детектора аномалій"""
    
    def __init__(self, security_logger):
        self.security_logger = security_logger
        self.logger = security_logger.logger
        self.patterns = self._load_patterns()
        self.user_profiles = {}
        self.global_statistics = {}
        self.anomaly_history = []
    
    def _load_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Завантажує паттерни аномалій"""
        return {
            "unusual_login_time": {
                "weight": 0.3,
                "description": "Незвичайний час входу",
                "threshold": 0.7
            },
            "unusual_location": {
                "weight": 0.5,
                "description": "Незвичайна локація",
                "threshold": 0.8
            },
            "rapid_requests": {
                "weight": 0.4,
                "description": "Швидкі запити",
                "threshold": 0.6
            },
            "failed_attempts": {
                "weight": 0.6,
                "description": "Невдалі спроби",
                "threshold": 0.5
            }
        }
    
    async def detect_anomaly(self, security_log) -> tuple:
        """Виявляє аномалії"""
        try:
            anomaly_score = 0.0
            anomaly_details = []
            
            # Спрощена логіка для тестування
            if security_log.event_type == SecurityEventType.LOGIN_FAILED.value:
                anomaly_score = 0.8
                anomaly_details.append({
                    "type": "failed_attempts",
                    "score": 0.8,
                    "weight": 0.6,
                    "details": {"failed_count": 5},
                    "severity": "high"
                })
            elif security_log.event_type == SecurityEventType.API_RATE_LIMIT.value:
                anomaly_score = 0.6
                anomaly_details.append({
                    "type": "rapid_requests",
                    "score": 0.6,
                    "weight": 0.4,
                    "details": {"requests_count": 100},
                    "severity": "medium"
                })
            
            # Оновлюємо статистику
            await self._update_statistics(security_log, anomaly_score, anomaly_details)
            
            return anomaly_score, anomaly_details
            
        except Exception as e:
            self.logger.error(f"Помилка виявлення аномалії: {e}")
            return 0.0, []
    
    def _calculate_severity(self, score: float) -> AnomalySeverity:
        """Обчислює рівень серйозності"""
        if score >= 0.8:
            return AnomalySeverity.CRITICAL
        elif score >= 0.6:
            return AnomalySeverity.HIGH
        elif score >= 0.4:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    async def _update_statistics(self, security_log, anomaly_score: float, 
                                anomaly_details: List[Dict[str, Any]]) -> None:
        """Оновлює статистику"""
        try:
            anomaly_record = {
                "timestamp": datetime.utcnow(),
                "user_id": security_log.user_id,
                "ip_address": security_log.ip_address,
                "event_type": security_log.event_type,
                "anomaly_score": anomaly_score,
                "anomaly_details": anomaly_details,
                "severity": self._calculate_severity(anomaly_score).value
            }
            
            self.anomaly_history.append(anomaly_record)
            
            if len(self.anomaly_history) > 1000:
                self.anomaly_history = self.anomaly_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"Помилка оновлення статистики: {e}")
    
    async def get_anomaly_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Отримує статистику аномалій"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            recent_anomalies = [
                anomaly for anomaly in self.anomaly_history
                if anomaly["timestamp"] >= cutoff_date
            ]
            
            if not recent_anomalies:
                return {
                    "period_days": days,
                    "total_anomalies": 0,
                    "average_score": 0.0,
                    "severity_distribution": {},
                    "type_distribution": {}
                }
            
            total_anomalies = len(recent_anomalies)
            total_score = sum(anomaly["anomaly_score"] for anomaly in recent_anomalies)
            average_score = total_score / total_anomalies
            
            severity_counts = {}
            for anomaly in recent_anomalies:
                severity = anomaly["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            type_counts = {}
            for anomaly in recent_anomalies:
                for detail in anomaly["anomaly_details"]:
                    anomaly_type = detail["type"]
                    type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
            
            return {
                "period_days": days,
                "total_anomalies": total_anomalies,
                "average_score": average_score,
                "severity_distribution": severity_counts,
                "type_distribution": type_counts,
                "recent_anomalies": recent_anomalies[-10:]
            }
            
        except Exception as e:
            self.logger.error(f"Помилка отримання статистики аномалій: {e}")
            return {}


class TestAnomalyDetector:
    """Тести детектора аномалій"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.security_logger = MockSecurityLogger()
        self.detector = MockAnomalyDetector(self.security_logger)
    
    def test_load_patterns(self):
        """Тест завантаження паттернів"""
        patterns = self.detector.patterns
        
        assert "unusual_login_time" in patterns
        assert "unusual_location" in patterns
        assert "rapid_requests" in patterns
        assert "failed_attempts" in patterns
        
        # Перевіряємо структуру паттерну
        pattern = patterns["failed_attempts"]
        assert "weight" in pattern
        assert "description" in pattern
        assert "threshold" in pattern
        assert pattern["weight"] == 0.6
        assert pattern["threshold"] == 0.5
    
    @pytest.mark.asyncio
    async def test_detect_anomaly_failed_login(self):
        """Тест виявлення аномалії при невдалому вході"""
        # Створюємо мок security_log
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        mock_log.user_id = 123
        mock_log.ip_address = "192.168.1.1"
        mock_log.created_at = datetime.utcnow()
        
        # Виявляємо аномалію
        anomaly_score, anomaly_details = await self.detector.detect_anomaly(mock_log)
        
        assert anomaly_score > 0
        assert len(anomaly_details) > 0
        
        # Перевіряємо деталі
        detail = anomaly_details[0]
        assert detail["type"] == "failed_attempts"
        assert detail["score"] == 0.8
        assert detail["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_detect_anomaly_rate_limit(self):
        """Тест виявлення аномалії при перевищенні rate limit"""
        # Створюємо мок security_log
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.API_RATE_LIMIT.value
        mock_log.user_id = 123
        mock_log.ip_address = "192.168.1.1"
        mock_log.created_at = datetime.utcnow()
        
        # Виявляємо аномалію
        anomaly_score, anomaly_details = await self.detector.detect_anomaly(mock_log)
        
        assert anomaly_score > 0
        assert len(anomaly_details) > 0
        
        # Перевіряємо деталі
        detail = anomaly_details[0]
        assert detail["type"] == "rapid_requests"
        assert detail["score"] == 0.6
        assert detail["severity"] == "medium"
    
    @pytest.mark.asyncio
    async def test_detect_anomaly_normal_event(self):
        """Тест виявлення аномалії при нормальній події"""
        # Створюємо мок security_log для нормальної події
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_SUCCESS.value
        mock_log.user_id = 123
        mock_log.ip_address = "192.168.1.1"
        mock_log.created_at = datetime.utcnow()
        
        # Виявляємо аномалію
        anomaly_score, anomaly_details = await self.detector.detect_anomaly(mock_log)
        
        assert anomaly_score == 0.0
        assert len(anomaly_details) == 0
    
    def test_calculate_severity(self):
        """Тест обчислення серйозності"""
        # Критична серйозність
        severity = self.detector._calculate_severity(0.9)
        assert severity == AnomalySeverity.CRITICAL
        
        # Висока серйозність
        severity = self.detector._calculate_severity(0.7)
        assert severity == AnomalySeverity.HIGH
        
        # Середня серйозність
        severity = self.detector._calculate_severity(0.5)
        assert severity == AnomalySeverity.MEDIUM
        
        # Низька серйозність
        severity = self.detector._calculate_severity(0.3)
        assert severity == AnomalySeverity.LOW
    
    @pytest.mark.asyncio
    async def test_update_statistics(self):
        """Тест оновлення статистики"""
        # Створюємо мок security_log
        mock_log = Mock()
        mock_log.user_id = 123
        mock_log.ip_address = "192.168.1.1"
        mock_log.event_type = "test_event"
        
        # Оновлюємо статистику
        await self.detector._update_statistics(mock_log, 0.8, [{"type": "test"}])
        
        # Перевіряємо що запис додано
        assert len(self.detector.anomaly_history) > 0
        
        record = self.detector.anomaly_history[-1]
        assert record["user_id"] == 123
        assert record["ip_address"] == "192.168.1.1"
        assert record["anomaly_score"] == 0.8
        assert record["severity"] == "critical"
    
    @pytest.mark.asyncio
    async def test_get_anomaly_statistics(self):
        """Тест отримання статистики аномалій"""
        # Додаємо тестові аномалії
        mock_log = Mock()
        mock_log.user_id = 123
        mock_log.ip_address = "192.168.1.1"
        mock_log.event_type = "test_event"
        
        await self.detector._update_statistics(mock_log, 0.8, [{"type": "test"}])
        await self.detector._update_statistics(mock_log, 0.6, [{"type": "test2"}])
        
        # Отримуємо статистику
        statistics = await self.detector.get_anomaly_statistics(days=7)
        
        assert "period_days" in statistics
        assert "total_anomalies" in statistics
        assert "average_score" in statistics
        assert "severity_distribution" in statistics
        assert "type_distribution" in statistics
        
        assert statistics["period_days"] == 7
        assert statistics["total_anomalies"] == 2
        assert statistics["average_score"] == 0.7
    
    @pytest.mark.asyncio
    async def test_detect_anomaly_with_exception(self):
        """Тест обробки винятків при виявленні аномалій"""
        # Створюємо мок security_log що викликає помилку
        mock_log = Mock()
        mock_log.event_type = SecurityEventType.LOGIN_FAILED.value
        mock_log.user_id = 123
        mock_log.ip_address = "192.168.1.1"
        
        # Симулюємо помилку
        with patch.object(self.detector, '_update_statistics', side_effect=Exception("Test error")):
            anomaly_score, anomaly_details = await self.detector.detect_anomaly(mock_log)
            
            # Перевіряємо що помилка оброблена
            assert anomaly_score == 0.0
            assert len(anomaly_details) == 0


class TestAnomalySeverity:
    """Тести рівнів серйозності аномалій"""
    
    def test_severity_values(self):
        """Тест значень серйозності"""
        assert AnomalySeverity.LOW.value == "low"
        assert AnomalySeverity.MEDIUM.value == "medium"
        assert AnomalySeverity.HIGH.value == "high"
        assert AnomalySeverity.CRITICAL.value == "critical"
    
    def test_severity_comparison(self):
        """Тест порівняння серйозності"""
        # Перевіряємо що всі рівні серйозності унікальні
        severity_values = [s.value for s in AnomalySeverity]
        assert len(severity_values) == len(set(severity_values))
        
        # Перевіряємо що всі значення присутні
        assert "low" in severity_values
        assert "medium" in severity_values
        assert "high" in severity_values
        assert "critical" in severity_values


class TestSecurityEventType:
    """Тести типів подій безпеки"""
    
    def test_event_type_values(self):
        """Тест значень типів подій"""
        assert SecurityEventType.LOGIN_SUCCESS.value == "login_success"
        assert SecurityEventType.LOGIN_FAILED.value == "login_failed"
        assert SecurityEventType.API_ACCESS.value == "api_access"
        assert SecurityEventType.API_RATE_LIMIT.value == "api_rate_limit"
        assert SecurityEventType.MFA_FAILED.value == "mfa_failed"
    
    def test_event_type_enumeration(self):
        """Тест перелічення типів подій"""
        event_types = list(SecurityEventType)
        assert len(event_types) >= 5
        
        # Перевіряємо що всі типи мають унікальні значення
        values = [event.value for event in event_types]
        assert len(values) == len(set(values))


class TestMockSecurityLogger:
    """Тести мок логера безпеки"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.logger = MockSecurityLogger()
    
    def test_log_event(self):
        """Тест логування події"""
        event_data = {
            "event_type": "test_event",
            "user_id": 123,
            "ip_address": "192.168.1.1"
        }
        
        self.logger.log_event(**event_data)
        
        assert len(self.logger.logged_events) == 1
        logged_event = self.logger.logged_events[0]
        assert logged_event["event_type"] == "test_event"
        assert logged_event["user_id"] == 123
        assert logged_event["ip_address"] == "192.168.1.1"
    
    def test_logger_initialization(self):
        """Тест ініціалізації логера"""
        assert self.logger.logged_events == []
        assert self.logger.logger is not None 