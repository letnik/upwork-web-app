"""
Розширені алерти з умовними правилами та розумними нотифікаціями
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import re

from shared.config.logging import get_logger


class AlertCondition(Enum):
    """Типи умов алертів"""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX_MATCH = "regex_match"
    CUSTOM_FUNCTION = "custom_function"


class AlertSeverity(Enum):
    """Рівні серйозності алертів"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AlertCondition:
    """Умова алерту"""
    field: str
    condition: AlertCondition
    value: Any
    custom_function: Optional[Callable] = None


@dataclass
class AdvancedAlertRule:
    """Розширене правило алерту"""
    name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity
    time_window_minutes: int
    cooldown_minutes: int
    notification_channels: List[str]
    escalation_rules: List[Dict[str, Any]] = None
    enabled: bool = True
    custom_actions: List[Callable] = None


@dataclass
class AlertContext:
    """Контекст алерту"""
    rule_name: str
    severity: AlertSeverity
    triggered_at: datetime
    conditions_met: List[str]
    current_values: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    recommendations: List[str]


class AdvancedAlertingSystem:
    """Розширена система алертів"""
    
    def __init__(self):
        self.rules: List[AdvancedAlertRule] = []
        self.active_alerts: Dict[str, AlertContext] = {}
        self.alert_history: List[AlertContext] = []
        self.escalation_history: Dict[str, List[datetime]] = {}
        
        self.logger = get_logger("advanced-alerting")
        
        # Налаштування нотифікацій
        self.notification_config = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@example.com",
                "password": "your-password",
                "recipients": ["admin@example.com", "dev@example.com"]
            },
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/...",
                "channel": "#alerts"
            },
            "telegram": {
                "enabled": False,
                "bot_token": "your-bot-token",
                "chat_id": "your-chat-id"
            },
            "pagerduty": {
                "enabled": False,
                "api_key": "your-api-key",
                "service_id": "your-service-id"
            }
        }
        
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Налаштування стандартних правил алертів"""
        
        # Правило: Високий CPU + повільні відповіді
        high_cpu_slow_response = AdvancedAlertRule(
            name="High CPU with Slow Responses",
            description="Система перевантажена з повільними відповідями",
            conditions=[
                AlertCondition("cpu_usage", AlertCondition.GREATER_THAN, 80),
                AlertCondition("avg_response_time", AlertCondition.GREATER_THAN, 2000)
            ],
            severity=AlertSeverity.HIGH,
            time_window_minutes=5,
            cooldown_minutes=15,
            notification_channels=["email", "slack"],
            escalation_rules=[
                {"delay_minutes": 10, "channels": ["pagerduty"]},
                {"delay_minutes": 30, "channels": ["phone"]}
            ],
            custom_actions=[self._auto_scale_service]
        )
        
        # Правило: Багато помилок 500
        high_500_errors = AdvancedAlertRule(
            name="High 500 Error Rate",
            description="Високий рівень серверних помилок",
            conditions=[
                AlertCondition("error_500_count", AlertCondition.GREATER_THAN, 10),
                AlertCondition("error_rate_percent", AlertCondition.GREATER_THAN, 5)
            ],
            severity=AlertSeverity.CRITICAL,
            time_window_minutes=2,
            cooldown_minutes=10,
            notification_channels=["email", "slack", "pagerduty"],
            custom_actions=[self._restart_service, self._rollback_deployment]
        )
        
        # Правило: Підозріла активність
        suspicious_activity = AdvancedAlertRule(
            name="Suspicious Activity Detected",
            description="Виявлено підозрілу активність",
            conditions=[
                AlertCondition("failed_logins", AlertCondition.GREATER_THAN, 5),
                AlertCondition("unauthorized_access", AlertCondition.GREATER_THAN, 3)
            ],
            severity=AlertSeverity.HIGH,
            time_window_minutes=1,
            cooldown_minutes=5,
            notification_channels=["email", "slack", "telegram"],
            custom_actions=[self._block_suspicious_ips]
        )
        
        # Правило: Деградація продуктивності
        performance_degradation = AdvancedAlertRule(
            name="Performance Degradation",
            description="Продуктивність сервісу знизилася",
            conditions=[
                AlertCondition("performance_degradation_percent", AlertCondition.GREATER_THAN, 50)
            ],
            severity=AlertSeverity.MEDIUM,
            time_window_minutes=10,
            cooldown_minutes=20,
            notification_channels=["email", "slack"],
            custom_actions=[self._optimize_queries]
        )
        
        self.add_rule(high_cpu_slow_response)
        self.add_rule(high_500_errors)
        self.add_rule(suspicious_activity)
        self.add_rule(performance_degradation)
    
    def add_rule(self, rule: AdvancedAlertRule):
        """Додавання правила алерту"""
        self.rules.append(rule)
        self.logger.info(f"Додано розширене правило алерту: {rule.name}")
    
    def add_custom_condition(self, name: str, condition_func: Callable):
        """Додавання кастомної умови"""
        setattr(AlertCondition, name.upper(), condition_func)
        self.logger.info(f"Додано кастомну умову: {name}")
    
    async def check_alerts(self, current_metrics: Dict[str, Any], 
                          historical_data: List[Dict[str, Any]] = None) -> List[AlertContext]:
        """Перевірка умов для алертів"""
        triggered_alerts = []
        current_time = datetime.utcnow()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Перевірка cooldown
            if self._is_in_cooldown(rule.name, current_time):
                continue
            
            # Перевірка умов
            conditions_met = []
            all_conditions_met = True
            
            for condition in rule.conditions:
                if self._evaluate_condition(condition, current_metrics, historical_data):
                    conditions_met.append(f"{condition.field} {condition.condition.value} {condition.value}")
                else:
                    all_conditions_met = False
                    break
            
            if all_conditions_met:
                # Створення контексту алерту
                alert_context = AlertContext(
                    rule_name=rule.name,
                    severity=rule.severity,
                    triggered_at=current_time,
                    conditions_met=conditions_met,
                    current_values=current_metrics,
                    historical_data=historical_data or [],
                    recommendations=self._generate_recommendations(rule, current_metrics)
                )
                
                triggered_alerts.append(alert_context)
                self.active_alerts[rule.name] = alert_context
                self.alert_history.append(alert_context)
                
                # Виконання кастомних дій
                if rule.custom_actions:
                    await self._execute_custom_actions(rule.custom_actions, alert_context)
                
                # Відправка сповіщень
                await self._send_notifications(alert_context, rule)
                
                # Перевірка ескалації
                await self._check_escalation(alert_context, rule)
        
        return triggered_alerts
    
    def _evaluate_condition(self, condition: AlertCondition, current_metrics: Dict[str, Any], 
                           historical_data: List[Dict[str, Any]] = None) -> bool:
        """Оцінка умови алерту"""
        field_value = current_metrics.get(condition.field)
        
        if condition.condition == AlertCondition.GREATER_THAN:
            return field_value > condition.value
        elif condition.condition == AlertCondition.LESS_THAN:
            return field_value < condition.value
        elif condition.condition == AlertCondition.EQUALS:
            return field_value == condition.value
        elif condition.condition == AlertCondition.NOT_EQUALS:
            return field_value != condition.value
        elif condition.condition == AlertCondition.CONTAINS:
            return condition.value in str(field_value)
        elif condition.condition == AlertCondition.NOT_CONTAINS:
            return condition.value not in str(field_value)
        elif condition.condition == AlertCondition.REGEX_MATCH:
            return bool(re.search(condition.value, str(field_value)))
        elif condition.condition == AlertCondition.CUSTOM_FUNCTION:
            return condition.custom_function(field_value, current_metrics, historical_data)
        
        return False
    
    def _is_in_cooldown(self, rule_name: str, current_time: datetime) -> bool:
        """Перевірка чи правило в cooldown періоді"""
        if rule_name not in self.active_alerts:
            return False
        
        last_alert = self.active_alerts[rule_name]
        rule = next((r for r in self.rules if r.name == rule_name), None)
        
        if not rule:
            return False
        
        time_since_alert = current_time - last_alert.triggered_at
        return time_since_alert.total_seconds() < rule.cooldown_minutes * 60
    
    def _generate_recommendations(self, rule: AdvancedAlertRule, 
                                current_metrics: Dict[str, Any]) -> List[str]:
        """Генерація рекомендацій на основі правил"""
        recommendations = []
        
        if "cpu_usage" in current_metrics and current_metrics["cpu_usage"] > 80:
            recommendations.append("Розгляньте можливість масштабування сервісу")
        
        if "avg_response_time" in current_metrics and current_metrics["avg_response_time"] > 2000:
            recommendations.append("Оптимізуйте запити до бази даних")
        
        if "error_500_count" in current_metrics and current_metrics["error_500_count"] > 10:
            recommendations.append("Перевірте логи додатку на наявність помилок")
        
        if "failed_logins" in current_metrics and current_metrics["failed_logins"] > 5:
            recommendations.append("Перевірте систему безпеки на наявність атак")
        
        return recommendations
    
    async def _execute_custom_actions(self, actions: List[Callable], 
                                    alert_context: AlertContext):
        """Виконання кастомних дій"""
        for action in actions:
            try:
                if asyncio.iscoroutinefunction(action):
                    await action(alert_context)
                else:
                    action(alert_context)
                
                self.logger.info(f"Виконано кастомну дію: {action.__name__}")
                
            except Exception as e:
                self.logger.error(f"Помилка виконання кастомної дії {action.__name__}", 
                                extra={"error": str(e)})
    
    async def _send_notifications(self, alert_context: AlertContext, rule: AdvancedAlertRule):
        """Відправка сповіщень"""
        channels = self._get_notification_channels(rule, alert_context)
        
        for channel in channels:
            try:
                if channel == "email":
                    await self._send_email_notification(alert_context, rule)
                elif channel == "slack":
                    await self._send_slack_notification(alert_context, rule)
                elif channel == "telegram":
                    await self._send_telegram_notification(alert_context, rule)
                elif channel == "pagerduty":
                    await self._send_pagerduty_notification(alert_context, rule)
                
            except Exception as e:
                self.logger.error(f"Помилка відправки сповіщення через {channel}", 
                                extra={"error": str(e)})
    
    def _get_notification_channels(self, rule: AdvancedAlertRule, 
                                 alert_context: AlertContext) -> List[str]:
        """Визначення каналів сповіщень"""
        channels = rule.notification_channels.copy()
        
        # Додавання каналів на основі серйозності
        if alert_context.severity == AlertSeverity.CRITICAL:
            if "pagerduty" not in channels:
                channels.append("pagerduty")
        
        # Додавання каналів на основі часу
        current_hour = datetime.utcnow().hour
        if 9 <= current_hour <= 18:  # Робочі години
            if "slack" not in channels:
                channels.append("slack")
        
        return channels
    
    async def _check_escalation(self, alert_context: AlertContext, rule: AdvancedAlertRule):
        """Перевірка ескалації алерту"""
        if not rule.escalation_rules:
            return
        
        current_time = datetime.utcnow()
        alert_id = f"{rule.name}_{alert_context.triggered_at.isoformat()}"
        
        if alert_id not in self.escalation_history:
            self.escalation_history[alert_id] = []
        
        for escalation_rule in rule.escalation_rules:
            delay_minutes = escalation_rule.get("delay_minutes", 0)
            escalation_time = alert_context.triggered_at + timedelta(minutes=delay_minutes)
            
            if current_time >= escalation_time and escalation_time not in self.escalation_history[alert_id]:
                # Ескалація алерту
                await self._escalate_alert(alert_context, escalation_rule)
                self.escalation_history[alert_id].append(escalation_time)
    
    async def _escalate_alert(self, alert_context: AlertContext, escalation_rule: Dict[str, Any]):
        """Ескалація алерту"""
        escalation_channels = escalation_rule.get("channels", [])
        
        for channel in escalation_channels:
            try:
                if channel == "pagerduty":
                    await self._send_pagerduty_escalation(alert_context)
                elif channel == "phone":
                    await self._send_phone_notification(alert_context)
                
                self.logger.info(f"Алерт ескальовано через {channel}")
                
            except Exception as e:
                self.logger.error(f"Помилка ескалації через {channel}", extra={"error": str(e)})
    
    # Кастомні дії
    async def _auto_scale_service(self, alert_context: AlertContext):
        """Автоматичне масштабування сервісу"""
        self.logger.info("Виконується автоматичне масштабування сервісу")
        # Логіка масштабування
    
    async def _restart_service(self, alert_context: AlertContext):
        """Перезапуск сервісу"""
        self.logger.info("Виконується перезапуск сервісу")
        # Логіка перезапуску
    
    async def _rollback_deployment(self, alert_context: AlertContext):
        """Відкат деплойменту"""
        self.logger.info("Виконується відкат деплойменту")
        # Логіка відкату
    
    async def _block_suspicious_ips(self, alert_context: AlertContext):
        """Блокування підозрілих IP"""
        self.logger.info("Блокування підозрілих IP адрес")
        # Логіка блокування
    
    async def _optimize_queries(self, alert_context: AlertContext):
        """Оптимізація запитів"""
        self.logger.info("Виконується оптимізація запитів")
        # Логіка оптимізації
    
    # Методи відправки сповіщень
    async def _send_email_notification(self, alert_context: AlertContext, rule: AdvancedAlertRule):
        """Відправка email сповіщення"""
        # Реалізація відправки email
        pass
    
    async def _send_slack_notification(self, alert_context: AlertContext, rule: AdvancedAlertRule):
        """Відправка Slack сповіщення"""
        # Реалізація відправки Slack
        pass
    
    async def _send_telegram_notification(self, alert_context: AlertContext, rule: AdvancedAlertRule):
        """Відправка Telegram сповіщення"""
        # Реалізація відправки Telegram
        pass
    
    async def _send_pagerduty_notification(self, alert_context: AlertContext, rule: AdvancedAlertRule):
        """Відправка PagerDuty сповіщення"""
        # Реалізація відправки PagerDuty
        pass
    
    async def _send_pagerduty_escalation(self, alert_context: AlertContext):
        """Ескалація через PagerDuty"""
        # Реалізація ескалації
        pass
    
    async def _send_phone_notification(self, alert_context: AlertContext):
        """Відправка телефонного сповіщення"""
        # Реалізація телефонного сповіщення
        pass
    
    def resolve_alert(self, rule_name: str):
        """Вирішення алерту"""
        if rule_name in self.active_alerts:
            del self.active_alerts[rule_name]
            self.logger.info(f"Алерт вирішено: {rule_name}")
    
    def get_active_alerts(self) -> List[AlertContext]:
        """Отримання активних алертів"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[AlertContext]:
        """Отримання історії алертів"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.triggered_at > cutoff_time]


# Глобальний екземпляр розширеної системи алертів
advanced_alerting_system = AdvancedAlertingSystem()


def get_advanced_alerting_system() -> AdvancedAlertingSystem:
    """Отримання розширеної системи алертів"""
    return advanced_alerting_system 