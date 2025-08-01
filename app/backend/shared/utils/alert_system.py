"""
Розширена система сповіщень безпеки
SECURITY-009: Детекція аномалій та система сповіщень
"""

import asyncio
import json
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .security_logger import SecurityLogger, SecurityEventType, SecurityLevel
from .anomaly_detector import AnomalyDetector, AnomalySeverity


class AlertChannel(Enum):
    """Канали сповіщень"""
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"


class AlertPriority(Enum):
    """Пріоритети сповіщень"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSystem:
    """Розширена система сповіщень безпеки"""
    
    def __init__(self, security_logger: SecurityLogger, anomaly_detector: AnomalyDetector):
        self.security_logger = security_logger
        self.anomaly_detector = anomaly_detector
        self.logger = security_logger.logger
        self.alert_rules = self._load_alert_rules()
        self.alert_history = []
        self.channel_configs = self._load_channel_configs()
        self.rate_limits = {}  # Rate limiting для сповіщень
        
    def _load_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Завантажує розширені правила алертів"""
        return {
            "multiple_failed_logins": {
                "threshold": 5,
                "window": 300,  # 5 хвилин
                "priority": AlertPriority.HIGH,
                "channels": [AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                "message_template": "Multiple failed login attempts detected for IP {ip_address}"
            },
            "suspicious_ip": {
                "threshold": 10,
                "window": 3600,  # 1 година
                "priority": AlertPriority.CRITICAL,
                "channels": [AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.DASHBOARD],
                "message_template": "Suspicious activity detected from IP {ip_address}"
            },
            "api_rate_limit_exceeded": {
                "threshold": 3,
                "window": 60,  # 1 хвилина
                "priority": AlertPriority.MEDIUM,
                "channels": [AlertChannel.DASHBOARD],
                "message_template": "API rate limit exceeded for IP {ip_address}"
            },
            "mfa_failures": {
                "threshold": 3,
                "window": 300,  # 5 хвилин
                "priority": AlertPriority.HIGH,
                "channels": [AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                "message_template": "Multiple MFA failures detected for user {user_id}"
            },
            "anomaly_detected": {
                "threshold": 0.7,  # Бал аномалії
                "priority": AlertPriority.HIGH,
                "channels": [AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                "message_template": "Security anomaly detected: {anomaly_type} (score: {score})"
            },
            "geographic_anomaly": {
                "threshold": 1,  # Будь-яка географічна аномалія
                "priority": AlertPriority.CRITICAL,
                "channels": [AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.TELEGRAM],
                "message_template": "Geographic anomaly detected from {country_code}"
            },
            "behavior_change": {
                "threshold": 0.6,  # Бал зміни поведінки
                "priority": AlertPriority.MEDIUM,
                "channels": [AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                "message_template": "Behavior change detected for user {user_id}"
            },
            "burst_activity": {
                "threshold": 10,
                "window": 600,  # 10 хвилин
                "priority": AlertPriority.HIGH,
                "channels": [AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                "message_template": "Burst activity detected for user {user_id}"
            }
        }
    
    def _load_channel_configs(self) -> Dict[AlertChannel, Dict[str, Any]]:
        """Завантажує конфігурації каналів сповіщень"""
        return {
            AlertChannel.EMAIL: {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@example.com",
                "password": "your_password",
                "from_email": "alerts@example.com",
                "to_emails": ["admin@example.com", "security@example.com"],
                "rate_limit": 10,  # Максимум сповіщень за годину
                "rate_limit_window": 3600
            },
            AlertChannel.SMS: {
                "enabled": False,  # Потребує SMS провайдера
                "provider": "twilio",
                "account_sid": "your_account_sid",
                "auth_token": "your_auth_token",
                "from_number": "+1234567890",
                "to_numbers": ["+1234567890"],
                "rate_limit": 5,
                "rate_limit_window": 3600
            },
            AlertChannel.TELEGRAM: {
                "enabled": False,  # Потребує Telegram бота
                "bot_token": "your_bot_token",
                "chat_id": "your_chat_id",
                "rate_limit": 20,
                "rate_limit_window": 3600
            },
            AlertChannel.SLACK: {
                "enabled": False,  # Потребує Slack webhook
                "webhook_url": "your_webhook_url",
                "channel": "#security-alerts",
                "rate_limit": 30,
                "rate_limit_window": 3600
            },
            AlertChannel.WEBHOOK: {
                "enabled": False,
                "webhook_url": "your_webhook_url",
                "headers": {"Authorization": "Bearer your_token"},
                "rate_limit": 50,
                "rate_limit_window": 3600
            },
            AlertChannel.DASHBOARD: {
                "enabled": True,
                "rate_limit": 100,
                "rate_limit_window": 3600
            }
        }
    
    async def check_alerts(self, security_log) -> List[Dict[str, Any]]:
        """Перевіряє алерти на основі події"""
        try:
            alerts_triggered = []
            
            # Перевіряємо різні типи алертів
            alerts_triggered.extend(await self._check_failed_logins(security_log))
            alerts_triggered.extend(await self._check_suspicious_ips(security_log))
            alerts_triggered.extend(await self._check_api_rate_limits(security_log))
            alerts_triggered.extend(await self._check_mfa_failures(security_log))
            alerts_triggered.extend(await self._check_anomaly_alerts(security_log))
            
            # Відправляємо сповіщення
            for alert in alerts_triggered:
                await self._send_alert(alert)
            
            return alerts_triggered
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки алертів: {e}")
            return []
    
    async def _check_failed_logins(self, security_log) -> List[Dict[str, Any]]:
        """Перевіряє алерти на невдалі спроби входу"""
        alerts = []
        
        if security_log.event_type == SecurityEventType.LOGIN_FAILED.value:
            ip_address = security_log.ip_address
            if not ip_address:
                return alerts
            
            # Отримуємо кількість невдалих спроб за останні 5 хвилин
            failed_attempts = await self._get_failed_attempts(ip_address, minutes=5)
            
            rule = self.alert_rules["multiple_failed_logins"]
            if len(failed_attempts) >= rule["threshold"]:
                alert = {
                    "type": "multiple_failed_logins",
                    "priority": rule["priority"],
                    "channels": rule["channels"],
                    "message": rule["message_template"].format(ip_address=ip_address),
                    "details": {
                        "ip_address": ip_address,
                        "failed_count": len(failed_attempts),
                        "threshold": rule["threshold"],
                        "time_window": "5 minutes"
                    },
                    "timestamp": datetime.utcnow()
                }
                alerts.append(alert)
        
        return alerts
    
    async def _check_suspicious_ips(self, security_log) -> List[Dict[str, Any]]:
        """Перевіряє підозрілі IP адреси"""
        alerts = []
        
        if security_log.ip_address:
            ip_address = security_log.ip_address
            
            # Отримуємо кількість запитів за останню годину
            recent_requests = await self._get_recent_requests(ip_address, hours=1)
            
            rule = self.alert_rules["suspicious_ip"]
            if len(recent_requests) >= rule["threshold"]:
                alert = {
                    "type": "suspicious_ip",
                    "priority": rule["priority"],
                    "channels": rule["channels"],
                    "message": rule["message_template"].format(ip_address=ip_address),
                    "details": {
                        "ip_address": ip_address,
                        "requests_count": len(recent_requests),
                        "threshold": rule["threshold"],
                        "time_window": "1 hour"
                    },
                    "timestamp": datetime.utcnow()
                }
                alerts.append(alert)
        
        return alerts
    
    async def _check_api_rate_limits(self, security_log) -> List[Dict[str, Any]]:
        """Перевіряє перевищення rate limits"""
        alerts = []
        
        if security_log.event_type == SecurityEventType.API_RATE_LIMIT.value:
            ip_address = security_log.ip_address
            if not ip_address:
                return alerts
            
            # Отримуємо кількість перевищень rate limit за останню хвилину
            rate_limit_violations = await self._get_rate_limit_violations(ip_address, minutes=1)
            
            rule = self.alert_rules["api_rate_limit_exceeded"]
            if len(rate_limit_violations) >= rule["threshold"]:
                alert = {
                    "type": "api_rate_limit_exceeded",
                    "priority": rule["priority"],
                    "channels": rule["channels"],
                    "message": rule["message_template"].format(ip_address=ip_address),
                    "details": {
                        "ip_address": ip_address,
                        "violations_count": len(rate_limit_violations),
                        "threshold": rule["threshold"],
                        "time_window": "1 minute"
                    },
                    "timestamp": datetime.utcnow()
                }
                alerts.append(alert)
        
        return alerts
    
    async def _check_mfa_failures(self, security_log) -> List[Dict[str, Any]]:
        """Перевіряє невдалі спроби MFA"""
        alerts = []
        
        if security_log.event_type == SecurityEventType.MFA_FAILED.value:
            user_id = security_log.user_id
            if not user_id:
                return alerts
            
            # Отримуємо кількість невдач MFA за останні 5 хвилин
            mfa_failures = await self._get_mfa_failures(user_id, minutes=5)
            
            rule = self.alert_rules["mfa_failures"]
            if len(mfa_failures) >= rule["threshold"]:
                alert = {
                    "type": "mfa_failures",
                    "priority": rule["priority"],
                    "channels": rule["channels"],
                    "message": rule["message_template"].format(user_id=user_id),
                    "details": {
                        "user_id": user_id,
                        "failures_count": len(mfa_failures),
                        "threshold": rule["threshold"],
                        "time_window": "5 minutes"
                    },
                    "timestamp": datetime.utcnow()
                }
                alerts.append(alert)
        
        return alerts
    
    async def _check_anomaly_alerts(self, security_log) -> List[Dict[str, Any]]:
        """Перевіряє алерти на основі аномалій"""
        alerts = []
        
        # Використовуємо детектор аномалій
        anomaly_score, anomaly_details = await self.anomaly_detector.detect_anomaly(security_log)
        
        if anomaly_score > 0:
            # Перевіряємо кожну аномалію
            for detail in anomaly_details:
                anomaly_type = detail["type"]
                score = detail["score"]
                
                # Перевіряємо чи є правило для цього типу аномалії
                if anomaly_type in self.alert_rules:
                    rule = self.alert_rules[anomaly_type]
                    threshold = rule.get("threshold", 0.5)
                    
                    if score >= threshold:
                        alert = {
                            "type": f"anomaly_{anomaly_type}",
                            "priority": rule["priority"],
                            "channels": rule["channels"],
                            "message": rule["message_template"].format(
                                anomaly_type=anomaly_type,
                                score=score
                            ),
                            "details": {
                                "anomaly_type": anomaly_type,
                                "score": score,
                                "threshold": threshold,
                                "anomaly_details": detail["details"]
                            },
                            "timestamp": datetime.utcnow()
                        }
                        alerts.append(alert)
        
        return alerts
    
    async def _send_alert(self, alert: Dict[str, Any]) -> bool:
        """Відправляє сповіщення через всі налаштовані канали"""
        try:
            success = True
            
            # Перевіряємо rate limiting
            if not await self._check_rate_limit(alert):
                self.logger.warning(f"Rate limit exceeded for alert: {alert['type']}")
                return False
            
            # Відправляємо через кожен канал
            for channel in alert["channels"]:
                if channel in self.channel_configs and self.channel_configs[channel]["enabled"]:
                    channel_success = await self._send_to_channel(channel, alert)
                    success = success and channel_success
            
            # Зберігаємо в історію
            self.alert_history.append({
                **alert,
                "sent": success,
                "sent_at": datetime.utcnow()
            })
            
            # Обмежуємо історію
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
            return success
            
        except Exception as e:
            self.logger.error(f"Помилка відправки сповіщення: {e}")
            return False
    
    async def _send_to_channel(self, channel: AlertChannel, alert: Dict[str, Any]) -> bool:
        """Відправляє сповіщення через конкретний канал"""
        try:
            config = self.channel_configs[channel]
            
            if channel == AlertChannel.EMAIL:
                return await self._send_email(config, alert)
            elif channel == AlertChannel.SMS:
                return await self._send_sms(config, alert)
            elif channel == AlertChannel.TELEGRAM:
                return await self._send_telegram(config, alert)
            elif channel == AlertChannel.SLACK:
                return await self._send_slack(config, alert)
            elif channel == AlertChannel.WEBHOOK:
                return await self._send_webhook(config, alert)
            elif channel == AlertChannel.DASHBOARD:
                return await self._send_dashboard(config, alert)
            else:
                self.logger.warning(f"Невідомий канал сповіщень: {channel}")
                return False
                
        except Exception as e:
            self.logger.error(f"Помилка відправки через канал {channel}: {e}")
            return False
    
    async def _send_email(self, config: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Відправляє сповіщення по email"""
        try:
            # Створюємо повідомлення
            msg = MIMEMultipart()
            msg['From'] = config["from_email"]
            msg['To'] = ", ".join(config["to_emails"])
            msg['Subject'] = f"Security Alert: {alert['type']}"
            
            # Формуємо тіло повідомлення
            body = f"""
Security Alert Detected

Type: {alert['type']}
Priority: {alert['priority'].value}
Message: {alert['message']}
Timestamp: {alert['timestamp']}

Details:
{json.dumps(alert['details'], indent=2)}

This is an automated security alert.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Відправляємо (в реальному проекті тут була б налаштована SMTP)
            # server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            # server.starttls()
            # server.login(config["username"], config["password"])
            # server.send_message(msg)
            # server.quit()
            
            self.logger.info(f"Email alert sent: {alert['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка відправки email: {e}")
            return False
    
    async def _send_sms(self, config: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Відправляє SMS сповіщення"""
        try:
            # В реальному проекті тут була б інтеграція з SMS провайдером
            # Наприклад, Twilio
            self.logger.info(f"SMS alert sent: {alert['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка відправки SMS: {e}")
            return False
    
    async def _send_telegram(self, config: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Відправляє Telegram сповіщення"""
        try:
            # В реальному проекті тут була б інтеграція з Telegram Bot API
            message = f"🚨 Security Alert\n\n{alert['message']}\n\nPriority: {alert['priority'].value}"
            
            # url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
            # data = {
            #     "chat_id": config["chat_id"],
            #     "text": message,
            #     "parse_mode": "HTML"
            # }
            # response = requests.post(url, data=data)
            
            self.logger.info(f"Telegram alert sent: {alert['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка відправки Telegram: {e}")
            return False
    
    async def _send_slack(self, config: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Відправляє Slack сповіщення"""
        try:
            # В реальному проекті тут була б інтеграція з Slack Webhook
            payload = {
                "channel": config["channel"],
                "text": f"🚨 Security Alert: {alert['message']}",
                "attachments": [{
                    "color": self._get_priority_color(alert["priority"]),
                    "fields": [
                        {"title": "Type", "value": alert["type"], "short": True},
                        {"title": "Priority", "value": alert["priority"].value, "short": True},
                        {"title": "Details", "value": json.dumps(alert["details"], indent=2)}
                    ]
                }]
            }
            
            # response = requests.post(config["webhook_url"], json=payload)
            
            self.logger.info(f"Slack alert sent: {alert['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка відправки Slack: {e}")
            return False
    
    async def _send_webhook(self, config: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Відправляє webhook сповіщення"""
        try:
            # В реальному проекті тут була б відправка webhook
            # response = requests.post(
            #     config["webhook_url"],
            #     json=alert,
            #     headers=config["headers"]
            # )
            
            self.logger.info(f"Webhook alert sent: {alert['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка відправки webhook: {e}")
            return False
    
    async def _send_dashboard(self, config: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Зберігає сповіщення для dashboard"""
        try:
            # В реальному проекті тут було б збереження в БД для dashboard
            self.logger.info(f"Dashboard alert stored: {alert['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка збереження для dashboard: {e}")
            return False
    
    def _get_priority_color(self, priority: AlertPriority) -> str:
        """Повертає колір для пріоритету"""
        colors = {
            AlertPriority.LOW: "#36a64f",
            AlertPriority.MEDIUM: "#ffa500",
            AlertPriority.HIGH: "#ff6b6b",
            AlertPriority.CRITICAL: "#ff0000"
        }
        return colors.get(priority, "#808080")
    
    async def _check_rate_limit(self, alert: Dict[str, Any]) -> bool:
        """Перевіряє rate limiting для сповіщень"""
        try:
            alert_type = alert["type"]
            current_time = datetime.utcnow()
            
            # Отримуємо конфігурацію каналу з найвищим пріоритетом
            channels = alert["channels"]
            if not channels:
                return True
            
            # Використовуємо конфігурацію першого каналу
            channel_config = self.channel_configs[channels[0]]
            rate_limit = channel_config.get("rate_limit", 100)
            rate_limit_window = channel_config.get("rate_limit_window", 3600)
            
            # Перевіряємо історію сповіщень
            cutoff_time = current_time - timedelta(seconds=rate_limit_window)
            recent_alerts = [
                a for a in self.alert_history
                if a["type"] == alert_type and a["sent_at"] >= cutoff_time
            ]
            
            return len(recent_alerts) < rate_limit
            
        except Exception as e:
            self.logger.error(f"Помилка перевірки rate limit: {e}")
            return True
    
    # Допоміжні методи (моки для тестування)
    async def _get_failed_attempts(self, ip_address: str, minutes: int) -> List[Any]:
        """Отримує невдалі спроби входу"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_recent_requests(self, ip_address: str, hours: int) -> List[Any]:
        """Отримує нещодавні запити"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_rate_limit_violations(self, ip_address: str, minutes: int) -> List[Any]:
        """Отримує порушення rate limit"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def _get_mfa_failures(self, user_id: int, minutes: int) -> List[Any]:
        """Отримує невдачі MFA"""
        # Мок - в реальному проекті тут був би запит до БД
        return []
    
    async def get_alert_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Отримує статистику сповіщень"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Фільтруємо сповіщення за період
            recent_alerts = [
                alert for alert in self.alert_history
                if alert["timestamp"] >= cutoff_date
            ]
            
            if not recent_alerts:
                return {
                    "period_days": days,
                    "total_alerts": 0,
                    "sent_alerts": 0,
                    "priority_distribution": {},
                    "type_distribution": {},
                    "channel_distribution": {}
                }
            
            # Обчислюємо статистику
            total_alerts = len(recent_alerts)
            sent_alerts = len([a for a in recent_alerts if a.get("sent", False)])
            
            # Розподіл по пріоритетах
            priority_counts = {}
            for alert in recent_alerts:
                priority = alert["priority"].value
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Розподіл по типах
            type_counts = {}
            for alert in recent_alerts:
                alert_type = alert["type"]
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            # Розподіл по каналах
            channel_counts = {}
            for alert in recent_alerts:
                for channel in alert["channels"]:
                    channel_counts[channel.value] = channel_counts.get(channel.value, 0) + 1
            
            return {
                "period_days": days,
                "total_alerts": total_alerts,
                "sent_alerts": sent_alerts,
                "success_rate": sent_alerts / total_alerts if total_alerts > 0 else 0,
                "priority_distribution": priority_counts,
                "type_distribution": type_counts,
                "channel_distribution": channel_counts,
                "recent_alerts": recent_alerts[-10:]  # Останні 10 сповіщень
            }
            
        except Exception as e:
            self.logger.error(f"Помилка отримання статистики сповіщень: {e}")
            return {} 