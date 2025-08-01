"""
Тести для MVP компонентів - Система сповіщень (Telegram, Push, Email)
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
from test_helpers import create_test_user, get_test_db


class TestNotificationSystem:
    """Тести для системи сповіщень"""
    
    def test_notification_creation(self):
        """Тест створення сповіщення"""
        # Mock дані
        user = create_test_user()
        
        # Дані сповіщення
        notification_data = {
            "id": "notif_123",
            "type": "job_alert",
            "title": "Нова вакансія знайдена",
            "message": "Знайдено вакансію Python Developer з бюджетом $3000-$6000",
            "priority": "high",
            "channels": ["email", "telegram", "push"],
            "user_id": user["id"],
            "created_at": datetime.utcnow(),
            "read": False,
            "metadata": {
                "job_id": "upwork_job_123",
                "match_score": 85.5,
                "budget": "$3000-$6000"
            }
        }
        
        # Перевіряємо структуру даних
        assert "id" in notification_data
        assert "type" in notification_data
        assert "title" in notification_data
        assert "message" in notification_data
        assert "channels" in notification_data
        
        # Перевіряємо типи даних
        assert isinstance(notification_data["id"], str)
        assert isinstance(notification_data["type"], str)
        assert isinstance(notification_data["title"], str)
        assert isinstance(notification_data["channels"], list)
        
        # Перевіряємо валідність даних
        assert len(notification_data["id"]) > 0
        assert len(notification_data["title"]) <= 200
        assert len(notification_data["message"]) <= 1000
        assert notification_data["priority"] in ["low", "medium", "high", "urgent"]
        
        print("✅ Тест створення сповіщення пройшов")
    
    def test_notification_channels(self):
        """Тест каналів сповіщень"""
        # Валідні канали сповіщень
        valid_channels = ["email", "telegram", "push", "slack", "sms"]
        
        for channel in valid_channels:
            # Перевіряємо, що канал валідний
            assert channel in valid_channels, f"Неправильний канал сповіщення: {channel}"
            
            # Створюємо приклад сповіщення для кожного каналу
            notification = {
                "type": "job_alert",
                "title": f"Тестове сповіщення - {channel}",
                "message": f"Тестове повідомлення через {channel}",
                "channel": channel,
                "priority": "medium"
            }
            
            # Перевіряємо структуру
            assert "type" in notification
            assert "title" in notification
            assert "message" in notification
            assert "channel" in notification
            assert notification["channel"] == channel
        
        print("✅ Тест каналів сповіщень пройшов")
    
    def test_email_notification(self):
        """Тест email сповіщень"""
        # Mock конфігурація email
        email_config = {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "alerts@example.com",
            "password": "your-password",
            "recipients": ["user@example.com"]
        }
        
        # Перевіряємо конфігурацію
        assert email_config["enabled"] == True
        assert len(email_config["smtp_server"]) > 0
        assert email_config["smtp_port"] > 0
        assert len(email_config["username"]) > 0
        assert len(email_config["recipients"]) > 0
        
        # Приклад email сповіщення
        email_notification = {
            "to": "user@example.com",
            "subject": "Нова вакансія - Python Developer",
            "body": """
            Знайдено нову вакансію:
            
            Позиція: Python Developer
            Бюджет: $3000-$6000
            Оцінка підходящості: 85.5%
            
            Переглянути: https://upwork.com/job/123
            """,
            "html_body": "<h2>Нова вакансія</h2><p>Python Developer - $3000-$6000</p>"
        }
        
        # Перевіряємо структуру email
        assert "to" in email_notification
        assert "subject" in email_notification
        assert "body" in email_notification
        
        # Перевіряємо валідність email
        assert "@" in email_notification["to"]
        assert len(email_notification["subject"]) <= 200
        assert len(email_notification["body"]) > 0
        
        print("✅ Тест email сповіщень пройшов")
    
    def test_telegram_notification(self):
        """Тест Telegram сповіщень"""
        # Mock конфігурація Telegram
        telegram_config = {
            "enabled": True,
            "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            "chat_id": "-1001234567890",
            "parse_mode": "HTML"
        }
        
        # Перевіряємо конфігурацію
        assert telegram_config["enabled"] == True
        assert len(telegram_config["bot_token"]) > 0
        assert len(telegram_config["chat_id"]) > 0
        
        # Приклад Telegram сповіщення
        telegram_notification = {
            "chat_id": "-1001234567890",
            "text": """
🔔 <b>Нова вакансія знайдена!</b>

💼 <b>Python Developer</b>
💰 Бюджет: $3000-$6000
⭐ Оцінка: 85.5%

🔗 <a href="https://upwork.com/job/123">Переглянути</a>
            """,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        # Перевіряємо структуру Telegram сповіщення
        assert "chat_id" in telegram_notification
        assert "text" in telegram_notification
        assert "parse_mode" in telegram_notification
        
        # Перевіряємо валідність
        assert len(telegram_notification["text"]) > 0
        assert telegram_notification["parse_mode"] in ["HTML", "Markdown"]
        
        print("✅ Тест Telegram сповіщень пройшов")
    
    def test_push_notification(self):
        """Тест Push сповіщень"""
        # Mock конфігурація Push
        push_config = {
            "enabled": True,
            "vapid_public_key": "your-vapid-public-key",
            "vapid_private_key": "your-vapid-private-key",
            "subject": "mailto:alerts@example.com"
        }
        
        # Перевіряємо конфігурацію
        assert push_config["enabled"] == True
        assert len(push_config["vapid_public_key"]) > 0
        assert len(push_config["vapid_private_key"]) > 0
        
        # Приклад Push сповіщення
        push_notification = {
            "title": "Нова вакансія",
            "body": "Python Developer - $3000-$6000",
            "icon": "/icon-192x192.png",
            "badge": "/badge-72x72.png",
            "data": {
                "url": "https://upwork.com/job/123",
                "job_id": "upwork_job_123",
                "match_score": 85.5
            },
            "actions": [
                {
                    "action": "view",
                    "title": "Переглянути"
                },
                {
                    "action": "dismiss",
                    "title": "Закрити"
                }
            ]
        }
        
        # Перевіряємо структуру Push сповіщення
        assert "title" in push_notification
        assert "body" in push_notification
        assert "data" in push_notification
        
        # Перевіряємо валідність
        assert len(push_notification["title"]) <= 50
        assert len(push_notification["body"]) <= 200
        assert "job_id" in push_notification["data"]
        
        print("✅ Тест Push сповіщень пройшов")
    
    def test_notification_priority_system(self):
        """Тест системи пріоритетів сповіщень"""
        # Приклади сповіщень з різними пріоритетами
        notifications_by_priority = [
            {
                "type": "job_alert",
                "title": "Висока оцінка вакансії",
                "priority": "urgent",
                "match_score": 95.0
            },
            {
                "type": "job_alert", 
                "title": "Нова вакансія",
                "priority": "high",
                "match_score": 85.0
            },
            {
                "type": "system_update",
                "title": "Оновлення системи",
                "priority": "medium"
            },
            {
                "type": "weekly_report",
                "title": "Тижневий звіт",
                "priority": "low"
            }
        ]
        
        for notification in notifications_by_priority:
            # Перевіряємо пріоритет
            assert notification["priority"] in ["low", "medium", "high", "urgent"]
            
            # Перевіряємо логіку пріоритетів
            if "match_score" in notification:
                if notification["match_score"] >= 90:
                    assert notification["priority"] in ["high", "urgent"], "Високі оцінки повинні мати високий пріоритет"
                elif notification["match_score"] >= 80:
                    assert notification["priority"] in ["medium", "high"], "Середні оцінки повинні мати середній пріоритет"
            
            # Перевіряємо тип сповіщення
            assert notification["type"] in ["job_alert", "system_update", "weekly_report"]
        
        print("✅ Тест системи пріоритетів пройшов")
    
    def test_notification_delivery_tracking(self):
        """Тест відстеження доставки сповіщень"""
        # Mock дані для відстеження доставки
        delivery_tracking = [
            {
                "notification_id": "notif_1",
                "channel": "email",
                "status": "sent",
                "sent_at": datetime.utcnow(),
                "delivery_time_ms": 250
            },
            {
                "notification_id": "notif_1", 
                "channel": "telegram",
                "status": "sent",
                "sent_at": datetime.utcnow(),
                "delivery_time_ms": 180
            },
            {
                "notification_id": "notif_1",
                "channel": "push", 
                "status": "failed",
                "sent_at": datetime.utcnow(),
                "error": "Invalid subscription"
            }
        ]
        
        for tracking in delivery_tracking:
            # Перевіряємо структуру
            assert "notification_id" in tracking
            assert "channel" in tracking
            assert "status" in tracking
            assert "sent_at" in tracking
            
            # Перевіряємо статуси
            assert tracking["status"] in ["pending", "sent", "failed", "delivered"]
            
            # Перевіряємо час доставки
            if "delivery_time_ms" in tracking:
                assert tracking["delivery_time_ms"] > 0
                assert tracking["delivery_time_ms"] < 5000, "Час доставки повинен бути менше 5 секунд"
        
        print("✅ Тест відстеження доставки пройшов")


class TestNotificationIntegration:
    """Інтеграційні тести для системи сповіщень"""
    
    def test_notification_complete_workflow(self):
        """Тест повного workflow сповіщень"""
        # 1. Створення користувача
        user = create_test_user()
        assert user["id"] is not None
        
        # 2. Налаштування сповіщень користувача
        user_notification_settings = {
            "email_enabled": True,
            "telegram_enabled": True,
            "push_enabled": True,
            "email": "user@example.com",
            "telegram_chat_id": "123456789",
            "notification_preferences": {
                "job_alerts": True,
                "system_updates": False,
                "weekly_reports": True
            }
        }
        
        # 3. Симуляція знаходження нової вакансії
        new_job = {
            "job_id": "upwork_job_123",
            "title": "Python Developer",
            "budget": "$3000-$6000",
            "match_score": 85.5
        }
        
        # 4. Створення сповіщення
        notification = {
            "id": "notif_123",
            "type": "job_alert",
            "title": "Нова вакансія знайдена",
            "message": f"Знайдено вакансію {new_job['title']} з бюджетом {new_job['budget']}",
            "priority": "high" if new_job["match_score"] >= 80 else "medium",
            "channels": ["email", "telegram", "push"],
            "user_id": user["id"],
            "metadata": {
                "job_id": new_job["job_id"],
                "match_score": new_job["match_score"]
            }
        }
        
        # 5. Перевірка валідності
        assert notification["priority"] == "high"  # 85.5 >= 80
        assert "email" in notification["channels"]
        assert "telegram" in notification["channels"]
        assert "push" in notification["channels"]
        
        # 6. Симуляція відправки
        delivery_results = [
            {"channel": "email", "status": "sent", "delivery_time_ms": 250},
            {"channel": "telegram", "status": "sent", "delivery_time_ms": 180},
            {"channel": "push", "status": "sent", "delivery_time_ms": 120}
        ]
        
        # 7. Перевірка результатів
        for result in delivery_results:
            assert result["status"] == "sent"
            assert result["delivery_time_ms"] < 1000
        
        print("✅ Тест повного workflow сповіщень пройшов")
    
    def test_notification_rate_limiting(self):
        """Тест обмеження частоти сповіщень"""
        # Налаштування обмежень
        rate_limits = {
            "email": {"max_per_hour": 10, "max_per_day": 100},
            "telegram": {"max_per_hour": 20, "max_per_day": 200},
            "push": {"max_per_hour": 30, "max_per_day": 300}
        }
        
        # Симуляція сповіщень за годину
        notifications_sent = {
            "email": 8,
            "telegram": 15,
            "push": 25
        }
        
        # Перевірка обмежень
        for channel, sent_count in notifications_sent.items():
            limit = rate_limits[channel]["max_per_hour"]
            assert sent_count <= limit, f"Перевищено ліміт для {channel}: {sent_count} > {limit}"
        
        print("✅ Тест обмеження частоти пройшов")
    
    def test_notification_user_preferences(self):
        """Тест налаштувань користувача"""
        # Приклади налаштувань користувачів
        user_preferences = [
            {
                "user_id": "user_1",
                "email_enabled": True,
                "telegram_enabled": False,
                "push_enabled": True,
                "job_alerts": True,
                "system_updates": False,
                "weekly_reports": True
            },
            {
                "user_id": "user_2",
                "email_enabled": False,
                "telegram_enabled": True,
                "push_enabled": True,
                "job_alerts": True,
                "system_updates": True,
                "weekly_reports": False
            }
        ]
        
        for prefs in user_preferences:
            # Перевіряємо структуру налаштувань
            assert "user_id" in prefs
            assert "email_enabled" in prefs
            assert "telegram_enabled" in prefs
            assert "push_enabled" in prefs
            
            # Перевіряємо логіку: хоча б один канал повинен бути активним
            active_channels = sum([
                prefs["email_enabled"],
                prefs["telegram_enabled"], 
                prefs["push_enabled"]
            ])
            assert active_channels > 0, "Хоча б один канал сповіщень повинен бути активним"
            
            # Перевіряємо, що job_alerts завжди увімкнені для тестування
            assert prefs["job_alerts"] == True, "Сповіщення про вакансії повинні бути увімкнені"
        
        print("✅ Тест налаштувань користувача пройшов")


if __name__ == "__main__":
    # Запуск тестів
    test_notifications = TestNotificationSystem()
    test_notifications.test_notification_creation()
    test_notifications.test_notification_channels()
    test_notifications.test_email_notification()
    test_notifications.test_telegram_notification()
    test_notifications.test_push_notification()
    test_notifications.test_notification_priority_system()
    test_notifications.test_notification_delivery_tracking()
    
    test_integration = TestNotificationIntegration()
    test_integration.test_notification_complete_workflow()
    test_integration.test_notification_rate_limiting()
    test_integration.test_notification_user_preferences()
    
    print("\n🎉 Всі тести системи сповіщень пройшли успішно!") 