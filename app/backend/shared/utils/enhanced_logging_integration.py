"""
Розширена інтеграція логування з новими компонентами
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Додаємо шлях до shared
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config.logging import setup_logging, get_logger
from shared.utils.alerting_system import alerting_system
from shared.utils.log_cleanup_service import log_cleanup_service, CleanupConfig


class EnhancedLoggingIntegration:
    """Розширена інтеграція логування з новими компонентами"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("enhanced-logging-integration")
        
        # Налаштування системи очищення
        self.cleanup_config = CleanupConfig(
            retention_days=90,
            archive_enabled=True,
            archive_path="logs/archive",
            compression_enabled=True,
            cleanup_interval_hours=24,
            max_archive_size_gb=10,
            backup_enabled=True,
            backup_path="logs/backup"
        )
        
        self.logger.info("Ініціалізовано розширену інтеграцію логування", extra={
            "service_name": service_name,
            "cleanup_enabled": True,
            "alerting_enabled": True
        })
    
    def setup_enhanced_logging(self):
        """Налаштування розширеного логування"""
        try:
            # Налаштування базового логування
            setup_logging(service_name=self.service_name)
            
            # Запуск сервісу очищення
            log_cleanup_service.config = self.cleanup_config
            log_cleanup_service.start_scheduled_cleanup()
            
            # Налаштування системи алертів
            self._setup_alerting()
            
            self.logger.info("Розширене логування налаштовано", extra={
                "service_name": self.service_name,
                "components": ["base_logging", "cleanup_service", "alerting_system"]
            })
            
        except Exception as e:
            self.logger.error("Помилка налаштування розширеного логування", extra={
                "error": str(e),
                "service_name": self.service_name
            })
            raise
    
    def _setup_alerting(self):
        """Налаштування системи алертів"""
        try:
            # Налаштування email сповіщень
            alerting_system.notification_config["email"].update({
                "enabled": True,
                "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("SMTP_USERNAME", ""),
                "password": os.getenv("SMTP_PASSWORD", ""),
                "recipients": os.getenv("ALERT_RECIPIENTS", "").split(",") if os.getenv("ALERT_RECIPIENTS") else []
            })
            
            # Налаштування Slack сповіщень
            if os.getenv("SLACK_WEBHOOK_URL"):
                alerting_system.notification_config["slack"].update({
                    "enabled": True,
                    "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                    "channel": os.getenv("SLACK_CHANNEL", "#alerts")
                })
            
            # Налаштування Telegram сповіщень
            if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
                alerting_system.notification_config["telegram"].update({
                    "enabled": True,
                    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
                    "chat_id": os.getenv("TELEGRAM_CHAT_ID")
                })
            
            self.logger.info("Система алертів налаштована", extra={
                "email_enabled": alerting_system.notification_config["email"]["enabled"],
                "slack_enabled": alerting_system.notification_config["slack"]["enabled"],
                "telegram_enabled": alerting_system.notification_config["telegram"]["enabled"]
            })
            
        except Exception as e:
            self.logger.error("Помилка налаштування алертів", extra={"error": str(e)})
    
    def check_alerts(self, logs: list) -> list:
        """Перевірка алертів на основі логів"""
        try:
            alerts = alerting_system.check_alerts(logs)
            
            if alerts:
                self.logger.info(f"Виявлено {len(alerts)} нових алертів", extra={
                    "alerts_count": len(alerts),
                    "alert_types": [alert.alert_type.value for alert in alerts]
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error("Помилка перевірки алертів", extra={"error": str(e)})
            return []
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Отримання статистики очищення"""
        try:
            return log_cleanup_service.get_cleanup_stats()
        except Exception as e:
            self.logger.error("Помилка отримання статистики очищення", extra={"error": str(e)})
            return {}
    
    def manual_cleanup(self) -> Dict[str, int]:
        """Ручне очищення логів"""
        try:
            self.logger.info("Початок ручного очищення логів")
            stats = log_cleanup_service.cleanup_old_logs()
            
            self.logger.info("Ручне очищення завершено", extra=stats)
            return stats
            
        except Exception as e:
            self.logger.error("Помилка ручного очищення", extra={"error": str(e)})
            return {}
    
    def manual_archive(self) -> Dict[str, int]:
        """Ручне архівування логів"""
        try:
            self.logger.info("Початок ручного архівування логів")
            stats = log_cleanup_service.archive_logs()
            
            self.logger.info("Ручне архівування завершено", extra=stats)
            return stats
            
        except Exception as e:
            self.logger.error("Помилка ручного архівування", extra={"error": str(e)})
            return {}
    
    def manual_backup(self) -> Dict[str, int]:
        """Ручне резервне копіювання логів"""
        try:
            self.logger.info("Початок ручного резервного копіювання")
            stats = log_cleanup_service.backup_logs()
            
            self.logger.info("Ручне резервне копіювання завершено", extra=stats)
            return stats
            
        except Exception as e:
            self.logger.error("Помилка ручного резервного копіювання", extra={"error": str(e)})
            return {}
    
    def get_active_alerts(self) -> list:
        """Отримання активних алертів"""
        try:
            return alerting_system.get_active_alerts()
        except Exception as e:
            self.logger.error("Помилка отримання активних алертів", extra={"error": str(e)})
            return []
    
    def resolve_alert(self, alert_id: str):
        """Вирішення алерту"""
        try:
            alerting_system.resolve_alert(alert_id)
            self.logger.info(f"Алерт вирішено: {alert_id}")
        except Exception as e:
            self.logger.error(f"Помилка вирішення алерту {alert_id}", extra={"error": str(e)})
    
    def shutdown(self):
        """Зупинка сервісів"""
        try:
            # Зупинка сервісу очищення
            log_cleanup_service.stop_scheduled_cleanup()
            
            self.logger.info("Розширене логування зупинено", extra={
                "service_name": self.service_name
            })
            
        except Exception as e:
            self.logger.error("Помилка зупинки розширеного логування", extra={"error": str(e)})


def create_logs_directory():
    """Створення директорії для логів"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Створюємо піддиректорії
    subdirs = ["test", "archive", "backup"]
    for subdir in subdirs:
        (logs_dir / subdir).mkdir(exist_ok=True)
    
    print(f"✅ Створено директорію для логів: {logs_dir.absolute()}")


def create_elk_directories():
    """Створення директорій для ELK Stack"""
    elk_dir = Path("docker/elk")
    elk_dir.mkdir(parents=True, exist_ok=True)
    
    # Створюємо піддиректорії
    subdirs = ["logstash/pipeline", "logstash/config", "filebeat"]
    for subdir in subdirs:
        (elk_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Створено директорії для ELK Stack: {elk_dir.absolute()}")


def create_enhanced_logging_documentation():
    """Створення документації по розширеному логуванню"""
    docs_dir = Path("shared/docs")
    docs_dir.mkdir(exist_ok=True)
    
    documentation = '''# Розширена система логування з ELK Stack та алертами

## Огляд

Система логування була розширена інтеграцією з ELK Stack, розумними алертами та автоматичним очищенням логів.

### Нові компоненти

1. **ELK Stack** - Elasticsearch, Logstash, Kibana для аналізу логів
2. **Alerting System** - розумна система алертів з email/Slack/Telegram сповіщеннями
3. **Log Cleanup Service** - автоматичне очищення та архівування логів
4. **Enhanced Integration** - інтеграція всіх компонентів

### ELK Stack

#### Запуск ELK Stack
```bash
cd docker/elk
docker-compose up -d
```

#### Доступ до сервісів
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Logstash**: http://localhost:9600

#### Конфігурація
- `docker/elk/logstash/pipeline/logstash.conf` - обробка логів
- `docker/elk/filebeat/filebeat.yml` - збір логів

### Система алертів

#### Типи алертів
- **High Error Rate** - високий рівень помилок (>10%)
- **Slow Response Time** - повільні відповіді (>2с)
- **Security Events** - події безпеки
- **Performance Degradation** - деградація продуктивності

#### Налаштування сповіщень
```bash
# Email
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-password
export ALERT_RECIPIENTS=admin@example.com,dev@example.com

# Slack
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
export SLACK_CHANNEL=#alerts

# Telegram
export TELEGRAM_BOT_TOKEN=your-bot-token
export TELEGRAM_CHAT_ID=your-chat-id
```

### Сервіс очищення логів

#### Автоматичне очищення
- Ротація логів кожні 24 години
- Архівування старих логів
- Резервне копіювання
- Стиснення архівів

#### Налаштування
```python
cleanup_config = CleanupConfig(
    retention_days=90,           # Зберігання 90 днів
    archive_enabled=True,        # Архівування увімкнено
    compression_enabled=True,    # Стиснення увімкнено
    max_archive_size_gb=10,      # Максимум 10GB архівів
    backup_enabled=True          # Резервне копіювання увімкнено
)
```

### Використання

#### Ініціалізація
```python
from shared.utils.enhanced_logging_integration import EnhancedLoggingIntegration

# Створення інтеграції
integration = EnhancedLoggingIntegration("my-service")

# Налаштування
integration.setup_enhanced_logging()

# Перевірка алертів
alerts = integration.check_alerts(logs)

# Отримання статистики
stats = integration.get_cleanup_stats()

# Ручне очищення
integration.manual_cleanup()

# Зупинка
integration.shutdown()
```

#### Моніторинг в Kibana

1. Відкрийте Kibana: http://localhost:5601
2. Створіть індекс-патерн: `logs-*`
3. Створіть Dashboard для моніторингу:
   - Кількість помилок по часу
   - Середній час відповіді
   - Події безпеки
   - Продуктивність сервісів

#### Алерти в реальному часі

Система автоматично відправляє сповіщення при:
- Високому рівні помилок
- Повільних відповідях
- Підозрілих подіях безпеки
- Деградації продуктивності

### Переваги

1. **Централізований аналіз** - всі логи в одному місці
2. **Розумні алерти** - автоматичне виявлення проблем
3. **Автоматичне очищення** - економія місця на диску
4. **Масштабованість** - готовність до зростання
5. **Візуалізація** - красиві графіки в Kibana
6. **Пошук** - швидкий пошук по логах
7. **Архівування** - довгострокове зберігання
8. **Резервне копіювання** - захист від втрати даних

### Рекомендації

1. Налаштуйте алерти відповідно до ваших потреб
2. Регулярно переглядайте Dashboard в Kibana
3. Налаштуйте резервне копіювання архівів
4. Моніторте розмір архівів та очищайте старі
5. Налаштуйте різні канали сповіщень для різних типів алертів
'''
    
    with open(docs_dir / "ENHANCED_LOGGING_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print(f"✅ Створено документацію: {docs_dir / 'ENHANCED_LOGGING_GUIDE.md'}")


def main():
    """Головна функція для налаштування розширеного логування"""
    print("🚀 Налаштування розширеного логування...")
    
    # Створення директорій
    create_logs_directory()
    create_elk_directories()
    
    # Створення документації
    create_enhanced_logging_documentation()
    
    print("✅ Розширене логування налаштовано!")
    print("\n📋 Наступні кроки:")
    print("1. Запустіть ELK Stack: cd docker/elk && docker-compose up -d")
    print("2. Налаштуйте змінні середовища для алертів")
    print("3. Інтегруйте EnhancedLoggingIntegration в ваші сервіси")
    print("4. Відкрийте Kibana: http://localhost:5601")


if __name__ == "__main__":
    main() 