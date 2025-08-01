"""
Система розумних алертів для логування
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

from shared.config.logging import get_logger


class AlertSeverity(Enum):
    """Рівні серйозності алертів"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Типи алертів"""
    ERROR_THRESHOLD = "error_threshold"
    RESPONSE_TIME = "response_time"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_DOWN = "service_down"
    DISK_SPACE = "disk_space"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"


@dataclass
class AlertRule:
    """Правило алерту"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: Callable[[List[Dict]], bool]
    threshold: float
    time_window_minutes: int
    cooldown_minutes: int
    notification_channels: List[str]
    description: str
    enabled: bool = True


@dataclass
class Alert:
    """Алерт"""
    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    service_name: str
    environment: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertingSystem:
    """Система розумних алертів"""
    
    def __init__(self):
        self.logger = get_logger("alerting-system")
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_check_time = datetime.utcnow()
        
        # Налаштування сповіщень
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
            }
        }
        
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Налаштування стандартних правил алертів"""
        
        # Правило для порогу помилок
        self.add_rule(AlertRule(
            name="High Error Rate",
            alert_type=AlertType.ERROR_THRESHOLD,
            severity=AlertSeverity.HIGH,
            condition=self._check_error_threshold,
            threshold=0.1,  # 10% помилок
            time_window_minutes=5,
            cooldown_minutes=10,
            notification_channels=["email", "slack"],
            description="Помилки перевищують 10% від загальної кількості запитів"
        ))
        
        # Правило для повільних відповідей
        self.add_rule(AlertRule(
            name="Slow Response Time",
            alert_type=AlertType.RESPONSE_TIME,
            severity=AlertSeverity.MEDIUM,
            condition=self._check_response_time,
            threshold=2000.0,  # 2 секунди
            time_window_minutes=5,
            cooldown_minutes=15,
            notification_channels=["email"],
            description="Середній час відповіді перевищує 2 секунди"
        ))
        
        # Правило для подій безпеки
        self.add_rule(AlertRule(
            name="Security Events",
            alert_type=AlertType.SECURITY_EVENT,
            severity=AlertSeverity.CRITICAL,
            condition=self._check_security_events,
            threshold=5,  # 5 подій безпеки
            time_window_minutes=1,
            cooldown_minutes=5,
            notification_channels=["email", "slack", "telegram"],
            description="Виявлено підозрілі події безпеки"
        ))
        
        # Правило для деградації продуктивності
        self.add_rule(AlertRule(
            name="Performance Degradation",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.MEDIUM,
            condition=self._check_performance_degradation,
            threshold=0.5,  # 50% деградація
            time_window_minutes=10,
            cooldown_minutes=20,
            notification_channels=["email"],
            description="Продуктивність сервісу знизилася на 50%"
        ))
    
    def add_rule(self, rule: AlertRule):
        """Додавання правила алерту"""
        self.alert_rules.append(rule)
        self.logger.info(f"Додано правило алерту: {rule.name}")
    
    def check_alerts(self, logs: List[Dict]) -> List[Alert]:
        """Перевірка умов для алертів"""
        new_alerts = []
        current_time = datetime.utcnow()
        
        # Фільтруємо логи за часовим вікном
        time_window = current_time - timedelta(minutes=5)  # За замовчуванням 5 хвилин
        recent_logs = [log for log in logs if self._parse_timestamp(log.get('timestamp', '')) > time_window]
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Перевіряємо чи не в cooldown періоді
            if self._is_in_cooldown(rule):
                continue
            
            # Оцінюємо правило
            if rule.condition(recent_logs):
                alert = self._create_alert(rule, recent_logs, current_time)
                new_alerts.append(alert)
                self.active_alerts[alert.id] = alert
                self.alert_history.append(alert)
                
                # Відправляємо сповіщення
                self._send_notifications(alert)
        
        return new_alerts
    
    def _check_error_threshold(self, logs: List[Dict]) -> bool:
        """Перевірка порогу помилок"""
        if not logs:
            return False
        
        error_count = len([log for log in logs if log.get('level') == 'ERROR'])
        total_count = len(logs)
        error_rate = error_count / total_count if total_count > 0 else 0
        
        return error_rate >= 0.1  # 10%
    
    def _check_response_time(self, logs: List[Dict]) -> bool:
        """Перевірка часу відповіді"""
        api_logs = [log for log in logs if 'API:' in log.get('message', '')]
        if not api_logs:
            return False
        
        response_times = []
        for log in api_logs:
            try:
                log_data = json.loads(log.get('message', '{}'))
                if 'context' in log_data and 'duration_ms' in log_data['context']:
                    response_times.append(log_data['context']['duration_ms'])
            except (json.JSONDecodeError, KeyError):
                continue
        
        if not response_times:
            return False
        
        avg_response_time = sum(response_times) / len(response_times)
        return avg_response_time >= 2000.0  # 2 секунди
    
    def _check_security_events(self, logs: List[Dict]) -> bool:
        """Перевірка подій безпеки"""
        security_logs = [log for log in logs if 'Security:' in log.get('message', '')]
        return len(security_logs) >= 5
    
    def _check_performance_degradation(self, logs: List[Dict]) -> bool:
        """Перевірка деградації продуктивності"""
        performance_logs = [log for log in logs if 'Performance:' in log.get('message', '')]
        if len(performance_logs) < 10:
            return False
        
        # Простий алгоритм виявлення деградації
        recent_performance = performance_logs[-10:]
        older_performance = performance_logs[:-10] if len(performance_logs) >= 20 else []
        
        if not older_performance:
            return False
        
        recent_avg = self._calculate_performance_average(recent_performance)
        older_avg = self._calculate_performance_average(older_performance)
        
        if older_avg == 0:
            return False
        
        degradation = (recent_avg - older_avg) / older_avg
        return degradation >= 0.5  # 50% деградація
    
    def _calculate_performance_average(self, logs: List[Dict]) -> float:
        """Розрахунок середньої продуктивності"""
        durations = []
        for log in logs:
            try:
                log_data = json.loads(log.get('message', '{}'))
                if 'context' in log_data and 'duration_ms' in log_data['context']:
                    durations.append(log_data['context']['duration_ms'])
            except (json.JSONDecodeError, KeyError):
                continue
        
        return sum(durations) / len(durations) if durations else 0
    
    def _create_alert(self, rule: AlertRule, logs: List[Dict], timestamp: datetime) -> Alert:
        """Створення алерту"""
        import uuid
        
        alert_id = str(uuid.uuid4())
        
        # Формуємо деталі алерту
        details = {
            "logs_count": len(logs),
            "time_window_minutes": rule.time_window_minutes,
            "threshold": rule.threshold,
            "sample_logs": logs[-5:] if logs else []  # Останні 5 логів
        }
        
        return Alert(
            id=alert_id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            message=f"Алерт: {rule.description}",
            timestamp=timestamp,
            service_name=logs[0].get('service_name', 'unknown') if logs else 'unknown',
            environment=logs[0].get('environment', 'unknown') if logs else 'unknown',
            details=details
        )
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Перевірка чи правило в cooldown періоді"""
        current_time = datetime.utcnow()
        
        # Шукаємо останній алерт для цього правила
        for alert in reversed(self.alert_history):
            if alert.rule_name == rule.name and not alert.resolved:
                time_since_alert = current_time - alert.timestamp
                return time_since_alert.total_seconds() < rule.cooldown_minutes * 60
        
        return False
    
    def _send_notifications(self, alert: Alert):
        """Відправка сповіщень"""
        self.logger.info(f"Відправка сповіщень для алерту: {alert.id}")
        
        # Email сповіщення
        if self.notification_config["email"]["enabled"]:
            self._send_email_notification(alert)
        
        # Slack сповіщення
        if self.notification_config["slack"]["enabled"]:
            self._send_slack_notification(alert)
        
        # Telegram сповіщення
        if self.notification_config["telegram"]["enabled"]:
            self._send_telegram_notification(alert)
    
    def _send_email_notification(self, alert: Alert):
        """Відправка email сповіщення"""
        try:
            config = self.notification_config["email"]
            
            msg = MIMEMultipart()
            msg['From'] = config["username"]
            msg['To'] = ", ".join(config["recipients"])
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.rule_name}"
            
            body = f"""
            Алерт: {alert.rule_name}
            Серйозність: {alert.severity.value}
            Сервіс: {alert.service_name}
            Середовище: {alert.environment}
            Час: {alert.timestamp}
            Опис: {alert.message}
            
            Деталі:
            {json.dumps(alert.details, indent=2, ensure_ascii=False)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email сповіщення відправлено для алерту: {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Помилка відправки email: {str(e)}")
    
    def _send_slack_notification(self, alert: Alert):
        """Відправка Slack сповіщення"""
        try:
            config = self.notification_config["slack"]
            
            payload = {
                "channel": config["channel"],
                "text": f"🚨 *{alert.severity.value.upper()}*: {alert.rule_name}",
                "attachments": [{
                    "fields": [
                        {"title": "Сервіс", "value": alert.service_name, "short": True},
                        {"title": "Середовище", "value": alert.environment, "short": True},
                        {"title": "Опис", "value": alert.message, "short": False}
                    ],
                    "color": self._get_severity_color(alert.severity)
                }]
            }
            
            response = requests.post(config["webhook_url"], json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Slack сповіщення відправлено для алерту: {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Помилка відправки Slack: {str(e)}")
    
    def _send_telegram_notification(self, alert: Alert):
        """Відправка Telegram сповіщення"""
        try:
            config = self.notification_config["telegram"]
            
            message = f"""
🚨 *{alert.severity.value.upper()}*: {alert.rule_name}

Сервіс: {alert.service_name}
Середовище: {alert.environment}
Опис: {alert.message}
Час: {alert.timestamp}
            """
            
            url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
            payload = {
                "chat_id": config["chat_id"],
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Telegram сповіщення відправлено для алерту: {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Помилка відправки Telegram: {str(e)}")
    
    def _get_severity_color(self, severity: AlertSeverity) -> str:
        """Отримання кольору для серйозності"""
        colors = {
            AlertSeverity.LOW: "#36a64f",
            AlertSeverity.MEDIUM: "#ffa500",
            AlertSeverity.HIGH: "#ff4500",
            AlertSeverity.CRITICAL: "#ff0000"
        }
        return colors.get(severity, "#808080")
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Парсинг timestamp"""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return datetime.utcnow()
    
    def resolve_alert(self, alert_id: str):
        """Вирішення алерту"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Алерт вирішено: {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Отримання активних алертів"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Отримання історії алертів"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp > cutoff_time]


# Глобальний екземпляр системи алертів
alerting_system = AlertingSystem() 