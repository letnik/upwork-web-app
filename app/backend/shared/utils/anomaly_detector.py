"""
Розширений детектор аномалій
SECURITY-009: Детекція аномалій та система сповіщень
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import statistics
import math

from .security_logger import SecurityLogger, SecurityEventType, SecurityLevel


class AnomalyType(Enum):
    """Типи аномалій"""
    UNUSUAL_LOGIN_TIME = "unusual_login_time"
    UNUSUAL_LOCATION = "unusual_location"
    RAPID_REQUESTS = "rapid_requests"
    FAILED_ATTEMPTS = "failed_attempts"
    SUSPICIOUS_PATTERNS = "suspicious_patterns"
    BEHAVIOR_CHANGE = "behavior_change"
    BURST_ACTIVITY = "burst_activity"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"


class AnomalySeverity(Enum):
    """Рівні серйозності аномалій"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyDetector:
    """Розширений детектор аномалій з машинним навчанням"""
    
    def __init__(self, security_logger: SecurityLogger):
        self.security_logger = security_logger
        self.logger = security_logger.logger
        self.patterns = self._load_patterns()
        self.user_profiles = {}  # Профілі користувачів
        self.global_statistics = {}  # Глобальна статистика
        self.anomaly_history = []  # Історія аномалій
        
    def _load_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Завантажує розширені паттерни аномалій"""
        return {
            "unusual_login_time": {
                "weight": 0.3,
                "description": "Незвичайний час входу",
                "threshold": 0.7,
                "window_hours": 24
            },
            "unusual_location": {
                "weight": 0.5,
                "description": "Незвичайна локація",
                "threshold": 0.8,
                "max_distance_km": 1000
            },
            "rapid_requests": {
                "weight": 0.4,
                "description": "Швидкі запити",
                "threshold": 0.6,
                "max_requests_per_minute": 60
            },
            "failed_attempts": {
                "weight": 0.6,
                "description": "Невдалі спроби",
                "threshold": 0.5,
                "max_failures_per_hour": 5
            },
            "suspicious_patterns": {
                "weight": 0.7,
                "description": "Підозрілі паттерни",
                "threshold": 0.8,
                "patterns": ["admin", "config", "debug", "test"]
            },
            "behavior_change": {
                "weight": 0.5,
                "description": "Зміна поведінки",
                "threshold": 0.6,
                "learning_period_days": 7
            },
            "burst_activity": {
                "weight": 0.4,
                "description": "Спалах активності",
                "threshold": 0.7,
                "burst_threshold": 10
            },
            "geographic_anomaly": {
                "weight": 0.6,
                "description": "Географічна аномалія",
                "threshold": 0.8,
                "suspicious_countries": ["XX", "YY", "ZZ"]
            }
        }
    
    async def detect_anomaly(self, security_log) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Виявляє аномалії в події безпеки
        
        Args:
            security_log: Запис логу безпеки
            
        Returns:
            Tuple[float, List[Dict]]: (загальний бал аномалії, список деталей)
        """
        try:
            anomaly_score = 0.0
            anomaly_details = []
            
            # Перевіряємо різні типи аномалій
            time_anomaly = await self._check_unusual_login_time(security_log)
            location_anomaly = await self._check_unusual_location(security_log)
            rapid_anomaly = await self._check_rapid_requests(security_log)
            failed_anomaly = await self._check_failed_attempts(security_log)
            pattern_anomaly = await self._check_suspicious_patterns(security_log)
            behavior_anomaly = await self._check_behavior_change(security_log)
            burst_anomaly = await self._check_burst_activity(security_log)
            geo_anomaly = await self._check_geographic_anomaly(security_log)
            
            # Збираємо всі аномалії
            anomalies = [
                ("unusual_login_time", time_anomaly),
                ("unusual_location", location_anomaly),
                ("rapid_requests", rapid_anomaly),
                ("failed_attempts", failed_anomaly),
                ("suspicious_patterns", pattern_anomaly),
                ("behavior_change", behavior_anomaly),
                ("burst_activity", burst_anomaly),
                ("geographic_anomaly", geo_anomaly)
            ]
            
            # Обчислюємо загальний бал
            for anomaly_type, (score, details) in anomalies:
                if score > 0:
                    weight = self.patterns[anomaly_type]["weight"]
                    anomaly_score += score * weight
                    
                    if details:
                        anomaly_details.append({
                            "type": anomaly_type,
                            "score": score,
                            "weight": weight,
                            "details": details,
                            "severity": self._calculate_severity(score)
                        })
            
            # Нормалізуємо результат
            anomaly_score = min(anomaly_score, 1.0)
            
            # Оновлюємо статистику
            await self._update_statistics(security_log, anomaly_score, anomaly_details)
            
            return anomaly_score, anomaly_details
            
        except Exception as e:
            self.logger.error(f"Помилка виявлення аномалії: {e}")
            return 0.0, []
    
    async def _check_unusual_login_time(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє незвичайний час входу"""
        try:
            if security_log.event_type != SecurityEventType.LOGIN_SUCCESS.value:
                return 0.0, {}
            
            current_hour = datetime.utcnow().hour
            user_id = security_log.user_id
            
            # Отримуємо історію входів користувача
            user_history = await self._get_user_login_history(user_id)
            
            if not user_history:
                return 0.0, {}
            
            # Обчислюємо середній час входу
            login_hours = [login.hour for login in user_history]
            mean_hour = statistics.mean(login_hours)
            std_hour = statistics.stdev(login_hours) if len(login_hours) > 1 else 2
            
            # Перевіряємо чи поточний час значно відрізняється
            z_score = abs(current_hour - mean_hour) / std_hour if std_hour > 0 else 0
            
            if z_score > 2.0:  # Більше 2 стандартних відхилень
                score = min(z_score / 4.0, 1.0)  # Нормалізуємо до 1.0
                return score, {
                    "current_hour": current_hour,
                    "mean_hour": mean_hour,
                    "std_hour": std_hour,
                    "z_score": z_score,
                    "unusual": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки часу входу: {e}")
            return 0.0, {}
    
    async def _check_unusual_location(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє незвичайну локацію"""
        try:
            if not security_log.ip_address:
                return 0.0, {}
            
            user_id = security_log.user_id
            current_ip = security_log.ip_address
            
            # Отримуємо історію IP адрес користувача
            user_ips = await self._get_user_ip_history(user_id)
            
            if not user_ips:
                return 0.0, {}
            
            # Перевіряємо чи IP адреса нова для користувача
            if current_ip not in user_ips:
                # Спрощена логіка - в реальному проекті тут була б геолокація
                score = 0.8  # Висока ймовірність аномалії для нової IP
                return score, {
                    "current_ip": current_ip,
                    "known_ips": user_ips,
                    "new_ip": True,
                    "unusual": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки локації: {e}")
            return 0.0, {}
    
    async def _check_rapid_requests(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє швидкі запити"""
        try:
            ip_address = security_log.ip_address
            if not ip_address:
                return 0.0, {}
            
            # Отримуємо кількість запитів за останню хвилину
            recent_requests = await self._get_recent_requests(ip_address, minutes=1)
            
            max_requests = self.patterns["rapid_requests"]["max_requests_per_minute"]
            
            if len(recent_requests) > max_requests:
                score = min(len(recent_requests) / (max_requests * 2), 1.0)
                return score, {
                    "requests_count": len(recent_requests),
                    "max_allowed": max_requests,
                    "time_window": "1 minute",
                    "rapid": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки швидких запитів: {e}")
            return 0.0, {}
    
    async def _check_failed_attempts(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє невдалі спроби"""
        try:
            if security_log.event_type != SecurityEventType.LOGIN_FAILED.value:
                return 0.0, {}
            
            ip_address = security_log.ip_address
            if not ip_address:
                return 0.0, {}
            
            # Отримуємо кількість невдалих спроб за останню годину
            failed_attempts = await self._get_failed_attempts(ip_address, hours=1)
            
            max_failures = self.patterns["failed_attempts"]["max_failures_per_hour"]
            
            if len(failed_attempts) > max_failures:
                score = min(len(failed_attempts) / (max_failures * 2), 1.0)
                return score, {
                    "failed_count": len(failed_attempts),
                    "max_allowed": max_failures,
                    "time_window": "1 hour",
                    "suspicious": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки невдалих спроб: {e}")
            return 0.0, {}
    
    async def _check_suspicious_patterns(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє підозрілі паттерни"""
        try:
            user_agent = security_log.user_agent or ""
            endpoint = security_log.details.get("endpoint", "") if security_log.details else ""
            
            suspicious_patterns = self.patterns["suspicious_patterns"]["patterns"]
            
            # Перевіряємо User-Agent
            user_agent_lower = user_agent.lower()
            suspicious_ua_patterns = ["bot", "crawler", "scraper", "spider", "curl", "wget"]
            
            ua_score = 0.0
            for pattern in suspicious_ua_patterns:
                if pattern in user_agent_lower:
                    ua_score += 0.3
            
            # Перевіряємо endpoint
            endpoint_score = 0.0
            for pattern in suspicious_patterns:
                if pattern in endpoint.lower():
                    endpoint_score += 0.5
            
            total_score = min(ua_score + endpoint_score, 1.0)
            
            if total_score > 0:
                return total_score, {
                    "user_agent": user_agent,
                    "endpoint": endpoint,
                    "suspicious_patterns": suspicious_patterns,
                    "ua_score": ua_score,
                    "endpoint_score": endpoint_score,
                    "suspicious": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки підозрілих паттернів: {e}")
            return 0.0, {}
    
    async def _check_behavior_change(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє зміну поведінки користувача"""
        try:
            user_id = security_log.user_id
            if not user_id:
                return 0.0, {}
            
            # Отримуємо профіль користувача
            user_profile = await self._get_user_profile(user_id)
            
            if not user_profile:
                return 0.0, {}
            
            # Аналізуємо поточну активність
            current_activity = {
                "event_type": security_log.event_type,
                "ip_address": security_log.ip_address,
                "user_agent": security_log.user_agent,
                "timestamp": security_log.created_at
            }
            
            # Порівнюємо з типовою поведінкою
            behavior_score = await self._compare_behavior(user_profile, current_activity)
            
            if behavior_score > 0.5:
                return behavior_score, {
                    "user_profile": user_profile,
                    "current_activity": current_activity,
                    "behavior_change": True,
                    "score": behavior_score
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки зміни поведінки: {e}")
            return 0.0, {}
    
    async def _check_burst_activity(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє спалах активності"""
        try:
            user_id = security_log.user_id
            if not user_id:
                return 0.0, {}
            
            # Отримуємо активність користувача за останні 10 хвилин
            recent_activity = await self._get_user_recent_activity(user_id, minutes=10)
            
            burst_threshold = self.patterns["burst_activity"]["burst_threshold"]
            
            if len(recent_activity) > burst_threshold:
                score = min(len(recent_activity) / (burst_threshold * 2), 1.0)
                return score, {
                    "activity_count": len(recent_activity),
                    "burst_threshold": burst_threshold,
                    "time_window": "10 minutes",
                    "burst": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки спалаху активності: {e}")
            return 0.0, {}
    
    async def _check_geographic_anomaly(self, security_log) -> Tuple[float, Dict[str, Any]]:
        """Перевіряє географічну аномалію"""
        try:
            ip_address = security_log.ip_address
            if not ip_address:
                return 0.0, {}
            
            # Спрощена логіка - в реальному проекті тут була б геолокація
            suspicious_countries = self.patterns["geographic_anomaly"]["suspicious_countries"]
            
            # Імітуємо геолокацію на основі IP
            country_code = self._get_country_from_ip(ip_address)
            
            if country_code in suspicious_countries:
                return 0.8, {
                    "ip_address": ip_address,
                    "country_code": country_code,
                    "suspicious_countries": suspicious_countries,
                    "geographic_anomaly": True
                }
            
            return 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки географічної аномалії: {e}")
            return 0.0, {}
    
    def _calculate_severity(self, score: float) -> AnomalySeverity:
        """Обчислює рівень серйозності аномалії"""
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
        """Оновлює статистику аномалій"""
        try:
            # Зберігаємо аномалію в історію
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
            
            # Обмежуємо історію до останніх 1000 записів
            if len(self.anomaly_history) > 1000:
                self.anomaly_history = self.anomaly_history[-1000:]
            
            # Оновлюємо глобальну статистику
            await self._update_global_statistics(anomaly_score, anomaly_details)
            
        except Exception as e:
            self.logger.error(f"Помилка оновлення статистики: {e}")
    
    async def _update_global_statistics(self, anomaly_score: float, 
                                      anomaly_details: List[Dict[str, Any]]) -> None:
        """Оновлює глобальну статистику аномалій"""
        try:
            current_time = datetime.utcnow()
            
            # Статистика за день
            day_key = current_time.strftime("%Y-%m-%d")
            if day_key not in self.global_statistics:
                self.global_statistics[day_key] = {
                    "total_anomalies": 0,
                    "total_score": 0.0,
                    "severity_counts": {
                        "low": 0, "medium": 0, "high": 0, "critical": 0
                    },
                    "type_counts": {}
                }
            
            day_stats = self.global_statistics[day_key]
            day_stats["total_anomalies"] += 1
            day_stats["total_score"] += anomaly_score
            
            # Підрахунок по серйозності
            severity = self._calculate_severity(anomaly_score).value
            day_stats["severity_counts"][severity] += 1
            
            # Підрахунок по типах аномалій
            for detail in anomaly_details:
                anomaly_type = detail["type"]
                if anomaly_type not in day_stats["type_counts"]:
                    day_stats["type_counts"][anomaly_type] = 0
                day_stats["type_counts"][anomaly_type] += 1
            
        except Exception as e:
            self.logger.error(f"Помилка оновлення глобальної статистики: {e}")
    
    # Допоміжні методи (моки для тестування)
    async def _get_user_login_history(self, user_id: int) -> List[datetime]:
        """Отримує історію входів користувача"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_user_ip_history(self, user_id: int) -> List[str]:
        """Отримує історію IP адрес користувача"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_recent_requests(self, ip_address: str, minutes: int) -> List[Any]:
        """Отримує нещодавні запити з IP"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_failed_attempts(self, ip_address: str, hours: int) -> List[Any]:
        """Отримує невдалі спроби з IP"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Отримує профіль користувача"""
        # Мок - в реальному проекті тут був би запит до БД
        return {}
    
    async def _compare_behavior(self, user_profile: Dict[str, Any], 
                               current_activity: Dict[str, Any]) -> float:
        """Порівнює поточну активність з профілем користувача"""
        # Мок - в реальному проекті тут була б логіка порівняння
        return 0.0
    
    async def _get_user_recent_activity(self, user_id: int, minutes: int) -> List[Any]:
        """Отримує нещодавню активність користувача"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    def _get_country_from_ip(self, ip_address: str) -> str:
        """Отримує країну з IP адреси"""
        # Мок - в реальному проекті тут була б геолокація
        return "US"
    
    async def get_anomaly_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Отримує статистику аномалій"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Фільтруємо аномалії за період
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
            
            # Обчислюємо статистику
            total_anomalies = len(recent_anomalies)
            total_score = sum(anomaly["anomaly_score"] for anomaly in recent_anomalies)
            average_score = total_score / total_anomalies
            
            # Розподіл по серйозності
            severity_counts = {}
            for anomaly in recent_anomalies:
                severity = anomaly["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Розподіл по типах
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
                "recent_anomalies": recent_anomalies[-10:]  # Останні 10 аномалій
            }
            
        except Exception as e:
            self.logger.error(f"Помилка отримання статистики аномалій: {e}")
            return {} 