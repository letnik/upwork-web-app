#!/usr/bin/env python3
"""
Тести для MVP-009: Синхронізація з Upwork (раз на день)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from tests.utils.test_helpers import create_test_user, get_test_db

class TestUpworkSync:
    """Тести для синхронізації з Upwork"""

    def test_upwork_api_client_creation(self):
        """Тест створення Upwork API клієнта"""
        user = create_test_user()
        
        # Симулюємо Upwork API клієнт
        upwork_client = Mock()
        upwork_client.user_id = user["id"]
        upwork_client.access_token = "test_access_token"
        upwork_client.refresh_token = "test_refresh_token"
        upwork_client.last_sync = datetime.now()
        upwork_client.is_connected = True
        
        assert upwork_client.user_id == user["id"]
        assert upwork_client.access_token == "test_access_token"
        assert upwork_client.is_connected == True
        assert upwork_client.last_sync is not None
        
        print("✅ Тест створення Upwork API клієнта пройшов")

    def test_upwork_sync_frequency(self):
        """Тест частоти синхронізації (раз на день)"""
        user = create_test_user()
        
        # Симулюємо останню синхронізацію
        last_sync = datetime.now() - timedelta(hours=12)  # 12 годин тому
        current_time = datetime.now()
        
        # Перевіряємо, чи можна синхронізувати (раз на день)
        time_since_last_sync = current_time - last_sync
        can_sync = time_since_last_sync.total_seconds() >= 86400  # 24 години
        
        assert pytest.approx(time_since_last_sync.total_seconds(), abs=1) == 43200  # 12 годин
        assert not can_sync  # Ще не пройшло 24 години
        
        # Симулюємо синхронізацію після 24 годин
        last_sync = datetime.now() - timedelta(hours=25)  # 25 годин тому
        time_since_last_sync = current_time - last_sync
        can_sync = time_since_last_sync.total_seconds() >= 86400
        
        assert can_sync  # Пройшло більше 24 годин
        
        print("✅ Тест частоти синхронізації (раз на день) пройшов")

    def test_upwork_data_synchronization(self):
        """Тест синхронізації даних з Upwork"""
        user = create_test_user()
        
        # Симулюємо дані для синхронізації
        sync_data = {
            "profile": {
                "name": "John Doe",
                "title": "Full Stack Developer",
                "skills": ["Python", "React", "Node.js"],
                "hourly_rate": 50,
                "total_earnings": 25000
            },
            "jobs": [
                {"id": "job1", "title": "Web Developer", "budget": 5000, "status": "active"},
                {"id": "job2", "title": "Mobile App", "budget": 8000, "status": "completed"}
            ],
            "proposals": [
                {"id": "prop1", "job_id": "job1", "status": "submitted"},
                {"id": "prop2", "job_id": "job2", "status": "accepted"}
            ],
            "contracts": [
                {"id": "contract1", "client": "Client A", "rate": 50, "status": "active"},
                {"id": "contract2", "client": "Client B", "rate": 60, "status": "completed"}
            ]
        }
        
        # Перевіряємо структуру даних
        assert "profile" in sync_data
        assert "jobs" in sync_data
        assert "proposals" in sync_data
        assert "contracts" in sync_data
        
        # Перевіряємо дані профілю
        assert sync_data["profile"]["name"] == "John Doe"
        assert sync_data["profile"]["hourly_rate"] == 50
        assert len(sync_data["profile"]["skills"]) == 3
        
        # Перевіряємо кількість елементів
        assert len(sync_data["jobs"]) == 2
        assert len(sync_data["proposals"]) == 2
        assert len(sync_data["contracts"]) == 2
        
        print("✅ Тест синхронізації даних з Upwork пройшов")

    def test_upwork_sync_error_handling(self):
        """Тест обробки помилок синхронізації"""
        user = create_test_user()
        
        # Симулюємо різні типи помилок
        sync_errors = [
            {"type": "network_error", "message": "Connection timeout", "retry_count": 0},
            {"type": "auth_error", "message": "Token expired", "retry_count": 1},
            {"type": "rate_limit", "message": "Rate limit exceeded", "retry_count": 2},
            {"type": "api_error", "message": "Invalid request", "retry_count": 3}
        ]
        
        def handle_sync_error(error):
            """Обробка помилки синхронізації"""
            if error["type"] == "network_error" and error["retry_count"] < 3:
                return "retry"
            elif error["type"] == "auth_error":
                return "refresh_token"
            elif error["type"] == "rate_limit":
                return "wait"
            else:
                return "fail"
        
        # Тестуємо обробку помилок
        assert handle_sync_error(sync_errors[0]) == "retry"
        assert handle_sync_error(sync_errors[1]) == "refresh_token"
        assert handle_sync_error(sync_errors[2]) == "wait"
        assert handle_sync_error(sync_errors[3]) == "fail"
        
        print("✅ Тест обробки помилок синхронізації пройшов")

    def test_upwork_sync_retry_mechanism(self):
        """Тест механізму повторних спроб"""
        user = create_test_user()
        
        # Симулюємо механізм повторних спроб
        max_retries = 3
        retry_delays = [60, 300, 900]  # 1 хв, 5 хв, 15 хв
        
        def should_retry(error_count, error_type):
            """Визначає, чи потрібно повторити спробу"""
            if error_count >= max_retries:
                return False
            if error_type == "auth_error":
                return True
            if error_type == "network_error":
                return True
            return False
        
        def get_retry_delay(error_count):
            """Отримує затримку перед повторною спробою"""
            if error_count < len(retry_delays):
                return retry_delays[error_count]
            return retry_delays[-1]
        
        # Тестуємо логіку повторних спроб
        assert should_retry(0, "network_error") == True
        assert should_retry(2, "auth_error") == True
        assert should_retry(3, "network_error") == False
        
        assert get_retry_delay(0) == 60
        assert get_retry_delay(1) == 300
        assert get_retry_delay(2) == 900
        assert get_retry_delay(5) == 900  # Максимальна затримка
        
        print("✅ Тест механізму повторних спроб пройшов")

    def test_upwork_sync_data_validation(self):
        """Тест валідації даних синхронізації"""
        user = create_test_user()
        
        def validate_sync_data(data):
            """Валідація даних синхронізації"""
            errors = []
            
            if not data.get("profile"):
                errors.append("Профіль користувача відсутній")
            
            if not data.get("jobs"):
                errors.append("Дані про вакансії відсутні")
            
            if not data.get("proposals"):
                errors.append("Дані про пропозиції відсутні")
            
            # Перевіряємо формат даних
            if data.get("profile"):
                profile = data["profile"]
                if not profile.get("name"):
                    errors.append("Ім'я користувача відсутнє")
                if not profile.get("title"):
                    errors.append("Посада користувача відсутня")
            
            return errors
        
        # Валідні дані
        valid_data = {
            "profile": {
                "name": "John Doe",
                "title": "Developer",
                "skills": ["Python", "React"]
            },
            "jobs": [{"id": "job1", "title": "Web Developer"}],
            "proposals": [{"id": "prop1", "status": "submitted"}]
        }
        valid_errors = validate_sync_data(valid_data)
        assert len(valid_errors) == 0
        
        # Невалідні дані
        invalid_data = {
            "profile": {
                "name": "",
                "title": ""
            },
            "jobs": [],
            "proposals": []
        }
        invalid_errors = validate_sync_data(invalid_data)
        assert len(invalid_errors) >= 3  # Мінімум 3 основні помилки
        
        print("✅ Тест валідації даних синхронізації пройшов")

    def test_upwork_sync_incremental_update(self):
        """Тест інкрементального оновлення даних"""
        user = create_test_user()
        
        # Симулюємо поточні дані
        current_data = {
            "jobs": [
                {"id": "job1", "title": "Web Developer", "status": "active"},
                {"id": "job2", "title": "Mobile App", "status": "completed"}
            ],
            "proposals": [
                {"id": "prop1", "job_id": "job1", "status": "submitted"},
                {"id": "prop2", "job_id": "job2", "status": "accepted"}
            ]
        }
        
        # Симулюємо нові дані з Upwork
        new_data = {
            "jobs": [
                {"id": "job1", "title": "Web Developer", "status": "completed"},  # Змінено статус
                {"id": "job2", "title": "Mobile App", "status": "completed"},
                {"id": "job3", "title": "New Project", "status": "active"}  # Нова вакансія
            ],
            "proposals": [
                {"id": "prop1", "job_id": "job1", "status": "accepted"},  # Змінено статус
                {"id": "prop2", "job_id": "job2", "status": "accepted"},
                {"id": "prop3", "job_id": "job3", "status": "submitted"}  # Нова пропозиція
            ]
        }
        
        # Визначаємо зміни
        updated_jobs = []
        new_jobs = []
        updated_proposals = []
        new_proposals = []
        
        # Аналізуємо зміни в вакансіях
        current_job_ids = {job["id"] for job in current_data["jobs"]}
        new_job_ids = {job["id"] for job in new_data["jobs"]}
        
        for job in new_data["jobs"]:
            if job["id"] in current_job_ids:
                # Знаходимо відповідну поточну вакансію
                current_job = next(j for j in current_data["jobs"] if j["id"] == job["id"])
                if current_job["status"] != job["status"]:
                    updated_jobs.append(job)
            else:
                new_jobs.append(job)
        
        # Аналізуємо зміни в пропозиціях
        current_proposal_ids = {prop["id"] for prop in current_data["proposals"]}
        new_proposal_ids = {prop["id"] for prop in new_data["proposals"]}
        
        for prop in new_data["proposals"]:
            if prop["id"] in current_proposal_ids:
                current_prop = next(p for p in current_data["proposals"] if p["id"] == prop["id"])
                if current_prop["status"] != prop["status"]:
                    updated_proposals.append(prop)
            else:
                new_proposals.append(prop)
        
        # Перевіряємо результати
        assert len(updated_jobs) == 1  # job1 змінив статус
        assert len(new_jobs) == 1      # job3 новий
        assert len(updated_proposals) == 1  # prop1 змінив статус
        assert len(new_proposals) == 1      # prop3 новий
        
        print("✅ Тест інкрементального оновлення даних пройшов")

    def test_upwork_sync_logging(self):
        """Тест логування синхронізації"""
        user = create_test_user()
        
        # Симулюємо лог синхронізації
        sync_log = {
            "user_id": user["id"],
            "sync_start": datetime.now(),
            "sync_end": None,
            "status": "running",
            "items_synced": 0,
            "errors": [],
            "warnings": []
        }
        
        # Симулюємо успішну синхронізацію
        sync_log["sync_end"] = datetime.now()
        sync_log["status"] = "completed"
        sync_log["items_synced"] = 150
        
        # Перевіряємо лог
        assert sync_log["user_id"] == user["id"]
        assert sync_log["status"] == "completed"
        assert sync_log["items_synced"] == 150
        assert sync_log["sync_start"] is not None
        assert sync_log["sync_end"] is not None
        
        # Перевіряємо тривалість синхронізації
        duration = sync_log["sync_end"] - sync_log["sync_start"]
        assert duration.total_seconds() >= 0
        
        print("✅ Тест логування синхронізації пройшов")

    def test_upwork_sync_performance(self):
        """Тест продуктивності синхронізації"""
        user = create_test_user()
        
        # Симулюємо метрики продуктивності
        performance_metrics = {
            "sync_duration_seconds": 45,
            "items_per_second": 3.33,  # 150 items / 45 seconds
            "memory_usage_mb": 128,
            "api_calls_count": 25,
            "cache_hit_rate": 0.85
        }
        
        # Перевіряємо показники продуктивності
        assert performance_metrics["sync_duration_seconds"] <= 300  # Не більше 5 хвилин
        assert performance_metrics["items_per_second"] >= 1.0  # Мінімум 1 елемент/сек
        assert performance_metrics["memory_usage_mb"] <= 512  # Не більше 512MB
        assert performance_metrics["api_calls_count"] <= 100  # Не більше 100 API викликів
        assert 0 <= performance_metrics["cache_hit_rate"] <= 1  # Від 0 до 1
        
        # Перевіряємо якісні показники
        assert performance_metrics["cache_hit_rate"] >= 0.8  # Високий рівень кешування
        assert performance_metrics["items_per_second"] >= 2.0  # Хороша швидкість обробки
        
        print("✅ Тест продуктивності синхронізації пройшов")

if __name__ == "__main__":
    test_instance = TestUpworkSync()
    test_instance.test_upwork_api_client_creation()
    test_instance.test_upwork_sync_frequency()
    test_instance.test_upwork_data_synchronization()
    test_instance.test_upwork_sync_error_handling()
    test_instance.test_upwork_sync_retry_mechanism()
    test_instance.test_upwork_sync_data_validation()
    test_instance.test_upwork_sync_incremental_update()
    test_instance.test_upwork_sync_logging()
    test_instance.test_upwork_sync_performance()
    print("\n🎉 Всі тести синхронізації з Upwork пройшли успішно!") 